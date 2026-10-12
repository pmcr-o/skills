#!/usr/bin/env python3
"""Validate a generated DotAgents workspace and its provider projections."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PMCR_O_MARKERS = (
    "I AM THE",
    "I ORCHESTRATE",
    "I PLAN",
    "I MAKE",
    "I CHECK",
    "I REFLECT",
)
OPTIONAL_LAYERS = ("references", "assets", "scripts", "tests")


def fail(message: str) -> None:
    raise AssertionError(message)


def load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON: {path}: {exc}")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()

    manifest_path = root / "dotagents.manifest.json"
    if not manifest_path.is_file():
        fail("missing dotagents.manifest.json")
    manifest = load(manifest_path)
    if manifest.get("schemaVersion") != 2:
        fail("unsupported manifest schemaVersion")
    if manifest.get("sourceOfTruth") != ".agents/skills":
        fail("sourceOfTruth must be .agents/skills")
    if manifest.get("controlPlaneRoot") != ".pmcro":
        fail("controlPlaneRoot must be .pmcro")
    if manifest.get("createAuthority") != "dotagents-skill-creator":
        fail("Skill Creator must be the registered CREATE authority")
    if manifest.get("promotion") != "generated-unchecked":
        fail("generated workspace must remain unchecked before independent CHECK")

    for control_file in (
        ".pmcro/charter.json",
        ".pmcro/registry.json",
        ".pmcro/manifests/README.md",
        ".pmcro/trails/README.md",
        ".pmcro/checkpoints/README.md",
        ".pmcro/seeds/README.md",
    ):
        if not (root / control_file).is_file():
            fail(f"missing control-plane file: {control_file}")

    charter = load(root / ".pmcro/charter.json")
    registry = load(root / ".pmcro/registry.json")
    if charter.get("maxDepth") != 1 or charter.get("sideEffects") != "staged-only":
        fail("control-plane charter is not bounded")
    if registry.get("sourceOfTruth") != ".agents/skills":
        fail("control-plane registry points at the wrong source")
    if registry.get("createAuthority") != "dotagents-skill-creator":
        fail("control-plane registry has the wrong CREATE authority")

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
        if not (base / "SKILL.md").is_file():
            fail(f"{skill}: missing SKILL.md")
        agents_dir = base / "agents"
        if not agents_dir.is_dir():
            fail(f"{skill}: missing agents/")

        agent_markdown_files = sorted(agents_dir.glob("*.md"))
        if not agent_markdown_files:
            fail(f"{skill}: missing PMCR-O agent markdown")
        if not any(all(marker in path.read_text(encoding="utf-8") for marker in PMCR_O_MARKERS) for path in agent_markdown_files):
            fail(f"{skill}: no agent contains the complete PMCR-O identity/cognition markers")

        agent_json = agents_dir / "agent.json"
        if not agent_json.is_file():
            fail(f"{skill}: missing provider-neutral agents/agent.json")
        agent = load(agent_json)
        for field in ("id", "providers", "entrypoints", "outputs", "maxDepth", "optionalLayers"):
            if field not in agent:
                fail(f"{skill}: agent surface missing {field}")
        if agent["maxDepth"] != 1:
            fail(f"{skill}: maxDepth must be 1")
        if agent.get("authority") != "draft-only":
            fail(f"{skill}: generated agent must be draft-only")

        generated_layers = set(component.get("generatedLayers", []))
        unknown_layers = generated_layers.difference(OPTIONAL_LAYERS)
        if unknown_layers:
            fail(f"{skill}: unknown generated layers: {sorted(unknown_layers)}")
        for layer in OPTIONAL_LAYERS:
            layer_path = base / layer
            if layer in generated_layers:
                if not layer_path.is_dir():
                    fail(f"{skill}: declared layer missing: {layer}/")
                if not any(path.is_file() for path in layer_path.iterdir()):
                    fail(f"{skill}: declared layer is empty: {layer}/")
            elif layer_path.exists():
                fail(f"{skill}: optional layer exists but was not declared: {layer}/")

        plugin_file = root / "plugins" / plugin / "plugin.json"
        projection = load(plugin_file)
        if projection.get("sourceOfTruth") not in (".agents/skills", f".agents/skills/{skill}"):
            fail(f"{plugin}: projection points at the wrong source")
        if not any(item.get("name") == skill for item in projection.get("skills", [])):
            fail(f"{plugin}: plugin projection does not list {skill}")
        if projection.get("authority") != "metadata-only-until-checked":
            fail(f"{plugin}: projection authority is too broad")

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
        if request.get("kind") != "skill.create.request":
            fail(f"{component_id}: wrong create request kind")
        if request.get("requiredInvoker") != "dotagents-skill-creator":
            fail(f"{component_id}: create request does not route to Skill Creator")
        if request.get("creatorAuthority") != "dotagents-skill-creator":
            fail(f"{component_id}: CREATE authority mismatch")
        if request.get("target", {}).get("skill") != skill:
            fail(f"{component_id}: create request targets the wrong skill")
        rules = request.get("rules", {})
        if rules.get("requiredCore") != ["SKILL.md", "agents/"]:
            fail(f"{component_id}: wrong required core")
        if rules.get("registrationRequiresIndependentCheck") is not True:
            fail(f"{component_id}: independent CHECK must gate registration")
        if set(rules.get("generatedLayers", [])) != generated_layers:
            fail(f"{component_id}: generated layer record mismatch")
        if "rawSeed" in request:
            if request.get("rawSeedImmutable") is not True:
                fail(f"{component_id}: raw seed is not marked immutable")
            if request.get("rawSeedSha256") != sha256_text(request["rawSeed"]):
                fail(f"{component_id}: raw seed hash mismatch")

    marketplace = root / ".agents" / "plugins" / "marketplace.json"
    if not marketplace.is_file():
        fail("missing generic marketplace index")
    index = load(marketplace)
    if index.get("createAuthority") != "dotagents-skill-creator":
        fail("marketplace index has the wrong CREATE authority")
    if index.get("promotion") != "catalog-only-until-checked":
        fail("marketplace projection must remain unchecked")

    print(f"PASS: {len(components)} component(s), PMCR-O core shape, optional layers, seed provenance, and projections validated")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
