#!/usr/bin/env python3
"""Validate the local Clean Architecture builder skill contract."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo.resolve()
    skill = root / "skills/pmcro-clean-architecture"
    required = [
        "SKILL.md",
        "agents/openai.yaml",
        "agents/clean-architecture.json",
        "references/layers.md",
        "references/source-intake.md",
        "references/runtime-mapping.md",
        "assets/application-request.json",
        "assets/manifest.schema.json",
        "assets/README.md",
        "scripts/simulate_architecture.py",
    ]
    missing = [path for path in required if not (skill / path).is_file()]
    if missing:
        print("FAIL: missing " + ", ".join(missing))
        return 1
    surface = json.loads((skill / "agents/clean-architecture.json").read_text(encoding="utf-8"))
    for field in ("inputs", "outputs", "accept", "deny", "dependencies"):
        if not surface.get(field):
            print(f"FAIL: agent surface missing {field}")
            return 1
    request = skill / "assets/application-request.json"
    result = subprocess.run([sys.executable, str(skill / "scripts/simulate_architecture.py"), str(request)], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr or result.stdout)
        return 1
    output = json.loads(result.stdout)
    if output["simulation"] is not True or output["verified"] is not False:
        print("FAIL: simulation boundary missing")
        return 1
    if "IUnitOfWork" not in output["output"]["decisions"] or "runtime-map:maf-workflows-codeact-harness-mcp" not in output["output"]["decisions"]:
        print("FAIL: Unit of Work projection missing")
        return 1
    print("PASS: Clean Architecture skill structure and simulation contract validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
