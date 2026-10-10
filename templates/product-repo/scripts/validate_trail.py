#!/usr/bin/env python3
"""Validate a generic PMCR-O JSONL trail without domain-specific assumptions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = ("trailId", "cycleId", "eventId", "phase", "role", "iAm", "act", "status", "evidenceRefs")
PHASES = {"orchestrate", "plan", "make", "check", "reflect"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trail", type=Path, required=True)
    args = parser.parse_args()
    events = [json.loads(line) for line in args.trail.read_text(encoding="utf-8").splitlines() if line.strip()]
    seen = set()
    phases = set()
    for event in events:
        missing = [field for field in REQUIRED if field not in event]
        if missing:
            raise SystemExit(f"FAIL: missing {missing} in {event.get('eventId', '<unknown>')}")
        phases.add(event["phase"])
        if event["phase"] not in PHASES:
            raise SystemExit(f"FAIL: unknown phase {event['phase']}")
        parent = event.get("parentId")
        if parent is not None and parent not in seen:
            raise SystemExit(f"FAIL: parent does not precede event {event['eventId']}")
        seen.add(event["eventId"])
    if phases != PHASES:
        raise SystemExit("FAIL: trail must cover orchestrate, plan, make, check, and reflect")
    if not any(event["role"] == "checker" and event["verified"] is True for event in events):
        raise SystemExit("FAIL: trail has no verified checker event")
    if not any(event["phase"] == "reflect" and event.get("nextSeed", {}).get("unexecuted") is True for event in events):
        raise SystemExit("FAIL: trail has no unexecuted reflector seed")
    print(f"PASS: generic trail; events={len(events)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
