# フェイザー シーン フロー (フェイザー 4.2、コア ライフサイクルは 3.90 にも適用されます)

 シーン マネージャーは、小さなステート マシンを通じてすべてのシーンを実行します。どの
遷移動詞が実行するのかを知ることで、最も一般的なフェイザーのバグ (非表示のシーン、再起動後の
の古い状態、イベント リスナーの重複) を防ぐことができます。

 ## ライフサイクル順序

 シーンは **1 回起動** (ステータス `INIT`) し、**
 回何度でも起動**できます。起動するたびに次のように実行されます:

```
start → (loading, if preload queued anything) → create → running
```

- `init(data)` — すべての起動時に最初に実行されます。 **ここで実行固有の状態をリセットします。**
- `preload()` — アセットのダウンロードをキューに入れます。オプション。
- `create(data)` — ゲーム オブジェクトを構築します。 `preload` にキューに入れられたアセットの準備が整いました。
- `update(time, delta)` — シーンが `running` の間、フレームごとに呼び出されます。

 同じ `data` オブジェクトが、
 `scene.start(key, data)` / `scene.launch(key, data)` から `init` および `create` に渡されます。

 ## 遷移動詞

 |方法 |ターゲットへの影響 |発信者への影響 |
|--------|---------------|------|
| `start(key, data)` |開始 (または再起動) | **発信者を停止** |
| `launch(key, data)` |並行して開始 |呼び出し元は実行を続けます |
| `switch(key)` |開始またはウェイク |発信者を**寝て** |
| `pause(key?)` |更新を停止し、レンダリングを続けます | — |
| `resume(key?)` |更新を再開 | — |
| `sleep(key?)` |更新とレンダリングを停止し、状態を維持します。 — |
| `wake(key?)` |睡眠シーンを再開する | — |
| `stop(key?)` |シャットダウン (オブジェクトを解放) | — |

 経験則:

 - **HUD/オーバーレイ** → `launch` 1 回。後のシーンは後で
を描画するため、上にレンダリングされます。 `start` ではなく、`setVisible()` または `sleep`/`wake` に切り替えます。
- **モーダル一時停止メニュー** → `pause` はゲームプレイ シーン、`launch` はメニュー;クローズ時は`resume` 
。
- **タイトル ⇄ 再訪するゲームプレイ** → 再初期化にコストがかかる場合は、`stop`/`start` (毎回新鮮) よりも `sleep`/`wake` (状態が保持され、
 を 1 回だけ開始) を優先します。

 ## 再起動状態のバグ

 シーンは長期間存続するインスタンスです。コンストラクターで設定されたフィールドは **1 回**、
 に設定されるため、再起動後も最後の値が保持されます:

```js
// WRONG — gameOver stays true forever after the first game over.
export default class Play extends Phaser.Scene {
  constructor() {
    super('play');
    this.gameOver = false;   // runs once, never again
  }
}

// RIGHT — init() runs on every (re)start.
export default class Play extends Phaser.Scene {
  constructor() { super('play'); }
  init() { this.gameOver = false; }
}
```

同じことが、ゲーム オブジェクトを収集するモジュール レベルの配列にも当てはまります。
 `shutdown` でクリアしないと、前回の実行で破壊されたオブジェクトが保持されます。

```js
create() {
  this.enemies = [];
  // Clean up when the scene stops so the next run starts empty.
  this.events.once('shutdown', () => { this.enemies.length = 0; });
}
```

## リスナーの重複

 **グローバル** エミッター (レジストリ、入力
マネージャー、別のシーン) の `create` で追加されたリスナーは、シーンの再起動後も存続し、スタックされます。次のいずれか:

 - `.once(...)` で追加するか、または
- `shutdown` で削除します:

```js
create() {
  const onChange = (p, v) => this.refresh(v);
  this.registry.events.on('changedata-coins', onChange);
  this.events.once('shutdown', () => {
    this.registry.events.off('changedata-coins', onChange);
  });
}
```

## シーンの削除または置換

 オリジナルが破棄されるまで、シーン キーを再利用することはできません。同じキーの下でインスタンス
を交換するには、シャットダウンが完了した後にインスタンスを削除します:

```js
this.scene.remove('level'); // remove by key
// then later
this.scene.add('level', NewLevelScene, true); // true = autostart
```

キーを操作する代わりに便利な方法は、アクティブなレベルのキーを
レジストリに保存し、その値によって追加/削除することです。 
