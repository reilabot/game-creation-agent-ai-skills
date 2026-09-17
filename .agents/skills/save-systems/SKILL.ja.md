---
name: save-systems
description: >
  Design save/load for game state — choosing what to serialize, file formats,
  save slots, atomic crash-safe writes, schema versioning and migration, and
  autosave. Engine-neutral. Use when the user mentions save system, save/load,
  game state persistence, save slots, autosave, save file corruption, or
  migrating old saves to a new version.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # セーブ システム

 セーブ ファイルは、再起動しても存続する **ゲーム状態のシリアル化されたスナップショット**です。
ハード部分はバイトの書き込みではありません。保存する *何を*選択し、保存中のクラッシュによって破損しないように
に書き込み、
 パッチを配布した後に *古い* セーブを読み取ります。この 3 つを正しく設定すれば、残りは配管です。

 ##

 を使用する場合 - セッションおよびゲーム更新全体にわたって、プレイヤーの統計、インベントリ、世界の国旗、設定、
 の位置などの進行状況を保持するために使用します。
- 保存スロット、クイック保存/自動保存、およびクラッシュ セーフ書き込みの設計に使用します。
- コンテンツ/コード変更 (バージョン管理と
移行) 後に古い保存ファイルが壊れた場合に使用します。

 **使用しない*場合:** Roblox クラウド永続性の詳細には、
 `roblox-datastores` を使用します。保存がシリアル化するデータ モデル (リソース/SO) には、
 `godot-resources` / `unity-scriptableobjects` を使用します。 Godot の `FileAccess`/
`ResourceSaver` および `user://` パスについては、
 がここでパターンを適用している間、Godot エンジン スキルに従います。

 ## コア ワークフロー

 1. **どの状態が権限があるかを決定します。** エンジン オブジェクトやシーン ノードではなく、*データ* (hp、位置、シード、
 ロック解除フラグ) を保存します。ロード時にデータから
オブジェクトを再構築します。ライブ ノード参照をシリアル化しないでください。
2. **バージョン管理されたスキーマを定義します。** すべての保存には、`version` 整数が埋め込まれます。これは
で、パッチを適用するゲームにとって最も重要なフィールドです。
3. **形式を選択します。** 読みやすさとデバッグしやすさを考慮して JSON/テキスト。サイズ/速度または軽度の耐タンパー性のためのバイナリ
形式。 JSON から始めます。
4. **アトミックに書き込みます。** 一時ファイルにシリアル化してフラッシュし、その後、
 実際のファイルに名前を変更します。クラッシュすると、古いセーブデータか新しいセーブデータが残ります。
 が書きかけのセーブデータになることはありません。
5. **防御的にロードします。** バージョンを読み取り、現在のバージョンに移行し、検証し、
 をインスタンス化します。最後に正常に保存したときのバックアップを保持し、解析エラーが発生した場合にフォールバックします。
6. **安全な境界で自動保存** (レベル変更、チェックポイント)、調整され、
 の別のスロットに保存されるため、手動保存を妨げることはありません。
7. **確認**: 保存、完全に終了、再起動、ロード — 検査によって
状態が一致することを確認します。以前のバージョンからセーブデータをロードしてテストします。

 ## パターン

 ### 1. 状態をプレーン データ (エンジン オブジェクトではない) としてシリアル化する

```gdscript
# Build a dictionary of pure data. Each savable object reports its own state.
func capture_state() -> Dictionary:
    return {
        "version": SAVE_VERSION,                 # ALWAYS stamp the schema version
        "player": { "hp": player.hp, "pos": [player.position.x, player.position.y] },
        "inventory": player.inventory.to_array(),  # ids + counts, not Item nodes
        "flags": world.flags,                    # e.g. {"met_guard": true}
        "seed": world.seed,                      # regenerate procedural content
    }

# On load, RECONSTRUCT objects from the data — do not expect live references back.
func apply_state(data: Dictionary) -> void:
    player.hp = data["player"]["hp"]
    player.position = Vector2(data["player"]["pos"][0], data["player"]["pos"][1])
    player.inventory.from_array(data["inventory"])
    world.flags = data["flags"]
```

### 2. アトミックでクラッシュセーフな書き込み (一時 + 名前変更)

```gdscript
# RIGHT: write to a temp file, then atomically rename over the target.
func save_atomic(path: String, data: Dictionary) -> void:
    var tmp := path + ".tmp"
    var f := FileAccess.open(tmp, FileAccess.WRITE)
    f.store_string(JSON.stringify(data))
    f.flush()                                    # ensure bytes hit disk
    f.close()
    DirAccess.rename_absolute(tmp, path)         # replaces the target; atomic on POSIX
# WRONG: opening `path` directly and writing in place — a crash mid-write leaves a
# truncated, unloadable save and destroys the player's progress.
```

Rename-over-target は POSIX (同じボリューム) ではアトミックです。 Windows では、名前変更による置換
はアトミックであることが保証されていないため、
 の名前変更の前に、前のファイルを `path + ".bak"` として保持してください。そのバックアップにより、不正な書き込みから回復できることが実際に保証されます。

 ### 3. 移行によるバージョン管理されたロード

```python
SAVE_VERSION = 3

def load_save(raw_bytes):
    data = parse(raw_bytes)                  # JSON/binary -> dict
    v = data.get("version", 0)
    if v > SAVE_VERSION:
        raise NewerSaveError(v)              # save is from a newer build; refuse
    while v < SAVE_VERSION:                   # apply migrations in order, v -> v+1
        data = MIGRATIONS[v](data)
        v += 1
        data["version"] = v
    validate(data)                            # check required keys / ranges
    return data

# Each migration is a pure function from one version's shape to the next.
def migrate_1_to_2(d):
    d["flags"] = {k: True for k in d.pop("completed_quests", [])}  # list -> set-map
    return d
MIGRATIONS = {1: migrate_1_to_2, 2: migrate_2_to_3}
```

### 4. スロットの保存 + 調整された自動保存

```gdscript
const SLOT_PATH := "user://save_%d.json"      # manual slots 0..N
const AUTOSAVE_PATH := "user://autosave.json"  # separate file: never clobbers a slot
var _autosave_cooldown := 0.0

func autosave_if_due(dt: float) -> void:
    _autosave_cooldown -= dt
    if _autosave_cooldown <= 0.0:
        save_atomic(AUTOSAVE_PATH, capture_state())
        _autosave_cooldown = 60.0             # throttle: at most once a minute
# Trigger an immediate autosave on checkpoints/level transitions, not mid-combat.
```

## 落とし穴

 - **エンジン オブジェクト/ノード パスのシリアル化** はシーン構造に保存されます。
ノードの名前を変更すると、古い保存はすべて壊れます。データを保存し、ロード時にオブジェクトを再構築します。
- **バージョン フィールドなし。** パッチを出荷する日は、既存のすべての保存が
推測ゲームになります。バージョン 1 の `version` をスタンプします。
- **インプレース書き込み** 破損により、クラッシュや電源喪失が防止されます。常に一時書き込みを行ってから、
 で名前を変更します。 `.bak` を保持します。
- **ファイルを盲目的に信頼します。** 保存が切り捨てられたり、手動で編集されたり、
 クラウド同期されたりして古くなります。負荷時に検証し、障害が発生した場合はバックアップに戻ります。
- **浮動小数点数とロケール** テキスト シリアライザーは、一部のロケールでは精度を落としたり、カンマ
小数点区切り文字を使用したりすることがあります。ロケール不変のシリアライザーを使用します。
- **手動保存を自動保存する**、またはアクション中に起動して
の不整合な状態を保存します。専用の自動保存スロットを使用して、安全な境界で保存します。
- **マルチプレイヤーでのシークレットの保存またはクライアント セーブの信頼** ローカル セーブは
プレイヤーによって制御されます。それをオンライン状態に対して権威のあるものとして決して扱わないでください。クラウドの場合、
 はデバイスのデータ制限と競合 (`roblox-datastores`) を処理します。

 ## 参照

 - `references/versioning-and-migration.md` — スキーマ進化戦略、
 移行チェーン、バックアップ/ロールバック、形式のトレードオフ (JSON とバイナリ)、および
ロード時間検証チェックリスト。

 ## 関連スキル

 - `roblox-datastores` — クラウド永続性、リクエスト制限、セッション ロック。
- `godot-resources`、`unity-scriptableobjects` — シリアル化するデータ モデル。
- `procedural-gen` — ワールドを保存するのではなく、シードを保存して再生成します。
- `rpg`、`survival-crafting`、`visual-novel` — このスキルを構成するジャンル。 
