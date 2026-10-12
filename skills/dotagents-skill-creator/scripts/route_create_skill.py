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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--plugin", required=True)
    parser.add_argument("--raw-seed")
    parser.add_argument("--with-references", action="store_true")
    parser.add_argument("--with-assets", action="store_true")
    parser.add_argument("--with-scripts", action="store_true")
    parser.add_argument("--with-tests", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--json", action="store_true", help="emit JSON; retained for provider-neutral CLI symmetry")
    args = parser.parse_args()

    catalog_path = Path(args.catalog).expanduser().resolve()
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"HALT: cannot read catalog: {exc}", file=sys.stderr)
        return 2

    matches = [entry for entry in catalog.get("entries", []) if entry.get("name") == args.skill]
    generated_layers = []
    if args.with_references:
        generated_layers.append("references")
    if args.with_assets:
        generated_layers.append("assets")
    if args.with_scripts:
        generated_layers.append("scripts")
    if args.with_tests:
        generated_layers.append("tests")

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
            "generatedLayers": generated_layers,
            "phaseInjectionAllowed": False,
        },
        "nextSeed": "Run Skill Creator during MAKE, then independently CHECK the generated child before promotion or use.",
    }
    if args.raw_seed is not None:
        request["rawSeed"] = args.raw_seed
        request["rawSeedSha256"] = sha256_text(args.raw_seed)
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
