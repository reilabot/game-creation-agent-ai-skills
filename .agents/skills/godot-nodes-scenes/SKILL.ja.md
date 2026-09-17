---
name: godot-nodes-scenes
description: >
  Structure a Godot 4.7 project with the scene tree and node composition: build
  reusable scenes, instance PackedScenes at runtime, navigate the tree safely,
  and register autoload singletons. Use when designing .tscn scenes, deciding how
  to split nodes, spawning instances with instantiate(), wiring autoloads, or
  fixing "node not found"/freed-node errors in a Godot project.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # Godot ノードとシーン (4.x)

 ノードとシーンからゲームを作成し、実行時にそれらをインスタンス化し、解放されたノードや失われたノードでクラッシュすることなく
ツリーにアクセスします。 **Godot 4.7** をターゲットとします。

 ##

 を使用する場合 - `.tscn` シーンを構築するとき、フィーチャをノードに分割する方法を選択するとき、
 で `PackedScene` (弾丸、敵、UI) をインスタンス化するとき、または自動ロード シングルトンを設定するときに使用します。
- `null` を返す `get_node()` / `$Path` をデバッグする場合、または「以前に解放された
インスタンスを呼び出そうとする」場合に使用します。

 **使用しない場合:** GDScript 言語/構文 → `godot-gdscript`;信号ベースの
デカップリング → `godot-signals-groups`;物理ボディ/衝突 → `godot-physics`。

 ## コア ワークフロー

 1. **コンポジションを含むモデル。** シーンは、`.tscn` として保存されたノードのツリーです。小さな
の単一目的シーン (プレイヤー、バレット、敵) を構築し、それらから大きなシーンを構成します。
深い継承よりも子ノードの追加を優先します。
2. ルートにスクリプトを与え、`@export` 設定を公開することで、**シーンを再利用可能**にします。
保存します。 `PackedScene` になり、何度でもインスタンス化できます。
3. `preload`/`load` → `scene.instantiate()` →
`add_child(instance)` による **実行時のインスタンス**。追加後 (または前、両方とも機能します) 位置/状態を設定します。
4. **ノードに安全にアクセスします。** 固定の子には `@onready var x = $Path` を使用します。ツリーの深いノードには一意の
名 (`%Name`) を使用します。ノードがまだ存在するとは決して想定しないでください。
5. **グローバル状態/サービスに自動ロードを使用する** (ゲーム状態、オーディオ、シーン切り替え) —
はプロジェクト設定 > グローバル (自動ロード) に登録されており、どこからでも名前でアクセスできます。
6. **`queue_free()` でノードを解放し**、その後のアクセスを `is_instance_valid()` で保護します。

 ## パターン

 ### 1. 実行時にシーンをインスタンス化する

```gdscript
extends Node2D

const BULLET := preload("res://bullet.tscn")   # preload: loaded at compile time

func shoot(at: Vector2, dir: Vector2) -> void:
    var bullet := BULLET.instantiate()         # create an instance of the scene
    bullet.global_position = at
    bullet.direction = dir                      # set exported/public state
    add_child(bullet)                           # now it's in the tree and runs
```

### 2. 安全なノード アクセス: $、get_node_or_null、および一意の名前

```gdscript
@onready var label: Label = $UI/Label            # $ is sugar for get_node("UI/Label")
@onready var health_bar: ProgressBar = %HealthBar # % = scene-unique name (rename-proof)

func update() -> void:
    var optional := get_node_or_null("Maybe/Missing")  # returns null instead of erroring
    if optional:
        optional.queue_free()
```

### 3. 自動ロード シングルトン (グローバル ゲーム状態)

```gdscript
# game_state.gd — add in Project Settings > Globals > Autoload as "GameState".
extends Node

var score := 0
signal score_changed(value: int)

func add_score(points: int) -> void:
    score += points
    score_changed.emit(score)         # any scene can: GameState.score_changed.connect(...)
```

### 4. 走行シーンを変更する

```gdscript
func go_to_level_2() -> void:
    # Swaps the current scene for another. Frees the old scene tree.
    get_tree().change_scene_to_file("res://levels/level_2.tscn")
    # Or, with a preloaded PackedScene:
    # get_tree().change_scene_to_packed(LEVEL_2)
```

## 落とし穴

 - **`$Path` / `get_node()` は、パスが間違っているか、ノード
がまだツリーにない場合、`null` またはエラーを返します**。 `@onready` を使用してパスがシーンと一致することを確認するか、オプションのノードに
`get_node_or_null()` を使用します。
- **ノードの名前を変更すると、`$Path` が壊れます。** **一意の名前** (`%Name`、
 を右クリックして [一意の名前としてアクセス] で設定) を使用して、名前の変更や親の再設定後も深い参照が存続できるようにします。
- **`free()` フレーム途中でノードを使用している他のコードがクラッシュする可能性があります**。
`queue_free()` (フレームの最後で削除) を優先し、`is_instance_valid(node)` をオンにします。
- **`add_child()` の前に子の状態を設定する** ことは問題ありませんが、子でのみ `_ready()` を実行すると、ツリーに入った_後_、その前の `@onready` 変数を期待しないでください。
- **オートロードの順序は重要です**: オートロードはリストの順序でメイン シーンの前に追加されます。
自動ロードは、まだ存在するメイン シーンに依存できません。
- Godot 4 では **`instance()` は `instantiate()` に名前変更されました**。 `preload` は
解析時に実行されます (パスは一定である必要があります)。 `load` は実行時に実行されます (パスは変数にすることができます)。
- **`change_scene_to_file()` は即時ではなく遅延**です。Godot は現在のフレームの終わりに古い
シーンを交換して解放します。呼び出し後のコードは引き続き _old_
ツリーに対して実行され、`get_tree().current_scene` は次のフレームまで新しいシーンになりません。新しい
シーンのノードを同じ行に読み取らないでください。新しいシーンの `_ready()` から実行します。

 ## 参照

 - シーンの継承、コードからシーンを保存するときの `owner`/所有権、グループと
の一意の名前、およびノー​​ド パスのエッジ ケースについては、`references/tree-and-instancing.md` を参照してください。

 ## 関連スキル

 - `godot-gdscript` — 言語、ライフサイクル、および `@onready`。
- `godot-signals-groups` — インスタンス化されたシーンをスポナーから切り離します。
- `godot-resources` — インスタンス間でデータを複製せずに共有します。
- `save-systems` — 実行間でシーン/ゲームの状態を保持します。 
