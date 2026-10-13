#!/usr/bin/env python3
"""Validate role-owned, hash-chained PMCR-O JSONL frames."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROLES = {"orchestrator", "planner", "maker", "checker", "reflector"}
ROLE_KINDS = {
    "orchestrator": "orchestrator.route",
    "planner": "planner.plan",
    "maker": "maker.result",
    "checker": "checker.verdict",
    "reflector": "reflector.reflect",
}
STATUSES = {"open", "complete", "blocked", "halted"}
VERDICTS = {"PASS", "LOOP", "HALT"}
SEED_LEVELS = {"meta", "meta2", "meta3"}
REQUIRED = {
    "orchestrator.route": {"goal", "scope", "next_role", "caps"},
    "planner.plan": {"acceptance_criteria", "validated_resources", "steps"},
    "maker.result": {"plan_ref", "files_changed", "commands", "claim"},
    "checker.verdict": {"plan_ref", "maker_ref", "verdict", "checks", "independent"},
    "reflector.reflect": {"observations", "earned_constraints", "next_seed"},
}
COMMON = {
    "frame_id", "trail_id", "cycle_id", "seq", "role", "kind", "parent_id",
    "prev_hash", "hash", "status", "payload",
}


class FrameError(ValueError):
    """A deterministic frame validation failure."""


def canonical_without_hash(frame: dict[str, Any]) -> bytes:
    material = dict(frame)
    material.pop("hash", None)
    return json.dumps(
        material, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def frame_hash(frame: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_without_hash(frame)).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise FrameError(message)


def validate_payload(frame: dict[str, Any]) -> None:
    kind = frame["kind"]
    payload = frame["payload"]
    require(isinstance(payload, dict), f"seq {frame['seq']}: payload must be an object")
    missing = REQUIRED[kind] - payload.keys()
    require(not missing, f"seq {frame['seq']}: missing payload fields {sorted(missing)}")

    if kind == "orchestrator.route":
        caps = payload["caps"]
        require(isinstance(caps, dict), f"seq {frame['seq']}: caps must be an object")
        for name in ("loops", "calls", "seconds"):
            require(isinstance(caps.get(name), int) and caps[name] >= 0,
                    f"seq {frame['seq']}: caps.{name} must be a non-negative integer")
    elif kind == "planner.plan":
        require(isinstance(payload["validated_resources"], list),
                f"seq {frame['seq']}: validated_resources must be a list")
        require(isinstance(payload["steps"], list),
                f"seq {frame['seq']}: steps must be a list")
        require("verdict" not in payload, f"seq {frame['seq']}: planner cannot issue a verdict")
    elif kind == "maker.result":
        require("verdict" not in payload, f"seq {frame['seq']}: maker cannot issue a verdict")
        require(isinstance(payload["files_changed"], list),
                f"seq {frame['seq']}: files_changed must be a list")
        require(isinstance(payload["commands"], list),
                f"seq {frame['seq']}: commands must be a list")
    elif kind == "checker.verdict":
        require(payload["verdict"] in VERDICTS,
                f"seq {frame['seq']}: verdict must be PASS, LOOP, or HALT")
        require(payload["independent"] is True,
                f"seq {frame['seq']}: checker must declare independent=true")
        require(isinstance(payload["checks"], list),
                f"seq {frame['seq']}: checks must be a list")
        if payload["verdict"] == "LOOP":
            require("repair_seed" in payload,
                    f"seq {frame['seq']}: LOOP requires exactly one repair_seed")
        if payload["verdict"] == "HALT":
            require(frame["status"] == "halted",
                    f"seq {frame['seq']}: HALT requires status=halted")
    elif kind == "reflector.reflect":
        seed = payload["next_seed"]
        require(isinstance(seed, dict), f"seq {frame['seq']}: next_seed must be an object")
        require(seed.get("level") in SEED_LEVELS,
                f"seq {frame['seq']}: next_seed.level must be meta, meta2, or meta3")
        require(isinstance(seed.get("prompt_intent"), str) and seed["prompt_intent"].strip(),
                f"seq {frame['seq']}: next_seed.prompt_intent is required")
        require(seed.get("unexecuted") is True,
                f"seq {frame['seq']}: next seed must be unexecuted=true")
        for constraint in payload["earned_constraints"]:
            require(isinstance(constraint, dict),
                    f"seq {frame['seq']}: each earned constraint must be an object")
            require(constraint.get("status") in {"candidate", "promoted"},
                    f"seq {frame['seq']}: constraint status must be candidate or promoted")
            require(constraint.get("source_trail_refs"),
                    f"seq {frame['seq']}: constraint needs source_trail_refs")
            require(constraint.get("acceptance_basis") == "ACCEPT",
                    f"seq {frame['seq']}: constraint needs acceptance_basis=ACCEPT")


def validate(path: Path) -> int:
    frames: list[dict[str, Any]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise FrameError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
        require(isinstance(value, dict), f"line {line_number}: frame must be an object")
        frames.append(value)

    require(frames, "no frames found")
    trail_id = frames[0].get("trail_id")
    cycle_id = frames[0].get("cycle_id")
    seen_ids: set[str] = set()
    previous: dict[str, Any] | None = None

    for expected_seq, frame in enumerate(frames, 1):
        missing = COMMON - frame.keys()
        require(not missing, f"seq {expected_seq}: missing envelope fields {sorted(missing)}")
        require(frame["frame_id"] not in seen_ids, f"seq {expected_seq}: duplicate frame_id")
        seen_ids.add(frame["frame_id"])
        require(frame["trail_id"] == trail_id, f"seq {expected_seq}: trail_id changed")
        require(frame["cycle_id"] == cycle_id, f"seq {expected_seq}: cycle_id changed")
        require(frame["seq"] == expected_seq, f"seq {expected_seq}: sequence is not contiguous")
        require(frame["role"] in ROLES, f"seq {expected_seq}: unknown role")
        require(frame["kind"] == ROLE_KINDS[frame["role"]],
                f"seq {expected_seq}: role {frame['role']} cannot emit {frame['kind']}")
        require(frame["status"] in STATUSES, f"seq {expected_seq}: invalid status")

        if previous is None:
            require(frame["parent_id"] is None, "seq 1: parent_id must be null")
            require(frame["prev_hash"] is None, "seq 1: prev_hash must be null")
        else:
            require(previous["status"] == "complete",
                    f"seq {expected_seq}: previous frame is not complete")
            require(frame["parent_id"] == previous["frame_id"],
                    f"seq {expected_seq}: parent_id does not reference previous frame")
            require(frame["prev_hash"] == previous["hash"],
                    f"seq {expected_seq}: prev_hash does not link to previous hash")

        require(frame["hash"] == frame_hash(frame),
                f"seq {expected_seq}: hash mismatch")
        validate_payload(frame)
        previous = frame

    print(f"PASS: {len(frames)} PMCR-O frames validated")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frames", type=Path, help="JSONL frame log")
    args = parser.parse_args()
    try:
        return validate(args.frames)
    except (OSError, UnicodeError, FrameError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
