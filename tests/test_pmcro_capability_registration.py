import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("pmcro-resource-registry", "pmcro-message-queue")


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def tree_digest(skill):
    base = ROOT / "skills" / skill
    files = sorted(
        (p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"),
        key=lambda p: p.relative_to(ROOT).as_posix(),
    )
    entries = [
        {"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in files
    ]
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


class CapabilityRegistrationTests(unittest.TestCase):
    def test_registry_records_are_registered_checked_and_digest_bound(self):
        registry = load(".pmcro/registry/index.json")
        records = {row["resourceId"]: row for row in registry["resources"]}
        self.assertEqual(set(records), {f"skill:{s}" for s in SKILLS})
        for skill in SKILLS:
            record = records[f"skill:{skill}"]
            self.assertEqual(record["state"], "registered-checked")
            self.assertTrue(record["admissibleToPlanner"])
            self.assertTrue(record["provenancePreserved"])
            self.assertFalse(record["physicalDeleteOnRevoke"])
            self.assertEqual(record["contentDigest"], tree_digest(skill))
            self.assertEqual(record["checkerVerdictRef"], ".pmcro/evidence/candidate-capabilities-check.json")
            self.assertTrue(record["registrationRef"].startswith(".pmcro/evidence/capability-registration.json#"))

    def test_registration_is_not_execution_or_grant_widening(self):
        evidence = load(".pmcro/evidence/capability-registration.json")
        self.assertTrue(evidence["independentChecker"])
        self.assertTrue(evidence["registrationAuthorizedBySeed"])
        self.assertFalse(evidence["grantsWidened"])
        self.assertFalse(evidence["invokedDuringRegistration"])
        self.assertFalse(evidence["reflectedSeedConsumed"])
        self.assertEqual(evidence["firstUsePolicy"], "fresh-later-cycle-only")
        self.assertFalse(evidence["modelAuthorityChanged"])
        for row in evidence["registrations"]:
            self.assertEqual(row["state"], "registered-checked")
            self.assertTrue(row["admissibleToPlanner"])
            self.assertFalse(row["registrationCycleUseAllowed"])
            self.assertTrue(row["nextCycleUseAllowed"])

    def test_agents_and_transport_preserve_later_cycle_boundary(self):
        registry = load(".pmcro/registry/index.json")
        transport = next(row for row in registry["transports"] if row["transportId"] == "filesystem-spool-v1")
        self.assertEqual(transport["state"], "registered-checked")
        self.assertFalse(transport["grantsAuthority"])
        self.assertFalse(transport["autoExecutesNextSeed"])
        for skill in SKILLS:
            agent = load(f"skills/{skill}/agents/{skill}.json")
            self.assertEqual(agent["status"], "registered-checked")
            self.assertTrue(agent["availableToPlanner"])
            self.assertFalse(agent["registrationCycleUseAllowed"])
            self.assertTrue(agent["nextCycleUseAllowed"])
            self.assertFalse(agent["authority"]["grantsRuntimeAuthority"])

    def test_canonical_and_compatibility_catalogs_expose_registered_resources(self):
        canonical = load("plugins/pmcro/.pmcro-plugin/plugin.json")
        canonical_skills = {row["id"]: row for row in canonical["skills"]}
        legacy = load("plugins/pmcro/plugin.json")
        legacy_skills = {row["id"]: row for row in legacy["skills"]}
        agents = load(".agents/plugins/marketplace.json")["plugins"][0]
        agent_skills = {row["id"]: row for row in agents["skills"]}
        for skill in SKILLS:
            self.assertEqual(canonical_skills[skill]["registrationState"], "registered-checked")
            self.assertEqual(canonical_skills[skill]["firstUsePolicy"], "fresh-later-cycle-only")
            self.assertEqual(legacy_skills[skill]["registrationState"], "registered-checked")
            self.assertEqual(agent_skills[skill]["registrationState"], "registered-checked")

    def test_claude_projection_contains_registered_skills_without_authority_widening(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "claude"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/project_marketplace.py"), "--repo", str(ROOT), "--provider", "claude", "--out", str(out)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            manifest = json.loads((out / "projection-manifest.json").read_text(encoding="utf-8"))
            self.assertFalse(manifest["canonical"])
            self.assertFalse(manifest["grantsRuntimeAuthority"])
            for skill in SKILLS:
                self.assertIn(skill, manifest["projectSkills"])
                self.assertTrue((out / ".claude" / "skills" / skill / "SKILL.md").is_file())
                self.assertTrue((out / "plugins" / "pmcro" / "skills" / skill / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
