# Skill-creator lifecycle gate

Every PMCR-O lifecycle that creates or reconciles a skill begins with one
`skill.create.request` message emitted through `@skill-creator /create-skill`.
The message is the declarative bridge from messy intent to a generic skill
shape. It must name the plugin, skill, purpose, scope, validated resources,
required folders/files, sample prompts, message contract, and simulate/apply
mode.

The bounded route is:

`skill.create.request -> ORCHESTRATE -> PLAN -> MAKE -> CHECK -> REFLECT`

The request does not grant tools or approve a marketplace entry. The maker
creates only the declared shape. The checker validates the shape and behavior
from a fresh boundary. Reflect records the earned constraint and one
unexecuted seed. Marketplace registration is the
`after-independent-checker` projection.

The generic template requires `agents/`, `scripts/`, `references/`, `assets/`,
and `tests/`, an agent manifest, a validator, example documentation, and a
bounded `references/sample-prompts.md`. A specialized child adds domain
content while inheriting the contract and without widening its grant.
