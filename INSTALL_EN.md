# Game Dev Super Stack Installation Instructions (English)

This document is both a human guide and a complete execution prompt for an AI coding agent. Give the AI this file's URL or full contents while it is operating at the target game project's root, then ask:

```text
Read this entire INSTALL_EN.md and install and validate Game Dev Super Stack in the current game project while following every safety constraint.
```

## Instructions for the AI agent

Install Game Dev Super Stack into the current game project. Do not stop at a proposal: retrieve the distribution, place or safely merge its files, and complete validation.

Source repository:

```text
https://github.com/reilabot/game-creation-agent-ai-skills
```

### Safety constraints

1. Before changing files, inspect the project root, `AGENTS.md`, `.agents/`, `scripts/`, `tests/`, and uncommitted changes.
2. Never overwrite an existing file blindly. If a same-named file differs, inspect the diff and preserve the project's existing behavior while integrating the Stack.
3. Never upload or expose `.env` files, credentials, databases, save data, private keys, proprietary assets, or unrelated game code.
4. Download into a temporary directory and copy only the listed Stack files into the target project.
5. If `AGENTS.md` exists, merge the Stack instructions; do not replace the existing file.
6. Run validation after installation and report failures accurately.

### Retrieve the distribution

If Git is available, clone into a temporary directory:

```bash
git clone --depth 1 https://github.com/reilabot/game-creation-agent-ai-skills.git <temporary-directory>
```

Without Git, download and extract this archive into a temporary directory:

```text
https://github.com/reilabot/game-creation-agent-ai-skills/archive/refs/heads/main.zip
```

### Install into the target project

Merge only these paths from the temporary distribution:

```text
.agents/
scripts/build_gamedev_stack.py
scripts/gamedev_router.py
scripts/install_stack.py
scripts/validate_stack.py
tests/router-fixtures.json
docs/
LICENSE
LICENSES/
ORIGINAL_SKILLS_LICENSE.en.md
ORIGINAL_SKILLS_LICENSE.ja.md
TERMS_OF_USE.en.md
TERMS_OF_USE.ja.md
THIRD_PARTY_NOTICES.md
```

Merge this section into the target project's `AGENTS.md` without removing existing instructions:

```markdown
## Game Dev Super Stack

- For substantial game work, begin with `.agents/skills/game-studio-director/SKILL.md`.
- Analyze the project, confirm or select the language, and route only the necessary engine and cross-cutting skills.
- Keep simulation truth separate from presentation and connect feedback systems through explicit contracts.
- Finish playable increments with `game-qa-playtest` and `gamedev-quality-gate`.
- Require explicit approval before publishing, deployment, purchases, credential use, or production/player-data mutation.
```

### AI client discovery

Keep `.agents/skills/` as the single source of truth.

- OpenAI Codex: use `.agents/skills/` and `AGENTS.md`.
- Cursor: use `.agents/skills/` as project skills.
- Gemini CLI: use `.agents/skills/` and verify with `/skills`.
- Google Antigravity: use `.agents/skills/` as workspace skills.
- GitHub Copilot: use `.agents/skills/` as project skills.
- Claude Code: only if the environment does not discover `.agents/skills/`, create a junction or symlink from `.claude/skills` to `.agents/skills`. Do not duplicate the skills.
- Other clients: register `.agents/skills` as the Agent Skills search root when supported.

### Validate

Run from the target project root:

```bash
python scripts/validate_stack.py
```

Required result:

```text
skills=109 fixtures=17 errors=0
```

Also inspect a Router result:

```bash
python scripts/gamedev_router.py "four-player online survival crafting game with a dedicated server" --engine unreal
```

Confirm that the result contains `engine`, `language_selection`, `skills`, `roles`, `model_classes`, `tools`, and `dependency_order`.

### Completion report

Report:

1. Project-relative installation paths
2. Files created or merged
3. Skill and fixture counts
4. Validator result
5. Conflicts and how they were resolved
6. Whether the active AI client discovered the skills
7. Remaining limitations or manual steps

Do not claim completion unless validation reports `skills=109 fixtures=17 errors=0`.
