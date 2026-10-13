#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
QUEUE_DIRS = ("inbox", "processing", "delayed", "completed", "dead-letter", "state", "receipts", "tmp")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_time(value: str | None):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + f".tmp.{os.getpid()}")
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def ensure_root(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for name in QUEUE_DIRS:
        (root / name).mkdir(parents=True, exist_ok=True)


def config_path(root: Path) -> Path:
    return root / "config.json"


def read_config(root: Path) -> dict:
    path = config_path(root)
    if not path.is_file():
        raise ValueError("queue is not initialized")
    return load_json(path)


def safe_id(value: str, label: str) -> None:
    if not SAFE_ID.fullmatch(value):
        raise ValueError(f"invalid {label}")


def body_for_content(msg: dict) -> dict:
    return {k: v for k, v in msg.items() if k not in {"contentDigest", "dedupeDigest"}}


def body_for_dedupe(msg: dict) -> dict:
    ignored = {"contentDigest", "dedupeDigest", "createdAt", "availableAt"}
    return {k: v for k, v in msg.items() if k not in ignored}


def content_digest(msg: dict) -> str:
    return sha256_bytes(canonical(body_for_content(msg)))


def dedupe_digest(msg: dict) -> str:
    return sha256_bytes(canonical(body_for_dedupe(msg)))


def locate(root: Path, message_id: str):
    for name in ("inbox", "processing", "delayed", "completed", "dead-letter"):
        path = root / name / f"{message_id}.json"
        if path.is_file():
            return path
    return None


def state_path(root: Path, message_id: str) -> Path:
    return root / "state" / f"{message_id}.json"


def read_state(root: Path, message_id: str):
    path = state_path(root, message_id)
    return load_json(path) if path.is_file() else None


def validate_message(msg: dict, cfg: dict) -> None:
    required = [
        "apiVersion", "kind", "messageId", "traceId", "correlationId", "parentMessageId", "causationId",
        "trailId", "cycleId", "sourceAgent", "targetAgent", "plugin", "skill", "createdAt", "availableAt",
        "expiresAt", "evidenceStatus", "grantRefs", "payload", "dedupeDigest", "contentDigest"
    ]
    missing = [name for name in required if name not in msg]
    if missing:
        raise ValueError("missing message fields: " + ", ".join(missing))
    if msg["apiVersion"] != "pmcro.message/v1":
        raise ValueError("unsupported apiVersion")
    for key in ("messageId", "traceId", "correlationId"):
        safe_id(str(msg[key]), key)
    if msg["targetAgent"] != cfg["agent"]:
        raise ValueError("targetAgent does not match queue owner")
    if msg["kind"] not in cfg["allowedKinds"]:
        raise ValueError("message kind not allowed")
    if msg["evidenceStatus"] not in {"CONFIRMED", "NOT-YET-VERIFIED", "NOT-RUN"}:
        raise ValueError("invalid evidenceStatus")
    if content_digest(msg) != msg["contentDigest"]:
        raise ValueError("content digest mismatch")
    if dedupe_digest(msg) != msg["dedupeDigest"]:
        raise ValueError("dedupe digest mismatch")


def init_queue(root: Path, agent: str, kinds_file: Path, lease_seconds: int, max_attempts: int, retry_base_seconds: int):
    ensure_root(root)
    safe_id(agent, "agent")
    kinds_doc = load_json(kinds_file)
    kinds = sorted(kinds_doc.get("kinds", {}).keys())
    if not kinds:
        raise ValueError("allowed message kinds are empty")
    cfg = {
        "schema": "pmcro.queue/v1",
        "agent": agent,
        "transport": "filesystem-spool-v1",
        "status": "candidate-unregistered",
        "durability": "write-temp-then-atomic-move",
        "delivery": "at-least-once",
        "ordering": "best-effort FIFO by inbox write time; correctness must not depend on global order",
        "leaseSeconds": lease_seconds,
        "maxAttempts": max_attempts,
        "retryBaseSeconds": retry_base_seconds,
        "deduplication": "messageId + dedupeDigest; contentDigest protects exact immutable envelope body",
        "immutableEnvelope": True,
        "mutableStateSeparated": True,
        "ackReceiptImmutable": True,
        "sharedMutableTrail": False,
        "receiverCreatesLocalTrail": True,
        "grantsAuthority": False,
        "phaseInjectionAllowed": False,
        "autoExecutesNextSeed": False,
        "allowedKinds": kinds,
    }
    atomic_json(config_path(root), cfg)
    return cfg


def enqueue(root: Path, args) -> dict:
    cfg = read_config(root)
    safe_id(args.message_id, "messageId")
    safe_id(args.trace_id or args.message_id, "traceId")
    safe_id(args.correlation_id or args.trace_id or args.message_id, "correlationId")
    payload = load_json(Path(args.payload_file)) if args.payload_file else {}
    now = utc_now()
    available = now + timedelta(seconds=max(0, args.delay_seconds))
    msg = {
        "apiVersion": "pmcro.message/v1",
        "kind": args.kind,
        "messageId": args.message_id,
        "traceId": args.trace_id or args.message_id,
        "correlationId": args.correlation_id or args.trace_id or args.message_id,
        "parentMessageId": args.parent_message_id or "",
        "causationId": args.causation_id or "",
        "trailId": args.trail_id,
        "cycleId": args.cycle_id,
        "sourceAgent": args.source_agent,
        "targetAgent": args.target_agent,
        "plugin": args.plugin or "",
        "skill": args.skill or "",
        "createdAt": iso(now),
        "availableAt": iso(available),
        "expiresAt": args.expires_at or "",
        "evidenceStatus": args.evidence_status,
        "grantRefs": args.grant_ref or [],
        "payload": payload,
    }
    msg["dedupeDigest"] = dedupe_digest(msg)
    msg["contentDigest"] = content_digest(msg)
    validate_message(msg, cfg)
    existing = locate(root, args.message_id)
    receipt = root / "receipts" / f"{args.message_id}.json"
    if existing:
        old = load_json(existing)
        if old.get("dedupeDigest") == msg["dedupeDigest"]:
            return {"status": "IDEMPOTENT", "messageId": args.message_id, "contentDigest": old["contentDigest"]}
        raise ValueError("messageId conflict with different semantic content")
    if receipt.is_file():
        old_receipt = load_json(receipt)
        if old_receipt.get("dedupeDigest") == msg["dedupeDigest"]:
            return {"status": "IDEMPOTENT", "messageId": args.message_id, "contentDigest": old_receipt["messageDigest"]}
        raise ValueError("messageId conflicts with completed receipt")
    temp = root / "tmp" / f"{args.message_id}.{os.getpid()}.json"
    atomic_json(temp, msg)
    destination = root / ("delayed" if args.delay_seconds > 0 else "inbox") / f"{args.message_id}.json"
    os.replace(temp, destination)
    atomic_json(state_path(root, args.message_id), {
        "messageId": args.message_id,
        "status": "DELAYED" if args.delay_seconds > 0 else "ENQUEUED",
        "attempt": 0,
        "availableAt": msg["availableAt"],
        "claimedBy": "",
        "leaseUntil": "",
        "lastError": "",
        "updatedAt": iso(now),
    })
    return {"status": "ENQUEUED", "messageId": args.message_id, "contentDigest": msg["contentDigest"], "dedupeDigest": msg["dedupeDigest"]}


def recover(root: Path) -> dict:
    cfg = read_config(root)
    now = utc_now()
    moved = []
    for name in ("inbox", "processing", "delayed"):
        for path in sorted((root / name).glob("*.json")):
            msg = load_json(path)
            try:
                validate_message(msg, cfg)
            except Exception:
                continue
            mid = msg["messageId"]
            state = read_state(root, mid) or {"messageId": mid, "attempt": 0, "status": name.upper()}
            expiry = parse_time(msg.get("expiresAt"))
            if expiry and expiry <= now:
                os.replace(path, root / "dead-letter" / path.name)
                state.update({"status": "DEAD_LETTER", "claimedBy": "", "leaseUntil": "", "lastError": "expired", "updatedAt": iso(now)})
                atomic_json(state_path(root, mid), state)
                moved.append([mid, "DEAD_LETTER"])
                continue
            if name == "processing":
                lease_until = parse_time(state.get("leaseUntil"))
                if lease_until and lease_until <= now:
                    if int(state.get("attempt", 0)) >= int(cfg["maxAttempts"]):
                        destination = root / "dead-letter" / path.name
                        state["status"] = "DEAD_LETTER"
                        state["lastError"] = "lease expired at max attempts"
                    else:
                        delay = int(cfg["retryBaseSeconds"]) * (2 ** max(0, int(state.get("attempt", 0)) - 1))
                        destination = root / "delayed" / path.name
                        state["status"] = "DELAYED"
                        state["availableAt"] = iso(now + timedelta(seconds=delay))
                        state["lastError"] = "lease expired"
                    state["claimedBy"] = ""
                    state["leaseUntil"] = ""
                    state["updatedAt"] = iso(now)
                    os.replace(path, destination)
                    atomic_json(state_path(root, mid), state)
                    moved.append([mid, state["status"]])
            elif name == "delayed":
                available = parse_time(state.get("availableAt") or msg.get("availableAt"))
                if available and available <= now:
                    os.replace(path, root / "inbox" / path.name)
                    state.update({"status": "ENQUEUED", "updatedAt": iso(now)})
                    atomic_json(state_path(root, mid), state)
                    moved.append([mid, "ENQUEUED"])
    return {"status": "RECOVERED", "moved": moved}


def claim(root: Path, worker_id: str, message_id: str | None, kind: str | None):
    cfg = read_config(root)
    safe_id(worker_id, "workerId")
    recover(root)
    now = utc_now()
    files = sorted((root / "inbox").glob("*.json"), key=lambda p: (p.stat().st_mtime_ns, p.name))
    for path in files:
        if message_id and path.stem != message_id:
            continue
        msg = load_json(path)
        validate_message(msg, cfg)
        if kind and msg["kind"] != kind:
            continue
        state = read_state(root, msg["messageId"]) or {"messageId": msg["messageId"], "attempt": 0}
        destination = root / "processing" / path.name
        try:
            os.replace(path, destination)
        except FileNotFoundError:
            continue
        state.update({
            "status": "PROCESSING",
            "attempt": int(state.get("attempt", 0)) + 1,
            "claimedBy": worker_id,
            "leaseUntil": iso(now + timedelta(seconds=int(cfg["leaseSeconds"]))),
            "updatedAt": iso(now),
        })
        atomic_json(state_path(root, msg["messageId"]), state)
        return {"status": "CLAIMED", "path": str(destination), "message": msg, "delivery": state}
    return {"status": "NO_MESSAGE"}


def ack(root: Path, message_id: str, worker_id: str, result_file: str | None):
    safe_id(message_id, "messageId")
    safe_id(worker_id, "workerId")
    source = root / "processing" / f"{message_id}.json"
    if not source.is_file():
        raise ValueError("processing message not found")
    msg = load_json(source)
    state = read_state(root, message_id)
    if not state or state.get("status") != "PROCESSING" or state.get("claimedBy") != worker_id:
        raise ValueError("worker does not own lease")
    receipt_path = root / "receipts" / f"{message_id}.json"
    if receipt_path.exists():
        raise ValueError("receipt already exists")
    result_digest = sha256_bytes(Path(result_file).read_bytes()) if result_file else ""
    now = utc_now()
    destination = root / "completed" / source.name
    os.replace(source, destination)
    receipt = {
        "schema": "pmcro.queue.receipt/v1",
        "messageId": message_id,
        "messageDigest": msg["contentDigest"],
        "dedupeDigest": msg["dedupeDigest"],
        "workerId": worker_id,
        "attempt": int(state.get("attempt", 0)),
        "completedAt": iso(now),
        "resultDigest": result_digest,
        "sourceAgent": msg["sourceAgent"],
        "targetAgent": msg["targetAgent"],
        "sourceTrailRef": msg["trailId"],
    }
    atomic_json(receipt_path, receipt)
    state.update({"status": "COMPLETED", "claimedBy": "", "leaseUntil": "", "updatedAt": iso(now)})
    atomic_json(state_path(root, message_id), state)
    return {"status": "ACKED", "receipt": receipt}


def nack(root: Path, message_id: str, worker_id: str, reason: str, retry_delay_seconds: int | None):
    cfg = read_config(root)
    safe_id(message_id, "messageId")
    safe_id(worker_id, "workerId")
    source = root / "processing" / f"{message_id}.json"
    if not source.is_file():
        raise ValueError("processing message not found")
    state = read_state(root, message_id)
    if not state or state.get("status") != "PROCESSING" or state.get("claimedBy") != worker_id:
        raise ValueError("worker does not own lease")
    now = utc_now()
    if int(state.get("attempt", 0)) >= int(cfg["maxAttempts"]):
        destination = root / "dead-letter" / source.name
        state["status"] = "DEAD_LETTER"
    else:
        delay = retry_delay_seconds if retry_delay_seconds is not None else int(cfg["retryBaseSeconds"]) * (2 ** max(0, int(state.get("attempt", 0)) - 1))
        destination = root / "delayed" / source.name
        state["status"] = "DELAYED"
        state["availableAt"] = iso(now + timedelta(seconds=max(0, delay)))
    state.update({"lastError": reason, "claimedBy": "", "leaseUntil": "", "updatedAt": iso(now)})
    os.replace(source, destination)
    atomic_json(state_path(root, message_id), state)
    return {"status": state["status"], "messageId": message_id, "attempt": state["attempt"]}


def stats(root: Path):
    cfg = read_config(root)
    result = {"agent": cfg["agent"], "transport": cfg["transport"], "grantsAuthority": cfg["grantsAuthority"]}
    for name in ("inbox", "processing", "delayed", "completed", "dead-letter", "receipts"):
        result[name] = len(list((root / name).glob("*.json")))
    return result


def emit(value, code=0):
    print(json.dumps(value, indent=2, sort_keys=True))
    return code


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="op", required=True)

    init = sub.add_parser("init")
    init.add_argument("--root", required=True); init.add_argument("--agent", required=True); init.add_argument("--allowed-kinds-file", required=True); init.add_argument("--lease-seconds", type=int, default=300); init.add_argument("--max-attempts", type=int, default=3); init.add_argument("--retry-base-seconds", type=int, default=5)

    enq = sub.add_parser("enqueue")
    enq.add_argument("--root", required=True); enq.add_argument("--kind", required=True); enq.add_argument("--message-id", required=True); enq.add_argument("--trace-id"); enq.add_argument("--correlation-id"); enq.add_argument("--parent-message-id"); enq.add_argument("--causation-id"); enq.add_argument("--trail-id", required=True); enq.add_argument("--cycle-id", required=True); enq.add_argument("--source-agent", required=True); enq.add_argument("--target-agent", required=True); enq.add_argument("--plugin"); enq.add_argument("--skill"); enq.add_argument("--payload-file"); enq.add_argument("--evidence-status", default="NOT-RUN"); enq.add_argument("--grant-ref", action="append"); enq.add_argument("--delay-seconds", type=int, default=0); enq.add_argument("--expires-at")

    cl = sub.add_parser("claim")
    cl.add_argument("--root", required=True); cl.add_argument("--worker-id", required=True); cl.add_argument("--message-id"); cl.add_argument("--kind")

    ak = sub.add_parser("ack")
    ak.add_argument("--root", required=True); ak.add_argument("--message-id", required=True); ak.add_argument("--worker-id", required=True); ak.add_argument("--result-file")

    nk = sub.add_parser("nack")
    nk.add_argument("--root", required=True); nk.add_argument("--message-id", required=True); nk.add_argument("--worker-id", required=True); nk.add_argument("--reason", required=True); nk.add_argument("--retry-delay-seconds", type=int)

    rc = sub.add_parser("recover")
    rc.add_argument("--root", required=True)

    vm = sub.add_parser("verify-message")
    vm.add_argument("--root", required=True); vm.add_argument("--message-file", required=True)

    st = sub.add_parser("stats")
    st.add_argument("--root", required=True)

    a = p.parse_args()
    root = Path(a.root)
    try:
        if a.op == "init":
            return emit(init_queue(root, a.agent, Path(a.allowed_kinds_file), a.lease_seconds, a.max_attempts, a.retry_base_seconds))
        if a.op == "enqueue":
            return emit(enqueue(root, a))
        if a.op == "claim":
            return emit(claim(root, a.worker_id, a.message_id, a.kind))
        if a.op == "ack":
            return emit(ack(root, a.message_id, a.worker_id, a.result_file))
        if a.op == "nack":
            return emit(nack(root, a.message_id, a.worker_id, a.reason, a.retry_delay_seconds))
        if a.op == "recover":
            return emit(recover(root))
        if a.op == "verify-message":
            cfg = read_config(root); msg = load_json(Path(a.message_file)); validate_message(msg, cfg); return emit({"status": "VALID", "messageId": msg["messageId"], "contentDigest": msg["contentDigest"]})
        return emit(stats(root))
    except Exception as exc:
        return emit({"status": "HALT", "error": str(exc)}, 2)


if __name__ == "__main__":
    raise SystemExit(main())
