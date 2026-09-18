# ソースロック

 ## 外部スキル

 - リポジトリ: `https://github.com/gamedev-skills/awesome-gamedev-agent-skills`
- ソース リビジョン: `b105e1cf617adf0b68ed98790a716bbb60993179`
- ライセンス: Apache-2.0;通知付きで再配布が許可されています
- 統合: 選択したフォルダーのベンダー、未変更
- ローカルの宛先: `.agents/skills/<source-folder-name>`
- 更新手順: 上流の差分とライセンスを監査し、固定されたリビジョンを変更し、`scripts/install_stack.py` で SHA-256 をアーカイブし、空の一時ツリーにインストールし、バリデーターとフィクスチャーの両方を実行し、レビューされた外部フォルダーのみを置き換えます。
- 複製: `python scripts/install_stack.py --dest <empty-project-copy>`

 ロックされたソース パス (28):

 `unity-csharp-scripting`、`unreal-cpp-gameplay`、`godot-gdscript`、`godot-nodes-scenes`、`roblox-luau`、 `roblox-networking`、`bevy-ecs`、`phaser-core`、`pixijs-rendering`、`threejs-scene-setup`、`pygame-core`、`love2d-core`、`save-systems`、`performance-optimization`、`game-ai`、 `procedural-gen`、`audio-design`、`shader-programming`、`level-design`、`game-ui-ux`、`input-systems`、`game-feel`、`survival-crafting`、`rpg`、`roguelike`、 `platformer`、`steam-publish`、`itch-publish`。

 ## ローカル スキル

 他の 81 のスキルは、`scripts/build_gamedev_stack.py` によって生成されたオリジナルのリポジトリ ローカル作業です。外部ソース ロックはありません。生成されたファイルは権限があり、既存のスキル フォルダーの上書きを意図的に拒否します。 

これら81個の独自Skillには、リポジトリ独自のツール、設定、テスト、文書とともにApache License 2.0が適用されます。
