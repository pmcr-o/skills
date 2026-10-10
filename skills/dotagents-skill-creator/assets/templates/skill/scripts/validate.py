#!/usr/bin/env python3
"""Validate one generated DotAgents skill without external dependencies."""

from pathlib import Path
import json
import sys


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = ["SKILL.md", "agents", "scripts", "references", "assets", "tests"]
    missing = [name for name in required if not (ROOT / name).exists()]
    if missing:
        print("FAIL: missing " + ", ".join(missing))
        return 1
    if not any((ROOT / "agents").iterdir()):
        print("FAIL: agents/ is empty")
        return 1
    for folder in ("scripts", "references", "assets", "tests"):
        if not any(path.is_file() for path in (ROOT / folder).iterdir()):
            print(f"FAIL: {folder}/ is empty")
            return 1
    surface = ROOT / "agents" / "agent.json"
    try:
        data = json.loads(surface.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"FAIL: invalid agents/agent.json: {exc}")
        return 1
    for field in ("id", "providers", "entrypoints", "outputs", "maxDepth"):
        if field not in data:
            print(f"FAIL: agent surface missing {field}")
            return 1
    print("PASS: generated DotAgents skill structure and agent surface validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
