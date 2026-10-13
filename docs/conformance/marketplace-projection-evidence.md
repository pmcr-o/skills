# Marketplace projection conformance evidence

Status: checked-local

## Scope

This evidence covers the candidate canonical marketplace/plugin authority files, Claude projection compiler, compatibility projection references, role-specific training-candidate metadata, and the existing PMCR-O repository regression suite.

## Runtime

- Authorized device: `PMCRO_Company`
- Branch: `pmcro/skill-creator-bootstrap-reconcile`
- Synced remote head before this slice: `aaec6c16180823ef3cac5ce20aed057366603826`
- Python used for deterministic validation: Python 3.12 via `py -3.12`

## Results

- Root repository tests: **51 passed**.
- Skill Creator tests: **5 passed**.
- CAPABILITY_IMPORT route tests: **3 passed**.
- CAPABILITY_IMPORT importer tests: **3 passed**.
- Repository structural validator: **PASS** (`148 required files, 12 agent surfaces, 222 trail events`).
- JSON parse validation: **PASS** (`79` JSON files across canonical/control/provider compatibility roots).
- Claude marketplace projection tests: **4 passed**, including deterministic regeneration, five-role agent projection, portable skill projection, provider non-authority, and candidate training-data non-eligibility.

## Important boundaries

Generation success is not marketplace promotion. The canonical marketplace and plugin remain `0.4.0-candidate` / `candidate-unregistered` until an independent promotion Cycle explicitly registers them.

No Ollama model was trained, pulled, bound as active, or activated. Training candidate descriptors remain `trainingEligible=false`, `explicitOptIn=false`, and `trainingAuthorityGranted=false`.

`skills/dotagents-skill-creator/scripts/validate_workspace.py` validates a generated Skill Creator workspace with `dotagents.manifest.json`; the repository root is not such a workspace, so it is not a repository-root conformance gate. Skill Creator behavior is instead covered by its deterministic test suite above.
