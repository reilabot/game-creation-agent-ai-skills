# Architecture

```text
USER GOAL
  -> game-studio-director
  -> gamedev-project-analyzer
  -> engine / genre / platform detection
  -> gamedev-router + capability-class routing
  -> engine and system specialists
  -> playable increment
  -> game-qa-playtest + gamedev-quality-gate
  -> bounded fix loop
  -> game-build-ci-cd + publishing skill
```

One engine route is exclusive; disciplines and genres compose additively. The router uses evidence or an explicit `--engine`, never guesses a concrete product model, and caps fixture selections to avoid context flooding.

Feedback uses a semantic contract such as `event_kind`, `source`, `target`, `world_position`, `magnitude`, `tags`, and `timestamp`. Gameplay owns truth; animation, camera, VFX, audio, haptics, UI, and accessibility subscribe without becoming authorities. Tuning belongs in data/assets/configuration, not scattered literals.

Independent tasks may run in parallel only after contracts are stable. Schema, authority, save migration, integration, and release promotion remain ordered.
