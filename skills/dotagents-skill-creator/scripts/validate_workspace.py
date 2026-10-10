#!/usr/bin/env python3
"""Validate a generated DotAgents workspace and its provider projections."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise AssertionError(message)


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON: {path}: {exc}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    manifest_path = root / "dotagents.manifest.json"
    if not manifest_path.is_file():
        fail("missing dotagents.manifest.json")
    manifest = load(manifest_path)
    if manifest.get("schemaVersion") != 1:
        fail("unsupported manifest schemaVersion")
    if manifest.get("sourceOfTruth") != ".agents/skills":
        fail("sourceOfTruth must be .agents/skills")
    if manifest.get("controlPlaneRoot") != ".pmcro":
        fail("controlPlaneRoot must be .pmcro")
    for control_file in (
        ".pmcro/charter.json",
        ".pmcro/registry.json",
        ".pmcro/governance/README.md",
        ".pmcro/governance/agent-governance-toolkit.json",
        ".pmcro/manifests/README.md",
        ".pmcro/trails/README.md",
        ".pmcro/checkpoints/README.md",
        ".pmcro/seeds/README.md",
    ):
        if not (root / control_file).is_file():
            fail(f"missing control-plane file: {control_file}")
    charter = load(root / ".pmcro/charter.json")
    registry = load(root / ".pmcro/registry.json")
    governance = load(root / ".pmcro/governance/agent-governance-toolkit.json")
    if charter.get("maxDepth") != 1 or charter.get("sideEffects") != "staged-only":
        fail("control-plane charter is not bounded")
    if registry.get("sourceOfTruth") != ".agents/skills":
        fail("control-plane registry points at the wrong source")
    if charter.get("governanceReferences") != ["microsoft.agent-governance-toolkit"]:
        fail("charter is missing the declared governance reference")
    if registry.get("governanceRoot") != ".pmcro/governance":
        fail("control-plane registry points at the wrong governance root")
    if governance.get("kind") != "governance-reference":
        fail("invalid governance reference kind")
    if governance.get("referenceId") != "microsoft.agent-governance-toolkit":
        fail("unexpected governance reference id")
    if "microsoft/agent-governance-toolkit" not in governance.get("source", ""):
        fail("governance reference source is not the official toolkit repository")
    documents = governance.get("documents", {})
    if not documents.get("architecture", "").endswith("/docs/ARCHITECTURE.md"):
        fail("governance reference is missing ARCHITECTURE.md")
    if not documents.get("adrIndex", "").endswith("/docs/adr/index.md"):
        fail("governance reference is missing the ADR index")
    if governance.get("role") != "policy-enforcement-reference":
        fail("governance reference has the wrong role")
    if governance.get("authority", {}).get("grantsRuntimeAuthority") is not False:
        fail("governance reference must not grant runtime authority")
    if governance.get("verification", {}).get("reverifyBeforePromotion") is not True:
        fail("governance reference must be reverified before promotion")
    managed = set(manifest.get("managedPaths", []))
    if any(path.startswith(("/", "\\\\")) or re.match(r"^[A-Za-z]:", path) for path in managed):
        fail("managed paths must be relative")
    components = manifest.get("components", {})
    if not components:
        fail("manifest has no components")
    for component_id, component in components.items():
        skill = component.get("skill")
        plugin = component.get("plugin")
        if not skill or not NAME_RE.fullmatch(skill) or not plugin or not NAME_RE.fullmatch(plugin):
            fail(f"invalid component id: {component_id}")
        base = root / ".agents" / "skills" / skill
        required = ["SKILL.md", "agents", "scripts", "references", "assets", "tests"]
        for name in required:
            if not (base / name).exists():
                fail(f"{skill}: missing {name}")
        for folder in ("agents", "scripts", "references", "assets", "tests"):
            if not any(path.is_file() for path in (base / folder).iterdir()):
                fail(f"{skill}: empty {folder}")
        agent = load(base / "agents" / "agent.json")
        for field in ("id", "providers", "entrypoints", "outputs", "maxDepth"):
            if field not in agent:
                fail(f"{skill}: agent surface missing {field}")
        if agent["maxDepth"] != 1:
            fail(f"{skill}: maxDepth must be 1")
        plugin_file = root / "plugins" / plugin / "plugin.json"
        projection = load(plugin_file)
        if projection.get("sourceOfTruth") not in (".agents/skills", f".agents/skills/{skill}"):
            fail(f"{plugin}: projection points at the wrong source")
        if not any(item.get("name") == skill for item in projection.get("skills", [])):
            fail(f"{plugin}: plugin projection does not list {skill}")
        claude = root / "plugins" / plugin / ".claude-plugin" / "marketplace.json"
        if not claude.is_file():
            fail(f"{plugin}: missing Claude marketplace projection")
        if f".agents/skills/{skill}" not in claude.read_text(encoding="utf-8"):
            fail(f"{plugin}: Claude projection does not reference canonical skill")
        recorded = set(component.get("paths", []))
        if not recorded.issubset(managed):
            fail(f"{component_id}: component paths are not all managed")
        for relative in recorded:
            if not (root / relative).is_file():
                fail(f"managed file missing: {relative}")
        request_path = root / ".agents" / "requests" / "create-skill" / f"{plugin}--{skill}.json"
        request = load(request_path)
        if request.get("requiredInvoker") != "create-skill":
            fail(f"{component_id}: missing create-skill handoff")
        if request.get("target", {}).get("skill") != skill:
            fail(f"{component_id}: create-skill handoff targets the wrong skill")
    if not (root / ".agents/plugins/marketplace.json").is_file():
        fail("missing generic marketplace index")
    print(f"PASS: {len(components)} component(s), provider-neutral agent surfaces, and marketplace projections validated")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
