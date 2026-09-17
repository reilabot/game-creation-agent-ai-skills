# RPG 統計、戦闘、クエスト (深さ)

 `SKILL.md` の背後にある数式とデータ形状。エンジン中立の疑似コード。すべての数値
を、法則ではなく、プレイテストに合わせて調整するための開始点として扱います。

 ## 1. 統計ブロック: 基本、派生、および修飾子

 **基本**属性を**派生**の戦闘統計から分離することで、単一の属性変更が予測どおりに波及するようにします。
独自のレイヤーに**修飾子**を保持するため、バフ/装備は
になります。基本値を損なうことなく元に戻すことができます。

```python
# Base attributes (what leveling/allocation changes)
base = { "STR": 10, "AGI": 10, "INT": 10, "VIT": 10 }

# Derived stats are pure functions of base (+ modifiers). Recompute; never store as truth.
def derive(base, mods):
    s = sum_layers(base, mods)                  # base + flat + percent modifiers
    return {
        "max_hp":  20 + s["VIT"] * 8,
        "attack":  s["STR"] * 2,
        "defense": s["VIT"] * 1 + s["AGI"] * 0.5,
        "crit":    min(0.05 + s["AGI"] * 0.005, 0.50),   # cap it
        "speed":   s["AGI"],
    }
```

モディファイアーレイヤー (この順序で適用): **ベース → フラット追加 → パーセント乗数 → クランプ**。
アイテムを装備するとモディファイアがプッシュされます。装備を解除すると同じものがポップします。これにより、
 の古典的な「バフが切れて間違った HP になった」というバグが回避されます。

 ## 2. ダメージ計算式

 2 つの一般的なファミリー — 1 つを選択し、一貫性を保ちます:

```python
# (a) Subtractive: defense flatly reduces damage. Simple; high defense can trivialize hits.
dmg = max(1, attacker.attack - defender.defense)        # floor at 1 so nothing is immune

# (b) Ratio/mitigation: defense gives diminishing % reduction. Scales smoothly to high numbers.
mitigation = defender.defense / (defender.defense + K)  # K ~ 100; tune the curve
dmg = attacker.attack * (1 - mitigation)

# Layer on: random variance (±10%), crit multiplier, and type effectiveness.
dmg *= rng.range(0.9, 1.1)
if is_crit: dmg *= 1.5
dmg *= type_multiplier(attacker.element, defender.element)   # 0.5 / 1.0 / 2.0
```

減算は、数値が低いと「戦術的」に感じられます。ゲーム終盤の値が大きいほど、比率はより適切にスケールされます。

 ## 3. 平準化曲線

 XP から次のレベルまでが全体のペースを形成します。 3 つの一般的な曲線:

```python
# Linear-ish (gentle):     next = base * level
# Quadratic (classic JRPG):next = base * level^2
# Exponential (steep):     next = base * growth^level     # growth ~1.2–1.5

def xp_to_next(level, base=100, kind="quadratic", growth=1.3):
    if kind == "linear":      return base * level
    if kind == "quadratic":   return base * level * level
    if kind == "exponential": return int(base * (growth ** level))
```

ガイダンス: 初期のレベルを速く保ち (数分で報酬)、後のレベルを伸ばします。ステータスはレベルアップ時に
および/またはスキル ポイントを獲得します。次のロック解除を電報で伝えて、プレイヤーを前に引っ張ります。

 ## 4. ターンベースとアクションの戦闘タイムライン

 | |ターン制 |アクション |
|---|---|---|
|時間 |離散;選択するには一時停止してください |リアルタイム;反射神経が重要 |
|イニシアチブ |速度統計 / ATB ゲージ指示ターン |クールダウン/攻撃タイミング |
|強さ |奥深い戦略、アクセス可能 |直感的で表現力豊かなスキル |
| | で構築するターン スケジューラ (`roguelike` パターン 2 を参照) |エンジンの動き・物理スキル |

 ATB (「アクティブ タイム バトル」) はハイブリッドです。ゲージは `speed` によって満たされます。いっぱいになると、俳優は演技することができます。

 ## 5. インベントリおよび機器データ

```python
# Items are data, not code. Define them as resources/assets (see godot-resources /
# unity-scriptableobjects) and reference by id.
item = {
    "id": "iron_sword", "name": "Iron Sword", "slot": "weapon",
    "stackable": False, "max_stack": 1,
    "modifiers": [ {"stat": "STR", "type": "flat", "value": 3} ],
    "value": 50,
}
# Inventory = list of (item_id, count). Equipment = slot -> item_id.
# Equipping applies the item's modifiers (push); unequipping removes them (pop).
```

## 6. クエスト状態モデル

```python
# A quest is a small state machine with objectives. Persist its state in the save.
quest = {
    "id": "missing_cat", "state": "available",   # available -> active -> complete -> turned_in
    "objectives": [ {"id": "find_cat", "done": False, "count": 0, "needed": 1} ],
    "rewards": { "xp": 150, "gold": 30, "items": ["iron_sword"] },
}
# Game events (kill, pickup, talk) update matching objectives; when all done, state=complete.
# Dialogue conditions read quest state; turning in grants rewards and advances dependent quests.
```

クエストの*定義*をデータとして保存し、クエストの*進行状況*を保存します。 `dialogue-systems` 条件/変数を介したクエスト状態でのダイアログ ラインと
NPC の動作をゲートします。 
