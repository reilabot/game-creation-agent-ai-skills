---
name: survival-crafting
description: >
  Build a survival-crafting game: resource gathering, inventory, crafting and a tech tree,
  needs (hunger/thirst/temperature), and base building. Use for a survival or crafting/base-building game.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # サバイバル クラフト

 サバイバル クラフト ゲームのプレイブック — 収集 → クラフト → 構築のループ、サバイバルのニーズ、
 のクラフト/技術の進歩、および基地の構築。これは **構成** スキルです。
 インベントリ データ、世界のコンテンツ、永続性、脅威を調整します。それらの初歩的なことを再教育するものではありません。
それは、生存を退屈ではなく緊張させるループと圧力システム (ニーズ、不足、エスカレーション) を定義します。

 ##

 を使用する場合 - プレイヤーが**リソースを収集し、アイテム/構造物を作成し、生存ニーズを管理し、
 がエスカレートする脅威に対する基地を構築**する場合に使用します: サバイバル サンドボックス、クラフト/基地構築ゲーム。
- ニーズ (空腹/喉の渇き/気温)、ク​​ラフト技術ツリー、収集ループ、
、または基地の配置/構築を設計するときに使用します。

 **使用しない場合:** RPG のマイナー機能としてのクラフト → `rpg`。パーマデスグリッドダンジョン→
 `roguelike`。データ資産としての在庫/アイテムの場合は、`godot-resources` /
`unity-scriptableobjects` を使用します。ワールド世代の場合は、`procedural-gen`。

 ## コア ループ

 **原材料の収集 → ツール/アイテムの作成 → 基地の構築とアップグレード → 生存ニーズの管理
→ より良いリソースを求めてさらに探索 → エスカレートする脅威から生き残る → より高いレベルで繰り返します。**
各ループは *次の * ループのロックを解除する必要があります (より良いツール → 新しいものに到達)バイオーム → 新しいリソース →
より良い工芸品)。そのはしごが壊れると、ゲームは大変なことになります。

 ## 必須システム

 1. **リソース ノード + 収集** — 収集可能なワールド オブジェクト。ツールの要件/階層。復活する。
2. **インベントリ** — スタック、容量 (スロットまたは重量)、ドロップ/転送、ホットバー。
3. **クラフト** — レシピ (入力→出力)、クラフト ステーション/テクノロジー ゲート、テクノロジー ツリー。
4. **生存ニーズ** — 飢え、渇き、気温、スタミナ、健康、そして衰退とその結果。
5. **ベースビルディング** — 配置可能な構造物、ビルドグリッド/スナップ、ストレージ、クラフトステーション。
6. **世界 + 昼/夜** — バイオーム/リソース (多くの場合手続き型)。脅威を引き起こすタイムサイクル。
7. **脅威** — エスカレートする敵対的な生き物/天候/出来事。戦闘か回避か。
8. **保存/ロード** — 世界の状態、在庫、基地、ニーズ、進行状況。広い世界の永続性。

 ## デザインノブ

 |ノブ |効果 |メモ |
|------|--------|----------|
|減衰率が必要 |圧力ケイデンス |探索するには十分に遅くても、重要になるには十分に高速です。 |
|必要性と失敗の結果 |賭け金 |即死ではなく時間経過によるダメージ。 |
|資源不足/リスポーン |探査プッシュ |基地付近が不足している→さらに移動してください。 |
|ツール階層/ゲート |進行ラダー |より良いツール→新しいノードタイプ。 |
|レシピの複雑さ / 技術の深さ |長期的な目標 |フラットリストではなく、複数ステップのチェーン。 |
|インベントリ制限 (スロット/重量) |物流の緊張 |ベーストリップとストレージを強制します。 |
|脅威拡大曲線 |時間の経過による困難 |夜間/季節/イベントランプ。 |
|日の長さ |リズム |昼＝集まる、夜＝守る。 |

 ## パターン

 ### 1. 段階的な結果によるニーズの減衰

```python
# Pseudocode in the per-frame/per-tick update. dt = seconds. Needs fall; failure bleeds HP.
def update_needs(p, dt):
    p.hunger = max(0, p.hunger - HUNGER_RATE * dt)
    p.thirst = max(0, p.thirst - THIRST_RATE * dt)
    p.temp   = approach(p.temp, ambient_temperature(p), TEMP_RATE * dt)

    # Consequences are graded, not binary: warnings, then attrition — never instant death.
    if p.hunger == 0 or p.thirst == 0:
        p.hp -= STARVE_DAMAGE * dt          # damage over time creates urgency with recovery room
    if p.temp < COLD_THRESHOLD or p.temp > HEAT_THRESHOLD:
        p.hp -= EXPOSURE_DAMAGE * dt
    if p.hunger > 0 and p.thirst > 0 and not exposed(p):
        p.hp = min(p.max_hp, p.hp + REGEN_RATE * dt)   # safe + fed => heal
```

### 2. 作成: 入力を検証し、アトミックに消費する

```python
# Pseudocode. Recipes are data: inputs -> output, with an optional station/tech requirement.
recipe = {"id": "stone_axe",
          "inputs": {"wood": 3, "stone": 2}, "output": ("stone_axe", 1),
          "station": "workbench", "requires_tech": "basic_tools"}

def can_craft(recipe, inv, tech, station):
    if recipe.get("requires_tech") and recipe["requires_tech"] not in tech: return False
    if recipe.get("station") and recipe["station"] != station: return False
    return all(inv.count(item) >= n for item, n in recipe["inputs"].items())

def craft(recipe, inv, tech, station):
    if not can_craft(recipe, inv, tech, station): return False
    for item, n in recipe["inputs"].items(): inv.remove(item, n)   # consume all, then add
    inv.add(*recipe["output"])                                     # atomic: no partial craft
    return True
```

### 3. ツール層ごとにゲートされた収集

```python
# Pseudocode. A node yields only if the held tool meets its required tier.
def harvest(node, tool):
    if tool.tier < node.required_tier:
        return notify("Need a better tool")        # e.g. stone node needs a pickaxe, not fists
    node.hp -= tool.power
    if node.hp <= 0:
        spawn_drops(node.drop_table)               # weighted drops (see roguelike loot pattern)
        node.start_respawn(node.respawn_time)      # node returns later; world isn't depleted forever
```

## 落とし穴 / 失敗モード

 - **即死のニーズ** → フラストレーションと保存嫌い。時間の経過とともに障害によるダメージを与え、明確な警告と回復パスを備えた
(パターン 1)。
- **はしごを使わずにグラインド** → 新しいギャザリングのロックが解除されないギャザリング。各層は次の
を開く必要があります (より良いツール → 新しいノード → 新しいリソース → より良いクラフト)。
- **非アトミック クラフト** → 入力は消費されますが、エッジ ケースでは出力が許可されません。最初に
を検証し、次に 1 つのステップとして消費して追加します (パターン 2)。
- **制限のない在庫** → 物流上の緊張がなく、拠点や保管場所を設ける理由もありません。
スロットまたは重量によって制限されます。
- **世界を永久に枯渇させる** → プレイヤーはマップを剥ぎ取って終了します。ノードを再生成するか、
 は時間の経過とともにリソースを再生成します。
- **`dt` によってスケーリングされていないフレームごとの減衰** → 異なるハードウェアでは異なる速度でドレインする必要があります。
`dt` でスケールします。
- **大きな世界を保存できない / 脆弱な保存** → クラッシュにより数時間のデータが消去されます。ワールド + ベース + ニーズ
を段階的に永続化します。バージョンを変更します (`save-systems` を参照)。
- **フラットな脅威カーブ** → ゲーム終盤のプレッシャーなし。夜間/季節/イベントの段階に応じてエスカレーションします。

 ## 構成 (これらのスキルから構築)

 - **データとしてのアイテム/レシピ:** `godot-resources` / `unity-scriptableobjects` — アイテム、レシピ、技術ツリー、ドロップ テーブル。
- **ワールド:** バイオーム/リソース配置用の `procedural-gen`。作成された領域の場合は `level-design`。
- **永続性:** 大規模な世界の状態、ベース、インベントリ、ニーズ、およびバージョン管理用の `save-systems`。
- **脅威:** クリーチャーの場合は `game-ai`。近接/衝突用のエンジン物理スキル。
- **建物/配置:** `godot-tilemap` / `unity-tilemap-2d` (2D) または `godot-3d-essentials` (3D) と UI スナップ。
- **UI:** インベントリ/クラフト/HUD レイアウトおよびスケーリング用の `game-ui-ux`。 `godot-ui-control` は、具体的なインベントリ、クラフト メニュー、HUD の必要性、ビルド モード用です。

 ## 参考資料

 - 完全なニーズ モデルとしきい値、クラフト テクノロジー ツリー グラフ、収集/リスポーン調整、
 ベース構築グリッド、および脅威エスカレーションについては、`references/needs-and-crafting.md` を参照してください。 
