# Game Dev Super Stack

A portable Agent Skills stack for planning, building, validating, and shipping games across Unity, Unreal Engine, Godot, Roblox, Bevy, Phaser, PixiJS, Three.js, pygame, LÖVE, and custom engines.

## 日本語での説明

Game Dev Super Stackは、ゲームの企画、設計、実装、検証、公開までを支援する、AIコーディングエージェント向けのゲーム開発Skill集です。Unity、Unreal Engine、Godot、Roblox、Bevy、Phaser、PixiJS、Three.js、pygame、LÖVE、独自エンジンに対応しています。

109個のSkillから、ゲームエンジン、プログラミング言語、ジャンル、ゲームシステム、ネットワーク、UI/UX、VFX、オーディオ、アクセシビリティ、パフォーマンス、QA、CI/CD、ストア公開など、依頼内容に必要なSkillだけをRouterが選択します。ゲーム制作時の言語選択には`gamedev-language-selector`が使用されます。

主な特徴:

- OpenAI Codex、Claude Code、Cursor、Gemini CLI、Google Antigravity、GitHub Copilotなどで利用可能
- 既存プロジェクトのエンジン、言語、構成を検出して尊重
- ゲーム開発に必要なSkillを依存関係順に選択
- 実装後に機能、視覚、パフォーマンス、アクセシビリティ、ネットワークを検証
- 公開、デプロイ、購入、認証情報の利用、プレイヤーデータの変更は明示的な承認がある場合だけ実行
- 全Markdownに英語版（`*.en.md`）と日本語版（`*.ja.md`）を用意

AIへ一つのMarkdownを渡して導入する場合は、[INSTALL_JA.md](INSTALL_JA.md)を使用してください。英語版は[INSTALL_EN.md](INSTALL_EN.md)です。導入後は次のコマンドで構成を検証できます。

```bash
python scripts/validate_stack.py
```

正常な場合は`skills=109 fixtures=17 errors=0`と表示されます。

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

Original Game Dev Super Stack content is licensed under Apache License 2.0. Vendored skills retain their upstream Apache-2.0 attribution; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
