#!/usr/bin/env python3
"""Emit the explicit create-skill handoff for a discovered marketplace."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--skill", required=True)
    parser.add_argument("--plugin", required=True)
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
    request = {
        "schemaVersion": 1,
        "kind": "create-skill-handoff",
        "requiredInvoker": "create-skill",
        "entrypoint": "@skill-creator /create-skill",
        "status": "ready-for-create-skill",
        "target": {"skill": args.skill, "plugin": args.plugin},
        "sourceCatalog": {
            "kind": catalog.get("kind", "marketplace-catalog"),
            "path": catalog_path.name,
            "existingMatches": matches,
        },
        "rules": {
            "preserveExistingSource": True,
            "reuseByAdapter": True,
            "copyOnlyAfterChecker": True,
            "requiredFolders": ["agents", "scripts", "references", "assets"],
        },
        "nextSeed": "Invoke create-skill with this handoff, then validate the canonical child before marketplace staging.",
    }
    rendered = json.dumps(request, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"PASS: create-skill handoff written to {output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
