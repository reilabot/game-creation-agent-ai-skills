# プロファイリングと予算 — `performance-optimization` の深さ

 本文の詳細はここにあります: エンジンごとのプロファイラーのウォークスルー、CPU 対 GPU トリアージ フロー、
 プーリング マネージャー、バッチ化/インスタンス化ルール、割り当て/GC ガイダンス、LOD/カリング、アセット
予算。 **Godot 4.7**、**Unity 6.3 LTS**、**Unreal 5.8** をターゲットとしています。

 ## 1. CPU 対 GPU のトリアージ (修正する前に決定)

```text
1. Read total frame time vs your budget (16.67 ms @60).
2. Compare CPU-frame time and GPU-frame time:
     GPU >> CPU  → GPU-bound  → draw calls, overdraw, shader cost, resolution, lights/shadows.
     CPU >> GPU  → CPU-bound  → scripts, physics, pathfinding, allocations/GC, too many nodes.
     Both high / alternating → find the per-frame spike in the timeline (one function/system).
3. Within the bound side, sort costs descending and attack the top one only.
4. Re-measure. If it didn't move the frame time, you fixed the wrong thing — revert and re-triage.
```

GPU 依存のゲームは、より高速な C# からは高速化されません。 CPU に依存するゲームは、描画
呼び出しが減っても高速化されません。この分割は、パフォーマンス作業において最も重要な決定です。

 ## 2. エンジンごとのプロファイラー クイック スタート

 **Godot 4.7**
- エディター: **デバッガー ▸ プロファイラー** (関数ごとのスクリプト + 物理時間、フレーム時間)、および
**モニター** タブ (FPS、描画コール、ビデオ/静的メモリ、オブジェクト/ノード数)。
- コード: `Performance.get_monitor(Performance.TIME_PROCESS)` (プロセスミリ秒)、
 `Performance.TIME_PHYSICS_PROCESS`、`Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME`、
 `Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME`、`Performance.MEMORY_STATIC`。
- ビジュアル デバッグ: ビューポート **情報の表示/フレーム時間の表示** オーバーレイ。

 **Unity 6.3 LTS**
- **プロファイラー** ウィンドウ: CPU 使用率、GPU 使用率、レンダリング、メモリ モジュール。 **ディープ プロファイル**
は慎重に使用してください (オーバーヘッドが高く、数値が歪められます)。
- **フレーム デバッガー**。描画呼び出しを段階的に実行し、バッチ処理 (SetPass 呼び出し、バッチ) を中断するものを確認します。
- コード: `ProfilerRecorder` `"CPU Main Thread Frame Time"` を追跡 (Unity 6.3 LTS000 マニュアル)、
 内蔵 HUD/CSV 用。 CPU/GPU フレーム時間の場合は `FrameTimingManager`。
- **エディターだけでなく、デバイス上で開発ビルドをプロファイリング** (`Autoconnect Profiler`)。

 **Unreal 5**
- コンソール: `stat unit` (フレーム / ゲーム / 描画 / GPU ms)、`stat fps`、`stat scenerendering`
(描画呼び出し、プリミティブ)、`stat game`、 `stat gpu`。
- 完全なタイムライン トレースのための **Unreal Insights**。 GPU の故障の場合は、`ProfileGPU` (Ctrl+Shift+,)。

 ## 3. プーリング マネージャー (汎用)

```text
class Pool<T>:
    free: list
    create_fn, reset_fn
    prewarm(n):  for n → free.push(create_fn())          # allocate up front, off the hot path
    acquire():   t = free.pop() or create_fn(); activate(t); return t
    release(t):  reset_fn(t); deactivate(t); free.push(t)  # never destroy; recycle
```

弾丸、砲弾、パーティクル、ダメージ数値、ウェーブ中の
敵、オーディオ ワンショットなど、頻繁かつ短期間にスポーンされるあらゆるものをプールします。初めて使用する際のトラブルを避けるために、負荷時に予熱してください。プールに上限を設け、
 がオーバーフロー ポリシー (拡張するか、最も古いものをリサイクルする) を決定します。

 ## 4. バッチ処理とインスタンス化のルール

 - **バッチを壊すもの:** オブジェクト間の異なるマテリアル、テクスチャ、またはレンダリング状態。
マテリアルと **アトラス** テクスチャを共有すると、オブジェクトの実行が 1 回の描画呼び出しとして送信されます。
- **同一のメッシュ、多数のインスタンス** → GPU インスタンス化: Unity (
 マテリアルで *GPU インスタンス化* を有効にする) / Godot `MultiMesh` + `MultiMeshInstance2D/3D` / Unreal インスタンス化スタティック メッシュまたは
階層 ISM。
- **静的ジオメトリ** → 静的バッチ処理 (Unity)、静的としてマーク。可能な限り焼きます。
- **2D** → テクスチャ アトラス + 共有マテリアル バッチ スプライト;スプライトごとのマテリアルは避けてください。
- **UI** → キャンバスの再構築を最小限に抑えます (Unity: 静的/動的キャンバスを分割)。要素
の変更によってキャンバス全体が汚されてはなりません。
- **ライト/シャドウ** → 静的ライティングをベイク処理します。リアルタイムシャドウキャスターをキャップします。小さな影を取り除きます。

 ## 5. 割り当て / GC ガイダンス

 - **C# (Unity):** フレームごとの `new` なし、`Update` の LINQ なし、ボックス化を回避 (例: 辞書
キーとしての `enum`)、使用します。 `NonAlloc` 物理クエリ、`List`/配列を再利用 (`Clear()` は realloc ではありません)、小さなホット データには
構造体を優先し、`GetComponent`/`Find` 結果をキャッシュします。目標は、定常状態で **0 B GC.Alloc per
Frame** です。
- **GDScript (Godot):** `_process` ごとに新しい `Array`/`Dictionary` をビルドしないでください。再利用;型付き
配列を好みます。タイマー/シグナルに属する `_process` での負荷の高い作業を避けてください。
- **一般:** 文字列は古典的な隠しアロケーター (連結、書式設定) です。文字列を構築することはほとんどありません。
 は、結果をキャッシュします。

 ## 6. 不要なテクニック (アルゴリズムの勝利)

 - **実行頻度を下げる:** AI/HUD/高価なチェックを
フレームごとではなく、タイマーまたは N フレームごとに更新します。フレーム間でずらして表示します (タイムスライス)。
- **空間パーティション:** グリッド/四分木/八分木のため、クエリはすべての N ではなく、近くのオブジェクトのみに接触します。
- **LOD とカリング:** 遠くの詳細が低くなります。錐台/オクルージョンカリング。画面外の
遠方のエンティティをデスポーンします。
- **結果のキャッシュ:** 経路探索、見通し線、派生データをメモ化します。変更すると無効になります。
- **延期/償却:** プロシージャル生成と読み込みをフレーム全体に分散して、スパイクを回避します。

 ## 7. 資産予算 (ソースでの回帰の防止)

 |資産 |一般的なデスクトップの予算 |モバイルの予算 |メモ |
|------|----------------------|---------------|------|
|テクスチャの最大サイズ | 2048–4096 | 1024–2048 |ミップマップを使用します。圧縮 (BCn / ASTC) |
|三角形の文字 | 30,000 – 80,000 | 5k～20k |距離の LOD |
|描画呼び出し/フレーム |数千台前半 |数百 |モバイルで最も重要なカウント |
|リアルタイム ライト |いくつか | 1–2 + ベイクド |残りを焼く |
|オーディオ |ストリーミング音楽、メモリ内の短い SFX |同じ |ロード時にすべてを解凍しないでください。

 モバイルには **サーマル スロットリング**が追加されています。2 分間 60 FPS に達してから低下するゲームは
オーバーヒートです。ヘッドルームを目標にし、フレーム レートを制限し、持続的な GPU 負荷を軽減します。 
