# three.js シーン グラフ、カメラ、クリーンアップ (r150+)

 シーン セットアップ スキルの背後にある詳細: 座標規則、`Object3D`
階層、正投影カメラ、およびリソースの破棄。

 ## 座標と規則

 - 右手座標系: **+X 右、+Y 上、+Z ビューアに向かって**。新しい
`PerspectiveCamera` は **-Z** を見下ろします。
- 回転は **ラジアン** 単位で行われます (度である `PerspectiveCamera` の `fov` を除く)。
度で考える場合は、`THREE.MathUtils.degToRad(deg)` を使用します。
- 単位は任意ですが、一貫性があります。 glTF モデルはメートル単位で作成されます。
スケールを選択し、プロジェクト全体でそれを維持します。

 ## Object3D 階層

 すべての視覚的なもの (`Mesh`、`Group`、`Camera`、`Light`) は `Object3D` を拡張し、
 `position` を持ちます。 `rotation`、`quaternion`、`scale`。子は親の
変換を継承します。

```js
import * as THREE from 'three';

const turret = new THREE.Group();         // empty transform node
turret.add(barrelMesh);                   // child, positioned relative to turret
scene.add(turret);
turret.rotation.y = Math.PI / 4;          // rotates the whole group

barrelMesh.removeFromParent();            // detach (r129+)
scene.add(barrelMesh);                    // re-parent to the scene root
```

便利なトラバーサル/ルックアップ ヘルパー:

```js
scene.getObjectByName('Player');          // first descendant with that .name
root.traverse((obj) => { /* visit every descendant */ });
obj.getWorldPosition(new THREE.Vector3()); // world-space position
```

物理/ゲームプレイ オブジェクトの親のスケーリングを避けます。非ユニット親スケールは子を介して
を複合し、ワールド空間の計算 (レイキャスト、距離) でエラーが発生しやすくなります。

 ## PerspectiveCamera と OrthographicCamera

 - **PerspectiveCamera(fov、aspect、near、far)** — オブジェクトは距離とともに縮小します。
3D のデフォルト。シーンに応じて、`near`/`far` をできるだけしっかりと固定してください。遠方/近方の巨大な
比は、深度精度 (Z ファイティング) を破壊します。
- **OrthographicCamera(left、right、top、bottom、near、far)** — 遠近感なし。
は、2.5D、アイソメ、または CAD のようなビューに最適です。アスペクトに合わせて錐台のサイズを変更します:

```js
const aspect = window.innerWidth / window.innerHeight;
const d = 5;
const cam = new THREE.OrthographicCamera(-d * aspect, d * aspect, d, -d, 0.1, 100);
// On resize, recompute left/right from the new aspect, then updateProjectionMatrix().
```

投影プロパティ (`aspect`、`fov`、錐台範囲、`zoom`) を変更した後、
 は `camera.updateProjectionMatrix()` を呼び出します。

 ## リソースの破棄 (リークの回避)

 three.js は、GPU メモリのガベージ コレクションを行うことはできません。
シーンからオブジェクトを削除すると、GPU は何も解放されません。ジオメトリ、マテリアル、および
テクスチャを明示的に破棄する必要があります。

```js
function disposeObject(obj) {
  obj.traverse((node) => {
    if (node.geometry) node.geometry.dispose();
    const materials = Array.isArray(node.material) ? node.material : [node.material];
    for (const mat of materials) {
      if (!mat) continue;
      for (const key of Object.keys(mat)) {
        const value = mat[key];
        if (value && value.isTexture) value.dispose(); // map, normalMap, etc.
      }
      mat.dispose();
    }
  });
  obj.removeFromParent();
}
```

また、レンダー ターゲット (`renderTarget.dispose()`) を破棄し、完全なティアダウンでは、
 レンダラー (`renderer.dispose()`) も破棄します。レベルを交換するときは、次のレベルをロードする前に古いレベルの
サブツリーを破棄します。そうしないと、遷移ごとにメモリが増加します。

 ## ループの停止と再開

 `renderer.setAnimationLoop(fn)` はループを開始します。 `setAnimationLoop(null)` は
を停止します (たとえば、Page Visibility API によってタブが非表示になっている場合、またはメニューが開いている場合)。この
は WebXR で必要なループでもあり、`requestAnimationFrame` は XR
フレームを駆動しません。

 ## レンダー オン デマンド

 静的なシーンまたはエディターの場合、連続ループは必要ありません。
何かが変更されたときのみレンダリングします (入力、コントロールの `change` イベント、トゥイーン ステップ):

```js
let needsRender = true;
controls.addEventListener('change', () => { needsRender = true; });
renderer.setAnimationLoop(() => {
  if (!needsRender) return;
  needsRender = false;
  renderer.render(scene, camera);
});
```

これにより、アニメーション以外のコンテンツの GPU/バッテリーの使用量が大幅に削減されます。 
