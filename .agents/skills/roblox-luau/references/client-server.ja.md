# Roblox クライアント/サーバー モデルと通信 (現在のエンジン)

 Luau スキルの詳細: コードがマシン間でどのように分割されるか、メッセージング
プリミティブ、レプリケーションのタイミング、およびタグ/属性。

 ## コードが実行される場所

 |コンテナ |実行日 | | に使用します。
|-----------|---------|---------|
| `ServerScriptService` |サーバー |権威あるゲームロジック (`Script`) |
| `ServerStorage` |サーバー |クライアントが決して見てはいけない資産/データ |
| `ReplicatedStorage` |両方 |リモート、`ModuleScript`、共有アセット |
| `StarterPlayerScripts` |クライアント |永続的なクライアント ロジック (`LocalScript`) |
| `StarterCharacterScripts` |クライアント |キャラクターごとのクライアント ロジック |
| `StarterGui` |クライアント | UI スクリプト |

 サーバーは権威ある世界をシミュレートします。各クライアントは独自のビューをレンダリングし、
 が入力を送信します。 Roblox は常にクライアント→サーバーのレプリケーションをフィルタリングするため、クライアントはサーバー所有の状態を
直接変更できません。リモート経由でのみ要求できます。

 ## RemoteEvent と RemoteFunction

 どちらも `ReplicatedStorage` に存在するため、どちらの側でも見つけることができます。

 - **RemoteEvent** — ファイアアンドフォーゲット、一方向、非同期。
- クライアント→サーバー: `remote:FireServer(args)` → サーバーは `remote.OnServerEvent:Connect(function(player, args) ... end)` を処理します。 `player` はエンジンによって噴射され、信頼できます。それ以降はすべてそうではありません。
- サーバー→クライアント: `remote:FireClient(player, args)` または `remote:FireAllClients(args)` → クライアントは `remote.OnClientEvent:Connect(function(args) ... end)` を処理します。

 - **RemoteFunction** — リクエスト/レスポンス。呼び出し元は戻り値を **譲ります**。
- クライアント→サーバー: `local result = remote:InvokeServer(args)`;サーバーは `remote.OnServerInvoke = function(player, args) return ... end` を定義します。
- ほとんどの場合、`RemoteEvent` を優先します。 **サーバーによってクライアント上で呼び出される `RemoteFunction`** は危険です。悪意のあるクライアントは戻れなくなるか、エラーが発生してサーバーがハングする可能性があります。クライアント→サーバーのみを呼び出し、検証し、タイムアウトを考慮します。

 ### すべてのサーバー ハンドラーのセキュリティ チェックリスト

 1. 引数 **タイプ** を検証します (`type(x) ~= "number"` → 拒否)。
2. 引数 **範囲/アイデンティティ** を検証します (このアイテムは存在しますか? このプレイヤーはそれを買う余裕がありますか? 彼らが操作しているものを所有していますか?)。
3. アクションが高価な場合はレート制限を行います (プレイヤーごとの最終呼び出し時間を追跡します)。
4. 機密データ (価格、戦利品テーブル、他のプレイヤーの個人データ) を「返されるために」
クライアントに送信しないでください。サーバー上で決定します。

 ## BindableEvent / BindableFunction

 **同じマシン内** (サーバー間スクリプト、またはクライアントから
クライアント) のメッセージングには、`BindableEvent`/`BindableFunction` を使用します。これらはネットワークを越えず、
 にはセキュリティ境界がありません。リモートの代わりに使用しないでください。

 ## レプリケーションのタイミングと WaitForChild

 クライアントが起動すると、時間の経過とともにデータ モデルがストリーミングされるため、
 が期待する子がまだ存在しない可能性があります。クライアントでは、

を使用します。```lua
local remote = ReplicatedStorage:WaitForChild("BuyItem")        -- yields until it exists
local gui = player:WaitForChild("PlayerGui"):WaitForChild("HUD")
```

`WaitForChild` はオプションのタイムアウトを受け入れます。何もない場合は、約 5 秒後に警告が表示されます。
サーバー上には、作成したインスタンスがすぐに存在するため、直接インデックスを作成しても問題ありません。

 ## 接続とクリーンアップ

 `:Connect` は `RBXScriptConnection` を返します。
切断されない長期間の接続がリークし、破棄されたインスタンスで起動される可能性があります:

```lua
local conn = part.Touched:Connect(onTouch)
-- when done:
conn:Disconnect()

-- One-shot: auto-disconnects after the first fire.
part.Touched:Once(onTouchOnce)

-- Clean up everything tied to a player on leave:
Players.PlayerRemoving:Connect(function(player) cleanupFor(player) end)
```

## 属性と CollectionService タグ

 - **属性** は、型指定されたメタデータをインスタンスに直接保存し、
 クライアント (`part:SetAttribute("Damage", 25)`、`part:GetAttribute("Damage")`、および
`part:GetAttributeChangedSignal("Damage"):Connect(...)`) に複製します。余分な `Value` オブジェクトを使用せず、デザイナーが調整可能な
値に適しています。
- **CollectionService タグ** は、データ駆動型システムの文字列タグによってインスタンスをグループ化します:

```lua
local CollectionService = game:GetService("CollectionService")
for _, door in CollectionService:GetTagged("Door") do
    setupDoor(door)
end
CollectionService:GetInstanceAddedSignal("Door"):Connect(setupDoor)
```

タグと属性を組み合わせて使用​​すると、ハードコーディングされた参照を使用せずに、タグ付けされた
インスタンス (デザイナーが Studio に配置したもの) を選択する動作システムを構築できます。

 ## スタジオ テスト

 - **プレイ** — サーバーとクライアントを組み合わせたセッションでのアバター。
- **実行** — プレーヤーを使用しないサーバー シミュレーション。
- **開始 (ローカル サーバー)** — 個別のサーバー + N クライアント ウィンドウ。
がレプリケーションとリモートを適切にテストする唯一の方法です。サーバー/クライアント ビューの切り替えと
出力ウィンドウを使用して、メッセージがどちら側から来たかを確認します。 
