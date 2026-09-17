---
name: game-ai
description: >
  Design NPC and enemy decision-making with finite state machines, behavior
  trees, steering behaviors, and A* pathfinding — engine-neutral algorithms
  that pair with the detected engine's navigation API. Use when building enemy
  AI, an FSM or behavior tree, steering/flocking, or pathfinding, or when the
  user mentions state machine, behavior tree, blackboard, A*, navmesh, seek, or
  patrol/chase.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # ゲーム AI: 決定、ステアリング、および経路探索

 3 つの分離可能なレイヤーから信頼できる NPC の動作を構築します: **決定** (
 が何をするか)、**ステアリング** (そこに移動する方法)、**パス** (マップ上でルートを設定する方法)。
それらを分離したままにします。ビヘイビア ツリーがターゲットを選択し、パスファインダーが
ウェイポイントを生成し、ステアリングがそれに追従します。このスキルは、エンジンに依存しない
アルゴリズムを学習します。以下の関連スキルを介してそれらをエンジンにバインドします。

 ##

 を使用する場合 - 敵/NPC ロジックを実装する場合に使用します: パトロール、追跡/逃走、警備状態、
 グループの移動、または「プレイヤーへのパスの検索」。
- **FSM** (いくつかのクリア状態)、**動作ツリー** (優先順位のある多くの
リアクティブ動作)、または **ステアリング** (スムーズなローカル移動) のいずれかを選択するために使用します。
- パスファインディングを統合する場合に使用します: グリッド/グラフ上の A*、またはエンジン
ナビメッシュ エージェントを駆動します。

 **使用しない*場合:** エンジンの具体的なナビメッシュ/エージェント API とベイクに、
 は `unity-navmesh`、`unreal-behavior-trees`、または Godot の `NavigationAgent2D/3D`
を使用します (エンジン スキルを参照)。移動/衝突感を求める場合は、`physics-tuning`を使用してください。レーンに沿って波を生成する
については、`tower-defense` ジャンル スキルを参照してください。

 ## コア ワークフロー

 1. **複雑さによって意思決定モデルを選択します。** 明らかな
遷移がある 2 ～ 5 つの状態 → FSM。多くの動作、優先順位、中断、再利用 → 動作
ツリー。継続的な「各オプションをどれだけ強く望むか」→ユーティリティのスコアリング。
2. **モーションから決定を分離します。** 決定レイヤーは *意図*
(ターゲット位置、アクション) を出力します。ステアリングや経路探索により、意図が動きに変わります。
3. **右側のグラフのパス** グリッド タイル、ウェイポイント グラフ、またはベイクされたナビゲーションメッシュ。
ノードが少ない = A* が高速です。 3D にはエンジンのナビメッシュを優先します。
タイル ゲームのグリッド上の A*。
4. **ゴールに向かってまっすぐではなく、**パスに沿って操縦します** - 次のウェイポイントに従い、近づくと
が進むため、エージェントは角を曲がります。
5. **パスを控えめに再計算します。** パス検索は、フレームごとではなく、タイマーまたはゴールが
タイルを移動したときに行います。パスをキャッシュします。ウェイポイントインデックスのみが進みます。
6. **観察によって確認します。** エージェントを観察します。エージェントはゴールに到達しますか、コーナーで
スタックしますか、状態間で振動しますか?チューニング中のパスと現在の状態を
画面に描画します。

 ## パターン

 ### 1. 有限状態マシン (1 つの状態オブジェクト、明示的な遷移)

```gdscript
# Each state is a small object with enter/update/exit. The machine owns "current".
class_name State
func enter(agent): pass
func update(agent, dt) -> State: return null   # return a new state to transition
func exit(agent): pass

# --- Chase state: returns Patrol when the player escapes sight range ---
class Chase extends State:
    func update(agent, dt) -> State:
        if not agent.can_see(agent.target):
            return Patrol.new()                 # transition by returning next state
        agent.move_toward(agent.target.position, dt)
        return null                             # null = stay in this state

# --- Driver: call once per frame ---
func tick(dt):
    var next = current.update(self, dt)
    if next != null:
        current.exit(self); next.enter(self); current = next
```

遷移ロジックを状態の「内部」(またはテーブル内) に保持し、`if` フラグの増大する山
として決して保持しないでください。 1 つの国家が 1 つの行動を所有します。これが FSM を読み取り可能に保つためのものです。

 ### 2. 動作ツリーのティック (複合ノードはステータスを返します)

```gdscript
# A node's tick() returns SUCCESS, FAILURE, or RUNNING (still working this frame).
enum Status { SUCCESS, FAILURE, RUNNING }

# Sequence: run children in order; stop at the first non-SUCCESS (logical AND).
func sequence_tick(children, agent, dt) -> int:
    for child in children:
        var s = child.tick(agent, dt)
        if s != Status.SUCCESS:
            return s                 # FAILURE or RUNNING short-circuits the sequence
    return Status.SUCCESS

# Selector: try children until one succeeds or is RUNNING (logical OR / fallback).
func selector_tick(children, agent, dt) -> int:
    for child in children:
        var s = child.tick(agent, dt)
        if s != Status.FAILURE:
            return s                 # SUCCESS or RUNNING stops the search
    return Status.FAILURE
```

ガード AI はトップダウンで次のように読みます: `Selector[ Sequence[CanSeePlayer?, Chase], Patrol ]`
— 見えていれば追跡し、そうでなければパトロールします。
リーフ ノード、デコレーター (インバーター、クールダウン)、および黒板については、「`references/behavior-trees.md`」を参照してください。

 ### 3. ステアリング: シークと到着 (スムーズ、フレームレートに依存しない)

```gdscript
# Seek: accelerate toward a target at full speed. Steering = desired - current.
func seek(pos, vel, target, max_speed, max_force) -> Vector2:
    var desired = (target - pos).normalized() * max_speed
    return (desired - vel).limit_length(max_force)   # a force, not a teleport

# Arrive: like seek, but ramp speed down inside slow_radius so it stops cleanly.
func arrive(pos, vel, target, max_speed, max_force, slow_radius) -> Vector2:
    var offset = target - pos
    var dist = offset.length()
    if dist < 0.001: return -vel                      # already there: kill drift
    var ramped = max_speed * min(dist / slow_radius, 1.0)
    var desired = offset / dist * ramped
    return (desired - vel).limit_length(max_force)

# Per frame: vel += steering * dt; pos += vel * dt   (always scale by dt)
```

### 4. A* ヒューリスティックは過大評価してはなりません (または、パスが最短にならなくなります)

```python
# Match the heuristic to the movement. An ADMISSIBLE heuristic (never larger
# than the true remaining cost) keeps A* optimal.
def heuristic(a, b):
    dx, dy = abs(a.x - b.x), abs(a.y - b.y)
    # return dx + dy             # Manhattan: 4-direction grids (no diagonals)
    return (dx + dy) + (1.414 - 2) * min(dx, dy)   # octile: 8-direction grids
# f(n) = g(n) + h(n): g = cost from start, h = heuristic to goal.
# Overestimating h is faster but no longer guarantees the shortest path.
```

完全な A* ループ (優先キュー、`came_from` 再構成、グリッド + ウェイポイント
グラフ) は `references/pathfinding.md` にあります。

 ## 落とし穴

 - **すべてのフレームのパスファインディング**により、フレーム レートが低下します。ターゲットが新しいタイルに移動したときに、タイマーまたは
のみで再計算します。間にキャッシュされたウェイポイントをたどります。
- **次のウェイポイントではなく、ゴールに向かってまっすぐ**すると、エージェント
は壁や角に抱きつくようになります。道に従ってください。半径内に入ったらウェイポイントを進めます。
- **許容できない A\* ヒューリスティック** (例: スケールアップされたユークリッド距離、または対角グリッド上のマンハッタン 
) は、高速ではあるが *最短ではない* パスを返します。許可された動きと一致するヒューリスティック
を選択します。
- **複数フレーム アクション
(歩行、アニメーションの再生) で RUNNING を返さないビヘイビアー ツリー リーフがあると、ツリーは
ティックごとにアクションを再開します。アクションが完了するまで RUNNING を返します。
- **FSM 移行スパゲッティ**: `if state == ...` チェックをあらゆる場所に散布します。
は、防止するために FSM が存在する混乱を再作成します。状態の遷移を維持します。
- **見通し線もチェックもスタックなし** → エージェントは永遠に壁に食い込みます。再パスまたは状態変更を強制する
タイムアウトを追加します。

 ## 参照

 - `references/pathfinding.md` — 完全な A* (優先キュー、再構築)、
 グリッドとウェイポイントのグラフ、エンジン ナビメッシュに従うタイミング。
- `references/behavior-trees.md` — ノード分類、リーフ/デコレーター実装、
 黒板、および FSM 対 BT の選択。

 ## 関連スキル

 - `unity-navmesh`、`unreal-behavior-trees` — コンクリート エンジン AI/ナビゲーション API。
- `physics-tuning` — 移動、衝突反応、エージェントの半径。
- `procedural-gen` — AI がナビゲートするグラフ/レベルを生成します。
- `tower-defense`、`fps-shooter` — このスキルを構成するジャンル。 
