#!/usr/bin/env python3
"""Create or reconcile a provider-neutral DotAgents workspace.

The default is a dry-run. The script has no network or package-install path.
It only deletes component paths recorded in a prior dotagents manifest when
--clean-managed is explicitly supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, Iterable


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION = "0.1.0"
SCHEMA_VERSION = 1
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PACKAGE_ROOT / "assets" / "templates" / "skill"


class PlanError(Exception):
    pass


def fail(message: str) -> "NoReturn":
    raise PlanError(message)


def valid_name(value: str, label: str) -> str:
    if not NAME_RE.fullmatch(value):
        fail(f"{label} must match lowercase letters, digits, and single hyphens: {value}")
    return value


def resolve_root(raw: str) -> Path:
    if os.name != "nt" and re.match(r"^[A-Za-z]:[\\/]", raw):
        fail(f"Windows drive path is not mounted in this runtime: {raw}")
    if raw.startswith("\\\\"):
        fail("UNC roots are not accepted by the portable bootstrap")
    root = Path(raw).expanduser()
    if root.is_absolute() and os.name != "nt":
        return root.resolve()
    if os.name == "nt" and root.is_absolute():
        return root.resolve()
    return root.resolve()


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        fail(f"generated path escaped workspace root: {path}")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.name}: {exc}")


def render(name: str, values: dict) -> str:
    path = TEMPLATE_ROOT / name
    if not path.is_file():
        fail(f"missing bundled template: {name}")
    text = path.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def json_text(value: dict) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def build_component(root: Path, skill: str, plugin: str, display: str, description: str) -> Dict[str, str]:
    base = f".agents/skills/{skill}"
    values = {
        "skill_name": skill,
        "plugin_name": plugin,
        "display_name": display,
        "description": description,
        "description_short": description[:160],
    }
    files: Dict[str, str] = {
        f"{base}/SKILL.md": render("SKILL.md.tmpl", values),
        f"{base}/agents/agent.json": render("agents/agent.json.tmpl", values).replace('"$ ', '"$'),
        f"{base}/agents/openai.yaml": render("agents/openai.yaml.tmpl", values),
        f"{base}/scripts/validate.py": (TEMPLATE_ROOT / "scripts/validate.py").read_text(encoding="utf-8"),
        f"{base}/scripts/README.md": (TEMPLATE_ROOT / "scripts/README.md").read_text(encoding="utf-8"),
        f"{base}/references/contract.md": (TEMPLATE_ROOT / "references/contract.md").read_text(encoding="utf-8"),
        f"{base}/references/README.md": (TEMPLATE_ROOT / "references/README.md").read_text(encoding="utf-8"),
        f"{base}/assets/README.md": (TEMPLATE_ROOT / "assets/README.md").read_text(encoding="utf-8"),
        f"{base}/tests/test_structure.py": (TEMPLATE_ROOT / "tests/test_structure.py").read_text(encoding="utf-8"),
    }
    files[f"{base}/assets/manifest.json"] = json_text({
        "artifactId": f"{plugin}.{skill}",
        "artifactType": "skill",
        "version": VERSION,
        "parent": {"artifactId": "dotagents.workspace", "depth": 1, "maxDepth": 1},
        "sourceOfTruth": f".agents/skills/{skill}",
        "providers": ["generic", "chatgpt", "codex", "claude", "ollama"],
        "requiredFolders": ["agents", "scripts", "references", "assets", "tests"],
        "promotion": "generated",
        "evidenceTier": "pattern-valid",
        "nextSeed": "Run a separate checker against the generated skill before promotion.",
    })
    files[f"plugins/{plugin}/plugin.json"] = json_text({
        "schemaVersion": 1,
        "pluginId": plugin,
        "version": VERSION,
        "projection": True,
        "sourceOfTruth": f".agents/skills/{skill}",
        "skills": [{"name": skill, "path": f".agents/skills/{skill}", "version": VERSION}],
        "providers": ["generic", "chatgpt", "codex", "claude", "ollama"],
        "authority": "metadata-only-until-checked",
    })
    files[f"plugins/{plugin}/.claude-plugin/marketplace.json"] = json_text({
        "name": plugin,
        "version": VERSION,
        "metadata": {"projection": True, "sourceOfTruth": ".agents/skills"},
        "plugins": [{
            "name": skill,
            "source": f"../../.agents/skills/{skill}",
            "version": VERSION,
            "description": description,
        }],
    })
    return files


def workspace_files(
    root: Path,
    skill: str,
    plugin: str,
    display: str,
    description: str,
    component_paths: Iterable[str],
    previous: dict,
    source_catalog: dict | None,
    source_ref: str | None,
) -> Dict[str, str]:
    files = build_component(root, skill, plugin, display, description)
    component_id = f"{plugin}/{skill}"
    request_path = f".agents/requests/create-skill/{plugin}--{skill}.json"
    catalog_path = ".agents/catalog/source-marketplace.json"
    catalog_ref = catalog_path if source_catalog else None
    if source_catalog:
        files[catalog_path] = json_text(source_catalog)
    files[request_path] = json_text({
        "schemaVersion": 1,
        "kind": "create-skill-handoff",
        "requiredInvoker": "create-skill",
        "entrypoint": "@skill-creator /create-skill",
        "status": "ready-for-create-skill",
        "target": {"skill": skill, "plugin": plugin},
        "sourceCatalogRef": catalog_ref,
        "sourceRef": source_ref or "local-source-not-declared",
        "existingMatches": (source_catalog or {}).get("entries", []),
        "rules": {
            "preserveExistingSource": True,
            "reuseByAdapter": True,
            "copyOnlyAfterChecker": True,
            "requiredFolders": ["agents", "scripts", "references", "assets"],
        },
        "nextSeed": "Invoke create-skill with this handoff, then validate the canonical child before marketplace staging.",
    })
    component_paths = set(component_paths)
    component_paths.add(request_path)
    if source_catalog:
        component_paths.add(catalog_path)
    control_files = {
        ".pmcro/charter.json": json_text({
            "schemaVersion": 1,
            "domainId": "dotagents.workspace",
            "charterId": "dotagents-local-charter",
            "owner": "local-principal",
            "scope": [".agents/skills", ".agents/plugins", "plugins", ".pmcro"],
            "allowedOperations": ["filesystem.read", "filesystem.write", "validator"],
            "sideEffects": "staged-only",
            "maxDepth": 1,
            "governanceReferences": ["microsoft.agent-governance-toolkit"],
            "policyBoundary": "reference-only-until-locally-checked",
            "status": "draft-until-checked",
        }),
        ".pmcro/registry.json": json_text({
            "schemaVersion": 1,
            "sourceOfTruth": ".agents/skills",
            "capabilityRoots": [".agents/skills", ".agents/agents"],
            "pluginRoots": [".agents/plugins", "plugins"],
            "controlPlaneRoot": ".pmcro",
            "trailRoot": ".pmcro/trails",
            "checkpointRoot": ".pmcro/checkpoints",
            "manifestRoot": ".pmcro/manifests",
            "seedRoot": ".pmcro/seeds",
            "governanceRoot": ".pmcro/governance",
            "governanceReferences": ["microsoft.agent-governance-toolkit"],
            "loaderModes": ["generic", "chatgpt", "codex", "claude", "ollama"],
            "authority": "charter-and-grant-required",
        }),
        ".pmcro/governance/README.md": (
            "# PMCR-O governance references\n\n"
            "References in this folder inform policy and tool-boundary checks.\n"
            "They do not grant runtime authority; the local charter, explicit grant,\n"
            "and independent checker evidence remain authoritative.\n\n"
            "`agent-governance-toolkit.json` records the Microsoft Agent Governance\n"
            "Toolkit architecture and ADR documents as a re-verifiable boundary\n"
            "reference. PMCR-O still owns trail, phase, and next-seed semantics.\n"
        ),
        ".pmcro/governance/agent-governance-toolkit.json": json_text({
            "schemaVersion": 1,
            "kind": "governance-reference",
            "referenceId": "microsoft.agent-governance-toolkit",
            "source": "https://github.com/microsoft/agent-governance-toolkit",
            "documents": {
                "architecture": "https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/ARCHITECTURE.md",
                "adrIndex": "https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/adr/index.md",
                "adrGuide": "https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/adr/README.md",
            },
            "role": "policy-enforcement-reference",
            "scope": "tool-and-policy-boundary",
            "compatibility": "boundary-implementation-reference",
            "pmcroRelationship": {
                "pmcroOwns": ["orchestration", "phase-transitions", "trail", "checker", "next-seed"],
                "referenceMayInform": ["action-policy", "tool-boundary", "allow-warn-deny-review"],
            },
            "authority": {
                "grantsRuntimeAuthority": False,
                "requiresLocalCharter": True,
                "requiresExplicitGrant": True,
                "requiresCheckerEvidence": True,
            },
            "verification": {
                "sourceRef": "main-is-reference-only",
                "pinBeforePromotion": True,
                "reverifyBeforePromotion": True,
            },
        }),
        ".pmcro/manifests/README.md": "# PMCR-O manifests\n\nStore bounded artifact manifests here.\n",
        ".pmcro/trails/README.md": "# PMCR-O trails\n\nAppend trail events; do not rewrite prior verdicts.\n",
        ".pmcro/checkpoints/README.md": "# PMCR-O checkpoints\n\nStore inspectable staged checkpoints here.\n",
        ".pmcro/seeds/README.md": "# PMCR-O seeds\n\nStore one unexecuted next seed per reflection.\n",
    }
    files.update(control_files)
    existing_components = dict(previous.get("components", {}))
    existing_components[component_id] = {
        "skill": skill,
        "plugin": plugin,
        "canonicalPath": f".agents/skills/{skill}",
        "paths": sorted(component_paths),
    }
    all_paths = set(previous.get("managedPaths", []))
    all_paths.update(component_paths)
    all_paths.update({"dotagents.manifest.json", ".agents/plugins/marketplace.json", "DOTAGENTS.md"})
    all_paths.update(control_files)
    plugins = sorted({item.get("plugin") for item in existing_components.values() if item.get("plugin")})
    creation_routes = dict(previous.get("creationRoutes", {}))
    creation_routes[component_id] = request_path
    source_marketplaces = list(previous.get("sourceMarketplaces", []))
    if source_catalog:
        source_marketplaces.append({
            "name": source_catalog.get("sourceRootName", "existing-marketplace"),
            "ref": source_ref or "local-source-not-declared",
            "trust": "candidate",
            "adapter": "create-skill",
            "catalogRef": catalog_ref,
        })
    deduped_sources = []
    source_keys = set()
    for item in source_marketplaces:
        key = json.dumps(item, sort_keys=True)
        if key not in source_keys:
            source_keys.add(key)
            deduped_sources.append(item)
    manifest = {
        "schemaVersion": SCHEMA_VERSION,
        "artifactId": "dotagents.workspace",
        "artifactType": "workspace",
        "version": VERSION,
        "sourceOfTruth": ".agents/skills",
        "controlPlaneRoot": ".pmcro",
        "governanceReferences": ["microsoft.agent-governance-toolkit"],
        "providers": ["generic", "chatgpt", "codex", "claude", "ollama"],
        "plugins": plugins,
        "components": existing_components,
        "managedPaths": sorted(all_paths),
        "safety": {
            "defaultMode": "dry-run",
            "deletePolicy": "managed-component-only",
            "network": False,
            "packageInstall": False,
            "credentials": False,
        },
        "promotion": "generated",
        "creationRoutes": creation_routes,
        "sourceMarketplaces": deduped_sources,
    }
    files["dotagents.manifest.json"] = json_text(manifest)
    files["DOTAGENTS.md"] = (
        "# DotAgents workspace\n\n"
        "Canonical skills live under `.agents/skills/`. Plugin files are projections.\n"
        "PMCR-O control data lives under `.pmcro/`; it is not executable skill source.\n"
        "Run the creator in dry-run mode first, then apply explicitly.\n"
        "Unknown files are preserved; cleanup is limited to recorded managed paths.\n"
    )
    plugin_entries = {}
    for item in existing_components.values():
        plugin_id = item.get("plugin")
        if not plugin_id:
            continue
        plugin_entries.setdefault(plugin_id, []).append({
            "name": item["skill"],
            "canonicalPath": item["canonicalPath"],
            "version": VERSION,
            "projectionPath": f"plugins/{plugin_id}",
        })
    index = {
        "schemaVersion": 1,
        "marketplaceId": "personal-dotagents",
        "sourceOfTruth": ".agents/skills",
        "controlPlaneRoot": ".pmcro",
        "createSkillRequired": True,
        "createSkillHandoffs": creation_routes,
        "plugins": [{"name": key, "projectionPath": f"plugins/{key}", "skills": sorted(value, key=lambda entry: entry["name"])}
                    for key, value in sorted(plugin_entries.items())],
        "providers": {
            "generic": "agents/agent.json",
            "chatgpt": "agents/agent.json",
            "codex": "agents/openai.yaml",
            "claude": "plugins/<plugin>/.claude-plugin/marketplace.json",
            "ollama": "scripts/*.py plus agents/agent.json",
        },
        "promotion": "catalog-only-until-checked",
    }
    files[".agents/plugins/marketplace.json"] = json_text(index)

    current_plugin_skills = [
        {"name": item["skill"], "path": item["canonicalPath"], "version": VERSION}
        for item in existing_components.values() if item.get("plugin") == plugin
    ]
    files[f"plugins/{plugin}/plugin.json"] = json_text({
        "schemaVersion": 1,
        "pluginId": plugin,
        "version": VERSION,
        "projection": True,
        "sourceOfTruth": ".agents/skills",
        "skills": sorted(current_plugin_skills, key=lambda entry: entry["name"]),
        "providers": ["generic", "chatgpt", "codex", "claude", "ollama"],
        "authority": "metadata-only-until-checked",
    })
    files[f"plugins/{plugin}/.claude-plugin/marketplace.json"] = json_text({
        "name": plugin,
        "version": VERSION,
        "metadata": {"projection": True, "sourceOfTruth": ".agents/skills"},
        "plugins": [{
            "name": item["name"],
            "source": f"../../{item['path']}",
            "version": item["version"],
        } for item in sorted(current_plugin_skills, key=lambda entry: entry["name"])],
    })
    return files


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_remove(root: Path, relative: str) -> None:
    target = (root / relative).resolve()
    if target == root or root not in target.parents:
        fail(f"refusing cleanup outside workspace: {relative}")
    if target.is_symlink():
        fail(f"refusing cleanup of symlink: {relative}")
    if target.is_file():
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)


def prepare(root: Path, files: Dict[str, str], previous: dict, component_id: str, clean: bool) -> dict:
    old_component = previous.get("components", {}).get(component_id, {})
    old_paths = set(old_component.get("paths", []))
    desired = set(files)
    stale = sorted(old_paths - desired)
    if clean:
        for relative in stale:
            safe_remove(root, relative)
    operations = []
    for relative, content in sorted(files.items()):
        target = root / relative
        if target.exists() and target.is_symlink():
            fail(f"refusing to follow symlink at {relative}")
        if target.exists() and target.is_dir():
            fail(f"file path is an existing directory: {relative}")
        if target.is_file():
            current = target.read_text(encoding="utf-8")
            if current == content:
                operations.append({"path": relative, "action": "unchanged", "sha256": sha256(content)})
            elif relative in previous.get("managedPaths", []) or relative in old_paths:
                operations.append({"path": relative, "action": "update-managed", "sha256": sha256(content)})
            else:
                fail(f"unknown conflicting file; refusing overwrite: {relative}")
        else:
            operations.append({"path": relative, "action": "create", "sha256": sha256(content)})
    return {"operations": operations, "staleRemoved": stale if clean else [], "componentId": component_id}


def apply(root: Path, files: Dict[str, str], plan: dict) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="workspace root; Windows drive paths work on Windows")
    parser.add_argument("--skill", required=True, help="new skill name")
    parser.add_argument("--plugin", required=True, help="plugin projection name")
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--description", default="A bounded provider-neutral agent skill.")
    parser.add_argument("--source-catalog", help="read-only catalog from discover_marketplace.py")
    parser.add_argument("--source-ref", help="pinned local checkout, tag, or commit reference")
    parser.add_argument("--apply", action="store_true", help="write the planned files")
    parser.add_argument("--clean-managed", action="store_true", help="remove only stale paths owned by this component")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable plan")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        skill = valid_name(args.skill, "skill")
        plugin = valid_name(args.plugin, "plugin")
        if args.clean_managed and not args.apply:
            fail("--clean-managed requires --apply")
        root = resolve_root(args.root)
        manifest_path = root / "dotagents.manifest.json"
        previous = load_json(manifest_path) if manifest_path.exists() else {}
        display = args.display_name or skill.replace("-", " ").title()
        component_id = f"{plugin}/{skill}"
        source_catalog = None
        if args.source_catalog:
            source_catalog = load_json(Path(args.source_catalog).expanduser())
            if source_catalog.get("kind") != "marketplace-catalog":
                fail("--source-catalog must be a marketplace-catalog JSON file")
        component_files = build_component(root, skill, plugin, display, args.description)
        component_paths = sorted(component_files)
        files = workspace_files(
            root, skill, plugin, display, args.description, component_paths, previous,
            source_catalog, args.source_ref,
        )
        plan = prepare(root, files, previous, component_id, args.clean_managed)
        plan.update({"root": str(root), "mode": "apply" if args.apply else "dry-run", "artifactId": f"{plugin}.{skill}"})
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True))
        else:
            print(f"DotAgents plan: {plan['mode']} -> {root}")
            for op in plan["operations"]:
                print(f"{op['action']}: {op['path']}")
            for relative in plan["staleRemoved"]:
                print(f"remove-managed: {relative}")
        if args.apply:
            apply(root, files, plan)
            print("APPLIED: run validate_workspace.py before promotion")
        return 0
    except PlanError as exc:
        print(f"HALT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
