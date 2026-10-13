import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class RegistryQueueReconciliationTests(unittest.TestCase):
    def test_durable_messages_are_transport_not_authority(self):
        schema = load(".pmcro/protocol/message-envelope.schema.json")
        ctx = schema["properties"]["transportContext"]["properties"]
        self.assertFalse(ctx["grantsAuthority"]["const"])
        self.assertFalse(ctx["phaseInjectionAllowed"]["const"])
        self.assertFalse(ctx["autoExecutesNextSeed"]["const"])
        self.assertIn("dedupeDigest", schema["required"])
        self.assertIn("contentDigest", schema["required"])

    def test_message_kind_ownership_preserves_phase_law(self):
        kinds = load(".pmcro/protocol/message-kinds.json")
        self.assertEqual(kinds["kinds"]["planner.plan"]["owner"], "planner")
        self.assertEqual(kinds["kinds"]["maker.result"]["owner"], "maker")
        self.assertEqual(kinds["kinds"]["checker.verdict"]["owner"], "checker")
        self.assertEqual(kinds["kinds"]["reflector.reflect"]["owner"], "reflector")
        self.assertIn("only during MAKE", " ".join(kinds["invariants"]))
        self.assertIn("never executes", " ".join(kinds["invariants"]))

    def test_filesystem_spool_is_candidate_and_cannot_auto_continue(self):
        index = load(".pmcro/registry/index.json")
        transport = index["transports"][0]
        self.assertEqual(transport["transportId"], "filesystem-spool-v1")
        self.assertEqual(transport["state"], "candidate-unregistered")
        self.assertFalse(transport["grantsAuthority"])
        self.assertFalse(transport["autoExecutesNextSeed"])

        schema = load(".pmcro/protocol/transport-binding.schema.json")
        props = schema["properties"]
        self.assertEqual(props["delivery"]["const"], "at-least-once")
        self.assertTrue(props["immutableEnvelope"]["const"])
        self.assertTrue(props["mutableStateSeparated"]["const"])
        self.assertTrue(props["ackReceipt"]["const"])
        self.assertFalse(props["sharedMutableTrail"]["const"])
        self.assertFalse(props["grantsAuthority"]["const"])
        self.assertFalse(props["autoExecutesNextSeed"]["const"])

    def test_registry_state_machine_controls_planner_admissibility(self):
        schema = load(".pmcro/protocol/registry-record.schema.json")
        states = {
            block["if"]["properties"]["state"]["const"]: block["then"]["properties"]
            for block in schema["allOf"]
        }
        self.assertFalse(states["generated-unchecked"]["admissibleToPlanner"]["const"])
        self.assertFalse(states["checked-candidate"]["admissibleToPlanner"]["const"])
        self.assertTrue(states["registered-checked"]["admissibleToPlanner"]["const"])
        self.assertFalse(states["revoked"]["admissibleToPlanner"]["const"])
        self.assertFalse(schema["properties"]["physicalDeleteOnRevoke"]["const"])

    def test_capability_graph_resolves_every_validated_resource_through_registry(self):
        graph = load(".pmcro/protocol/capability-graph.schema.json")
        ref = graph["$defs"]["validatedRef"]
        self.assertIn("registryRef", ref["required"])
        self.assertEqual(ref["properties"]["validationState"]["const"], "registered-checked")
        authority = load(".pmcro/registry/authority.json")
        self.assertEqual(authority["canonical"]["registry"], ".pmcro/registry/index.json")

    def test_skill_create_request_uses_progressive_core_and_stays_unchecked(self):
        schema = load(".pmcro/protocol/skill-create-message.schema.json")
        props = schema["properties"]
        self.assertEqual(props["requiredFolders"]["items"]["enum"], ["agents"])
        self.assertEqual(props["requiredFiles"]["items"]["enum"], ["SKILL.md"])
        self.assertEqual(set(props["optionalFolders"]["items"]["enum"]), {"references", "assets", "scripts", "tests"})
        self.assertEqual(props["candidateState"]["const"], "generated-unchecked")
        self.assertTrue(props["registrationRequiredBeforeUse"]["const"])

        example = load("skills/pmcro-skill-lifecycle/assets/skill-create-request.example.json")
        self.assertEqual(example["requiredFolders"], ["agents"])
        self.assertEqual(example["requiredFiles"], ["SKILL.md"])
        self.assertEqual(example["candidateState"], "generated-unchecked")
        self.assertTrue(example["registrationRequiredBeforeUse"])

    def test_skill_creator_create_does_not_imply_other_lifecycle_authority(self):
        creator = load("skills/dotagents-skill-creator/agents/dotagents-skill-creator.json")
        lifecycle = creator["lifecycleCapabilitySeparation"]
        self.assertEqual(lifecycle["CREATE"]["authority"], "registered")
        self.assertTrue(lifecycle["CREATE"]["candidateOnly"])
        for op in ("READ", "UPDATE", "DELETE"):
            self.assertEqual(lifecycle[op]["authority"], "separate-capability-required")
        self.assertEqual(lifecycle["REGISTER"]["authority"], "independent-checker-and-registry-required")
        self.assertEqual(lifecycle["USE"]["authority"], "later-cycle-plan-and-grant-required")

    def test_reconciled_training_candidates_remain_ineligible(self):
        data = load(".pmcro/training/candidates/registry-queue-candidates.json")
        self.assertEqual(data["datasetClass"], "synthetic-contract-examples")
        self.assertFalse(data["trainingEligible"])
        self.assertFalse(data["explicitOptIn"])
        self.assertFalse(data["trainingAuthorityGranted"])
        self.assertFalse(data["containsPrivateReasoning"])
        self.assertFalse(data["containsSecrets"])
        self.assertEqual({r["role"] for r in data["records"]}, {
            "pmcro-orchestrator", "pmcro-planner", "pmcro-maker", "pmcro-checker", "pmcro-reflector"
        })

    def test_adrs_cover_transport_and_registry_decisions(self):
        index = (ROOT / "docs/adr/index.md").read_text(encoding="utf-8")
        for number in (9, 10):
            self.assertIn(f"ADR-{number:04d}:", index)
            self.assertEqual(len(list((ROOT / "docs/adr").glob(f"{number:04d}-*.md"))), 1)


if __name__ == "__main__":
    unittest.main()
