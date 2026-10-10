#!/usr/bin/env python3
"""Route one reflector seed into a new bounded orchestrator cycle."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROUTES = {
    "meta": {"display_level": "meta", "repair_surface": "artifact-or-phase", "first_target": "maker"},
    "meta2": {"display_level": "meta-meta", "repair_surface": "skill-or-workflow", "first_target": "planner"},
    "meta3": {"display_level": "meta-meta-meta", "repair_surface": "orchestrator-agent-prompt", "first_target": "orchestrator"},
}


def frame_hash(frame: dict[str, Any]) -> str:
    material = dict(frame)
    material.pop("hash", None)
    encoded = json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_frame(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        values = [json.loads(line) for line in raw.splitlines() if line.strip()]
        value = next((candidate for candidate in reversed(values) if isinstance(candidate, dict) and candidate.get("kind") == "reflector.reflect"), None)
        if value is None:
            raise ValueError("JSONL input contains no reflector.reflect frame")
    if not isinstance(value, dict):
        raise ValueError("reflection must be a JSON object")
    if value.get("role") != "reflector" or value.get("kind") != "reflector.reflect":
        raise ValueError("input is not a reflector.reflect frame")
    if value.get("status") != "complete" or value.get("hash") != frame_hash(value):
        raise ValueError("reflection frame is incomplete or has a hash mismatch")
    seed = value.get("payload", {}).get("next_seed")
    if not isinstance(seed, dict) or seed.get("unexecuted") is not True:
        raise ValueError("next seed must be an unexecuted object")
    if seed.get("level") not in ROUTES:
        raise ValueError("next seed level must be meta, meta2, or meta3")
    if not isinstance(seed.get("prompt_intent"), str) or not seed["prompt_intent"].strip():
        raise ValueError("next seed prompt_intent is required")
    return value


def route(frame: dict[str, Any], depth: int, max_depth: int) -> dict[str, Any]:
    seed = frame["payload"]["next_seed"]
    level = seed["level"]
    decision = ROUTES[level]
    bounded = depth < max_depth
    return {
        "route_kind": "orchestrator.next_seed_route",
        "source_frame": f"{frame['trail_id']}:{frame['frame_id']}",
        "entrypoint": "@orchestrator /pmcro:orchestrate",
        "level": level,
        "display_level": decision["display_level"],
        "repair_surface": decision["repair_surface"],
        "first_target": decision["first_target"],
        "prompt_intent": seed["prompt_intent"],
        "required_resources": seed.get("required_resources", []),
        "depth": depth,
        "max_depth": max_depth,
        "admitted": bounded,
        "unexecuted": True,
        "decision_basis": "typed reflection evidence and bounded seed policy",
        "stop_reason": None if bounded else "max-depth reached; preserve seed without execution",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reflection", type=Path)
    parser.add_argument("--depth", type=int, default=0)
    parser.add_argument("--max-depth", type=int, default=3)
    parser.add_argument("--out", type=Path, help="write the route decision as JSON")
    args = parser.parse_args()
    if args.depth < 0 or args.max_depth < 0:
        parser.error("depth values must be non-negative")
    try:
        decision = route(load_frame(args.reflection), args.depth, args.max_depth)
        rendered = json.dumps(decision, ensure_ascii=False, sort_keys=True) + "\n"
        if args.out:
            args.out.write_text(rendered, encoding="utf-8")
            print(f"PASS: wrote {args.out}")
        else:
            print(rendered, end="")
        return 0 if decision["admitted"] else 2
    except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
