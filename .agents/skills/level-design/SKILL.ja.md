---
name: level-design
description: >
  Design and build playable levels — the blockout/whitebox-to-playable workflow,
  player metrics and grid layout, pacing and flow (tension/rest curve), gating
  and the critical path, and encounter design. Engine-neutral practice. Use when
  the user mentions level design, blockout/whitebox/greybox, level layout, level
  pacing, encounter design, or the critical path through a level.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # レベル デザイン

 レベルは、空間を通じて提供される **意図的なエクスペリエンスのシーケンス**です。
良いレベル デザインは *プロセス* です。動きの基礎となるメトリクスを定義し、プリミティブでジオメトリをブロックし、再生してからドレスアップします。決してその逆は行わないでください。この
スキルは、エンジンに依存しない練習です。 `godot-tilemap`/`unity-tilemap-2d` を
に使用して、2D グリッドと 3D のグリッドマップをレイアウトします。

 ##

 を使用する場合 - クリティカル パス、ペーシング、ゲート、エンカウント、
、およびプレイヤーが学習する場所とテストされる場所など、レベルの構造を計画するために使用します。
- **ブロックアウト→テスト→反復→ドレス** ワークフローを使用して、アートが存在する前に
が再生できるレベルを構築します。
- キャラクターの動きからレベル **メトリクス**を導出するために使用します。これにより、ジオメトリが
に到達可能で公平になります。

 **レベルをアルゴリズム的に *生成*するために*使用しない*場合は、`procedural-gen`
(作成された設計と手続き型の設計は補完的です)。エンジンのタイル/グリッド
ペイント ツールの場合は、`godot-tilemap` / `unity-tilemap-2d` を使用します。移動
能力の場合、メトリクスはエンジン移動スキル + `input-systems` から取得されます。

 ## コア ワークフロー

 1. **最初にメトリクスを導き出します。** キャラクターを測定します: 最大ジャンプの高さと距離、
 走行速度、リーチ、カメラの範囲。すべての隙間、出っ張り、廊下のサイズは
単位で決まります。ジオメトリを構築する前にロックしてください。
2. **ブロックアウト (ホワイトボックス/グレーボックス)** テクスチャ化されていない
プリミティブからレベル全体を正しいスケールで構築します。
の変更を安価にしながら、フロー、見通し線、到達可能性を検証します。まだアートはありません。
3. **クリティカル パス** (スタート → ゴール) と、
 ほとんどのプレイヤーが通ると予想される **ゴールデン パス**を定義します。オプション/秘密のパスをその上に重ねます。
4. **経験のペースを調整します。** 意図的なカーブで緊張と休憩を交互に行います。
は戦闘、戦闘、戦闘を実行しません。プレイヤーに息を吹き込み、
 が期待する余地を与えてください。
5. **教えてからテストします。** 安全な場所で各メカニズムを紹介し、プレーヤー
に練習させてから、プレッシャーの下でテストします。 
の直線ではなく、鋸歯状になると難易度が上がります。
6. **意図を持ってゲートします。** ロック/キー、アビリティ、および一方向のドロップを使用して、
 の順序とペースを制御します。壁ではなく、光、線、ランドマークを使ってガイドします。
7. **プレイテストと反復。** 実際のプレイヤーを観察してください。プレイヤーはどこで迷ったり、行き詰まったり、退屈したり、不当に殺されたりするのでしょうか?ブロックアウトを修正します。良いプレーができるときだけ服を着てください。

 ## パターン

 ### 1. プレーヤーの指標があらゆる次元を推進

```gdscript
# Measure the character ONCE, then size geometry in these units. If the jump
# changes, gaps must be re-derived — never eyeball reachability.
const RUN_SPEED      := 240.0   # px/s (or m/s in 3D)
const MAX_JUMP_H     := 96.0    # peak height of a full jump
const MAX_JUMP_DIST  := 200.0   # horizontal distance of a running jump
const SAFE_GAP       := MAX_JUMP_DIST * 0.7   # comfortable, not pixel-perfect
const HARD_GAP       := MAX_JUMP_DIST * 0.95  # a deliberate skill check
# Build platforms so required jumps use SAFE_GAP; reserve HARD_GAP for optional reward.
```

到達可能なレベルは、正直な指標から外れます。 `MAX_JUMP_DIST +
1` away is impossible; one at `SAFE_GAP` に配置されたプラットフォームは公正です。設計者とコードが一致するように、これらの定数を
レベルのデータの横に置いてください。

 ### 2. データとしての遭遇/ペーシング (緊張のタイムライン)

```gdscript
# Author the level as a sequence of beats with an intended intensity (0..1).
# This makes the pacing curve explicit and reviewable before you build rooms.
const BEATS := [
    { "room": "entry",      "type": "teach",   "intensity": 0.1 },
    { "room": "hall_1",     "type": "combat",  "intensity": 0.5 },
    { "room": "vista",      "type": "rest",    "intensity": 0.1 },  # breather + reward
    { "room": "gauntlet",   "type": "combat",  "intensity": 0.8 },
    { "room": "save_room",  "type": "rest",    "intensity": 0.2 },  # before the boss
    { "room": "boss",       "type": "climax",  "intensity": 1.0 },
]
# Read the intensity column top-to-bottom: it should rise overall but dip for rests
# (a sawtooth), never flatline high. Drive spawns/music intensity from this.
```

### 3. ゲートとクリティカル パス (小さなグラフ)

```gdscript
# Model the level as rooms + gated connections. Validate that the goal is
# reachable with the keys/abilities the player can actually obtain in order.
const ROOMS := {
    "entry":   { "exits": [ { "to": "hall_1" } ] },
    "hall_1":  { "exits": [ { "to": "vista", "needs": "double_jump" },
                            { "to": "side_room" } ] },           # optional branch
    "side_room": { "exits": [ { "to": "hall_1" } ], "grants": "double_jump" },
    "vista":   { "exits": [ { "to": "boss", "needs": "red_key" } ] },
}
# Validation (do this!): from "entry", can the player reach "boss" given that
# "double_jump" is granted in "side_room" before "vista" requires it? A flood
# fill that only traverses an exit when its `needs` is already satisfiable
# proves the critical path isn't soft-locked.
```

## 落とし穴

 - **プレイ前にドレスアップ。** 検証していないブロックアウトの詳細を説明すると、変更するレイアウトで最もコストのかかる作業が
無駄になります。最初にグレーボックスとテストを行ってください。
- **メトリクスを無視するジオメトリ**: ジャンプでクリアできないギャップ、
 が届く下の棚、カメラが必要とするよりも狭い廊下。すべてをプレーヤー単位でサイズ設定します。
- **フラットなペース。** 壁から壁への戦闘 (または壁から壁への静けさ) はプレイヤーを麻痺させます。
緊張と休息を交互に繰り返します。クライマックスの前に一息入れてセーブします。
- **教える前にメカニックをテストします。** プレイヤーは、致命的な場所で
で初めて危険に遭遇します。安全に導入し、練習させてからテストします。
- **ソフトロックと行き止まり** ゲートには、
 ゲートを通過した後にのみ取得できる能力/キーが必要です。接続性だけでなく、クリティカル パスのキー/機能の順序を検証します。
- **読みやすさやガイダンスがありません。** プレイヤーは何も目を引くものがないと道に迷ってしまいます。
ライト、誘導線、色、ランドマークを使用してパスを指します。
- **標識のない一方通行のドロップ** ストランドやプレイヤーを驚かせます。 Telegraph
不可逆的な動き。
- **プロシージャルとオーサリングの混同。** 生成は、
 オーサリングのペースではなく、多様性を与えます。さまざまな場合は `procedural-gen` を使用します。意図のために手書きで作成します。

 ## 参考文献

 - `references/pacing-and-flow.md` — 難易度/張力曲線の詳細、
 ティーチング ループ設計 (導入→開発→ツイスト→テスト)、可読性とガイダンス
テクニック、2D 対 3D レイアウトの考慮事項、およびブロックアウトのレビューチェックリスト。

 ## 関連スキル

 - `godot-tilemap`、`unity-tilemap-2d` — 2D レベル グリッドをペイントします。 3D 用のグリッドマップ。
- `procedural-gen` — 作成された構造を補完する多様性を生成します。
- `game-ai` — 構築した空間を移動する敵に遭遇します。
- `platformer`、`puzzle`、`roguelike` — このスキルを構成するジャンル。 
