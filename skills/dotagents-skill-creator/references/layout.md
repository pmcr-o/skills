# Generated workspace layout

```text
<root>/
  dotagents.manifest.json
  .pmcro/
    charter.json
    registry.json
    governance/README.md
    governance/agent-governance-toolkit.json
    manifests/README.md
    trails/README.md
    checkpoints/README.md
    seeds/README.md
  .agents/
    catalog/source-marketplace.json       # optional read-only discovery result
    requests/create-skill/<plugin>--<skill>.json
    plugins/marketplace.json
    skills/<skill>/
      SKILL.md
      agents/agent.json
      agents/openai.yaml
      scripts/validate.py
      scripts/README.md
      references/contract.md
      references/README.md
      assets/manifest.json
      assets/README.md
      tests/test_structure.py
  plugins/<plugin>/
    plugin.json
    .claude-plugin/marketplace.json
```

The `.agents/skills/<skill>` directory is the only editable implementation.
The generic marketplace index is usable by a catalog-aware agent. The
`.claude-plugin` file is a provider projection for Claude-style plugin
loaders. ChatGPT/Codex can route through `agents/agent.json` and
`agents/openai.yaml`; Ollama can execute the Python scripts and consume the
same JSON contract without needing a vendor plugin system.

`.pmcro/` is the global control-plane mirror. It records authority, governance
references, and evidence, not executable skill code. The Agent Governance
Toolkit documents are a re-verifiable policy-boundary reference; they do not
grant runtime authority. A loader may combine a global workspace
with a project-local one, but the local charter and explicit grant still win;
directory presence alone never grants runtime access.

The generated child skill is intentionally small. Add domain behavior through
new scripts, references, assets, and tests in the canonical directory, then
rerun validation. Do not create a second skill copy under `plugins/`.
