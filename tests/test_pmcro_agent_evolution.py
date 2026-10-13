import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class AgentEvolutionTests(unittest.TestCase):
    def test_planner_uses_checked_minimum_capability_graph(self):
        planner = load("skills/pmcro-planner/agents/pmcro-planner.json")
        policy = planner["capabilityPlanningPolicy"]
        self.assertTrue(policy["validatedOnly"])
        self.assertTrue(policy["minimumSufficient"])
        self.assertFalse(policy["inventMissingCapability"])
        self.assertTrue(policy["declareGaps"])
        self.assertTrue(policy["goalExecutionBlockedByGap"])
        self.assertIn("capability_graph", planner["outputs"])
        self.assertIn("capability_gaps", planner["outputs"])

        schema = load(".pmcro/protocol/capability-graph.schema.json")
        checked = schema["$defs"]["validatedRef"]["properties"]["validationState"]["const"]
        self.assertEqual(checked, "registered-checked")
        self.assertEqual(schema["allOf"][0]["then"]["properties"]["capabilityGaps"]["maxItems"], 0)

    def test_skill_creator_is_registered_gap_factory_not_hidden_delegation(self):
        creator = load("skills/dotagents-skill-creator/agents/dotagents-skill-creator.json")
        self.assertEqual(creator["registeredLifecycleAuthority"], "CREATE")
        self.assertNotIn("requiredDelegation", creator)
        gap = creator["capabilityGapPolicy"]
        self.assertTrue(gap["acceptedOnlyFromValidatedPlan"])
        self.assertTrue(gap["createsCandidateOnly"])
        self.assertFalse(gap["candidateAvailableToPlanner"])
        self.assertTrue(gap["requiresIndependentChecker"])
        self.assertTrue(gap["requiresRegistrationBeforeLaterUse"])
        self.assertEqual(creator["agentFactoryPolicy"]["minimumCore"], ["SKILL.md", "agents/*.json"])
        self.assertTrue(creator["agentFactoryPolicy"]["noEmptyOptionalFolders"])

    def test_maker_can_bootstrap_gap_but_not_use_candidate_same_cycle(self):
        maker = load("skills/pmcro-maker/agents/pmcro-maker.json")
        policy = maker["capabilityGapPolicy"]
        self.assertTrue(policy["mayInvokeRegisteredSkillCreator"])
        self.assertEqual(policy["createdCapabilityState"], "generated-unchecked")
        self.assertFalse(policy["createdCapabilityAvailableInSameCycle"])
        self.assertFalse(policy["selfCertificationAllowed"])

    def test_agent_evolution_state_machine_gates_planner_availability(self):
        schema = load(".pmcro/protocol/agent-evolution.schema.json")
        by_state = {
            block["if"]["properties"]["state"]["const"]: block["then"]["properties"]
            for block in schema["allOf"]
        }
        self.assertFalse(by_state["generated-unchecked"]["availableToPlanner"]["const"])
        self.assertFalse(by_state["checked-candidate"]["availableToPlanner"]["const"])
        self.assertTrue(by_state["registered"]["availableToPlanner"]["const"])
        self.assertFalse(by_state["generated-unchecked"]["nextCycleUseAllowed"]["const"])
        self.assertTrue(by_state["registered"]["nextCycleUseAllowed"]["const"])

    def test_reflect_never_reactivates_make_and_starts_fresh_cycle(self):
        reflector = load("skills/pmcro-reflector/agents/pmcro-reflector.json")
        policy = reflector["reflectionPolicy"]
        self.assertFalse(policy["executesNextSeed"])
        self.assertFalse(policy["canReactivateMakerInSameCycle"])
        self.assertEqual(policy["nextCycleStartsAt"], "orchestrate")
        seed_schema = load(".pmcro/protocol/next-seed-intent.schema.json")
        props = seed_schema["properties"]
        self.assertTrue(props["unexecuted"]["const"])
        self.assertFalse(props["executesNextSeed"]["const"])
        self.assertEqual(props["nextCycleStartsAt"]["const"], "orchestrate")

    def test_orchestrator_manages_goal_and_cataloged_agents(self):
        orchestrator = load("skills/pmcro-orchestrator/agents/pmcro-orchestrator.json")
        policy = orchestrator["goalPolicy"]
        self.assertTrue(policy["managesHighLevelGoals"])
        self.assertTrue(policy["selectsOnlyCatalogedAgents"])
        self.assertTrue(policy["passesValidatedCatalogToPlanner"])
        self.assertTrue(policy["doesNotExecuteMakerWork"])

    def test_skill_lifecycle_core_and_later_cycle_use(self):
        lifecycle = load("skills/pmcro-skill-lifecycle/agents/pmcro-skill-lifecycle.json")
        self.assertEqual(lifecycle["requiredFolders"], ["agents"])
        self.assertEqual(lifecycle["requiredFiles"], ["SKILL.md"])
        self.assertEqual(set(lifecycle["optionalFolders"]), {"references", "assets", "scripts", "tests"})
        self.assertFalse(lifecycle["candidateAvailableToPlanner"])
        self.assertTrue(lifecycle["laterUseRequiresFreshCycle"])
        self.assertEqual(lifecycle["lifecycle"], ["CREATE", "CHECK", "REGISTER", "LATER_USE"])

    def test_synthetic_training_candidates_are_safe_and_not_authorized(self):
        candidates = load(".pmcro/training/candidates/agent-evolution-candidates.json")
        self.assertEqual(candidates["datasetClass"], "synthetic-contract-examples")
        self.assertFalse(candidates["trainingEligible"])
        self.assertFalse(candidates["explicitOptIn"])
        self.assertFalse(candidates["trainingAuthorityGranted"])
        self.assertFalse(candidates["containsPrivateReasoning"])
        roles = {row["role"] for row in candidates["records"]}
        self.assertEqual(roles, {"pmcro-orchestrator", "pmcro-planner", "pmcro-maker", "pmcro-checker", "pmcro-reflector"})

    def test_role_eval_profiles_include_evolution_dimensions(self):
        evals = load(".pmcro/evals/pmcro-role-evals.json")
        profiles = load(".pmcro/training/role-dataset-profiles.json")
        profile_map = {row["role"]: row for row in profiles["profiles"]}
        self.assertIn("minimum-capability-graph", evals["pmcro-planner"]["dimensions"])
        self.assertIn("skill-creator-gap-bootstrap", evals["pmcro-maker"]["dimensions"])
        self.assertIn("candidate-state-gating", evals["pmcro-checker"]["dimensions"])
        self.assertIn("fresh-cycle-boundary", evals["pmcro-reflector"]["dimensions"])
        for role, profile in profile_map.items():
            self.assertEqual(set(profile["trainingObjectives"]), set(evals[role]["dimensions"]))

    def test_adrs_for_all_indexed_initial_decisions_exist(self):
        index = (ROOT / "docs/adr/index.md").read_text(encoding="utf-8")
        for number in range(1, 9):
            marker = f"ADR-{number:04d}:"
            self.assertIn(marker, index)
            matches = list((ROOT / "docs/adr").glob(f"{number:04d}-*.md"))
            self.assertEqual(len(matches), 1, marker)


if __name__ == "__main__":
    unittest.main()
