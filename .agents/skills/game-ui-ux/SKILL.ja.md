---
name: game-ui-ux
description: >
  Design and build game UI/UX — HUDs, menus, and overlays — that survive every screen: anchor-
  based responsive layout, resolution/aspect scaling and safe areas, keyboard/gamepad focus
  navigation, a screen/menu state stack, and event-driven (not polled) HUD updates. Engine-
  neutral patterns that pair with the detected engine's UI skill. Use when the user mentions
  HUD, health bar, main menu, pause menu, settings screen, UI layout, anchors, UI scaling,
  aspect ratio, safe area, controller/keyboard menu navigation, or wiring UI to game state.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # ゲーム UI/UX


ゲームパッドとマウスを使用して、電話、ウルトラワイド モニター、テレビ上で正しく動作する HUD とメニューを構築します。このスキルは、エンジンに依存しない UI アーキテクチャ (レスポンシブ レイアウト、
 スケーリング、フォーカス ナビゲーション、画面フロー、UI がゲーム状態と対話する方法) を所有し、
 具象ウィジェット API をエンジン UI スキルに委ねます。

 ##

 を使用する場合 - HUD (ヘルス/弾薬/スコア)、メニュー (メイン/一時停止/設定)、インベントリまたは
ショップ画面、またはオーバーレイを構築し、正しくスケールしてナビゲートする必要がある場合に使用します。
- 他の解像度/アスペクト比で壊れる、ノッチ/安全領域を無視する UI を修正するために使用します。
 はコントローラーでは使用できないか、フレームごとのポーリングによってゲームの状態に接続されます。
- フ​​ラグ スープではなく、スタックとして画面フロー (タイトル → ゲーム → 一時停止 → 設定) を構造化するために使用します。

 **使用しない*場合:** エンジンの具体的な UI ノード/コンポーネントおよびスタイル設定には、
 `godot-ui-control` または Unity UI (UGUI/UI ツールキット) を使用します。 *視覚的* パンチ (ボタンのポップ、
 の数字にダメージを与える、シェイク) の場合は、`game-feel` を使用します。会話 UI を分岐するには、`dialogue-systems` を使用します。
の UI 文字列の翻訳、つまりローカリゼーションの場合 (
 の再バインド画面については、`references/` および `input-systems` を参照してください)。カード/ボード レイアウトの詳細については、`card-game` ジャンルがこのスキルを構成します。

 ## コア ワークフロー

 1. **レイアウト モデルを選択します: アンカー + コンテナ。絶対ピクセルは使用しないでください。** 要素を
のエッジ/コーナー/中央に固定し、コンテナ (行、列、グリッド) を子に流し込みます。絶対
`(x, y)` 位置は、最初の新しい解像度で中断されます。
2. UI 全体の **スケーリング戦略を選択**:
(ほとんどのゲーム) に合わせてスケーリングする基準解像度に加えて、他のアスペクト比での追加の幅/高さのポリシー (レターボックス、
 拡張、または HUD コーナーを外側に固定)。
3. **安全領域を尊重します。** ノッチ、丸い角、
、TV のオーバースキャンによってクリップされないように、重要な UI を画面の端から挿入します。
4. **すべての画面キーボード/ゲームパッドを操作可能にします。** 画面ごとに初期フォーカス コントロールを設定し、
 でフォーカス順序/隣接を定義し、明確なフォーカス ハイライトを表示します。マウスとフォーカスは共存する必要があります。
5. **画面をスタックとしてモデル化します。** プッシュ (ゲーム上で一時停止)、ポップ (再開)、入力 + 可視性
がトップ画面に渡されます。これにより、オーバーレイと「バック」が簡単になります。
6. **ポーリングではなく、イベントから HUD を駆動します。** HUD は `health_changed`、
 `score_changed` などをサブスクライブし、それらが起動したときにのみ更新します。
 フレームごとにゲームの状態を読み取るわけではありません。
7. **画面とデバイス間で確認します。** ウィンドウのサイズを変更し、アスペクト比を切り替え、
 マウスを取り外し、ゲームパッドのみでナビゲートし、フォーカス、スケーリング、および安全領域のインセットを確認します。どの解像度で実際に観察した内容を
に報告します。

 ## パターン

 ### 1. 絶対座標ではなく、アンカー + コンテナ

```gdscript
# Godot 4.7. Anchor a HUD label to the TOP-LEFT; let a container flow a row of hearts.
func _ready() -> void:
    $Score.set_anchors_preset(Control.PRESET_TOP_LEFT)   # sticks to the corner at any size
    # An HBoxContainer auto-lays-out children left-to-right; never position hearts by hand.
    for i in lives:
        $Hearts.add_child(make_heart())                   # HBoxContainer spaces them for you
# Unity 6.3 LTS uGUI: set RectTransform anchors to the corner; use a HorizontalLayoutGroup.
# RIGHT: anchors + layout groups. WRONG: rect.anchoredPosition = new Vector2(640, 360) (1080p-only).
```

### 2. 基準解像度にスケールする (1 つの UI、多くの画面)

```text
# Godot 4.7 — Project Settings > Display > Window > Stretch:
#   Mode = "canvas_items", Aspect = "expand", reference size e.g. 1920x1080.
#   UI scales to the window; "expand" reveals extra space you anchor HUD corners into.
# Unity 6.3 LTS — Canvas > CanvasScaler:
#   UI Scale Mode = "Scale With Screen Size", Reference Resolution = 1920x1080,
#   Match = 0.5 (blend width/height) — pick 1.0 if your HUD is height-critical.
```

### 3. ノッチ/オーバースキャンの安全領域インセット

```gdscript
# Godot 4.7. Inset a margin container to the OS-reported safe rect (phones, TVs).
func _apply_safe_area() -> void:
    var safe: Rect2i = DisplayServer.get_display_safe_area()
    var win := DisplayServer.window_get_size()
    $Margin.add_theme_constant_override("margin_left", safe.position.x)
    $Margin.add_theme_constant_override("margin_top",  safe.position.y)
    $Margin.add_theme_constant_override("margin_right", win.x - safe.end.x)
    $Margin.add_theme_constant_override("margin_bottom", win.y - safe.end.y)
# Unity 6.3 LTS: read Screen.safeArea (Rect in pixels) and set a panel's anchorMin/anchorMax to
# safeArea.position / (position+size) normalized by Screen.width/height.
```

### 4. ゲームパッド/キーボード フォーカス (これがないとコントローラーでは UI が使用できません)

```gdscript
# Godot 4.7. Give each screen a default focus and wire neighbors so a stick/d-pad walks it.
func _on_screen_shown() -> void:
    $PlayButton.grab_focus()                               # always focus SOMETHING on open
$PlayButton.focus_neighbor_bottom = $SettingsButton.get_path()
$SettingsButton.focus_neighbor_top = $PlayButton.get_path()
# Unity 6.3 LTS: EventSystem.SetSelectedGameObject(playButton) on enable; set each Selectable's
# Navigation (Explicit or Automatic). RIGHT: a control is focused on open. WRONG: nothing
# selected → the gamepad does nothing and the player is stuck.
```

### 5. イベント駆動型 HUD (ゲーム ロジックから UI を切り離す)

```gdscript
# RIGHT: HUD reacts to a signal; it updates only when health actually changes.
func _ready() -> void:
    player.health_changed.connect(_on_health_changed)     # emitted by gameplay
func _on_health_changed(current: int, max: int) -> void:
    $HealthBar.value = float(current) / max
# WRONG: func _process(dt): $HealthBar.value = player.hp / player.max_hp  # polls every frame,
# couples UI to the player's internals, and runs work even when nothing changed.
```

## 落とし穴

 - **絶対ピクセル位置 / 単一の設計解像度。** モニターでは正しく表示されますが、他の場所では
が壊れます。エッジ/中央に固定し、コンテナーとともに流れます。
- **アスペクト比ポリシーはありません。** 16:9 のみのレイアウトでは、ウルトラワイドや携帯電話ではクロップまたはレターボックスがうまく表示されません。
レターボックスと拡張を決定し、HUD を外側に移動するコーナーに固定します。
- **安全領域を無視しています。** HUD がノッチの下にあるか、TV のオーバースキャンにより失われました。重要な要素を挿入します。
- **初期フォーカスなし/フォーカス隣接なし。** ゲームはゲームパッドではプレイできません。プレイヤーは何も選択されていない状態でメニューに
を配置します。常に 1 つのコントロールに焦点を当て、ナビゲーションを定義します。
- **`_process`/`Update` でゲームの状態をポーリングします。** UI を内部に結合し、作業を無駄にします。信号/イベント経由で
更新をプッシュします。
- **小さな固定フォント サイズ。** 離れたテレビや小さな携帯電話では読めません。
UI を使用してテキストを拡大縮小し、テキスト サイズのオプションを提供します。
- **ブール フラグとしてのメニュー フロー** (`isPaused`、`inSettings`、…) が管理できなくなります。プッシュ/ポップで
画面スタックを使用します。
- **ハードコードされた英語の文字列がレイアウトに焼き付けられています。** 翻訳のオーバーフロー ボタン。
文字列を外部化し、コンテナーのサイズをコンテンツに合わせます (`references/` を参照)。
- **マウスのみまたはフォーカスのみ。** 両方をサポートします。入力デバイスの切り替えによってユーザーが混乱してはいけません。

 ## 参考資料

 - エンジンごとのストレッチ/スケール モード、安全領域の計算、完全なフォーカス ナビゲーションと
画面スタック パターン、ダイジェティック UI と非ダイジェティック UI、アクセシビリティ (テキスト サイズ、コントラスト、
 カラーブラインド セーフ状態)、およびローカリゼーション対応レイアウト、`references/layout-and-flow.md` を読み取ります。

 ## 関連スキル

 - `godot-ui-control`、Unity UI (UGUI/UI ツールキット) — 具体的なウィジェット、テーマ、スタイル。
- `game-feel` — このレイアウトの上にあるボタン ポップ、トランジション、および HUD ジュース。
- `dialogue-systems` — この UI シェル内に存在する会話/選択 UI。
- `input-systems` — デバイスの切り替え、画面の再バインド、およびアクセス可能なコントロール。
- `rpg`、`card-game`、`tower-defense`、`visual-novel` — このスキルを構成する UI の多いジャンル。 
