import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("queue_candidate", SKILL / "scripts/queue.py")
queue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(queue)


class MessageQueueContractTests(unittest.TestCase):
    def test_checked_candidate_transport_invariants(self):
        agent = json.loads((SKILL / "agents/pmcro-message-queue.json").read_text(encoding="utf-8"))
        self.assertEqual(agent["status"], "checked-candidate")
        self.assertFalse(agent["availableToPlanner"])
        self.assertFalse(agent["authority"]["grantsRuntimeAuthority"])
        self.assertFalse(agent["authority"]["phaseInjectionAllowed"])
        self.assertFalse(agent["authority"]["autoExecutesNextSeed"])
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "queue"
            cfg = queue.init_queue(root, "target-agent", REPO / ".pmcro/protocol/message-kinds.json", 1, 2, 0)
            self.assertEqual(cfg["delivery"], "at-least-once")
            self.assertTrue(cfg["immutableEnvelope"])
            self.assertTrue(cfg["mutableStateSeparated"])
            self.assertFalse(cfg["sharedMutableTrail"])
            self.assertFalse(cfg["grantsAuthority"])
            self.assertFalse(cfg["autoExecutesNextSeed"])


if __name__ == "__main__":
    unittest.main()
