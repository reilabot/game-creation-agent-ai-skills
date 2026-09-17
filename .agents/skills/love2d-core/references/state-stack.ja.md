# 画面状態スタック (LÖVE 11.5)

 小さくて完全な画面マネージャー: メニュー → ゲーム → 一時停止。アクティブな画面がスタック上にあるため、
 オーバーレイ (ゲームの上で一時停止) は簡単です。各 *画面* は、
、オプションのメソッド `enter`、`leave`、`update(dt)`、`draw`、`keypressed(key)` のいずれかを備えたプレーンな Lua テーブルです。

 これは、`SKILL.md` の短いスニペットの完全版です。 `state_stack.lua` を
プロジェクト ルートと `screens/` の下の画面にドロップします。

 ## `state_stack.lua`

```lua
-- state_stack.lua — minimal screen/state manager for LÖVE 11.x.
-- A screen is a table that may define: enter, leave, update(dt), draw, keypressed(key).
local Stack = { screens = {} }

-- Add a screen on top (e.g. open a pause overlay above the game).
function Stack.push(screen)
    table.insert(Stack.screens, screen)
    if screen.enter then screen:enter() end
end

-- Remove and return the top screen (e.g. close the pause overlay).
function Stack.pop()
    local screen = table.remove(Stack.screens)
    if screen and screen.leave then screen:leave() end
    return screen
end

-- Replace the top screen entirely (e.g. menu -> game).
function Stack.switch(screen)
    if #Stack.screens > 0 then Stack.pop() end
    Stack.push(screen)
end

function Stack.current()
    return Stack.screens[#Stack.screens]
end

return Stack
```

## `main.lua` に接続します

 各 LÖVE コールバックをトップ画面にデリゲートします。ヘルパーは
メソッドを省略した画面を許容するため、画面は必要なものだけを実装します。

```lua
local Stack = require("state_stack")

-- Call method `name` on the top screen if it exists.
local function forward(name, ...)
    local screen = Stack.current()
    if screen and screen[name] then screen[name](screen, ...) end
end

function love.load()        Stack.push(require("screens.menu")) end
function love.update(dt)    forward("update", dt) end
function love.draw()        forward("draw") end
function love.keypressed(k) forward("keypressed", k) end
```

### オーバーレイの描画 (一時停止したゲームの上に一時停止)

 一時停止画面の背後にゲームを表示し続けるには、すべての画面を下から上に描画しますが、上の画面のみを更新します:

```lua
function love.update(dt)
    forward("update", dt)                 -- only the top screen updates
end

function love.draw()
    for _, screen in ipairs(Stack.screens) do   -- draw all, bottom to top
        if screen.draw then screen:draw() end
    end
end
```

## 画面例

```lua
-- screens/menu.lua
local menu = {}

function menu:draw()
    love.graphics.setColor(1, 1, 1)
    love.graphics.print("MENU — press Enter to play, Esc to quit", 20, 20)
end

function menu:keypressed(key)
    if key == "return" then
        require("state_stack").switch(require("screens.game"))
    elseif key == "escape" then
        love.event.quit()
    end
end

return menu
```

```lua
-- screens/game.lua
local Stack = require("state_stack")
local game = {}

function game:enter()
    self.player = { x = 100, y = 100, speed = 220 }
end

function game:update(dt)
    if love.keyboard.isDown("right") then
        self.player.x = self.player.x + self.player.speed * dt   -- dt-scaled motion
    end
end

function game:draw()
    love.graphics.setColor(0.2, 0.8, 1.0)
    love.graphics.rectangle("fill", self.player.x, self.player.y, 40, 40)
    love.graphics.setColor(1, 1, 1)
    love.graphics.print("P = pause, hold Right to move", 20, 20)
end

function game:keypressed(key)
    if key == "p" then Stack.push(require("screens.pause")) end  -- overlay, game stays beneath
end

return game
```

```lua
-- screens/pause.lua
local Stack = require("state_stack")
local pause = {}

function pause:draw()
    -- Dim the game beneath, then label the overlay.
    love.graphics.setColor(0, 0, 0, 0.5)
    love.graphics.rectangle("fill", 0, 0, love.graphics.getWidth(), love.graphics.getHeight())
    love.graphics.setColor(1, 1, 1)
    love.graphics.print("PAUSED — press P to resume", 20, 60)
end

function pause:keypressed(key)
    if key == "p" then Stack.pop() end   -- return to the game underneath
end

return pause
```

## 注意事項

 - `require("screens.menu")` は呼び出しごとに **同じテーブル** を返すため (Lua はモジュールをキャッシュします)、ここでの
画面は事実上シングルトンです。インスタンスごとの最新の状態が必要な場合は、
 モジュールをファクトリー (`return function() return setmetatable({}, Screen) end`) にして呼び出します。
- 画面ロジックを `update`/`draw` に維持します。 `enter` でブロックしないでください。長いロードは、フレーム間で生成される
ロード画面に属します。
- このマネージャーには仕様上、トランジション/アニメーションがありません。クロスフェードが必要な場合は、
 が縮小するアルファ四角形を描画する上に `fade` 画面を追加します。スタックはすでにそれをサポートしています。 
