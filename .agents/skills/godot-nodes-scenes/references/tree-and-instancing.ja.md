# シーン ツリーとインスタンス化リファレンス (Godot 4.7)

 `godot-nodes-scenes` の深度コンパニオン。

 ## ノード パス

 - `$Child`、`$Child/Grandchild` — `get_node(...)` の相対パス シュガー。
- `$"Node With Spaces"` — スペースを含むパス、または数字で始まるパスを引用符で囲みます。
- `%UniqueName` — シーン固有のノード。エディターでノードを「一意の名前としてアクセス」とマークします。
ノードがそのシーンのサブツリーのどこに位置していても、参照は機能します。
- `get_node("../Sibling")` — `..` は親に近づきます。
- `get_tree().root` — 一番上の `Window`。現在のシーンは
`get_tree().current_scene` です。

 ## ロードとインスタンス化

```gdscript
const SCENE := preload("res://enemy.tscn")   # constant path, loaded with the script
var dynamic := load(path_variable)            # runtime path, may be a variable

var e := SCENE.instantiate()                  # PackedScene -> Node
add_child(e)                                  # enters tree, _ready() fires
# To instance with the editor state of exported sub-resources, instantiate() is enough.
```

`instantiate()` フラグ: `PackedScene.GEN_EDIT_STATE_DISABLED` (デフォルト、ランタイム) 対
`GEN_EDIT_STATE_INSTANCE`/`GEN_EDIT_STATE_MAIN` (エディター ツールのみ)。

 ## コードからシーンを保存するときの所有権

 コードでシーンを構築して保存するには、シリアル化するすべてのノードの
`owner` がシーン ルートに設定されている必要があります:

```gdscript
func save_built_scene() -> void:
    var root := Node2D.new()
    var child := Sprite2D.new()
    root.add_child(child)
    child.owner = root                 # without this, child is NOT saved
    var packed := PackedScene.new()
    packed.pack(root)
    ResourceSaver.save(packed, "res://generated.tscn")
```

## シーンの継承

 エディターで、ベース `.tscn` からの「新しい継承シーン」により、
 がベースのノードを継承し、プロパティをオーバーライドしたりノードを追加したりできる子シーンが作成されます。共通の基地を共有する亜種
の敵に役立ちます。ベースへの変更は、継承されたシーンに反映されます。

 ## グループ vs 一意の名前 vs 自動ロード

 - **一意の名前 (`%`)** — *同じシーン* 内の特定のノードを参照します。
- **グループ** — 多くのノードにタグを付け、それらすべてに対して動作します。 `godot-signals-groups`を参照してください。
- **自動ロード** — すべてのシーンにわたって名前でアクセスできる 1 つのグローバル インスタンス。レベルごとのノードではなく、
 サービスとクロスシーン状態に使用します。

 ## 解放と有効性

```gdscript
node.queue_free()                 # safe: deletes at end of current frame
if is_instance_valid(node):       # guard against use-after-free
    node.do_something()
node.free()                       # immediate; only when you control the timing
```

`get_child_count()`、`get_children()`、`move_child(node, idx)`、および
`reparent(new_parent)` (4.x) は、実行時にツリー構造を管理します。 `reparent` は、デフォルトでグローバル
変換を保持します。

 ## 遅延呼び出し

 物理コールバックまたはシグナル ハンドラー中にノードを追加/削除する場合、
 の「クエリのフラッシュ」エラーを回避するために延期してください:

```gdscript
add_child.call_deferred(instance)
node.queue_free()                 # already deferred
```
