#!/usr/bin/env python3
"""Build a single text-only activation packet for a model workspace."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path


EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "dist", "build"}
TEXT_SUFFIXES = {
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".txt",
    ".tmpl",
    ".yaml",
    ".yml",
    ".gitignore",
}


def iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".gitignore":
            continue
        yield path


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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


def git_history(repo: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(repo), "log", "--oneline", "--decorate", "-8"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def build_packet(
    repo: Path,
    source_seed: Path | None,
    commit: str,
    artifact_kind: str,
    archive_name: str,
    archive_sha256: str,
) -> str:
    files: list[tuple[str, str, str]] = []
    for path in iter_text_files(repo):
        content = read_text(path)
        files.append((path.relative_to(repo).as_posix(), content, digest(content)))

    if source_seed is not None:
        content = read_text(source_seed)
        files.append(("session-input/" + source_seed.name, content, digest(content)))

    files.sort(key=lambda item: item[0])
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest_lines = [
        f"{display_path} | sha256={file_hash} | chars={len(content)}"
        for display_path, content, file_hash in files
    ]

    activation = """PASTE-READY ACTIVATION

Load this packet as the project context for Thought Transfer PMCR-O. This file is a simulated ZIP-as-text: it represents the archive’s text entries and replay metadata so a model workspace can ingest them without binary ZIP parsing.

Do not claim that the simulated philosopher voices are historical speakers or conscious entities. Treat them as bounded design lenses. Treat the trail as the archive and any training row as a redacted candidate projection that requires an independent checker.

Start by acknowledging the packet with one ORCHESTRATE frame using this exact routing shape:

@orchestrator /pmcro:orchestrate "Ingest the Thought Transfer packet, preserve its raw seed, and propose the minimum bounded next action." #trail:AI-STUDIO-THOUGHT-TRANSFER-001

Then return only: (1) the preserved raw seed, (2) the selected domain(s), (3) the flow direction—backward or forward, (4) the smallest plan, (5) the acceptance evidence, and (6) one unexecuted next seed. Do not invoke external tools, publish, send messages, or claim MCP/Figma/MAF access unless a later user explicitly provides and authorizes that capability.

"""
    contract = """PMCR-O OPERATING CONTRACT

ORCHESTRATE: preserve raw input, identify principal and entrypoint, and establish a local-only charter.
PLAN: choose the minimum role graph and acceptance contract.
MAKE: create only the declared text/design artifact.
CHECK: use a fresh checker context; the maker must not certify its own work.
REFLECT: record the earned constraint and one next seed; do not execute the seed in the same cycle.

BACKWARD FLOW: checked trail -> domain discovery -> redacted candidate -> independent review -> reusable skill/template.
FORWARD FLOW: checked trail product -> declared identity + intent -> bounded personalization -> quality check -> deliverable.

MCP enables structured Thought Transfer across a boundary by carrying intent, capability, artifacts, evidence, and handoffs. It does not transfer consciousness or grant implicit authority.
"""

    history = git_history(repo)
    header = "\n".join(
        [
            "THOUGHT TRANSFER PMCR-O — SIMULATED ZIP-AS-TEXT ACTIVATION PACKET",
            "=" * 78,
            f"PACKET_VERSION: 0.1.0",
            f"ARTIFACT_KIND: {artifact_kind}",
            f"SOURCE_COMMIT: {commit}",
            f"ARCHIVE_NAME: {archive_name}",
            f"ARCHIVE_SHA256: {archive_sha256 or 'not-supplied'}",
            f"GENERATED_UTC: {generated_at}",
            f"FILE_COUNT: {len(files)}",
            "SCOPE: text-only projection of the local repository plus the user-provided seed",
            "BOUNDARY: no credentials, external connector state, or binary Git objects",
            "",
            activation.rstrip(),
            "",
            contract.rstrip(),
            "",
            "DOMAIN I AM SURFACES",
            "",
            "Each domain is a bounded role surface, not a claim of personhood:",
            "- dotnet-skills: production skill layout and compatibility checker",
            "- pmcro: phase, trail, checker, and next-seed contract",
            "- mcp: typed capability bridge with provenance",
            "- maf: workflow and checkpoint adapter",
            "- figma: design surface with explicit account scope",
            "- harness-codeact: bounded action executor with evidence",
            "- marketplace: version, digest, and promotion gate",
            "",
            "FILE MANIFEST",
            "",
            *manifest_lines,
            "",
            "GIT HISTORY (TEXT REPLAY)",
            "",
            *history,
            "",
        ]
    )
    return header + "\n".join(section(path, content) for path, content, _ in files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--source-seed", type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--artifact-kind", default="activation-packet")
    parser.add_argument("--archive-name", default="not-supplied")
    parser.add_argument("--archive-sha256", default="")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    packet = build_packet(
        args.repo.resolve(),
        args.source_seed.resolve() if args.source_seed else None,
        args.commit,
        args.artifact_kind,
        args.archive_name,
        args.archive_sha256,
    )
    args.out.write_text(packet, encoding="utf-8")
    print(f"wrote {args.out} ({len(packet)} characters)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
