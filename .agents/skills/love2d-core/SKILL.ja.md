---
name: love2d-core
description: >
  Structure and debug a LÖVE (Love2D) game in Lua: the love.load/update/draw loop,
  delta-time movement, input, and screen states. Use when building a LÖVE 11.x game
  (main.lua, conf.lua, .love).
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # LÖVE (Love2D) コア

 Lua で LÖVE ゲームの基礎 (コールバック ループ、フレーム レート、
 の独立した動き、入力、画面状態) をセットアップしてデバッグします。 **LOVE 11.5** がターゲットです。

 ##

 を使用する場合 - LÖVE ゲームを開始するとき、`main.lua`/`conf.lua` を接続するとき、またはコア ループ、間違った速度で実行される
の動作、入力処理、または画面切り替えを修正するときに使用します。
- ワークスペースに、`love.*`、`conf.lua`、または `.love` ファイルを呼び出す `main.lua` がある場合に使用します。

 **使用しない*場合:** LÖVE に関係のない Lua *言語* の質問。物理ボディ/ジョイント
(LÖVE は `love.physics` 経由で Box2D を使用します。これは別の問題です)。シェーダー コード (`love.graphics`
GLSL は独自のトピックです)。クロスエンジンの保存/ロード パターンの場合は、`save-systems` を使用します。

 ## コア ワークフロー

 1. **エントリ ポイントを確認します。** LÖVE ゲームは `main.lua` を実行します。
`love.load()` (ワンタイムセットアップ)、`love.update(dt)` (状態)、および `love.draw()` (レンダリング) を定義する必要があります。
ウィンドウ/バージョンのセットアップは `conf.lua` で行われます (モジュールをロードする *前* に実行します)。
2. **バージョンを固定します。** `t.version = "11.5"` を `conf.lua` に設定して、LÖVE が不一致について警告するようにします。
3. **すべてのモーションを `dt`** (デルタ時間、秒単位) で駆動するため、速度はフレームレートに依存しません。
4. **入力を処理**する 2 つの方法: ポーリング (`update` の `love.keyboard.isDown`、押したキーの場合) と
イベント (`love.keypressed` コールバック、個別の押しの場合)。
5.
`if` フラグの山ではなく、小さな状態スタックを使用して **画面を管理** (メニュー、ゲーム、一時停止) します。パターンと `references/state-stack.md` を参照してください。
6. **実行して観察します。** プロジェクト フォルダーから `love .` を使用して起動します。動作すると仮定する前に、ウィンドウ、
 の動作速度、画面上の入力を確認してください。

 ## パターン

 ### 1. `main.lua` スケルトン (コールバック ループ + 入力)

```lua
-- main.lua — LÖVE calls these callbacks for you. Colors are 0–1 in LÖVE 11.x.
function love.load()
    -- One-time setup. speed is in PIXELS PER SECOND, not per frame.
    player = { x = 100, y = 100, size = 40, speed = 220 }
    love.graphics.setBackgroundColor(0.1, 0.1, 0.12)
end

function love.update(dt)
    -- Polled input: good for continuous movement while a key is held.
    if love.keyboard.isDown("right") then player.x = player.x + player.speed * dt end
    if love.keyboard.isDown("left")  then player.x = player.x - player.speed * dt end
    if love.keyboard.isDown("down")  then player.y = player.y + player.speed * dt end
    if love.keyboard.isDown("up")    then player.y = player.y - player.speed * dt end
end

function love.draw()
    love.graphics.setColor(0.2, 0.8, 1.0)                 -- tint ON
    love.graphics.rectangle("fill", player.x, player.y, player.size, player.size)
    love.graphics.setColor(1, 1, 1)                       -- reset tint before text/images
    love.graphics.print("Arrow keys to move, Esc to quit", 10, 10)
end

function love.keypressed(key)
    -- Event input: fires once per physical press. Use for menus, jumps, toggles.
    if key == "escape" then love.event.quit() end
end
```

### 2. フレームレートの独立性 (最も一般的なバグ)

```lua
-- RIGHT: scaled by dt → same real-world speed at 30 or 240 FPS.
player.x = player.x + player.speed * dt
-- WRONG: "pixels per frame" → moves twice as fast at double the frame rate.
player.x = player.x + player.speed
```

### 3. `conf.lua` (ウィンドウ + バージョン; `main.lua` より前に実行)

```lua
-- conf.lua — must be its own file; love.conf will NOT run from main.lua.
function love.conf(t)
    t.version = "11.5"             -- the LÖVE version this game targets (string "X.Y")
    t.window.title  = "My LÖVE Game"
    t.window.width  = 800
    t.window.height = 600
    t.window.vsync  = 1            -- number since 11.0: 1 = on, 0 = off, -1 = adaptive
    t.window.resizable = false
    t.modules.physics = false      -- disable modules you don't use to trim startup/memory
end
```

### 4. LÖVE 11.x では色は 0 ～ 1 (0 ～ 255 ではありません)

```lua
-- LÖVE 11.x uses normalized floats. (Pre-11.0 code used 0–255 and will look wrong.)
love.graphics.setColor(1, 0, 0)                          -- opaque red
love.graphics.setColor(0.2, 0.8, 1.0, 0.5)               -- translucent cyan (alpha 0.5)
-- Need to convert old byte values? Use the helper instead of dividing by hand:
love.graphics.setColor(love.math.colorFromBytes(128, 234, 255))
```

### 5. 画面の状態 (概要 - 参照の完全なマネージャー)

```lua
-- A screen is a table with optional :update(dt), :draw(), :keypressed(key).
-- Keep the active screen on a stack so pause/menu overlays are trivial to pop.
local Stack = require("state_stack")   -- see references/state-stack.md for the module
function love.load()              Stack.push(require("screens.menu")) end
function love.update(dt)          Stack.current():update(dt) end
function love.draw()              Stack.current():draw() end
function love.keypressed(key)     Stack.current():keypressed(key) end
```

## 落とし穴

 - **速度は FPS によって異なります** → `* dt` を忘れています。位置、タイマー、
、またはアニメーションに対するフレームごとの変更はすべて、`dt` によってスケーリングする必要があります。
- **`love.conf` が `main.lua`** に配置される → 黙って何も行われません。これは、モジュールをロードする *前* に実行される `conf.lua`、
 に存在する必要があります。
- **色が褪せているか、見えない** → 0 ～ 255 の値を使用しました。 11.x では、`setColor(255,0,0)`
は白に固定されます。 `setColor(1,0,0)` または `love.math.colorFromBytes` を使用します。
- **1 回の `setColor` 後に着色されたすべてのもの** → 色はグローバルであり、複数の描画にわたって持続します。
色付けを解除したいテキスト/画像を描画する前に、`love.graphics.setColor(1, 1, 1)` でリセットしてください。
- **キーを放したり繰り返しても何も起こりません** → `love.keypressed(key, scancode, isrepeat)`
は押すと (および OS のキーを繰り返すと) 起動します。リリースには `love.keyreleased` を使用し、押したキーの繰り返しを無視する必要がある場合は、
 `isrepeat` をチェックします。

 ## 参照

 - 完全なプッシュ/ポップ画面状態マネージャー (メニュー → ゲーム → 一時停止、委任された
コールバック) については、`references/state-stack.md` を参照してください。

 ## 関連スキル

 - `save-systems` — ゲーム状態の保存/読み込み (エンジンに依存しない)。
- `input-systems` — 再バインド可能なマルチデバイス入力アーキテクチャ。
- `pygame-core` / `phaser-core` — 他の軽量エンジンの同じループ概念。 
