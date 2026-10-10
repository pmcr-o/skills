#!/usr/bin/env python3
"""Validate a rendered Thought Transfer JSON frame."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_VOICE = ("i_am", "i_notice", "i_ask", "i_refuse", "i_hand_off")
REQUIRED_ENVELOPE = ("phaseId", "role", "principal", "contextId", "maxTurns", "maxDepth", "sideEffects")


def fail(message: str) -> None:
    raise ValueError(message)


def validate(frame: dict) -> None:
    if frame.get("simulation") is not True:
        fail("simulation must be true")
    if frame.get("flow") not in {"backward", "forward"}:
        fail("flow must be backward or forward")
    if "historical speaker" not in frame.get("attribution", ""):
        fail("attribution must state that this is not a historical speaker")
    voice = frame.get("voice")
    if not isinstance(voice, dict):
        fail("voice object is required")
    for field in REQUIRED_VOICE:
        if not isinstance(voice.get(field), str) or not voice[field].strip():
            fail(f"voice.{field} must be a non-empty string")
    envelope = frame.get("envelope")
    if not isinstance(envelope, dict):
        fail("envelope object is required")
    for field in REQUIRED_ENVELOPE:
        if field not in envelope:
            fail(f"envelope.{field} is required")
    if envelope["maxTurns"] < 1 or envelope["maxDepth"] < 0:
        fail("invalid finite limits")
    if envelope["sideEffects"] not in {"none", "staged", "approved"}:
        fail("invalid side-effect mode")
    event = frame.get("trailEvent")
    if not isinstance(event, dict):
        fail("trailEvent object is required")
    for field in ("eventId", "phase", "role", "principal", "contextId", "flow", "action", "evidence", "status"):
        if field not in event:
            fail(f"trailEvent.{field} is required")
    if event["flow"] != frame["flow"]:
        fail("trail event and frame flow must match")
    if event["contextId"] != envelope["contextId"]:
        fail("trail event and envelope context IDs must match")
    if event["role"] != envelope["role"]:
        fail("trail event and envelope roles must match")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frame", type=Path)
    args = parser.parse_args()
    try:
        validate(json.loads(args.frame.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"PASS: valid Thought Transfer frame: {args.frame}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
