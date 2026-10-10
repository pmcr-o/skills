# Source repository intake

An external Clean Architecture repository is an optional teaching source, not
an authority grant. Before reuse, require:

- canonical repository URL;
- exact commit or immutable ref;
- license and allowed use;
- requested subpaths;
- source hash and discovery catalog;
- checker evidence for the mapped layers and tests.

Without those fields, use the local declarative baseline and emit an
unexecuted next seed requesting the missing source reference. Never infer a
repository from a vague name, copy a branch as executable authority, or merge
source files into an existing project without a staged child boundary.
