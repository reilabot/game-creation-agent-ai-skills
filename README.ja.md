# Game Creation Agent AI Skills（日本語）

 Unity、Unreal Engine、Godot、Roblox、Bevy、Phaser、PixiJS、Three.js、pygame、LÖVE、カスタム エンジン全体でゲームを計画、構築、検証、出荷するためのポータブル エージェント スキル スタック。

 ## 含まれるもの

 - 109 個の独立して検出可能なエージェント スキル
- 28 個のピン留めされた Apache-2.0 アップストリーム スキルと 81 個のオリジナル スキル
- ゲーム スタジオ ディレクター、プロジェクト アナライザー、言語セレクター、ルーター、およびクオリティ ゲート
- エンジン、ジャンル、ゲームプレイ、ネットワーキング、UI/UX、VFX、オーディオ、アクセシビリティ、パフォーマンス、QA、CI/CD、出版カバレッジ
- 17 個のルーティング フィクスチャと依存関係のない Python バリデータ
- 複数の AI コーディング エージェント用の共有 `.agents/skills` レイアウト

 ## クイック スタート

 このリポジトリをゲーム プロジェクト内またはその横にクローンし、`.agents`、`scripts`、および `tests` をプロジェクト ルートにコピーして、次を実行します:

```bash
python scripts/validate_stack.py
python scripts/gamedev_router.py "four-player online survival crafting game with a dedicated server" --engine unreal
```

期待される検証結果:

```text
skills=109 fixtures=17 errors=0
```

## インストール

 - 日本語の 1 ファイル AI インストーラー: [INSTALL_JA.md](INSTALL_JA.md)
- 英語の 1 ファイル AI インストーラー: [INSTALL_EN.md](INSTALL_EN.md)
- アーキテクチャ: [docs/architecture.md](docs/architecture.md)
- カバレッジ マトリックス: [docs/coverage-matrix.md](docs/coverage-matrix.md)
- ソースとライセンス ロック: [docs/source-lock.md](docs/source-lock.md)
- 検証証拠: [docs/validation-report.md](docs/validation-report.md)

 ## サポートされる AI クライアント

 正規のプロジェクトの場所は `.agents/skills` です。ディストリビューションには、OpenAI Codex、Claude Code、Cursor、Gemini CLI、Google Antigravity、GitHub Copilot、およびその他のエージェント スキル互換クライアントのセットアップ ノートが含まれています。

 すべての Markdown ソースには、明示的な英語 (`*.en.md`) と日本語 (`*.ja.md`) のコンパニオンがあります。 `SKILL.md` は、ツールの互換性のための正規のエージェント スキル エントリ ポイントのままです。

 ## 安全性

 ルーターは選択のみを実行します。公開、デプロイメント、購入、資格情報の使用、および本番またはプレーヤー データの変更には、アクションの時点で明示的な承認が必要です。決して秘密を犯さないでください。

 ## ライセンス

Game Creation Agent AI SkillsにはApache License 2.0が適用されます。これには、独自Skill 81個と、リポジトリ独自のツール、設定、テスト、文書が含まれます。外部Skill 28個には、元のApache-2.0帰属表示が維持されています。詳細は[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)を参照してください。
