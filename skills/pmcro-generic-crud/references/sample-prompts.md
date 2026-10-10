# Sample prompts

Use these to start the generic CRUD skill. Keep them short and concrete.

## Prompt 1 — add a domain entity

```text
Model `Customer : EntityBase` and expose Add, Get, List, Update, and Delete through `IUnitOfWork.Repository<Customer>()`. Show only the needed delta.
```

## Prompt 2 — compose another CRUD capability

```text
Add a CRUD-shaped `CustomerAddress` capability by composing a typed repository or adapter. Reuse the generic contract where its invariants fit.
```

## Prompt 3 — keep deletion safe

```text
Simulate a delete request for a marketplace resource. Return a revoke/tombstone plan, not physical deletion, and include checker evidence requirements.
```
