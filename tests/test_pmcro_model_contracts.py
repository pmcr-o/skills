import json, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROLES=['pmcro-orchestrator','pmcro-planner','pmcro-maker','pmcro-checker','pmcro-reflector']
class ModelContractTests(unittest.TestCase):
    def test_model_binding_is_provider_neutral(self):
        s=json.loads((ROOT/'.pmcro/protocol/model-binding.schema.json').read_text())
        provider=s['properties']['provider']
        self.assertEqual(provider['type'],'string'); self.assertNotIn('enum',provider)
        self.assertFalse(s['properties']['grantsCapabilityAuthority']['const'])
    def test_training_is_opt_in_and_excludes_sensitive_classes(self):
        s=json.loads((ROOT/'.pmcro/protocol/training-data-eligibility.schema.json').read_text())
        self.assertFalse(s['properties']['defaultEligible']['const']); self.assertTrue(s['properties']['explicitOptIn']['const'])
        text=json.dumps(s)
        for value in ['secrets','credentials','private-reasoning','unapproved-user-content']: self.assertIn(value,text)
    def test_lifecycle_requires_eval_provenance_and_independent_check(self):
        s=json.loads((ROOT/'.pmcro/protocol/model-lifecycle.schema.json').read_text())
        rg=s['properties']['registrationGate']['properties']
        self.assertTrue(rg['independentCheckRequired']['const']); self.assertTrue(rg['evaluationRequired']['const']); self.assertTrue(rg['provenanceRequired']['const'])
        ci=s['properties']['checkerIndependence']['properties']
        self.assertTrue(ci['makerAndCheckerBindingsMustDiffer']['const']); self.assertFalse(ci['checkerMayRepairCandidate']['const'])
    def test_ollama_projection_has_five_unresolved_candidate_bindings(self):
        p=json.loads((ROOT/'.pmcro/projections/ollama/pmcro-role-models.json').read_text())
        self.assertEqual(p['provider'],'ollama'); self.assertEqual(p['status'],'candidate-untrained-unregistered'); self.assertFalse(p['runtimeAuthorityGranted'])
        self.assertEqual({b['agentRole'] for b in p['bindings']}, set(ROLES))
        for b in p['bindings']:
            self.assertIsNone(b['resolvedModelRef']); self.assertEqual(b['status'],'candidate-untrained'); self.assertFalse(b['grantsCapabilityAuthority'])
        self.assertNotEqual(p['checkerIsolation']['makerBinding'],p['checkerIsolation']['checkerBinding'])
    def test_role_eval_contracts_are_distinct(self):
        e=json.loads((ROOT/'.pmcro/evals/pmcro-role-evals.json').read_text())
        for r in ROLES: self.assertIn(r,e); self.assertTrue(e[r]['dimensions'])
        self.assertIn('no-repair',e['pmcro-checker']['dimensions'])
        self.assertIn('exactly-one-next-seed',e['pmcro-reflector']['dimensions'])
    def test_no_ghostwriter_materialization(self):
        self.assertFalse((ROOT/'skills/GHOSTWRITER').exists()); self.assertFalse((ROOT/'skills/ghostwriter').exists())
if __name__=='__main__': unittest.main()
