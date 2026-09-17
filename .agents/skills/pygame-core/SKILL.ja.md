---
name: pygame-core
description: >
  Structure a pygame (pygame-ce) game in Python: the init/event/update/draw loop,
  delta-time movement, Surface/Rect blitting, keyboard/mouse input, and
  Sprite/Group management with collision. Use when building or debugging a pygame
  game — when the user mentions pygame, pygame-ce, the game loop, blit, Surface,
  Rect, sprite groups, or clock.tick. Targets pygame-ce.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # pygame Core

 Python で pygame ゲームの基礎を構築します: メイン ループ、デルタタイム
の動き、`Surface`/`Rect` による描画、入力、および `Sprite`/`Group` 管理。
**pygame-ce 2.5.7** (アクティブに維持されているコミュニティ フォーク、同じ
`import pygame`) をターゲットとしています。

 ##

 を使用する場合 - pygame ゲームの開始、ループの修正、フレーム レート依存の速度、
 入力処理、ブリッティング、またはスプライト/グループの衝突の場合に使用します。
- コードが `import pygame` を実行し、プロジェクトが `pygame-ce`
(または `pygame`) に依存する場合に使用します。

 **使用すべきではない場合:** pygame に関係のない Python 言語の質問。 3D レンダリング
(pygame は 2D)。クロスエンジンの保存/ロードの場合は、`save-systems` を使用します。再バインド可能な入力
アーキテクチャについては、`input-systems` を参照してください。

 ## コア ワークフロー

 1. **従来の pygame ではなく、pygame-ce をインストールします。** `pip install pygame-ce` — これは、
 で維持されるフォークであり、`pygame` としてインポートされます。 1 つの環境に両方をインストールしないでください。
2. **初期化してウィンドウを開きます。** `pygame.init()`、`screen =
pygame.display.set_mode((w, h))`, `クロック = pygame.time.Clock()`。
3. **1 つのループを実行します: イベント → 更新 → 描画 → 反転。**
フレーム (`for event in pygame.event.get()`) ごとにイベント キューをポンプし、状態を更新し、再描画してから、
 `pygame.display.flip()` を実行します。
4. **フレームレートに依存しないようにします。** `dt = clock.tick(60) / 1000` (秒)
を取得し、`dt` によってすべてのモーションをスケールします。ポジションを浮動小数点として保持します。整数四角形でのブリット。
5. **2 つの方法で入力を処理します:** イベント ベース (`KEYDOWN`/`MOUSEBUTTONDOWN`、個別の
アクションの場合) とポーリング (`pygame.key.get_pressed()`、保留された移動の場合)。
6. **`Sprite` + `Group` を使用してオブジェクトを整理します。** `pygame.sprite.Sprite`
を `image`/`rect` でサブクラス化します。 `group.update(dt)` および `group.draw(screen)` は、
 バッチを処理します。動作していると判断する前に、それを実行してウィンドウを確認してください。

 ## パターン

 ### 1. 最小限のゲーム ループ (スケルトン)

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("My Game")
clock = pygame.time.Clock()

running = True
while running:
    dt = clock.tick(60) / 1000          # cap at 60 FPS; dt = seconds since last frame
    for event in pygame.event.get():    # MUST drain the queue or the OS thinks it hung
        if event.type == pygame.QUIT:
            running = False

    # update game state here, scaled by dt ...

    screen.fill((18, 18, 28))           # clear each frame
    # draw everything here ...
    pygame.display.flip()               # present the frame

pygame.quit()
```

### 2. デルタ時間移動 (フレームレートに依存しない)

```python
from pygame.math import Vector2

pos = Vector2(100, 100)        # keep position as floats
speed = 220                    # PIXELS PER SECOND, not per frame

# inside the loop, after computing dt:
keys = pygame.key.get_pressed()
direction = Vector2(
    keys[pygame.K_RIGHT] - keys[pygame.K_LEFT],
    keys[pygame.K_DOWN]  - keys[pygame.K_UP],
)
if direction.length_squared() > 0:
    direction = direction.normalize()      # equal speed on diagonals
pos += direction * speed * dt              # RIGHT: dt-scaled
screen.blit(player_img, (round(pos.x), round(pos.y)))  # blit at integer pixels
```

### 3. 入力: イベントとポーリング

```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False
    elif event.type == pygame.KEYDOWN:        # discrete press: jump, menu, pause
        if event.key == pygame.K_SPACE:
            jump()
        elif event.key == pygame.K_ESCAPE:
            running = False
    elif event.type == pygame.MOUSEBUTTONDOWN:
        shoot_at(event.pos)                   # event.pos = (x, y)

# Polled state (read once per frame) for continuous/held input:
keys = pygame.key.get_pressed()
if keys[pygame.K_a]:
    move_left(dt)
```

### 4. スプライト サブクラス + グループ

```python
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # convert() once at load makes blits much faster; _alpha keeps transparency.
        self.image = pygame.image.load("player.png").convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = 240

    def update(self, dt):                      # Group.update(dt) calls this per sprite
        keys = pygame.key.get_pressed()
        self.pos.x += (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed * dt
        self.rect.center = (round(self.pos.x), round(self.pos.y))

all_sprites = pygame.sprite.Group()
all_sprites.add(Player(400, 300))

# in the loop:
all_sprites.update(dt)        # calls each sprite's update(dt)
all_sprites.draw(screen)      # blits each sprite at its rect
```

### 5. 衝突検出

```python
# Sprite vs group: e.g. player picking up coins (True = remove collided coins).
collected = pygame.sprite.spritecollide(player, coins, dokill=True)
score += len(collected)

# Group vs group: bullets vs enemies (kill both on hit).
hits = pygame.sprite.groupcollide(bullets, enemies, True, True)

# Plain rect overlap (no sprites needed):
if player.rect.colliderect(door_rect):
    open_door()
```

## 落とし穴

 - **ウィンドウがフリーズする/「応答なし」** → イベント キューをポンプしませんでした。フレームごとに
`pygame.event.get()` (または `pygame.event.pump()`) を呼び出します。
- **高速なマシンでは速度が異なります** → フレームごとに固定量だけ移動しました。
`dt = clock.tick(fps) / 1000` でスケールし、1 秒あたりのピクセル数の値を使用します。
- **サブピクセル移動スナップ/ジッター** → `rect` 座標は整数です。
の真の位置を float の `Vector2` として保存し、各
フレームに `rect.center = round(...)` を割り当てます。
- **ブリットが遅い / フレームレートが低下する** → 読み込まれた画像に対して `.convert()` (不透明) または
`.convert_alpha()` (透明) を 1 回呼び出します。変換されていないサーフェスは、
 のブリット速度がはるかに遅くなります。
- **何も表示されません** → `pygame.display.flip()` (または `update()`) を忘れたか、`screen.fill(...)` の前に
を引いたためクリアされました。
- **描画順序が間違っています** → pygame はペインターの順序を使用します。後のブリットが以前のブリットをカバーします。
最初に背景を描画し、最後にスプライトを描画します。
- **`pip install pygame` は古いものを取得しました** → メンテナンスされたフォークには、
 `pip install pygame-ce` を使用します。両方をインストールするとインポートの競合が発生します。
- **対角線の移動が高速化** →
の速度でスケーリングする前に方向ベクトルを正規化します。

 ## 参照

 - `Group` バリアント (z オーダーの `GroupSingle`、`LayeredUpdates`)、`mask` とのピクセルパーフェクト
衝突、スプライトシートのスライス、単純なアニメーション、サウンド/音楽、および
テキスト レンダリングについては、`references/sprites-and-collision.md` を読み取ります。

 ## 関連スキル

 - `love2d-core` — LÖVE/Lua と同じループ概念。
- `bevy-ecs` — プロジェクトが pygame を超えた場合のより重い ECS エンジン。
- `input-systems` / `save-systems` — エンジンに依存しない入力と永続性。
- `platformer` / `roguelike` — pygame と組み合わせるジャンル テンプレート。 
