---
name: godot-gdscript
description: >
  Write idiomatic GDScript for Godot 4.7: static typing, the node lifecycle
  (_ready/_process/_physics_process), @export/@onready/@tool annotations,
  signals, and await for asynchronous flow. Use when editing .gd scripts in a
  Godot project (project.godot), writing or debugging GDScript, or porting 3.x
  GDScript to 4.x (function signatures, yield to await, export to @export).
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # Godot GDScript (4.x)

 静的に型指定された正しい GDScript を記述し、ノードのライフサイクルを使用し、エンジンが意図する方法で
システムに信号を送ります。 **Godot 4.7** (GDScript 2.0) をターゲットとします。

 ##
を使用する場合
- `.gd` ファイルを作成または修正する場合に使用します: `@export`/`@onready` を使用した変数、関数、クラス、
 の宣言、信号の接続、またはコルーチン/信号の待機。
- Godot 3.x スクリプトを 4.x に移植すると、スクリプトが解析されなくなる場合に使用します。

 **使用しない場合:** シーン/ノードの構造とインスタンス化の質問 →
`godot-nodes-scenes`;信号 *アーキテクチャ*/デカップリング パターン →
`godot-signals-groups`; GDScript の代わりに C# を使用 → `godot-csharp`。

 ## コア ワークフロー

 1. **入力できるものはすべて入力します。** GDScript 2.0 は、静的型
(`var hp: int = 10`、`func add(a: int, b: int) -> int:`) をサポートします。タイプは
解析時にエラーをキャッチし、VM を高速化します。推論型には `:=` を使用します。
2. **ライフサイクル コールバックを目的に応じて使用します。** ノード
とその子がツリーに入るときに `_ready()` を 1 回実行します。 `_process(delta)` レンダリングされたフレームごと。固定物理チェックの
`_physics_process(delta)` (移動/物理に使用します)。
3. **`_init()` ではなく、`@onready`** を使用してノード参照を取得します。ノードがツリーに入るまで、子は
に存在しません。
4. **`@export` を使用して調整パラメータを公開**し、デザイナーがインスペクターで編集できるようにします。
5. **シグナル + `await`** を使用してイベントに反応し、ポーリングではなく、きれいに読み取られます。
6. **実行エラーと読み取りエラー。** デバッガー パネルには、入力されたエラーが行番号とともに出力されます。
は、最初のエラーを最初に修正します (後のエラーはカスケードになることがよくあります)。

 ## パターン

 ### 1. ライフサイクル、@export、および @onready を使用した型指定されたスクリプト

```gdscript
extends Node2D
class_name Spinner            # registers a global type usable in other scripts

@export var speed: float = 90.0          # editable in the Inspector (degrees/sec)
@export_range(0, 10, 0.5) var wobble := 2.0
@onready var sprite: Sprite2D = $Sprite2D # resolved when the node enters the tree

func _ready() -> void:
    # Runs once, after children are ready. Safe to touch $Sprite2D here.
    sprite.modulate = Color.AQUA

func _process(delta: float) -> void:
    # delta is seconds since last frame; multiply rates by it for FPS independence.
    rotation_degrees += speed * delta
```

### 2. シグナル: 宣言、発行、接続 (4.x 呼び出し可能構文)

```gdscript
extends Node

signal health_changed(current: int, maximum: int)   # typed signal params

var health := 100

func take_damage(amount: int) -> void:
    health = max(health - amount, 0)
    health_changed.emit(health, 100)     # 4.x: emit as a method on the signal

func _ready() -> void:
    # 4.x: connect with a Callable, not a string method name.
    health_changed.connect(_on_health_changed)

func _on_health_changed(current: int, maximum: int) -> void:
    print("HP: %d/%d" % [current, maximum])
```

### 3. await — タイマーまたはシグナルが起動するまで一時停止します (3.x のyieldを置き換えます)

```gdscript
func flash_then_continue() -> void:
    modulate = Color.RED
    await get_tree().create_timer(0.2).timeout   # resume after 0.2s
    modulate = Color.WHITE
    # await any signal: var result = await some_node.some_signal
```

### 4. ラムダ、型付き配列、安全なアクセス

```gdscript
var enemies: Array[Node] = []                    # typed array

func cull_dead() -> void:
    enemies = enemies.filter(func(e): return e.is_inside_tree())

func get_first_name(d: Dictionary) -> String:
    return d.get("name", "unknown")              # default avoids missing-key errors
```

## 落とし穴

 - **3.x → 4.x シグナル API が変更されました。** `emit_signal("x")` は引き続き動作しますが、
 `x.emit(...)` を優先します。 `connect("x", self, "_on_x")` はなくなりました。`x.connect(_on_x)` を
呼び出し可能で使用してください。 `yield(obj, "sig")` は `await obj.sig` になりました。
- **`export var` は `@export var`** になりました (注釈)。同様に、`onready`→`@onready`、
 `tool`→`@tool`、`remote`/`master` RPC キーワード → `@rpc(...)` アノテーション。
- **`_init()` の `@onready` および `$NodePath` が失敗します** — ノードはまだツリーにありません。
`_ready()` または `@onready` でノード参照を初期化します。
- **整数の除算は切り捨てられます。** `5 / 2 == 2`。 `5.0 / 2` を使用するか、`float` にキャストします。
- **`_process` 対 `_physics_process`。** `move_and_slide()` と物理演算を
`_physics_process(delta)` に配置します。 `_process` を使用すると、モーションのフレームレートに依存します。
- **`class_name` はプロジェクト全体で一意である必要があります**。また、
 他のスクリプトまたはインスペクター タイプとしてタイプ名を使用する必要があります。

 ## 参考資料

 - 注釈の完全なリスト、高度な型指定、およびスタイル規則については、
 `references/annotations-and-typing.md` を参照してください。

 ## 関連スキル

 - `godot-nodes-scenes` — シーン ツリー、インスタンス化、自動ロード。
- `godot-signals-groups` — 信号とグループを備えたイベント駆動型のアーキテクチャ。
- `godot-resources` — カスタム `Resource` タイプを使用したデータ駆動型の設計。
- `godot-csharp` — C#/.NET を使用した同じエンジンのコンセプト。 
