from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def current_tokens(root: Path) -> set[str]:
    tokens: set[str] = set()
    skills = root / "skills"
    if skills.is_dir():
        for p in skills.iterdir():
            if p.is_dir():
                tokens.update(part for part in p.name.lower().split("-") if part)
                tokens.add(p.name.lower())
    plugin = root / "plugins" / "pmcro" / ".pmcro-plugin" / "plugin.json"
    if plugin.is_file():
        data = load_json(plugin)
        for row in data.get("skills", []):
            sid = str(row.get("id", "")).lower()
            tokens.add(sid)
            tokens.update(part for part in sid.split("-") if part)
    return tokens


def classify_agent(agent_id: str, tokens: set[str]) -> tuple[str, str]:
    base = agent_id.lower().removesuffix("-agent")
    if base in {"pmcro", "skill-creator", "desktop-commander", "maf", "dotagents"}:
        return "MERGE", "overlaps an existing canonical PMCR-O capability/system surface"
    if base in tokens or agent_id.lower() in tokens:
        return "MERGE", "domain token already appears in the checked C: marketplace"
    return "ADOPT", "candidate domain system not presently represented as a full canonical C: agent project"


def inspect_agent(a_root: Path, row: dict, tokens: set[str]) -> dict:
    agent_id = row["id"]
    local = a_root / agent_id
    classification, reason = classify_agent(agent_id, tokens)
    skill_files = list(local.rglob("SKILL.md")) if local.is_dir() else []
    return {
        "id": agent_id,
        "catalogStatus": row.get("status"),
        "role": row.get("role"),
        "declaredSkills": row.get("skills"),
        "repository": row.get("repository"),
        "localPath": str(local),
        "exists": local.is_dir(),
        "surfaces": {
            "pmcro": (local / ".pmcro").is_dir(),
            "agents": (local / ".agents").is_dir(),
            "claude": (local / ".claude").exists(),
            "claudePlugin": (local / ".claude-plugin").exists(),
            "github": (local / ".github").exists(),
            "agentsMd": (local / "AGENTS.md").is_file(),
        },
        "observedSkillFiles": len(skill_files),
        "classification": classification,
        "reason": reason,
    }


def concept_rows() -> list[dict]:
    return [
        {"id": "pmcro-canonical-authority", "classification": "ADOPT", "evidence": "A:/marketplace README/catalog declare .pmcro canonical; matches checked C: law."},
        {"id": "provider-projections", "classification": "ADOPT", "evidence": "A: host -> .agents -> .pmcro projection chain matches provider-projection law."},
        {"id": "generated-domain-agent-projects", "classification": "MERGE", "evidence": "A: eng/src and refresh/build tooling provide a mature generator model to reconcile with C: projection compiler."},
        {"id": "agent-registry-and-filesystem-queues", "classification": "MERGE", "evidence": "A: agent-registry.json binds local paths and filesystem-spool-v1 queues; richer than current C: registry."},
        {"id": "pinned-upstream-source", "classification": "ADOPT", "evidence": "A: eng/upstream uses pinned vendor source plus lock digest; compatible with provenance law."},
        {"id": "independent-marketplace-validation", "classification": "ADOPT", "evidence": "A: eng/validate-agent-repos.py is explicitly independent whole-marketplace validation."},
        {"id": "mandatory-all-skill-folders", "classification": "SUPERSEDE", "evidence": "A: eng/README requires scripts/references/assets/tests for every owned skill; current C: law requires only SKILL.md + agents/ and optional progressive layers."},
        {"id": "automatic-post-reflect-cycle", "classification": "SUPERSEDE", "evidence": "A: agent contracts automatically admit REFLECT next seed; checked C: next-seed law keeps it unexecuted until a fresh admitted Cycle."},
        {"id": "recursive-phase-cycles", "classification": "DEFER", "evidence": "A: contracts allow recursive lifecycle inside every bounded phase; current law only clearly admits explicit child delegation as a child Cycle."},
        {"id": "i-context-accountability-frame", "classification": "DEFER", "evidence": "A: pmcro.i-context/v1 appears useful but has no checked equivalent in current C: contracts yet."},
        {"id": "cross-agent-local-trails", "classification": "MERGE", "evidence": "A: each I owns a local trail and cross-I handoffs reference source trails; reconcile with current trail/evidence graph."},
        {"id": "transport-model-not-authority", "classification": "ADOPT", "evidence": "A: explicitly states transport/model identity never grants authority; matches checked C: law."},
        {"id": "maker-no-self-certification", "classification": "ADOPT", "evidence": "A: Maker output remains evidence until independent CHECK; matches current C: law."},
        {"id": "eng-history", "classification": "REFERENCE", "evidence": "A: eng/history is declared superseded provenance and must not drive new builds."},
    ]


def render_md(data: dict) -> str:
    lines = [
        "# A:\\marketplace reconciliation map",
        "",
        "This artifact is generated from read-only inspection of `A:\\marketplace` and comparison against the checked C: PMCR-O contracts. It does not authorize mutation of A:.",
        "",
        f"Source catalog schema: `{data['source']['catalogSchema']}`  ",
        f"Canonical agents observed: **{len(data['agents'])}**  ",
        f"Legacy marketplaces observed: **{len(data['legacy'])}**",
        "",
        "## Classification law",
        "",
        "`ADOPT` = aligned pattern worth importing subject to normal CHECK. `MERGE` = overlaps current canonical work and needs reconciliation. `SUPERSEDE` = conflicts with checked law. `REFERENCE` = provenance/evidence only. `DEFER` = potentially useful but insufficiently reconciled.",
        "",
        "## Agent projects",
        "",
        "| Agent | Role | Declared skills | Observed SKILL.md | Classification |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in data["agents"]:
        lines.append(f"| `{row['id']}` | {row.get('role') or ''} | {row.get('declaredSkills') or 0} | {row['observedSkillFiles']} | **{row['classification']}** |")
    lines += ["", "## Legacy marketplace trees", ""]
    for row in data["legacy"]:
        lines.append(f"- `{row['id']}` — **REFERENCE**: {row.get('status', 'legacy')}.")
    lines += ["", "## Architectural concepts", ""]
    for row in data["concepts"]:
        lines.append(f"- **{row['classification']}** `{row['id']}` — {row['evidence']}")
    lines += [
        "",
        "## Mutation boundary",
        "",
        "No A: file, repository state, registry entry, queue, generated project, or trail is changed by this reconciliation map. Future migration must consume this map as source evidence and run CREATE/CHECK/REGISTER in the canonical workspace before later use.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=r"A:\marketplace")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--json-out", default="docs/reconciliation/a-marketplace-reconciliation.json")
    ap.add_argument("--md-out", default="docs/reconciliation/a-marketplace-reconciliation.md")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    source = Path(args.source)
    catalog = load_json(source / "catalog.json")
    tokens = current_tokens(root)
    agents = [inspect_agent(source, row, tokens) for row in catalog.get("agents", [])]
    legacy = [dict(row, classification="REFERENCE") for row in catalog.get("legacy", [])]
    data = {
        "schema": "pmcro.reconciliation/v1",
        "source": {
            "path": str(source),
            "mode": "read-only",
            "catalogSchema": catalog.get("schema"),
            "canonicalAuthority": catalog.get("canonicalAuthority"),
            "projection": catalog.get("projection"),
            "hostChain": catalog.get("hostChain"),
        },
        "target": {"path": str(root), "authority": "checked-canonical-comparison"},
        "allowedClassifications": ["ADOPT", "MERGE", "SUPERSEDE", "REFERENCE", "DEFER"],
        "agents": agents,
        "legacy": legacy,
        "concepts": concept_rows(),
        "mutation": {"sourceMutationAllowed": False, "registrationAllowed": False, "promotionAllowed": False},
    }
    json_path = root / args.json_out
    md_path = root / args.md_out
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_md(data), encoding="utf-8")
    print(f"WROTE {json_path}")
    print(f"WROTE {md_path}")
    print(f"AGENTS={len(agents)} LEGACY={len(legacy)} CONCEPTS={len(data['concepts'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
