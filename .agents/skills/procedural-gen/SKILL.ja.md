---
name: procedural-gen
description: >
  Generate game content procedurally — seeded deterministic RNG, value/Perlin/
  Simplex noise for terrain and heightmaps, grid dungeon generation (rooms +
  corridors, BSP, random walk), and weighted loot/drop tables. Engine-neutral
  algorithms. Use when the user mentions procedural generation, perlin/simplex
  noise, random seed, dungeon generator, heightmap/terrain, or loot tables.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # 手続き型生成

 コンパクトなルールとシードからレベル、地形、戦利品を生成します。優れた procgen のスルーライン
は **決定論** です。単一のシードが同じ世界を再現するため、
 のバグは再現可能であり、プレイヤーはシードを共有できます。このスキルは、コア
アルゴリズム (ノイズ、シードされた RNG、ダンジョン レイアウト、加重テーブル) を所有します。
`roguelike` や `survival-crafting` などのジャンルがそれを消費します。

 ##
を使用する場合
- マップ、ダンジョン、地形ハイトマップ、アイテム ドロップ、または手動で作成したくないコンテンツ
を生成するために使用します。
- 結果が **シードから再現可能**である必要がある場合に使用します (デバッグ、毎日の
チャレンジ、共有可能なワールド)。
- 重み付けされたランダムな結果 (戦利品のレア度、スポーン テーブル) を選択するために使用します。

 **使用しない*場合:** エンジンのタイル API で結果を *ペイント*するには、
 `godot-tilemap` または `unity-tilemap-2d` を使用します。生成されたマップを通じて AI をルーティングするために、
 は `game-ai` を使用します。注意深く手動でペースを進めるレベルの場合は、`level-design` を使用してください。procgen と
で作成されたデザインは補完的であり、互換性はありません。

 ## コア ワークフロー

 1. **ランダム性を所有します。** シードされた RNG インスタンスを 1 つ作成し、それをあらゆる場所に
渡します。生成コードではグローバル/静的ランダムを決して呼び出さないでください。これにより、
 の結果が再現不可能になり、順序に依存します。
2. **コンテンツのテクニックを選択します。** 連続地形/高さマップ → ノイズ。
個別の部屋/廊下 → 空間分割またはエージェントベースのカービング。
レアリティによる結果 → 加重テーブル。
3. **最初にプレーン データ グリッド/配列を生成**し、レンダリングから切り離します。
生成により、`int[][]` または辞書が埋められます。別のパスで描画されます。
4. **結果をプレーヤーに送信する前に検証します。** すべての部屋
は到達可能ですか?スポーンは安全ですか？出口への道はあるのか？失敗した
レイアウトを拒否または修復します。プレイヤーに壊れた地図を渡さないでください。
5. **シードを固定して調整**すると、各パラメーターの変更が個別に表示されます。その後、
 でシードをスイープして、1 つのラッキー マップだけでなく、分布を確認します。

 ## パターン

 ### 1. シードされた決定論的 RNG (基礎)

```python
import random
rng = random.Random(seed)        # a dedicated instance — NOT the global random.*
room_count = rng.randint(5, 12)  # same seed -> same sequence, every run
# RIGHT: thread `rng` through every function that makes a choice.
# WRONG: calling random.randint(...) (global state) — order-dependent, unseedable.
```

同等のエンジン: Godot `var rng = RandomNumberGenerator.new(); rng.seed = s`;
ユニティ `var rng = new System.Random(seed)` (または `UnityEngine.Random.InitState`)。
ワールドを再生成できるように、シードを保存ファイルに保存します。

 ### 2. ハイトマップのフラクタル (fBm) ノイズ

```python
# Sum several octaves: each higher octave has higher frequency, lower amplitude.
def fbm(noise, x, y, octaves=5, lacunarity=2.0, gain=0.5):
    total, amp, freq, norm = 0.0, 1.0, 1.0, 0.0
    for _ in range(octaves):
        total += amp * noise(x * freq, y * freq)   # noise() returns ~0..1
        norm  += amp                                # track total amplitude
        amp   *= gain                               # each octave contributes less
        freq  *= lacunarity                         # ...at a higher frequency
    return total / norm                             # normalize back into 0..1

# Redistribute to carve flat valleys / sharpen peaks: higher exp -> more lowland.
elevation = pow(fbm(noise, nx, ny), 2.2)
```

実際のノイズ ライブラリ (`FastNoiseLite`、`opensimplex`、
 `Unity.Mathematics.noise`、または `Mathf.PerlinNoise`) を使用します。勾配
ノイズを自分で実装しないでください。種子 **異なる種子の標高と水分**のため、両方のフィールドに対する
バイオーム ルックアップは完全には相関していません。完全なバイオーム検索と
島の整形は `references/noise.md` にあります。

 ### 3. 加重戦利品テーブル (レアリティに応じた選択)

```python
# Roll proportional to weight: common drops far more often than legendary.
def weighted_pick(rng, table):           # table: list of (item, weight)
    total = sum(w for _, w in table)
    roll = rng.uniform(0, total)          # a point on the cumulative line
    upto = 0.0
    for item, w in table:
        upto += w
        if roll < upto:                   # first bucket the roll falls into
            return item
    return table[-1][0]                   # float-safety fallback

loot = weighted_pick(rng, [("common", 70), ("rare", 25), ("legendary", 5)])
```

重みは相対的なものなので、合計が 100 になる必要はありません。悪いストリークを防ぐには、
 "pity"/bag システムを使用してください (ディストリビューションに関する `references/dungeon-generation.md` の注意事項を参照)。

 ### 4. 部屋と廊下のダンジョン (スケッチ)

```python
# 1. Place non-overlapping rooms; 2. connect them; 3. carve into the grid.
rooms = []
for _ in range(attempts):
    r = Rect(rng.randint(1, W-w-1), rng.randint(1, H-h-1), w, h)
    if not any(r.intersects(o.expand(1)) for o in rooms):  # keep a 1-tile gap
        rooms.append(r)
for a, b in zip(rooms, rooms[1:]):       # connect each room to the next
    carve_l_corridor(grid, a.center, b.center, rng)   # horizontal then vertical
```

完全なジェネレーター (BSP 分割、L 回廊、到達可能性チェック、および
ランダム ウォーク ケーブ) は `references/dungeon-generation.md` にあります。

 ## 落とし穴

 - **生成内でグローバル RNG を使用**するとワールドが再現できなくなり、呼び出し順序が変更された瞬間に
が中断されます。常にシードされたインスタンスを渡します。
- **相関ノイズ フィールド**: *同じ*
シード/オフセットから標高と水分をサンプリングすると、バンド状に並ぶバイオームが生成されます。各フィールドをオフセットまたは再シードします。
- **オクターブ アーティファクト**: 再正規化せずにオクターブを追加すると、値が
`0..1` からプッシュされます。合計された振幅で除算します (ライブラリの出力範囲に注意してください。一部の
は `-1..1` を返し、一部の `0..1` を返します)。
- **接続チェックなし**: 部屋や洞窟が孤立してしまう可能性があります。
からスポーンし、再生前に到達不能な領域を破棄/再接続してからフラッドフィルします。
- **無制限の配置ループ**: 「N 部屋が収まるまで試行し続ける」は、小さなグリッド上で
を永遠に回転させることができます。試行を制限し、受け入れられる部屋の数を減らします。
- **グローバルに一度シードし、その後フレーム タイミングに依存**: 生成に漏れる非決定的な
入力 (時間、物理学、ハッシュのランダム化) は、
 の再現性を破壊します。

 ## 参照

 - `references/noise.md` — オクターブ/ラクナリティ/ゲイン、再分配、アイランド
シェーピング、2 軸バイオーム ルックアップ、ブルー ノイズ オブジェクト スキャッター。
- `references/dungeon-generation.md` — BSP、部屋+廊下、ランダム ウォーク洞窟、
 セル オートマトン スムージング、接続検証、分布/同情テーブル。

 ## 関連スキル

 - `godot-tilemap`、`unity-tilemap-2d` — 生成されたグリッドをエンジンにペイントします。
- `game-ai` — 生成されたグラフ上のパスファインディング。
- `level-design` — procgen が補完するペーシングと手書きの構造。
- `roguelike`、`survival-crafting` — このスキルを構成するジャンル。 
