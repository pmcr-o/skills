import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "skills/pmcro-resource-registry/scripts/registry.py"
QUEUE = ROOT / "skills/pmcro-message-queue/scripts/queue.py"
KINDS = ROOT / ".pmcro/protocol/message-kinds.json"


def run_json(*args, expected=0):
    result = subprocess.run([sys.executable, *map(str, args)], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != expected:
        raise AssertionError(f"exit={result.returncode} expected={expected}\nstdout={result.stdout}\nstderr={result.stderr}")
    return json.loads(result.stdout)


def sha(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ResourceRegistryCandidateTests(unittest.TestCase):
    def test_register_resolve_revoke_preserves_verified_history(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "registry"
            content = Path(td) / "skill.txt"
            content.write_text("checked capability\n", encoding="utf-8")
            checker = Path(td) / "checker.json"
            checker.write_text(json.dumps({"kind": "checker.verdict", "verdict": "PASS", "checker": "pmcro-checker"}), encoding="utf-8")

            created = run_json(
                REGISTRY, "register", "--root", root, "--resource-id", "skill.demo", "--kind", "skill",
                "--content", content, "--producer-agent", "pmcro-maker", "--checker-evidence", checker,
                "--trail-ref", "trail:test:registry",
            )
            self.assertEqual(created["record"]["state"], "registered-checked")
            self.assertTrue(created["record"]["availableToPlanner"])
            self.assertNotEqual(created["record"]["producerAgent"], created["record"]["checker"])

            verified = run_json(REGISTRY, "verify", "--root", root)
            self.assertTrue(verified["valid"])
            self.assertEqual(verified["sequence"], 1)

            resolved = run_json(REGISTRY, "resolve", "--root", root, "--resource-id", "skill.demo")
            self.assertTrue(resolved["admissibleToPlanner"])

            run_json(REGISTRY, "revoke", "--root", root, "--resource-id", "skill.demo", "--trail-ref", "trail:test:revoke", "--reason", "superseded")
            after = run_json(REGISTRY, "resolve", "--root", root, "--resource-id", "skill.demo", expected=3)
            self.assertFalse(after["admissibleToPlanner"])
            self.assertTrue(after["revoked"])
            verified_after = run_json(REGISTRY, "verify", "--root", root)
            self.assertTrue(verified_after["valid"])
            self.assertEqual(verified_after["sequence"], 2)
            self.assertEqual(len(list((root / "records").glob("*.json"))), 1)
            self.assertEqual(len(list((root / "events").glob("*.json"))), 2)

    def test_registration_rejects_self_certification(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "registry"
            content = Path(td) / "skill.txt"
            content.write_text("candidate\n", encoding="utf-8")
            checker = Path(td) / "checker.json"
            checker.write_text(json.dumps({"kind": "checker.verdict", "verdict": "PASS", "checker": "pmcro-maker"}), encoding="utf-8")
            halted = run_json(
                REGISTRY, "register", "--root", root, "--resource-id", "skill.self", "--kind", "skill",
                "--content", content, "--producer-agent", "pmcro-maker", "--checker-evidence", checker,
                "--trail-ref", "trail:test:self", expected=2,
            )
            self.assertEqual(halted["status"], "HALT")
            self.assertIn("independently validate", halted["error"])


class MessageQueueCandidateTests(unittest.TestCase):
    def initialize(self, root: Path):
        cfg = run_json(QUEUE, "init", "--root", root, "--agent", "target-agent", "--allowed-kinds-file", KINDS, "--lease-seconds", "1", "--max-attempts", "2", "--retry-base-seconds", "0")
        self.assertFalse(cfg["grantsAuthority"])
        self.assertFalse(cfg["phaseInjectionAllowed"])
        self.assertFalse(cfg["autoExecutesNextSeed"])
        self.assertTrue(cfg["immutableEnvelope"])
        self.assertFalse(cfg["sharedMutableTrail"])
        return cfg

    def enqueue(self, root: Path, message_id: str, payload: Path, kind="maker.result"):
        return run_json(
            QUEUE, "enqueue", "--root", root, "--kind", kind, "--message-id", message_id,
            "--trail-id", "trail:source", "--cycle-id", "cycle:1", "--source-agent", "source-agent",
            "--target-agent", "target-agent", "--plugin", "pmcro", "--skill", "make", "--payload-file", payload,
        )

    def test_idempotency_conflict_claim_and_immutable_ack_receipt(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "queue"
            self.initialize(root)
            payload = Path(td) / "payload.json"
            payload.write_text(json.dumps({"value": 1}), encoding="utf-8")
            first = self.enqueue(root, "msg-1", payload)
            self.assertEqual(first["status"], "ENQUEUED")
            envelope = root / "inbox/msg-1.json"
            before = sha(envelope)
            again = self.enqueue(root, "msg-1", payload)
            self.assertEqual(again["status"], "IDEMPOTENT")

            other = Path(td) / "other.json"
            other.write_text(json.dumps({"value": 2}), encoding="utf-8")
            conflict = run_json(
                QUEUE, "enqueue", "--root", root, "--kind", "maker.result", "--message-id", "msg-1",
                "--trail-id", "trail:source", "--cycle-id", "cycle:1", "--source-agent", "source-agent",
                "--target-agent", "target-agent", "--plugin", "pmcro", "--skill", "make", "--payload-file", other,
                expected=2,
            )
            self.assertEqual(conflict["status"], "HALT")

            claimed = run_json(QUEUE, "claim", "--root", root, "--worker-id", "worker-1", "--message-id", "msg-1")
            self.assertEqual(claimed["status"], "CLAIMED")
            processing = root / "processing/msg-1.json"
            self.assertEqual(before, sha(processing))
            acked = run_json(QUEUE, "ack", "--root", root, "--message-id", "msg-1", "--worker-id", "worker-1")
            self.assertEqual(acked["status"], "ACKED")
            completed = root / "completed/msg-1.json"
            self.assertEqual(before, sha(completed))
            receipt = root / "receipts/msg-1.json"
            receipt_before = sha(receipt)
            run_json(QUEUE, "ack", "--root", root, "--message-id", "msg-1", "--worker-id", "worker-1", expected=2)
            self.assertEqual(receipt_before, sha(receipt))
            self.assertEqual(acked["receipt"]["sourceTrailRef"], "trail:source")

    def test_retry_dead_letter_and_expired_lease_recovery(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "queue"
            self.initialize(root)
            payload = Path(td) / "payload.json"
            payload.write_text("{}", encoding="utf-8")
            self.enqueue(root, "msg-retry", payload)
            run_json(QUEUE, "claim", "--root", root, "--worker-id", "worker-1", "--message-id", "msg-retry")
            first_nack = run_json(QUEUE, "nack", "--root", root, "--message-id", "msg-retry", "--worker-id", "worker-1", "--reason", "retry", "--retry-delay-seconds", "0")
            self.assertEqual(first_nack["status"], "DELAYED")
            run_json(QUEUE, "recover", "--root", root)
            second_claim = run_json(QUEUE, "claim", "--root", root, "--worker-id", "worker-2", "--message-id", "msg-retry")
            self.assertEqual(second_claim["delivery"]["attempt"], 2)
            final_nack = run_json(QUEUE, "nack", "--root", root, "--message-id", "msg-retry", "--worker-id", "worker-2", "--reason", "final")
            self.assertEqual(final_nack["status"], "DEAD_LETTER")
            self.assertTrue((root / "dead-letter/msg-retry.json").is_file())

            self.enqueue(root, "msg-lease", payload)
            run_json(QUEUE, "claim", "--root", root, "--worker-id", "worker-3", "--message-id", "msg-lease")
            state_path = root / "state/msg-lease.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["leaseUntil"] = "2000-01-01T00:00:00Z"
            state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
            recovered = run_json(QUEUE, "recover", "--root", root)
            self.assertTrue(any(row[0] == "msg-lease" for row in recovered["moved"]))
            self.assertTrue((root / "inbox/msg-lease.json").is_file())

    def test_reflected_seed_remains_data_not_execution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "queue"
            cfg = self.initialize(root)
            payload = Path(td) / "reflect.json"
            payload.write_text(json.dumps({"next_seed": {"intent": "future work", "unexecuted": True, "nextCycleStartsAt": "orchestrate"}}), encoding="utf-8")
            self.enqueue(root, "msg-reflect", payload, kind="reflector.reflect")
            self.assertTrue((root / "inbox/msg-reflect.json").is_file())
            self.assertEqual(len(list((root / "processing").glob("*.json"))), 0)
            self.assertFalse(cfg["autoExecutesNextSeed"])


class CandidateLifecycleTests(unittest.TestCase):
    def test_candidates_have_progressive_core_and_manual_parity(self):
        for skill in ("pmcro-resource-registry", "pmcro-message-queue"):
            root = ROOT / "skills" / skill
            self.assertTrue((root / "SKILL.md").is_file())
            agents = list((root / "agents").glob("*.json"))
            self.assertEqual(len(agents), 1)
            agent = json.loads(agents[0].read_text(encoding="utf-8"))
            self.assertEqual(agent["status"], "registered-checked")
            self.assertEqual(agent["checkerVerdictRef"], ".pmcro/evidence/candidate-capabilities-check.json")
            self.assertTrue(agent["availableToPlanner"])
            self.assertFalse(agent["registrationCycleUseAllowed"])
            self.assertTrue(agent["nextCycleUseAllowed"])
            self.assertTrue(agent["manualParity"]["required"])
            self.assertFalse(agent["authority"]["grantsRuntimeAuthority"])
            self.assertIsNotNone(agent["registrationRef"])


if __name__ == "__main__":
    unittest.main()
