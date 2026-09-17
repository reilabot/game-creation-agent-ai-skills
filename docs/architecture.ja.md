# アーキテクチャ

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

1 つのエンジン ルートが排他的です。分野とジャンルは加算的に構成されます。ルーターは証拠または明示的な `--engine` を使用し、具体的な製品モデルを推測することはなく、コンテキストのフラッディングを避けるためにフィクスチャの選択を制限します。

 フィードバックは、`event_kind`、`source`、`target`、`world_position`、`magnitude`、`tags`、`timestamp` などのセマンティック コントラクトを使用します。ゲームプレイには真実が含まれます。アニメーション、カメラ、VFX、オーディオ、ハプティクス、UI、アクセシビリティは、権威にならずにサブスクライブできます。チューニングは、散在するリテラルではなく、データ/資産/構成に属します。

 独立したタスクは、コントラクトが安定した後にのみ並行して実行できます。スキーマ、権限、保存移行、統合、およびリリースのプロモーションは順序付けされたままになります。 
