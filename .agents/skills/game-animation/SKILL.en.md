---
name: game-animation
description: Design responsive state-driven animation, rigs, retargeting, root motion, blending, events, and performance. Use for character or object animation.
---

# game-animation

## Scope

Own this responsibility while preserving the detected engine's conventions. Do not replace adjacent specialists; compose through explicit data and semantic event contracts.

## Workflow

1. Read the project profile, player-facing goal, constraints, target hardware, and existing tests before changing files.
2. State measurable behavior, ownership, tunable parameters, failure cases, and the smallest playable increment.
3. Implement through engine-native APIs after detecting versions and available tools. Keep simulation truth separate from presentation.
4. Connect neighboring systems with data schemas or semantic events; avoid direct cross-system dependencies where a stable contract works.
5. Produce state graph, timing contract, transition and runtime tests.

## Quality gate

Test the representative player journey and edge cases on the target input and platform. Capture available logs, screenshots/video, profiler data, saves, or network traces. A file existing is not proof of correct behavior.

## Boundaries

Require explicit approval immediately before destructive data operations, purchases, credential use, store publication, production deployment, or irreversible external changes. Never embed secrets. Route final acceptance through `gamedev-quality-gate`.
