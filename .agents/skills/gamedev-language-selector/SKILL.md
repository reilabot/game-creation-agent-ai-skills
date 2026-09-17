---
name: gamedev-language-selector
description: Select or confirm a programming language for a game project from engine constraints, target platforms, performance needs, iteration speed, ecosystem, and team capability. Use for new projects, undecided engines, or language/engine tradeoffs.
---

# Game Development Language Selector

Choose a language only after separating hard constraints from preferences. If an existing engine or codebase fixes the language, confirm that constraint instead of proposing a rewrite.

## Decision inputs

- Existing engine, source language, build pipeline, plugins, and shipped code
- Target platforms and store or console restrictions
- Game scale, simulation density, latency, memory, loading, and determinism needs
- Team experience, hiring, iteration speed, debugging, tooling, middleware, and maintenance horizon
- Networking authority, modding/scripting needs, native integration, and deployment model

## Workflow

1. Detect existing project evidence first. Treat an established engine-language pairing as locked unless the user explicitly requests migration analysis.
2. Convert requirements into hard constraints, weighted preferences, and unknowns. Do not equate raw language speed with shipped-game performance without profiling evidence.
3. Eliminate incompatible options, then compare the remaining candidates on platform support, engine maturity, libraries, iteration, runtime behavior, operations, and team risk.
4. Return one primary recommendation when evidence is decisive. Otherwise return a ranked shortlist and name the smallest prototype or benchmark that resolves the uncertainty.
5. Route to the matching engine Skill. Keep gameplay scripting, native extensions, shaders, build scripts, and backend services as separate language decisions when appropriate.

## Output contract

Report `primary`, `alternatives`, `locked_by_engine`, `confidence`, `reasons`, `tradeoffs`, and `validation`. Never invent an engine-language combination that the target engine does not support.

## Boundaries

Do not migrate an existing project, add a runtime, or change build tooling merely because another language scores higher. Such changes require an explicit migration request and evidence covering plugins, assets, saves, CI, platform certification, and rollback.
