---
name: performance-optimization
description: >
  Find and fix game performance problems methodically — measure with the engine profiler first,
  reason about the frame-time budget, locate the CPU-vs-GPU bottleneck, then apply the right fix:
  object pooling, draw-call batching, fewer allocations/GC spikes, and asset budgets. Engine-
  neutral method that pairs with each engine's profiler. Use when the user mentions performance,
  optimize, low/dropping FPS, frame drops, stutter, lag, profiler, frame budget, draw calls,
  batching, garbage collection/GC spikes, object pooling, or "the game runs slow".
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # パフォーマンスの最適化

 パフォーマンスの作業は測定の規律であり、コツを詰め込んだものではありません。方法は常に
と同じです。**プロファイル → 1 つのボトルネックを見つけて → それを修正 → 再度測定**。このスキルは、
 ループと最もレバレッジの高い修正 (プーリング、バッチ処理、割り当て制御、資産予算) を教え、
 が各エンジンのプロファイラーを示します。シミュレーション コストとして `physics-tuning` と組み合わせます。

 ##

 を使用する場合 - フレーム レートが低いか不均一である場合、ゲームが途切れたり途切れたりする場合、またはターゲット
(デスクトップ 60 FPS、モバイル 30/60) に到達する必要があり、現在はヒットしていない場合に使用します。
- 「何を」最適化するかを決定するために使用します。コードを変更する前に、プロファイルを作成し、フレーム バジェットを読み取り、ボトルネックが CPU
か GPU かを特定します。
- 特定の修正を適用するために使用します: オブジェクト プーリング、描画呼び出し/バッチ削減、フレームごとの
割り当てと GC スパイクの削除、アセット予算の設定。

 **使用しない*場合:** 特に物理ジッター/トンネリング/タイムステップには、`physics-tuning` を使用します。
エンジンの具体的なプロファイラー UI とレンダリング設定については、その
エンジン スキルを使用します (`godot-export` は一部のビルド設定をカバーし、エンジン コアは残りをカバーします)。このスキル
は、クロスエンジン方式であり、共有修正です。

 ## 黄金律: 最初に測定し、決して推測しない

 プロファイリングなしで適用されるほとんどのパフォーマンス「修正」は、間違った対象をターゲットにしており、複雑さが増し、
 の利益は得られません。 **測定していないコードを最適化しないでください。** プロファイラーを開き、代表的なハードウェア上の代表的なシーンで単一の
最大コストを見つけて、それを修正します。次に進む前に、
 まで再測定して、修正が役に立ったことを確認してください。重要な場合は **リリース/最適化ビルド** をプロファイリングします。
 エディターとデバッグ ビルドは存在します (エディターのオーバーヘッド、コンパイラーの最適化なし)。

 ## コア ワークフロー

 1. **ターゲットを定義して再現します。** 目標 (例: 60 FPS = 16.67 ミリ秒/フレーム) を示し、
 で再現可能な最悪のケースのシーンを見つけます。 「時々遅い」は修正できません。再現可能なスパイクは修正可能です。
2. **コードに触れる前にプロファイルを作成します。** エンジン プロファイラーを実行し、フレームを読み取ります。合計フレーム
時間、および CPU (ゲーム ロジック、物理学、スクリプト) と GPU (レンダリング) 間の分割。
3. **ボトルネックを見つけます — CPU または GPU。** GPU 時間 ≫ CPU の場合、描画コール/オーバードロー/シェーダー/
解像度を攻撃します。 CPU 時間が支配的な場合は、スクリプト/物理/割り当てを攻撃します。間違った側の
を修正しても何も起こりません。
4. **単一の最大コストを修正します。** ホット ラインを微細に最適化するよりも、**アルゴリズム** の勝利 (作業、キャッシュ、空間
パーティションの削減、実行頻度の削減) を優先します。一致する共有修正
(プーリング、バッチ処理、割り当ての削除) を適用します。
5. **同じシーン/ハードウェアで再測定します。** 移動した番号を確認します。直感ではなく、
 データに基づいて保持または元に戻します。
6. **固定されたままになるようにバジェットを設定します。** サブシステムごとのフレームごとのミリ秒バジェット、およびアセット バジェット
(テクスチャ サイズ、トライアングル数、描画呼び出しの上限)。検証にパフォーマンス チェックを追加します。
7. **測定された数値をレポートします。** フレーム時間の前後の状態、見つかったボトルネック、および修正
— 決して「速くなるべき」ではありません。エディター内でしか測定できない場合は、そう言ってください。

 ## パターン

 ### 1. フレーム予算の計算 (「遅いと感じる」を数値に変換)

```text
target FPS → frame budget:   60 FPS = 16.67 ms   |   30 FPS = 33.3 ms   |   120 FPS = 8.33 ms
The WHOLE frame (CPU sim + render submit + GPU) must fit the budget; the GPU runs in parallel,
so the slower of CPU-frame and GPU-frame sets your FPS. Allocate sub-budgets, e.g. @60 FPS:
  gameplay/scripts ~5 ms · physics ~3 ms · rendering(CPU submit) ~4 ms · UI/other ~2 ms · slack.
If one subsystem blows its slice, that's your target — not whatever you assumed.
```

### 2. エンジン プロファイラーで測定します (修正の前にこれを実行します)

```text
Godot 4.7 : Debugger ▸ Profiler (script/physics time) and Monitors tab (FPS, draw calls, memory).
            In code: Performance.get_monitor(Performance.TIME_PROCESS) and
            Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME).
Unity 6.3 LTS   : Profiler window (CPU/GPU/Memory/Rendering modules) + Frame Debugger for draw calls.
            In code: a ProfilerRecorder tracking "CPU Main Thread Frame Time" for a HUD/log.
Unreal 5  : `stat unit` (Frame/Game/Draw/GPU ms), `stat fps`, `stat scenerendering` (draw calls);
            Unreal Insights for deep traces.
# Read the split: is the Draw/GPU line the biggest, or the Game/CPU line? That decides the fix.
```

### 3. オブジェクト プーリング (ホット ループでの割り当て/解放の停止)

```gdscript
# Bullets, particles, enemies, damage numbers: reuse a fixed set instead of instantiate()/free()
# every frame — that thrashes memory and (in C#) feeds the GC.
var _pool: Array[Node] = []
func acquire() -> Node:
    var n: Node = _pool.pop_back() if not _pool.is_empty() else bullet_scene.instantiate()
    n.set_process(true); n.visible = true
    return n
func release(n: Node) -> void:
    n.set_process(false); n.visible = false       # disable + hide; DON'T free
    _pool.append(n)                                # back to the pool for reuse
# RIGHT: pre-warm the pool at load; reuse. WRONG: instantiate()/queue_free() per shot.
```

### 4. ドローコールをカットする (最も一般的な GPU 側の利点)

```text
Each unique material/texture/state change is roughly a draw call; thousands of them stall the GPU.
- Atlas textures and share materials so sprites/meshes batch into one call.
- Identical meshes → GPU instancing (Unity), MultiMesh / MultiMeshInstance (Godot), Instanced
  Static Mesh (Unreal).
- Static geometry → static batching / baking; mark non-moving objects static.
- Reduce overdraw: limit large overlapping transparent/particle layers (they re-shade pixels).
- Fewer real-time lights/shadows; bake lighting where it doesn't move.
Measure draw calls before and after — the count should drop, and so should GPU frame time.
```

### 5. フレームごとの割り当てを強制終了します (GC スパイク = スタッター)

```csharp
// Unity 6.3 LTS (C#). Allocating every frame fills the managed heap; the GC then stalls a frame.
// WRONG (allocates each call): foreach (var e in FindObjectsOfType<Enemy>()) ...  // + LINQ, new[]
// RIGHT: cache references once, reuse buffers, avoid LINQ/boxing in Update.
void Update() {
    _hits = Physics.RaycastNonAlloc(ray, _hitBuffer);   // reuse a preallocated array
    for (int i = 0; i < _hits; i++) { /* ... */ }       // no per-frame allocation
}
// Godot/GDScript: avoid building new arrays/dictionaries every frame in _process; reuse them.
```

## 落とし穴

 - **プロファイリングを使用しない最適化** 直感的な原因は通常間違っています。まず、
 回ごとに測定します。
- **エディターのプロファイリング / デバッグ ビルド。** エディターのオーバーヘッドと最適化されていないコードは誤解を招きます。実数のターゲット ハードウェア上でビルドされたリリース
をプロファイルします。
- **間違った側面を修正します。** GPU がボトルネックである場合 (またはその逆の場合)、CPU コードをマイクロ最適化しても何も変わりません。まず CPU と GPU の分割を確認します。
- **アルゴリズムに対するマイクロ最適化。** O(n²) ループまたはフレームごとの
フルシーン クエリ時の関数の削減は実際のコストです。仕事を減らして、磨かないでください。
- **ホット ループでインスタンス化/解放します。** フレームごとに弾丸/パーティクルを生成および破棄すると、
 断片化と GC スパイクが発生します。それらをプールします。
- **フレームごとの割り当て / LINQ / `Update` のボックス化** (C#) GC フィード → 定期的なヒッチ。
キャッシュして再利用します。
- 固有のマテリアルとバッチ処理されていないスプライト/メッシュからの **描画呼び出し爆発**。アトラス、
 マテリアル、インスタンス、バッチを共有します。
- スタックされた透明/パーティクル/フルスクリーン効果の再シェーディング ピクセルからの **オーバードロー**。
- **予算がありません。** サブシステムごとのミリ秒と資産の上限がないと、パフォーマンスは静かに低下します。
は、ビルド/CI チェックでそれらを強制します。
- **最適化が早すぎます。** 楽しんだり測定したりする前に、プロトタイプのパフォーマンスを歪めないでください。

 ## 参照

 - エンジンごとのプロファイラーのウォークスルー、CPU 対 GPU トリアージ フローチャート、完全なプーリング
マネージャー、エンジンごとのバッチング/インスタンス化ルール、割り当て/GC ガイダンス、LOD/カリング、アセット
予算 (テクスチャ サイズ、トライアングル数、オーディオ、モバイルサーマル）、
 `references/profiling-and-budgets.md` を読み取ります。

 ## 関連スキル

 - `physics-tuning` — シミュレーション コスト、固定ステップ バジェット、スリープ ボディ、ブロードフェーズ レイヤー。
- `godot-export` — 測定されたパフォーマンスに影響を与える設定をリリース/ビルドします。
- `procedural-gen`、`game-ai` — 予算を設定して延期する一般的な CPU ホットスポット (生成、パス探索)。
- `roguelike`、`tower-defense`、`survival-crafting` — プーリング/予算が必要なエンティティの多いジャンル。 
