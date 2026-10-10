#!/usr/bin/env python3
"""Read-only discovery of existing skill repositories and marketplace shapes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frontmatter(path: Path) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    result = {}
    for line in lines[1:80]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"')
    return result


def candidate_dirs(root: Path):
    seen = set()
    roots = [root / ".agents" / "skills", root / "skills"]
    for plugin_root in (root / "plugins",):
        if plugin_root.is_dir():
            roots.extend(plugin_root.glob("*/skills"))
    for base in roots:
        if not base.is_dir():
            continue
        for skill_dir in sorted(base.iterdir()):
            if not skill_dir.is_dir() or not (skill_dir / "SKILL.md").is_file():
                continue
            resolved = skill_dir.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            yield skill_dir


def inspect(root: Path, skill_dir: Path) -> dict:
    metadata = frontmatter(skill_dir / "SKILL.md")
    required = {folder: (skill_dir / folder).is_dir() and any((skill_dir / folder).iterdir())
                for folder in ("agents", "scripts", "references", "assets")}
    agents = sorted(str(path.relative_to(root).as_posix()) for path in (skill_dir / "agents").glob("*") if path.is_file()) if (skill_dir / "agents").is_dir() else []
    return {
        "name": metadata.get("name") or skill_dir.name,
        "description": metadata.get("description", ""),
        "path": skill_dir.relative_to(root).as_posix(),
        "sha256": sha256(skill_dir / "SKILL.md"),
        "agentFiles": agents,
        "requiredFolders": required,
        "agentPresent": bool(agents),
        "shape": "complete" if all(required.values()) and agents else "partial",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="existing marketplace or skill repository")
    parser.add_argument("--output", help="optional JSON output path")
    parser.add_argument("--json", action="store_true", help="emit JSON; retained for provider-neutral CLI symmetry")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"HALT: source root does not exist: {args.root}", file=sys.stderr)
        return 2
    entries = [inspect(root, path) for path in candidate_dirs(root)]
    catalog = {
        "schemaVersion": 1,
        "kind": "marketplace-catalog",
        "sourceRootName": root.name,
        "readOnly": True,
        "entries": entries,
        "counts": {
            "skills": len(entries),
            "complete": sum(entry["shape"] == "complete" for entry in entries),
            "partial": sum(entry["shape"] == "partial" for entry in entries),
        },
        "nextAction": "Route a requested child through create-skill before generation.",
    }
    rendered = json.dumps(catalog, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(f"PASS: discovered {len(entries)} skill(s); catalog={output}")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
