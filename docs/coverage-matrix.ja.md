# カバレッジ マトリックス

 ステータスは `full`、`partial`、`planned`、または `not-applicable` で、証拠スキルに名前を付けます。

 ## エンジン × 基本性能

 |エンジン |コア |ゲームプレイ/データ | UI/入力 |ビルド/リリース |
|---|---|---|---|---|
|団結 |フル `unity-csharp-scripting` |フルクロスエンジンシステム |フル `game-responsive-ui`、`game-input-design` |部分的 `game-build-ci-cd` |
|アンリアル |フル `unreal-cpp-gameplay` |フルクロスエンジンシステム |フル UI/入力スペシャリスト |部分的 `game-build-ci-cd` |
|ゴドー |フル `godot-gdscript`、`godot-nodes-scenes` |フルクロスエンジンシステム |フル UI/入力スペシャリスト |部分的 `game-build-ci-cd` |
|ロブロックス |フル `roblox-luau`、`roblox-networking` |フルクロスエンジンシステム |フル UI/入力スペシャリスト |部分的なプラットフォームの公開 |
|ベヴィ |フル `bevy-ecs` |フルクロスエンジンシステム |エンジン UI の詳細の一部 |部分的 `game-build-ci-cd` |
|フェイザー |フル `phaser-core` |フルクロスエンジンシステム |フル UI/入力スペシャリスト |フル `itch-publish` |
| PixiJS |フル `pixijs-rendering` |部分的なフレームワーク/ゲーム ループ |フル UI/入力スペシャリスト |フル `itch-publish` |
|スリー.js |フル `threejs-scene-setup` |フルクロスエンジンシステム |フル UI/入力スペシャリスト |フル `itch-publish` |
|パイゲーム |フル `pygame-core` |フルクロスエンジンシステム |部分的な高度な UI |部分的なデスクトップパッケージ |
|愛 |フル `love2d-core` |フルクロスエンジンシステム |部分的な高度な UI |部分的なデスクトップパッケージ |
|カスタムエンジン |部分的なプロジェクトネイティブ API |完全な契約/システム |完全な意図、計画されたアダプター |部分的にプラットフォーム固有 |

 ## ジャンル x 必要なシステム

 |ジャンルファミリー |ステータスとスキル |
|---|---|
| RPG、ローグライク、サバイバル、プラットフォーマー |フル `rpg`、`roguelike`、`survival-crafting`、`platformer` |
| MMO、RTS、4X、都市/コロニー/大物 |フル `genre-mmo`、`genre-rts`、`genre-4x`、`genre-city-builder`、`genre-colony-sim`、`genre-tycoon` |
|ソウルライク、メトロイドヴァニア、格闘 |それぞれの完全な `genre-*`、戦闘/感覚/ネットコード スキル |
|レース、スポーツ、リズム |それぞれの完全な `genre-*`、レイテンシー/カメラ/オーディオ スキル |
|エクストラクション、MOBA、オートバトラー、パーティー |それぞれの完全な `genre-*`、権限/経済/QA スキル |
|アイドル・ガチャ・ライブサービス |フル `genre-idle-incremental`、`genre-gacha-live-service`、経済/出版ゲート |

 ## 生産段階 x オーナー

 |ステージ |ステータスとスキル |
|---|---|
|コンセプト・デザイン |フル `game-design`、`game-studio-director` |
|エンジニアリング/ゲームプレイ/ワールド/AI |フル エンジン スキル、`game-ai`、`level-design`、システム スキル |
| 2D/3D/アニメーション/VFX/オーディオ |フル `game-art-*`、`game-animation`、`game-vfx-*`、`game-audio` |
| UI/UX/アクセシビリティ/感触 |すべて `game-ui-*`、`game-accessibility`、`game-*-feel`、入力/カメラ/ハプティクス |
|パフォーマンス/QA |フル `performance-optimization`、`game-qa-playtest`、`gamedev-quality-gate` |
|ビルド/公開/liveops |完全な汎用パイプライン。部分的なプラットフォーム SDK の詳細 |

 ## プラットフォーム x 配信

 |プラットフォーム |ステータスとスキル |
|---|---|
| Steam デスクトップ |完全汎用 `steam-publish`、`game-build-ci-cd` |
| itch.io/web |完全な `itch-publish`、Web エンジンのスキル |
|モバイル |完全な設計/テストの意図。部分的な店舗固有の自動化 |
|コンソール |計画された SDK 固有の機密ツール。一般的なゲートが適用されます。
|ロブロックス |部分的なプラットフォーム固有のリリース。完全なランタイムスキル |

 ## プレーヤー トポロジ x ネットワーク/保存/QA

|トポロジー |ステータスとスキル |
|---|---|
|シングルプレイヤー |フル `save-systems`、`game-save-migration`、QA |
|ローカルマルチプレイヤー |完全な入力/アクセシビリティ/QA。部分的なエンジン デバイス アダプター |
|オンライン協力プレイ |フル権限/予測/同期解除/コントラクトの保存 |
|競争力のあるロールバック |完全な `game-rollback-netcode`、アンチチート、障害テスト |

 指示で要求されている正確な UI/VFX/フィールの責任は、同じ名前のスキル ディレクトリによって個別に追跡できます。アクセシビリティとパフォーマンスは、リリース時にのみ追加されるのではなく、設計ルートと品質ゲートで選択されます。

 ## 言語選択

 `gamedev-language-selector` は常にルーティングされます。既存のエンジンは、サポートされている主言語をロックします。新しいプロジェクトは、プラットフォーム、エンジン エコシステム、パフォーマンス、イテレーション速度、チームの制約を使用して比較されます。ルーターは、主な選択肢、代替案、信頼度、理由、トレードオフ、および検証スパイクを返します。証拠が不十分な場合は、確実性を生み出すのではなく、候補リストを返します。 
