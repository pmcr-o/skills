# Friend-run activation

Give a friend the repository or a text activation bundle. Ask them to load
the contract before the raw trail and to keep their provider identity in the
handoff.

From the product-repository root:

```text
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/validate.ps1
python scripts/validate_trail.py --trail .pmcro/trails/example.jsonl
```

The first run is inspect or simulate. A friend may continue routine local
work only when the autonomy grant is active and unexpired. The friend must
start a new checker context for a verdict. They must stop on credentials,
external writes, deletion, publishing, a scope change, or repeated failure.

For token-limited hosts, send metadata and contract first, then request the
evidence or asset packet by exact path. Never paste credentials into a trail
or activation packet.
