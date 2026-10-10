#!/usr/bin/env python3
"""Project eligible PMCR-O JSONL events into redacted training candidates."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


ELIGIBLE = {"complete", "pass"}
SECRET_KEY = re.compile(r"(secret|token|password|api[_-]?key|authorization|private[_-]?key|email)", re.I)


def principal_ref(value: object) -> str:
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:12]
    return f"principal:{digest}"


def redact(value: object, key: str = "") -> object:
    if SECRET_KEY.search(key):
        return "[REDACTED]"
    if isinstance(value, dict):
        return {str(k): redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(item, key) for item in value]
    return value


def quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def candidate(event: dict, flow: str, trail_id: str, domain: str) -> dict:
    event_id = event["eventId"]
    role = event.get("role", "unknown-role")
    phase = event.get("phase", "unknown-phase")
    action = event.get("action", "recorded-action")
    line = f"@{role} /pmcro:{phase} {quote(action)} #trail:{trail_id}"
    evidence = redact(event.get("evidence", {}))
    target = {
        "flow": flow,
        "source_event_id": event_id,
        "action": action,
        "evidence": evidence,
    }
    if flow == "backward":
        target["purpose"] = "derive one reusable constraint or skill change from checked evidence"
    else:
        target["purpose"] = "produce a bounded user-facing deliverable from a checked trail product"
    return {
        "status": "candidate",
        "flow": flow,
        "messages": [
            {"role": "user", "content": line},
            {"role": "assistant", "content": json.dumps(target, ensure_ascii=False, sort_keys=True)},
        ],
        "metadata": {
            "trail_id": trail_id,
            "source_event_ids": [event_id],
            "parent_event_id": event.get("parentId"),
            "domain": domain,
            "principal_ref": principal_ref(event.get("principal", "unknown")),
            "redaction": "applied",
            "simulation": event.get("type") == "simulated_i_am_frame",
            "checker_required": True,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--flow", choices=["backward", "forward"], required=True)
    parser.add_argument("--trail-id", required=True)
    parser.add_argument("--domain", default="pmcro")
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = []
    for line_number, line in enumerate(args.input.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSON on line {line_number}: {exc}")
        if event.get("status") not in ELIGIBLE:
            continue
        if not event.get("eventId") or "evidence" not in event:
            continue
        rows.append(candidate(event, args.flow, args.trail_id, args.domain))

    output = "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    print(f"projected {len(rows)} candidate rows", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
