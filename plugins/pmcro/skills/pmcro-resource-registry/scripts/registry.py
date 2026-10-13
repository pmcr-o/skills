#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest_path(path: Path):
    path = path.resolve()
    if path.is_file():
        return sha256_bytes(path.read_bytes()), "file", 1
    if not path.is_dir():
        raise ValueError("content path does not exist")
    h = hashlib.sha256()
    count = 0
    for item in sorted(x for x in path.rglob("*") if x.is_file()):
        rel = item.relative_to(path).as_posix()
        h.update(rel.encode("utf-8")); h.update(b"\0")
        h.update(hashlib.sha256(item.read_bytes()).digest()); h.update(b"\n")
        count += 1
    return h.hexdigest(), "tree", count


def event_digest(event: dict) -> str:
    body = dict(event)
    body.pop("eventDigest", None)
    return sha256_bytes(canonical(body))


def record_digest(record: dict) -> str:
    body = dict(record)
    body.pop("recordDigest", None)
    return sha256_bytes(canonical(body))


def manifest(root: Path):
    path = root / "manifest.json"
    return load_json(path) if path.is_file() else {"schema": "pmcro.resource-registry-manifest/v1", "sequence": 0, "headDigest": ""}


def event_files(root: Path):
    folder = root / "events"
    return sorted(folder.glob("*.json")) if folder.is_dir() else []


def validate_checker(path: Path, producer: str):
    raw = path.read_bytes()
    data = json.loads(raw.decode("utf-8-sig"))
    if data.get("kind") != "checker.verdict" or data.get("verdict") != "PASS":
        raise ValueError("checker artifact must be checker.verdict PASS")
    checker = str(data.get("checker", "")).strip()
    if not checker:
        raise ValueError("checker identity missing")
    if producer and checker == producer:
        raise ValueError("producer cannot independently validate its own resource")
    return data, raw, sha256_bytes(raw)


def verify(root: Path) -> dict:
    root = root.resolve()
    mf = manifest(root)
    expected_seq = 0
    prev = ""
    state = {}
    errors = []
    for path in event_files(root):
        try:
            event = load_json(path)
        except Exception as exc:
            errors.append(f"event unreadable {path.name}: {exc}")
            continue
        expected_seq += 1
        if event.get("sequence") != expected_seq:
            errors.append(f"sequence mismatch {path.name}")
        if event.get("previousEventDigest", "") != prev:
            errors.append(f"previous digest mismatch {path.name}")
        actual = event_digest(event)
        if event.get("eventDigest") != actual:
            errors.append(f"event digest mismatch {path.name}")
        rid = event.get("resourceId")
        action = event.get("action")
        if action == "REGISTER":
            rd = event.get("recordDigest", "")
            rp = root / "records" / f"{rd}.json"
            if not rp.is_file():
                errors.append(f"missing record {rd}")
            else:
                record = load_json(rp)
                if record.get("recordDigest") != rd or record_digest(record) != rd:
                    errors.append(f"record digest mismatch {rid}")
                ed = record.get("checkerDigest", "")
                ep = root / "evidence" / f"{ed}.json"
                if not ep.is_file() or sha256_bytes(ep.read_bytes()) != ed:
                    errors.append(f"checker evidence mismatch {rid}")
                state[rid] = {"record": record, "revoked": False, "event": event}
        elif action == "REVOKE":
            if rid not in state:
                errors.append(f"revocation without registration {rid}")
            else:
                state[rid]["revoked"] = True
                state[rid]["revocation"] = event
        else:
            errors.append(f"unsupported action {action}")
        prev = actual
    if mf.get("sequence", 0) != expected_seq:
        errors.append("manifest sequence mismatch")
    if mf.get("headDigest", "") != prev:
        errors.append("manifest head mismatch")
    return {"schema": "pmcro.resource-registry-verification/v1", "valid": not errors, "sequence": expected_seq, "headDigest": prev, "resources": state, "errors": errors}


def append_event(root: Path, action: str, resource_id: str, trail_ref: str, extra: dict):
    mf = manifest(root)
    event = {
        "schema": "pmcro.resource-registry-event/v1",
        "sequence": int(mf.get("sequence", 0)) + 1,
        "previousEventDigest": mf.get("headDigest", ""),
        "action": action,
        "resourceId": resource_id,
        "createdAt": utc_now(),
        "actorAgent": "pmcro-resource-registry",
        "trailRef": trail_ref,
        **extra,
    }
    event["eventDigest"] = event_digest(event)
    target = root / "events" / f"{event['sequence']:08d}-{event['eventDigest']}.json"
    if target.exists():
        raise ValueError("event already exists")
    atomic_json(target, event)
    atomic_json(root / "manifest.json", {"schema": "pmcro.resource-registry-manifest/v1", "sequence": event["sequence"], "headDigest": event["eventDigest"], "updatedAt": event["createdAt"]})
    return event


def register(root: Path, resource_id: str, kind: str, content: Path, producer: str, checker_path: Path, trail_ref: str):
    if not SAFE_ID.fullmatch(resource_id):
        raise ValueError("invalid resource id")
    current = verify(root)
    if not current["valid"]:
        raise ValueError("registry verification failed before registration")
    active = current["resources"].get(resource_id)
    if active and not active.get("revoked"):
        raise ValueError("resource id already registered")
    check, raw, check_digest = validate_checker(checker_path, producer)
    digest, content_type, item_count = digest_path(content)
    next_sequence = int(manifest(root).get("sequence", 0)) + 1
    record = {
        "schema": "pmcro.registry-record/v1",
        "resourceId": resource_id,
        "resourceKind": kind,
        "state": "registered-checked",
        "contentDigest": digest,
        "contentType": content_type,
        "itemCount": item_count,
        "producerAgent": producer,
        "checker": check["checker"],
        "checkerDigest": check_digest,
        "checkerVerdictRef": str(checker_path.resolve()),
        "registrationRef": f"registry-event:{next_sequence}",
        "grantRefs": [],
        "provenanceRefs": [trail_ref, str(content.resolve())],
        "availableToPlanner": True,
        "createdAt": utc_now(),
    }
    record["recordDigest"] = record_digest(record)
    evidence_target = root / "evidence" / f"{check_digest}.json"
    if not evidence_target.exists():
        evidence_target.parent.mkdir(parents=True, exist_ok=True)
        evidence_target.write_bytes(raw)
    atomic_json(root / "records" / f"{record['recordDigest']}.json", record)
    event = append_event(root, "REGISTER", resource_id, trail_ref, {"recordDigest": record["recordDigest"]})
    return {"record": record, "event": event}


def revoke(root: Path, resource_id: str, trail_ref: str, reason: str):
    state = verify(root)
    if not state["valid"]:
        raise ValueError("registry verification failed")
    current = state["resources"].get(resource_id)
    if not current or current.get("revoked"):
        raise ValueError("resource is not an active registered resource")
    return append_event(root, "REVOKE", resource_id, trail_ref, {"reason": reason})


def resolve(root: Path, resource_id: str):
    state = verify(root)
    current = state["resources"].get(resource_id)
    admissible = bool(
        state["valid"]
        and current
        and not current.get("revoked")
        and current["record"].get("state") == "registered-checked"
        and current["record"].get("availableToPlanner") is True
    )
    return {
        "schema": "pmcro.resource-resolution/v1",
        "resourceId": resource_id,
        "registryValid": state["valid"],
        "admissibleToPlanner": admissible,
        "record": current["record"] if current else None,
        "revoked": bool(current and current.get("revoked")),
        "errors": state["errors"],
    }


def emit(value, code=0):
    print(json.dumps(value, indent=2, sort_keys=True))
    return code


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="op", required=True)
    reg = sub.add_parser("register")
    reg.add_argument("--root", required=True); reg.add_argument("--resource-id", required=True); reg.add_argument("--kind", required=True); reg.add_argument("--content", required=True); reg.add_argument("--producer-agent", required=True); reg.add_argument("--checker-evidence", required=True); reg.add_argument("--trail-ref", required=True)
    res = sub.add_parser("resolve")
    res.add_argument("--root", required=True); res.add_argument("--resource-id", required=True)
    rev = sub.add_parser("revoke")
    rev.add_argument("--root", required=True); rev.add_argument("--resource-id", required=True); rev.add_argument("--trail-ref", required=True); rev.add_argument("--reason", required=True)
    ver = sub.add_parser("verify")
    ver.add_argument("--root", required=True)
    a = p.parse_args()
    root = Path(a.root)
    try:
        if a.op == "register":
            return emit(register(root, a.resource_id, a.kind, Path(a.content), a.producer_agent, Path(a.checker_evidence), a.trail_ref))
        if a.op == "resolve":
            out = resolve(root, a.resource_id)
            return emit(out, 0 if out["admissibleToPlanner"] else 3)
        if a.op == "revoke":
            return emit(revoke(root, a.resource_id, a.trail_ref, a.reason))
        out = verify(root)
        return emit(out, 0 if out["valid"] else 4)
    except Exception as exc:
        return emit({"status": "HALT", "error": str(exc)}, 2)


if __name__ == "__main__":
    raise SystemExit(main())
