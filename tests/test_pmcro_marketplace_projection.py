import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROLE_IDS = {
    "pmcro-orchestrator",
    "pmcro-planner",
    "pmcro-maker",
    "pmcro-checker",
    "pmcro-reflector",
}


class MarketplaceProjectionTests(unittest.TestCase):
    def load(self, relative: str):
        return json.loads((ROOT / relative).read_text(encoding="utf-8"))

    def test_one_canonical_marketplace_and_plugin_authority(self):
        authority = self.load(".pmcro/registry/authority.json")
        marketplace = self.load(authority["canonical"]["marketplace"])
        plugin = self.load(authority["canonical"]["plugins"]["pmcro"])
        self.assertEqual(marketplace["authority"], "canonical")
        self.assertEqual(plugin["authority"], "canonical")
        self.assertFalse(marketplace["projectionPolicy"]["providerSurfacesAreCanonical"])
        self.assertFalse(plugin["providerProjectionAuthority"])
        self.assertEqual(marketplace["plugins"][0]["manifest"], "plugins/pmcro/.pmcro-plugin/plugin.json")

        agents_projection = self.load(".agents/plugins/marketplace.json")
        legacy_plugin = self.load("plugins/pmcro/plugin.json")
        self.assertEqual(agents_projection["projectionOf"], ".pmcro-plugin/marketplace.json")
        self.assertEqual(legacy_plugin["projectionOf"], "plugins/pmcro/.pmcro-plugin/plugin.json")
        self.assertIn(".pmcro-plugin/marketplace.json", agents_projection["sourceOfTruth"])
        self.assertEqual(agents_projection["version"], marketplace["version"])
        self.assertEqual(agents_projection["plugins"][0]["version"], plugin["version"])
        self.assertFalse(agents_projection["canonical"])
        self.assertFalse(agents_projection["grantsRuntimeAuthority"])

    def test_canonical_plugin_declares_five_role_agents_and_skill_packages(self):
        plugin = self.load("plugins/pmcro/.pmcro-plugin/plugin.json")
        self.assertEqual({item["id"] for item in plugin["agents"]}, ROLE_IDS)
        skill_ids = {item["id"] for item in plugin["skills"]}
        self.assertTrue(ROLE_IDS.issubset(skill_ids))
        self.assertIn("pmcro-init", skill_ids)
        self.assertNotIn("pmcro-init", {item["id"] for item in plugin["agents"]})
        for skill in plugin["skills"]:
            path = ROOT / skill["sourceRef"]
            self.assertTrue((path / "SKILL.md").is_file(), skill["id"])

    def test_claude_projection_is_deterministic_noncanonical_and_complete(self):
        script = ROOT / "scripts/project_marketplace.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            out = Path(temp_dir) / "claude"
            result = subprocess.run(
                [sys.executable, str(script), "--repo", str(ROOT), "--provider", "claude", "--out", str(out)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)

            marketplace = json.loads((out / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
            self.assertEqual(marketplace["$schema"], "https://anthropic.com/claude-code/marketplace.schema.json")
            self.assertEqual(marketplace["plugins"][0]["source"], "./plugins/pmcro")

            plugin = json.loads((out / "plugins/pmcro/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(plugin["name"], "pmcro")
            self.assertEqual(plugin["version"], self.load("plugins/pmcro/.pmcro-plugin/plugin.json")["version"])
            self.assertTrue((out / ".claude" / "skills" / "pmcro-init" / "SKILL.md").is_file())
            self.assertFalse((out / ".claude" / "agents" / "pmcro-init.md").exists())

            manifest = json.loads((out / "projection-manifest.json").read_text(encoding="utf-8"))
            self.assertFalse(manifest["canonical"])
            self.assertFalse(manifest["grantsRuntimeAuthority"])
            self.assertEqual(set(manifest["projectAgents"]), ROLE_IDS)

            for role in ROLE_IDS:
                project_agent = out / ".claude" / "agents" / f"{role}.md"
                plugin_agent = out / "plugins" / "pmcro" / "agents" / f"{role}.md"
                self.assertTrue(project_agent.is_file())
                self.assertTrue(plugin_agent.is_file())
                text = project_agent.read_text(encoding="utf-8")
                self.assertIn("GENERATED PROJECTION", text)
                self.assertIn("Canonical PMCR-O contract", text)
                self.assertTrue((out / ".claude" / "skills" / role / "SKILL.md").is_file())
                self.assertTrue((out / "plugins" / "pmcro" / "skills" / role / "SKILL.md").is_file())

            first = (out / "projection-manifest.json").read_text(encoding="utf-8")
            result2 = subprocess.run(
                [sys.executable, str(script), "--repo", str(ROOT), "--provider", "claude", "--out", str(out)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result2.returncode, 0, result2.stderr + result2.stdout)
            second = (out / "projection-manifest.json").read_text(encoding="utf-8")
            self.assertEqual(first, second)

    def test_training_candidates_remain_ineligible_and_role_specific(self):
        candidates = self.load(".pmcro/training/candidates/marketplace-projection-candidates.json")
        self.assertFalse(candidates["trainingAuthorityGranted"])
        self.assertEqual({item["role"] for item in candidates["candidates"]}, ROLE_IDS)
        self.assertIn("private-reasoning", candidates["forbiddenSources"])
        self.assertIn("evaluation-holdout", candidates["forbiddenSources"])
        for candidate in candidates["candidates"]:
            self.assertFalse(candidate["trainingEligible"])
            self.assertFalse(candidate["explicitOptIn"])
            self.assertTrue(candidate["requiresIndependentCheck"])
            self.assertTrue(candidate["sourceRefs"])


if __name__ == "__main__":
    unittest.main()
