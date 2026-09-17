# pygame スプライト、コリジョン、メディア (pygame-ce 2.5+)

 pygame-core スキルの奥深さ: グループ バリアント、ピクセルパーフェクトコリジョン、
 スプライトシート、アニメーション、オーディオ/テキスト。

 ## グループ バリアント

 `pygame.sprite` は複数のコンテナを出荷します。必要に応じて選択:

 |クラス | | に使用します。
|------|-----------|
| `Group` |一般的な場合。 `update(*args)` + `draw(surface)` |
| `GroupSingle` |最大 1 つのスプライトを保持するスロット (例: プレーヤー) |
| `LayeredUpdates` |スプライトごとに描画するグループ `_layer` (z オーダー) |
| `RenderUpdates` |部分的な画面再描画のためにダーティな四角形を追跡します。

```python
from pygame.sprite import LayeredUpdates
world = LayeredUpdates()
world.add(background, layer=0)
world.add(player, layer=10)        # higher layer draws on top
world.add(ui, layer=20)
world.update(dt)
world.draw(screen)
```

スプライトは、`self.kill()` を使用して **すべて** グループから自身を削除します。メンバーシップは
双方向です: `group.has(sprite)`、`sprite.groups()`。

 ## 衝突関数

 `spritecollide` および `groupcollide` は、デフォルトで四角形のオーバーラップを使用します。オプションの
`collided` コールバックは、より正確なテストでスワップします:

```python
import pygame
from pygame.sprite import collide_rect, collide_circle, collide_mask

# Circle collision (set sprite.radius, or it's derived from the rect):
pygame.sprite.spritecollide(player, rocks, False, collide_circle)

# Pixel-perfect via masks (see below):
pygame.sprite.spritecollide(player, spikes, False, collide_mask)
```

その他のヘルパー: `pygame.sprite.collide_rect_ratio(0.75)` (縮小四角形)、
 `spritecollideany` (高速ブールっぽい「任意のヒット」)、および `Rect` メソッド
`colliderect`、`collidepoint`、`collidelist`、 `collidelistall`。

 ## マスクとのピクセルパーフェクト衝突

 四角形衝突は寛大です。タイトなヒットボックスの場合、各スプライトの
アルファから `Mask` を構築し、重複をテストします:

```python
class Bullet(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.image = image.convert_alpha()
        self.rect = self.image.get_rect(center=pos)
        self.mask = pygame.mask.from_surface(self.image)  # build once

# collide_mask uses each sprite's .mask:
if pygame.sprite.collide_mask(bullet, enemy):
    enemy.kill()
```

スプライトの画像が変更された場合 (アニメーション フレームごとなど) にマスクを再構築するか、
 フレームごとのマスクのリストを保持します。

 ## スプライトシートのスライス

```python
def load_frames(path, frame_w, frame_h):
    sheet = pygame.image.load(path).convert_alpha()
    cols = sheet.get_width() // frame_w
    rows = sheet.get_height() // frame_h
    frames = []
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * frame_w, r * frame_h, frame_w, frame_h)
            frames.append(sheet.subsurface(rect))   # view into the sheet, no copy
    return frames
```

## シンプルなフレームアニメーション

```python
class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, frames, fps, pos):
        super().__init__()
        self.frames = frames
        self.frame_time = 1 / fps
        self.timer = 0.0
        self.index = 0
        self.image = frames[0]
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        self.timer += dt
        while self.timer >= self.frame_time:
            self.timer -= self.frame_time
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]
```

## オーディオ

```python
pygame.mixer.init()                       # or rely on pygame.init()
jump_sfx = pygame.mixer.Sound("jump.wav") # short SFX, fully loaded
jump_sfx.set_volume(0.5)
jump_sfx.play()

pygame.mixer.music.load("theme.ogg")      # streamed music (one track at a time)
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(loops=-1)         # -1 = loop forever
```

`.ogg`/`.wav` を優先します。多くの短いエフェクトは `Sound` として保持し、長いトラックは
単一の `music` ストリームに保持します。

 ## テキスト

```python
font = pygame.font.Font(None, 36)         # None = default font; or a .ttf path
# Antialiased text is slow to render — cache the Surface, re-render only on change.
label = font.render(f"Score: {score}", True, (255, 255, 255))
screen.blit(label, (10, 10))
```

フレームごとにテキストを再レンダリングすることは、一般的なパフォーマンスの罠です。一度レンダリングして再ブリットします。
 は文字列が変更された場合にのみ再レンダリングします。 
