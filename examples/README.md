# Repository examples

These examples are documented teaching artifacts. They are not historical
quotations, live provider traces, or production evidence.

| Example | Purpose | Expected output | Evidence and limits |
| --- | --- | --- | --- |
| `backward-learning-frame.json` | Show a checked trail projected backward into a reusable lesson | A redacted candidate frame | Pattern-valid only |
| `forward-story-frame.json` | Show a checked trail projected forward into an identity-aware product | A bounded product frame | Pattern-valid only |
| `backward-training-candidates.jsonl` | Show redacted backward-flow training candidates | Rows marked `candidate` | Requires separate approval; not automatic training |
| `forward-training-candidates.jsonl` | Show redacted forward-flow candidates | Rows marked `candidate` | Does not prove product quality or user identity |

Inputs are the JSON/JSONL files themselves plus the referenced trail IDs.
Scripts and validators define expected fields; they do not execute external
providers or certify a deployment.
