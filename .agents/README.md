# Game Dev Super Stack

This repository-local stack contains independently discoverable Agent Skills. Start with `game-studio-director`; it invokes `gamedev-project-analyzer`, confirms or selects the language with `gamedev-language-selector`, then uses `gamedev-router` and closes each increment with `gamedev-quality-gate`.

The router deliberately selects a small composition: one detected engine, applicable genre/system skills, then QA. JSON documents with `.yaml` names are valid YAML 1.2 and remain readable by the standard-library tooling.

Run:

```powershell
python scripts/gamedev_router.py "Steam向け4人協力型サバイバル、建築、クラフト、専用サーバー" --engine unreal
python scripts/validate_stack.py
```

Codex discovers project skills under `.agents/skills/`. Antigravity users should configure the same directory as a workspace Agent Skills root; if their build only scans `.agent/skills`, create a non-vendored junction or copy during local setup and keep `.agents/skills` authoritative.
