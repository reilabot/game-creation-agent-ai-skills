---
name: phaser-core
description: >
  Set up and debug a Phaser 4 game: the Game config, the Scene lifecycle
  (init/preload/create/update), the asset loader, cameras, and cross-scene
  communication. Use when building or debugging a Phaser game — when the user
  mentions Phaser, Phaser.Game, Phaser.Scene, preload/create/update, this.load,
  this.add, or scene transitions. For Arcade Physics movement/collisions use
  phaser-arcade-physics.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # Phaser 4 コア

 Phaser ゲームの基礎を設定します: `Game` 設定、`Scene`
ライフサイクル、アセットの読み込み、カメラ、シーン間のデータの受け渡し。新しいプロジェクトでは
**Phaser 4.2** をターゲットとします。ユーザーが明示的に移行を要求しない限り、既存の Phaser 3.90 プロジェクトを
固定メジャーに保持します。

 ##

 を使用する場合 - Phaser ゲームの開始時、`Phaser.Game` 設定の配線時、
 `Scene` の構築時、`preload` でのアセットのロード時、またはシーン トランジションと共有
状態の修正時に使用します。
- プロジェクトに `package.json` または `import Phaser from 'phaser'`、`import Phaser from 'phaser'` の `phaser` があり、コードで `preload()`/`create()`/`update()` を使用する場合に使用します。

 **使用しない*場合:** 移動、速度、コライダー、重力、またはオーバーラップ →
`phaser-arcade-physics` を使用します。複雑な剛体シミュレーションでは、物質物理学が使用されます (
 の別の関心事)。クロスエンジンの保存/ロード パターンには、`save-systems` を使用します。

 ## コア ワークフロー

 1. **最初にインストールされているメジャーを検出します。** `package.json` とロックファイルを読み取ります。新しい作業には
Phaser 4.2 を使用してください。 Phaser 3 プロジェクトを Phaser 4 としてサイレントに書き換えないでください。
2. **構成からゲームを作成します** `type:
Phaser.AUTO` (WebGL with Canvas fallback), a `width`/`height`, and a `scene`
配列を使用して `new Phaser.Game(config)` を作成します。最初のシーン (および `active: true` を含むシーン) が自動的に開始されます。
3. **各画面を `Scene` としてモデル化します。** `Phaser.Scene` をサブクラス化し、一意の
`key` を `super` に渡し、ライフサイクルを実装します: `init(data)` → `preload()` →
`create(data)`→`update(time, delta)`。
4. **`preload` にアセットをロードし、`create` で使用します。** キューに登録されたアセットは、`create` まで
利用できません。ローダーはシーンごとにあります。埋められるキャッシュはグローバルです。
5. **コンストラクターではなく、`init()` で実行ごとの状態をリセットします。** シーン インスタンスは再起動後も
で再利用されるため、コンストラクター セットのフィールドは古い値を保持します。
6. `this.scene.start/launch/switch/sleep/wake` を使用して **画面間を移動**します。
`this.registry` (グローバル) または兄弟シーンのイベント エミッターを介してデータを共有します。
7. **実行して観察します。** ページを提供して開き、アセットが読み込まれることを確認し (
 の [ネットワーク] タブとコンソールを確認します)、シーンが期待どおりに切り替わることを確認してから、成功したと判断します。

 ## パターン

 ### 1. ゲーム設定 + ブート (ES モジュール)

```js
// main.js — one Game owns the renderer, loop, cache, and Scene Manager.
import Phaser from 'phaser';
import BootScene from './scenes/BootScene.js';
import PlayScene from './scenes/PlayScene.js';

const config = {
  type: Phaser.AUTO,            // WebGL if available, else Canvas
  width: 800,
  height: 600,
  backgroundColor: '#1d1d28',
  scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
  scene: [BootScene, PlayScene] // BootScene starts first
};

new Phaser.Game(config);
```

### 2. ライフサイクル全体のシーン

```js
// scenes/PlayScene.js
import Phaser from 'phaser';

export default class PlayScene extends Phaser.Scene {
  constructor() {
    super('play');                  // unique scene key
  }

  init(data) {
    // Reset run-specific state HERE so restarts start clean.
    this.score = 0;
    this.level = data.level ?? 1;
  }

  preload() {
    // Queue downloads. Not usable until create().
    this.load.image('player', 'assets/player.png');
    this.load.spritesheet('coin', 'assets/coin.png', { frameWidth: 16, frameHeight: 16 });
  }

  create() {
    this.player = this.add.sprite(400, 300, 'player');
    this.scoreText = this.add.text(10, 10, 'Score: 0', { fontSize: '20px', color: '#fff' });
    this.cursors = this.input.keyboard.createCursorKeys();
  }

  update(time, delta) {
    // delta is milliseconds since last frame; divide by 1000 for seconds.
    const speed = 200 * (delta / 1000);
    if (this.cursors.left.isDown)  this.player.x -= speed;
    if (this.cursors.right.isDown) this.player.x += speed;
  }
}
```

### 3. クロスシーンデータ + イベント

```js
// The registry is a global DataManager shared by every scene.
this.registry.set('coins', 0);                 // in any scene
const coins = this.registry.get('coins');      // read anywhere

// React to registry changes (e.g. a HUD scene listening to gameplay):
this.registry.events.on('changedata-coins', (parent, value) => {
  this.coinText.setText(`Coins: ${value}`);
});

// Talk directly to another running scene via its event emitter:
const ui = this.scene.get('hud');
ui.events.emit('show-message', 'Level cleared!');
```

### 4. シーンの遷移 (適切な動詞を選択)

```js
this.scene.start('gameover', { score: this.score }); // stop this scene, start target
this.scene.launch('hud');        // run a second scene in parallel (overlay HUD)
this.scene.switch('menu');       // sleep this scene, start/wake target
this.scene.pause();              // freeze updates but keep rendering (modal)
this.scene.sleep();              // stop updating AND rendering, keep state for wake
```

### 5. プレーヤーを追跡するカメラ

```js
this.cameras.main.setBounds(0, 0, 1600, 1200);  // world size
this.cameras.main.startFollow(this.player, true, 0.1, 0.1); // smooth lerp follow
this.cameras.main.setZoom(1.5);
```

## 落とし穴

 - **アセットは `create`/`update` の `undefined`** → アセットを
`preload` にキューに入れるのを忘れたか、間違ったキーを使用しました。ローダーは `preload` と `create` の間で実行されます。
- **再起動時の状態リーク** → コンストラクターでフィールドを設定します。シーン
インスタンスが再利用されます。 `init()` で実行状態をリセットし、`shutdown` で配列をクリアします。
- **`this.scene.start` 対 `this.scene.launch`** → `start` は呼び出しシーンを停止します。
`launch` はターゲットを並行して実行します。 HUD に `start` を使用すると、ゲームが非表示になります。
- **コールバック内の `this` は間違っています** → アロー関数はシーンの `this` を維持します。プレーン
`function` コールバックにはコンテキスト引数または `.bind(this)` が必要です。
- **フェイザー 2 チュートリアルが機能しない** → フェイザー 3、
 では「ステート」の名前が「シーン」に変更され、各シーンはグローバル
ゲーム ワールドではなく、独自のシステム (入力、カメラ、トゥイーン) を所有します。
- **フェイザー 3 のカスタム パイプラインがフェイザー 4 で失敗する** → フェイザー 4 はレンダラーを再構築し、
 が古い FX/パイプライン拡張ポイントを置き換えました。 Phaser 4 ガイドに対してカスタム シェーダーとレンダラー
プラグインを移行します。内部レンダラー コードを機械的にコピーしないでください。
- **何もレンダリングされない/黒い画面** → キャンバスがマウントされていること、`width`/`height`
が設定されていること、およびシーンが実際に開始されていることを確認します (`game.scene.dump()` の出力を確認してください)。

 ## リファレンス

 - 完全なシーン ステート マシン (一時停止/再開とスリープ/ウェイクと停止/開始、
 の再起動状態のバグ、およびシーンの削除/置換) については、
 `references/scene-flow.md` を参照してください。

 ## 関連スキル

 - `phaser-arcade-physics` — 速度、重力、コライダー、オーバーラップ、およびグループ。
- `input-systems` — 再バインド可能なマルチデバイス入力アーキテクチャ (エンジンに依存しない)。
- `pixijs-rendering` / `threejs-scene-setup` — 他のブラウザー レンダリング スタック。
- `platformer` / `puzzle` — フェイザースキルを構成するジャンルテンプレート。 
