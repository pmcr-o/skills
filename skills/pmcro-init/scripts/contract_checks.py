import copy
import hashlib
import json

PHASE_MARKERS = {
    "ORCHESTRATE": "/pmcro:orchestrate",
    "PLAN": "/pmcro:plan",
    "MAKE": "/pmcro:make",
    "CHECK": "/pmcro:check",
    "REFLECT": "/pmcro:reflect",
}


def normalize_grant(values):
    return frozenset(values)


def resolve_effective_grant(delegated, host_maximum, environment_maximum, denies=()):
    """Only PMCR-O core derives effective authority; adapters provide maxima/denies."""
    return (
        normalize_grant(delegated)
        & normalize_grant(host_maximum)
        & normalize_grant(environment_maximum)
    ) - normalize_grant(denies)


def serialization_matches(phase, marker):
    return PHASE_MARKERS.get(phase) == marker


def canonical_frame_bytes(frame):
    payload = copy.deepcopy(frame)
    payload.pop("frameDigest", None)
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def compute_frame_digest(frame):
    return hashlib.sha256(canonical_frame_bytes(frame)).hexdigest()


def validate_frame_integrity(frame, predecessor=None):
    if frame.get("frameDigest") != compute_frame_digest(frame):
        return False
    prior = frame.get("priorFrameDigest")
    if predecessor is None:
        return prior is None
    return prior == predecessor.get("frameDigest") and predecessor.get("frameDigest") == compute_frame_digest(predecessor)


def validate_verified_state(state):
    verdict = state.get("checkerVerdict", {})
    proof = state.get("evidenceProof", {})
    if verdict.get("verdict") != "PASS":
        return False
    if not verdict.get("checkerIdentityRef") or not verdict.get("makerIdentityRef"):
        return False
    if verdict["checkerIdentityRef"] == verdict["makerIdentityRef"]:
        return False
    if proof.get("proofKind") != "CHECKER_EVIDENCE":
        return False
    evidence = proof.get("evidenceRefs") or []
    if not evidence or not proof.get("evidenceDigest"):
        return False
    if any(item.get("kind") != "CHECKER_EVIDENCE_ARTIFACT" for item in evidence):
        return False
    if any(item.get("producerCheckerIdentityRef") != verdict["checkerIdentityRef"] for item in evidence):
        return False
    return True
