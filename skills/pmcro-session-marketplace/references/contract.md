# Session-to-marketplace contract

## Artifact graph

```text
ingestId
├── source/source-manifest.json
├── source/redacted-session.txt
├── source/session.txt                 # only with explicit include-raw
├── pmcro/frames.jsonl
├── marketplace/skill-candidate.json
├── training/candidates.jsonl
└── reports/architecture-assessment.md
```

The source file is immutable input. The other paths are derived children and
must carry `ingestId`, source hash, scope, evidence tier, and promotion state.

## Claim tiers

| Tier | Meaning | Allowed use |
| --- | --- | --- |
| `verified` | Direct local evidence was rerun by the checker | acceptance evidence |
| `candidate` | Reusable pattern extracted from a checked transformation | staged skill/training input |
| `simulation` | Designed or simulated domain behavior | labeled example only |
| `unknown` | Mentioned or claimed without accessible evidence | roadmap/blocker only |
| `blocked` | Attempt could not proceed under its charter | reflection and repair seed |

The uploaded session says W: was offline in part of the trail and later reports
results from a disconnected implementation. This constructor may preserve the
claim as `unknown`, but it must not upgrade it to `verified` merely because the
sentence says “verified,” “passed,” or “implemented.”

## Input/output/accept/deny

The package manifest must expose:

```json
{
  "input": {"sourceRef": "...", "consent": "user-authorized", "scope": "..."},
  "output": {"artifacts": ["..."], "evidenceTier": "candidate"},
  "accept": ["..."],
  "deny": ["..."],
  "simulationPolicy": {"simulation": true, "verified": false}
}
```

These are declarative decisions, not hidden permissions. The checker can
accept the package transformation while denying live W: access, provider
claims, automatic model training, or promotion.

## Recursive seeds

The reflector's seed is raw input for the next cycle. A next cycle may produce
another seed, but the depth/call cap is inherited and a new checker is
required. A seed may be `meta` (artifact), `meta2` (skill/workflow), or `meta3`
(orchestrator/agent/prompt system). It never authorizes its own execution.
