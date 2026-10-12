#!/usr/bin/env python3
"""Emit a provider-neutral Skill Creator CREATE request for a discovered marketplace."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


OPTIONAL_LAYERS = ("references", "assets", "scripts", "tests")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"cannot read {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} root must be a JSON object")
    return value


def validate_capability_import(value: dict, *, skill: str, plugin: str) -> set[str]:
    if value.get("kind") != "capability.import" or value.get("schemaVersion") != 1:
        raise ValueError("capability import must be schemaVersion=1 kind=capability.import")
    if value.get("status") != "generated-unchecked":
        raise ValueError("capability import must remain generated-unchecked before Skill Creator routing")

    projection = value.get("skillProjection")
    if not isinstance(projection, dict):
        raise ValueError("capability import is missing skillProjection")
    target = projection.get("target")
    if target != {"skill": skill, "plugin": plugin}:
        raise ValueError("capability import target does not match --skill/--plugin")
    if projection.get("requiredCore") != ["SKILL.md", "agents/"]:
        raise ValueError("capability import must preserve the canonical required core")
    if projection.get("registrationRequiresIndependentCheck") is not True:
        raise ValueError("capability import must require independent checking before registration")

    transport = value.get("transport")
    if not isinstance(transport, dict) or transport.get("secretMaterialIncluded") is not False:
        raise ValueError("capability import transport must explicitly exclude secret material")

    effects = value.get("effects")
    if not isinstance(effects, dict) or effects.get("executionAuthorityGranted") is not False:
        raise ValueError("capability import must not grant execution authority")
    for tool in value.get("tools", []):
        if not isinstance(tool, dict) or tool.get("executionAuthorityGranted") is not False:
            raise ValueError("every imported tool must explicitly deny execution authority")
    for resource in value.get("resources", []):
        if not isinstance(resource, dict) or resource.get("executable") is not False:
            raise ValueError("imported resources must remain non-executable")
    for prompt in value.get("prompts", []):
        if not isinstance(prompt, dict) or prompt.get("inert") is not True:
            raise ValueError("imported prompts must remain inert")

    layers = projection.get("suggestedLayers", [])
    if not isinstance(layers, list):
        raise ValueError("skillProjection.suggestedLayers must be an array")
    unknown = sorted(set(layers) - set(OPTIONAL_LAYERS))
    if unknown:
        raise ValueError(f"capability import requested unknown layers: {', '.join(unknown)}")
    return set(layers)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--plugin", required=True)
    parser.add_argument("--raw-seed")
    parser.add_argument("--capability-import", help="normalized CAPABILITY_IMPORT JSON to embed as Skill Creator input")
    parser.add_argument("--with-references", action="store_true")
    parser.add_argument("--with-assets", action="store_true")
    parser.add_argument("--with-scripts", action="store_true")
    parser.add_argument("--with-tests", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true", help="emit JSON; retained for provider-neutral CLI symmetry")
    args = parser.parse_args()

    catalog_path = Path(args.catalog).expanduser().resolve()
    try:
        catalog = load_json(catalog_path, "catalog")
        capability_import = None
        imported_layers: set[str] = set()
        if args.capability_import:
            capability_import = load_json(Path(args.capability_import).expanduser().resolve(), "capability import")
            imported_layers = validate_capability_import(capability_import, skill=args.skill, plugin=args.plugin)
    except ValueError as exc:
        print(f"HALT: {exc}", file=sys.stderr)
        return 2

    matches = [entry for entry in catalog.get("entries", []) if entry.get("name") == args.skill]
    generated_layers = set(imported_layers)
    if args.with_references:
        generated_layers.add("references")
    if args.with_assets:
        generated_layers.add("assets")
    if args.with_scripts:
        generated_layers.add("scripts")
    if args.with_tests:
        generated_layers.add("tests")

    raw_seed = args.raw_seed
    if capability_import is not None:
        import_seed = capability_import.get("provenance", {}).get("rawSeed")
        if import_seed is not None:
            if not isinstance(import_seed, str):
                print("HALT: capability import rawSeed must be a string", file=sys.stderr)
                return 2
            if raw_seed is not None and raw_seed != import_seed:
                print("HALT: --raw-seed conflicts with immutable capability-import provenance", file=sys.stderr)
                return 2
            raw_seed = import_seed

    request = {
        "schemaVersion": 2,
        "kind": "skill.create.request",
        "requiredInvoker": "dotagents-skill-creator",
        "creatorAuthority": "dotagents-skill-creator",
        "entrypoint": "@skill-creator /create-skill",
        "seedEntrypoint": "@orchestrator /pmcro:seed",
        "status": "ready-for-skill-creator",
        "target": {"skill": args.skill, "plugin": args.plugin},
        "sourceCatalog": {
            "kind": catalog.get("kind", "marketplace-catalog"),
            "path": catalog_path.name,
            "existingMatches": matches,
        },
        "rules": {
            "preserveExistingSource": True,
            "reuseByAdapter": True,
            "registrationRequiresIndependentCheck": True,
            "requiredCore": ["SKILL.md", "agents/"],
            "optionalLayers": list(OPTIONAL_LAYERS),
            "generatedLayers": sorted(generated_layers),
            "phaseInjectionAllowed": False,
            "importDoesNotGrantExecutionAuthority": True,
            "preserveImportedSchemas": True,
        },
        "nextSeed": "Run Skill Creator during MAKE, then independently CHECK the generated child before promotion or use.",
    }
    if capability_import is not None:
        request["capabilityImport"] = capability_import
    if raw_seed is not None:
        request["rawSeed"] = raw_seed
        request["rawSeedSha256"] = sha256_text(raw_seed)
        request["rawSeedImmutable"] = True

    rendered = json.dumps(request, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"PASS: Skill Creator request written to {output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
