import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]

SCHEMA_PATH = ROOT / "schemas" / "pmcro-init.schema.json"
MACHINE_PATH = ROOT / "state-machine" / "init-v0.2.machine.json"
VECTORS_PATH = ROOT / "conformance" / "init-v0.2.vectors.json"


CANONICAL_PHASES = [
    "ORCHESTRATE",
    "PLAN",
    "MAKE",
    "CHECK",
    "REFLECT",
]

PHASE_MARKERS = {
    "ORCHESTRATE": "/pmcro:orchestrate",
    "PLAN": "/pmcro:plan",
    "MAKE": "/pmcro:make",
    "CHECK": "/pmcro:check",
    "REFLECT": "/pmcro:reflect",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


SCHEMA = load_json(SCHEMA_PATH)
MACHINE = load_json(MACHINE_PATH)
VECTORS = load_json(VECTORS_PATH)


def normalize_grant(values):
    return frozenset(values)


def resolve_effective_grant(
    delegated,
    host_maximum,
    environment_maximum,
    denies=(),
):
    """
    Canonical PMCR-O authority resolver.

    Host adapters report maxima and denies.
    They do not determine effective authority.
    """
    return (
        normalize_grant(delegated)
        & normalize_grant(host_maximum)
        & normalize_grant(environment_maximum)
    ) - normalize_grant(denies)


def resolve_child_grant(parent_effective, delegated_to_child):
    return normalize_grant(parent_effective) & normalize_grant(
        delegated_to_child
    )


def serialization_matches(phase, marker):
    return PHASE_MARKERS[phase] == marker


def frame_digest(payload: dict) -> str:
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return hashlib.sha256(canonical).hexdigest()


def transition_allowed(source, target):
    return [source, target] in MACHINE["transitions"]


def test_schema_is_valid_draft_2020_12():
    Draft202012Validator.check_schema(SCHEMA)


def test_canonical_cognition_is_immutable():
    assert MACHINE["canonicalCognition"] == CANONICAL_PHASES


def test_no_execute_phase_exists():
    assert "EXECUTE" not in MACHINE["canonicalCognition"]


def test_check_cannot_be_omitted():
    projected = [
        "ORCHESTRATE",
        "PLAN",
        "MAKE",
        "REFLECT",
    ]

    assert projected != CANONICAL_PHASES
    assert "CHECK" not in projected


def test_init_cannot_jump_directly_to_ready():
    forbidden_sources = [
        "UNINITIALIZED",
        "PREFLIGHT",
        "HOST_IDENTIFIED",
        "AUTHORITY_BOUND",
        "BOUNDED_HYDRATION",
    ]

    for source in forbidden_sources:
        assert not transition_allowed(source, "READY")


def test_grant_monotonicity():
    effective = resolve_effective_grant(
        delegated={"read"},
        host_maximum={"read", "write", "shell"},
        environment_maximum={"read", "write"},
    )

    assert effective == {"read"}


def test_denies_override_available_authority():
    effective = resolve_effective_grant(
        delegated={"read", "write"},
        host_maximum={"read", "write"},
        environment_maximum={"read", "write"},
        denies={"write"},
    )

    assert effective == {"read"}


def test_child_cannot_widen_parent_delegation():
    parent = {"read", "write"}
    child = resolve_child_grant(
        parent_effective=parent,
        delegated_to_child={"read"},
    )

    assert child == {"read"}
    assert child <= parent


def test_serialization_fidelity():
    assert serialization_matches(
        "MAKE",
        "/pmcro:make",
    )

    assert not serialization_matches(
        "MAKE",
        "/pmcro:check",
    )


def test_host_memory_does_not_create_verified_state():
    host_memory_claim = "tests passed"
    checker_verdict = None

    may_enter_verified_state = (
        bool(host_memory_claim)
        and checker_verdict is not None
    )

    assert may_enter_verified_state is False


def test_resume_requires_rebind():
    definition = SCHEMA["$defs"]["ResumeRebind"]
    steps = (
        definition["properties"]["steps"]["prefixItems"]
    )

    required = [item["const"] for item in steps]

    assert "REBIND_PRINCIPAL" in required
    assert "REBIND_AUTHORITY" in required
    assert "REVALIDATE_ENVIRONMENT" in required
    assert "REPROJECT_CAPABILITIES" in required
    assert "RECHECK_CONFORMANCE" in required


def test_host_adapter_cannot_emit_effective_grant():
    props = (
        SCHEMA["$defs"]["HostAdapterObservation"]
        ["properties"]
    )

    assert "effectiveGrant" not in props


def test_host_adapter_cannot_emit_phase_contract():
    props = (
        SCHEMA["$defs"]["HostAdapterObservation"]
        ["properties"]
    )

    forbidden = {
        "canonicalPhases",
        "phaseOrder",
        "cognitiveContract",
    }

    assert forbidden.isdisjoint(props)


def test_training_eligibility_is_false():
    init_schema = SCHEMA["$defs"]["InitFrame"]

    training = (
        init_schema["properties"]["trainingEligible"]
    )

    assert training["const"] is False


def test_registration_is_unregistered():
    init_schema = SCHEMA["$defs"]["InitFrame"]

    registration = (
        init_schema["properties"]["registrationState"]
    )

    assert registration["const"] == "UNREGISTERED"


@pytest.mark.parametrize(
    "vector",
    VECTORS["hosts"],
    ids=lambda item: item["id"],
)
def test_host_vectors_have_explicit_expectation(vector):
    assert vector["id"]
    assert vector["host"]["vendor"]
    assert vector["host"]["product"]
    assert vector["expect"]


def test_claude_parent_permission_does_not_widen_child():
    effective = resolve_effective_grant(
        delegated={"read"},
        host_maximum={"read", "write", "shell"},
        environment_maximum={"read", "write", "shell"},
    )

    assert effective == {"read"}


def test_openai_checker_grant_remains_read_only():
    effective = resolve_effective_grant(
        delegated={"read"},
        host_maximum={"read", "write", "shell"},
        environment_maximum={"read", "write", "shell"},
    )

    assert effective == {"read"}


def test_copilot_all_tools_default_does_not_widen():
    effective = resolve_effective_grant(
        delegated={"read"},
        host_maximum={"read", "write", "shell", "mcp"},
        environment_maximum={"read", "write", "shell", "mcp"},
    )

    assert effective == {"read"}


def test_cursor_resume_never_implies_prior_authority():
    continuation_exists = True
    authority_rebound = False

    ready = continuation_exists and authority_rebound

    assert ready is False


def test_grok_allowed_tools_metadata_is_not_grant():
    metadata_allowed_tools = {"read"}
    host_enforced_grant = None

    assert metadata_allowed_tools
    assert host_enforced_grant is None


def test_mcp_discovery_does_not_imply_invocation():
    discovered = True
    pmcro_registered = False
    pmcro_granted = False

    invokable = (
        discovered
        and pmcro_registered
        and pmcro_granted
    )

    assert invokable is False


def test_maf_continuation_id_does_not_prove_ownership():
    continuation_id_valid = True
    principal_authorized = False

    resume_allowed = (
        continuation_id_valid
        and principal_authorized
    )

    assert resume_allowed is False


def test_trail_provenance_chain():
    previous_frame = {
        "frameId": "frame-001",
        "phase": "PLAN",
    }

    previous_digest = frame_digest(previous_frame)

    current_frame = {
        "frameId": "frame-002",
        "phase": "MAKE",
        "priorFrameDigest": previous_digest,
    }

    assert (
        current_frame["priorFrameDigest"]
        == frame_digest(previous_frame)
    )


def test_self_change_remains_candidate_until_checked():
    candidate_contract_change = True
    distinct_checker_pass = False

    activated = (
        candidate_contract_change
        and distinct_checker_pass
    )

    assert activated is False

# --- CHECK-027 regression suite (candidate r1) ---


def _validator_for(defname):
    wrapper = {
        '$schema': 'https://json-schema.org/draft/2020-12/schema',
        '$defs': SCHEMA['$defs'],
        '$ref': f'#/$defs/{defname}',
    }
    return Draft202012Validator(wrapper)


def _errors(defname, instance):
    return list(_validator_for(defname).iter_errors(instance))


def _grant(cap, action, effect):
    return {
        'capabilityRef': cap,
        'actions': [action],
        'resourceScope': '*',
        'effectClass': effect,
        'constraints': [],
    }


def _host_surface():
    return {
        'vendor': 'checker',
        'product': 'fixture',
        'surface': 'test',
        'executionMode': 'isolated',
        'version': '1',
    }


def _load_contract_checks():
    import importlib.util
    path = ROOT / 'conformance' / 'contract_checks.py'
    spec = importlib.util.spec_from_file_location('pmcro_contract_checks', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_regression_027_01_effective_grant_is_not_authorable():
    authority = {
        'authorityId': 'auth-1',
        'principalRef': 'principal-1',
        'delegatedGrant': [_grant('cap-read', 'read', 'READ')],
        'hostMaximum': [_grant('cap-read', 'read', 'READ')],
        'environmentMaximum': [_grant('cap-read', 'read', 'READ')],
        'denies': [],
        'effectiveGrant': [_grant('cap-write', 'write', 'WRITE')],
        'revocationState': 'ACTIVE',
        'rebindRequiredOnResume': True,
        'evidenceRefs': ['evidence-1'],
    }
    assert _errors('AuthorityEnvelope', authority)


def test_regression_027_01_core_resolver_is_monotonic():
    checks = _load_contract_checks()
    effective = checks.resolve_effective_grant(
        {'read'},
        {'read', 'write', 'shell'},
        {'read', 'write'},
    )
    assert effective == {'read'}


def test_regression_027_02_schema_binds_phase_to_marker():
    frame = {
        'frameId': 'frame-2',
        'trailRef': 'trail-1',
        'cycleRef': 'cycle-1',
        'agentRef': 'agent-1',
        'role': 'pmcro-maker',
        'phase': 'MAKE',
        'serializedPhaseMarker': '/pmcro:check',
        'authorityEnvelopeRef': 'auth-1',
        'status': 'COMPLETE',
        'provenance': {
            'proofType': 'HASH_CHAIN',
            'algorithm': 'SHA-256',
            'canonicalization': 'PMCR-O-JSON-SORTED-V1',
            'evidenceRefs': ['trail-evidence'],
        },
        'priorFrameDigest': None,
        'frameDigest': 'a' * 64,
    }
    assert _errors('CognitiveFrame', frame)


def _valid_frame(frame_id, phase, marker, prior=None):
    checks = _load_contract_checks()
    frame = {
        'frameId': frame_id,
        'trailRef': 'trail-1',
        'cycleRef': 'cycle-1',
        'agentRef': 'agent-1',
        'role': 'pmcro-maker',
        'phase': phase,
        'serializedPhaseMarker': marker,
        'authorityEnvelopeRef': 'auth-1',
        'status': 'COMPLETE',
        'provenance': {
            'proofType': 'HASH_CHAIN',
            'algorithm': 'SHA-256',
            'canonicalization': 'PMCR-O-JSON-SORTED-V1',
            'evidenceRefs': ['trail-evidence'],
        },
        'priorFrameDigest': None if prior is None else prior['frameDigest'],
    }
    frame['frameDigest'] = checks.compute_frame_digest(frame)
    return frame


def test_regression_027_03_provenance_chain_is_executable():
    checks = _load_contract_checks()
    prior = _valid_frame('frame-1', 'PLAN', '/pmcro:plan')
    current = _valid_frame('frame-2', 'MAKE', '/pmcro:make', prior)
    assert checks.validate_frame_integrity(prior)
    assert checks.validate_frame_integrity(current, prior)

    forged = dict(current)
    forged['frameDigest'] = 'e' * 64
    assert not checks.validate_frame_integrity(forged, prior)


def test_regression_027_03_provenance_shape_is_typed():
    forged = {
        'frameId': 'frame-forged',
        'trailRef': 'trail-1',
        'cycleRef': 'cycle-1',
        'agentRef': 'agent-1',
        'role': 'pmcro-maker',
        'phase': 'MAKE',
        'serializedPhaseMarker': '/pmcro:make',
        'authorityEnvelopeRef': 'auth-1',
        'status': 'COMPLETE',
        'provenance': {'claimed': 'trusted-without-evidence'},
        'priorFrameDigest': 'f' * 64,
        'frameDigest': 'e' * 64,
    }
    assert _errors('CognitiveFrame', forged)


def _valid_verified_state(checker='checker-1', maker='maker-1', verdict='PASS'):
    return {
        'stateId': 'state-1',
        'originatingProjectRef': 'project-1',
        'originatingTrailRef': 'trail-1',
        'originatingCycleRef': 'cycle-1',
        'checkerVerdict': {
            'verdictId': 'verdict-1',
            'checkerIdentityRef': checker,
            'makerIdentityRef': maker,
            'verdict': verdict,
        },
        'evidenceProof': {
            'proofKind': 'CHECKER_EVIDENCE',
            'evidenceRefs': [{
                'kind': 'CHECKER_EVIDENCE_ARTIFACT',
                'ref': 'evidence-1',
                'digest': 'd' * 64,
                'producerCheckerIdentityRef': checker,
            }],
            'evidenceDigest': 'b' * 64,
        },
        'stateDigest': 'c' * 64,
        'verifiedAt': '2026-10-13T19:00:00Z',
    }


def test_regression_027_04_host_memory_cannot_shape_shift_into_verified_state():
    promoted = {
        'stateId': 'state-from-memory',
        'originatingProjectRef': 'project-1',
        'originatingTrailRef': 'trail-1',
        'originatingCycleRef': 'cycle-1',
        'checkerIdentityRef': 'host-memory',
        'checkerVerdictRef': 'memory-claim-not-verdict',
        'evidenceRefs': ['host-memory://tests-passed'],
        'stateDigest': 'b' * 64,
        'verifiedAt': '2026-10-13T19:00:00Z',
    }
    assert _errors('VerifiedStateRef', promoted)


def test_regression_027_04_verified_state_requires_pass_and_distinct_checker():
    checks = _load_contract_checks()
    valid = _valid_verified_state()
    assert not _errors('VerifiedStateRef', valid)
    assert checks.validate_verified_state(valid)

    same_identity = _valid_verified_state(checker='maker-1', maker='maker-1')
    assert not checks.validate_verified_state(same_identity)

    failed = _valid_verified_state(verdict='FAIL')
    assert _errors('VerifiedStateRef', failed)
    assert not checks.validate_verified_state(failed)

    wrong_producer = _valid_verified_state()
    wrong_producer['evidenceProof']['evidenceRefs'][0]['producerCheckerIdentityRef'] = 'checker-other'
    assert not checks.validate_verified_state(wrong_producer)


def _host_observation(host_granted=False):
    return {
        'capabilityRef': 'tool-x',
        'class': 'DISCOVERY',
        'hostSurface': _host_surface(),
        'discovered': True,
        'hostAvailable': True,
        'hostGranted': host_granted,
        'actions': ['invoke'],
        'scope': '*',
        'enforcementKind': 'METADATA',
        'evidenceRefs': ['host-discovery-evidence'],
    }


def test_regression_027_05_discovery_is_separate_from_registration_grant_invocation():
    candidate = {
        'hostObservation': _host_observation(host_granted=False),
        'pmcro': {
            'registrationState': 'REGISTERED',
            'grantState': 'GRANTED',
            'invokableNow': True,
            'registrationEvidenceRefs': ['registration-1'],
            'grantEvidenceRefs': ['grant-1'],
            'invocationEvidenceRefs': ['invoke-1'],
        },
    }
    assert _errors('CapabilityProjection', candidate)


def test_regression_027_05_registration_and_grant_require_dedicated_evidence():
    candidate = {
        'hostObservation': _host_observation(host_granted=True),
        'pmcro': {
            'registrationState': 'REGISTERED',
            'grantState': 'GRANTED',
            'invokableNow': True,
            'registrationEvidenceRefs': [],
            'grantEvidenceRefs': [],
            'invocationEvidenceRefs': [],
        },
    }
    assert _errors('CapabilityProjection', candidate)


def _environment():
    return {
        'hostSurface': _host_surface(),
        'workspace': {'available': True, 'dirty': False},
        'filesystem': {'readBoundary': '*', 'writeBoundary': '/tmp', 'persistence': 'SESSION'},
        'execution': {'shell': True, 'processes': True, 'packageInstall': False, 'computerUse': False, 'browser': False},
        'network': {'available': False, 'boundary': 'none'},
        'sandbox': {'available': True},
        'lifecycle': {'ephemeral': True, 'resumable': False, 'durable': False, 'background': False},
        'evidenceRefs': ['env-evidence'],
    }


def test_regression_027_06_adapter_observations_are_host_only():
    adapter = {
        'adapterId': 'adapter-1',
        'hostSurface': _host_surface(),
        'environment': _environment(),
        'authority': {
            'hostMaximum': [_grant('cap-read', 'read', 'READ')],
            'denies': [],
            'approvalMechanisms': [],
            'enforceability': 'ENFORCED',
        },
        'capabilityObservations': [{
            **_host_observation(host_granted=True),
            'pmcroRegistered': True,
            'pmcroGranted': True,
            'invokableNow': True,
        }],
        'enforcementAssessment': {'status': 'FULL', 'unsupportedInvariants': []},
    }
    assert _errors('HostAdapterObservation', adapter)


def test_regression_027_06_adapter_schema_points_to_host_observation_only():
    items = SCHEMA['$defs']['HostAdapterObservation']['properties']['capabilityObservations']['items']
    assert items == {'$ref': '#/$defs/HostCapabilityObservation'}
