#!/usr/bin/env python3
"""Deterministically project canonical PMCR-O marketplace state to .agents compatibility."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def safe_source(repo: Path, relative: str) -> Path:
    target = (repo / relative).resolve()
    root = repo.resolve()
    if target != root and root not in target.parents:
        raise ValueError(f"source escapes repository: {relative}")
    return target


def first_agent(repo: Path, skill_ref: str) -> tuple[str | None, dict]:
    base = safe_source(repo, skill_ref) / "agents"
    files = sorted(base.glob("*.json")) if base.is_dir() else []
    if not files:
        return None, {}
    path = files[0]
    return path.relative_to(repo).as_posix(), load_json(path)


def project(repo: Path) -> dict:
    marketplace_ref = ".pmcro-plugin/marketplace.json"
    marketplace = load_json(repo / marketplace_ref)
    if marketplace.get("authority") != "canonical":
        raise ValueError("canonical marketplace authority required")
    if marketplace.get("projectionPolicy", {}).get("providerSurfacesAreCanonical") is not False:
        raise ValueError("provider projections cannot be canonical")

    projected_plugins = []
    for plugin_entry in marketplace.get("plugins", []):
        plugin_ref = plugin_entry["manifest"]
        plugin = load_json(repo / plugin_ref)
        if plugin.get("authority") != "canonical":
            raise ValueError(f"canonical plugin authority required: {plugin_ref}")
        skills = []
        for skill in plugin.get("skills", []):
            source_ref = skill["sourceRef"]
            agent_ref, agent = first_agent(repo, source_ref)
            entry = {
                "id": skill["id"],
                "path": source_ref,
                "agent": agent_ref,
                "entrypoint": agent.get("entrypoint") or ((agent.get("entrypoints") or [None])[0]),
                "input": list(agent.get("inputs") or []),
                "output": list(agent.get("outputs") or []),
                "accept": list(agent.get("accept") or []),
                "deny": list(agent.get("deny") or agent.get("refusals") or []),
            }
            for field in ("registryRef", "registrationState", "plannerAdmissible", "firstUsePolicy"):
                if field in skill:
                    entry[field] = skill[field]
            skills.append(entry)
        projected_plugins.append({
            "id": plugin["id"],
            "displayName": plugin.get("displayName", plugin["name"]),
            "version": plugin["version"],
            "manifest": plugin_ref,
            "promotion": plugin.get("promotion"),
            "skills": skills,
        })

    return {
        "apiVersion": "pmcro.agents-projection/v1",
        "marketplaceId": marketplace["id"],
        "version": marketplace["version"],
        "sourceOfTruth": [marketplace_ref] + [p["manifest"] for p in marketplace.get("plugins", [])] + ["skills/"],
        "plugins": projected_plugins,
        "projectionOf": marketplace_ref,
        "canonical": False,
        "grantsRuntimeAuthority": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    out = args.out.resolve() if args.out else repo / ".agents/plugins/marketplace.json"
    payload = project(repo)
    write_json(out, payload)
    print(json.dumps({"projection": out.as_posix(), "version": payload["version"], "skills": sum(len(p["skills"]) for p in payload["plugins"]), "canonical": False, "grantsRuntimeAuthority": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
