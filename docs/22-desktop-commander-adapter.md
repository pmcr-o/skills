# Desktop Commander as a PMCR-O runtime adapter

Desktop Commander supplies mechanics around the PMCR-O graph:

| Connector operation | Default grant | PMCR-O meaning |
| --- | --- | --- |
| list/read/search | read-only | inspect a declared repository or skill catalog |
| process | exact command, finite timeout, capped output | run a named validator or proof |
| write | explicit project path | materialize a planned artifact |
| handoff | typed evidence | return paths, exits, hashes, and next owner |

PowerShell marketplace skills are domain adapters behind this surface. A
generic `sample-child` can inherit the folder and envelope contract, then add
specialized references, scripts, assets, and tests. The child is a staged
candidate until a fresh checker validates it.

The connector does not grant system-root deletion, credentials, arbitrary shell,
publishing, or GitHub push. GitHub repository creation is a separate repository
surface with explicit remote authorization and its own PMCR-O cycle.
