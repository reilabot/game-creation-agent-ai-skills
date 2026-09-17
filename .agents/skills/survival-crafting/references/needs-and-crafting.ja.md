# 生存ニーズ、クラフトツリー、建物 (深さ)

 `SKILL.md` の詳細。エンジン中立の疑似コード。数値は調整の開始点です。

 ## 1. ニーズ モデル

 各ニーズは、時間の経過とともに減衰し、
 しきい値で結果を引き起こす `[0, max]` の値です。プレイヤーが反応する時間を確保できるように、結果を**等級** (警告→消耗) に保ちます。
|
|必要 |からの衰退 |失敗の結果 | | によって復元されました
 |------|---------------|---------------------|-------------|
|飢え |時間、活動 | HP 0 での消耗 |食べ物を食べる |
|喉の渇き |時間 (空腹よりも速い) | HP 0 での消耗 |飲酒 |
|温度 |環境、湿気、時間帯 |寒すぎる/暑すぎるとHPが消耗する |火災、避難所、衣類 |
|スタミナ |スプリント/作業 | 0 ではスプリント/攻撃はできません |残り |
|健康 |故障、破損が必要 | 0時の死 |安全 + 栄養補給、回復アイテム |

```python
# Rates as fraction of max per real second (tune so a day cycle has meaningful pressure).
HUNGER_RATE = 0.6 / 60     # ~empty in ~100 s of neglect at this scale (illustrative)
THIRST_RATE = 1.0 / 60     # thirst should bite before hunger
```

デザイン ノート:
- 通常、喉の渇きは空腹よりも早く減ります。どちらも通常のプレイ中には対処できるはずであり、
 は無視された場合にのみ危険です。
- 衰退を活動 (全力疾走/寒さで空腹感が高まる) に結び付けて、緊急の圧力を高めます。
- ニーズがゼロになる前に、常に警告状態で HUD にニーズを表示します。

 ## 2. 技術ツリーの作成

 **技術ノード**の有向非巡回グラフとしてのモデル進行。レシピは、
 前提技術が研究/構築されるとロック解除されます。これにより、制作がフラットなリストではなく、長期的な目標に変わります。

```python
tech = {
    "basic_tools":   {"requires": [],               "unlocks": ["stone_axe", "stone_pick"]},
    "workbench":     {"requires": ["basic_tools"],  "unlocks": ["workbench_recipes"]},
    "metalworking":  {"requires": ["workbench"],     "unlocks": ["furnace", "iron_tools"]},
}
def can_unlock(node, owned): return all(r in owned for r in tech[node]["requires"])
```

テクノロジー (作業台 → 炉 → 鍛冶) の後ろにステーションとレシピをステーションの後ろに配置するため、
 プレイヤーは物理的にツリーを登っていきます。各層は、新しい
リソース層 (石→鉄→上級) へのアクセスを許可し、収集→クラフト→リーチのループを閉じる必要があります。

 ## 3. レシピ データとマルチステップ チェーン

```python
# Intermediate products make crafting feel like progression, not a vending machine.
recipes = {
    "plank":     {"inputs": {"log": 1},                 "output": ("plank", 2), "station": None},
    "nails":     {"inputs": {"iron_ingot": 1},          "output": ("nails", 4), "station": "forge"},
    "wall":      {"inputs": {"plank": 4, "nails": 2},   "output": ("wall", 1),  "station": "workbench"},
}
# Refining (log -> plank, ore -> ingot) before assembly (plank+nails -> wall) adds depth
# without more raw resource types.
```

## 4. 収集とリスポーン

 - ノードには HP/ツール層要件と **ドロップ テーブル** (重み付けされています。ローグライク戦利品
パターンを参照)。間違った/弱いツール = 歩留まりがないか、歩留まりが遅い。
- ワールドが永久に削除されないようにリスポーンします。タイマーベースの再成長、またはプレーヤーが離れているときのゾーンベースの
の再作成です。基地近くの不足により、探索が外側に押し出されます。
- ツール階層ゲート ノード タイプ (拳 → 木、石ピック → 石/鉱石、金属ピック → 硬い鉱石)、
 は、「より遠くへ探索」を「より良い収集のロックを解除」に変えるメインレバーです。

 ## 5. ベース構築

 - **グリッド/スナップ配置:** 構造をグリッドまたは既存のピースのソケットにスナップします。コミットする前に、
 の配置 (重複していないこと、有効な地面上、手の届く範囲内) を検証してください。
- **構造的健全性 (オプション):** サポート/安定性ルールにより深みが増しますが、複雑さが伴います。ファンタジーに役立つ場合にのみ、
 を追加します。
- **機能:** 基地は、脅威サイクルに対するストレージ (追加の在庫)、クラフト ステーション (テクノロジー ゲート)、および
防御 (壁/トラップ) を提供します。ストレージにより在庫の上限が緩和されるため、
 プレーヤーは大量に集めて戻ってきます。つまり、意図的な物流ループです。

```python
def place(structure, pos, world, inv):
    if not world.is_valid_placement(structure, pos): return notify("Can't build here")
    if not inv.has(structure.cost): return notify("Missing materials")
    inv.consume(structure.cost)
    world.add_structure(structure, pos)     # now functions as storage/station/defense
```

## 6. 脅威の拡大

 - **昼/夜:** 昼は収集、夜は防御 — 自然なリズム。脅威は夜に出現するか、
 が強化されます。
- **段階的エスカレーション:** 経過日数、到達した技術レベル、または
スポーンからの距離によって脅威が増加するため、世界はプレイヤーの力と歩調を合わせます。プレイヤーが基地を準備できるように、大きなイベント (「ブラッド ムーン」
 スタイルの襲撃) をテレグラフで送信します。
- 進行ラダーに対するバランスのエスカレーション: 新しい脅威は、
 プレイヤーがそれに対抗するツール/防御のロックを解除するとおおよそ到着するはずです。

 ## 7. 広大な世界を救う

 サバイバルセーブは大規模かつ頻繁に行われます。増分的に永続化し (チャンク/構造の変更)、移行用に
`version` を保持し、戦闘中の
ではなく安全なイベント (睡眠、日のロールオーバー) で自動保存します。スロット/バージョン管理の仕組みを `save-systems` に延期します。 
