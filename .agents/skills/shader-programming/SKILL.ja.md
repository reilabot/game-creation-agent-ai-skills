---
name: shader-programming
description: >
  Write game shaders from cross-engine fundamentals — the vertex→fragment
  pipeline, coordinate spaces, UV math, and common 2D/3D effects (tint, UV
  scroll, dissolve, outline, fresnel rim, vignette) in GLSL with HLSL
  equivalents. Use when the user mentions shaders, fragment/pixel shader, vertex
  shader, UV, GLSL, HLSL, or effects like dissolve, outline, or rim light.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # シェーダー プログラミング (クロスエンジン)

 シェーダーは、GPU 上で **頂点ごと**および**ピクセルごと**で実行される小さなプログラムです。
概念 (パイプライン、座標空間、UV、および
の共通エフェクトの構築方法) は、エンジン間で移植されます。言語の方言と組み込み変数
の名前のみが変更されます。このスキルは、HLSL
と同等の GLSL のポータブルな基礎を教えます。正確な
エンジン構文と組み込みについては、`godot-shaders` (または Unity/Unreal マテリアル ドキュメント) を使用してください。

 ##

 を使用する場合 - 頂点/フラグメント シェーダーを理解または作成し、UV、
 座標空間、および GPU パイプラインについて推論するために使用します。
- 一般的なエフェクトの構築に使用します: 色合い/再カラー、スクロール テクスチャ、ディゾルブ、
 アウトライン、フレネル/リム ライト、ビネット、カラー グレーディング。
- GLSL と HLSL 間、またはエンジン間でシェーダーの概念を変換するために使用します。

 **使用しない*場合:** エンジンの正確なシェーダー言語と組み込みについては、
 `godot-shaders` (Godot シェーディング言語) またはエンジンのマテリアル ドキュメントを使用します。完全な
パーティクル VFX システムについては、`unreal-niagara` を参照してください。後処理 *スタック* については、
 エンジンのレンダラ設定に従います。

 ## コア ワークフロー

 1. **現在どの段階にいるかを確認します。** **頂点** シェーダーは、各頂点
をクリップ スペースに変換し、データ (UV、法線) を渡します。 **フラグメント/ピクセル**
シェーダーはラスタライズされたピクセルごとに実行され、色を出力します。ほとんどのゲームエフェクトはフラグメントステージで
を実行します。
2. **座標空間を追跡します。** 位置は、モデル → ワールド → ビュー → クリップ空間に移動します。
法線はワールドまたはビュー空間に属します。スペースの混在は最も一般的なバグです。
3. **UV と時間でエフェクトを操作します。** UV は `0..1` テクスチャ座標です。
は、それらをオフセット、スケール、または歪め、`time` ユニフォームでアニメーション化します。
4. **ピクセルごとに動作し、ブランチライトします。** 可能であれば、`if` よりも `mix`、`step`、`smoothstep`、および
`clamp` を優先します。 GPU はピクセルをロックステップで実行し、
 分岐分岐を嫌います。
5. **ユニフォーム** (描画ごとに一定) および **可変** (補間された
頂点→フラグメント) を介してデータを渡します。テクスチャ サンプルは少なくしてください。それらはコストを支配します。
6. **視覚的にターゲット ハードウェア上で確認します。** デスクトップでは適切に見えるシェーダーが、モバイルでは壊れる可能性があります (精度、機能の不足)。発送先をテストします。

 ## パターン

 GLSL スタイルのフラグメント スニペット (Godot の `canvas_item`/`spatial`
シェーダーと OpenGL に近い)。 HLSL の同等物については `references/effects.md` を、完全なアウトライン/フレネル/ビネット シェーダについては
を参照してください。

 ### 1. フラグメントの基本: サンプル、ティント、結合

```glsl
// Per-pixel: read the texture at this UV, multiply by a color (tint), keep alpha.
uniform sampler2D tex;
uniform vec4 tint;          // e.g. (1,0,0,1) reddens; multiply is non-destructive
in vec2 uv;                 // interpolated 0..1 texture coordinate (a "varying")
out vec4 frag;
void main() {
    vec4 c = texture(tex, uv);   // HLSL: tex.Sample(samp, uv)
    frag = c * tint;             // component-wise multiply tints without clipping
}
```

### 2. スクロール UV (アニメーション テクスチャ) — フレームレートに依存しない

```glsl
// Add time * speed to the UV to scroll. fract() wraps it into 0..1 so it tiles.
uniform sampler2D tex;
uniform float time;          // seconds, supplied by the engine
uniform vec2 scroll_speed;   // UV units per second, e.g. (0.1, 0.0)
in vec2 uv;
out vec4 frag;
void main() {
    vec2 scrolled = fract(uv + scroll_speed * time);  // HLSL: frac(...)
    frag = texture(tex, scrolled);
}
// Drive with a real time uniform, not a per-frame accumulator, so speed is stable.
```

### 3. ディゾルブ (ノイズ マップのしきい値を適用し、エッジをグローします)

```glsl
// Hide pixels where noise < threshold; tint a thin band at the boundary.
uniform sampler2D tex;
uniform sampler2D noise_tex;     // grayscale noise, 0..1
uniform float amount;            // 0 = fully visible, 1 = fully dissolved
uniform float edge = 0.05;       // width of the glowing edge band
uniform vec4 edge_color;
in vec2 uv;
out vec4 frag;
void main() {
    vec4 c = texture(tex, uv);
    float n = texture(noise_tex, uv).r;
    if (n < amount) discard;                 // cut away dissolved pixels
    float e = smoothstep(amount, amount + edge, n);  // 0 at the edge -> 1 inside
    frag = mix(edge_color, c, e);            // HLSL: lerp(edge_color, c, e)
}
```

### 4. フレネル リム ライト (3D) — 視角を明るくする

```glsl
// Rim = 1 where the surface faces away from the camera (silhouette glow).
in vec3 world_normal;        // normalized, world space (from the vertex stage)
in vec3 view_dir;            // normalized, surface -> camera, world space
uniform float power = 3.0;
uniform vec3 rim_color;
out vec4 frag;
void main() {
    float f = pow(1.0 - clamp(dot(world_normal, view_dir), 0.0, 1.0), power);
    frag = vec4(rim_color * f, 1.0);   // add to lighting; f peaks at the silhouette
}
// Correctness: normal and view_dir MUST be in the same space and normalized.
```

## 落とし穴

 - **座標空間を混合する** (
 ビュー空間のライトに対してワールド空間の法線を照らす) と、微妙に間違ったシェーディングが発生します。スペースを 1 つ選択し、
 のすべてをそこに変換します。
- **正規化を忘れている** 補間された法線/方向: 補間
はベクトルを短縮するため、`dot()` の結果がドリフトします。フラグメントステージの`normalize()`。
- **エンジン全体にわたる UV の仮定。** 一部のエンジンは V を反転します (
 原点の左上と左下)。テクスチャが上下逆さまに表示される場合があります。エンジンの規約を理解してください。
- **重い分岐/動的ループ**により GPU が停止します。 `step`/`smoothstep`/
`mix` を優先します。 `if`/`discard` を予約すると、本当に安価な早期出荷が可能になります。
- **`discard` は初期の Z** を破っており、タイル化されたモバイル GPU のパフォーマンスに悪影響を与える可能性があります。
は、可能な限りアルファ ブレンディングを好みます。
- **モバイルでの精度**: `highp` と `mediump` は重要です。低精度シマーの大きな UV または時間値 
。座標と時刻には適切な精度を使用してください。
- **GLSL == HLSL と仮定します。** `mix`↔`lerp`、`fract`↔`frac`、`texture()`↔`.Sample()`、
 `vec2`↔`float2`、列優先の行列と行優先の行列。参照マッピングを参照してください。

 ## リファレンス

 - `references/effects.md` — フル アウトライン (2D スプライト + 3D)、ビネット、およびカラー
グレーディング シェーダー。 GLSL↔HLSL 関数/型マッピング テーブル。エンジンごとのノート
(Godot `canvas_item`/`spatial`、Unity ShaderLab/HLSL、Unreal マテリアル ノード)。

 ## 関連スキル

 - `godot-shaders` — Godot シェーディング言語の構文、組み込み、およびスクリーン リーディング。
- `unreal-niagara` — GPU パーティクル VFX (別のシェーダー使用)。
- `procedural-gen` — ディゾルブとプロシージャル テクスチャリングを駆動するノイズ。 
