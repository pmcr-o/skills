# PMCR-O agent product repository template

This is a provider-neutral product repository starter. A Codex, Claude,
Ollama, MAF, MCP, Harness, or CodeAct adapter may operate it only through the
declared grant and the same generic PMCR-O trail.

## Friend-run sequence

1. Copy this template into a new local repository.
2. Replace the product and principal placeholders.
3. Review `autonomy-grant.example.json`; keep routine work scoped and finite.
4. Start in inspect or simulate mode.
5. Run the validators and hand the artifact to a separate checker.
6. Stage or publish only after the checker and policy gate pass.

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
python scripts/validate_trail.py --trail .pmcro/trails/example.jsonl
```

`autoApprove` in the example means “continue inside this existing grant”; it
does not mean unrestricted autonomy. Credentials, deletion, external writes,
publishing, and scope changes require a new grant and checker cycle.
