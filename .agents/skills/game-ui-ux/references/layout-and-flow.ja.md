# レイアウト、スケーリング、フロー — `game-ui-ux` の深さ

 `game-ui-ux` 本体の詳細については、ここで説明します。エンジンごとのスケーリング モード、安全領域の計算、完全な
フォーカス + スクリーン スタック パターン、ダイエジェティック UI、アクセシビリティ、およびローカリゼーション対応レイアウト。スニペット
は **Godot 4.7** および **Unity 6.3 LTS** をターゲットとしています。

 ## 1. エンジンごとのスケーリング モード

 **Godot 4.7** (プロジェクト設定 → 表示 → ウィンドウ → ストレッチ):

 |設定 | |を選択してください効果 |
|----------|--------|--------|
|モード | `canvas_items` | UI はウィンドウに合わせてスケールします (対 `viewport` = ピクセル正確、`disabled` = なし)。
|側面 | `expand` |奇数の比率でより多くのワールド/UI スペースを表示します。 `keep` レターボックス |
|スケール | `1.0`+ |グローバル UI 乗数 |

 アンカー HUD コーナーを使用すると、`expand` で必要な場所に余分なスペースを配置できます。 `keep_width`/`keep_height`
は、ハード 16:9 デザインの 1 つの軸をピン留めします。

 **Unity 6.3 LTS** (各キャンバスの `CanvasScaler`):

 - `UI Scale Mode = Scale With Screen Size`。
- `Reference Resolution = 1920×1080` (またはアートのデザイン サイズ)。
- `Screen Match Mode = Match Width Or Height`、`Match = 0.5` (ブレンド)。垂直方向の
レイアウトが絶対にクリップされない場合は `1.0` を使用し、水平方向のレイアウトが禁止される場合は `0.0` を使用します。
- スプライトベースの UI の場合は `Reference Pixels Per Unit = 100`。

 ## 2. 安全領域の計算

 OS は、画面内の安全な長方形を報告します (ノッチ、丸い角、およびテレビ
ではオーバースキャン マージンを除きます)。 **重要な** UI (ヘルス、タイマー、プロンプト) のみを挿入します。装飾アートは
端まではみ出す可能性があります。

```text
# Normalized anchors from a pixel safe rect (engine-neutral):
anchorMin = (safe.x / screenW,                 safe.y / screenH)
anchorMax = ((safe.x + safe.w) / screenW,       (safe.y + safe.h) / screenH)
# Re-apply on resolution change / orientation change, not once at startup.
```

- **Godot:** `DisplayServer.get_display_safe_area()` → `Rect2i` (ピクセル単位)。
`size_changed` に再適用してください。
- **Unity:** `Screen.safeArea` → `Rect` (ピクセル単位)。 `Screen.width/height` または
`Screen.orientation` が変更されたときに再計算します (フレームごとの作業を避けるために、最後に適用された四角形をキャッシュします)。

 ## 3. フォーカス ナビゲーション (フル パターン)

 コントローラー/キーボードの使いやすさの要件:

 1. 開いているすべての画面で **初期フォーカス** (`grab_focus()` / `EventSystem.SetSelectedGameObject`)。
2. 予測可能な動きのための **明示的な隣接** (Godot `focus_neighbor_*`; Unity `Navigation`
= 上下左右で明示的、または単純なグリッドの場合は自動)。
3. **目に見えるフォーカス スタイル** はホバーとは異なります (テーマ フォーカス スタイルボックス / Unity で選択可能な
トランジション)。決して色だけに依存しないでください (アクセシビリティを参照)。
4. リストの最後で意図的に **折り返しまたは停止**します。モーダルダイアログ内にフォーカスをトラップします。
5. **デバイスの共存:** マウスを動かすと選択を更新できます。ゲームパッドを押すと、
 に焦点を当てたコントロールが動作します。マウスが動いたときにフォーカスをクリアしないでください。

```gdscript
# Godot 4.7: trap focus inside a modal so the stick can't escape to the game behind it.
func open_modal() -> void:
    _prev_focus = get_viewport().gui_get_focus_owner()
    $Modal.show(); $Modal/OK.grab_focus()
func close_modal() -> void:
    $Modal.hide()
    if is_instance_valid(_prev_focus): _prev_focus.grab_focus()
```

## 4. 画面/メニュー スタック

 画面を UI 状態のスタックとしてモデル化します。上部は入力を所有しており、表示されます。オーバーレイの場合はプッシュ、「戻る」の場合は
のポップ。これにより、一時停止、一時停止上の設定、および確認のダイアログが一般化されます。

```gdscript
# Godot 4.7 sketch (a CanvasLayer per screen; pausing the tree under an overlay):
var _stack: Array[Control] = []
func push(screen: Control) -> void:
    if _stack.size() > 0: _stack.back().set_process_input(false)
    _stack.append(screen); add_child(screen); screen.grab_focus_default()
func pop() -> void:
    var top := _stack.pop_back(); top.queue_free()
    if _stack.size() > 0:
        _stack.back().set_process_input(true); _stack.back().grab_focus_default()
# Pause overlay: get_tree().paused = true and set the overlay's process_mode = ALWAYS.
```

これは、`love2d-core` の `references/state-stack.md` の状態スタックのアイデアを反映し、UI に適用されます。

 ## 5. ダイジェティック UI と非ダイジェティック UI

 - **非ダイジェティック:** フィクション (ほとんどの HUD) の外側のスクリーン プレーン上に描画されます。最も安く、最も明確。
- **ダイジェティック:** ワールドに存在する UI (銃の弾薬カウンター、スーツのヘルス)。
の没入感が増し、作業量が増えると、可読性が損なわれる可能性があります。重要な要素に使用し、非ダイジェティック フォールバックを維持します。
- **空間/ワールド空間:** フローティングヘルスバー、ダメージ数値 - ワールド位置にアンカー、画面外の場合は
クランプを画面端に固定し、距離に応じてスケール (3D)。

 ## 6. アクセシビリティ (ベイクイン、ボルトオンではありません)

 - **テキスト サイズ オプション**、小さなフォントをハードコーディングしないでください。サイズを基準高さのパーセンテージに設定します。
- **コントラストと色の独立性:** 色だけで状態をエンコードしないでください。アイコン/形状/テキストを追加します。
色盲に対応したパレットを提供します。
- **スケーラブルなヒット ターゲット** (タッチ用) (≥ ~9 mm);小さなボタンの周りのパディング。
- **動作を減らす/点滅を減らす**を切り替えます (`game-feel` と連携します)。
- **フル キーボード + ゲームパッド** の到達可能性 (セクション 3)。マウスのみの背後でアクションをゲートしないでください。

 ## 7. ローカリゼーション対応レイアウト

 - 文字列を外部化します (Godot `tr()` + 翻訳 CSV/PO; Unity Localization パッケージ)。
表示テキストをレイアウト ロジックにベイクしないでください。
- コンテナーのサイズを **コンテンツに合わせて**することで、長い翻訳 (ドイツ語は最大 30% 長い) がクリップされないようにする。
英語に合わせたサイズの固定幅ボタンは避けてください。
- RTL ミラーリングとさまざまな数値/日付形式用の余地を残します。
- アイコンをテキストから分離して、文字列のみを翻訳する必要があるようにします。 
