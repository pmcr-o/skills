# CAPABILITY_IMPORT conformance evidence

This directory records bounded import evidence; it is not an execution registry.

`aspire-agent-mcp.discovery.json` is a static, pinned snapshot derived from `pmcr-o/aspire-agent` at commit `95cda7cca4fa2c47f66331bcbe4c07d44d8c1502`. The source project declares an Aspire MCP server and a local launch wrapper, but this conformance run did **not** start the server or call MCP discovery/runtime methods. Therefore `tools`, `resources`, `resourceTemplates`, and `prompts` are intentionally empty rather than inferred.

`aspire-agent-mcp.capability-import.json` is the deterministic normalized candidate. It remains `generated-unchecked`, contains no secret material, and grants no execution authority.

`aspire-agent-mcp.skill-create.request.json` demonstrates the subsequent Skill Creator handoff. It does not mean the imported Aspire skill has been created, checked, promoted, or registered.
