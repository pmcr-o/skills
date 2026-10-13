#!/usr/bin/env python3
"""Build a progressive-disclosure text bundle for a separate model workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


TEXT_SUFFIXES = {
    ".gitignore",
    ".json",
    ".jsonl",
    ".md",
    ".cs",
    ".csproj",
    ".fs",
    ".fsproj",
    ".props",
    ".targets",
    ".sln",
    ".py",
    ".ps1",
    ".proto",
    ".txt",
    ".tmpl",
    ".yaml",
    ".yml",
}
EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "dist", "build"}
PACKAGE_VERSION = "0.1.0"


@dataclass(frozen=True)
class PackageSpec:
    package_id: str
    filename: str
    load_order: int
    role: str
    when_to_load: str
    selectors: tuple[str, ...]


PACKAGE_SPECS = (
    PackageSpec(
        "00-core",
        "thought-transfer-pmcro-00-core.txt",
        0,
        "activation contract and router",
        "Always load first; it is sufficient to open an ORCHESTRATE frame.",
        (
            "README.md",
            "SESSION_HANDOFF.md",
            "docs/00-overview.md",
            "docs/11-google-ai-studio-activation.md",
        ),
    ),
    PackageSpec(
        "01-domains",
        "thought-transfer-pmcro-01-domains.txt",
        1,
        "domain, entrypoint, and trail-narrative registry",
        "Load when the request names a domain, account, connector, or entrypoint.",
        (
            ".agents/README.md",
            ".agents/agents/*.json",
            ".pmcro/protocol/**",
            "skills/progressive-trail-flow/assets/domain-registry.json",
            "skills/progressive-trail-flow/references/domain-registry.md",
            "skills/progressive-trail-flow/references/progressive-disclosure.md",
            "docs/08-mcp-and-thought-transfer.md",
            "docs/09-progressive-trail-flow.md",
            "docs/04-local-execution-and-adapters.md",
            "docs/06-git-time-travel-and-trails.md",
            "docs/05-autonomous-ai-company.md",
            "docs/07-skill-marketplace.md",
            "docs/12-catalog-mcp-server-image.md",
            "docs/references.md",
        ),
    ),
    PackageSpec(
        "02-skills",
        "thought-transfer-pmcro-02-skills.txt",
        2,
        "installable declarative skills, generic template, and bundle tooling",
        "Load when the request asks to inspect, create, install, extend, or validate a skill/package.",
        (
            "skills/**",
            "templates/**",
            "scripts/build_activation_bundle.py",
            "scripts/validate_repo.py",
        ),
    ),
    PackageSpec(
        "03-trails",
        "thought-transfer-pmcro-03-trails.txt",
        3,
        "PMCR-O protocol, trail, validators, and design notes",
        "Load when evidence, replay, checker state, implementation details, or tests are needed.",
        (
            ".pmcro/trails/**",
        ),
    ),
    PackageSpec(
        "04-lenses-and-examples",
        "thought-transfer-pmcro-04-lenses-and-examples.txt",
        4,
        "simulated I AM lenses, narratives, examples, and local verification harness",
        "Load when the task needs worked examples, voice simulations, or training projections.",
        (
            "simulations/**",
            "examples/**",
            "docs/01-i-am-simulation.md",
            "scripts/build_activation_txt.py",
            "tests/test_repo.py",
        ),
    ),
    PackageSpec(
        "05-source",
        "thought-transfer-pmcro-05-source.txt",
        5,
        "optional user-provided source seed",
        "Load only when the raw uploaded transcript is needed; do not load by default.",
        (),
    ),
)


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def section(display_path: str, content: str) -> str:
    return "\n".join(
        [
            "=" * 78,
            f"FILE: {display_path}",
            "=" * 78,
            content.rstrip(),
            "",
        ]
    )


def expand_selector(root: Path, selector: str) -> list[Path]:
    if selector.endswith("/**"):
        base = root / selector[:-3]
        if not base.is_dir():
            return []
        return sorted(path for path in base.rglob("*") if path.is_file())
    return sorted(path for path in root.glob(selector) if path.is_file())


def valid_text_path(path: Path) -> bool:
    return path.name == ".gitignore" or path.suffix.lower() in TEXT_SUFFIXES


def collect_files(root: Path, spec: PackageSpec) -> list[tuple[str, str, str]]:
    paths: dict[str, Path] = {}
    for selector in spec.selectors:
        for path in expand_selector(root, selector):
            if any(part in EXCLUDED_PARTS for part in path.parts):
                continue
            if not valid_text_path(path):
                raise ValueError(f"non-text file selected for {spec.package_id}: {path}")
            display = path.relative_to(root).as_posix()
            paths[display] = path
    return [
        (display, read_text(paths[display]), sha256_text(read_text(paths[display])))
        for display in sorted(paths)
    ]


def collect_source(source_seed: Path | None) -> list[tuple[str, str, str]]:
    if source_seed is None:
        return []
    if not source_seed.is_file():
        raise ValueError(f"source seed does not exist: {source_seed}")
    content = read_text(source_seed)
    return [(f"session-input/{source_seed.name}", content, sha256_text(content))]


def git_history(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), "log", "--oneline", "--decorate", "-8"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def package_header(
    spec: PackageSpec,
    commit: str,
    file_records: list[tuple[str, str, str]],
    package_hash: str | None = None,
) -> str:
    chars = sum(len(content) for _, content, _ in file_records)
    lines = [
        "THOUGHT TRANSFER PMCR-O — PROGRESSIVE ACTIVATION PACKAGE",
        "=" * 78,
        f"PACKAGE_VERSION: {PACKAGE_VERSION}",
        f"PACKAGE_ID: {spec.package_id}",
        f"LOAD_ORDER: {spec.load_order}",
        f"PACKAGE_ROLE: {spec.role}",
        f"WHEN_TO_LOAD: {spec.when_to_load}",
        f"SOURCE_COMMIT: {commit}",
        f"FILE_COUNT: {len(file_records)}",
        f"SOURCE_CHARS: {chars}",
        f"ESTIMATED_TOKENS: {(chars + 3) // 4}",
        f"PACKAGE_SHA256: {package_hash or 'verify-after-write'}",
        "BOUNDARY: text-only, no credentials, connector state, or binary Git objects",
        "",
    ]
    if file_records:
        lines.extend(["PACKAGE FILE MANIFEST", ""])
        lines.extend(
            f"{display} | sha256={file_hash} | chars={len(content)}"
            for display, content, file_hash in file_records
        )
        lines.append("")
    return "\n".join(lines)


def core_contract(package_index: list[dict[str, object]]) -> str:
    index_lines = [
        "PACKAGE INDEX",
        "",
        "Load 00-core first. Request later packages by exact PACKAGE_ID; do not infer omitted files.",
        "Approximate tokens are chars/4 and vary by tokenizer.",
        "",
        "PACKAGE_ID | FILE | LOAD_ORDER | PACKAGE_CHARS | APPROX_TOKENS | SHA256 | WHEN",
    ]
    for item in package_index:
        index_lines.append(
            f"{item['package_id']} | {item['filename']} | {item['load_order']} | "
            f"{item['package_chars']} | {item['estimated_tokens']} | {item['sha256']} | "
            f"{item['when_to_load']}"
        )
    index_lines.extend(
        [
            "",
            "The core package hash is intentionally not self-inlined; verify it with sha256sum after writing.",
            "",
            "PASTE-READY ACTIVATION",
            "",
            "You are receiving the core packet for Thought Transfer PMCR-O. Treat it as a bounded project control plane, not as a claim that simulated voices are persons or that MCP transfers consciousness.",
            "",
            '@orchestrator /pmcro:orchestrate "Ingest the Thought Transfer core packet, preserve its raw seed, identify the minimum required package, and propose the next bounded action." #trail:AI-STUDIO-THOUGHT-TRANSFER-002',
            "",
            "Return only:",
            "1. the raw seed preserved verbatim or a clear statement that the source package has not yet been loaded;",
            "2. the selected domain and flow direction (backward or forward);",
            "3. the minimum package(s) required next, named exactly;",
            "4. the smallest bounded plan and acceptance evidence; and",
            "5. one unexecuted next seed.",
            "",
            "Do not execute PLAN, MAKE, CHECK, or REFLECT in the receiving workspace until the orchestrator has opened the local charter. Do not claim Google, MCP, Figma, MAF, Harness, CodeAct, or account access merely because a package describes it.",
            "",
            "PMCR-O OPERATING CONTRACT",
            "",
            "ORCHESTRATE: preserve raw input, identify principal and entrypoint, and establish a local-only charter.",
            "PLAN: choose the minimum role graph and acceptance contract.",
            "MAKE: create only the declared text/design artifact.",
            "CHECK: use a fresh checker context; the maker must not certify its own work.",
            "REFLECT: record the earned constraint and one next seed; never execute that seed automatically.",
            "SESSION HANDOFF: pass only validated package IDs, paths, hashes, commits, evidence, scope, and one unexecuted seed; request missing packages explicitly instead of replaying the full session.",
            "PHASE ROUTE: ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT. The orchestrator owns advancement; a checker finding returns to REFLECT, not to an arbitrary phase.",
            "NEXT-SEED LEVELS: meta repairs the current artifact/phase; meta-meta repairs the skill/workflow; meta-meta-meta repairs the orchestrator, agent surface, or prompt system.",
            "",
            "Each phase may have its own bounded agent surface. The independent checker is a separate producer/checker context, not merely another label for every phase agent.",
            "Multiple accounts are separate entrypoints and principals. An account connection is a capability boundary, not implicit authority to use every account.",
            "If another session builds a catalog MCP image, treat it as a separate entrypoint. Only checked trail IDs, package IDs, source commits, and bounded handoff envelopes may cross. The catalog is read-only by default and cannot self-promote.",
            "",
            "BACKWARD FLOW: checked trail -> domain discovery -> redacted candidate -> independent review -> reusable skill/template.",
            "FORWARD FLOW: checked trail product -> declared identity + intent -> bounded personalization -> quality check -> deliverable.",
            "",
            "MCP is a structured Thought Transfer boundary carrying intent, capability, artifacts, evidence, and handoffs. It does not transfer consciousness or grant implicit authority.",
            "",
            "PACKAGE REQUEST EXAMPLES",
            "",
            "REQUEST_PACKAGE: 01-domains    # account, domain, entrypoint, or connector question",
            "REQUEST_PACKAGE: 02-skills     # skill creation, installation, or extension",
            "REQUEST_PACKAGE: 03-trails     # evidence, replay, tests, or checker details",
            "REQUEST_PACKAGE: 04-lenses-and-examples  # worked I AM or backward/forward examples",
            "REQUEST_PACKAGE: 05-source     # only when the full uploaded seed is needed",
            "",
        ]
    )
    return "\n".join(index_lines)


def build_package(
    root: Path,
    spec: PackageSpec,
    commit: str,
    package_index: list[dict[str, object]],
    source_seed: Path | None,
) -> str:
    records = collect_source(source_seed) if spec.package_id == "05-source" else collect_files(root, spec)
    header = package_header(spec, commit, records)
    if spec.package_id == "00-core":
        body = core_contract(package_index) + "\n\nCORE REFERENCE FILES\n\n"
    elif spec.package_id == "03-trails":
        history = git_history(root)
        body = "GIT HISTORY (TEXT REPLAY)\n\n" + "\n".join(history) + "\n\n"
    elif spec.package_id == "05-source" and not records:
        body = (
            "OPTIONAL SOURCE PACKAGE\n\n"
            "No source seed was supplied for this build. The package remains intentionally empty.\n"
        )
    else:
        body = ""
    return header + body + "".join(section(display, content) for display, content, _ in records)


def build_bundle(root: Path, source_seed: Path | None, commit: str, out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Non-core package sizes are independent of the core manifest, so compute them first.
    preliminary: dict[str, str] = {}
    for spec in PACKAGE_SPECS:
        if spec.package_id == "00-core":
            continue
        preliminary[spec.package_id] = build_package(root, spec, commit, [], source_seed)

    package_index: list[dict[str, object]] = []
    for spec in PACKAGE_SPECS:
        document = preliminary.get(spec.package_id, "")
        records = collect_source(source_seed) if spec.package_id == "05-source" else collect_files(root, spec)
        source_chars = sum(len(content) for _, content, _ in records)
        package_chars: object = len(document) if document else "self"
        estimated_tokens: object = (len(document) + 3) // 4 if document else "self"
        package_hash: object = sha256_text(document) if document else "self-not-inlined"
        package_index.append(
            {
                "package_id": spec.package_id,
                "filename": spec.filename,
                "load_order": spec.load_order,
                "role": spec.role,
                "when_to_load": spec.when_to_load,
                "source_chars": source_chars,
                "package_chars": package_chars,
                "estimated_tokens": estimated_tokens,
                "sha256": package_hash,
            }
        )

    documents: dict[str, str] = {}
    for spec in PACKAGE_SPECS:
        documents[spec.package_id] = build_package(root, spec, commit, package_index, source_seed)

    # Core carries the final hashes of packages 01-05. Its own hash is deliberately external.
    documents["00-core"] = build_package(root, PACKAGE_SPECS[0], commit, package_index, source_seed)

    paths: list[Path] = []
    for spec in PACKAGE_SPECS:
        path = out_dir / spec.filename
        path.write_text(documents[spec.package_id], encoding="utf-8")
        paths.append(path)

    manifest = {
        "bundleVersion": PACKAGE_VERSION,
        "sourceCommit": commit,
        "packages": [
            {
                **item,
                "actualChars": len(documents[item["package_id"]]),
                "actualTokensEstimate": (len(documents[item["package_id"]]) + 3) // 4,
                "actualSha256": sha256_text(documents[item["package_id"]]),
            }
            for item in package_index
        ],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--source-seed", type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    paths = build_bundle(
        args.repo.resolve(),
        args.source_seed.resolve() if args.source_seed else None,
        args.commit,
        args.out_dir.resolve(),
    )
    for path in paths:
        print(f"wrote {path} ({path.stat().st_size} bytes)")
    print(f"wrote {args.out_dir.resolve() / 'manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
