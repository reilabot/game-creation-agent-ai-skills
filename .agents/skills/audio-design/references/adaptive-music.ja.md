# アダプティブ (ダイナミック) ミュージック

 アダプティブ ミュージックは、1 つのトラックをループするのではなく、ゲームプレイに合わせて変化します。
の 2 つのテクニックが主であり、それらが組み合わされています:

 - **垂直レイヤー (再オーケストレーション)** - 複数のステム (ドラム、ベース、メロディー、
 テンション パッド) が同期して再生されます。
で基礎となるループを変更せずに、レイヤーをフェードイン/フェードアウトして強度を変更します。すべてのレイヤーが同じ
タイムラインを共有するため、シームレスです。
- **水平方向の再シーケンス** — トラックはセグメント (イントロ、ループ A、
 ループ B、戦闘、アウトロ) に分割されます。次に再生するセグメントを切り替えて、
 の音楽境界 (小節/フレーズ) でトランジションし、変更がビートに反映されるようにします。

 ## 垂直レイヤー

 すべてのレイヤーは同じ長さで、一緒に始まります。音量だけが変わります。

```gdscript
# Keep N stem players in sync (same position), and fade volumes by intensity.
var layers := { "base": p_base, "drums": p_drums, "tension": p_tension }

func start_layers() -> void:
    for p in layers.values():
        p.volume_db = -80.0       # start silent
        p.play()                  # all begin together -> stay sample-aligned
    layers["base"].volume_db = 0.0

func set_intensity(level: int) -> void:   # 0 calm .. 2 combat
    _fade(layers["drums"],   0.0 if level >= 1 else -80.0)
    _fade(layers["tension"], 0.0 if level >= 2 else -80.0)

func _fade(p, target_db: float, t := 0.8) -> void:
    create_tween().tween_property(p, "volume_db", target_db, t)
```

ヒント: 同じ BPM/長さでステムを作成し、整列してバウンスします。
~0.5 ～ 1.5 秒のフェードは音楽的に感じられます。インスタントカットは機械的な感じがします。レイヤーが
再起動することはないため、強度はいつでも同期を失うことなく変更できます。

 ## 水平方向の再シーケンス

 トランジションが唐突に聞こえないように、安全な音楽ポイントでセグメントを切り替えます。

```gdscript
# Request a section change; apply it only at the next bar boundary.
var pending_section := ""
const BPM := 120.0
const BEATS_PER_BAR := 4
var sec_per_bar := 60.0 / BPM * BEATS_PER_BAR

func request_section(name: String) -> void:
    pending_section = name        # don't switch mid-bar; queue it

func on_bar_boundary(pos: float) -> void:
    if pending_section != "":
        crossfade_to(pending_section, 0.2)   # short crossfade across the seam
        pending_section = ""
```

トランジション戦略、おおよそ洗練されています:

 - **即時クロスフェード** — 素早いボリューム ブレンド。リスクの低い変更には問題ありません。
- **クオンタイズ スイッチ** — 次のビート/小節/フレーズを待ってから切り替えます。 「時間通り」に留まるべき音楽の
のデフォルト。
- **トランジション セグメント** — A→B を音楽的に接続するために作成された短いブリッジ クリップ。
- **スティンガー** — ループを変更することなく、イベント (ボス
の登場、秘密の発見) のためにベッドの上に重ねられたワンショットの音楽アクセント。

 ## ゲームプレイを強度にマッピング

 生のイベントではなく、小さく滑らかな強度値から音楽を駆動します:

```gdscript
# Combine signals into 0..1, smooth it, then map to layers/sections with hysteresis.
func intensity_from_state(enemies_near: int, player_hp01: float) -> float:
    var raw = clamp(enemies_near / 5.0, 0.0, 1.0) * (1.0 - 0.4 * player_hp01)
    intensity = lerp(intensity, raw, 0.05)   # smooth so it doesn't flicker
    return intensity

# Hysteresis: require crossing different thresholds up vs down so the music
# doesn't oscillate when intensity hovers at a boundary.
func level_from_intensity(i: float, current: int) -> int:
    if current < 1 and i > 0.6: return 1
    if current >= 1 and i < 0.4: return 0
    return current
```

## 実用的なメモ

 - **フレーム デルタではなく、オーディオ クロックからタイミングを駆動**し、スケジューリング時に出力
レイテンシーを考慮します。
- **ループ ポイント**はサンプル精度である必要があります。継ぎ目から隙間やカチッという音が出ます。
ループを作成してバーの境界を作成し、ラップをテストします。
- **ミドルウェア** (FMOD、Wwise) は、レイヤー化、量子化されたトランジション、および
パラメーター駆動の強度をネイティブに実装します。音楽システムが少数のステム/セグメントを超えて
に成長したときに、それに到達します。
- **予算**: 同時ステムを多数使用すると、音声とメモリにコストがかかります。長い音楽をストリーミングします。
は、ローエンドのターゲットではステム数を控えめに保ちます。 
