# ビヘイビア ツリー、FSM、および黒板

 **ビヘイビア ツリー** (BT) は、フレームごとにルートからチェックされたノードのツリーです。
すべてのノードの `tick()` は、次の 3 つのステータスのいずれかを返します。

 - `SUCCESS` — ノードはこのフレームでジョブを終了しました。
- `FAILURE` — ノードはジョブを実行できませんでした。
- `RUNNING` — ノードにはさらに多くのフレーム (歩行、アニメーション、待機) が必要です。

 制御はルートから下に流れます。ステータスが元に戻ります。ツリーの形状
*は優先ロジックです。これが、BT がフラット FSM の
よりもはるかに優れた多くの動作に対応できる理由です。

 ## ノード分類

 |カテゴリー |ノード |行動 |
|---|---|---|
|複合 | **シーケンス** |子を左→右にチェックマークを付けます。最初の非 `SUCCESS` で戻ります。論理積。 |
|複合 | **セレクター** (フォールバック) |子を左→右にチェックマークを付けます。最初の非 `FAILURE` で戻ります。論理和。 |
|複合 | **パラレル** |すべての子にチェックを入れます。ポリシーの成功/失敗 (例: N は成功する必要があります)。 |
|デコレーター | **インバーター** | `SUCCESS`↔`FAILURE`を交換します。 `RUNNING`を通過させます。 |
|デコレーター | **繰り返し / 失敗するまで繰り返し** |子供に何度も繰り返しチェックを入れます。 |
|デコレーター | **クールダウン/タイムアウト** |子どもにゲートを与えたり、時間を制限したりする。 |
|葉 | **状態** |世界/黒板をテストします → `SUCCESS`/`FAILURE` (副作用なし)。 |
|葉 | **アクション** |何かをしてください。完了するまで `RUNNING` を返します。 |

 ## ステートフル コンポジットと RUNNING

 Naive コンポジットは、ティックごとに最初の子から再開されます。マルチフレーム
アクションの場合、コンポジットは **どの子が実行中だったかを記憶**し、そこから再開する必要があります:

```gdscript
class Sequence:
    var children = []
    var _running = 0                 # index of the child that returned RUNNING

    func tick(agent, dt) -> int:
        while _running < children.size():
            var s = children[_running].tick(agent, dt)
            if s == Status.RUNNING:
                return Status.RUNNING        # resume here next frame
            if s == Status.FAILURE:
                _running = 0                 # whole sequence fails; reset
                return Status.FAILURE
            _running += 1                    # child SUCCESS -> advance
        _running = 0                         # reached the end -> sequence succeeds
        return Status.SUCCESS
```

セレクターは鏡像です。`FAILURE` で進み、`SUCCESS`
または `RUNNING` で戻り、子が成功するとインデックスをリセットします。

 ## リーフの例

```gdscript
# Condition leaf: pure test, no side effects.
class CanSeePlayer:
    func tick(agent, dt) -> int:
        return Status.SUCCESS if agent.can_see(agent.blackboard.player) else Status.FAILURE

# Action leaf: multi-frame, returns RUNNING until it arrives.
class MoveTo:
    var key  # blackboard key holding the destination
    func tick(agent, dt) -> int:
        var dest = agent.blackboard.get(key)
        if dest == null: return Status.FAILURE
        agent.move_toward(dest, dt)
        return Status.SUCCESS if agent.position.distance_to(dest) < 4.0 else Status.RUNNING
```

ツリーとしての完全なガード:

```
Selector
├── Sequence            # attack branch (highest priority)
│   ├── CanSeePlayer
│   ├── MoveTo(player)
│   └── Attack
└── Patrol              # fallback when nothing else applies
```

## 黒板

 **ブラックボード**は、ノードを分離する共有メモリです。条件によって読み取られ、
 アクションによって書き込まれます。また、他のノードへのハード参照を保持するノードはありません。
の現在のターゲット、最後に確認された位置、ホーム ポイント、パス、タイマーをそこに保存します。これは、同じ `MoveTo` アクションでサブツリーの追跡、パトロール、および逃走を可能にする
です。

```gdscript
# A blackboard is just a typed key/value store on the agent.
agent.blackboard = {
    "player": null,            # set by perception each tick
    "home": Vector2(100, 100),
    "path": [],                # filled by the pathfinder
}
```

## FSM と動作ツリー —
の選択
| FSM は次の場合に使用します。 |次の場合にビヘイビア ツリーを使用します。 |
|---|---|
| 2 ～ 5 つの明確に名前が付けられた州 |優先順位のある多くの動作 |
|遷移は明白であり、ほとんどありません。動作は相互に割り込み/プリエンプトします。
|動作はほとんど変わりません。敵全体でサブツリーを再利用したい。
|最もシンプルなものが必要です |デザイナーが調整可能なデータ駆動型の AI が必要です |

 出荷中のゲームの多くは、トップレベル モード (アイドル / 戦闘 /
デッド) の FSM と戦闘状態内のビヘイビアー ツリーの**両方**を使用します。 FSM から始めます。 `if` ロジックがいくつかの遷移を超えた場合、
 状態をビヘイビア ツリーに移行します。

 ## ユーティリティ AI (概要)

 離散状態よりも「各オプションがどれだけ欲しいか」の方が重要な場合は、各候補アクションをユーティリティ関数で
スコアリングし、最も高いものを選択します。

```
score(action) = sum of weighted considerations, each a 0..1 curve of a fact
choose the action with the maximum score (optionally softmax for variety)
```

ユーティリティは、微妙なトレードオフ (体力/弾薬/
距離による回復 vs 攻撃 vs 逃げる) に合わせてスケールしますが、デバッグはツリーよりも困難です。 BT の分岐
が条件の茂みになったときに手を伸ばしてください。 
