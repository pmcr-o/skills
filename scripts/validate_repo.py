#!/usr/bin/env python3
"""Validate the structural contracts for the Thought Transfer example repo."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise AssertionError(message)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def main() -> int:
    required = [
        "README.md",
        ".agents/README.md",
        ".pmcro/protocol/trail-schema.json",
        ".pmcro/protocol/phase-envelope.json",
        ".pmcro/protocol/agent-surface-envelope.json",
        ".pmcro/protocol/skill-create-message.schema.json",
        ".agents/agents/pmcro-product-repo.json",
        ".pmcro/trails/0001-source-seed.jsonl",
        "templates/skill-manifest.json",
        "templates/SKILL.md.tmpl",
        "templates/sample-prompts.md.tmpl",
        "templates/agent-surface.json",
        "templates/skill-output-envelope.json",
        "templates/crud-envelope.json",
        "templates/README.md",
        "plugins/pmcro/plugin.json",
        "plugins/pmcro/README.md",
        "plugins/pmcro/skills/README.md",
        "plugins/pmcro/references/architecture.md",
        "plugins/pmcro/references/cascading-orchestration.md",
        "plugins/pmcro/references/progressive-disclosure.md",
        "plugins/pmcro/references/thought-transfer.md",
        "plugins/pmcro/references/trail-schema.md",
        "plugins/pmcro/references/dependency-map.md",
        "plugins/pmcro/references/generic-concept-mapping.md",
        "plugins/pmcro/references/agent-independence-and-catalogs.md",
        "plugins/pmcro/references/desktop-commander.md",
        "plugins/pmcro/references/maf-native-filesystem.md",
        "plugins/pmcro/references/maf-chain-output.md",
        "plugins/pmcro/references/skill-creator-lifecycle.md",
        "skills/pmcro-skill-lifecycle/SKILL.md",
        "skills/pmcro-skill-lifecycle/agents/openai.yaml",
        "skills/pmcro-skill-lifecycle/agents/pmcro-skill-lifecycle.json",
        "skills/pmcro-skill-lifecycle/references/sample-prompts.md",
        "skills/pmcro-skill-lifecycle/assets/README.md",
        "skills/pmcro-skill-lifecycle/scripts/validate.ps1",
        "skills/pmcro-skill-lifecycle/tests/README.md",
        "skills/pmcro-product-repo/SKILL.md",
        "skills/pmcro-product-repo/agents/openai.yaml",
        "skills/pmcro-product-repo/agents/pmcro-product-repo.json",
        "skills/pmcro-product-repo/references/sample-prompts.md",
        "skills/pmcro-product-repo/references/product-repo-contract.md",
        "skills/pmcro-product-repo/references/generic-trail-contract.md",
        "skills/pmcro-product-repo/references/friend-run.md",
        "skills/pmcro-product-repo/assets/README.md",
        "skills/pmcro-product-repo/assets/autonomy-grant.example.json",
        "skills/pmcro-product-repo/assets/product-repo-request.example.json",
        "skills/pmcro-product-repo/scripts/validate.ps1",
        "skills/pmcro-product-repo/scripts/validate_product_repo.py",
        "skills/pmcro-product-repo/tests/README.md",
        "templates/product-repo/README.md",
        "templates/product-repo/product.manifest.json",
        "templates/product-repo/autonomy-grant.example.json",
        "templates/product-repo/.agents/README.md",
        "templates/product-repo/.agents/agents/orchestrator.json",
        "templates/product-repo/.agents/agents/checker.json",
        "templates/product-repo/.agents/agents/reflector.json",
        "templates/product-repo/.pmcro/protocol/trail-event.schema.json",
        "templates/product-repo/.pmcro/trails/README.md",
        "templates/product-repo/.pmcro/trails/example.jsonl",
        "templates/product-repo/scripts/validate.ps1",
        "templates/product-repo/scripts/validate_trail.py",
        "templates/product-repo/tests/README.md",
        "skills/thought-transfer/SKILL.md",
        "skills/thought-transfer/agents/openai.yaml",
        "skills/thought-transfer/references/lens-mappings.md",
        "skills/thought-transfer/references/trail-contract.md",
        "skills/thought-transfer/assets/frame-template.json",
        "skills/thought-transfer/scripts/render_frame.py",
        "skills/thought-transfer/scripts/validate_frame.py",
        "skills/progressive-trail-flow/SKILL.md",
        "skills/progressive-trail-flow/agents/openai.yaml",
        "skills/progressive-trail-flow/references/domain-registry.md",
        "skills/progressive-trail-flow/references/training-projection.md",
        "skills/progressive-trail-flow/references/progressive-disclosure.md",
        "skills/progressive-trail-flow/assets/domain-registry.json",
        "skills/progressive-trail-flow/scripts/project_training.py",
        "skills/pmcro-agent-surface/SKILL.md",
        "skills/pmcro-agent-surface/agents/openai.yaml",
        "skills/pmcro-agent-surface/agents/agent-surface.json",
        "skills/pmcro-agent-surface/references/agent-surface-contract.md",
        "skills/pmcro-agent-surface/references/simulation-parity.md",
        "skills/pmcro-agent-surface/assets/agent-surface-request.json",
        "skills/pmcro-agent-surface/assets/manifest.schema.json",
        "skills/pmcro-agent-surface/scripts/simulate_agent_api.py",
        "skills/pmcro-agent-surface/scripts/validate_surface.py",
        "skills/pmcro-memory-governance/SKILL.md",
        "skills/pmcro-memory-governance/agents/openai.yaml",
        "skills/pmcro-memory-governance/agents/memory-governance.json",
        "skills/pmcro-memory-governance/references/memory-contract.md",
        "skills/pmcro-memory-governance/references/enterprise-checklist.md",
        "skills/pmcro-memory-governance/assets/valid-memory-record.json",
        "skills/pmcro-memory-governance/assets/invalid-memory-record.json",
        "skills/pmcro-memory-governance/scripts/validate_memory.py",
        "skills/pmcro-output-conventions/SKILL.md",
        "skills/pmcro-output-conventions/agents/openai.yaml",
        "skills/pmcro-output-conventions/agents/output-conventions.json",
        "skills/pmcro-output-conventions/references/envelope.md",
        "skills/pmcro-output-conventions/references/maf-chain.md",
        "skills/pmcro-output-conventions/assets/planner-simulation.json",
        "skills/pmcro-output-conventions/scripts/render_console.py",
        "skills/pmcro-generic-crud/SKILL.md",
        "skills/pmcro-generic-crud/agents/openai.yaml",
        "skills/pmcro-generic-crud/agents/generic-crud.json",
        "skills/pmcro-generic-crud/references/crud-contract.md",
        "skills/pmcro-generic-crud/references/safety-and-simulation.md",
        "skills/pmcro-generic-crud/assets/create-request.json",
        "skills/pmcro-generic-crud/assets/delete-request.json",
        "skills/pmcro-generic-crud/assets/PmcroResource.cs",
        "skills/pmcro-generic-crud/assets/CleanArchitectureEntityRepository.cs",
        "skills/pmcro-generic-crud/assets/dotnet-model-request.json",
        "skills/pmcro-generic-crud/assets/dotnet-clean-architecture-request.json",
        "skills/pmcro-generic-crud/assets/dotnet-unit-of-work-request.json",
        "skills/pmcro-generic-crud/scripts/simulate_crud.py",
        "skills/pmcro-clean-architecture/SKILL.md",
        "skills/pmcro-clean-architecture/agents/openai.yaml",
        "skills/pmcro-clean-architecture/agents/clean-architecture.json",
        "skills/pmcro-clean-architecture/references/layers.md",
        "skills/pmcro-clean-architecture/references/source-intake.md",
        "skills/pmcro-clean-architecture/references/runtime-mapping.md",
        "skills/pmcro-clean-architecture/assets/application-request.json",
        "skills/pmcro-clean-architecture/assets/manifest.schema.json",
        "skills/pmcro-clean-architecture/scripts/simulate_architecture.py",
        "skills/pmcro-clean-architecture/scripts/validate_architecture.py",
        "skills/pmcro-clean-architecture/tests/test_structure.py",
        "docs/01-i-am-simulation.md",
        "docs/08-mcp-and-thought-transfer.md",
        "docs/09-progressive-trail-flow.md",
        "docs/11-google-ai-studio-activation.md",
        "docs/12-catalog-mcp-server-image.md",
        "docs/13-agent-surface-api-and-scope.md",
        "docs/14-agent-memory-governance.md",
        "docs/15-maf-skill-chain-and-console-simulation.md",
        "docs/16-skill-contract-template.md",
        "docs/17-clean-architecture-generic-repository.md",
        "docs/18-example-artifact-documentation.md",
        "docs/19-generic-concept-mapping.md",
        "docs/21-agent-independence-and-catalogs.md",
        "docs/22-desktop-commander-adapter.md",
        "examples/README.md",
        "scripts/build_activation_txt.py",
        "scripts/build_activation_bundle.py",
        "examples/backward-training-candidates.jsonl",
        "examples/forward-training-candidates.jsonl",
        "simulations/i-am-hofstadter.md",
        "simulations/i-am-buber.md",
        "simulations/i-am-von-neumann.md",
        "simulations/i-am-thought-transfer.md",
    ]
    for relative in required:
        if not (ROOT / relative).is_file():
            fail(f"missing required file: {relative}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    for phrase in ("generated role-play", "not historical quotations", "independent checker"):
        if phrase not in readme:
            fail(f"README must state boundary: {phrase}")

    activation_doc = (ROOT / "docs/11-google-ai-studio-activation.md").read_text(encoding="utf-8").lower()
    for phrase in ("progressive disclosure", "00-core", "request later packets by", "token"):
        if phrase not in activation_doc:
            fail(f"activation doc must document: {phrase}")

    catalog_doc = (ROOT / "docs/12-catalog-mcp-server-image.md").read_text(encoding="utf-8").lower()
    for phrase in ("two-session boundary", "checked trail", "read-only", "independent checker", "next seed"):
        if phrase not in catalog_doc:
            fail(f"catalog MCP design must document: {phrase}")

    for relative in (".agents/agents", ".pmcro/protocol", ".pmcro/trails", "docs", "simulations", "templates"):
        directory = ROOT / relative
        if not directory.is_dir():
            fail(f"missing required directory: {relative}")

    skill_dirs = sorted(
        path for path in (ROOT / "skills").iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if not skill_dirs:
        fail("expected at least one installable skill")
    for skill_dir in skill_dirs:
        for folder in ("agents", "scripts", "references", "assets", "tests"):
            if not (skill_dir / folder).is_dir():
                fail(f"skill is missing required folder {folder}: {skill_dir.name}")
        required_skill_files = (
            "SKILL.md",
            "agents/openai.yaml",
            "scripts/validate.ps1",
            "references/sample-prompts.md",
            "assets/README.md",
            "tests/README.md",
        )
        for relative in required_skill_files:
            if not (skill_dir / relative).is_file():
                fail(f"skill is missing required file {relative}: {skill_dir.name}")
        if len((skill_dir / "SKILL.md").read_text(encoding="utf-8").splitlines()) > 150:
            fail(f"SKILL.md exceeds the 150-line authoring limit: {skill_dir.name}")
        sample_prompts = skill_dir / "references/sample-prompts.md"
        if not sample_prompts.is_file():
            fail(f"skill is missing its copy/paste prompt surface: {skill_dir.name}")
        prompt_blocks = re.findall(
            r"(?ms)^## Prompt [^\n]*\n+```text\s*\n(.*?)\n```",
            sample_prompts.read_text(encoding="utf-8"),
        )
        if not 1 <= len(prompt_blocks) <= 5:
            fail(f"skill must expose 1-5 sample prompts: {skill_dir.name}")
        if any(not prompt.strip() or len(prompt.strip()) > 600 for prompt in prompt_blocks):
            fail(f"skill sample prompts must be concrete and <=600 characters: {skill_dir.name}")
        asset_files = [path for path in (skill_dir / "assets").rglob("*") if path.is_file() and path.name != "README.md"]
        if asset_files and not (skill_dir / "assets/README.md").is_file():
            fail(f"skill examples/assets require assets/README.md documentation: {skill_dir.name}")
        agent_dir = skill_dir / "agents"
        if not agent_dir.is_dir() or not any(path.is_file() for path in agent_dir.iterdir()):
            fail(f"skill must include an agent file in its agents directory: {skill_dir.name}")
        if not any(path.is_file() for path in agent_dir.glob("*.json")):
            fail(f"skill must include a machine-readable agents/*.json manifest: {skill_dir.name}")
        openai_surface = agent_dir / "openai.yaml"
        if openai_surface.is_file() and 'sample_prompts_ref: "references/sample-prompts.md"' not in openai_surface.read_text(encoding="utf-8"):
            fail(f"OpenAI agent surface must point to sample prompts: {openai_surface}")
        for agent_path in agent_dir.glob("*.json"):
            agent = load_json(agent_path)
            if agent.get("independentSurface") is not True:
                fail(f"agent surface must declare independentSurface=true: {agent_path}")
            if agent.get("samplePromptsRef") != "references/sample-prompts.md":
                fail(f"agent surface must point to sample prompts: {agent_path}")

    agent_files = sorted((ROOT / ".agents/agents").glob("*.json"))
    if len(agent_files) < 5:
        fail("expected at least five declarative agent surfaces")
    agents = {load_json(path)["id"]: load_json(path) for path in agent_files}
    if any(agent.get("independentSurface") is not True for agent in agents.values()):
        fail("every declarative agent surface must declare independentSurface=true")
    checker = agents.get("thought-transfer.checker")
    if not checker or checker["independentChecker"] is not True:
        fail("checker must declare independentChecker=true")
    if checker["contextBoundary"] != "checker-fresh" or checker["maxTurns"] != 1:
        fail("checker must have a fresh boundary and one-turn stop cap")
    catalog_surface = agents.get("thought-transfer.catalog-mcp-server")
    if not catalog_surface or catalog_surface["contextBoundary"] != "read-only-catalog":
        fail("catalog MCP surface must be read-only")
    if catalog_surface["independentChecker"] is not False:
        fail("catalog MCP surface must not certify itself")

    surface_ids = {"pmcro.global-orchestrator", "pmcro.personal-orchestrator", "projectname.orchestration-service"}
    surfaces = {agent_id: agents.get(agent_id) for agent_id in surface_ids}
    if any(surface is None for surface in surfaces.values()):
        fail("global, personal, and project agent surfaces must be declared")
    for agent_id, surface in surfaces.items():
        if surface["apiVersion"] != "pmcro.dev/v1" or surface["kind"] != "AgentSurface":
            fail(f"invalid agent surface kind: {agent_id}")
        if surface["status"]["simulation"] is not True or surface["status"]["verified"] is not False:
            fail(f"agent surface must start simulation-only: {agent_id}")
    personal_surface = surfaces["pmcro.personal-orchestrator"]
    if personal_surface["extends"]["ref"] != "pmcro.global-orchestrator":
        fail("personal surface must extend the global surface")
    if personal_surface["extends"]["policy"] != "non-widening":
        fail("personal surface inheritance must be non-widening")
    project_surface = surfaces["projectname.orchestration-service"]
    if project_surface["scope"] != "project" or project_surface["capabilityType"] != "service":
        fail("ProjectName.OrchestrationService must remain a project-scoped service")

    plugin_manifest = load_json(ROOT / "plugins/pmcro/plugin.json")
    if plugin_manifest["id"] != "pmcro" or plugin_manifest["kind"] != "PMCR-OPlugin":
        fail("invalid PMCR-O plugin manifest")
    manifest_skill_ids = {skill["id"] for skill in plugin_manifest["skills"]}
    expected_skill_ids = {"pmcro-bip", "pmcro-agent-surface", "pmcro-output-conventions", "pmcro-marketplace", "pmcro-github-marketplace", "pmcro-trail-product", "pmcro-clean-architecture"}
    expected_skill_ids = {"pmcro-bip", "pmcro-agent-surface", "pmcro-output-conventions", "pmcro-marketplace", "pmcro-github-marketplace", "pmcro-trail-product", "pmcro-clean-architecture", "pmcro-skill-lifecycle", "pmcro-product-repo"}
    if not expected_skill_ids.issubset(manifest_skill_ids):
        fail("PMCR-O plugin is missing one of its five core skills")
    adapter_ids = {adapter["id"] for adapter in plugin_manifest["runtimeAdapters"]}
    if "maf-native-filesystem" not in adapter_ids:
        fail("PMCR-O plugin must declare the MAF Native filesystem adapter")
    if "desktop-commander" not in adapter_ids:
        fail("PMCR-O plugin must declare the Desktop Commander runtime adapter")
    if "pmcro-memory-governance" not in manifest_skill_ids:
        fail("PMCR-O plugin must declare the memory-governance extension")
    if "pmcro-generic-crud" not in manifest_skill_ids:
        fail("PMCR-O plugin must declare the generic CRUD foundation")
    if "desktop-commander" not in manifest_skill_ids:
        fail("PMCR-O plugin must declare the Desktop Commander adapter skill")
    if "pmcro-clean-architecture" not in manifest_skill_ids:
        fail("PMCR-O plugin must declare the Clean Architecture builder")
    if plugin_manifest["defaultOutputContract"] != "templates/skill-output-envelope.json":
        fail("PMCR-O plugin must declare the default skill output contract")
    if plugin_manifest.get("samplePromptContract") != "templates/skill-manifest.json#samplePrompts":
        fail("PMCR-O plugin must declare the sample-prompt contract")
    if set(plugin_manifest["outputProfiles"]) != {"json", "dotnet-console", "trail"}:
        fail("PMCR-O plugin output profiles are incomplete")
    authoring_gate = plugin_manifest.get("policy", {}).get("authoringGate", {})
    if authoring_gate.get("entrypoint") != "@skill-creator /create-skill":
        fail("PMCR-O plugin must route skill authoring through @skill-creator /create-skill")
    if authoring_gate.get("messageKind") != "skill.create.request":
        fail("PMCR-O plugin must declare the skill.create.request gate")
    if set(authoring_gate.get("requiredBefore", [])) != {"plan", "make"}:
        fail("skill.create.request must precede plan and make")
    if authoring_gate.get("marketplaceRegistration") != "after-independent-checker":
        fail("marketplace registration must follow an independent checker")

    product_manifest = load_json(ROOT / "templates/product-repo/product.manifest.json")
    if product_manifest.get("apiVersion") != "pmcro.product-repo/v1":
        fail("product repository template must declare pmcro.product-repo/v1")
    if product_manifest.get("trailContract") != ".pmcro/protocol/trail-event.schema.json":
        fail("product repository must point to the generic trail contract")
    if product_manifest.get("promotion") != "checker-verified-only":
        fail("product repository must require checker-verified promotion")
    product_grant = load_json(ROOT / "templates/product-repo/autonomy-grant.example.json")
    if product_grant.get("autoApprove") is not True or product_grant.get("checker", {}).get("required") is not True:
        fail("product repository autonomy must be bounded and checker-gated")
    if "credentials" in product_grant.get("scope", {}).get("operations", []):
        fail("product repository autonomy cannot include credentials")

    memory_skill_text = (ROOT / "skills/pmcro-memory-governance/SKILL.md").read_text(encoding="utf-8").lower()
    for phrase in ("redact", "freshness", "retention", "revocation", "independent checker"):
        if phrase not in memory_skill_text:
            fail(f"memory governance skill must document: {phrase}")

    manifest = load_json(ROOT / "templates/skill-manifest.json")
    if manifest.get("contractVersion") != "pmcro.skill/v1":
        fail("generic skill template must declare the PMCR-O contract version")
    if set(manifest.get("messageContract", {})) != {"input", "output", "accept", "deny"}:
        fail("generic skill template must expose input/output/accept/deny")
    example_docs = manifest.get("exampleDocumentation", {})
    if example_docs.get("requiredFile") != "assets/README.md" or set(example_docs.get("requiredSections", [])) != {"Purpose", "Inputs", "Expected output", "Evidence and limits"}:
        fail("generic skill template must require documented examples")
    sample_prompts = manifest.get("samplePrompts", {})
    if (
        sample_prompts.get("requiredFile") != "references/sample-prompts.md"
        or sample_prompts.get("maxPrompts") != 5
        or sample_prompts.get("maxCharactersPerPrompt") != 600
        or sample_prompts.get("format") != "markdown-copy-paste"
    ):
        fail("generic skill template must require bounded sample prompts")
    for folder in ("agents", "scripts", "references", "assets", "tests"):
        if folder not in manifest["requiredFolders"]:
            fail(f"skill manifest missing required folder: {folder}")
    for required_file in ("scripts/validate.ps1", "references/sample-prompts.md", "assets/README.md", "tests/README.md"):
        if required_file not in manifest.get("requiredFiles", []):
            fail(f"skill manifest missing required file: {required_file}")
    if "agents/*.json" not in manifest.get("requiredFilePatterns", []):
        fail("skill manifest must require a machine-readable agents/*.json file")
    manifest_gate = manifest.get("authoringGate", {})
    if manifest_gate.get("entrypoint") != "@skill-creator /create-skill" or manifest_gate.get("messageKind") != "skill.create.request":
        fail("skill manifest must declare the skill.create.request authoring gate")
    if manifest_gate.get("marketplaceRegistration") != "after-independent-checker":
        fail("skill manifest must delay marketplace registration until after checking")
    if manifest["defaultAuthoringSurface"] != "skill-creator":
        fail("generic skill creator must be the default authoring surface")

    skill_text = (ROOT / "skills/thought-transfer/SKILL.md").read_text(encoding="utf-8")
    for phrase in ("Backward flow", "Forward flow", "MCP", "independent checker"):
        if phrase.lower() not in skill_text.lower():
            fail(f"skill must document: {phrase}")
    interface_text = (ROOT / "skills/thought-transfer/agents/openai.yaml").read_text(encoding="utf-8")
    for phrase in ("Thought Transfer", "$thought-transfer"):
        if phrase not in interface_text:
            fail(f"skill interface metadata missing: {phrase}")

    flow_skill_text = (ROOT / "skills/progressive-trail-flow/SKILL.md").read_text(encoding="utf-8")
    for phrase in ("backward", "forward", "training", "domain", "redacted"):
        if phrase.lower() not in flow_skill_text.lower():
            fail(f"progressive flow skill must document: {phrase}")
    flow_interface_text = (ROOT / "skills/progressive-trail-flow/agents/openai.yaml").read_text(encoding="utf-8")
    for phrase in ("Progressive Trail Flow", "$progressive-trail-flow"):
        if phrase not in flow_interface_text:
            fail(f"progressive flow interface metadata missing: {phrase}")
    registry = load_json(ROOT / "skills/progressive-trail-flow/assets/domain-registry.json")
    if len(registry.get("domains", [])) < 5:
        fail("progressive domain registry must contain at least five domains")
    for domain in registry["domains"]:
        for field in ("id", "entrypoints", "iAm", "scope", "loadWhen", "artifacts", "checker"):
            if field not in domain:
                fail(f"domain registry entry missing {field}: {domain.get('id')}")

    trail_path = ROOT / ".pmcro/trails/0001-source-seed.jsonl"
    events = []
    for line_number, line in enumerate(trail_path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"invalid trail JSON on line {line_number}: {exc}")
        for field in ("eventId", "phase", "role", "type", "action", "evidence"):
            if field not in event:
                fail(f"trail event {line_number} missing {field}")
        events.append(event)
    if not events or events[0]["parentId"] is not None:
        fail("trail must begin with a root seed")
    ids = {event["eventId"] for event in events}
    for event in events[1:]:
        if event.get("parentId") not in ids:
            fail(f"trail parent missing for {event['eventId']}")
    if not any(event["role"] == "independent-checker" for event in events):
        fail("trail must contain an independent checker event")

    for example in ("examples/forward-story-frame.json", "examples/backward-learning-frame.json"):
        frame = load_json(ROOT / example)
        if frame.get("simulation") is not True or "trailEvent" not in frame:
            fail(f"invalid rendered frame example: {example}")
    for example in ("examples/backward-training-candidates.jsonl", "examples/forward-training-candidates.jsonl"):
        rows = [json.loads(line) for line in (ROOT / example).read_text(encoding="utf-8").splitlines() if line.strip()]
        if not rows or any(row.get("status") != "candidate" for row in rows):
            fail(f"training projection must contain candidate rows: {example}")
        if any(row.get("metadata", {}).get("redaction") != "applied" for row in rows):
            fail(f"training projection must record redaction: {example}")

    markers = ("I AM:", "I NOTICE:", "I ASK:", "I REFUSE:", "I HAND OFF:")
    for path in sorted((ROOT / "simulations").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if path.name == "phase-voices.md":
            continue
        if "Simulation status:" not in text:
            fail(f"simulation status missing in {path}")
        for marker in markers:
            if marker not in text:
                fail(f"{marker} missing in {path}")
        if re.search(r"I AM:\s+(Douglas Hofstadter|Martin Buber|John von Neumann)\b", text):
            fail(f"historical impersonation-like label in {path}")

    print(f"PASS: {len(required)} required files, {len(agent_files)} agent surfaces, {len(events)} trail events")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
