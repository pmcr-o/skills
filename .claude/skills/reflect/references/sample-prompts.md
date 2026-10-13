# Sample prompts

Use these to start the reflector skill. Keep them short and concrete.

## Prompt 1 — reflect a PASS

```text
After the independent checker PASS, record the earned constraint and emit one unexecuted meta next seed. Do not run that seed.
```

## Prompt 2 — route a LOOP

```text
Reflect this LOOP finding as a repair seed for the smallest responsible role. Preserve the maker output and wait for the next checker verdict.
```

## Prompt 3 — halt safely

```text
Reflect this HALT without promoting artifacts. State the blocking evidence, preserve the trail, and emit the smallest unexecuted repair intent.
```
