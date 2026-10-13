# PMCR-O Known Limitations and Design Boundaries

PMCR-O intentionally separates availability, authority, evidence, and lifecycle state.

PMCR-O does not imply any of the following:

- host capability equals PMCR-O authority;
- model availability equals capability grant;
- generated artifact equals checked artifact;
- registered transport equals execution permission;
- invocation success equals task completion;
- simulation equals runtime evidence;
- Trail, Cycle, Frame, or Evidence data equals training data;
- provider projection equals canonical definition;
- planner output automatically invokes a Maker;
- Maker output automatically invokes a Checker;
- Checker verdict automatically invokes a Reflector;
- REFLECT output automatically executes a future seed;
- a child agent inherits every parent permission;
- a product orchestrator inherits subsystem permissions;
- a script's existence authorizes unrestricted command execution;
- an imported MCP/OpenAPI/gRPC/A2A capability is trusted or executable merely because discovery succeeded;
- a trained model is registered, bound, or production-ready;
- GitHub or any source-control host is required to define PMCR-O authority.

## Current maturity boundaries

Provider projections can lag canonical contracts until checked projection compilers exist. Local and remote execution environments may be unavailable independently of repository state. A branch can contain candidate contracts that are not registered or promoted.

Role-specific Ollama bindings are candidate projections until a separately governed training/evaluation lifecycle produces checked model versions. No role model should be treated as existing solely because a target model name is declared.

Training-data profiles define eligibility and routing only. They do not collect private data automatically and do not authorize model training.
