# PixiJS v8 アセットと表示オブジェクト

 v8 アセット パイプラインと `Sprite` を超える表示オブジェクト タイプの詳細。
`SKILL.md` はブート パスとシーン グラフをカバーします。このファイルにはテクスチャが入力され、
 にはその他の描画内容が書き込まれます。

 ## `Assets` システム (v8)

 `Assets` は、v7 `Loader` を置き換えます。 URL/エイリアスによってキャッシュされるため、同じソースに対して
`Assets.load` を 2 回呼び出すと、2 回目はすぐに解決されます。

```js
import { Assets } from 'pixi.js';

// Single asset.
const tex = await Assets.load('assets/hero.png');

// Register aliases up front, load later by name.
Assets.add({ alias: 'hero', src: 'assets/hero.png' });
const hero = await Assets.load('hero');

// Load several at once (object form keeps results keyed).
const sheet = await Assets.load([ 'a.png', 'b.png' ]);

// Background-load without blocking, then `load` resolves instantly when needed.
Assets.backgroundLoad(['level-2-bg.png']);

// Free GPU + CPU memory when a screen is done.
await Assets.unload('hero');
```

サポートされるソース タイプには、画像、スプライト シート JSON (アトラス)、ビットマップ フォント、
 Web フォント、およびオーディオ (適切なローダーがインストールされている場合) が含まれます。アトラスは
`Spritesheet` としてロードされます。名前によるフレームへのアクセス:

```js
const sheet = await Assets.load('assets/characters.json'); // TexturePacker JSON
const idle = new Sprite(sheet.textures['hero_idle.png']);
const runFrames = sheet.animations['hero_run'];            // Texture[] for animation
```

## テクスチャ設定

```js
import { Texture } from 'pixi.js';

texture.source.scaleMode = 'nearest';  // crisp pixel art ('linear' is the default)
const sub = new Texture({ source: texture.source, frame: new Rectangle(0, 0, 16, 16) });
```

`Texture` は、`TextureSource` (GPU リソース) へのビューです。多くの `Texture` は
で 1 つのソースを共有できます。これがアトラスが余分なアップロードを回避する方法です。

 ## 表示オブジェクト タイプ

 ### AnimatedSprite

```js
import { AnimatedSprite } from 'pixi.js';
const anim = new AnimatedSprite(sheet.animations['hero_run']);
anim.animationSpeed = 0.2;   // fraction of a frame per ticker tick
anim.play();
app.stage.addChild(anim);
```

### グラフィックス (ベクトル描画)

 v8 は、滑らかで保持された API を使用します。形状を定義してから、塗りつぶし/ストロークを呼び出します。

```js
import { Graphics } from 'pixi.js';
const g = new Graphics()
  .roundRect(0, 0, 120, 60, 12)
  .fill(0x4488ff)
  .stroke({ width: 2, color: 0xffffff });
app.stage.addChild(g);
```

(v7 の順序は `beginFill` → 描画 → `endFill` でした。v8 では最初にシェイプを描画し、次に
が塗りつぶし/ストロークします。)

 ### テキストとビットマップテキスト

```js
import { Text, TextStyle } from 'pixi.js';
const score = new Text({
  text: 'Score: 0',
  style: new TextStyle({ fontFamily: 'Arial', fontSize: 24, fill: '#ffffff' }),
});
```

頻繁に変更される文字列 (HUD カウンター) には `BitmapText` を使用します。変更のたびに新しいテクスチャをラスタライズするのではなく、グリフ
テクスチャを再利用します。

 ### TilingSprite (スクロール背景)

```js
import { TilingSprite } from 'pixi.js';
const bg = new TilingSprite({ texture: skyTexture, width: app.screen.width, height: app.screen.height });
app.ticker.add((t) => { bg.tilePosition.x -= 0.5 * t.deltaTime; });
```

### ParticleContainer (多数の単純なスプライト)

 何千もの安価な同じテクスチャのスプライト (弾丸、パーティクル) の場合、
 `ParticleContainer` は、子ごとの機能と引き換えにスループットを確保します。動的
プロパティ (位置/回転など) を明示的に保ち、サポートされていない機能は避けてください。

 ## フィルター

 フィルターは、表示オブジェクトとその子に適用される GPU ポストプロセス効果です:

```js
import { BlurFilter } from 'pixi.js';
container.filters = [new BlurFilter({ strength: 4 })];
```

フィルターはサブツリーを一時テクスチャにレンダリングするため、メモリを消費し、
 レートをフィルします。控えめに適用し、不要な場合は削除 (`obj.filters = null`) します。

 ## クリーンアップ

 - `removeChild(child)` は切断されますが、GPU メモリは**解放されません**。
- `child.destroy()` は表示オブジェクトを解放します。
テクスチャも破棄するオプションを渡します: `sprite.destroy({ texture: true, textureSource: true })`。
- `Assets.unload(urlOrAlias)` は、ロードされたアセットの GPU/CPU メモリを解放します。
- WebGL/WebGPU コンテキスト損失時に、テクスチャはソースから復元されます。実行時に生成されるものについては、
 ソースを保持します (またはリロードできるようにします)。 
