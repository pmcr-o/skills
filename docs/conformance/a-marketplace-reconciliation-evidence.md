# A:\marketplace reconciliation evidence

Status: PASS for read-only discovery and deterministic reconciliation-map generation.

Source boundary: `A:\marketplace` was inspected read-only. No source mutation, registration, promotion, cleanup, queue writes, or trail writes were authorized.

Observed source system:

- 25 cataloged canonical agent projects.
- 6 legacy marketplace trees marked `migration-evidence`.
- All 25 agent projects expose `.pmcro`, `.agents`, `.claude`, `.claude-plugin`, `.github`, and `AGENTS.md` surfaces.
- 25/25 registered filesystem-spool queues exist.
- `eng/src` contains 23 durable source domains plus a pinned `eng/upstream/dotnet-skills` mirror and lock file.
- Release roots include `pmcro-agent`, `csuite-agent`, and marketplace releases.
- Recursive projection discovery found 1,902 `SKILL.md` files against 222 catalog-declared skills, confirming that provider/generated copies must not be treated as independent canonical skills.

Reconciliation decisions are generated into `docs/reconciliation/a-marketplace-reconciliation.json` and `.md` using `scripts/reconcile_a_marketplace.py`. Aligned architecture is classified ADOPT, overlapping canonical work MERGE, conflicting legacy law SUPERSEDE, historical material REFERENCE, and unresolved concepts DEFER.

Validation evidence:

- focused reconciliation tests: 7 PASS
- repository tests: 68 PASS
- Skill Creator tests: 5 PASS
- capability-import routing tests: 3 PASS
- capability-import tests: 3 PASS
- structural validator: PASS (`148 required files, 12 agent surfaces, 222 trail events`)
- JSON parse: PASS (`105` JSON files)
- deterministic reconciliation regeneration: PASS
- `git diff --check`: PASS
- A: source status entries before: 46,578
- A: source status entries after: 46,578
- exact A: status comparison: unchanged

This evidence does not promote or import any A: artifact. A later Cycle must perform bounded CREATE/CHECK/REGISTER work for selected ADOPT or MERGE candidates.
