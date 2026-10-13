import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TrainingDataContractTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads((ROOT / ".pmcro/protocol/training-data-eligibility.schema.json").read_text(encoding="utf-8"))
        self.profiles = json.loads((ROOT / ".pmcro/training/role-dataset-profiles.json").read_text(encoding="utf-8"))
        self.evals = json.loads((ROOT / ".pmcro/evals/pmcro-role-evals.json").read_text(encoding="utf-8"))

    def test_training_is_not_authorized_by_dataset_contract(self):
        self.assertFalse(self.profiles["trainingAuthorityGranted"])
        self.assertEqual(self.profiles["status"], "candidate-unchecked")
        self.assertFalse(self.profiles["sharedRules"]["trailDataEligibleByDefault"])

    def test_eligibility_is_opt_in_and_excludes_sensitive_classes(self):
        self.assertEqual(self.policy["properties"]["defaultEligible"]["const"], False)
        self.assertEqual(self.policy["properties"]["explicitOptIn"]["const"], True)
        excluded = set(self.profiles["sharedRules"]["excludedClasses"])
        self.assertTrue({"secrets", "credentials", "private-reasoning", "unapproved-user-content"}.issubset(excluded))

    def test_five_role_profiles_match_eval_contracts(self):
        profiles = {row["role"]: row for row in self.profiles["profiles"]}
        expected = {"pmcro-orchestrator", "pmcro-planner", "pmcro-maker", "pmcro-checker", "pmcro-reflector"}
        self.assertEqual(set(profiles), expected)
        for role, profile in profiles.items():
            self.assertEqual(profile["status"], "candidate-unchecked")
            self.assertIn(role, self.evals)
            self.assertEqual(set(profile["trainingObjectives"]), set(self.evals[role]["dimensions"]))
            self.assertEqual(set(profile["mustExcludeBehavior"]), set(self.evals[role]["mustNot"]))

    def test_maker_and_checker_are_separate(self):
        profiles = {row["role"]: row for row in self.profiles["profiles"]}
        maker = profiles["pmcro-maker"]
        checker = profiles["pmcro-checker"]
        self.assertNotEqual(maker["datasetId"], checker["datasetId"])
        self.assertNotEqual(maker["independenceGroup"], checker["independenceGroup"])
        self.assertIn(maker["datasetId"], checker["mustRemainSeparateFrom"])

    def test_eval_leakage_is_forbidden(self):
        self.assertFalse(self.profiles["sharedRules"]["evaluationLeakageAllowed"])


if __name__ == "__main__":
    unittest.main()
