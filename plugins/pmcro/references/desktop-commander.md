# Desktop Commander runtime adapter

Desktop Commander is a transport/runtime adapter, not a PMCR-O phase. Its
catalog entry exposes list/read/search/process/write with explicit path scope.
The generic foundation can specialize through a child skill while preserving
the same envelope, evidence, caps, and checker boundary.

PowerShell marketplace entries can provide implementation mechanics: filesystem
discovery, one-script invocation, auth-status checks, or a domain validator.
The adapter must not turn a catalog listing into authority and must not treat a
process exit code as a verdict unless the checker interprets it.

GitHub creation or push is intentionally separate. It needs a repository
surface, a remote target, explicit authorization, and a fresh checker.
