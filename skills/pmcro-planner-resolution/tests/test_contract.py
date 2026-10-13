import importlib.util
import json
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[3]
SPEC = importlib.util.spec_from_file_location("planner_resolution", SKILL / "scripts/resolve_plan.py")
resolver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resolver)


class PlannerResolutionContractTests(unittest.TestCase):
    def test_registered_granted_minimum_graph(self):
        registry = REPO / ".pmcro/registry/index.json"
        required = ["skill:pmcro-resource-registry", "skill:pmcro-message-queue"]
        graph = resolver.resolve(registry, "graph:test", "goal:test", required, required)
        self.assertTrue(graph["goalExecutionEligible"])
        self.assertEqual(len(graph["selectedSkills"]), 2)
        self.assertEqual(graph["capabilityGaps"], [])

    def test_missing_grant_is_a_denied_gap(self):
        registry = REPO / ".pmcro/registry/index.json"
        graph = resolver.resolve(
            registry,
            "graph:test",
            "goal:test",
            ["skill:pmcro-message-queue"],
            [],
        )
        self.assertFalse(graph["goalExecutionEligible"])
        self.assertEqual(graph["capabilityGaps"][0]["resolution"], "deny")

    def test_candidate_agent_remains_unregistered(self):
        agent = json.loads((SKILL / "agents/pmcro-planner-resolution.json").read_text(encoding="utf-8"))
        self.assertFalse(agent["availableToPlanner"])
        self.assertIsNone(agent["registrationRef"])
        self.assertFalse(agent["authority"]["invokesSelectedCapabilities"])


if __name__ == "__main__":
    unittest.main()
