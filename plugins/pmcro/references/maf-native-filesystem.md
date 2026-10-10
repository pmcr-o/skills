# MAF Native and filesystem skills

MAF Native supplies the runtime family; it does not erase PMCR-O boundaries.
Use `maf-workflows` to build the custom role graph with checkpoints and use
`maf-mcp-tools` to connect allowlisted MCP tools as separate processes. The
orchestrator remains a coordinator, not a bag of unrestricted tools.

The filesystem skill is the layout-aware adapter. Its default operation is a
relative, read-only discovery pass over:

- `.agents/agents/` and `.agents/plugins/` for declarative surfaces/catalogs;
- `.pmcro/protocol/` and `.pmcro/trails/` for contracts and append-only evidence;
- `.claude/`, `.codex/`, `.gemini/`, or other provider projections;
- the project source tree and its manifests.

Discovery returns paths, file kinds, hashes, declared scopes, and references.
It does not infer that a dot-folder is global, import credentials, execute a
script, write a file, or promote a marketplace child. Write, command, MCP, and
deployment operations require separate capabilities in the grant.

For a MAF-backed service, the surface can therefore simulate this sequence:

`discover layout -> resolve catalog -> activate dependency -> checkpoint -> check`

The local API script in `skills/pmcro-agent-surface/scripts/` simulates only
the typed surface response. It does not start a .NET process, call an MCP
server, or assert that `ProjectName.OrchestrationService` exists.
