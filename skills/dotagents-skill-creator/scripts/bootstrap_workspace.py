#!/usr/bin/env python3
"""Create or reconcile a provider-neutral DotAgents workspace.

Skill Creator is the registered CREATE lifecycle authority. The default is a
read-only dry-run. Generated candidates remain untrusted until independent
CHECK. Optional progressive-disclosure layers are emitted only when requested.
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
from typing import Dict, Iterable, NoReturn, Set


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
VERSION = "0.2.0"
SCHEMA_VERSION = 2
PACKAGE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PACKAGE_ROOT / "assets" / "templates" / "skill"
OPTIONAL_LAYERS = ("references", "assets", "scripts", "tests")
PMCR_O_MARKERS = (
    "I AM THE",
    "I ORCHESTRATE",
    "I PLAN",
    "I MAKE",
    "I CHECK",
    "I REFLECT",
)


class PlanError(Exception):
    pass


def fail(message: str) -> NoReturn:
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
    return Path(raw).expanduser().resolve()


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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def pmcro_agent_markdown(skill: str, display: str, description: str) -> str:
    role = re.sub(r"[^A-Za-z0-9]+", " ", display).strip().upper() or skill.upper()
    return (
        f"# {display} PMCR-O Agent\n\n"
        f"Purpose: {description}\n\n"
        f"I AM THE {role} AGENT.\n"
        f"I ORCHESTRATE requests for the `{skill}` capability within its declared scope and validated resources.\n"
        "I PLAN the bare-minimum work graph before any execution.\n"
        "I MAKE changes or invoke admitted capabilities only during MAKE.\n"
        "I CHECK completed MAKE evidence without corrective execution.\n"
        "I REFLECT one next seed from checked evidence without executing it.\n\n"
        "Generated artifacts are candidates until an independent checker validates them.\n"
    )


def requested_layers(args: argparse.Namespace) -> Set[str]:
    layers: Set[str] = set()
    if args.with_references:
        layers.add("references")
    if args.with_assets:
        layers.add("assets")
    if args.with_scripts:
        layers.add("scripts")
    if args.with_tests:
        layers.add("tests")
    return layers


def build_component(skill: str, plugin: str, display: str, description: str, layers: Set[str]) -> Dict[str, str]:
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
        f"{base}/agents/agent.md": pmcro_agent_markdown(skill, display, description),
        f"{base}/agents/agent.json": render("agents/agent.json.tmpl", values).replace('"$ ', '"$'),
    }
    openai_template = TEMPLATE_ROOT / "agents" / "openai.yaml.tmpl"
    if openai_template.is_file():
        files[f"{base}/agents/openai.yaml"] = render("agents/openai.yaml.tmpl", values)

    if "scripts" in layers:
        files[f"{base}/scripts/validate.py"] = (TEMPLATE_ROOT / "scripts/validate.py").read_text(encoding="utf-8")
        files[f"{base}/scripts/README.md"] = (TEMPLATE_ROOT / "scripts/README.md").read_text(encoding="utf-8")
    if "references" in layers:
        files[f"{base}/references/contract.md"] = (TEMPLATE_ROOT / "references/contract.md").read_text(encoding="utf-8")
        files[f"{base}/references/README.md"] = (TEMPLATE_ROOT / "references/README.md").read_text(encoding="utf-8")
    if "assets" in layers:
        files[f"{base}/assets/README.md"] = (TEMPLATE_ROOT / "assets/README.md").read_text(encoding="utf-8")
        files[f"{base}/assets/manifest.json"] = json_text({
            "artifactId": f"{plugin}.{skill}",
            "artifactType": "skill",
            "version": VERSION,
            "sourceOfTruth": base,
            "requiredCore": ["SKILL.md", "agents/"],
            "generatedLayers": sorted(layers),
            "promotion": "generated-unchecked",
            "nextSeed": "Run an independent checker before promotion or use.",
        })
    if "tests" in layers:
        files[f"{base}/tests/test_structure.py"] = (TEMPLATE_ROOT / "tests/test_structure.py").read_text(encoding="utf-8")

    files[f"plugins/{plugin}/plugin.json"] = json_text({
        "schemaVersion": 2,
        "pluginId": plugin,
        "version": VERSION,
        "projection": True,
        "sourceOfTruth": base,
        "skills": [{"name": skill, "path": base, "version": VERSION}],
        "authority": "metadata-only-until-checked",
    })
    files[f"plugins/{plugin}/.claude-plugin/marketplace.json"] = json_text({
        "name": plugin,
        "version": VERSION,
        "metadata": {"projection": True, "sourceOfTruth": ".agents/skills"},
        "plugins": [{
            "name": skill,
            "source": f"../../{base}",
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
    raw_seed: str | None,
    layers: Set[str],
) -> Dict[str, str]:
    files = build_component(skill, plugin, display, description, layers)
    component_id = f"{plugin}/{skill}"
    request_path = f".agents/requests/create-skill/{plugin}--{skill}.json"
    catalog_path = ".agents/catalog/source-marketplace.json"
    catalog_ref = catalog_path if source_catalog else None
    if source_catalog:
        files[catalog_path] = json_text(source_catalog)

    request = {
        "schemaVersion": 2,
        "kind": "skill.create.request",
        "requiredInvoker": "dotagents-skill-creator",
        "creatorAuthority": "dotagents-skill-creator",
        "entrypoint": "@skill-creator /create-skill",
        "status": "candidate-created-awaiting-independent-check",
        "target": {"skill": skill, "plugin": plugin},
        "sourceCatalogRef": catalog_ref,
        "sourceRef": source_ref or "local-source-not-declared",
        "existingMatches": (source_catalog or {}).get("entries", []),
        "rules": {
            "preserveExistingSource": True,
            "reuseByAdapter": True,
            "registrationRequiresIndependentCheck": True,
            "requiredCore": ["SKILL.md", "agents/"],
            "optionalLayers": list(OPTIONAL_LAYERS),
            "generatedLayers": sorted(layers),
        },
        "nextSeed": "Run an independent checker against the generated child before promotion or use.",
    }
    if raw_seed is not None:
        request["rawSeed"] = raw_seed
        request["rawSeedSha256"] = sha256_text(raw_seed)
        request["rawSeedImmutable"] = True
    files[request_path] = json_text(request)

    component_paths = set(component_paths)
    component_paths.add(request_path)
    if source_catalog:
        component_paths.add(catalog_path)

    control_files = {
        ".pmcro/charter.json": json_text({
            "schemaVersion": 2,
            "domainId": "dotagents.workspace",
            "charterId": "dotagents-local-charter",
            "owner": "local-principal",
            "scope": [".agents/skills", ".agents/plugins", "plugins", ".pmcro"],
            "allowedOperations": ["filesystem.read", "filesystem.write", "validator"],
            "sideEffects": "staged-only",
            "maxDepth": 1,
            "status": "draft-until-checked",
        }),
        ".pmcro/registry.json": json_text({
            "schemaVersion": 2,
            "sourceOfTruth": ".agents/skills",
            "createAuthority": "dotagents-skill-creator",
            "capabilityRoots": [".agents/skills", ".agents/agents"],
            "pluginRoots": [".agents/plugins", "plugins"],
            "controlPlaneRoot": ".pmcro",
            "trailRoot": ".pmcro/trails",
            "checkpointRoot": ".pmcro/checkpoints",
            "manifestRoot": ".pmcro/manifests",
            "seedRoot": ".pmcro/seeds",
            "authority": "charter-and-grant-required",
        }),
        ".pmcro/manifests/README.md": "# PMCR-O manifests\n\nStore bounded artifact manifests here.\n",
        ".pmcro/trails/README.md": "# PMCR-O trails\n\nAppend trail events; do not rewrite prior verdicts.\n",
        ".pmcro/checkpoints/README.md": "# PMCR-O checkpoints\n\nStore inspectable staged checkpoints here.\n",
        ".pmcro/seeds/README.md": "# PMCR-O seeds\n\nStore immutable raw seeds and one unexecuted next seed per reflection.\n",
    }
    files.update(control_files)

    existing_components = dict(previous.get("components", {}))
    existing_components[component_id] = {
        "skill": skill,
        "plugin": plugin,
        "canonicalPath": f".agents/skills/{skill}",
        "generatedLayers": sorted(layers),
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
            "adapter": "dotagents-skill-creator",
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
        "createAuthority": "dotagents-skill-creator",
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
        "promotion": "generated-unchecked",
        "creationRoutes": creation_routes,
        "sourceMarketplaces": deduped_sources,
    }
    files["dotagents.manifest.json"] = json_text(manifest)
    files["DOTAGENTS.md"] = (
        "# DotAgents workspace\n\n"
        "Canonical skills live under `.agents/skills/`. Provider/plugin files are projections.\n"
        "Skill Creator owns CREATE only; generated candidates require independent CHECK before promotion/use.\n"
        "The core skill shape is `SKILL.md` plus `agents/`; references/assets/scripts/tests are optional.\n"
        "PMCR-O control data lives under `.pmcro/`; it is not executable skill source.\n"
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
        })
    index = {
        "schemaVersion": 2,
        "marketplaceId": "personal-dotagents",
        "sourceOfTruth": ".agents/skills",
        "controlPlaneRoot": ".pmcro",
        "createAuthority": "dotagents-skill-creator",
        "createRequests": creation_routes,
        "plugins": [
            {"name": key, "projectionPath": f"plugins/{key}", "skills": sorted(value, key=lambda entry: entry["name"])}
            for key, value in sorted(plugin_entries.items())
        ],
        "promotion": "catalog-only-until-checked",
    }
    files[".agents/plugins/marketplace.json"] = json_text(index)

    current_plugin_skills = [
        {"name": item["skill"], "path": item["canonicalPath"], "version": VERSION}
        for item in existing_components.values() if item.get("plugin") == plugin
    ]
    files[f"plugins/{plugin}/plugin.json"] = json_text({
        "schemaVersion": 2,
        "pluginId": plugin,
        "version": VERSION,
        "projection": True,
        "sourceOfTruth": ".agents/skills",
        "skills": sorted(current_plugin_skills, key=lambda entry: entry["name"]),
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
                action = "unchanged"
            elif relative in previous.get("managedPaths", []) or relative in old_paths:
                action = "update-managed"
            else:
                fail(f"unknown conflicting file; refusing overwrite: {relative}")
        else:
            action = "create"
        operations.append({"path": relative, "action": action, "sha256": sha256_text(content)})
    return {"operations": operations, "staleRemoved": stale if clean else [], "componentId": component_id}


def apply(root: Path, files: Dict[str, str]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for relative, content in files.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, help="workspace root")
    parser.add_argument("--skill", required=True, help="new skill name")
    parser.add_argument("--plugin", required=True, help="plugin projection name")
    parser.add_argument("--display-name", default=None)
    parser.add_argument("--description", default="A bounded provider-neutral PMCR-O agent skill.")
    parser.add_argument("--raw-seed", help="immutable raw seed to preserve verbatim in the create request")
    parser.add_argument("--source-catalog", help="read-only catalog from discover_marketplace.py")
    parser.add_argument("--source-ref", help="pinned checkout, tag, or commit reference")
    parser.add_argument("--with-references", action="store_true")
    parser.add_argument("--with-assets", action="store_true")
    parser.add_argument("--with-scripts", action="store_true")
    parser.add_argument("--with-tests", action="store_true")
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
        layers = requested_layers(args)
        component_files = build_component(skill, plugin, display, args.description, layers)
        component_paths = sorted(component_files)
        files = workspace_files(
            root,
            skill,
            plugin,
            display,
            args.description,
            component_paths,
            previous,
            source_catalog,
            args.source_ref,
            args.raw_seed,
            layers,
        )
        plan = prepare(root, files, previous, component_id, args.clean_managed)
        plan.update({
            "root": str(root),
            "mode": "apply" if args.apply else "dry-run",
            "artifactId": f"{plugin}.{skill}",
            "createAuthority": "dotagents-skill-creator",
            "generatedLayers": sorted(layers),
        })
        if args.json:
            print(json.dumps(plan, indent=2, sort_keys=True))
        else:
            print(f"DotAgents plan: {plan['mode']} -> {root}")
            for op in plan["operations"]:
                print(f"{op['action']}: {op['path']}")
            for relative in plan["staleRemoved"]:
                print(f"remove-managed: {relative}")
        if args.apply:
            apply(root, files)
            print("APPLIED: generated candidate requires independent CHECK before promotion/use")
        return 0
    except PlanError as exc:
        print(f"HALT: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
