---
name: unity-csharp-scripting
description: >
  Write Unity 6.3 LTS C# gameplay scripts: the MonoBehaviour lifecycle
  (Awake/OnEnable/Start/Update/FixedUpdate/LateUpdate), GameObject and component
  access, coroutines, and Inspector serialization. Use when creating or editing .cs
  scripts in a Unity project, or when the user mentions MonoBehaviour, Start/Update,
  GetComponent, SerializeField, coroutines, or "Unity script".
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # Unity C# スクリプト (MonoBehaviour)

 Unity 6 で正しく慣用的なゲームプレイ スクリプトを作成します。ライフサイクル、コンポーネント
アクセス、シリアル化、およびコルーチンを正しく取得して、動作が決定的であり、
 インスペクターが有用であり続けるようにします。ターゲット **Unity 6.3 LTS (6000.3)**、C# / .NET Standard 2.1。

 ##

 を使用する場合 - `MonoBehaviour` を作成または修正するときに使用します。適切なライフサイクル コールバックの選択、コンポーネントの
読み取り/キャッシュ、インスペクターへのフィールドの公開、またはコルーチンを使用した時限ロジック
の実行です。
- プロジェクトに `*.cs` ファイル、`Assembly-CSharp` または `*.asmdef`、および
`ProjectSettings/` フォルダーがある場合に使用します。

 **使用しない場合:** リジッドボディの移動 / 衝突応答 → `unity-physics`;
プレーヤー入力を読み取り中 → `unity-input-system`;共有データ資産/構成 → `unity-scriptableobjects`;
アニメーターパラメータ → `unity-animation`。このスキルは、これらのサブシステムではなく、*スクリプト ライフサイクルと C#
配管*を所有します。

 ## コア ワークフロー

 1. **習慣ではなく目的によってコールバックを選択します。** `Awake` (キャッシュ参照、
 ロードで 1 回実行)、`OnEnable` (イベントのサブスクライブ)、`Start` (他のものに依存する初期化)オブジェクトの
`Awake`)、`Update` (フレームごとのロジック/入力ポーリング)、`FixedUpdate` (物理)、`LateUpdate`
(移動後のカメラ追跡)、`OnDisable`/`OnDestroy` (登録解除/クリーンアップ)。
2. **コンポーネント ルックアップを `Awake` にキャッシュします** — フレームごとに `GetComponent` を呼び出さないでください。
3. **調整パラメータはパブリック フィールドではなく、`[SerializeField] private`** で公開します。そのため、他のコード
は調整パラメータを変更できませんが、デザイナーはインスペクターで調整パラメータを編集できます。
4. **フレームごとの値を `Update` で `Time.deltaTime` によってスケールします** (および `Time.fixedDeltaTime`
セマンティクスは `FixedUpdate` で自動です)。
5. **時系列ロジックにコルーチンを使用します** (遅延、トゥイーン、「X を実行してから Y を実行する」)。
は `StartCoroutine` で開始し、決定的に停止します。
6. **プレイ モードで確認**: コンソールで null 参照例外がないか確認し、インスペクターで期待どおりに値
が更新されていることを確認し、`Update` がホットかどうかプロファイラーを監視します。

 ## パターン

 ### 1. ライフサイクル + キャッシュされたコンポーネント (正規のスケルトン)

```csharp
using UnityEngine;

[RequireComponent(typeof(Rigidbody))]      // auto-adds the dependency, prevents null refs
public class PlayerController : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 6f;   // editable in Inspector, private in code
    private Rigidbody _rb;                            // cached, not fetched per frame

    private void Awake() => _rb = GetComponent<Rigidbody>();  // cache once on load

    private void Update()
    {
        // Per-frame, non-physics work. Scale by deltaTime so it is frame-rate independent.
        transform.Rotate(0f, 90f * Time.deltaTime, 0f);
    }

    private void FixedUpdate()
    {
        // Physics work belongs here (fixed timestep). See the unity-physics skill.
        _rb.MovePosition(_rb.position + transform.forward * moveSpeed * Time.fixedDeltaTime);
    }
}
```

### 2. `TryGetComponent` による安全なコンポーネント アクセス

```csharp
// Avoids allocating a null and is clearer than GetComponent + null check.
if (other.TryGetComponent<Health>(out var health))
    health.Apply(-10);
```

### 3. インスペクターに正しく表示されるシリアル化

```csharp
[SerializeField, Range(0f, 1f)] private float volume = 0.8f;  // slider
[SerializeField] private string playerName = "Hero";          // private but serialized

[System.Serializable]                 // REQUIRED for a plain class to serialize/show
public class Stats { public int hp = 100; public int mana = 50; }

[SerializeField] private Stats stats = new();  // nested struct-like data in the Inspector
```

### 4. 時系列ロジックのコルーチン

```csharp
private void Start() => StartCoroutine(FlashThenHide());

private System.Collections.IEnumerator FlashThenHide()
{
    yield return new WaitForSeconds(0.5f);   // wait half a second of game time
    GetComponent<Renderer>().enabled = false;
    yield return null;                       // resume next frame
}
```

## 落とし穴

 - **`GetComponent` in `Update`** — すべてのフレームとタンクのパフォーマンスを検索します。
参照を `Awake`/`Start` にキャッシュします。
- **`Update` の物理** - 力を加えて `Rigidbody` を移動するか、`MovePosition` を
`FixedUpdate` の外に移動すると、ジッターとタイムステップに依存する動作が発生します。 `Update` で入力を読み取り、
 で `FixedUpdate` に物理演算を適用します。
- **オブジェクト全体の `Start` の順序に依存** — `Start` は *すべての* `Awake` の後に実行されますが、`Start` 間の
の順序は未定義です。 `Start`でオブジェクト間配線を行い、`Awake`でセルフセットアップを行います。
- **インスペクターに表示するためだけの `public` フィールド** — これにより、任意のスクリプトで
を変更することもできます。代わりに `[SerializeField] private` を使用してください。
- **`gameObject.tag == "Enemy"`** は文字列を割り当てるため、速度が遅くなります。
`gameObject.CompareTag("Enemy")` を使用します。
- **ゲームオブジェクトが無効になるとコルーチンが停止します** — 無効になったオブジェクトのコルーチンは
強制終了されます。トグルを継続する必要がある場合は、`OnEnable` で `StartCoroutine` を再実行します。
- **`Update` は `Start` より前に実行されることはありませんが、*最初の* `Update` は `Start`** と同じ
フレーム上で実行できます。これにより、セットアップを奇妙に分割した場合に、まだ初期化されていないフィールドを防ぐことができます。

 ## 参照

 - 完全なイベント実行順序テーブルと高度なコルーチン パターン (カスタム
`CustomYieldInstruction`、ハンドルによる停止、`WaitUntil`/`WaitWhile`) については、
 を参照してください。 `references/lifecycle-and-coroutines.md`。
- 主なドキュメント: Unity マニュアル「イベント関数の実行順序」
(`https://docs.unity3d.com/Manual/execution-order.html`) および `ScriptReference/MonoBehaviour`。

 ## 関連スキル

 - `unity-physics` — `Rigidbody`、衝突、および `FixedUpdate` モーション。
- `unity-input-system` — これらのスクリプトへのプレーヤー入力の読み取り。
- `unity-scriptableobjects` — シングルトンを使用せずにスクリプト間でデータ/構成を共有します。 
