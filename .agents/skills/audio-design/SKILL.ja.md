---
name: audio-design
description: >
  Implement game audio practice — bus/mixer architecture and gain in decibels,
  ducking (sidechain), adaptive/dynamic music via layering and re-sequencing,
  SFX variation, and beat synchronization. Engine-neutral. Use when the user
  mentions audio mixing, audio buses, adaptive/dynamic music, ducking, SFX
  variation, music layers, or syncing gameplay to the beat.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # オーディオ デザイン

 ゲーム オーディオは **ミキシング グラフと音楽システム**です。すべてのサウンドを
の小さなバス セットにルーティングして、グループのバランスを取り、処理できるようにします。 1 つのトラックをループするのではなく、レイヤー化と再シーケンスを通じて
再生に音楽を *反応* させます。このスキル
は移植可能な練習を教えます。具体的な API 用に、それを `godot-audio`、Unity の AudioMixer、または
ミドルウェア (FMOD/Wwise) にバインドします。

 ##

 - バス/ミキサー レイアウトの設計、グループ ボリュームの設定、サウンド グループへのエフェクト (リバーブ、
 圧縮、EQ) の適用に使用します。
- ダイアログまたはインパクトの下で音楽/アンビエンスをダッキングするために使用します (サイドチェーン)。
- 戦闘/探索の激しさに反応する適応音楽を構築するために使用します。
- SFX バリエーション (ピッチ/サンプルのランダム化) を追加し、イベントをビートに同期するために使用します。

 **使用しない*場合:** エンジンの具体的なオーディオ ノード/ストリームには、
 `godot-audio` またはエンジンのオーディオ スキルを使用します。ロード/ストリーミングとアセットのインポートは、
 エンジンの問題です。バスの音量を調整する UI スライダーについては、エンジン UI スキルを参照してください。

 ## コア ワークフロー

 1. **サウンドごとのボリュームではなく、バスをレイアウトします。** 一般的なツリー: `マスター ← {音楽、
 SFX、アンビエンス、UI、音声}`。すべてがバスに関係します。プレーヤーの設定
スライダーはバスのボリュームにマップされます。何百ものクリップ ボリュームを手動で設定しないでください。
2. **線形ではなく、デシベル単位で作業します。** 知覚される音量は対数です。音量
コントロールとオートメーションは dB 単位で動作する必要があります。エッジのみを変換します。
3. **ヘッドルームを残します。** クリッピングを避けるために、マスターのピークが 0 dBFS 未満になるようにミックスします (ターゲット
ラウドネス、たとえば、多くのゲームでは約 -14 ～ -16 LUFS を目指します)。
4. サイドチェーン コンプレッサー (またはボリューム オートメーション) を使用して **競合ソースをダッキング**:
音声/重要な SFX が再生されると、音楽バスが低下し、その後回復します。
5. *垂直* レイヤリング (ステムのフェードイン/フェードアウト) および/または
*水平* 再シーケンス (音楽の境界でセグメントを交換) により、**音楽をアダプティブにします**。
リファレンスを参照してください。
6. **小さなランダムなピッチ/ボリューム オフセットとサンプル プール
を使用して、繰り返される SFX を変化させます**。これにより、足音や打撃がロボットのように聞こえなくなります。
7. **実際の出力で確認します。** ヘッドフォンとスピーカーで聞いてください。
ミックスのバランスが取れているか、ダッキングは聞こえるがポンピングはしていないこと、音楽のトランジションがビートに合わせて
になっているかを確認してください。エディターのメーターだけから推測しないでください。

 ## パターン

 ### 1. バス ルーティングと dB ゲイン

```gdscript
# Route sounds to named buses; control GROUPS, not individual clips.
sfx_player.bus = "SFX"
music_player.bus = "Music"

# Map a 0..1 settings slider to decibels (linear_to_db), the perceptual unit.
func set_bus_volume(bus_name: String, slider01: float) -> void:
    var idx := AudioServer.get_bus_index(bus_name)
    var db := linear_to_db(clamp(slider01, 0.0001, 1.0))   # 0 -> silence, 1 -> 0 dB
    AudioServer.set_bus_volume_db(idx, db)
# RIGHT: slider -> dB via linear_to_db. WRONG: assigning slider01 straight as dB
# (a "0.5" would be only +0.5 dB — almost no change — and 0 would be 0 dB, full).
```

### 2. サイドチェーン経由のダッキング (音声の下に音楽が入ります)

```gdscript
# A compressor on the MUSIC bus, keyed by the VOICE bus, lowers music while
# dialogue plays, then releases. This is "sidechain ducking".
# Setup (engine-specific): add a compressor effect to the Music bus and set its
# sidechain to the Voice bus. Then tune:
#   threshold: level on Voice that triggers ducking (e.g. -30 dB)
#   ratio:     how hard to duck (e.g. 8:1 for a clear dip)
#   attack:    fast (~10 ms) so music gets out of the way promptly
#   release:   slow (~300-500 ms) so it recovers smoothly, not pumping
# No-middleware alternative: tween the Music bus volume down on voice start and
# back up on voice end.
func duck_music(active: bool) -> void:
    var target_db := -12.0 if active else 0.0
    create_tween().tween_method(
        func(v): set_bus_volume_db("Music", v), current_music_db, target_db, 0.25)
```

### 3. SFX バリエーション (「マシンガン」の繰り返しを殺す)

```gdscript
# Randomize pitch slightly and pick from a sample pool so repeats feel organic.
func play_varied(samples: Array, bus := "SFX") -> void:
    var p := AudioStreamPlayer.new()
    p.stream = samples[randi() % samples.size()]   # rotate through several takes
    p.bus = bus
    p.pitch_scale = randf_range(0.94, 1.06)         # +/- ~6% pitch wobble
    add_child(p); p.play()
    p.finished.connect(p.queue_free)                # clean up one-shots
```

### 4. ビート同期イベント (ミュージック グリッドにクオンタイズ)

```gdscript
# Schedule gameplay/visuals on musical time, not frame time, so they land on beat.
const BPM := 120.0
var seconds_per_beat := 60.0 / BPM

func current_beat(playback_position_sec: float) -> int:
    return int(playback_position_sec / seconds_per_beat)

# Quantize an action to the NEXT beat boundary instead of firing immediately.
func time_until_next_beat(pos: float) -> float:
    return seconds_per_beat - fmod(pos, seconds_per_beat)
# Drive timing from the audio playback clock, which is steadier than frame delta.
```

## 落とし穴

 - **スライダー値を dB として扱います。** 音量は対数です。 `0..1` から
`linear_to_db` までをマップします (そして `db_to_linear` で戻ります)。生の振幅
のリニア スライダーは、一番下まで何もしないように感じます。
- **バスではなくクリップごとのボリューム**により、グローバル バランス パスが不可能になり、
 の保存/設定が肥大化します。バスでミックス。
- **マスターをクリッピングしています。** 合計されたサウンドが 0 dBFS を超え、歪みます。
のヘッドルームを残します。ミキサーとしてではなく、セーフティネットとしてマスターにリミッターを設定します。
- **ポンピング ダッキング**: リリースが速すぎるか、レシオが高すぎると、音楽が
の息づかいのように聞こえるようになります。リリースを延長します。比率が低くなります。
- **ゲーム全体で単一の音楽トラックをループ**すると、平坦な感じがします。状態に応答するレイヤーまたは
セグメントを使用します (リファレンスを参照)。
- **ビート同期オフフレーム時間。** `delta` がドリフトします。 **オーディオ再生の
位置**を読み取り、音楽のタイミングを確認し、出力遅延を考慮します。
- **無制限のワンショット プレーヤー**:
を解放せずに AudioStreamPlayers を生成すると、リークが発生します。 `finished` では無料、または小さなプールを使用します。

 ## リファレンス

 - `references/adaptive-music.md` — 垂直レイヤリングと水平再シーケンス、
 トランジション タイミング (バー/クオンタイズ)、スティンガー、インテンシティ マッピング、クロスフェード。

 ## 関連スキル

 - `godot-audio` — バス、`AudioStreamPlayer`、エフェクト、Godot の同期とビート。
- `input-systems` — 入力アクションからオーディオをトリガーします。
- `physics-tuning` — 衝撃 SFX を引き起こす衝突イベント。
- `platformer`、`roguelike` — オーディオフィードバックに基づいた雰囲気のジャンル。 
