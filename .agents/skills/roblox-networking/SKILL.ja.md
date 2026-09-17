---
name: roblox-networking
description: >
  Design and harden Roblox client/server networking with RemoteEvent, RemoteFunction, and
  UnreliableRemoteEvent; server authority, argument and Instance validation, rate limits,
  proximity/ownership checks, targeted replication, streaming, lifecycle, prediction, and
  reconciliation. Use for Roblox remotes, exploits, request spam, multiplayer replication,
  network ownership, high-frequency cosmetic updates, or server/client desynchronization.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # Roblox ネットワーキング

 サーバーが権限のあるゲームの
状態を決定し、クライアントが入力またはインテントを提供する明示的なリクエストとレプリケーション コントラクトを構築します。 Roblox のローリング プラットフォーム API をターゲットとします。このスキルは、`roblox-luau` のネットワーキング入門書よりも
深く掘り下げられています。

 ##

 を使用する場合 - 境界を越えた Roblox 通信の設計、実装、デバッグ、またはセキュリティ保護に使用します。
- リモートがクライアント値を信頼する場合、悪用者が任意のインスタンス、メッセージ
スパム サービス、ストリーミング オブジェクトが見つからない場合、またはクライアントがサーバーと同意しない場合に使用します。

 **使用しない場合:** 基本的なルアウ/サービスは `roblox-luau` に属します。永続的な状態は
`roblox-datastores` に属します。物理的所有権メカニズムも `roblox-physics` で構成されます。

 ## ワークフロー

 1. **既存のプロトコルを検査します。** すべてのリモート エンドポイントと両方のエンドポイントを見つけます。ドキュメントの方向、
 送信者、ペイロード、頻度、権限、検証、およびコンシューマー。正規のリモート
フォルダーを再利用します。検出がスキップされたため、重複を作成しないでください。
2. **各メッセージを分類します。** クライアント リクエスト、サーバー ファクト、または一時的な外観サンプル。利便性ではなく、
 信頼できるイベント、信頼できないイベント、またはセマンティクスからの要求/応答を選択します。
3. **ペイロードを最小限に抑えます。** 安定した識別子とインテントを送信します。価格、ダメージ、
 の所有権の結果、任意のパス、またはサーバーが導き出すことができる計算結果を送信しないでください。
4. **レイヤーで検証します。** 高価な作業を行う前に、タイプ/形状/有限性、許可リストに登録された値、インスタンス クラスと
の祖先、プレーヤーの権限/状態、関連する距離/視線、サーバーのクールダウン、
、およびレートの予算を確認します。
5. **サーバーに適用します。** サーバーはターゲットを解決し、ヘルス、インベントリ、通貨、
 クールダウン、および進行状況を変更します。クライアント側のチェックにより UX は向上しますが、信頼は得られません。
6. **狭い範囲で複製します。** プライベートまたはローカルの事実には `FireClient` を使用します。共有された事実のみを放送します。
クライアントが個別のプレゼンテーション イベントを必要としない限り、レプリケートされたプロパティを再度送信することは避けてください。
7. **処理時間とライフサイクル。** リクエストは、死亡、リスポーン、ストリーミング変更、または
切断後に到着する可能性があります。処理中に現在のキャラクター/状態を解決し、プレイヤーごとのリミッター データをクリーンアップします。
8. **サーバーとクライアントで確認します。** 通常、不正な形式、スパム、範囲外、古い
キャラクター、急速なリスポーン、離脱、同時プレイヤー、ターゲット、およびブロードキャスト ケースを実行します。
サーバーと各クライアントの出力を個別に検査します。

 ## トランスポートを選択します

 |プリミティブ |使用 | | は使用しないでください。
|---|---|---|
| `RemoteEvent` |順序付けられた、信頼できる一方的な要求/事実 |古いものを新しいものに置き換える連続サンプル |
| `UnreliableRemoteEvent` |一時的な表面的/継続的な状態で、損失と再順序付けに耐性がある |購入、ダメージの決定、インベントリ、ワンショットの状態遷移 |
| `RemoteFunction` |本当に即時応答が必要な、クライアントからサーバーへの限定されたクエリ |サーバーからクライアントへの呼び出し。長時間/不確実な仕事。通常のコマンド |

 サーバーからクライアントを同期的に呼び出さないでください。クライアントが切断されたり、エラーが発生したり、
 が返されなかったりする場合があります。サーバー `RemoteEvent:FireClient()` を優先し、必要に応じて別の応答イベントを使用します。

 ## パターン: ゲームプレイを解決する前に検証

```lua
-- ServerScriptService/CombatRequests.server.luau
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local attack = ReplicatedStorage.Remotes.Attack
local lastRequest: {[Player]: number} = {}
local RANGE = 12
local COOLDOWN = 0.25

attack.OnServerEvent:Connect(function(player: Player, target: unknown)
    local now = Workspace:GetServerTimeNow()
    if now - (lastRequest[player] or -math.huge) < COOLDOWN then return end
    lastRequest[player] = now

    if typeof(target) ~= "Instance" or not target:IsA("Model") then return end
    if not target:IsDescendantOf(Workspace.Characters) then return end
    local targetHumanoid = target:FindFirstChildOfClass("Humanoid")
    local targetRoot = target:FindFirstChild("HumanoidRootPart")
    local character = player.Character
    local root = character and character:FindFirstChild("HumanoidRootPart")
    local humanoid = character and character:FindFirstChildOfClass("Humanoid")
    if not targetHumanoid or not targetRoot or not root or not humanoid then return end
    if humanoid.Health <= 0 or targetHumanoid.Health <= 0 then return end
    if (root.Position - targetRoot.Position).Magnitude > RANGE then return end
    if not serverCombatStateAllowsAttack(player, now) then return end

    targetHumanoid:TakeDamage(serverDamageFor(player))
end)

Players.PlayerRemoving:Connect(function(player)
    lastRequest[player] = nil
end)
```

これはまだコンパクトな例にすぎません。実際の近接攻撃システムでは、サーバーで認識されている攻撃ウィンドウ、
 視線/形状チェック、チーム ルール、ラグ ポリシーが必要になる場合があります。 1 回の距離チェックをセキュリティとして扱わないでください。

 ## パターン: 境界のトークン バケット

```lua
type Bucket = {tokens: number, updatedAt: number}
local buckets: {[Player]: Bucket} = {}
local CAPACITY, REFILL_PER_SECOND = 6, 3

local function consume(player: Player, cost: number): boolean
    local now = os.clock()
    local bucket = buckets[player] or {tokens = CAPACITY, updatedAt = now}
    bucket.tokens = math.min(CAPACITY,
        bucket.tokens + (now - bucket.updatedAt) * REFILL_PER_SECOND)
    bucket.updatedAt = now
    if bucket.tokens < cost then buckets[player] = bucket; return false end
    bucket.tokens -= cost
    buckets[player] = bucket
    return true
end
```

サーバーへの影響に応じてコストを割り当てます。データストアの呼び出し、クローン作成、レイキャスト、または広範な
レプリケーションの前に、安価に拒否します。拒否されたパケットごとに 1 つの警告ではなく、集計された不正行為シグナルをログに記録します。

 ## レプリケーション、ストリーミング、予測

 - レプリケートされたインスタンス/プロパティはすでに状態チャネルです。 DataModel の無条件の並列コピーではなく、意図、プライベート
状態、またはプレゼンテーション キューにリモートを使用します。
- インスタンスのストリーミングでは、有効なサーバー インスタンスがクライアントに存在しない可能性があります。安定した ID を送信すると、
 は不在を許容します。オプションのストリーミング コンテンツを永遠に待つ必要はありません。
- 高レートの表示データは `UnreliableRemoteEvent` を使用する場合があります。
の配送と順序は保証されていないため、各サンプルを自己完結型にしてください。 **1000 バイトを超えるペイロードはドロップされます** (スタジオ出力
が超過を報告します)。 `RemoteEvent` と `UnreliableRemoteEvent` は、そのタイプのすべてのリモートでカウントすると、およそ
**クライアントごとに 500 コール/秒** のスロットルを共有します。これは、
 の正当なプレーヤーが攻撃者より先に攻撃することです。
- 遅延に敏感な可逆プレゼンテーションのみを予測します。クライアント シーケンス/コマンド ID を含めます。
サーバーは権限のある状態と確認応答を返します。クライアントはスムーズに修正します。決して
で予測にダメージ、通貨、インベントリ、進行状況を与えないでください。
- ネットワークの所有権により応答性が向上しますが、そのクライアントが物理シミュレーションに影響を与えることができます。
サーバー上でのゲームプレイの影響を検証します。所有権は承認ではありません。

 ## よくある失敗

 |症状 |考えられる原因 |救済策 |
|---|---|---|
|搾取者は損害と代償を選択 |クライアントから受け入れられた結果 |インテント/IDを送信します。サーバー上で導出して適用する |
|任意のオブジェクトを削除可能 | `typeof(Instance)` のみがチェックされました |クラス、祖先、所有権、状態、および許可リストに登録された操作を検証します。
|プレーヤーでサーバーが停止する |サーバーはクライアント `RemoteFunction` を呼び出します。非同期イベントに置き換える |
|有効なプレーヤーがスロットリングをトリガーする |フレームごとの信頼できるメッセージ |周波数が低い、状態のレプリケーション、バッチ処理、または信頼性の低い化粧品 |
|古いパケットは新しい効果を逆転します。順序付けされていない信頼性の低いサンプルはコマンドとして扱われます。サンプルを置き換え可能/バージョン管理できるようにします。遷移に信頼できるイベントを使用する |
|リスポーン後にリモートが中断する |キャッシュされた文字/ルート |処理中に現在の文字を解決し、古い状態を拒否します。
|個人情報漏洩 |デフォルトで使用される `FireAllClients` | `FireClient` と最小限のペイロードを使用します。
|距離チェックはバイパスされます |クライアント所有のオブジェクトがターゲットの近くに移動しました |サーバー独自の重要なオブジェクトをアンカーし、完全なサーバー コンテキストを検証します。

 ## リソース

 - ペイロード ルール、インスタンス/有限性チェック、
 レプリケーション設計、および必要なマルチクライアント不正使用マトリックスについては、`references/validation-and-testing.md` をお読みください。

 ## 関連スキル

 - `roblox-luau` — 実行場所と基本的な RemoteEvent メカニズム。
- `roblox-characters` — リスポーンセーフなキャラクター解像度。
- `roblox-physics` — ネットワークの所有権、レイ/オーバーラップの検証、および物理的な影響。
- `roblox-studio-workflow` — サーバーとクライアントのテストと出力検査。

 ## 一次参照

 - `https://create.roblox.com/docs/scripting/events/remote`
- `https://create.roblox.com/docs/scripting/security/client-server-boundary`
- `https://create.roblox.com/docs/physics/network-ownership`
- `https://create.roblox.com/docs/studio/testing-modes` 
