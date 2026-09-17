# ローグライク生成、FOV、戦利品 (深度)

 `SKILL.md` のシステムの背後にあるアルゴリズム。エンジン中立の疑似コード。ノイズ/RNG
プリミティブとシードについては、`procedural-gen` を参照してください。このファイルはローグライク固有の接着剤です。

 ## 1. ダンジョン生成は

 必要な *テクスチャ* で選択します。すべては **接続パス** で終わる必要があります (§2)。

 ### 部屋と廊下 (クラシック、読みやすい)

```python
# Place non-overlapping rooms, then connect their centers with L-shaped tunnels.
rooms = []
for _ in range(MAX_ROOMS):
    r = random_rect(rng, min=4, max=10)
    if any(r.intersects(other.expand(1)) for other in rooms):
        continue                      # reject overlaps (expand by 1 to keep walls between)
    carve_room(map, r)
    if rooms:                         # connect to the previous room
        carve_h_then_v(map, rooms[-1].center, r.center, rng)
    rooms.append(r)
# First room = player spawn; last/farthest room = stairs down.
```

### BSP (バイナリ空間パーティション — きちんとした、建物のような)

 マップの四角形を再帰的にサブ四角形に分割します。リーフごとに 1 つの部屋を配置します。再帰を解きながら、
 兄弟ルームを接続します。均等に配置された、重なり合わない部屋を生成します。

 ### セルラー オートマトン (有機洞窟)

```python
# Random fill, then smooth: a cell becomes wall if most neighbors are walls.
fill_random(map, wall_chance=0.45, rng=rng)
for _ in range(4, 6):                 # 4–6 smoothing passes
    for cell in map:
        walls = count_wall_neighbors(map, cell)   # 8-neighborhood
        map[cell] = WALL if walls >= 5 else FLOOR
# Then keep only the largest connected floor region (discard isolated pockets).
```

### 酔っぱらいの散歩 (安くて曲がりくねった)

 ある点から開始し、目標のフロア パーセンテージに達するまでランダム ウォークでフロアを刻みます。
確実に接続されています (1 つの連続したパス) が、調整しないと不安定すぎる可能性があります。

 ## 2. 接続 (絶対にスキップしないでください)

```python
# Flood-fill from the player's start; any walkable cell not reached must be connected or removed.
reached = flood_fill(map, player_start)
regions = find_disconnected_floor_regions(map, reached)
for region in regions:
    carve_corridor(map, nearest_cell(reached), nearest_cell(region), rng)
# Re-flood and assert: every floor cell is now reachable.
```

洞窟の場合、一般的な近道は、単一の最大領域のみを保持し、残りを破棄することです。

 ## 3. 視野 — 対称シャドウキャスト

 必要なプロパティ: **対称** (A から B が見え、B から A が見える)、死角なし、
 プレーヤーの移動時のちらつきなし。再帰的シャドウキャスティングは、原点の周囲の 8 つの八分円をスキャンし、壁によって遮られた斜面の
「影」を追跡します:

```
for each of 8 octants:
    scan rows outward from the origin up to radius R
    track the visible slope range [start_slope, end_slope]
    when a wall is hit, recurse into the narrower slope range beyond it,
    and continue the current row with the reduced range
mark a cell visible if it lies within the current slope range and within R
```

実装メモ:
- 各八分円を共通の座標枠に変換し、1 つのルーチンで 8 つすべてを処理できるようにします。
- 正方形ではなく丸いライトには円形半径チェック (`dx*dx + dy*dy <= R*R`) を使用します。
- `explored` を個別にキャッシュします。探索されているが表示されていないセルを淡色表示します。

 対称バリアント (「対称シャドウキャスティング」) は推論が簡単で、
 単一セルの非対称性を回避します。スクラッチから実装する場合はそれをお勧めします。

 ## 4. 重み付けされた深さスケールの戦利品およびスポーン テーブル

```python
# A drop table is a list of (entry, weight). Weight is relative, not a probability.
goblin_loot = [
    ("nothing",      60),
    ("gold_small",   25),
    ("healing_potion", 10),
    ("rare_scroll",   5),
]
def roll(table, rng):
    total = sum(w for _, w in table)
    pick  = rng.range(0, total)        # [0, total)
    upto  = 0
    for entry, w in table:
        upto += w
        if pick < upto:
            return entry

# Depth scaling: shift weights toward stronger entries as depth increases,
# e.g. add depth-gated entries or multiply rare weights by a depth factor.
```

デザイン ガイダンス:
- レアがエキサイティングであり続けるように、重量の大部分として「何も」/コモンを維持します。
- 強力なアイテムを最小限の深さの後ろにゲートして、初期のランが雪だるま式に行われないようにします。
- **monster** スポーン テーブルと **item** ドロップ テーブルを分離します。どちらも深さに応じてスケールします。
- 「正確に 1 つ」の結果については、重み付き選択を使用します。 「それぞれがドロップする可能性がある」ため、独立したロールが繰り返されます。

 ## 5. 実行状態とプロファイル状態 (パーマデス + メタ進行)

 - **実行状態** (現在のダンジョン、HP、インベントリ、シード): 実行中のみ有効です。 *true*
permadeath の場合、ロードされた瞬間にこのセーブを削除または無効にして、再ロードできないようにします。
- **プロファイル状態** (ロック解除されたアイテム/クラス、ハイスコア、実績、通貨): 死亡しても
が持続します。これはローグライトがメタプログレッションに費やす金額です。
- 実行をワイプしてもプロファイルに触れないように、それらを別のファイル/セクションに保存します (スロット/バージョン管理の詳細については、
 `save-systems` を参照してください)。 
