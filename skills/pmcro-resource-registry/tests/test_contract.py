import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("registry_candidate", SKILL / "scripts/registry.py")
registry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registry)


class ResourceRegistryContractTests(unittest.TestCase):
    def test_checked_candidate_and_registry_round_trip(self):
        agent = json.loads((SKILL / "agents/pmcro-resource-registry.json").read_text(encoding="utf-8"))
        self.assertEqual(agent["status"], "registered-checked")
        self.assertTrue(agent["availableToPlanner"])
        self.assertFalse(agent["registrationCycleUseAllowed"])
        self.assertTrue(agent["nextCycleUseAllowed"])
        self.assertIsNotNone(agent["registrationRef"])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "registry"
            content = Path(td) / "resource.txt"
            content.write_text("resource\n", encoding="utf-8")
            checker = Path(td) / "checker.json"
            checker.write_text(json.dumps({"kind": "checker.verdict", "verdict": "PASS", "checker": "checker-agent"}), encoding="utf-8")
            registry.register(root, "resource.demo", "skill", content, "maker-agent", checker, "trail:test")
            self.assertTrue(registry.resolve(root, "resource.demo")["admissibleToPlanner"])
            registry.revoke(root, "resource.demo", "trail:revoke", "superseded")
            self.assertFalse(registry.resolve(root, "resource.demo")["admissibleToPlanner"])
            self.assertTrue(registry.verify(root)["valid"])


if __name__ == "__main__":
    unittest.main()
