#!/usr/bin/env python3
"""Deterministically project the canonical PMCR-O marketplace into provider-native surfaces."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

CLAUDE_MARKETPLACE_SCHEMA = "https://anthropic.com/claude-code/marketplace.schema.json"
ROLE_IDS = (
    "pmcro-orchestrator",
    "pmcro-planner",
    "pmcro-maker",
    "pmcro-checker",
    "pmcro-reflector",
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def safe_source(repo: Path, relative: str) -> Path:
    source = (repo / relative).resolve()
    root = repo.resolve()
    if source != root and root not in source.parents:
        raise ValueError(f"source escapes repository: {relative}")
    return source


def render_agent(agent_id: str, source_ref: str, contract: dict) -> str:
    description = contract.get("displayName") or contract.get("description") or f"PMCR-O {agent_id} role"
    return (
        "---\n"
        f"name: {agent_id}\n"
        f"description: {json.dumps(str(description), ensure_ascii=False)}\n"
        "---\n\n"
        "# GENERATED PROJECTION — NOT CANONICAL AUTHORITY\n\n"
        f"Canonical PMCR-O contract: `{source_ref}`.\n\n"
        "This Claude Code surface is generated from the canonical PMCR-O agent contract. "
        "It grants no additional capability, transport, model, or execution authority. "
        "Preserve ORCHESTRATE → PLAN → MAKE → CHECK → REFLECT and route missing capability through the canonical registry.\n"
    )


def copy_skill(source: Path, destination: Path) -> int:
    if not (source / "SKILL.md").is_file():
        raise ValueError(f"skill source lacks SKILL.md: {source}")
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".pytest_cache", ".mypy_cache", ".ruff_cache"),
    )
    return sum(1 for path in destination.rglob("*") if path.is_file())


def project_claude(repo: Path, out: Path) -> dict:
    marketplace_ref = ".pmcro-plugin/marketplace.json"
    marketplace = load_json(repo / marketplace_ref)
    if marketplace.get("authority") != "canonical":
        raise ValueError("marketplace must declare authority=canonical")
    if marketplace.get("projectionPolicy", {}).get("providerSurfacesAreCanonical") is not False:
        raise ValueError("provider projections must be non-canonical")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    claude_marketplace = {
        "$schema": CLAUDE_MARKETPLACE_SCHEMA,
        "name": marketplace["name"],
        "description": marketplace["description"],
        "owner": {"name": "PMCR-O"},
        "plugins": [],
    }
    projection_manifest = {
        "apiVersion": "pmcro.projection-result/v1",
        "provider": "claude-code",
        "canonicalMarketplaceRef": marketplace_ref,
        "canonical": False,
        "grantsRuntimeAuthority": False,
        "plugins": [],
        "projectAgents": [],
        "projectSkills": [],
        "generatedFileCount": 0,
    }

    project_agent_root = out / ".claude" / "agents"
    project_skill_root = out / ".claude" / "skills"
    project_agent_root.mkdir(parents=True, exist_ok=True)
    project_skill_root.mkdir(parents=True, exist_ok=True)
    (out / "CLAUDE.md").write_text(
        "# GENERATED PMCR-O CLAUDE PROJECTION\n\n"
        "Canonical authority remains in `.pmcro/`, `.pmcro-plugin/`, and portable `skills/`.\n"
        "Provider files are generated projections and MUST NOT widen PMCR-O grants.\n",
        encoding="utf-8",
    )

    projected_project_skills: set[str] = set()
    projected_project_agents: set[str] = set()

    for plugin_entry in marketplace["plugins"]:
        plugin_manifest_ref = plugin_entry["manifest"]
        plugin = load_json(repo / plugin_manifest_ref)
        if plugin.get("authority") != "canonical":
            raise ValueError(f"plugin must be canonical: {plugin_manifest_ref}")
        plugin_id = plugin["id"]
        plugin_out = out / "plugins" / plugin_id
        plugin_out.mkdir(parents=True, exist_ok=True)

        claude_marketplace["plugins"].append(
            {
                "name": plugin["name"],
                "description": plugin["description"],
                "version": plugin["version"],
                "source": f"./plugins/{plugin_id}",
                "category": plugin_entry.get("category", "development"),
            }
        )
        write_json(
            plugin_out / ".claude-plugin" / "plugin.json",
            {
                "name": plugin["name"],
                "version": plugin["version"],
                "description": plugin["description"],
                "author": {"name": "PMCR-O"},
            },
        )

        plugin_agent_root = plugin_out / "agents"
        plugin_agent_root.mkdir(parents=True, exist_ok=True)
        for agent in plugin.get("agents", []):
            source_ref = agent["sourceRef"]
            contract = load_json(safe_source(repo, source_ref))
            agent_id = agent["id"]
            rendered = render_agent(agent_id, source_ref, contract)
            (plugin_agent_root / f"{agent_id}.md").write_text(rendered, encoding="utf-8")
            if agent_id not in projected_project_agents:
                (project_agent_root / f"{agent_id}.md").write_text(rendered, encoding="utf-8")
                projected_project_agents.add(agent_id)

        plugin_skill_root = plugin_out / "skills"
        plugin_skill_root.mkdir(parents=True, exist_ok=True)
        for skill in plugin.get("skills", []):
            skill_id = skill["id"]
            source = safe_source(repo, skill["sourceRef"])
            copy_skill(source, plugin_skill_root / skill_id)
            if skill_id not in projected_project_skills:
                copy_skill(source, project_skill_root / skill_id)
                projected_project_skills.add(skill_id)

        projection_manifest["plugins"].append(
            {
                "id": plugin_id,
                "canonicalManifestRef": plugin_manifest_ref,
                "providerManifestRef": f"plugins/{plugin_id}/.claude-plugin/plugin.json",
            }
        )

    write_json(out / ".claude-plugin" / "marketplace.json", claude_marketplace)
    projection_manifest["projectAgents"] = sorted(projected_project_agents)
    projection_manifest["projectSkills"] = sorted(projected_project_skills)
    projection_manifest["generatedFileCount"] = sum(1 for path in out.rglob("*") if path.is_file()) + 1
    write_json(out / "projection-manifest.json", projection_manifest)
    return projection_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--provider", choices=["claude"], default="claude")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    manifest = project_claude(args.repo.resolve(), args.out.resolve())
    print(json.dumps(manifest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
