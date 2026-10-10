#!/usr/bin/env python3
"""Independently check a staged session marketplace package and append a verdict."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def canonical_without_hash(frame: dict[str, Any]) -> bytes:
    material = dict(frame)
    material.pop("hash", None)
    return json.dumps(material, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def frame_hash(frame: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_without_hash(frame)).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def check_package(root: Path) -> list[dict[str, Any]]:
    manifest = load_json(root / "manifest.json")
    source_manifest = load_json(root / "source/source-manifest.json")
    checks: list[dict[str, Any]] = []

    required = [
        "manifest.json",
        "source/source-manifest.json",
        "source/redacted-session.txt",
        "marketplace/skill-candidate.json",
        "training/candidates.jsonl",
        "pmcro/frames.jsonl",
    ]
    missing = [path for path in required if not (root / path).is_file()
    ]
    checks.append({"id": "package-shape", "command": "required artifact paths", "result": "PASS" if not missing else f"missing {missing}", "evidence_ref": "manifest.json"})
    if missing:
        raise ValueError(f"missing required artifacts: {missing}")

    source_path = Path(source_manifest["path"])
    source_hash_ok = source_path.is_file() and hashlib.sha256(source_path.read_bytes()).hexdigest() == source_manifest["sha256"]
    checks.append({"id": "source-integrity", "command": "sha256(source)", "result": "PASS" if source_hash_ok else "FAIL", "evidence_ref": "source/source-manifest.json"})
    if not source_hash_ok:
        raise ValueError("source hash does not match the registered source")

    candidate = load_json(root / "marketplace/skill-candidate.json")
    candidate_ok = candidate.get("state") == "staged" and candidate.get("promotable") is False and candidate.get("messageContract", {}).get("deny")
    checks.append({"id": "candidate-boundary", "command": "inspect skill candidate contract", "result": "PASS" if candidate_ok else "FAIL", "evidence_ref": "marketplace/skill-candidate.json"})
    if not candidate_ok:
        raise ValueError("candidate is missing staged/non-promotable boundary")

    rows = [json.loads(line) for line in (root / "training/candidates.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    rows_ok = bool(rows) and all(row.get("status") == "candidate" and row.get("metadata", {}).get("redaction") == "applied" for row in rows)
    checks.append({"id": "training-boundary", "command": "inspect candidate training rows", "result": "PASS" if rows_ok else "FAIL", "evidence_ref": "training/candidates.jsonl"})
    if not rows_ok:
        raise ValueError("training rows must remain redacted candidates")

    frames = [json.loads(line) for line in (root / "pmcro/frames.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(frames) != 3 or frames[-1].get("role") != "maker" or frames[-1].get("status") != "complete":
        raise ValueError("maker handoff must be the final pre-check frame")
    repo_root = Path(__file__).resolve().parents[3]
    protocol_validator = repo_root / "skills/pmcro-messages-protocol/scripts/validate_frames.py"
    result = subprocess.run([sys.executable, str(protocol_validator), str(root / "pmcro/frames.jsonl")], capture_output=True, text=True)
    frames_ok = result.returncode == 0
    checks.append({"id": "pmcro-prefix", "command": "validate_frames.py frames.jsonl", "result": "PASS" if frames_ok else result.stdout + result.stderr, "evidence_ref": "pmcro/frames.jsonl"})
    if not frames_ok:
        raise ValueError("pre-check PMCR-O frames failed validation")
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    root = args.package.expanduser().resolve()
    try:
        checks = check_package(root)
        frames_path = root / "pmcro/frames.jsonl"
        frames = [json.loads(line) for line in frames_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        parent = frames[-1]
        payload = {
            "plan_ref": frames[1]["frame_id"],
            "maker_ref": parent["frame_id"],
            "verdict": "PASS",
            "checks": checks,
            "independent": True,
            "input": {"package": str(root), "sourceClaims": "unknown until direct runtime evidence"},
            "output": {"packageCheck": "accepted", "runtimeClaims": "not accepted"},
            "accept": ["staged transformation is structurally valid", "candidate rows are redacted and labeled"],
            "deny": ["W: access", "provider-private claims", "automatic training", "promotion"],
            "_trail_id": parent["trail_id"],
            "_cycle_id": parent["cycle_id"],
        }
        frame = {
            "frame_id": "check-0004",
            "trail_id": parent["trail_id"],
            "cycle_id": parent["cycle_id"],
            "seq": 4,
            "role": "checker",
            "kind": "checker.verdict",
            "parent_id": parent["frame_id"],
            "prev_hash": parent["hash"],
            "status": "complete",
            "payload": {key: value for key, value in payload.items() if not key.startswith("_")},
        }
        frame["hash"] = frame_hash(frame)
        with frames_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(frame, ensure_ascii=False, sort_keys=True) + "\n")
        (root / "reports/checker.json").write_text(json.dumps({"independent": True, "verdict": "PASS", "checks": checks}, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("PASS: independent package checker accepted the staged transformation; runtime claims remain unknown")
        return 0
    except (OSError, UnicodeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"HALT: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
