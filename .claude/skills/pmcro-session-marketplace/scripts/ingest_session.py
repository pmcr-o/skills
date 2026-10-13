#!/usr/bin/env python3
"""Create a staged PMCR-O marketplace package from one authorized session file."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


SECRET_PATTERNS = [
    re.compile(r"(?i)\b(api[_ -]?key|access[_ -]?token|password|secret|backup[_ -]?code)\b\s*[:=]\s*\S+"),
    re.compile(r"-----BEGIN [^-]+ PRIVATE KEY-----.*?-----END [^-]+ PRIVATE KEY-----", re.I | re.S),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def redact(text: str) -> tuple[str, int]:
    count = 0
    for pattern in SECRET_PATTERNS:
        text, replaced = pattern.subn("[REDACTED-SENSITIVE-VALUE]", text)
        count += replaced
    return text, count


def first_goal(lines: list[str]) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith(("optimize,", "build ", "create ", "inspect ")):
            return stripped
    return "Convert the authorized session into a checked, reusable PMCR-O marketplace artifact."


def file_references(lines: list[str]) -> list[str]:
    found: list[str] = []
    pattern = re.compile(r"^[ \t]*([A-Za-z0-9][A-Za-z0-9_.-]*\.(?:txt|py|md|json|cs))\s*$")
    for line in lines:
        match = pattern.match(line)
        if match and match.group(1) not in found:
            found.append(match.group(1))
    return found


def next_intent(lines: list[str]) -> str:
    for index, line in enumerate(lines):
        if line.strip().lower().startswith(("next:", "next step:", "next milestone:")):
            same_line = line.split(":", 1)[1].strip()
            if same_line:
                return same_line
            for later in lines[index + 1 :]:
                if later.strip():
                    return later.strip()
    return "Re-open the derived package as a raw seed and admit only one evidence-backed domain adapter."


def domains(text: str) -> list[dict[str, Any]]:
    lower = text.lower()
    candidates = [
        ("marketplace", "skill catalog, plugin, and promotion surfaces"),
        ("mcp", "typed tool bridge and structured messages"),
        ("maf", "workflow and checkpoint runtime adapter"),
        ("terminal", "filesystem and command execution boundary"),
        ("provider", "model/provider capability claims"),
        ("windows-device", "W: or Desktop Commander connectivity"),
    ]
    result = []
    for name, purpose in candidates:
        if name in lower or (name == "windows-device" and ("w:" in lower or "desktop commander" in lower)):
            result.append({
                "id": name,
                "purpose": purpose,
                "simulation": True,
                "verified": False,
                "evidenceTier": "unknown",
                "accept": "design candidate only until direct domain evidence is supplied",
                "deny": "do not claim live access or runtime success from transcript text",
            })
    return result


def make_frame(frame_id: str, seq: int, role: str, kind: str, parent: dict[str, Any] | None, status: str, payload: dict[str, Any]) -> dict[str, Any]:
    frame = {
        "frame_id": frame_id,
        "trail_id": payload.pop("_trail_id"),
        "cycle_id": payload.pop("_cycle_id"),
        "seq": seq,
        "role": role,
        "kind": kind,
        "parent_id": parent["frame_id"] if parent else None,
        "prev_hash": parent["hash"] if parent else None,
        "status": status,
        "payload": payload,
    }
    material = json.dumps(frame, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    frame["hash"] = hashlib.sha256(material).hexdigest()
    return frame


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--include-raw", action="store_true")
    parser.add_argument("--max-cycles", type=int, default=3)
    args = parser.parse_args()
    if args.max_cycles < 1:
        parser.error("--max-cycles must be at least 1")
    try:
        source = args.source.expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(source)
        text = source.read_text(encoding="utf-8", errors="replace")
        redacted_text, redaction_count = redact(text)
        lines = text.splitlines()
        ingest_id = "ingest-" + sha256(source)[:12]
        trail_id = f"session:{ingest_id}"
        cycle_id = "cycle-0001"
        out = args.out.expanduser().resolve()
        (out / "source").mkdir(parents=True, exist_ok=True)
        (out / "pmcro").mkdir(parents=True, exist_ok=True)
        (out / "marketplace").mkdir(parents=True, exist_ok=True)
        (out / "training").mkdir(parents=True, exist_ok=True)
        (out / "reports").mkdir(parents=True, exist_ok=True)

        source_sha = sha256(source)
        source_manifest = {
            "ingestId": ingest_id,
            "path": str(source),
            "sha256": source_sha,
            "lineCount": len(lines),
            "authorized": True,
            "authorizationBasis": "user-supplied attachment in current session",
            "preservation": "read-only source; derived views are separate",
            "redactionApplied": True,
            "redactions": redaction_count,
        }
        write_json(out / "source/source-manifest.json", source_manifest)
        (out / "source/redacted-session.txt").write_text(redacted_text, encoding="utf-8")
        if args.include_raw:
            (out / "source/session.txt").write_text(text, encoding="utf-8")

        goal = first_goal(lines)
        refs = file_references(lines)
        domain_entries = domains(text)
        claims = []
        blocked = []
        for line in lines:
            lower = line.lower()
            if any(word in lower for word in ("verified", "passed", "implemented", "committed", "live api")):
                claims.append({"text": line.strip(), "status": "unknown", "evidenceTier": "unknown", "reason": "claim appears in transcript without attached runtime artifact"})
            if any(word in lower for word in ("blocked", "offline", "unverified", "remain pending")):
                blocked.append(line.strip())

        assessment = f"""# Derived architecture assessment\n\n- Ingest: `{ingest_id}`\n- Source SHA-256: `{source_sha}`\n- Source lines: `{len(lines)}`\n- Goal: {goal}\n- Explicit file references: {', '.join(refs) if refs else 'none'}\n- Domains: {', '.join(item['id'] for item in domain_entries) if domain_entries else 'none'}\n- Runtime claim policy: transcript claims remain `unknown` until direct artifacts are rerun.\n- Simulation policy: domain adapters are design candidates with `simulation: true` and `verified: false`.\n- Blocked indicators found: `{len(blocked)}`\n- Next raw seed: {next_intent(lines)}\n"""
        (out / "reports/architecture-assessment.md").write_text(assessment, encoding="utf-8")

        skill_candidate = {
            "kind": "skill-candidate",
            "skillId": "session-derived-spire-platform",
            "version": "0.1.0",
            "ingestId": ingest_id,
            "state": "staged",
            "promotable": False,
            "canonicalShape": {"requiredFolders": ["agents", "scripts", "references", "assets"], "requiresAgentFile": True},
            "sourceRefs": ["source/source-manifest.json", "source/redacted-session.txt"],
            "domains": domain_entries,
            "messageContract": {
                "input": {"sourceRef": "source/source-manifest.json", "consent": "user-authorized", "scope": "local transformation only"},
                "output": {"artifacts": ["pmcro/frames.jsonl", "training/candidates.jsonl"], "evidenceTier": "candidate"},
                "accept": ["source hash matches", "redaction is applied", "independent checker frame exists"],
                "deny": ["live W: access", "provider-private history", "automatic training", "automatic promotion"],
            },
        }
        write_json(out / "marketplace/skill-candidate.json", skill_candidate)

        training_rows = [
            {
                "id": f"{ingest_id}:constraint-boundary",
                "flow": "backward",
                "status": "candidate",
                "input": "An authorized session contains implementation claims and blocked access reports.",
                "output": "Separate transcript claims from rerunnable evidence and preserve the blocker as a next seed.",
                "accept": ["source event and hash are linked", "evidence tier is explicit"],
                "deny": ["upgrade prose claims to verified runtime facts"],
                "evidenceTier": "candidate",
                "metadata": {"redaction": "applied", "simulation": "labeled", "source": f"{ingest_id}:source"},
            },
            {
                "id": f"{ingest_id}:typed-domain-simulation",
                "flow": "backward",
                "status": "candidate",
                "input": "A domain such as MCP, MAF, terminal, or provider orchestration is mentioned without a reachable runtime.",
                "output": "Emit a typed simulation surface with input/output/accept/deny and no live-capability claim.",
                "accept": ["simulation=true", "verified=false", "domain scope is declared"],
                "deny": ["execute or publish the simulated adapter"],
                "evidenceTier": "simulation",
                "metadata": {"redaction": "applied", "simulation": "required", "source": f"{ingest_id}:domains"},
            },
        ]
        (out / "training/candidates.jsonl").write_text("\n".join(json.dumps(row, ensure_ascii=False, sort_keys=True) for row in training_rows) + "\n", encoding="utf-8")

        manifest = {
            "ingestId": ingest_id,
            "source": {"path": str(source), "sha256": source_sha, "lineCount": len(lines), "authorized": True, "redactionCount": redaction_count, "rawIncluded": args.include_raw},
            "input": {"sourceRef": "source/source-manifest.json", "consent": "user-authorized", "scope": "local-only session transformation", "maxCycles": args.max_cycles},
            "output": {"artifacts": ["source/source-manifest.json", "source/redacted-session.txt", "pmcro/frames.jsonl", "marketplace/skill-candidate.json", "training/candidates.jsonl", "reports/architecture-assessment.md"], "evidenceTier": "candidate"},
            "accept": ["source hash matches", "derived package validates", "checker frame is independent", "reflect seed remains unexecuted"],
            "deny": ["private provider logs", "credentials or tokens", "unverified runtime claims", "automatic model training", "automatic promotion", "unbounded recursion"],
            "simulationPolicy": {"simulation": True, "verified": False, "rule": "All unreachable MCP, terminal, MAF, provider, and code behavior remains labeled simulation."},
            "domains": domain_entries,
            "claimSummary": {"unknownClaims": len(claims), "blockedIndicators": len(blocked), "explicitFileReferences": refs},
            "promotion": "staged",
            "nextSeed": {"level": "meta2", "promptIntent": next_intent(lines), "unexecuted": True},
        }
        write_json(out / "manifest.json", manifest)

        base_scope = {"paths": [str(out)], "side_effects": "local-only", "source": str(source)}
        common = {"_trail_id": trail_id, "_cycle_id": cycle_id}
        route = make_frame("orchestrate-0001", 1, "orchestrator", "orchestrator.route", None, "complete", {
            **common,
            "goal": goal,
            "scope": base_scope,
            "next_role": "planner",
            "caps": {"loops": 1, "calls": 5, "seconds": 120, "max_depth": args.max_cycles},
            "accept": ["authorized source", "local-only derived package", "typed simulation boundaries"],
            "deny": ["provider login", "W: command execution", "automatic promotion"],
        })
        plan = make_frame("plan-0002", 2, "planner", "planner.plan", route, "complete", {
            **common,
            "acceptance_criteria": ["register and hash source", "emit redacted views", "emit typed candidate skill/training rows", "preserve simulation flags", "leave next seed unexecuted"],
            "validated_resources": [{"ref": str(source), "sha256": source_sha, "kind": "authorized-source"}, {"ref": "pmcro-session-marketplace", "kind": "skill-contract"}],
            "steps": [{"id": "ingest", "depends_on": []}, {"id": "project", "depends_on": ["ingest"]}, {"id": "check", "depends_on": ["project"]}, {"id": "reflect", "depends_on": ["check"]}],
            "input": {"sourceRef": str(source), "scope": "local-only"},
            "output": {"artifacts": manifest["output"]["artifacts"]},
            "accept": manifest["accept"],
            "deny": manifest["deny"],
        })
        generated_paths = [path.relative_to(out).as_posix() for path in sorted(out.rglob("*")) if path.is_file() and path.relative_to(out).as_posix() != "pmcro/frames.jsonl"]
        maker_files = [{"path": path, "action": "created", "sha256": sha256(out / path)} for path in generated_paths]
        maker = make_frame("make-0003", 3, "maker", "maker.result", plan, "complete", {
            **common,
            "plan_ref": plan["frame_id"],
            "files_changed": maker_files,
            "commands": [{"command": "python3 scripts/ingest_session.py", "exit_code": 0, "evidence_ref": "reports/architecture-assessment.md"}],
            "claim": "complete",
            "input": {"sourceRef": str(source), "consent": "user-authorized"},
            "output": {"staged": True, "evidenceTier": "candidate", "simulationDomains": [item["id"] for item in domain_entries]},
            "accept": ["files are local and hashed", "claims remain unknown where runtime evidence is absent"],
            "deny": ["checker verdict", "promotion", "live access"],
        })
        (out / "pmcro/frames.jsonl").write_text("\n".join(json.dumps(frame, ensure_ascii=False, sort_keys=True) for frame in (route, plan, maker)) + "\n", encoding="utf-8")
        write_json(out / "reports/maker.json", {"ingestId": ingest_id, "status": "complete", "files": generated_paths, "claim": "candidate package staged; no live runtime claim"})
        print(f"PASS: staged {ingest_id} with {len(generated_paths)} derived files and 3 PMCR-O frames")
        return 0
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
