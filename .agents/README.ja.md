# ゲーム開発スーパー スタック

 このリポジトリ ローカル スタックには、独立して検出可能なエージェント スキルが含まれています。 `game-studio-director` から始めます。 `gamedev-project-analyzer` を呼び出し、`gamedev-language-selector` で言語を確認または選択し、次に `gamedev-router` を使用して、`gamedev-quality-gate` で各増分を閉じます。

 ルーターは、検出された 1 つのエンジン、該当するジャンル/システム スキル、次に QA という小さな構成を意図的に選択します。 `.yaml` 名を持つ JSON ドキュメントは有効な YAML 1.2 であり、標準ライブラリ ツールで引き続き読み取り可能です。

 実行:

```powershell
python scripts/gamedev_router.py "Steam向け4人協力型サバイバル、建築、クラフト、専用サーバー" --engine unreal
python scripts/validate_stack.py
```

Codex は、`.agents/skills/` の下でプロジェクト スキルを検出します。 Antigravity ユーザーは、ワークスペースのエージェント スキル ルートと同じディレクトリを構成する必要があります。ビルドが `.agent/skills` のみをスキャンする場合は、ローカル セットアップ中に非ベンダー ジャンクションまたはコピーを作成し、`.agents/skills` の権限を維持します。 
