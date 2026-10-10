# Overview: from “I AM” to an inspectable artifact

The project question is not “How do we make a model claim to be a philosopher?” It is:

> How can a system use philosophical ideas as bounded interpretive lenses while preserving provenance, agency boundaries, and a trail that another agent can check?

Thought Transfer answers with a translation pipeline:

1. A human supplies a raw seed.
2. An orchestrator records the seed and constrains the charter.
3. A planner turns the intent into a small role graph and acceptance contract.
4. A maker creates declarative artifacts and simulations.
5. A fresh checker checks the artifacts without grading its own work.
6. A reflector records an earned constraint and emits a bounded next seed.

The system can have many entrypoints: different accounts, plugins, local models, Figma sessions, or API surfaces. An entrypoint identifies who or what is asking. The charter determines what may happen. Those are intentionally separate.

## Resource-first session handoff

A new session does not need the entire previous conversation by default. The orchestrator passes the smallest validated handoff:

- the preserved raw seed or derived intent;
- principal and entrypoint;
- exact package IDs, paths, hashes, commits, and evidence references that were checked;
- the phase charter and acceptance contract; and
- one unexecuted next-seed prompt intent.

The receiving session requests another package only when it cannot access a declared resource. A full transcript is an exceptional recovery input, not the normal Thought Transfer protocol. This keeps context progressive and prevents a session from inventing authority from information it was never asked to validate.

The orchestrator owns the phase transition. The only normal route is `ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`; a checker failure is not permission to jump directly between phases. Reflection records the earned constraint and returns control to a new bounded orchestrate frame.

Reflective next seeds have explicit levels: `meta` repairs the current artifact or phase acceptance; `meta-meta` repairs the skill or workflow contract; `meta-meta-meta` repairs the orchestrator, agent surface, or prompt-routing system. Every level remains a prompt intent and stays unexecuted until the orchestrator opens the next cycle.

## Two flows

The design has a backward flow and a forward flow:

```text
backward: trail -> reflection -> constraint -> reusable skill/design
forward:  checked trail product -> user identity + intent -> personalized deliverable
```

The backward flow is how the system learns a reusable pattern, like writing a book from lived chapters and then extracting a method. The forward flow is how a checked trail becomes a product that an end user can buy or use. The user injects identity and intent as declared context; the product may optimize for high-quality or commercially strong output, but it cannot guarantee bestseller status, impersonate the user, or widen its authority.

MCP fits between these stages as a typed transport and tool boundary: it can carry an intent envelope, invoke a domain capability, and return an artifact or evidence reference. It transfers structured work products and provenance—not a mind, consciousness, or private inner state.

## Three kinds of identity

| Identity | Meaning | What it cannot do by itself |
| --- | --- | --- |
| Account/principal | A caller or external identity | Grant extra permissions |
| Agent surface | A role with tools, limits, and a context boundary | Escape its declared charter |
| `I AM` simulation | A conceptual voice used for reasoning | Establish consciousness, personhood, or authority |

## The core invariant

Every phase can say “I AM [this bounded role]” only if it also says:

- what it notices;
- what it is allowed to do;
- what it refuses;
- what evidence it produces; and
- what it hands to the next phase.

That turns identity from a theatrical claim into a testable interface.
