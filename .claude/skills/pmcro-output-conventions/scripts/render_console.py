#!/usr/bin/env python3
"""Render a typed PMCR-O skill output as deterministic console text."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = ("apiVersion", "kind", "messageId", "traceId", "from", "to", "phase", "mode", "status", "simulation", "verified", "evidenceTier", "input", "output", "accept", "deny", "evidence", "next")


def compact(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    args = parser.parse_args()
    value = json.loads(args.record.read_text(encoding="utf-8"))
    missing = [field for field in REQUIRED if field not in value]
    if missing:
        raise SystemExit(f"FAIL: missing fields: {', '.join(missing)}")
    if value["kind"] != "SkillOutput" or value["apiVersion"] != "pmcro.dev/v1":
        raise SystemExit("FAIL: invalid skill output kind")
    if value["mode"] == "simulate" and (value["simulation"] is not True or value["verified"] is not False):
        raise SystemExit("FAIL: simulation output must be simulation=true and verified=false")
    print(f"I AM: {value['from']['skillId']}")
    print(f"TRACE: {value['traceId']}  MESSAGE: {value['messageId']}")
    print(f"PHASE: {value['phase']}  MODE: {value['mode']}  STATUS: {value['status']}")
    print(f"SIMULATION: {str(value['simulation']).lower()}  VERIFIED: {str(value['verified']).lower()}  EVIDENCE: {value['evidenceTier']}")
    print(f"INPUT: {value['input']['summary']}")
    print(f"OUTPUT: {value['output']['summary']}")
    print(f"ACCEPT: {compact(value['accept'])}")
    print(f"DENY: {compact(value['deny'])}")
    print(f"EVIDENCE: {compact(value['evidence'])}")
    print(f"I HAND OFF: {value['to']['role']} via {value['to']['skillId']} (unexecuted={str(value['next']['unexecuted']).lower()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
