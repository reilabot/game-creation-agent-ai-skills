# MonoBehaviour ライフサイクルとコルーチン (Unity 6.3 LTS)

 `unity-csharp-scripting` スキルの深さ: 完全な実行順序と、メイン プレイブックに収まらないコルーチン
パターン。 Unityマニュアル
「イベント関数の実行順序」ページおよび`ScriptReference/MonoBehaviour`と照合して検証しました。

 ## 実行順序 (ゲームプレイにとって重要な部分)

 オブジェクトごとに、エンジンはこれらを次の順序で呼び出します。フェーズ |コールバック |走る | | に使用します。
|------|----------|------|---------|
|ロード | `Awake` |オブジェクトのロード時に 1 回 (無効な場合でも) | `GetComponent` をキャッシュ、自己セットアップ |
|有効にする | `OnEnable` |オブジェクト/スクリプトが有効になるたびに |イベントをサブスクライブし、コルーチンを再準備する |
|初期化 | `Start` | 1 回、最初の `Update` の前、各 `Awake` の後 |他のオブジェクトに依存する配線 |
|物理学 | `FixedUpdate` |固定ステップごと (デフォルトは 0.02 秒) |剛体力、`MovePosition` |
|物理学 | `OnTriggerXXX` / `OnCollisionXXX` |物理ステップ中 |衝突/トリガー応答 |
|フレーム | `Update` |レンダリングされたフレームごとに 1 回 |入力ポーリング、非物理ロジック |
|フレーム | `LateUpdate` |フレームごとに 1 回、すべての `Update` の後 |カメラフォロー、IK修正 |
|無効にする | `OnDisable` |オブジェクト/スクリプトが無効になるたびに |イベントの購読を解除する |
|分解 | `OnDestroy` |破壊されたときに一度 |ネイティブ ハンドルを解放し、保存します。

 主な結果:

 - `FixedUpdate` は、フレーム レートに応じて、フレームごとに 0 回、1 回、または数回実行される可能性があります。
は、そこで生の「フレームごと」入力を読み取ることはありません。それを `Update` で読み取り、`FixedUpdate` で消費します。
- すべての `Awake` 呼び出しは、`Start` より前に終了します。プロジェクト設定でスクリプトの実行順序を設定しない限り、`Awake` 間 (および `Start` 間) の順序は
不定です。
- `OnEnable` は、最初の有効化時に `Awake` の後に実行され、その後、再有効化するたびに再度実行されます。すべての
`OnEnable` サブスクリプションと `OnDisable` サブスクリプション解除を組み合わせて、ハンドラーの重複を回避します。

 ## コルーチン生成命令

```csharp
yield return null;                          // resume at the start of the next frame
yield return new WaitForSeconds(2f);        // wait 2s of scaled game time (affected by Time.timeScale)
yield return new WaitForSecondsRealtime(2f);// wait 2s of real time (ignores timeScale; good for pause menus)
yield return new WaitForFixedUpdate();      // resume after the next physics step
yield return new WaitUntil(() => isReady);  // resume once the predicate is true
yield return new WaitWhile(() => isLoading);// resume once the predicate is false
yield return StartCoroutine(OtherRoutine());// run a nested coroutine to completion first
```

## コルーチンを決定的に停止する

 適切なルーチンを正確に停止できるように、ハンドルを保持しておいてください:

```csharp
private Coroutine _spawnLoop;

private void OnEnable()  => _spawnLoop = StartCoroutine(SpawnLoop());
private void OnDisable() { if (_spawnLoop != null) StopCoroutine(_spawnLoop); }

private System.Collections.IEnumerator SpawnLoop()
{
    var wait = new WaitForSeconds(1f);      // allocate once, reuse — avoids per-iteration GC
    while (true)
    {
        Spawn();
        yield return wait;
    }
}
```

`StopAllCoroutines()` は、MonoBehaviour 上のすべてのコルーチンを停止します。便利ですが、単刀直入です。
は、1 つのオブジェクトで複数のルーチンが実行されている場合、ハンドルによる停止を優先します。

 ## カスタム譲歩命令

 再利用可能な待ち条件が必要な場合:

```csharp
public class WaitForAnimationEnd : CustomYieldInstruction
{
    private readonly Animator _a;
    private readonly int _layer;
    public WaitForAnimationEnd(Animator a, int layer = 0) { _a = a; _layer = layer; }
    // keepWaiting == true means "keep yielding"; false resumes the coroutine.
    public override bool keepWaiting => _a.GetCurrentAnimatorStateInfo(_layer).normalizedTime < 1f;
}
```

## 注意点

 - ゲームオブジェクトが **非アクティブ化** (`SetActive(false)`) するか、
 スクリプトが破棄されると、コルーチンは強制終了されます。ただし、オブジェクト
がアクティブのままでスクリプト コンポーネントのみが無効になっている場合は、*強制終了されません。必要に応じて、`OnEnable` を再装備します。
- `Awake` から開始されたコルーチンは、オブジェクトが
アクティブになり、スクリプトが有効になるまで、最初の `yield` を超えて進みません。 `OnEnable`/`Start` でループを開始することを優先します。
- ループ反復ごとに `new WaitForSeconds(x)` を割り当てるとガベージが作成されます。インスタンスをキャッシュします。 
