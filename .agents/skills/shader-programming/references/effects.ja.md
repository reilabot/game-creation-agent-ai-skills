# シェーダー エフェクトと GLSL↔HLSL マッピング

 `SKILL.md` でスケッチされたエフェクトのフル バージョンに加え、エンジン間でシェーダーを移植するために
が必要とする方言マッピング。例は GLSL スタイルです。マッピング テーブル
は HLSL 形式を示します。

 ## GLSL ↔ HLSL クイック リファレンス

 | GLSL | HLSL |注 |
|---|---|---|
| `vec2/3/4`、`mat3/4` | `float2/3/4`、`float3x3/4x4` |ベクトルと行列 |
| `mix(a, b, t)` | `lerp(a, b, t)` |線形補間 |
| `fract(x)` | `frac(x)` |小数部 |
| `mod(a, b)` | `fmod(a, b)` |マイナスの場合は符号が異なります — 検証 |
| `texture(samp, uv)` | `tex.Sample(samp, uv)` |サンプラーは HLSL の別のオブジェクトです |
| `inversesqrt(x)` | `rsqrt(x)` | |
| `mat * vec` (列優先) | `mul(vec, mat)` (行優先) |行列の順序/規則が異なります |
| `gl_Position` / `out` カラー | `SV_Position` / `SV_Target` |セマンティクスによるステージ出力 |
| `dFdx/dFdy` | `ddx/ddy` |スクリーンスペースの導関数 |

 こちらにも注目してください: クリップ スペースの深度範囲 (OpenGL `-1..1` 対 D3D `0..1`) と UV/クリップ Y
方向は API 間で異なります。通常、エンジンはこれを正規化しますが、生のシェーダーを移植するときに
表面化します。

 ## 2D スプライト アウトライン (アルファ近傍をサンプル)

```glsl
// Draw an outline where a transparent pixel is adjacent to an opaque one.
uniform sampler2D tex;
uniform vec2 texel_size;     // (1/width, 1/height) of the texture
uniform vec4 outline_color;
in vec2 uv;
out vec4 frag;
void main() {
    vec4 c = texture(tex, uv);
    if (c.a > 0.5) { frag = c; return; }          // inside the sprite: unchanged
    // sample 4 neighbors; if any is opaque, this empty pixel is on the border
    float a = max(max(texture(tex, uv + vec2( texel_size.x, 0)).a,
                      texture(tex, uv + vec2(-texel_size.x, 0)).a),
                  max(texture(tex, uv + vec2(0,  texel_size.y)).a,
                      texture(tex, uv + vec2(0, -texel_size.y)).a));
    frag = (a > 0.5) ? outline_color : vec4(0.0);  // border pixel -> outline
}
```

輪郭をより厚くまたは滑らかにするには、8 つの近傍 (対角線を含む) をサンプリングするか、
 の小さな距離フィールド パスを実行します。 3D では、アウトラインは通常、異なる方法で行われます。法線に沿って外側にスケーリングされた
背面をレンダリングするか、ポストプロセスで深さ/法線の
の不連続性からエッジを検出します。

 ## ビネット (画面の端を暗くする) — 後処理

```glsl
// Darken pixels by distance from screen center. screen_uv is 0..1 across the view.
uniform sampler2D screen_tex;
uniform float strength = 0.6;   // 0 = none, 1 = strong
uniform float radius = 0.75;    // where darkening begins
in vec2 screen_uv;
out vec4 frag;
void main() {
    vec3 c = texture(screen_tex, screen_uv).rgb;
    float d = distance(screen_uv, vec2(0.5));      // 0 center .. ~0.707 corner
    float v = smoothstep(radius, radius * 0.5, d); // 1 in center, ->0 at edges
    frag = vec4(c * mix(1.0 - strength, 1.0, v), 1.0);
}
```

## カーブによるカラー グレーディング (明るさ/コントラスト/彩度)

```glsl
// Order matters: contrast around 0.5, then saturation, then brightness.
uniform sampler2D screen_tex;
uniform float brightness = 0.0;   // additive
uniform float contrast   = 1.0;   // multiplicative around mid-gray
uniform float saturation = 1.0;
in vec2 screen_uv;
out vec4 frag;
void main() {
    vec3 c = texture(screen_tex, screen_uv).rgb;
    c = (c - 0.5) * contrast + 0.5;                       // contrast
    float luma = dot(c, vec3(0.2126, 0.7152, 0.0722));    // Rec.709 luminance
    c = mix(vec3(luma), c, saturation);                   // saturation
    c += brightness;                                      // brightness
    frag = vec4(clamp(c, 0.0, 1.0), 1.0);
}
```

輝度重み `(0.2126, 0.7152, 0.0722)` は Rec.709 係数です。
 緑が知覚される明るさを支配します。 LUT ベースのグレーディングの場合は、代わりにピクセルの RGB によってインデックス付けされたカラー
ルックアップ テクスチャをサンプリングします。

 ## エンジンごとのメモ

 - **Godot (4.x) — `gdshader`.** Godot のシェーディング言語は、
 `shader_type` (2D の場合は `canvas_item`、2D の場合は `spatial`) を備えた GLSL に似ています。 3D）。組み込みが提供されます: 
、`UV`、`COLOR`、`TIME`、`TEXTURE`、`SCREEN_TEXTURE`、`NORMAL`、`VIEW`。
`fragment()` / `vertex()` 関数を記述します。ここにある GLSL の例を
組み込みにマップします。 `godot-shaders`を参照してください。
- **Unity — ShaderLab + HLSL.** シェーダーは、`.shader` ファイル (ShaderLab
ブロック) またはシェーダー グラフに存在します。コードは HLSL: `float4`、`lerp`、`tex2D`/`.Sample`、
 `SV_Target`。 URP/HDRP の供給には、ライティングと変換用のファイルが含まれています。
- **Unreal — マテリアル エディター (ノード グラフ) + HLSL。** ほとんどのオーサリングは視覚的な
ノードです。カスタム ノードには HLSL が埋め込まれます。コンセプト (UV、フレネル ノードを介したフレネル、UV スクロール用の
パナー) は、ここのパターンに直接マッピングされます。

 ## パフォーマンス チェックリスト

 - テクスチャ サンプルを最小限に抑えます。それらが主なコストです。
を再読み込みする代わりにサンプルを再利用します。
- ブランチおよび `discard` よりも数学 (`smoothstep`、`mix`) を優先します。
- ピクセル単位の精度
が必要ない場合、頂点ごとに重い値を計算します (その後補間します)。
- モバイルでは適切な精度を使用します (カラーの場合は `mediump`、UV/時間の場合はより高くなります)。
- 可能であれば、ローエンド GPU での依存テクスチャ読み取り (別のテクスチャから読み取られた値を使用したサンプリング)
を避けます。 
