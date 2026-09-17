# GDScript アノテーションと型指定リファレンス (Godot 4.7)

 `godot-gdscript` の深さのコンパニオン。 GDScript 2.0 では、すべての注釈は `@` で始まります。

 ## 共通のエクスポート注釈

```gdscript
@export var title: String = "Level 1"
@export var enabled := true
@export_range(0, 100, 1) var percent: int = 50          # min, max, step
@export_range(0.0, 1.0, 0.01, "or_greater") var gain := 1.0
@export_enum("Idle", "Walk", "Run") var state: int       # int-backed dropdown
@export_enum("Sword", "Bow") var weapon: String          # string-backed dropdown
@export_flags("Fire", "Water", "Earth") var resist: int  # bitmask
@export_file("*.json") var data_path: String             # file picker
@export_dir var folder: String
@export_multiline var description: String                 # multi-line text box
@export_color_no_alpha var tint: Color
@export_node_path("Camera2D") var cam_path: NodePath
@export_group("Movement")                                 # groups Inspector fields
@export var speed := 200.0
@export_subgroup("Air")
@export var air_control := 0.4
```

リソースの型付き配列をエクスポートします (データ駆動設計に最適):

```gdscript
@export var waves: Array[PackedScene] = []
@export var loot: Array[ItemResource] = []
```

## その他の注釈

 - `@onready var x = $Child` — ノードがツリーに入るときに割り当てます。
- `@tool` — エディターでスクリプトを実行します (ファイルの先頭)。エディター専用コードを
`if Engine.is_editor_hint():` でガードします。
- `@icon("res://icon.svg")` — `class_name` タイプのカスタム インスペクター アイコン。
- `@rpc("any_peer", "call_local", "reliable")` — ネットワーク化されたメソッドをマークします (
 `godot-multiplayer` を参照)。
- `@warning_ignore("unused_variable")` — 特定のパーサー警告を沈黙させます。
- `@static_unload` — スクリプトの静的変数のアンロードを許可します。

 ## 静的型付けの詳細

```gdscript
var a: int = 3                 # explicit type
var b := 3                     # inferred int via :=
var c: float                   # typed, defaults to 0.0
var nodes: Array[Node2D] = []  # typed array (element type enforced)
var scores: Dictionary = {}    # Dictionary is untyped in 4.3; typed dicts arrived in 4.4

func clamp_hp(hp: int) -> int:
    return clampi(hp, 0, 100)  # clampi/clampf are typed variants
```

VM は実行時の型チェックをスキップでき、エディターは実行前に
オートコンプリートして不一致にフラグを立てることができるため、入力されたコードは高速になります。

 ## ライフサイクル コールバック (順序)

 1. `_init()` — オブジェクトが構築されました (ツリーも子も解決されません)。
2. `_enter_tree()` — ノードがツリーに追加されました (子の準備ができていない可能性があります)。
3. `_ready()` — ノードとすべての子がツリー内にあります (1 回実行)。 `@onready` 変数は、この直前に
が割り当てられます。
4. `_process(delta)` — レンダリングされたすべてのフレーム (`set_process(false)` でスキップ)。
5. `_physics_process(delta)` — すべての固定物理ティック (デフォルトは 60 Hz)。
6. `_exit_tree()` — ノードがツリーから削除されました。
7. `_notification(what)` — 低レベルのキャッチオール (例: `NOTIFICATION_WM_CLOSE_REQUEST`)。

 ## イディオム

 - 解放された可能性のあるノードに触れる前に、`is_instance_valid(node)` を優先します。
- フ​​レーム中にノードを安全に削除するには、`free()` ではなく `queue_free()` (遅延) を使用します。
- `match` は GDScript のスイッチです。値、配列 `[1, var x]`、および `_` のデフォルトをサポートします。
- 文字列の書式設定: `"%s scored %d" % [name, score]`。
- デバッグ専用の不変式には `assert(cond, "msg")` を使用します (リリース ビルドでは削除されます)。 
