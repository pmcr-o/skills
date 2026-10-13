#!/usr/bin/env python3
"""Wait for one eligible checker frame and emit a reflector frame."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


def canonical_without_hash(frame: dict[str, Any]) -> bytes:
    material = dict(frame)
    material.pop("hash", None)
    return json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def frame_hash(frame: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_without_hash(frame)).hexdigest()


def load_queue(path: Path) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"line {line_number}: queue item must be an object")
        items.append(item)
    return items


def unwrap(item: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    frame = item.get("frame", item)
    if not isinstance(frame, dict):
        raise ValueError("queue item frame must be an object")
    return frame, item.get("acknowledged") is True or item.get("consumed") is True


def eligible_checker(items: list[dict[str, Any]]) -> dict[str, Any] | None:
    for item in items:
        frame, consumed = unwrap(item)
        if consumed:
            continue
        payload = frame.get("payload")
        if (
            frame.get("role") == "checker"
            and frame.get("kind") == "checker.verdict"
            and frame.get("status") == "complete"
            and isinstance(payload, dict)
            and payload.get("independent") is True
            and payload.get("verdict") in {"PASS", "LOOP", "HALT"}
        ):
            expected = frame_hash(frame)
            if frame.get("hash") != expected:
                raise ValueError(f"checker frame {frame.get('frame_id')} has a hash mismatch")
            return frame
    return None


def make_reflection(
    checker: dict[str, Any],
    level: str,
    prompt_intent: str,
    required_resources: list[str],
    observation: str | None,
    constraint: str | None,
) -> dict[str, Any]:
    checker_payload = checker["payload"]
    earned_constraints: list[dict[str, Any]] = []
    if constraint:
        if checker_payload["verdict"] != "PASS":
            raise ValueError("an earned constraint requires a PASS checker verdict")
        earned_constraints.append(
            {
                "status": "candidate",
                "source_trail_refs": [f"{checker['trail_id']}:{checker['frame_id']}"],
                "acceptance_basis": "ACCEPT",
                "text": constraint,
            }
        )

    frame = {
        "frame_id": f"reflect-{checker['seq'] + 1:04d}",
        "trail_id": checker["trail_id"],
        "cycle_id": checker["cycle_id"],
        "seq": checker["seq"] + 1,
        "role": "reflector",
        "kind": "reflector.reflect",
        "parent_id": checker["frame_id"],
        "prev_hash": checker["hash"],
        "status": "complete",
        "payload": {
            "observations": [
                observation
                or f"Independent checker completed with verdict {checker_payload['verdict']}."
            ],
            "earned_constraints": earned_constraints,
            "next_seed": {
                "level": level,
                "prompt_intent": prompt_intent,
                "required_resources": required_resources,
                "unexecuted": True,
            },
        },
    }
    frame["hash"] = frame_hash(frame)
    return frame


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--queue", type=Path, required=True, help="JSONL queue or trail view")
    parser.add_argument("--level", choices=("meta", "meta2", "meta3"), required=True)
    parser.add_argument("--prompt-intent", required=True)
    parser.add_argument("--required-resource", action="append", default=[])
    parser.add_argument("--observation")
    parser.add_argument("--constraint")
    parser.add_argument("--out", type=Path, help="write the frame instead of stdout")
    parser.add_argument("--append", type=Path, help="append the frame to a JSONL trail")
    args = parser.parse_args()
    try:
        if args.out and args.append:
            raise ValueError("use either --out or --append, not both")
        checker = eligible_checker(load_queue(args.queue))
        if checker is None:
            print("WAIT: no completed independent checker frame")
            return 2
        frame = make_reflection(
            checker,
            args.level,
            args.prompt_intent,
            args.required_resource,
            args.observation,
            args.constraint,
        )
        rendered = json.dumps(frame, ensure_ascii=False, sort_keys=True) + "\n"
        if args.out:
            args.out.write_text(rendered, encoding="utf-8")
            print(f"PASS: wrote {args.out}")
        elif args.append:
            with args.append.open("a", encoding="utf-8") as handle:
                handle.write(rendered)
            print(f"PASS: appended reflector frame to {args.append}")
        else:
            print(rendered, end="")
        return 0
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
