---
name: pixijs-rendering
description: >
  Build a PixiJS v8 render layer: create the async Application, load textures with
  Assets, compose the scene graph with Container and Sprite, drive the ticker loop,
  wire pointer events, and group draws with render groups. Use when building or
  debugging PixiJS v8 — when the user mentions PixiJS, Pixi, Application, app.stage,
  Container, Sprite, Assets.load, app.ticker, or eventMode. Pins the v8 async
  init() API.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # PixiJS 8.19 レンダリング

 PixiJS **8.19** アプリケーションをセットアップして構造化します: 非同期 `Application`、`Assets` 経由のアセット
ロード、`Container`/`Sprite` シーン グラフ、ティッカー ループ、
ポインター イベント、およびレンダリング グループ。 8.19 API (非同期 `init`、統合
`Assets`、`eventMode`) を固定します。

 ##

 を使用する場合 - PixiJS v8 プロジェクトの開始、空のキャンバスの修正、
 表示リストの構築、テクスチャのロード、ティッカーによるアニメーション化、またはポインター
入力の処理時に使用します。
- `package.json` が `pixi.js` (v8) に依存しており、コードが
`import { Application } from 'pixi.js'` を実行する場合に使用します。

 **使用しない場合:** フェイザーのシーン/ローダー モデル → `phaser-core`。 3D シーン →
`threejs-scene-setup`。 PixiJS v7 以前のコード (同期 `new
Application({...})`, `Loader`, `interactive = true`) は、最初に v8 への移行が必要です。
このスキルは v8 のみを対象としています。

 ## コア ワークフロー

 1. **アプリケーションを作成し、`await` します。** v8 では、`new Application()` は空です。
構成は `await app.init({...})` で行われます。 `app.canvas` (
 `app.view` ではない) を DOM に追加します。バンドラーの非同期関数でトップレベルの `await` をラップします。
2. **`Assets` でアセットをロードします。** `await Assets.load(url)` は `Texture` を返します。
の多くのアセットの場合は、マニフェスト/バンドルを登録し、名前でロードします。 v7 `Loader` はありません。
3. **シーン グラフを構築します。** すべては `app.stage` (`Container`) から派生します。
`Container` の関連オブジェクトをグループ化します。子の変換は、親
に対して相対的です。描画順 = 挿入順 (後 = 上)。
4. **ティッカーでアニメーション化します。** `app.ticker.add((ticker) => {...})`。
`ticker.deltaTime` (フレーム、60fps で ~1) または `ticker.deltaMS` (ミリ秒) によってモーションをスケールするため、
 の速度はフレームレートに依存しません。
5. `eventMode = 'static'` (または `'dynamic'`)、
、`obj.on('pointerdown', ...)` を設定して **オブジェクトごとのイベントを有効にします**。フェデレーション ポインター イベントはマウス/タッチ/ペンをカバーします。
6. **大きな静的サブツリーをレンダリング グループにプロモート** (`isRenderGroup: true`) し、
 GPU がその変換をキャッシュします。前後のプロフィール。画面上のピクセルを確認します。

 ## パターン

 ### 1. アプリケーションの非同期ブート (v8 エントリ ポイント)

```js
import { Application, Assets, Sprite } from 'pixi.js';

(async () => {
  // v8: construct empty, then await init(). Config does NOT go in the constructor.
  const app = new Application();
  await app.init({
    background: '#1099bb',
    resizeTo: window,        // track the window size
    antialias: true,
    // preference: 'webgpu',  // opt into WebGPU; default 'webgl'
  });

  document.body.appendChild(app.canvas); // v8 uses app.canvas, not app.view

  const texture = await Assets.load('https://pixijs.com/assets/bunny.png');
  const bunny = new Sprite(texture);
  bunny.anchor.set(0.5);
  bunny.position.set(app.screen.width / 2, app.screen.height / 2);
  app.stage.addChild(bunny);
})();
```

### 2. 相対変換シーン グラフのコンテナー

```js
import { Container, Sprite } from 'pixi.js';

const world = new Container();
app.stage.addChild(world);

// Children are positioned relative to `world`; move/scale/rotate the whole group
// by transforming the parent.
for (let i = 0; i < 10; i++) {
  const coin = new Sprite(coinTexture);
  coin.x = i * 40;
  world.addChild(coin);
}
world.position.set(100, 100);
world.scale.set(2);            // every coin scales with the container
```

### 3. ティッカー ループ (フレームレートに依存しない)

```js
let elapsed = 0;
app.ticker.add((ticker) => {
  // deltaTime ≈ 1 at 60fps; deltaMS is milliseconds since last frame.
  elapsed += ticker.deltaMS;
  bunny.rotation += 0.05 * ticker.deltaTime;          // smooth at any frame rate
  bunny.y = app.screen.height / 2 + Math.sin(elapsed / 500) * 50;
});
```

### 4. ポインター イベント (フェデレーテッド)

```js
bunny.eventMode = 'static';   // 'static' = interactive, doesn't move on its own
bunny.cursor = 'pointer';
bunny.on('pointerdown', (event) => {
  bunny.tint = 0xff0000;
  // event.global is the pointer position in stage space.
});
bunny.on('pointerover', () => bunny.scale.set(1.1));
bunny.on('pointerout',  () => bunny.scale.set(1.0));
```

### 5. 多くのアセットを名前でロードする (バンドル)

```js
import { Assets } from 'pixi.js';

await Assets.init({
  manifest: {
    bundles: [{
      name: 'level-1',
      assets: [
        { alias: 'hero',  src: 'assets/hero.png' },
        { alias: 'tiles', src: 'assets/tiles.png' },
      ],
    }],
  },
});

const bundle = await Assets.loadBundle('level-1'); // { hero: Texture, tiles: Texture }
const hero = new Sprite(bundle.hero);
```

### 6. 大規模な静的レイヤーのレンダー グループ

```js
// A big, rarely-changing background subtree: let the GPU cache its transforms.
const background = new Container({ isRenderGroup: true });
app.stage.addChild(background);
// Add hundreds of static tiles to `background`. Moving `background` itself stays
// cheap; constantly re-adding/removing children negates the benefit.
```

## 落とし穴

 - **空白のキャンバス / "app.stage は未定義です"** → `await app.init()` をしていないか、
 がコンストラクターを構成しました。 v8 ではコンストラクターは空です。すべてのオプションは
`init()` に移動します。
- **`app.view` は未定義です** → v8 では `app.canvas` に名前が変更されました。
- **v7 コードスロー** → `interactive = true` → `eventMode = 'static'`; `Loader`/
`loader.add` → `Assets.load`;同期`new Application({...})`→非同期`init`。
- **トップレベルの待機ビルド エラー (Vite ≤6.0.6)** → `(async () => { ... })()` でブートをラップします。
- **速度はフレーム レートによって異なります** → 動きに `ticker.deltaTime` を掛けます (または
`deltaMS` を使用します)。 60fps を想定しないでください。
- **クリックしても何も起こりません** → オブジェクトの `eventMode` は `'none'` (デフォルト) のままです。
は、`'static'` または `'dynamic'` に設定します。
- **ピクセル アートでテクスチャがぼやけて見える** →
`texture.source.scaleMode = 'nearest'` を設定します (またはロード時に渡します)。
- **メモリが増加** → `removeChild` は GPU メモリを解放しません。使い終わったアセットについては、
 `sprite.destroy()` および `Assets.unload(url)` を呼び出します。

 ## 参照

 - テクスチャ/アセット パイプライン (スプライト シート/アトラス、`Assets.add`、背景
のロード、アンロード) および Graphics/Text/`TilingSprite`/`ParticleContainer` と
フィルターについては、以下を参照してください。 `references/assets-and-display.md`。

 ## 関連スキル

 - `phaser-core` — バッテリー付属の 2D フレームワーク (シーン、物理、入力)。
- `threejs-scene-setup` — three.js を使用したブラウザーでの 3D。
- `prototype-fast` — 再生可能なスライスを素早くグレーボックス化します (しばしば PixiJS を引用します)。 
