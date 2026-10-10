# Example artifact documentation convention

Examples are part of the product surface. A local model, checker, or future
skill generator must be able to understand an example without guessing what
it proves.

Every file under `assets/`, `examples/`, or `tests/fixtures/` must have nearby
documentation with four minimum sections:

1. **Purpose** — what pattern the example teaches.
2. **Inputs** — the request, fixture, or assumptions it consumes.
3. **Expected output** — the observable result and important fields.
4. **Evidence and limits** — evidence tier, simulation status, and what was not
   executed or verified.

The documentation may be a directory `README.md`, a linked reference, or
inline XML/doc comments for a small code example plus a directory README. The
checker should reject an undocumented example rather than infer semantics
from filenames.

This convention applies equally to JSON schemas, C# assets, MAF workflow
fixtures, MCP tool examples, CodeAct plans, and generated console output.
Documentation makes the artifact teachable; it does not make a simulation a
runtime proof.
