---
name: platformer
description: >
  Build a 2D platformer: run/jump control with coyote time, jump buffering, and variable jump
  height, plus tiled levels and hazards. Use for a platformer or Mario/Celeste-like, or tuning jump feel.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # プラットフォーマー

 2D プラットフォーマー用のプレイブック — ラン/ジャンプ コントローラーの「感触」、レベル構造、危険、
、目標。これは**構成**スキルです。エンジン動作スキル、タイルマップ
スキル、デザイン スキルを実際に動作するゲームに結び付けます。物理学やタイルマップを再教育するものではありません**。
何を構築するか、ジャンプを気持ちよくする方法を教えてくれます。

 ##

 を使用する場合 - 横スクロールまたは単一画面のプラットフォーマー、「マリオのような」/
「セレステのような」ゲーム、または**サーフェス間のジャンプ**が中心動詞であるゲームを構築する場合に使用します。
- ジャンプが浮いている、反応しない、または「不公平」であると感じ、感触を修正する必要がある場合に使用します。
(コヨーテタイム、ジャンプバッファリング、可変高さ、コーナー補正)。

 **使用しない場合:** 無重力でのトップダウン移動 → エンジン移動スキル
を直接使用します。 3D 一人称トラバース → `fps-shooter`。グリッド/ターン移動→`roguelike`。
生のキネマティック ボディ API の場合は、`godot-2d-movement` (またはエンジンのコントローラー スキル) を使用します。

 ## コア ループ

 **ギャップ/危険を観察 → ジャンプまたは移動にコミット → 安全に着地 (または死亡) → 次の
チェックポイント/ゴールに到達。** プラットフォーマーは、その 1 つの
ジャンプの * 瞬間から瞬間* の感触に生も死も関係なく、何千回も繰り返されます。まずコントローラーを締めます。それ以外はすべて内容です。

 ## 必須システム

 1. **ラン/ジャンプ コントローラー** — 水平加速/減速、重力、ジャンプ、以下の感覚補助を使用します。
2. **固体 + 一方向衝突** — 地面、壁、および「ジャンプスルー」プラットフォーム。
3. **レベル ジオメトリ** — タイルマップまたは手動で配置されたコライダー。遊べるスペース。
4. **ハザード + 死亡/リスポーン** — スパイク、ピット、敵。最後のチェックポイントにリセットされます。
5. **チェックポイント / レベル目標** — 進行状況マーカーと勝利条件 (フラグ、ドア、出口)。
6. **カメラ** — レベル境界に固定されたデッドゾーンと先読みでプレイヤーを追跡します。
7. **ジュース** — 着地ダスト、スカッシュ/ストレッチ、ヒットストップ、サウンド。安くて大きな見返りを感じます。

 ## デザイン ノブ (ジャンプの感触を正しくする)

 生の数値ではなく、**結果** (タイル単位の高さ、頂点までの時間 (秒)) によってこれらを調整します。
|
|ノブ |効果 |健全な出発点 |
|------|--------|---------------------|
|最大ジャンプ高さ |リーチ | 3 ～ 4 タイル |
|頂点への時間 | 「重さ」/軽快さ | 0.30 ～ 0.40 秒 |
|落下重力乗数 |キビキビとした、浮かないフォール | 1.5～2.0×上昇重力 |
|コヨーテの時間 |棚を出た直後にジャンプ | 0.08 ～ 0.12 秒 (約 5 ～ 7 フレーム @60) |
|ジャンプバッファ |着地直前に押すとまだジャンプします | 0.10 ～ 0.15 秒 |
|可変ジャンプカット |タップ = ショートホップ、長押し = フル |リリース時に上向き速度を0.4～0.5倍カット |
|アペックスハング |空気制御のために上部にある短いフロート | `|vy|`<しきい値 | 付近で重力を 0.5 減少させます。
|接地加速/摩擦 |反応性と氷の比較 | 0.05 ～ 0.1 秒で最高速度に到達 |
|角補正 | 1 ～ 2 ピクセル切り取られた出っ張りを少しずつ通過する |横に最大 4 ピクセルまで微調整 |

 推測ではなく *感触* 値から重力とジャンプ速度を導き出します — パターン 1 を参照。

 ## パターン

 ### 1. 高さ + 時間 (マジックナンバーではない) からジャンプの物理を解く

```python
# Pseudocode. Pick the FEEL you want, then derive the physics. y-axis points DOWN.
# From kinematics: h = (g * t^2) / 2  and  v0 = g * t.
JUMP_HEIGHT   = 3.5 * TILE      # how high, in world units
TIME_TO_APEX  = 0.35            # seconds to reach the top

gravity       = (2 * JUMP_HEIGHT) / (TIME_TO_APEX ** 2)   # rising gravity
jump_velocity = -(2 * JUMP_HEIGHT) / TIME_TO_APEX         # negative = upward
fall_gravity  = gravity * 1.8   # heavier on the way down → less floaty
```

### 2. コヨーテタイム + ジャンプバッファ + 可変高さ (フィールコア)

```python
# Pseudocode in the per-frame update. dt = seconds since last frame.
# Timers count DOWN; refresh coyote while grounded, buffer on a fresh press.
if on_floor:
    coyote_timer = COYOTE_TIME           # 0.1
if jump_pressed_this_frame:
    buffer_timer = JUMP_BUFFER           # 0.12
coyote_timer -= dt
buffer_timer -= dt

# A jump is allowed if we pressed recently AND were grounded recently.
if buffer_timer > 0 and coyote_timer > 0:
    velocity.y   = jump_velocity
    buffer_timer = 0
    coyote_timer = 0                     # consume both so we can't double-jump

# Variable height: releasing jump early while still rising cuts the arc short.
if jump_released_this_frame and velocity.y < 0:
    velocity.y *= 0.45

# Asymmetric gravity: snappier fall than rise.
g = fall_gravity if velocity.y > 0 else gravity
velocity.y += g * dt
```

### 3. 一方通行ホーム

 上からはしっかり、下からはパススルー。ほとんどのエンジンは、タイル/コライダーの
に「一方向衝突」フラグを公開します。これを有効にし、プレイヤーが Down + Jump を押したときに数フレームの間衝突
を無効にすることで、プレイヤーが**ドロップスルー**できるようにします。衝突計算を再実装しないでください。

 ## 落とし穴 / 障害モード

 - **フレームごとの動きは `dt` によってスケールされません** → 速度はフレーム レートによって変化します。すべての速度
統合とタイマーでは `dt` を使用する必要があります。 (`physics-tuning` を参照。)
- **ふわふわジャンプ** → 対称重力。落下重力を上昇重力よりも重くします。
- **「ジャンプが登録されませんでした」** → 入力バッファリングがありません。バッファは着地前に約 0.1 秒間押します。
- **「落ちてジャンプできませんでした」** → コヨーテタイムはありません。地面から離れた後、約 0.1 秒間ジャンプできるようにします。
- **壁に張り付く/タイルの継ぎ目に引っかかる** →
タイルごとのコライダーではなく、単一のカプセル/ボックス コライダーを使用し、コーナー補正を追加します。
- **高速でフロアをトンネルする** → 連続衝突を有効にする / 高速ボディの固定
タイムステップを小さくします (`physics-tuning` を参照)。
- **カメラがスナップして吐き気を引き起こす** → フォローをスムーズ/ラープし、デッドゾーンを追加し、境界にクランプします。
- **間違った教えによる困難の壁** → 組み合わせる前にエリアごとに 1 つのメカニズムを導入します。

 ## 構成 (これらのスキルから構築)

 - **コントローラー本体:** `godot-2d-movement` (Godot `CharacterBody2D`);他のエンジンの場合は、
 エンジン コア + 物理スキル (`unity-physics`、`phaser-arcade-physics`、`pygame-core`) を使用します。
- **レベル:** ジオメトリの場合は `godot-tilemap` / `unity-tilemap-2d`。レイアウト、
 ペーシング、およびティーチング順序の `level-design`。
- **感触/物理学:** タイムステップ、CCD、安定性用の `physics-tuning`。
- **入力:** バッファリング、再バインド、およびゲームパッドのサポート用の `input-systems`。
- **ポーランド語:** `audio-design` (SFX/音楽用)。スカッシュ/ストレッチ用のエンジン アニメーション スキル。
- **プロセス:** コンテンツを構築する前にコントローラーをグレーボックス化する `prototype-fast`。

 ## 参考資料

 - ジャンプ数学の導出、完全なフィールチューニング テーブル、コーナー補正、移動/一方向
プラットフォーム、およびカメラ フォローについては、`references/feel-tuning.md` を参照してください。 
