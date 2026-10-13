import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs/reconciliation/a-marketplace-reconciliation.json"
SCRIPT = ROOT / "scripts/reconcile_a_marketplace.py"


class AMarketplaceReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(MAP.read_text(encoding="utf-8"))

    def test_source_is_read_only_and_mutation_is_forbidden(self):
        self.assertEqual(self.data["source"]["path"].lower(), r"a:\marketplace")
        self.assertEqual(self.data["source"]["mode"], "read-only")
        self.assertFalse(self.data["mutation"]["sourceMutationAllowed"])
        self.assertFalse(self.data["mutation"]["registrationAllowed"])
        self.assertFalse(self.data["mutation"]["promotionAllowed"])

    def test_catalog_has_expected_agent_and_legacy_counts(self):
        self.assertEqual(len(self.data["agents"]), 25)
        self.assertEqual(len(self.data["legacy"]), 6)
        self.assertTrue(all(row["classification"] == "REFERENCE" for row in self.data["legacy"]))

    def test_all_agent_projects_expose_canonical_and_projection_surfaces(self):
        for row in self.data["agents"]:
            self.assertTrue(row["exists"], row["id"])
            self.assertTrue(row["surfaces"]["pmcro"], row["id"])
            self.assertTrue(row["surfaces"]["agents"], row["id"])
            self.assertTrue(row["surfaces"]["claude"], row["id"])
            self.assertTrue(row["surfaces"]["claudePlugin"], row["id"])
            self.assertTrue(row["surfaces"]["github"], row["id"])

    def test_conflicting_legacy_laws_are_superseded(self):
        concepts = {row["id"]: row for row in self.data["concepts"]}
        self.assertEqual(concepts["mandatory-all-skill-folders"]["classification"], "SUPERSEDE")
        self.assertEqual(concepts["automatic-post-reflect-cycle"]["classification"], "SUPERSEDE")
        self.assertEqual(concepts["recursive-phase-cycles"]["classification"], "DEFER")

    def test_aligned_authority_laws_are_adopted(self):
        concepts = {row["id"]: row for row in self.data["concepts"]}
        for key in (
            "pmcro-canonical-authority",
            "provider-projections",
            "pinned-upstream-source",
            "independent-marketplace-validation",
            "transport-model-not-authority",
            "maker-no-self-certification",
        ):
            self.assertEqual(concepts[key]["classification"], "ADOPT", key)

    def test_existing_core_systems_merge_instead_of_duplicate(self):
        agents = {row["id"]: row for row in self.data["agents"]}
        for key in ("pmcro-agent", "dotagents-agent", "governance-agent", "desktop-commander-agent", "skill-creator-agent", "maf-agent"):
            self.assertEqual(agents[key]["classification"], "MERGE", key)

    def test_generator_is_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            out_json = Path(td) / "map.json"
            out_md = Path(td) / "map.md"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--root",
                    str(ROOT),
                    "--source",
                    r"A:\marketplace",
                    "--json-out",
                    str(out_json),
                    "--md-out",
                    str(out_md),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            generated = json.loads(out_json.read_text(encoding="utf-8"))
            generated["target"] = self.data["target"]
            self.assertEqual(generated, self.data)


if __name__ == "__main__":
    unittest.main()
