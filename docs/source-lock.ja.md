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

これら81個の独自Skillには、本ライセンスを含む版以降、Game Dev Super Stack独自Skillライセンス1.0が適用されます。使用と参考は許可され、作者詐称とSkillの販売は禁止され、派生Skillまたは記事を公開する場合は帰属表示またはリポジトリURLが必要です。[`ORIGINAL_SKILLS_LICENSE.ja.md`](../ORIGINAL_SKILLS_LICENSE.ja.md)および対応する利用規約を参照してください。
