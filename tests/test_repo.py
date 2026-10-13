import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ThoughtTransferRepoTests(unittest.TestCase):
    def test_structural_validator_passes(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_repo.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("PASS:", result.stdout)

    def test_checker_is_separate_and_bounded(self):
        checker = json.loads((ROOT / ".agents/agents/checker.json").read_text(encoding="utf-8"))
        self.assertTrue(checker["independentChecker"])
        self.assertEqual(checker["contextBoundary"], "checker-fresh")
        self.assertEqual(checker["maxTurns"], 1)

    def test_control_plane_uses_validated_resources_and_typed_seeds(self):
        orchestrator = json.loads((ROOT / ".agents/agents/orchestrator.json").read_text(encoding="utf-8"))
        planner = json.loads((ROOT / ".agents/agents/planner.json").read_text(encoding="utf-8"))
        reflector = json.loads((ROOT / ".agents/agents/reflector.json").read_text(encoding="utf-8"))
        self.assertEqual(orchestrator["phaseOrder"], ["orchestrate", "plan", "make", "check", "reflect"])
        self.assertEqual(planner["authority"], "plan-only")
        self.assertIn("validated_resources", planner["inputs"])
        self.assertEqual(reflector["nextSeedLevels"], ["meta", "meta-meta", "meta-meta-meta"])
        handoff = (ROOT / "docs/08-mcp-and-thought-transfer.md").read_text(encoding="utf-8").lower()
        for phrase in ("minimal cross-session handoff", "validated reference", "full transcript", "orchestrate -> plan -> make -> check -> reflect"):
            self.assertIn(phrase, handoff)

    def test_every_installable_skill_has_an_agent_file(self):
        skill_dirs = [path for path in (ROOT / "skills").iterdir() if (path / "SKILL.md").is_file()]
        self.assertTrue(skill_dirs)
        for skill_dir in skill_dirs:
            agent_dir = skill_dir / "agents"
            self.assertTrue(agent_dir.is_dir(), f"{skill_dir.name}/agents")
            agent_files = [path for path in agent_dir.iterdir() if path.is_file()]
            self.assertTrue(agent_files, skill_dir.name)
            self.assertTrue(list(agent_dir.glob("*.json")), f"{skill_dir.name}/agents/*.json")
            for folder in ("scripts", "references", "assets", "tests"):
                optional_dir = skill_dir / folder
                if optional_dir.is_dir():
                    self.assertTrue(any(path.is_file() for path in optional_dir.rglob("*")), f"{skill_dir.name}/{folder} must not be empty")
            prompt_file = skill_dir / "references/sample-prompts.md"
            if prompt_file.is_file():
                self.assertGreaterEqual(prompt_file.read_text(encoding="utf-8").count("## Prompt "), 1)

    def test_examples_have_nearby_documentation(self):
        for skill_dir in (ROOT / "skills").iterdir():
            assets = skill_dir / "assets"
            if not assets.is_dir():
                continue
            asset_files = [path for path in assets.rglob("*") if path.is_file() and path.name != "README.md"]
            if asset_files:
                self.assertTrue((assets / "README.md").is_file(), skill_dir.name)
        for path in (ROOT / "examples/README.md", ROOT / "templates/README.md", ROOT / "docs/18-example-artifact-documentation.md"):
            self.assertTrue(path.is_file(), path)

    def test_skill_creator_template_mirrors_input_output_contract(self):
        manifest = json.loads((ROOT / "templates/skill-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["contractVersion"], "pmcro.skill/v1")
        self.assertEqual(set(manifest["messageContract"]), {"input", "output", "accept", "deny"})
        self.assertEqual(manifest["requiredFolders"], ["agents"])
        self.assertEqual(set(manifest["optionalFolders"]), {"references", "assets", "scripts", "tests"})
        self.assertEqual(manifest["requiredFiles"], ["SKILL.md"])
        self.assertIn("agents/*.json", manifest["requiredFilePatterns"])
        self.assertEqual(manifest["progressiveDisclosure"]["core"], ["SKILL.md", "agents/"])
        self.assertFalse(manifest["progressiveDisclosure"]["emptyOptionalFoldersAllowed"])
        self.assertFalse(manifest["samplePrompts"]["required"])
        self.assertEqual(manifest["samplePrompts"]["maxPrompts"], 5)
        self.assertEqual(manifest["authoringGate"]["entrypoint"], "@skill-creator /create-skill")
        self.assertEqual(manifest["authoringGate"]["messageKind"], "skill.create.request")
        self.assertEqual(manifest["authoringGate"]["marketplaceRegistration"], "after-independent-checker")
        template = (ROOT / "templates/SKILL.md.tmpl").read_text(encoding="utf-8")
        for phrase in ("## Input and output contract", "### Input", "### Output", "agents/agent.json", "optional sample prompts"):
            self.assertIn(phrase.lower(), template.lower())

    def test_sample_prompts_are_bounded_copy_paste_surfaces(self):
        import re

        pattern = re.compile(r"(?ms)^## Prompt [^\n]*\n+```text\s*\n(.*?)\n```")
        for skill_dir in (ROOT / "skills").iterdir():
            if not (skill_dir / "SKILL.md").is_file():
                continue
            prompt_file = skill_dir / "references/sample-prompts.md"
            if not prompt_file.is_file():
                continue
            prompts = pattern.findall(prompt_file.read_text(encoding="utf-8"))
            self.assertGreaterEqual(len(prompts), 1, skill_dir.name)
            self.assertLessEqual(len(prompts), 5, skill_dir.name)
            self.assertTrue(all(prompt.strip() and len(prompt.strip()) <= 600 for prompt in prompts), skill_dir.name)

    def test_dotagents_creator_child_template_declares_machine_contract(self):
        template = (ROOT / "skills/dotagents-skill-creator/assets/templates/skill/agents/agent.json.tmpl").read_text(encoding="utf-8")
        for phrase in ('"inputs"', '"outputs"', '"accept"', '"deny"', '"defaultOutputContract"'):
            self.assertIn(phrase, template)
        self.assertIn('"${{skill_name}}"', template)

    def test_trail_contains_a_reflective_next_seed(self):
        events = [
            json.loads(line)
            for line in (ROOT / ".pmcro/trails/0001-source-seed.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(events[0]["type"], "raw_intent")
        self.assertTrue(any(event["type"] == "next_seed" for event in events))
        self.assertTrue(any(event["phase"] == "reflect" for event in events))

    def test_backward_and_forward_frames_are_explicit(self):
        backward = json.loads((ROOT / "examples/backward-learning-frame.json").read_text(encoding="utf-8"))
        forward = json.loads((ROOT / "examples/forward-story-frame.json").read_text(encoding="utf-8"))
        self.assertEqual(backward["flow"], "backward")
        self.assertEqual(forward["flow"], "forward")
        self.assertEqual(backward["trailEvent"]["flow"], backward["flow"])
        self.assertEqual(forward["trailEvent"]["flow"], forward["flow"])

    def test_progressive_flow_projects_only_redacted_candidates(self):
        registry = json.loads((ROOT / "skills/progressive-trail-flow/assets/domain-registry.json").read_text(encoding="utf-8"))
        domain_ids = {domain["id"] for domain in registry["domains"]}
        self.assertTrue({"dotnet-skills", "pmcro", "mcp", "maf", "figma"}.issubset(domain_ids))
        for name, flow in (
            ("backward-training-candidates.jsonl", "backward"),
            ("forward-training-candidates.jsonl", "forward"),
        ):
            rows = [json.loads(line) for line in (ROOT / "examples" / name).read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertTrue(rows)
            self.assertTrue(all(row["status"] == "candidate" for row in rows))
            self.assertTrue(all(row["flow"] == flow for row in rows))
            self.assertTrue(all(row["metadata"]["redaction"] == "applied" for row in rows))

    def test_each_philosophical_voice_has_a_refusal(self):
        required = ("I AM:", "I NOTICE:", "I ASK:", "I REFUSE:", "I HAND OFF:")
        for path in (ROOT / "simulations").glob("i-am-*.md"):
            text = path.read_text(encoding="utf-8")
            for marker in required:
                self.assertIn(marker, text, path.name)

    def test_activation_bundle_is_progressive_and_text_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "source-seed.txt"
            source.write_text("deterministic activation bundle source seed\n", encoding="utf-8")
            out_dir = Path(temp_dir) / "bundle"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/build_activation_bundle.py"),
                    "--repo",
                    str(ROOT),
                    "--source-seed",
                    str(source),
                    "--commit",
                    "test-commit",
                    "--out-dir",
                    str(out_dir),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            packages = sorted(out_dir.glob("*.txt"))
            self.assertEqual(len(packages), 6)
            self.assertEqual(packages[0].name, "thought-transfer-pmcro-00-core.txt")
            core = packages[0].read_text(encoding="utf-8")
            self.assertIn("REQUEST_PACKAGE: 01-domains", core)
            self.assertIn("PACKAGE_ID: 00-core", core)
            self.assertIn("05-source | thought-transfer-pmcro-05-source.txt", core)
            manifest = json.loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(len(manifest["packages"]), 6)
            self.assertEqual(manifest["packages"][0]["package_id"], "00-core")
            self.assertTrue(all(path.suffix == ".txt" for path in packages))

    def test_catalog_surface_is_read_only_and_two_session_design_is_explicit(self):
        surface = json.loads((ROOT / ".agents/agents/catalog-mcp-server.json").read_text(encoding="utf-8"))
        self.assertEqual(surface["contextBoundary"], "read-only-catalog")
        self.assertFalse(surface["independentChecker"])
        design = (ROOT / "docs/12-catalog-mcp-server-image.md").read_text(encoding="utf-8").lower()
        for phrase in ("two-session boundary", "checked trail", "read-only", "next seed"):
            self.assertIn(phrase, design)

    def test_marketplace_product_repository_is_a_checked_child(self):
        design = (ROOT / "docs/07-skill-marketplace.md").read_text(encoding="utf-8").lower()
        for phrase in ("actual product repository", "versioned declarative template", "independent check", "staged", "promoted"):
            self.assertIn(phrase, design)

    def test_reflect_skill_waits_for_checker_and_routes_messy_seed(self):
        reflector = json.loads((ROOT / ".agents/agents/reflector.json").read_text(encoding="utf-8"))
        self.assertEqual(reflector["invokedMarketplaceSkill"], "reflect")
        self.assertIn("checker.verdict", reflector["waitFor"])
        skill = (ROOT / "skills/reflect/SKILL.md").read_text(encoding="utf-8").lower()
        for phrase in ("wait", "completed", "independent", "unexecuted", "messy seed"):
            self.assertIn(phrase, skill)

    def test_reflect_scripts_wait_and_route(self):
        reflect_script = ROOT / "skills/reflect/scripts/reflect.py"
        route_script = ROOT / "skills/reflect/scripts/route_seed.py"
        queue = ROOT / "skills/reflect/assets/examples/checker-queue.jsonl"
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "reflect.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(reflect_script),
                    "--queue",
                    str(queue),
                    "--level",
                    "meta2",
                    "--prompt-intent",
                    "Re-open the seed as raw intent.",
                    "--required-resource",
                    "pmcro-messages-protocol",
                    "--out",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            frame = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(frame["kind"], "reflector.reflect")
            self.assertTrue(frame["payload"]["next_seed"]["unexecuted"])
            routed = subprocess.run(
                [sys.executable, str(route_script), str(output)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(routed.returncode, 0, routed.stderr + routed.stdout)
            decision = json.loads(routed.stdout)
            self.assertEqual(decision["display_level"], "meta-meta")
            self.assertEqual(decision["first_target"], "planner")
            self.assertTrue(decision["unexecuted"])

    def test_session_marketplace_contract_has_typed_decisions(self):
        agent = json.loads((ROOT / "skills/pmcro-session-marketplace/agents/session-marketplace.json").read_text(encoding="utf-8"))
        for field in ("inputs", "outputs", "accept", "deny"):
            self.assertTrue(agent[field], field)
        text = (ROOT / "skills/pmcro-session-marketplace/SKILL.md").read_text(encoding="utf-8").lower()
        for phrase in ("simulation: true", "verified: false", "redacted", "unexecuted", "independent checker"):
            self.assertIn(phrase, text)

    def test_pmcro_plugin_registers_reflect_and_session_marketplace(self):
        catalog = json.loads((ROOT / ".agents/plugins/marketplace.json").read_text(encoding="utf-8"))
        plugin = catalog["plugins"][0]
        skills = {skill["id"]: skill for skill in plugin["skills"]}
        self.assertEqual(plugin["id"], "pmcro")
        self.assertIn("reflect", skills)
        self.assertIn("pmcro-session-marketplace", skills)
        self.assertIn("pmcro-agent-surface", skills)
        self.assertIn("pmcro-output-conventions", skills)
        for skill in skills.values():
            for field in ("input", "output", "accept", "deny"):
                self.assertTrue(skill[field], f"{skill['id']}:{field}")

    def test_recursive_pmcro_plugin_declares_core_skills_and_maf_adapters(self):
        plugin = json.loads((ROOT / "plugins/pmcro/plugin.json").read_text(encoding="utf-8"))
        skill_ids = {skill["id"] for skill in plugin["skills"]}
        self.assertTrue(
            {"pmcro-bip", "pmcro-agent-surface", "pmcro-output-conventions", "pmcro-marketplace", "pmcro-github-marketplace", "pmcro-trail-product", "pmcro-clean-architecture", "pmcro-skill-lifecycle", "pmcro-product-repo"}
            .issubset(skill_ids)
        )
        adapter_ids = {adapter["id"] for adapter in plugin["runtimeAdapters"]}
        self.assertTrue({"maf-native-filesystem", "maf-mcp-tools", "maf-workflows", "desktop-commander"}.issubset(adapter_ids))
        self.assertEqual(plugin["samplePromptContract"], "templates/skill-manifest.json#samplePrompts")
        self.assertEqual(plugin["policy"]["authoringGate"]["messageKind"], "skill.create.request")

    def test_product_repository_template_has_bounded_autonomy_and_generic_trail(self):
        validator = ROOT / "skills/pmcro-product-repo/scripts/validate_product_repo.py"
        result = subprocess.run([sys.executable, str(validator)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("PASS: product repository template", result.stdout)
        manifest = json.loads((ROOT / "templates/product-repo/product.manifest.json").read_text(encoding="utf-8"))
        grant = json.loads((ROOT / "templates/product-repo/autonomy-grant.example.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["trailContract"], ".pmcro/protocol/trail-event.schema.json")
        self.assertEqual(manifest["promotion"], "checker-verified-only")
        self.assertTrue(grant["autoApprove"])
        self.assertTrue(grant["checker"]["required"])
        self.assertIn("local-commit", grant["scope"]["operations"])
        self.assertNotIn("credentials", grant["scope"]["operations"])
        trail_validator = ROOT / "templates/product-repo/scripts/validate_trail.py"
        trail = ROOT / "templates/product-repo/.pmcro/trails/example.jsonl"
        trail_result = subprocess.run([sys.executable, str(trail_validator), "--trail", str(trail)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(trail_result.returncode, 0, trail_result.stderr + trail_result.stdout)
        text = (ROOT / "plugins/pmcro/references/maf-native-filesystem.md").read_text(encoding="utf-8").lower()
        for phrase in (".agents/", ".pmcro/", "read-only", "maf-workflows", "maf-mcp-tools"):
            self.assertIn(phrase, text)
        adapter_text = (ROOT / "docs/22-desktop-commander-adapter.md").read_text(encoding="utf-8").lower()
        for phrase in ("sample-child", "powershell", "finite timeout", "github repository"):
            self.assertIn(phrase, adapter_text)

    def test_skill_creator_lifecycle_is_the_required_first_frame(self):
        schema = json.loads((ROOT / ".pmcro/protocol/skill-create-message.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["properties"]["kind"]["const"], "skill.create.request")
        self.assertEqual(schema["properties"]["mode"]["enum"], ["simulate", "apply"])
        lifecycle = (ROOT / "plugins/pmcro/references/skill-creator-lifecycle.md").read_text(encoding="utf-8").lower()
        for phrase in ("skill.create.request", "@skill-creator /create-skill", "orchestrate", "plan", "make", "check", "reflect", "after-independent-checker", "sample prompts"):
            self.assertIn(phrase, lifecycle)

    def test_clean_architecture_builder_maps_runtime_adapters(self):
        validator = ROOT / "skills/pmcro-clean-architecture/scripts/validate_architecture.py"
        result = subprocess.run([sys.executable, str(validator), "--repo", str(ROOT)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        mapping = (ROOT / "skills/pmcro-clean-architecture/references/runtime-mapping.md").read_text(encoding="utf-8").lower()
        for phrase in ("pmcr-o", "maf", "codeact", "harness", "mcp", "independent checker"):
            self.assertIn(phrase, mapping)

    def test_agent_independence_and_catalog_roles_are_distinct(self):
        design = (ROOT / "docs/21-agent-independence-and-catalogs.md").read_text(encoding="utf-8").lower()
        reference = (ROOT / "plugins/pmcro/references/agent-independence-and-catalogs.md").read_text(encoding="utf-8").lower()
        for phrase in ("independently", "addressable", "independent checker", "read-only progressive disclosure", "does not certify", "self-check"):
            self.assertIn(phrase, design)
        self.assertIn("independentchecker: true", reference)
        self.assertIn("independentchecker: false", reference)
        for path in (ROOT / ".agents/agents").glob("*.json"):
            self.assertTrue(json.loads(path.read_text(encoding="utf-8"))["independentSurface"], path.name)
        for path in (ROOT / "skills").glob("*/agents/*.json"):
            self.assertTrue(json.loads(path.read_text(encoding="utf-8"))["independentSurface"], path.name)

    def test_generic_concepts_map_across_domains_without_blind_copying(self):
        mapping = (ROOT / "docs/19-generic-concept-mapping.md").read_text(encoding="utf-8").lower()
        reference = (ROOT / "plugins/pmcro/references/generic-concept-mapping.md").read_text(encoding="utf-8").lower()
        for phrase in (
            "semantically reusable",
            "canonical envelope",
            "domain adapter",
            "semantic mapping",
            "runtime mapping",
            "evidence mapping",
            "not interchangeable",
            "independent checker",
        ):
            self.assertIn(phrase, mapping)
        repository = (ROOT / "docs/17-clean-architecture-generic-repository.md").read_text(encoding="utf-8").lower()
        for operation in ("addasync", "getbyidasync", "listasync", "updateasync", "deleteasync"):
            self.assertIn(operation, repository)
        self.assertIn("no per-entity crud", repository)
        self.assertIn("repository is needed", repository)
        self.assertIn("another", repository)
        self.assertIn("typed repository or adapter", repository)
        self.assertIn("scope, grant, phase meaning", reference)
        for phrase in ("universal lifecycle", "progressive disclosure", "physical erasure", "specialized actions"):
            self.assertIn(phrase, mapping)

    def test_global_personal_and_project_surfaces_are_explicitly_scoped(self):
        global_surface = json.loads((ROOT / ".agents/agents/global-orchestrator.json").read_text(encoding="utf-8"))
        personal_surface = json.loads((ROOT / ".agents/agents/personal-orchestrator.json").read_text(encoding="utf-8"))
        project_surface = json.loads((ROOT / ".agents/agents/projectname-orchestration-service.json").read_text(encoding="utf-8"))
        self.assertEqual(global_surface["scope"], "global")
        self.assertEqual(personal_surface["scope"], "personal")
        self.assertEqual(personal_surface["extends"]["ref"], global_surface["id"])
        self.assertEqual(personal_surface["extends"]["policy"], "non-widening")
        self.assertEqual(project_surface["scope"], "project")
        self.assertEqual(project_surface["capabilityType"], "service")
        for surface in (global_surface, personal_surface, project_surface):
            self.assertTrue(surface["status"]["simulation"])
            self.assertFalse(surface["status"]["verified"])

    def test_agent_surface_api_simulation_is_labeled_and_read_only(self):
        request = ROOT / "skills/pmcro-agent-surface/assets/agent-surface-request.json"
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "skills/pmcro-agent-surface/scripts/simulate_agent_api.py"),
                "--repo",
                str(ROOT),
                "--request",
                str(request),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["statusCode"], 200)
        self.assertTrue(payload["status"]["simulation"])
        self.assertFalse(payload["status"]["verified"])
        self.assertEqual(payload["status"]["evidenceTier"], "pattern-valid")
        self.assertEqual(payload["agent"]["scope"], "global")

    def test_memory_governance_accepts_checked_record_and_rejects_secret_candidate(self):
        validator = ROOT / "skills/pmcro-memory-governance/scripts/validate_memory.py"
        valid = subprocess.run(
            [sys.executable, str(validator), str(ROOT / "skills/pmcro-memory-governance/assets/valid-memory-record.json")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        invalid = subprocess.run(
            [sys.executable, str(validator), str(ROOT / "skills/pmcro-memory-governance/assets/invalid-memory-record.json")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
        self.assertEqual(invalid.returncode, 1)
        self.assertIn("FAIL:", invalid.stdout)

    def test_memory_is_separate_from_raw_trail_and_provider_context(self):
        design = (ROOT / "docs/14-agent-memory-governance.md").read_text(encoding="utf-8").lower()
        for phrase in ("raw trail", "checkpoint", "scope", "retention", "revocation", "enforced configuration", "mcp"):
            self.assertIn(phrase, design)

    def test_skill_output_profile_renders_a_labeled_dotnet_console_projection(self):
        renderer = ROOT / "skills/pmcro-output-conventions/scripts/render_console.py"
        fixture = ROOT / "skills/pmcro-output-conventions/assets/planner-simulation.json"
        result = subprocess.run(
            [sys.executable, str(renderer), str(fixture)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        for phrase in ("I AM: pmcro-planner", "PHASE: plan", "MODE: simulate", "SIMULATION: true", "VERIFIED: false", "I HAND OFF:"):
            self.assertIn(phrase, result.stdout)

    def test_generic_crud_simulation_supports_dotnet_model_and_safe_delete(self):
        simulator = ROOT / "skills/pmcro-generic-crud/scripts/simulate_crud.py"
        model_request = ROOT / "skills/pmcro-generic-crud/assets/dotnet-model-request.json"
        clean_request = ROOT / "skills/pmcro-generic-crud/assets/dotnet-clean-architecture-request.json"
        unit_request = ROOT / "skills/pmcro-generic-crud/assets/dotnet-unit-of-work-request.json"
        delete_request = ROOT / "skills/pmcro-generic-crud/assets/delete-request.json"
        model = subprocess.run([sys.executable, str(simulator), str(model_request)], cwd=ROOT, capture_output=True, text=True)
        clean = subprocess.run([sys.executable, str(simulator), str(clean_request)], cwd=ROOT, capture_output=True, text=True)
        unit = subprocess.run([sys.executable, str(simulator), str(unit_request)], cwd=ROOT, capture_output=True, text=True)
        delete = subprocess.run([sys.executable, str(simulator), str(delete_request)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(model.returncode, 0, model.stderr)
        self.assertEqual(clean.returncode, 0, clean.stderr)
        self.assertEqual(unit.returncode, 0, unit.stderr)
        self.assertEqual(delete.returncode, 0, delete.stderr)
        model_payload = json.loads(model.stdout)
        clean_payload = json.loads(clean.stdout)
        unit_payload = json.loads(unit.stdout)
        delete_payload = json.loads(delete.stdout)
        self.assertEqual(model_payload["crud"]["resource"]["kind"], "dotnet-base-model")
        self.assertEqual(model_payload["crud"]["operation"], "update")
        self.assertTrue(model_payload["simulation"])
        self.assertFalse(model_payload["verified"])
        self.assertEqual(delete_payload["output"]["decisions"], ["revocation-planned"])
        self.assertIn("physical delete by default", delete_payload["deny"])
        model_source = (ROOT / "skills/pmcro-generic-crud/assets/PmcroResource.cs").read_text(encoding="utf-8")
        clean_source = (ROOT / "skills/pmcro-generic-crud/assets/CleanArchitectureEntityRepository.cs").read_text(encoding="utf-8")
        self.assertIn("abstract record PmcroResource<TId, TVersion>", model_source)
        self.assertIn("IPmcroCrudStore<TResource, TId, TVersion>", model_source)
        self.assertEqual(clean_payload["crud"]["resource"]["kind"], "clean-architecture-repository")
        self.assertEqual(clean_payload["crud"]["architecture"], "clean-architecture")
        self.assertTrue(clean_payload["simulation"])
        self.assertIn("domain:EntityBase<Guid>", clean_payload["output"]["artifacts"])
        self.assertIn("Guid.NewGuid()", clean_source)
        self.assertIn("IGenericRepository<TEntity>", clean_source)
        self.assertIn("where TEntity : EntityBase", clean_source)
        self.assertIn("Task<bool> DeleteAsync", clean_source)
        self.assertIn("IUnitOfWork", clean_source)
        self.assertIn("Repository<TEntity>()", clean_source)
        self.assertIn("SaveChangesAsync", clean_source)
        self.assertEqual(unit_payload["crud"]["architecture"], "clean-architecture")
        self.assertTrue(unit_payload["simulation"])
        self.assertIn("application:IUnitOfWork", unit_payload["output"]["artifacts"])
        self.assertIn("crud-for-new-entity:inherited-from-EntityBase", unit_payload["output"]["artifacts"])


if __name__ == "__main__":
    unittest.main()
