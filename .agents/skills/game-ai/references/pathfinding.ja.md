# パスファインディング: A* 完全版

 A* は、**グラフ** (ノード + 加重エッジ) 上の最短パスを検索します。グリッドは
グラフの一種にすぎません。ノードがタイル、ルーム、
、またはナビメッシュ ポリゴンであっても、アルゴリズムは同じです。`neighbors()` と `cost()` のみが変わります。

 A* は、`f = g + h` によって順序付けされた優先キュー (*フロンティア*) を保持します。ここで、`g` は開始からの既知のコスト
であり、`h` は目標までのヒューリスティック推定です。それは
最適です **ただし** `h` は実際の残りのコストを決して過大評価しません (
 *許容*)。 `h = 0` では、A* はダイクストラのアルゴリズムに縮退します。

 ## 完全な A* (エンジン中立の Python)

```python
import heapq

def a_star(graph, start, goal):
    # Priority queue of (f_score, tie, node). heapq pops the SMALLEST first.
    frontier = [(0, 0, start)]
    came_from = {start: None}      # node -> node we reached it from
    cost_so_far = {start: 0.0}     # node -> best known g cost from start
    counter = 0                    # stable tie-breaker so heapq never compares nodes

    while frontier:
        _, _, current = heapq.heappop(frontier)
        if current == goal:
            break                  # early exit: we popped the goal, path is optimal

        for nxt in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, nxt)
            # Relax: accept this edge only if it improves the best known cost.
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + heuristic(nxt, goal)   # f = g + h
                counter += 1
                heapq.heappush(frontier, (priority, counter, nxt))
                came_from[nxt] = current

    return came_from, cost_so_far

def reconstruct_path(came_from, start, goal):
    if goal not in came_from:
        return None                # unreachable
    path = []
    node = goal
    while node != start:
        path.append(node)
        node = came_from[node]
    path.append(start)
    path.reverse()                 # came_from points backward; flip to start->goal
    return path
```

正確性の主なポイント:

 - **プッシュ時ではなく、*ポップ*するときにゴールを確認してください。** プッシュ時のテストは、エッジのコストが変化するとすぐに
として中断されます。ポップに対するテストは常に正しいです。
- **リラクゼーション** (`new_cost < cost_so_far[nxt]`) により、後で
より安価なルートが見つかった場合にノードを改善できます。不均一な移動コストでは不可欠です。
- **タイブレーカー**: ヒープ
がノード オブジェクト自体によって 2 つの等しい `f` ノードを順序付ける必要がないように、ノードの横に単調カウンターをプッシュします。

 ## 動作タイプ別のヒューリスティック

 |許可される動き |ヒューリスティック |式 (`dx=|ax-bx|`、`dy=|ay-by|`) |
|---|---|---|
| 4方向グリッド |マンハッタン | `dx + dy` |
| 8方向グリッド |オクタイル | `(dx + dy) + (sqrt(2) - 2) * min(dx, dy)` |
|任意角度 / ユークリッド空間 |ユークリッド | `sqrt(dx*dx + dy*dy)` |

 ヒューリスティックを最小ステップ コストでスケールし、
 `g` と同じ単位に留まります。 `h` が真のコストを超える可能性がある場合、A* は高速ですが、最適ではないパス
を返します (これは「重み付き A*」のトレードオフです。偶然ではなく意図的に使用してください)。

 ## グリッド グラフ アダプター

```python
class GridGraph:
    def __init__(self, walls, width, height):
        self.walls, self.w, self.h = walls, width, height
    def in_bounds(self, p): return 0 <= p[0] < self.w and 0 <= p[1] < self.h
    def passable(self, p):  return p not in self.walls
    def neighbors(self, p):
        x, y = p
        candidates = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]   # add diagonals for octile
        return [c for c in candidates if self.in_bounds(c) and self.passable(c)]
    def cost(self, a, b):
        return 1.0                  # uniform; return terrain weight for varied cost
```

## 代わりにエンジン ナビメッシュを使用する場合

 手巻きグリッド A* は、2D タイル ゲームや
アルゴリズムを理解するのに最適です。 3D ワールド、任意のジオメトリ、動的な障害物回避、および
エージェントの半径/高さの場合は、エンジンのベイクされたナビゲーションを優先します:

 - **Unity** — NavMesh をベイクし、`NavMeshAgent` を駆動します (`unity-navmesh` を参照)。
- **Unreal** — ナビゲーション メッシュ境界 + `AIController` MoveTo (`unreal-behavior-trees` を参照)。
- **Godot** — `NavigationRegion2D/3D` + `NavigationAgent2D/3D`、パスについて
`NavigationServer` をクエリします。

 これらは、
 が再実装するパス スムージング、オフメッシュ リンク、および混雑回避を処理します。ワールドが離散グリッド/グラフである場合は A* を直接使用し、コスト関数を完全に制御する必要がある場合は
を使用します。

 ## パフォーマンスに関するメモ

 - 検索を最適化する前にグラフを縮小します。開いた領域をマージし、密なグリッドの代わりにウェイポイント
グラフを使用するか、接続された領域を事前計算します。
- フ​​レームごとのパスファインディング作業に上限を設け (N 個の検索の予算)、残りをキューに入れます。
- 同じゴールに向かう多数のエージェントに対して、1 つの **フロー フィールド** (ゴールから外側への
ダイクストラ パス) を計算し、エージェントごとに A* を実行する代わりに、すべてのエージェントが勾配
に従うようにします。 
