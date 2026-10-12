import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "skills/dotagents-skill-creator/scripts/bootstrap_workspace.py"
VALIDATOR = ROOT / "skills/dotagents-skill-creator/scripts/validate_workspace.py"
ROUTER = ROOT / "skills/dotagents-skill-creator/scripts/route_create_skill.py"
PMCR_O_MARKERS = (
    "I AM THE",
    "I ORCHESTRATE",
    "I PLAN",
    "I MAKE",
    "I CHECK",
    "I REFLECT",
)
OPTIONAL_LAYERS = ("references", "assets", "scripts", "tests")


def run(*args):
    return subprocess.run([sys.executable, *args], text=True, capture_output=True)


class CreatorTests(unittest.TestCase):
    def test_dry_run_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            result = run(str(SCRIPT), "--root", str(workspace), "--skill", "sample-skill", "--plugin", "personal")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(workspace.exists())

    def test_cognition_only_apply_validate_repeat_and_seed_provenance(self):
        raw_seed = "messy seed:  keep   spacing ] and punctuation?!"
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            args = [
                str(SCRIPT),
                "--root", str(workspace),
                "--skill", "sample-skill",
                "--plugin", "personal",
                "--raw-seed", raw_seed,
                "--apply",
            ]
            first = run(*args)
            self.assertEqual(first.returncode, 0, first.stderr)

            base = workspace / ".agents/skills/sample-skill"
            self.assertTrue((base / "SKILL.md").is_file())
            self.assertTrue((base / "agents/agent.md").is_file())
            self.assertTrue((base / "agents/agent.json").is_file())
            for layer in OPTIONAL_LAYERS:
                self.assertFalse((base / layer).exists(), f"unexpected cognition-only layer: {layer}")

            agent_text = (base / "agents/agent.md").read_text(encoding="utf-8")
            for marker in PMCR_O_MARKERS:
                self.assertIn(marker, agent_text)

            request = json.loads(
                (workspace / ".agents/requests/create-skill/personal--sample-skill.json").read_text(encoding="utf-8")
            )
            self.assertEqual(request["kind"], "skill.create.request")
            self.assertEqual(request["requiredInvoker"], "dotagents-skill-creator")
            self.assertEqual(request["creatorAuthority"], "dotagents-skill-creator")
            self.assertEqual(request["rawSeed"], raw_seed)
            self.assertTrue(request["rawSeedImmutable"])
            self.assertEqual(request["rawSeedSha256"], hashlib.sha256(raw_seed.encode("utf-8")).hexdigest())
            self.assertEqual(request["rules"]["requiredCore"], ["SKILL.md", "agents/"])
            self.assertEqual(request["rules"]["generatedLayers"], [])
            self.assertTrue(request["rules"]["registrationRequiresIndependentCheck"])

            checked = run(str(VALIDATOR), "--root", str(workspace))
            self.assertEqual(checked.returncode, 0, checked.stderr)

            second = run(*args)
            self.assertEqual(second.returncode, 0, second.stderr)
            manifest = json.loads((workspace / "dotagents.manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["sourceOfTruth"], ".agents/skills")
            self.assertEqual(manifest["createAuthority"], "dotagents-skill-creator")
            self.assertEqual(manifest["promotion"], "generated-unchecked")
            self.assertEqual(manifest["components"]["personal/sample-skill"]["generatedLayers"], [])

    def test_optional_layers_are_emitted_only_when_requested(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            result = run(
                str(SCRIPT),
                "--root", str(workspace),
                "--skill", "mixed-skill",
                "--plugin", "personal",
                "--with-references",
                "--with-scripts",
                "--apply",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            base = workspace / ".agents/skills/mixed-skill"
            self.assertTrue((base / "references").is_dir())
            self.assertTrue((base / "scripts").is_dir())
            self.assertFalse((base / "assets").exists())
            self.assertFalse((base / "tests").exists())

            request = json.loads(
                (workspace / ".agents/requests/create-skill/personal--mixed-skill.json").read_text(encoding="utf-8")
            )
            self.assertEqual(request["rules"]["generatedLayers"], ["references", "scripts"])
            checked = run(str(VALIDATOR), "--root", str(workspace))
            self.assertEqual(checked.returncode, 0, checked.stderr)

    def test_router_uses_skill_creator_authority_and_canonical_seed_ingress(self):
        raw_seed = "create this from my messy intent"
        with tempfile.TemporaryDirectory() as directory:
            catalog = Path(directory) / "catalog.json"
            catalog.write_text(json.dumps({"kind": "marketplace-catalog", "entries": []}), encoding="utf-8")
            result = run(
                str(ROUTER),
                "--catalog", str(catalog),
                "--skill", "sample-skill",
                "--plugin", "personal",
                "--raw-seed", raw_seed,
                "--with-assets",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            request = json.loads(result.stdout)
            self.assertEqual(request["kind"], "skill.create.request")
            self.assertEqual(request["requiredInvoker"], "dotagents-skill-creator")
            self.assertEqual(request["creatorAuthority"], "dotagents-skill-creator")
            self.assertEqual(request["seedEntrypoint"], "@orchestrator /pmcro:seed")
            self.assertEqual(request["rawSeed"], raw_seed)
            self.assertTrue(request["rawSeedImmutable"])
            self.assertFalse(request["rules"]["phaseInjectionAllowed"])
            self.assertEqual(request["rules"]["generatedLayers"], ["assets"])

    def test_unknown_conflict_halts(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory) / "workspace"
            target = workspace / ".agents/skills/sample-skill/SKILL.md"
            target.parent.mkdir(parents=True)
            target.write_text("user-owned", encoding="utf-8")
            result = run(str(SCRIPT), "--root", str(workspace), "--skill", "sample-skill", "--plugin", "personal", "--apply")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown conflicting file", result.stderr)


if __name__ == "__main__":
    unittest.main()
