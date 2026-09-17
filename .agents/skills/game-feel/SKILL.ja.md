---
name: game-feel
description: >
  Add "juice" and game feel that makes actions satisfying — screen shake, hit-stop/freeze
  frames, tweened/eased motion, squash & stretch, knockback, and layered audio-visual
  feedback — as engine-neutral techniques that pair with the detected engine's tween,
  particle, and camera APIs. Use when the user mentions game feel, juice, "make it feel
  good/punchy", screen shake, hit stop, screen freeze, easing, squash and stretch, impact
  frames, or feedback/polish on hits, jumps, pickups, and deaths.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # ゲームの感触 (ジュース)

 *機能*するメカニクスと*良い*と感じるメカニクスの違いはフィードバックです。アクションが引き起こす、
の階層化された、少し誇張された反応です。このスキルは、エンジンの
ニュートラル テクニック (画面シェイク、ヒット ストップ、イージング、スカッシュ & ストレッチ、ノックバック、スタックされた
フィードバック) をカバーし、基礎となるシミュレーションを埋め込むことなくそれらを適用する方法を示します。
**既存のメカニックに磨きをかけます**。メカニズムは実装されていません。

 ##

 を使用する場合
- アクション (ヒット、ジャンプ、ダッシュ、拾う、死亡、ボタンを押す) が機械的に正しい
が、弱い、無重力、または満足のいくものではないように感じられ、応答性とパンチの効いた感触が必要な場合に使用します。
- 画面の揺れ、ヒットストップ/フリーズフレーム、緩和モーション、スカッシュ＆ストレッチ、ノックバック、
 フラッシュを追加したり、複数のフィードバック チャネルを 1 つのイベントに重ねたりするために使用します。
- ジュースの *どのくらい* が十分か、どこでノイズと交差するかを決定するために使用します。

 **使用しない*場合:** 生のコントローラーの計算 (ジャンプ高さ、コヨーテ時間) には、
 `platformer` ジャンルとエンジン移動スキルを使用します。カメラ *フォロー/デッドゾーン/オービット* フレーミング
の場合は、`camera-systems` を使用します (このスキルは手ぶれのみをトリガーします)。ミキシング、ダッキング、アダプティブ
音楽には、`audio-design` を使用します。シェーダベースのディゾルブ/フラッシュの場合は、`shader-programming` および
エンジン シェーダ スキルを使用します。具体的なトゥイーン/パーティクル ノード API の場合は、エンジン アニメーション スキル
(`godot-animation`、`unity-animation`) を使用します。

 ## 基本原則: フィードバックは階層化され、誇張されています

 満足のいくヒットは、通常、**5 ～ 8 個の小さな応答が 100 ミリ秒以内に同時に発火する**です: サウンド、
 パーティクルのバースト、短いヒットストップ、フラッシュ、ノックバック、小さな画面の揺れ、および
のポップ音アップ。どれも安いです。積み上げると「インパクト」と読みます。
状態が混乱するのを防ぐ 2 つのルールがあります。**(1)** 誇張して *簡単に*、休止状態に戻ります (ジュースは一時的なものであり、新たな休止状態
ではありません)。 **(2)** イベントの重要性に応じてジュースを調整します。足音はボスの死ではありません。

 ## コア ワークフロー

 1. **イベント フックが存在することを確認します。** ジュースは個別のイベントに添付されます: `on_hit`、`on_land`、
 `on_pickup`、`on_death`、 `on_fire`。メカニックがこれらを発行しない場合は、最初に追加します。
2. メニューから **イベントごとにフィードバック チャンネルを選択**します (サウンド、パーティクル、シェイク、ヒットストップ、
 フラッシュ、ノックバック、トゥイーン、ナンバー ポップ)。 2 ～ 3 から始めます。読み取れるまで追加し、その後停止します。
3. **リニアではなくモーションをイージングします。**
イーズ (「ポップ」の場合はオーバーシュート、「セトル」の場合はイーズアウト) を使用して、トゥイーンを通じてスケール/位置/UI の変更をルートします。直線的な動きはロボットのように感じられます。
4. **ヒットストップとシェイクはインパクトのために取っておきます。** これらは最も強力で悪用されやすいツールです。
 短時間で、重要度に合わせて調整され、日常的なアクションでは決して使用されません。
5. **重要なシミュレーションからフィードバックを遠ざけてください。** シェイクは
の本体ではなく、*カメラ/ビジュアル*を動かします。ヒットストップは、ゲームプレイ ロジックのストールではなく、タイム スケールまたはリアルタイムの一時停止を使用します。
6. **重要度層による調整** 小/中/大のフィードバック プリセットを定義し、イベント
を層に割り当てることで、ゲーム全体のジュースの一貫性と比例性が維持されます。
7. **再生して確認してください。** イベントを繰り返しトリガーします。
が発生し、休止状態に戻り、吐き気や入力ブロックがないことを確認します。
で観察したことを報告してください (シェイクは減衰しますか? ヒットストップ中に入力はまだ記録されますか?)。

 ## パターン

 ### 1. 減衰する「トラウマ」による画面の揺れ (ランダムなジッターではなくスムーズ)

```gdscript
# Godot 4.7. Store trauma 0..1; shake = trauma^2 so small hits barely move, big hits punch.
# Drives a Camera2D OFFSET (the visual), never the player body. Decays every frame.
@export var decay := 1.2          # trauma lost per second
@export var max_offset := Vector2(12, 8)
@export var max_roll := 0.1       # radians
var trauma := 0.0
var _t := 0.0

func add_trauma(amount: float) -> void:
    trauma = clampf(trauma + amount, 0.0, 1.0)   # hits ADD; they don't reset

func _process(dt: float) -> void:
    if trauma <= 0.0: return
    trauma = maxf(trauma - decay * dt, 0.0)
    var shake := trauma * trauma                  # quadratic: gentle low, sharp high
    _t += dt * 30.0
    # Smooth pseudo-random via sampled noise/sin, NOT rand each frame (that buzzes).
    offset = Vector2(max_offset.x * shake * sin(_t * 1.7),
                     max_offset.y * shake * sin(_t * 2.3))
    rotation = max_roll * shake * sin(_t * 1.1)
# Unity 6.3 LTS: identical model on a CinemachineCamera via CinemachineBasicMultiChannelPerlin
# (set AmplitudeGain/FrequencyGain from trauma^2) — see camera-systems.
```

### 2. ヒットストップ/フリーズフレーム(時間停止によるセルインパクト)

```gdscript
# Godot 4.7. Drop time scale, then restore after a REAL-TIME delay (unaffected by time_scale).
func hit_stop(duration := 0.08, scale := 0.05) -> void:
    Engine.time_scale = scale
    # 4th arg ignore_time_scale=true → the timer still fires while the game is frozen.
    await get_tree().create_timer(duration, true, false, true).timeout
    Engine.time_scale = 1.0
```

```csharp
// Unity 6.3 LTS (C#). WaitForSecondsRealtime ignores Time.timeScale, so the timer still elapses.
IEnumerator HitStop(float duration = 0.08f, float scale = 0.05f) {
    Time.timeScale = scale;
    yield return new WaitForSecondsRealtime(duration);
    Time.timeScale = 1f;            // RIGHT: real-time wait. WRONG: WaitForSeconds (never resumes at scale 0)
}
```

### 3. 緩和トゥイーン (「ポップ」) によるスカッシュ & ストレッチ + オーバーシュート

```gdscript
# Godot 4.7. Conserve volume: stretch one axis, squash the other, then spring back with overshoot.
func pop(node: Node2D) -> void:
    node.scale = Vector2(1.3, 0.7)                       # instant squash on the event
    var tw := create_tween()
    tw.tween_property(node, "scale", Vector2.ONE, 0.18) \
      .set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)   # BACK = overshoots past 1, settles
# RIGHT: ease back (TRANS_BACK/ELASTIC) for life. WRONG: linear tween → mechanical, dead.
```

### 4. 重要度によってスケールされたフィードバック バンドル (ジュースの比例を維持)

```gdscript
# One call per event; the tier decides intensity so the whole game stays consistent.
func feedback(event_pos: Vector2, tier: String) -> void:
    match tier:
        "small":  AudioBus.play("tick");  Camera.add_trauma(0.15)
        "medium": AudioBus.play("hit");   Camera.add_trauma(0.4);  hit_stop(0.05); spawn_particles(event_pos, 6)
        "large":  AudioBus.play("boom");  Camera.add_trauma(0.8);  hit_stop(0.12); spawn_particles(event_pos, 30); flash_white(0.06)
```

## 落とし穴

 - **カメラ オフセットの代わりにプレーヤー/本体を振る**と、衝突と照準が非同期になります。シミュレートされた変換ではなく、カメラ (またはビジュアル ピボット) を
シェイクします。
- **フレームごとにランダムなオフセット**が静的な音のように鳴ります。サンプリングされたノイズ/罪と
減衰するトラウマ値からのドライブ シェイクにより、スムーズで自己終了します。
- **`WaitForSeconds` によるヒットストップ / スケールされたタイマー** は再開しません (タイム スケール 0 では、タイマー
は進みません)。リアルタイム待機 (`WaitForSecondsRealtime`、または Godot の
`ignore_time_scale` タイマー) を使用します。
- **ホールド攻撃のすべてのフレームでヒットストップ**すると、ゲームがロックされます。衝撃ごとに1回トリガーします。
- **どこにでもあるリニア トゥイーン** はロボットのように感じられます。ほとんどすべてを簡単にします。オーバーシュート
(BACK/ELASTIC) を「ポップ」用に、イーズアウトを「セトリング」用に予約します。
- **永続的な誇張** (スケールが戻らない、シェイクが減衰しない) が新しい通常の
になり、フィードバックとしての読み取りが停止します。ジュースは休息に戻らなければなりません。
- **過剰な日常動作** (フルシェイク + 足音ごとにヒットストップ) は吐き気を引き起こしますが、
 は実際の影響を隠します。重要性に応じて調整します。 「画面の揺れを減らす」/「点滅を減らす」
 アクセシビリティ オプションを追加します。
- **入力をブロックするフィードバック** (長時間のフリーズ、キャンセルできないアニメーション) により、応答性が低下します。
ジュースを短く保ち、入力をバッファーに通します。

 ## 参考文献

 - トラウマシェイクの計算、イージングカーブのチートシート (ポップとセトルのイージング)、ノックバック
+ フラッシュ + ナンバーポップのレシピ、重要度層のプリセット、およびエンジンごとのトゥイーン/パーティクル バインディングについては、
 を参照してください。 `references/feedback-recipes.md`。

 ## 関連スキル

 - `camera-systems` — カメラのフォロー/デッドゾーン/オービットを所有します。このスキルはトラウマを揺さぶるだけです。
- `godot-animation`、`unity-animation` — コンクリート トゥイーン/AnimationPlayer/パーティクル API ジュースが乗ります。
- `audio-design` — すべてのフィードバック バンドルのサウンド レイヤー。ダッキングとSFXのバリエーション。
- `physics-tuning` — ノックバック力とタイムステップ ジュースが不安定になってはなりません。
- `platformer`、`fps-shooter`、`roguelike` — 瞬間瞬間の感触が高揚するジャンル。 
