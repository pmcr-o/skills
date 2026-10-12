---
name: pmcro-capability-import
description: Normalize external capability descriptions into the provider-neutral CAPABILITY_IMPORT intermediate representation, beginning with MCP tools, resources, prompts, schemas, effects, provenance, and transport metadata, then hand the checked candidate to Skill Creator without granting execution authority.
---

# PMCR-O capability import

Use this skill when functionality already exists behind a machine-readable agent or service protocol and should become a portable marketplace skill without a bespoke hand-written wrapper.

`CAPABILITY != TRANSPORT`. Importers preserve native protocol metadata while producing one provider-neutral intermediate representation. The first importer consumes an MCP discovery snapshot; later importers may target OpenAPI, gRPC, A2A, functions, or other sources while producing the same CAPABILITY_IMPORT contract.

## MCP mapping

- MCP tools become candidate executable capability contracts. Import does not grant authority to invoke them.
- MCP resources and resource templates become non-executable resource/reference contracts.
- MCP prompts become inert prompt-template contracts. A registered MCP runtime must still retrieve/render them when needed.
- Tool input/output schemas and prompt argument schemas become typed schema records referenced by the normalized contracts.
- MCP tool annotations are preserved as evidence. Effect classification uses explicit annotations only; the importer must not infer destructive/read semantics from tool names.
- MCP connection data becomes a transport binding containing references only. Do not copy tokens, headers, environment secrets, passwords, or credential values into the import manifest.

## Lifecycle

`DISCOVER SNAPSHOT -> NORMALIZE CAPABILITY_IMPORT -> ROUTE TO SKILL CREATOR -> CREATE CANDIDATE -> INDEPENDENT CHECK -> PROMOTE/REGISTER -> LATER USE`

The normalized import is always `generated-unchecked`. Discovery success is not runtime proof, imported code is not trusted code, and an available MCP transport is not authorization to execute any tool.

Skill Creator remains the registered CREATE authority. This skill compiles protocol metadata into Skill Creator input; it does not create or self-promote marketplace skills by itself.

## Canonical contract

The portable IR schema is `.pmcro/protocol/capability-import.schema.json`.

Required logical sections are:

- `source`: native source type, immutable source reference, native identity/version.
- `transport`: protocol/binding plus endpoint/command/auth references with `secretMaterialIncluded=false`.
- `tools`: normalized capability IDs, native names, schema references, effect classification, and `executionAuthorityGranted=false`.
- `resources`: normalized non-executable resource or resource-template records.
- `prompts`: normalized inert prompt records and argument-schema references.
- `schemas`: provider-neutral typed schema registry.
- `effects`: aggregate side-effect evidence; never an authority grant.
- `provenance`: importer identity plus exact discovery-snapshot SHA-256 and optional immutable raw-seed provenance.
- `skillProjection`: target skill/plugin, required core, progressive-disclosure layers, adapter reuse, and independent-check requirement.

## First importer: MCP snapshot

The initial implementation is deliberately offline and deterministic. It consumes an exported MCP discovery snapshot rather than opening a network/process connection itself.

```text
python scripts/import_mcp.py --snapshot <mcp-discovery.json> --skill <skill-name> --plugin <plugin-name> --source-ref <pinned-source-ref> --output <capability-import.json>
```

A snapshot may contain `server`, `transport`, `tools`, `resources`, `resourceTemplates`, and `prompts`. Unknown transport fields are not copied. Only reference-style transport fields are admitted into the normalized IR.

Then route the normalized candidate into the existing Skill Creator contract:

```text
python ../dotagents-skill-creator/scripts/route_create_skill.py --catalog <catalog.json> --skill <skill-name> --plugin <plugin-name> --capability-import <capability-import.json>
```

The router verifies that the import target matches the requested skill/plugin, merges only declared progressive-disclosure layers, embeds the normalized import as provenance-bearing Skill Creator input, and preserves the independent-check gate.

## Progressive disclosure

An imported capability always needs an inert asset layer to preserve the normalized import/transport/schema metadata. Add `references/` only when MCP resources/resource templates exist. MCP transport does not by itself require a generated script because a separately registered MCP runtime owns invocation. `tests/` remain optional unless a deterministic conformance suite is requested.

## Boundaries

This skill may normalize supplied metadata and produce Skill Creator request data. It does not start an MCP server, connect to a remote MCP endpoint, install packages, retrieve credentials, invoke imported tools, publish skills, or mark a generated child as checked.

Independent CHECK must validate the normalized contract and generated child before registration. Reflection emits exactly one unexecuted next seed.
