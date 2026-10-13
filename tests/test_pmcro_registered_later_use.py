import argparse
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


registry = load_module("pmcro_registry_use", "skills/pmcro-resource-registry/scripts/registry.py")
queue = load_module("pmcro_queue_use", "skills/pmcro-message-queue/scripts/queue.py")


class RegisteredLaterUseTests(unittest.TestCase):
    def canonical_records(self):
        index = json.loads((ROOT / ".pmcro/registry/index.json").read_text(encoding="utf-8"))
        self.assertEqual(index["authority"], "canonical")
        records = {item["resourceId"]: item for item in index["resources"]}
        for rid in ("skill:pmcro-resource-registry", "skill:pmcro-message-queue"):
            self.assertEqual(records[rid]["state"], "registered-checked")
            self.assertTrue(records[rid]["admissibleToPlanner"])
            self.assertIsNone(records[rid]["revocationRef"])
        return records

    def test_first_later_cycle_use_is_bounded_and_transport_is_not_authority(self):
        records = self.canonical_records()
        grant_refs = ["skill:pmcro-resource-registry", "skill:pmcro-message-queue"]
        self.assertEqual(set(grant_refs), set(records))

        with tempfile.TemporaryDirectory() as td:
            temp = Path(td)
            isolated_registry = temp / "registry"
            content = temp / "synthetic-resource.txt"
            content.write_text("synthetic checked resource\n", encoding="utf-8")
            checker = temp / "checker.json"
            checker.write_text(
                json.dumps({"kind": "checker.verdict", "verdict": "PASS", "checker": "synthetic-checker"}),
                encoding="utf-8",
            )

            registration = registry.register(
                isolated_registry,
                "synthetic.resource",
                "capability",
                content,
                "synthetic-maker",
                checker,
                "trail:synthetic:source",
            )
            resolution = registry.resolve(isolated_registry, "synthetic.resource")
            self.assertTrue(resolution["admissibleToPlanner"])
            self.assertTrue(registry.verify(isolated_registry)["valid"])
            self.assertEqual(registration["record"]["state"], "registered-checked")

            queue_root = temp / "queue"
            config = queue.init_queue(
                queue_root,
                "synthetic-checker",
                ROOT / ".pmcro/protocol/message-kinds.json",
                30,
                2,
                0,
            )
            self.assertFalse(config["grantsAuthority"])
            self.assertFalse(config["autoExecutesNextSeed"])
            self.assertFalse(config["sharedMutableTrail"])
            self.assertTrue(config["receiverCreatesLocalTrail"])

            payload = temp / "payload.json"
            payload.write_text(
                json.dumps(
                    {
                        "resolvedResourceId": "synthetic.resource",
                        "sourceTrailRef": "trail:synthetic:source",
                        "receiverLocalTrailRef": "trail:synthetic:receiver",
                        "reflectedNextSeed": "UNEXECUTED: continue only in a fresh Cycle",
                    }
                ),
                encoding="utf-8",
            )
            args = argparse.Namespace(
                kind="agent.handoff",
                message_id="later-use-001",
                trace_id="later-use-001",
                correlation_id="later-use-001",
                parent_message_id=None,
                causation_id=None,
                trail_id="trail:synthetic:source",
                cycle_id="cycle:synthetic:later-use",
                source_agent="pmcro-maker",
                target_agent="synthetic-checker",
                plugin="pmcro",
                skill="pmcro-message-queue",
                payload_file=str(payload),
                evidence_status="CONFIRMED",
                grant_ref=grant_refs,
                delay_seconds=0,
                expires_at=None,
            )
            first = queue.enqueue(queue_root, args)
            self.assertEqual(first["status"], "ENQUEUED")
            inbox = queue_root / "inbox/later-use-001.json"
            original = inbox.read_bytes()

            duplicate = queue.enqueue(queue_root, args)
            self.assertEqual(duplicate["status"], "IDEMPOTENT")

            claimed = queue.claim(queue_root, "worker.synthetic", "later-use-001", None)
            self.assertEqual(claimed["status"], "CLAIMED")
            processing = queue_root / "processing/later-use-001.json"
            self.assertEqual(processing.read_bytes(), original)

            result = temp / "result.json"
            result.write_text(
                json.dumps({"localTrailRef": "trail:synthetic:receiver", "checked": True}),
                encoding="utf-8",
            )
            acked = queue.ack(queue_root, "later-use-001", "worker.synthetic", str(result))
            self.assertEqual(acked["status"], "ACKED")
            receipt = acked["receipt"]
            self.assertEqual(receipt["sourceTrailRef"], "trail:synthetic:source")
            self.assertEqual(receipt["resultDigest"], hashlib.sha256(result.read_bytes()).hexdigest())
            self.assertEqual((queue_root / "completed/later-use-001.json").read_bytes(), original)

            completed = json.loads((queue_root / "completed/later-use-001.json").read_text(encoding="utf-8"))
            self.assertEqual(completed["grantRefs"], grant_refs)
            self.assertIn("UNEXECUTED", completed["payload"]["reflectedNextSeed"])

            # The first real later-use pass intentionally records the discovered
            # conformance blocker instead of hiding it: the canonical message
            # schema requires transportContext, while registered queue v1 does not
            # currently emit that field into the immutable envelope.
            envelope_schema = json.loads((ROOT / ".pmcro/protocol/message-envelope.schema.json").read_text(encoding="utf-8"))
            self.assertIn("transportContext", envelope_schema["required"])
            self.assertNotIn("transportContext", completed)
            self.assertFalse(config["grantsAuthority"])
            self.assertFalse(config["autoExecutesNextSeed"])


if __name__ == "__main__":
    unittest.main()
