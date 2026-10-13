import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROLE_IDS = {
    "pmcro-orchestrator",
    "pmcro-planner",
    "pmcro-maker",
    "pmcro-checker",
    "pmcro-reflector",
}
EXPECTED_VERSION = "0.4.1-candidate"
EXPECTED_FROZEN_ZIP = "d1019453cfe5c23584dcd01485caee3d294886783d4a712a62a32c7338b374da"


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(skill: str) -> str:
    base = ROOT / "skills" / skill
    files = sorted(
        (p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"),
        key=lambda p: p.relative_to(ROOT).as_posix(),
    )
    entries = [
        {"path": p.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()}
        for p in files
    ]
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def test_canonical_version_transition_is_coordinated():
    marketplace = load(".pmcro-plugin/marketplace.json")
    plugin = load("plugins/pmcro/.pmcro-plugin/plugin.json")
    assert marketplace["version"] == EXPECTED_VERSION
    assert plugin["version"] == EXPECTED_VERSION
    assert marketplace["authority"] == "canonical"
    assert plugin["authority"] == "canonical"


def test_init_is_skill_only_and_five_role_agents_are_unchanged():
    plugin = load("plugins/pmcro/.pmcro-plugin/plugin.json")
    assert {row["id"] for row in plugin["agents"]} == ROLE_IDS
    skills = {row["id"]: row for row in plugin["skills"]}
    assert "pmcro-init" in skills
    assert skills["pmcro-init"]["registrationState"] == "checked-candidate"
    assert skills["pmcro-init"]["plannerAdmissible"] is False


def test_skill_local_agent_preserves_bootstrap_boundary():
    agent = load("skills/pmcro-init/agents/pmcro-init.json")
    assert agent["topLevelPmcroRole"] is False
    assert agent["initIsCognitivePhase"] is False
    assert agent["canonicalCognition"] == ["ORCHESTRATE", "PLAN", "MAKE", "CHECK", "REFLECT"]
    assert agent["status"] == "checked-candidate"
    assert agent["availableToPlanner"] is False
    assert agent["registrationCycleUseAllowed"] is False
    assert agent["nextCycleUseAllowed"] is False
    assert agent["authority"]["grantsRuntimeAuthority"] is False
    assert agent["authority"]["canRegister"] is False
    assert agent["authority"]["canActivate"] is False
    assert agent["training"]["trainingEligible"] is False


def test_frozen_state_machine_remains_unregistered_training_ineligible_and_five_phase():
    machine = load("skills/pmcro-init/assets/state-machine/init-v0.2.machine.json")
    assert machine["canonicalCognition"] == ["ORCHESTRATE", "PLAN", "MAKE", "CHECK", "REFLECT"]
    assert "EXECUTE" not in machine["canonicalCognition"]
    assert machine["registrationState"] == "UNREGISTERED"
    assert machine["trainingEligible"] is False


def test_check028_provenance_remains_pass_without_promotion_effect():
    report = load(".pmcro/evidence/pmcro-init-check028/check028-report.json")
    assert report["aggregateVerdict"] == "PASS"
    assert report["candidateIntegrity"] == "PASS"
    assert report["baseline"]["candidatePytest"] == "50/50 PASS"
    assert report["independentChecker"]["checks"] == {"total": 21, "pass": 21, "fail": 0}
    assert report["trainingEligible"] is False
    assert report["registrationState"] == "UNREGISTERED"
    assert report["activation"] == "NONE"
    assert report["promotionEffect"].startswith("NONE")


def test_materialization_evidence_is_byte_bound_and_nonpromoting():
    evidence = load(".pmcro/evidence/pmcro-init-materialization.json")
    assert evidence["repositoryBase"] == "981f8130b1cbf259741b1e53974af068fcfee435"
    assert evidence["frozenPackageSha256"] == EXPECTED_FROZEN_ZIP
    assert evidence["versionTransition"] == {
        "from": "0.4.0-candidate",
        "to": EXPECTED_VERSION,
        "rule": "minimal monotonic patch preserving existing candidate prerelease form",
    }
    assert evidence["pluginPlacement"] == {"skills": True, "topLevelAgents": False}
    assert evidence["lifecycle"] == {
        "state": "checked-candidate",
        "admissibleToPlanner": False,
        "registered": False,
        "activated": False,
        "sameCycleUse": False,
    }
    assert evidence["trainingEligible"] is False
    assert len(evidence["contractMappings"]) == 16
    for row in evidence["contractMappings"]:
        assert row["byteIdentical"] is True
        assert sha256(ROOT / row["destination"]) == row["sha256"]


def test_registry_record_is_digest_bound_checked_candidate_only():
    registry = load(".pmcro/registry/index.json")
    record = next(row for row in registry["resources"] if row["resourceId"] == "skill:pmcro-init")
    assert record["resourceKind"] == "skill"
    assert record["sourceRef"] == "skills/pmcro-init"
    assert record["contentDigest"] == tree_digest("pmcro-init")
    assert record["checkerVerdictRef"] == ".pmcro/evidence/pmcro-init-materialization-check.json"
    assert record["state"] == "checked-candidate"
    assert record["admissibleToPlanner"] is False
    assert record["registrationRef"] is None
    assert record["revocationRef"] is None
    assert record["provenancePreserved"] is True
    assert record["physicalDeleteOnRevoke"] is False


def test_agents_projection_is_noncanonical_version_aligned_and_checked_candidate():
    marketplace = load(".pmcro-plugin/marketplace.json")
    plugin = load("plugins/pmcro/.pmcro-plugin/plugin.json")
    projection = load(".agents/plugins/marketplace.json")
    assert projection["projectionOf"] == ".pmcro-plugin/marketplace.json"
    assert projection["canonical"] is False
    assert projection["grantsRuntimeAuthority"] is False
    assert projection["version"] == marketplace["version"]
    assert projection["plugins"][0]["version"] == plugin["version"]
    skills = {row["id"]: row for row in projection["plugins"][0]["skills"]}
    assert skills["pmcro-init"]["registrationState"] == "checked-candidate"
    assert skills["pmcro-init"]["plannerAdmissible"] is False


def test_claude_projection_keeps_init_as_skill_not_role_agent():
    marketplace = load(".claude-plugin/marketplace.json")
    plugin = load("plugins/pmcro/.claude-plugin/plugin.json")
    canonical_plugin = load("plugins/pmcro/.pmcro-plugin/plugin.json")
    assert marketplace["plugins"][0]["version"] == EXPECTED_VERSION
    assert plugin["version"] == canonical_plugin["version"]
    assert (ROOT / ".claude/skills/pmcro-init/SKILL.md").is_file()
    assert (ROOT / "plugins/pmcro/skills/pmcro-init/SKILL.md").is_file()
    assert not (ROOT / ".claude/agents/pmcro-init.md").exists()
    assert not (ROOT / "plugins/pmcro/agents/pmcro-init.md").exists()
    assert {p.stem for p in (ROOT / ".claude/agents").glob("*.md")} == ROLE_IDS


def test_claude_projection_manifest_denies_authority():
    manifest = load(".pmcro/evidence/pmcro-init-claude-projection.json")
    assert manifest["canonical"] is False
    assert manifest["grantsRuntimeAuthority"] is False
    assert set(manifest["projectAgents"]) == ROLE_IDS
    assert "pmcro-init" in manifest["projectSkills"]
