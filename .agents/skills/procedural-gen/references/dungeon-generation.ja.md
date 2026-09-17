# ダンジョンとレベルの生成

 3 つのファミリーでほとんどの 2D レベルの生成をカバーします。すべては、後でタイル パスがレンダリングするプレーン グリッド
(`0 = wall`、`1 = floor`) に書き込みます。すべてがシードされた RNG を取得します。

 ## A. 部屋と廊下

 シンプルで読みやすく、認識しやすい部屋を提供します。長方形を配置して接続します。

```python
def generate(W, H, rng, attempts=200, rmin=4, rmax=9):
    grid = [[0]*W for _ in range(H)]          # 0 = wall
    rooms = []
    for _ in range(attempts):
        w = rng.randint(rmin, rmax); h = rng.randint(rmin, rmax)
        x = rng.randint(1, W - w - 1); y = rng.randint(1, H - h - 1)
        new = (x, y, w, h)
        if any(_overlap(new, o, pad=1) for o in rooms):
            continue                          # keep at least one tile between rooms
        _carve_room(grid, new)
        if rooms:                             # connect to the previously placed room
            (cx, cy), (px, py) = _center(new), _center(rooms[-1])
            _carve_h(grid, px, cx, py)        # horizontal leg
            _carve_v(grid, py, cy, cx)        # vertical leg -> L-shaped corridor
        rooms.append(new)
    return grid, rooms
```

「部屋をチェーンする」よりも興味深い接続を実現するには、中心の
最小スパニング ツリーを介して部屋を接続し、ループ用の追加のエッジをいくつか追加します。

 ## B. BSP (バイナリ空間分割)

 空間を再帰的に分割し、部屋が重なり合ってマップを並べて表示しないことを保証します。構造化された建物のようなダンジョンに適した 
。

```python
def bsp(node, rng, depth, min_size=8):
    if depth == 0 or (node.w < min_size*2 and node.h < min_size*2):
        node.room = _random_room_inside(node, rng)   # leaf: place one room
        return
    if node.w > node.h:                               # split the longer axis
        cut = rng.randint(min_size, node.w - min_size)
        left, right = node.split_vertical(cut)
    else:
        cut = rng.randint(min_size, node.h - min_size)
        left, right = node.split_horizontal(cut)
    bsp(left, rng, depth-1, min_size); bsp(right, rng, depth-1, min_size)
    node.children = (left, right)
    _connect(left.room_or_subroom(), right.room_or_subroom(), rng)  # join siblings
```

再帰の巻き戻し時に兄弟を接続するため、すべての領域が兄弟
にリンクされ、ツリー全体が接続されたままになります。

 ## C. ランダムウォーク / セルラー洞窟

 有機的な洞窟。酔っ払いの散歩で彫るか、シードノイズでセルオートマトンで
を滑らかにします。

```python
# Drunkard's walk: a digger wanders, carving floor, until enough is open.
def drunkard(W, H, rng, target_ratio=0.45):
    grid = [[0]*W for _ in range(H)]
    x, y = W//2, H//2; carved = 0; goal = int(W*H*target_ratio)
    while carved < goal:
        if grid[y][x] == 0: grid[y][x] = 1; carved += 1
        x = clamp(x + rng.choice([-1,0,1]), 1, W-2)   # random step, stay in bounds
        y = clamp(y + rng.choice([-1,0,1]), 1, H-2)
    return grid

# Cellular automata smoothing: a cell becomes wall if most neighbors are walls.
def smooth(grid, W, H, steps=4):
    for _ in range(steps):
        new = [row[:] for row in grid]
        for y in range(1, H-1):
            for x in range(1, W-1):
                walls = sum(1 for dy in (-1,0,1) for dx in (-1,0,1)
                            if grid[y+dy][x+dx] == 0)
                new[y][x] = 0 if walls >= 5 else 1   # 5/9 majority rule
        grid = new
    return grid
```

## 接続検証 (毎回実行)

 生成では領域を分離できます。スポーンからのフラッドフィル。床タイルが
に到達しないままの場合は、マップを破棄するか、最も近い到達タイルまでトンネルを掘るか、
 が最大の領域のみを保持します。

```python
def reachable_floor(grid, start):
    seen, stack = set(), [start]
    while stack:
        x, y = stack.pop()
        if (x, y) in seen or grid[y][x] == 0: continue
        seen.add((x, y))
        stack += [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    return seen        # compare len(seen) to total floor count; reconnect the rest
```

また、スポーンから終了までのパスが存在すること (`game-ai` A* を再利用)、スポーン
タイルが安全であること、キー アイテムがそれ自体でゲートされているロックの背後にないことも検証します。

 ## 戦利品/スポーンの分配制御

 純粋な加重ロールはストリーク (連続 10 個のコモン) を生成します。 2 つの修正:

 - **バッグ/デッキ**: 重量に比例してアイテムをバッグに詰め、シャッフルし、交換せずに
を描画し、空になったら補充します。窓越しの料金を保証します。
- **残念なタイマー**: 最後のレア以降のトラックロール。しきい値を超えると、
 はレアのチャンスを強制またはブーストします。ガチャ/戦利品システムで一般的です。

 これらをシードされた RNG にも保持して、ドロップ シーケンスの再現性を維持します。 
