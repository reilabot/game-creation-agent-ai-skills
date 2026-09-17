# Game Creation Agent AI Skills

A portable Agent Skills stack for planning, building, validating, and shipping games across Unity, Unreal Engine, Godot, Roblox, Bevy, Phaser, PixiJS, Three.js, pygame, LÖVE, and custom engines.

## What is included

- 109 independently discoverable Agent Skills
- 28 pinned Apache-2.0 upstream skills and 81 original skills
- Game Studio Director, Project Analyzer, Language Selector, Router, and Quality Gate
- Engine, genre, gameplay, networking, UI/UX, VFX, audio, accessibility, performance, QA, CI/CD, and publishing coverage
- 17 routing fixtures and a zero-dependency Python validator
- Shared `.agents/skills` layout for multiple AI coding agents

## Quick start

Clone this repository into or beside your game project, copy `.agents`, `scripts`, and `tests` into the project root, then run:

```bash
python scripts/validate_stack.py
python scripts/gamedev_router.py "four-player online survival crafting game with a dedicated server" --engine unreal
```

Expected validation result:

```text
skills=109 fixtures=17 errors=0
```

## Installation

- Japanese one-file AI installer: [INSTALL_JA.md](INSTALL_JA.md)
- English one-file AI installer: [INSTALL_EN.md](INSTALL_EN.md)
- Architecture: [docs/architecture.md](docs/architecture.md)
- Coverage matrix: [docs/coverage-matrix.md](docs/coverage-matrix.md)
- Source and license lock: [docs/source-lock.md](docs/source-lock.md)
- Validation evidence: [docs/validation-report.md](docs/validation-report.md)

## Supported AI clients

The canonical project location is `.agents/skills`. The distribution includes setup notes for OpenAI Codex, Claude Code, Cursor, Gemini CLI, Google Antigravity, GitHub Copilot, and other Agent Skills-compatible clients.

Every Markdown source has explicit English (`*.en.md`) and Japanese (`*.ja.md`) companions. `SKILL.md` remains the canonical Agent Skills entry point for tool compatibility.

## Safety

The Router performs selection only. Publishing, deployment, purchases, credential use, and production or player-data mutation require explicit approval at the point of action. Never commit secrets.

## License

This repository uses a split license model:

- The 81 original Skills use the [Game Creation Agent AI Skills Original Skills License 1.0](ORIGINAL_SKILLS_LICENSE.en.md). Use and reference are free; false authorship and sale of the Skills are prohibited; public derivative Skills and articles require attribution or the repository URL. See the [Terms of Use](TERMS_OF_USE.en.md).
- The 28 vendored Skills remain under Apache License 2.0. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [`LICENSES/Apache-2.0.txt`](LICENSES/Apache-2.0.txt).
- This is a source-available custom license, not an OSI-approved open-source license, because it restricts sale and paid redistribution of the original Skills.
