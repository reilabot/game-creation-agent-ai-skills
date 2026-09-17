---
name: threejs-scene-setup
description: >
  Stand up a three.js scene: import maps and the three/addons path, the
  Scene/PerspectiveCamera/WebGLRenderer trio, the setAnimationLoop render loop,
  responsive resize, and OrbitControls. Use when starting or debugging a three.js
  app — when the user mentions three.js, THREE.Scene, WebGLRenderer,
  PerspectiveCamera, the render loop, resizing, or OrbitControls. For models use
  threejs-gltf-loading; for materials/lights use threejs-materials-lighting.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # three.js シーンのセットアップ

 three.js アプリの基礎を作成します: モジュールの読み込み、
 シーン/カメラ/レンダラー トリオ、レンダー ループ、レスポンシブ サイズ変更、およびカメラ
コントロール。パターンは **r184** をターゲットとしています。サンプルとアドオンはリリース間で移動するため、既存のプロジェクトを
変更する前に、インストールされている `three` バージョンを読んでください。

 ##

 を使用する場合 - three.js シーンのブートストラップ、空白/黒のキャンバスの修正、
 キャンバスの応答性の向上、アニメーション ループの設定、または `OrbitControls` の追加の場合に使用します。
- `package.json` が `three` に依存し、コードが `import * as THREE from
'three'` を行う場合に使用します。

 **使用しない*場合:** `.gltf`/`.glb` モデルまたはスキン アニメーションをロード中 →
`threejs-gltf-loading`。マテリアル、ライト、シャドウ、環境マップ →
`threejs-materials-lighting`。 2Dレンダリング→`pixijs-rendering`。

 ## コア ワークフロー

 1. **インポート マップを使用して、three.js を ES モジュールとしてロードします。** r147 以降、ベア
指定子 `'three'` および `'three/addons/'` を (HTML または
バンドラーによって) マップする必要があります。アドオン (コントロール、ローダー) は `three/addons/...` の下にあります。
2. **トリオを作成します。** `Scene` (グラフのルート)、`PerspectiveCamera(fov,
アスペクト、ニア、ファー)` moved back from the origin, and a `WebGLRenderer`、その
`domElement` は DOM 内にあります。サイズと`pixelRatio`を設定します。
3. **メッシュを追加します。** `new Mesh(geometry, material)` および `scene.add(mesh)`。
で照らされたマテリアルでは、ライトも必要です (`threejs-materials-lighting` を参照)。
4. **`renderer.setAnimationLoop(fn)` でレンダリング ループを駆動します。** これは、最新の
WebXR/WebGPU に安全な、手動の `requestAnimationFrame` の代替品です。デルタ時間には
`Clock` を使用します。
5. **ハンドルのサイズ変更**により、カメラのアスペクトとレンダラーがキャンバスに一致します。
`camera.aspect` を更新し、`updateProjectionMatrix()` および `renderer.setSize(...)` を呼び出します。
6. **開発中のオービット/パン/ズーム用に `OrbitControls`** を追加します。成功したと仮定する前に、
 が実際にレンダリングするもの (点灯した立方体、コントロールの応答) を確認してください。

 ## パターン

 ### 1. HTML インポート マップ + モジュール エントリ (バンドラーなし)

```html
<canvas id="c"></canvas>
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.184.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.184.0/examples/jsm/"
  }
}
</script>
<script type="module" src="./main.js"></script>
```

バンドラー (Vite/webpack) を使用すると、インポート マップをスキップして、
 `npm i three` だけを実行します。同じ `import` ステートメントが解決されます。

 ### 2. シーン + カメラ + レンダラー

```js
// main.js
import * as THREE from 'three';

const canvas = document.querySelector('#c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // cap for perf
renderer.setSize(window.innerWidth, window.innerHeight);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x101018);

const camera = new THREE.PerspectiveCamera(
  60,                                   // vertical field of view (degrees)
  window.innerWidth / window.innerHeight, // aspect
  0.1,                                  // near
  100                                   // far
);
camera.position.set(3, 2, 5);
camera.lookAt(0, 0, 0);

const cube = new THREE.Mesh(
  new THREE.BoxGeometry(1, 1, 1),
  new THREE.MeshNormalMaterial()        // unlit; shows orientation without a light
);
scene.add(cube);
```

### 3. レンダリング ループ (setAnimationLoop + Clock)

```js
const clock = new THREE.Clock();

renderer.setAnimationLoop(() => {
  const dt = clock.getDelta();          // seconds since last frame
  cube.rotation.x += dt;                // frame-rate independent
  cube.rotation.y += dt * 0.7;
  renderer.render(scene, camera);
});
// renderer.setAnimationLoop(null); // stop the loop
```

### 4. レスポンシブ サイズ変更

```js
function onResize() {
  const w = window.innerWidth, h = window.innerHeight;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();      // required after changing aspect
  renderer.setSize(w, h);
}
window.addEventListener('resize', onResize);
```

### 5. OrbitControls (オービット/パン/ズーム)

```js
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;          // inertial feel
controls.target.set(0, 0, 0);

renderer.setAnimationLoop(() => {
  controls.update();                    // needed every frame when damping is on
  renderer.render(scene, camera);
});
```

## 落とし穴

 - **`Failed to resolve module specifier "three"`** → インポート マップ (またはバンドラー
構成) がありません。 `"three"` と `"three/addons/"` の両方をマップします。アドオンのパスは `/` で終わる必要があります。
- **黒いキャンバス、エラーなし** → カメラが原点 (オブジェクトの内側/後ろ) にあり、
、または光のない明るいマテリアル (`MeshStandardMaterial`) を使用しました。カメラを
後方に移動します。最初に `MeshNormalMaterial`/`MeshBasicMaterial` を使用してジオメトリを確認します。
- **何もアニメーション化しない** → ループ内で `renderer.render` を呼び出していないか、または
は `setAnimationLoop` を呼び出しているがループの外でレンダリングしています。
- **サイズ変更時にビューが伸縮/縮小** → レンダラーのサイズを変更しましたが、
 で `camera.aspect` + `updateProjectionMatrix()` が更新されませんでした。
- **HiDPI でぼやけるまたはギザギザ** → `renderer.setPixelRatio(...)` を設定します。
4K/Retina スクリーンのパフォーマンスが低下しないように、キャップ (≈2) を設定してください。
- **OrbitControls が死んでいるような気がする** → `enableDamping = true` では、フレームごとに
`controls.update()` を呼び出す必要があります。
- **古いチュートリアルでは `<script src="three.min.js">` を使用します** → r147 以降、three.js には
ES モジュールのみが同梱されています。 `type="module"` + マップをインポートしてください。

 ## 参照

 - 座標規則、シーン グラフ (`Group`、親子変換、
 `Object3D` 追加/削除)、2.5D の `OrthographicCamera`、および
の破棄については、リークを避けるためのジオメトリ/マテリアル/テクスチャについては、`references/scene-graph.md` を参照してください。

 ## 関連スキル

 - `threejs-materials-lighting` — サーフェスに明るい外観を与えます (ライト、シャドウ、PBR)。
- `threejs-gltf-loading` — 3D モデルをロードし、アニメーションを再生します。
- `pixijs-rendering` — ブラウザーでの 2D レンダリング。
- `fps-shooter` — three.js スキルを構成する 3D ジャンル テンプレート。 
