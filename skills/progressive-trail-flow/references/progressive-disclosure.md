# Progressive disclosure for local models

Keep the controller skill short. Load detail in this order:

1. Read the raw seed, phase, flow, and domain hint.
2. Load one registry entry.
3. Load only the reference file named by that entry.
4. Run the deterministic projection script.
5. Give the checker the generated row, source IDs, and acceptance contract.

Do not paste every domain’s documentation into every context. Smaller local models benefit when the script performs repeatable transformation and the references carry stable rules. Required folders are intentional: `scripts/` executes, `references/` explains, and `assets/` supplies templates or registries.
