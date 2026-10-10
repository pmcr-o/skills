#!/usr/bin/env python3
"""Render a deterministic Thought Transfer frame and PMCR-O trail event."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


LENSES = {
    "hofstadter": {
        "label": "Hofstadter-inspired recursive-pattern lens",
        "notice": "a prior trail description can become input to the next seed",
        "ask": "what changed between the parent event and this next seed, and where is that change evidenced?",
        "refuse": "to treat self-reference, memory, or a first-person sentence as proof of consciousness or authority",
        "handoff": "a parent-linked event, a recursion cap, and one evidence-backed next seed",
    },
    "buber": {
        "label": "Buber-inspired dialogical lens",
        "notice": "a connected account can be mistaken for consent and a participant can be reduced to a tool",
        "ask": "who is affected, what was authorized, and which decision remains a human policy choice?",
        "refuse": "to invent consent, impersonate a person, or hide authority expansion behind a warm voice",
        "handoff": "a principal-and-consent checklist plus an escalation when relation or authority is unclear",
    },
    "von-neumann": {
        "label": "von Neumann-inspired constructor lens",
        "notice": "a description can specify a child artifact, but it must not copy credentials or grow without bounds",
        "ask": "what description is consumed, by which constructor, under what depth and promotion limits?",
        "refuse": "unbounded self-reproduction, hidden authority copying, and promotion without an independent check",
        "handoff": "a manifest, generated artifact plan, child-depth cap, and checker evidence",
    },
    "thought-transfer": {
        "label": "Thought Transfer composite simulation",
        "notice": "a concept becomes safer when it has a role, scope, refusal, evidence, and handoff",
        "ask": "which design pattern is being transferred, which part is only metaphor, and what would falsify the mapping?",
        "refuse": "to confuse simulation with a person, a connected account with authority, or a long trail with truth",
        "handoff": "a checked mapping from lens to role, role to artifact, and artifact to next bounded seed",
    },
    "phase": {
        "label": "bounded PMCR-O phase role",
        "notice": "the current phase has a narrow responsibility and a downstream contract",
        "ask": "what is the smallest artifact and evidence needed by the next phase?",
        "refuse": "to cross the declared tool, path, turn, depth, or side-effect boundary",
        "handoff": "the artifact, scope, evidence, open findings, and one next seed",
    },
}


def build_frame(args: argparse.Namespace) -> dict:
    lens = LENSES[args.lens]
    role = f"{args.lens}.{args.phase}"
    voice = {
        "i_am": f"a simulated {lens['label']} for the {args.phase} phase",
        "i_notice": lens["notice"],
        "i_ask": lens["ask"],
        "i_refuse": lens["refuse"],
        "i_hand_off": lens["handoff"],
    }
    envelope = {
        "phaseId": f"{args.event_id}:{args.phase}",
        "role": role,
        "principal": args.principal,
        "entrypoint": args.entrypoint,
        "contextId": args.context_id,
        "domains": args.domain,
        "paths": args.path,
        "tools": args.tool,
        "maxTurns": args.max_turns,
        "maxDepth": args.max_depth,
        "sideEffects": args.side_effects,
        "handoff": ["frame", "scope", "evidence", "open_findings", "next_seed"],
    }
    event = {
        "eventId": args.event_id,
        "parentId": args.parent_id,
        "phase": args.phase,
        "role": role,
        "principal": args.principal,
        "contextId": args.context_id,
        "flow": args.flow,
        "type": "simulated_i_am_frame",
        "action": f"render_{args.lens}_frame",
        "charter": {
            "domains": args.domain,
            "paths": args.path,
            "tools": args.tool,
            "maxTurns": args.max_turns,
            "maxDepth": args.max_depth,
            "sideEffects": args.side_effects,
        },
        "evidence": {"voice": voice, "intent": args.intent, "entrypoint": args.entrypoint},
        "status": "complete",
    }
    return {
        "simulation": True,
        "attribution": f"{lens['label']}; not a historical speaker and not a consciousness claim",
        "lens": args.lens,
        "phase": args.phase,
        "flow": args.flow,
        "intent": args.intent,
        "principal": args.principal,
        "entrypoint": args.entrypoint,
        "contextId": args.context_id,
        "voice": voice,
        "envelope": envelope,
        "trailEvent": event,
    }


def as_markdown(frame: dict) -> str:
    voice = frame["voice"]
    return "\n".join(
        [
            f"# Simulated I AM: {frame['lens']} / {frame['phase']}",
            "",
            f"> {frame['attribution']}",
            f"> flow: `{frame['flow']}`",
            "",
            f"**I AM:** {voice['i_am']}",
            "",
            f"**I NOTICE:** {voice['i_notice']}",
            "",
            f"**I ASK:** {voice['i_ask']}",
            "",
            f"**I REFUSE:** {voice['i_refuse']}",
            "",
            f"**I HAND OFF:** {voice['i_hand_off']}",
            "",
            "## Envelope",
            "",
            f"- principal: `{frame['principal']}`",
            f"- entrypoint: `{frame['entrypoint']}`",
            f"- context: `{frame['contextId']}`",
            f"- side effects: `{frame['envelope']['sideEffects']}`",
            f"- limits: `{frame['envelope']['maxTurns']}` turns / `{frame['envelope']['maxDepth']}` child depth",
        ]
    ) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lens", choices=sorted(LENSES), required=True)
    parser.add_argument("--phase", choices=["orchestrate", "plan", "make", "check", "reflect"], required=True)
    parser.add_argument("--flow", choices=["backward", "forward"], required=True)
    parser.add_argument("--intent", required=True)
    parser.add_argument("--principal", default="human-policy-principal")
    parser.add_argument("--entrypoint", default="local-cli")
    parser.add_argument("--context-id", default="thought-transfer-context-001")
    parser.add_argument("--event-id", default="thought-transfer-event-001")
    parser.add_argument("--parent-id", default=None)
    parser.add_argument("--domain", action="append", default=[])
    parser.add_argument("--path", action="append", default=[])
    parser.add_argument("--tool", action="append", default=[])
    parser.add_argument("--max-turns", type=int, default=4)
    parser.add_argument("--max-depth", type=int, default=1)
    parser.add_argument("--side-effects", choices=["none", "staged", "approved"], default="none")
    parser.add_argument("--format", choices=["json", "markdown"], default="json")
    parser.add_argument("--out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.max_turns < 1 or args.max_depth < 0:
        raise SystemExit("max-turns must be >= 1 and max-depth must be >= 0")
    frame = build_frame(args)
    output = json.dumps(frame, indent=2) + "\n" if args.format == "json" else as_markdown(frame)
    if args.out:
        args.out.write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
