#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

SHA256 = re.compile(r"^[a-f0-9]{64}$")


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError("registry root must be an object")
    return value


def unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def resolve(registry_path: Path, graph_id: str, goal_ref: str, required: list[str], grants: list[str]) -> dict:
    registry = load_json(registry_path)
    if registry.get("kind") != "RegistryIndex" or registry.get("authority") != "canonical":
        raise ValueError("Planner resolution requires the canonical RegistryIndex")
    resources = registry.get("resources", [])
    if not isinstance(resources, list):
        raise ValueError("registry resources must be an array")

    by_id: dict[str, dict] = {}
    index_by_id: dict[str, int] = {}
    for index, record in enumerate(resources):
        if not isinstance(record, dict):
            raise ValueError("registry resource must be an object")
        rid = record.get("resourceId")
        if not isinstance(rid, str) or not rid:
            raise ValueError("registry resourceId missing")
        if rid in by_id:
            raise ValueError(f"duplicate registry resourceId: {rid}")
        by_id[rid] = record
        index_by_id[rid] = index

    selected: list[dict] = []
    gaps: list[dict] = []
    grant_set = set(grants)
    for rid in unique(required):
        record = by_id.get(rid)
        if record is None:
            gaps.append({
                "gapId": rid,
                "requiredBehavior": f"registered capability {rid}",
                "resolution": "skill-create",
            })
            continue

        state_ok = record.get("state") == "registered-checked"
        planner_ok = record.get("admissibleToPlanner") is True
        non_revoked = record.get("revocationRef") is None
        digest = record.get("contentDigest")
        digest_ok = isinstance(digest, str) and SHA256.fullmatch(digest) is not None
        if not state_ok or not planner_ok or not non_revoked or not digest_ok:
            gaps.append({
                "gapId": rid,
                "requiredBehavior": f"available registered capability {rid}",
                "resolution": "defer",
            })
            continue

        if rid not in grant_set:
            gaps.append({
                "gapId": rid,
                "requiredBehavior": f"explicit grant for {rid}",
                "resolution": "deny",
            })
            continue

        selected.append({
            "ref": record["sourceRef"],
            "validationState": "registered-checked",
            "evidenceRef": record["checkerVerdictRef"],
            "registryRef": f"{registry_path.as_posix()}#resources/{index_by_id[rid]}",
        })

    return {
        "graphId": graph_id,
        "goalRef": goal_ref,
        "catalogRef": registry_path.as_posix(),
        "catalogValidationRef": "canonical-registry-state",
        "selectedAgents": [],
        "selectedSkills": selected,
        "capabilityGaps": gaps,
        "goalExecutionEligible": len(gaps) == 0,
        "minimality": {
            "minimumSufficient": True,
            "evidenceRef": "deterministic:required-resource-set-only",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", required=True)
    parser.add_argument("--graph-id", required=True)
    parser.add_argument("--goal-ref", required=True)
    parser.add_argument("--require", action="append", default=[])
    parser.add_argument("--grant-ref", action="append", default=[])
    args = parser.parse_args()
    try:
        graph = resolve(Path(args.registry), args.graph_id, args.goal_ref, args.require, args.grant_ref)
    except Exception as exc:
        print(json.dumps({"status": "HALT", "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(graph, indent=2, sort_keys=True))
    return 0 if graph["goalExecutionEligible"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
