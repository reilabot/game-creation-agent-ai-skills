---
name: input-systems
description: >
  Architect game input — action mapping (abstracting keys into named actions),
  rebinding with conflict detection and persistence, multi-device support
  (keyboard, gamepad, touch), analog deadzones, and feel features like input
  buffering and coyote time, plus accessibility. Engine-neutral. Use when the
  user mentions input mapping, rebind controls, gamepad support, deadzone, input
  buffering, coyote time, or accessible controls.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # 入力システム

 ゲームプレイを生のキーに接続しないでください。物理入力 (キー、ボタン、タッチ)
を名前付き **アクション** (`jump`、`interact`、`move`) にマップし、ゲームプレイにアクションを読み取らせます。
この 1 つの間接的な方法により、再バインド、マルチデバイスのサポート、およびアクセシビリティ
がほぼ無料で提供されます。このスキルはエンジンに依存しないアーキテクチャです。それを
`unity-input-system`、`unreal-enhanced-input`、または Godot の `InputMap` にバインドします。

 ##

 を使用する場合 - 入力レイヤーの設計に使用します: アクション、バインディング、複数のデバイス、競合検出と保存されたバインディングを備えた
再バインド UI。
- アナログ処理 (デッドゾーン、感度) とゲームフィール機能
(入力バッファリング、コヨーテ タイム) を追加するために使用します。
- コントロールにアクセスできるようにするために使用します (完全な再マッピング、ホールドとトグル、感度、
 の同時押しは不要)。

 **使用しない*場合:** エンジンの具体的な入力パッケージ/API には、
、`unity-input-system`、`unreal-enhanced-input`、または Godot の InputMap を使用します。バッファー フィードの
移動/ジャンプ *物理* については、`physics-tuning` およびエンジン
移動スキルを参照してください。ディスクへのバインディングの永続化は `save-systems` です。

 ## コア ワークフロー

 1. **キーではなくアクションを定義します。** ゲームプレイでは「`jump` が押されていますか?」と尋ねられますが、「
 スペースが押されていますか?」という質問は決してされません。アクションは安定した契約です。バインディングはデータです。
2. **デバイスごとにバインドします。** 各アクションは、キーボード、ゲームパッド、および
タッチのバインドを保持します。アクティブなデバイスは、最後に送信された入力です。一致するように UI プロンプトを交換します。
3. **右端を読んでください。** 個別のアクションには *pressed-this-frame* (エッジ) を使用します。
(ジャンプ、インタラクション)、連続アクション (移動、照準) には *hold* (レベル) を使用します。
を混同すると、この 2 つが二重発射や押し忘れを引き起こします。
4. **アナログ入力をフィルターします。** スティック/トリガーにデッドゾーンを適用して、静止時のドリフト
がゼロとして読み取られ、感度/カーブを好みに合わせてスケールします。
5. **感触のためのバッファ。** 短いウィンドウで押されたアクションを記憶し、わずかに
早く押しても発火します (入力バッファリング)。
棚を離れた直後にジャンプを許可します (コヨーテ時間)。
6. **再バインドを最上級にします。** 次の入力をキャプチャし、
 の競合を検出し、バインディングを保持し、デフォルトにリセットする UI。
`save-systems` 経由で保存します。
7. **すべてのデバイスで検証**し、再バインドを使用して: キーボード、ゲームパッド、タッチ。ゲーム中に
アクションを再バインドし、ゲームプレイとプロンプトが続くことを確認します。

 ## パターン

 ### 1. 生のキーに対するアクション。エッジ vs ホールド

```gdscript
# Gameplay reads ACTIONS. The mapping from key/button to action lives in data.
# Discrete (edge): fire once on the press frame.
if Input.is_action_just_pressed("jump"):
    try_jump()
# Continuous (held): read every frame as an axis.
var move := Input.get_axis("move_left", "move_right")   # -1..1
player.velocity.x = move * RUN_SPEED
# RIGHT: name actions ("jump"); rebinding/devices just change the binding data.
# WRONG: `if Input.is_key_pressed(KEY_SPACE)` — unrebindable, keyboard-only,
# and `is_key_pressed` is a held check that would re-fire jump every frame.
```

同等のエンジン: Godot `InputMap` + `Input.is_action_just_pressed`; Unity
入力システム `InputAction` / アクション マップ;アンリアル拡張入力 `Input Actions` +
`Input Mapping Contexts`。

 ### 2. アナログデッドゾーンと感度

```gdscript
# Raw sticks never rest at exactly zero. Apply a RADIAL deadzone (on the vector
# length), not per-axis, so diagonals aren't clipped into the axes.
func apply_deadzone(stick: Vector2, dead := 0.2, sens := 1.0) -> Vector2:
    var mag := stick.length()
    if mag < dead:
        return Vector2.ZERO                      # inside deadzone -> no movement
    # Rescale so motion ramps from 0 at the edge of the deadzone, not from `dead`.
    var scaled := (mag - dead) / (1.0 - dead)
    return stick.normalized() * pow(scaled, sens)  # sens>1 = finer near center
# WRONG: clamping each axis separately — it carves a square hole and snaps to axes.
```

### 3. 入力バッファリング + コヨーテ タイム (寛容で応答性の高い感触)

```gdscript
# Buffer: a jump pressed slightly BEFORE landing still triggers on touchdown.
# Coyote: a jump pressed slightly AFTER walking off a ledge still works.
const BUFFER := 0.12   # seconds an early press stays "remembered"
const COYOTE := 0.10   # seconds after leaving ground you can still jump
var _buffer_timer := 0.0
var _coyote_timer := 0.0

func _physics_process(dt):
    _buffer_timer -= dt
    _coyote_timer = COYOTE if is_on_floor() else _coyote_timer - dt
    if Input.is_action_just_pressed("jump"):
        _buffer_timer = BUFFER                  # remember the press
    if _buffer_timer > 0.0 and _coyote_timer > 0.0:
        velocity.y = JUMP_VELOCITY
        _buffer_timer = 0.0; _coyote_timer = 0.0  # consume both so it fires once
```

### 4. 競合検出による再バインド

```gdscript
# Capture the next physical input, reject duplicates, then persist.
func rebind(action: String, event: InputEvent) -> bool:
    for other in actions:                        # conflict check across actions
        if other != action and binding_of(other) == event:
            return false                         # already used -> let UI warn/swap
    set_binding(action, event)                   # engine: erase old + add new event
    save_bindings()                              # persist (see save-systems)
    return true
# Always provide "reset to defaults", and never let the player unbind a key they
# need to reach the menu without an alternative.
```

## 落とし穴

 - ゲームプレイの **ハードコーディング キー** は再バインドをブロックし、ゲームパッド/タッチをロックアウトし、
 は入力ロジックを分散させます。名前付きアクションのみを読み取ります。
- **エッジとホールドの混乱**: ジャンプのホールド チェックを使用すると、フレームごとに再起動します。
は、移動のエッジ チェックを使用すると、保持された入力をドロップします。チェックとアクションを一致させます。
- **軸ごとのデッドゾーン** は、斜めのスティック入力をクリップし、動きを軸にスナップします。
ベクトルの大きさに放射状のデッドゾーンを使用します。
- **バッファリング/コヨーテ タイムがない** ため、たとえ
の物理法則が正しい場合でも、タイトなプラットフォーマーは不公平に感じます。プレイヤーは「明らかにジャンプを押した」のです。小さな窓を追加します。
- **競合処理を行わない再バインド**により、2 つのアクションでキーを共有したり、メニュー アクセスのバインドを解除してプレーヤーを
拘束したりできます。競合を検出します。帰り道を保証します。
- **デバイス変更時にプロンプ​​トが切り替わらない** ゲームパッド
プレーヤーに「スペースを押す」と表示されます。最後に使用したデバイスを追跡し、グリフを切り替えます。
- **アクセシビリティを無視**: 同時押しが必要、再マップなし、
 の感度は固定、ホールドのみのアクション。リマップ、切り替えとホールド、感度を提供します。
- **間違ったループで入力を読み取ります**:
の一貫した動きのための物理ステップで保持された状態をポーリングします。離散的なプレスをキャプチャして、フレーム間で見逃されるものがないようにします。

 ## 参考資料

 - `references/buffering-and-accessibility.md` — バッファリング/コヨーテ チューニング、ジャンプ フィール
(可変高さ、頂点)、デバイス検出とプロンプト スワップ、タッチ コントロール、
、およびアクセシビリティ チェックリスト (再マップ、トグル/ホールド、感度、レイテンシー)。

 ## 関連スキル

 - `unity-input-system`、`unreal-enhanced-input` — コンクリート エンジン入力 API
(Godot は `InputMap` + `Input` シングルトンを使用します)。
- `save-systems` — カスタム キー バインドと入力設定を保持します。
- `physics-tuning` — バッファ/コヨーテ ウィンドウがフィードする動き。
- `platformer`、`fps-shooter` — 入力処理に依存するジャンル。 
