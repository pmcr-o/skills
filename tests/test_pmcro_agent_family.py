import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROLES=['pmcro-orchestrator','pmcro-planner','pmcro-maker','pmcro-checker','pmcro-reflector']
CYCLE=['orchestrate','plan','make','check','reflect']
class AgentFamilyTests(unittest.TestCase):
    def load_agent(self, role):
        p=ROOT/'skills'/role/'agents'/f'{role}.json'
        self.assertTrue(p.exists(), p)
        return json.loads(p.read_text(encoding='utf-8'))
    def test_core_shape_and_full_cycle(self):
        for role in ROLES:
            self.assertTrue((ROOT/'skills'/role/'SKILL.md').exists())
            a=self.load_agent(role)
            self.assertEqual(a['fullInternalCycle'], CYCLE)
            self.assertEqual(len(a['cognition']),5)
            self.assertTrue(a['identity'].startswith('I AM THE '))
            for phase, line in zip(CYCLE,a['cognition']): self.assertIn('I '+phase.upper(), line)
    def test_role_is_not_phase_and_delegation_is_child_cycle(self):
        for role in ROLES:
            a=self.load_agent(role)
            self.assertIn(a['role'], ['orchestrator','planner','maker','checker','reflector'])
            self.assertTrue(a['delegation']['childCycleRequired'])
            self.assertTrue(a['delegation']['childGrantMustBeSubset'])
            self.assertFalse(a['delegation']['automaticNextRoleInvocation'])
    def test_checker_independence_and_no_repair(self):
        c=self.load_agent('pmcro-checker')
        self.assertTrue(c['independentChecker'])
        self.assertFalse(c['checkerPolicy']['repairDuringCheck'])
        self.assertFalse(c['checkerPolicy']['mayCheckOwnMakerOutput'])
        self.assertIn('maker',c['checkerPolicy']['requiredIsolationFromRoles'])
    def test_reflector_exactly_one_unexecuted_seed(self):
        r=self.load_agent('pmcro-reflector')['reflectionPolicy']
        self.assertTrue(r['exactlyOneNextSeed']); self.assertFalse(r['executesNextSeed'])
        self.assertEqual(set(r['operations']), {'CREATE','REFERENCE','PROMOTE','DEFER','SUPERSEDE','DEPENDENCY'})
    def test_api_and_grpc_projection(self):
        api=json.loads((ROOT/'.pmcro/protocol/pmcro-orchestration-api.schema.json').read_text())
        self.assertTrue(api['properties']['transitionPolicy']['properties']['enforced']['const'])
        self.assertTrue(api['properties']['transitionPolicy']['properties']['directRoleCallsRequireControlPlaneAdmission']['const'])
        proto=(ROOT/'.pmcro/projections/grpc/pmcro-orchestration.proto').read_text()
        for name in ['PmcroOrchestration','OrchestratorService','PlannerService','MakerService','CheckerService','ReflectorService']: self.assertIn(name, proto)
if __name__=='__main__': unittest.main()
