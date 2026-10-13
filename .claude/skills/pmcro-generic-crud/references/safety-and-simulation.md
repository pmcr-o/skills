# CRUD safety and simulation

The local adapter is deliberately simulation-only. It does not edit the
repository, invoke a MAF workflow, call MCP, contact GitHub, or delete a trail.

For a real adapter:

1. require an explicit scope and capability grant;
2. use optimistic concurrency (`expectedVersion`) for updates;
3. make create/update idempotent with a request/operation id;
4. make deletion a reversible revoke/tombstone until retention policy allows
   erasure;
5. emit the same operation id, resource version, output hash, and evidence
   refs to the checker and trail;
6. fail closed on unknown resource, scope mismatch, stale version, missing
   grant, or untrusted input.

The `.NET` console profile is a human projection of this contract. It is not a
test of the production filesystem, service, database, or MAF runtime.
