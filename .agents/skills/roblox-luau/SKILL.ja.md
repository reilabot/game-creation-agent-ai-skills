---
name: roblox-luau
description: >
  Script a Roblox experience in Luau: get services, create and parent Instances,
  connect events, run server Scripts vs client LocalScripts, and communicate across
  the client/server boundary with RemoteEvents/RemoteFunctions (server-authoritative).
  Use when building or debugging Roblox Studio scripts — when the user mentions
  Roblox, Luau, services, RemoteEvent, Instance.new, PlayerAdded, or client vs
  server. For saving player data use roblox-datastores.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # Roblox Luau スクリプト

 **Luau** での Roblox エクスペリエンスのスクリプトを作成します: サービス、`Instance`、イベント、
 サーバー/クライアント分割、安全な境界越え通信。現在の
Roblox エンジンと Studio をターゲットとします。

 ##

 を使用する場合 - Roblox スクリプトを作成するときに使用します: サービスの取得、インスタンスの作成/親化、イベントの
接続、サーバーとクライアントの決定、または `RemoteEvent`/
`RemoteFunction` 通信の配線。
- プロジェクトに `Script`/`LocalScript`/`ModuleScript` オブジェクト、`.rbxl(x)`
プレース、または Rojo `*.project.json` があり、コードが `game:GetService(...)` を呼び出す場合に使用します。

 **使用しない*場合:** セッション間でデータを永続化 → `roblox-datastores`。
リモート プロトコル アーキテクチャ、エクスプロイト強化、レート制限、高頻度レプリケーション、および
マルチクライアント不正行為テスト → `roblox-networking`。 Roblox
API に関係のない一般的な Lua の質問。エンジンに依存しない入力/保存アーキテクチャ → `input-systems` / `save-systems`。

 ## コア ワークフロー

 1. **`game:GetService("Name")` でサービスを取得します。** 一般的なもの: `Players`、
 `Workspace`、`ReplicatedStorage` (共有クライアント + サーバー)、 `ServerScriptService`
(サーバー専用コード)、`ServerStorage`、`RunService`、`UserInputService` (クライアント)。
2. **コードが実行される場所を確認します。** `Script` は **サーバー** 上で実行されます。 `LocalScript`
は **クライアント** (`StarterPlayerScripts`、`StarterGui`、またはプレイヤーの
キャラクター内) 上で実行されます。 `ModuleScript` は、`require` と共有されるコードです。
3. **インスタンスを意図的に作成します。** `local p = Instance.new("Part")`、その
プロパティを設定してから、`p.Parent` **last** (ペアレント化によりレプリケーションがトリガーされます) を設定します。
4. **イベントに反応します。** `:Connect` から `Players.PlayerAdded`、
 `part.Touched`、または `RunService.Heartbeat` などのシグナルに反応します。漏れを避けるため、完了したら接続を外してください。
5. **リモートとクライアント/サーバーの境界を越えてください。決してクライアントを信頼しないでください。**
クライアントは `RemoteEvent:FireServer(...)` 経由でリクエストします。サーバーが検証し、
 が適用されます。サーバーはすべてのゲーム状態に対して権限を持っています。
6. Play / Play Here / サーバー + クライアントを使用して **Studio でテスト**します。 [出力 
] ウィンドウとサーバー/クライアント ビューの切り替えを使用して、コードが実行された場所を確認します。

 ## パターン

 ### 1. サーバー スクリプト: プレイヤーの参加に反応する (リーダー統計)

```lua
-- ServerScriptService/Leaderboard.server.luau  (a Script = runs on the server)
local Players = game:GetService("Players")

local function onPlayerAdded(player: Player)
    local stats = Instance.new("Folder")
    stats.Name = "leaderstats"          -- this name makes it show on the leaderboard

    local coins = Instance.new("IntValue")
    coins.Name = "Coins"
    coins.Value = 0
    coins.Parent = stats

    stats.Parent = player               -- parent LAST
end

Players.PlayerAdded:Connect(onPlayerAdded)
```

### 2. インスタンスの作成と構成

```lua
local Workspace = game:GetService("Workspace")

local part = Instance.new("Part")
part.Size = Vector3.new(4, 1, 4)
part.Position = Vector3.new(0, 10, 0)
part.Anchored = true                    -- won't fall under gravity
part.BrickColor = BrickColor.new("Bright blue")
part.Parent = Workspace                 -- set Parent last so it replicates once, fully
```

### 3. イベントを接続します (リークを避けるために切断します)

```lua
local debounce = false
local connection
connection = part.Touched:Connect(function(hit: BasePart)
    local character = hit.Parent
    local humanoid = character and character:FindFirstChildOfClass("Humanoid")
    if not humanoid or debounce then return end
    debounce = true
    humanoid.Health -= 10
    task.wait(1)                        -- task.wait, NOT the deprecated wait()
    debounce = false
end)

-- Later, when the part is removed or the round ends:
-- connection:Disconnect()
```

### 4. RemoteEvent によるクライアント → サーバー (サーバー上で検証!)

```lua
-- ReplicatedStorage: create a RemoteEvent named "BuyItem" (in Studio or via code).
-- CLIENT (LocalScript): request a purchase. The client can lie — this is only a request.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local buyItem = ReplicatedStorage:WaitForChild("BuyItem")  -- wait: may not have replicated yet
buyButton.MouseButton1Click:Connect(function()
    buyItem:FireServer("sword")        -- send the item id only; never the price/result
end)
```

```lua
-- SERVER (Script): the ONLY place the transaction is decided.
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local buyItem = ReplicatedStorage:WaitForChild("BuyItem")
local PRICES = { sword = 100, shield = 75 }

buyItem.OnServerEvent:Connect(function(player: Player, itemId)
    -- TRUST NOTHING from the client. Validate types and values.
    if type(itemId) ~= "string" then return end
    local price = PRICES[itemId]
    if not price then return end                         -- unknown item
    local coins = player.leaderstats.Coins
    if coins.Value < price then return end               -- can't afford
    coins.Value -= price                                 -- server applies the change
    grantItem(player, itemId)
end)
```

### 5. RunService によるフレームごとのループ

```lua
local RunService = game:GetService("RunService")
-- Heartbeat fires every frame AFTER physics; dt is seconds since the last step.
RunService.Heartbeat:Connect(function(dt)
    spinner.CFrame *= CFrame.Angles(0, math.rad(90) * dt, 0)  -- 90deg/sec, frame-independent
end)
```

### 6. ModuleScript 内の共有コード

```lua
-- ReplicatedStorage/GameConfig (a ModuleScript) — usable by server and client.
local GameConfig = {}
GameConfig.MaxHealth = 100
function GameConfig.damageFor(weapon: string): number
    return ({ sword = 25, bow = 15 })[weapon] or 0
end
return GameConfig
```

```lua
local GameConfig = require(game:GetService("ReplicatedStorage"):WaitForChild("GameConfig"))
print(GameConfig.MaxHealth)
```

## 落とし穴

 - **クライアントを信頼することは悪用です** → クライアントは、あらゆる引数を
`RemoteEvent`/`RemoteFunction` に送信できます。
サーバー上のすべての引数の型と範囲を検証し、正常性、通貨、在庫に対するサーバーの権限を維持します。
- **`LocalScript` を置いた場所で実行されない** → LocalScript は、
、`StarterPlayerScripts`、`StarterCharacterScripts`、`StarterGui`、またはツールで実行されます。
 `Workspace` または `ServerScriptService` では実行されません。サーバー `Script` は、
 `ServerScriptService`/`Workspace` に属します。
- **非推奨のグローバル** → 古い
`wait()`/`spawn()`/`delay()` ではなく、`task.wait`/`task.spawn`/`task.delay` を使用してください (スケジュールとスロットリングが悪化します)。
- **最初にペアレントを作成し、次にプロパティを設定します** → 最初にプロパティを設定し、最後に `Parent`
を実行するため、インスタンスは最終状態で 1 回レプリケートされます。
- **参加直後のクライアント上の `nil`** → オブジェクトは時間の経過とともにストリーミング/複製されます。クライアントで直接インデックスを作成する代わりに、
 `parent:WaitForChild("Name")` を使用します。
- **接続が切断されることはありません** → 長期にわたる `:Connect` ハンドラーがリークし、破壊されたオブジェクトに対して
を起動する可能性があります。接続と `:Disconnect()` を保存します (または、必要に応じて
`Instance:GetAttributeChangedSignal`/`:Once` を使用します)。
- **RemoteEvent が適合する RemoteFunction の使用** → `RemoteFunction` は戻りを待つ
をブロックし、悪意のある/遅いクライアントはサーバーを停止させる可能性があります。本当に返信が必要な場合を除き、
 の一方向 `RemoteEvent` を優先します。

 ## 参照

 - 完全なクライアント/サーバー モデルの場合 (レプリケーション、`RemoteFunction` 対 `RemoteEvent`、
 `:WaitForChild` タイミング、同一コンテキスト メッセージング、属性、
`CollectionService` タグ、および `:Once`/接続クリーンアップ)、
 `references/client-server.md` を読み取ります。

 ## 関連スキル

 - `roblox-datastores` — セッション間でプレーヤー データを保持します (サーバーのみ)。
- `roblox-networking` — 運用リモート契約、サーバー検証、レート制限、レプリケーション、
 ストリーミング、予測、およびマルチクライアント テスト。
- `save-systems` — エンジンに依存しない永続性の概念。
- `game-ai` / `input-systems` — Luau に実装するポータブル AI および入力パターン。 
