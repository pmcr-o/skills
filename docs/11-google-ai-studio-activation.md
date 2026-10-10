# Google AI Studio activation packets

Google AI Studio is a separate model workspace, so the local repository needs a portable text projection. A single full-context dump is useful as an archive, but it is not the recommended first prompt: context windows, upload limits, and later retrieval all benefit from progressive disclosure.

## Recommended core-first bundle

Generate the six-package handoff with:

```bash
python3 scripts/build_activation_bundle.py \
  --repo . \
  --source-seed ../upload/'Pasted text(3).txt' \
  --commit "$(git rev-parse HEAD)" \
  --out-dir ../ai-studio-bundle
```

Load `thought-transfer-pmcro-00-core.txt` first. It contains the activation contract, PMCR-O rules, flow directions, entrypoint/account boundary, and an exact package index. The receiving model should request later packets by `PACKAGE_ID` instead of receiving the whole repository at once:

| Package | Purpose | Default | Approximate size |
| --- | --- | --- | --- |
| `00-core` | activation and routing contract | load first | small |
| `01-domains` | domain, account, and agent-entrypoint registry | request when needed | medium |
| `02-skills` | installable skills and generic skill-creator template | request for skill work | medium |
| `03-trails` | PMCR-O protocol, append-only trail, validators, and design notes | request for evidence/replay | larger |
| `04-lenses-and-examples` | simulated `I AM` voices and backward/forward examples | request for worked examples | medium |
| `05-source` | exact uploaded source seed | optional, request only when needed | small |

The package headers include source commit, file manifests, hashes, and rough `chars/4` token estimates. Exact token counts vary by model tokenizer. The bundle also contains a machine-readable `manifest.json` for local checking; the six text packets are the model-facing files.

The activation instruction in `00-core` is deliberately bounded:

```text
@orchestrator /pmcro:orchestrate "Ingest the Thought Transfer core packet, preserve its raw seed, identify the minimum required package, and propose the next bounded action." #trail:AI-STUDIO-THOUGHT-TRANSFER-002
```

The first response is an orchestration frame, not an execution claim. It should identify the selected domain, choose backward or forward flow, name the minimum next package, preserve the raw seed if available, and return one unexecuted next seed.

## Full text archive projection

The legacy single-packet builder remains available when a complete text replay is specifically wanted:

```bash
python3 scripts/build_activation_txt.py \
  --repo . \
  --source-seed ../upload/'Pasted text(3).txt' \
  --commit "$(git rev-parse HEAD)" \
  --out ../thought-transfer-pmcro-activation.txt
```

That packet begins with a paste-ready activation instruction, then the PMCR-O contract, domain `I AM` map, file manifest, and every text artifact from the repository. It excludes `.git` binary objects, caches, credentials, and unrelated private Library files. Use it as a replay/archive artifact, not as the first-load context.

For a literal text simulation of the complete ZIP checkpoint, add the archive metadata:

```bash
python3 scripts/build_activation_txt.py \
  --repo . \
  --source-seed ../upload/'Pasted text(3).txt' \
  --commit "$(git rev-parse HEAD)" \
  --artifact-kind simulated-zip-as-text \
  --archive-name thought-transfer-pmcro-session-v5.zip \
  --archive-sha256 '<sha256 from the ZIP check>' \
  --out ../thought-transfer-pmcro-session-v5.simulated-zip.txt
```

That file is not binary ZIP data. It is the model-readable simulation of the ZIP: archive metadata, Git history, manifest hashes, and delimited text entries for every included text file.

## Activation behavior

The receiving model should first acknowledge the core packet using the routing convention above. It should not claim that packages it has not received are loaded. A package request is a bounded next action, not permission to execute the next PMCR-O phase automatically.

## Why text instead of only ZIP

The ZIP is the archival and replay package. The split text bundle is the model-ingestion package: it is inspectable, pasteable, searchable, and independently requestable by package ID. The full simulated ZIP-as-text packet remains useful for audit and replay, but the core-first bundle reduces context pressure. All artifacts are derived from the same Git checkpoint and carry the same PMCR-O boundaries.
