---
name: rpg
description: >
  Build an RPG: stats and leveling, inventory and equipment, quests, branching dialogue, save/load,
  and combat. Use for an RPG/JRPG, or designing stat, inventory, quest, or combat systems.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # RPG

 ロールプレイング ゲームのプレイブック — ステータスと進行状況、在庫/装備、クエスト、
 ダイアログ、戦闘。これは**構成**スキルです。データ駆動型コンテンツ、
ダイアログ、および保存を結び付けます。それらの初歩的なことを再教育するものではありません。それは、成長と選択を有意義に感じさせるシステム
を定義し、それぞれを実装するスキルを指します。

 ##

 を使用する場合 - RPG/JRPG/アクション RPG を構築するときに使用します。プレイヤーには **成長するステータス**、
 **インベントリ**、**クエスト**、**対話**、および永続的な進行状況があります。
- レベリング カーブ、ダメージ計算式、インベントリ/装備モデル、または
クエスト ステート マシンを設計するときに使用します。

 **使用しない場合:** パーマデス ダンジョンは永続キャラクターなしで実行されます → `roguelike`。
純粋な会話・分岐ストーリー→`visual-novel`。オープンワールドのニーズ/クラフト/拠点構築 →
`survival-crafting`。対話エンジン自体には、`dialogue-systems` を使用します。

 ## コアループ

 **探索 → 遭遇 (戦闘 / 会話 / 解決) → 報酬の獲得 (XP、戦利品、ストーリー) →
の成長 (レベルアップ、ギアアップ、ロック解除) → より難しいコンテンツに挑戦します。** ファンタジーは * より強力になり、
 があなたのキャラクターを形作ります*。すべてのシステムは、成長と選択のループを養う必要があります。

 ## 必須システム

 1. **統計 + レベリング** — 基本属性、派生戦闘統計、XP カーブ、レベルアップゲイン。
2. **インベントリ + 装備** — データ定義のアイテム、スタッキング、スロット、ステータス修飾子。
3. **戦闘** — ターンベースまたはアクション。ダメージ計算式、ステータス効果、勝敗。
4. **クエスト** — 目標、ステート マシン (利用可能→アクティブ→完了→提出)、報酬。
5. **ダイアログ** — 分岐ライン、ゲーム状態の条件、重要な選択。
6. **保存/ロード** — キャラクター、インベントリ、クエストの進行状況、世界の国旗をバージョン管理とともに保持します。
7. **経済 + 進行ゲート** — ゴールド/ショップ。レベル/クエスト/地域のゲートパワー。
8. **UI** — HUD、インベントリ、クエストログ、ダイアログボックス、キャラクターシート。

 ## デザインノブ

 |ノブ |効果 |メモ |
|------|--------|----------|
| XP 曲線の形状 |パワーのペーシング |早い段階では速く、遅い段階では遅い（参考文献を参照）。 |
|統計→派生スケーリング |多様性を構築する | 1 つの属性が優勢であってはなりません。 |
|ダメージ計算式 |戦術的な感触 |減算的軽減と比率軽減 (参照)。 |
|ランダム分散 / クリティカル |スウィングネス | ±10% および ~1.5× クリティカルは安全なデフォルト値です。 |
|ドロップ率 / 経済性 |報酬ケイデンス |戦利品で店を矮小化しないようにしてください。 |
|パワーゲーティング |ゲートの難易度 |レベル/地域/クエストのロック。 |
|可逆修飾子 |バフ/ギアの正確さ |レイヤーMOD;基本統計は決して編集しないでください。 |
|選択の結果 |ロールプレイの重み |クエスト/ダイアログのフラグは結果を分岐させる必要があります。 |

 ## パターン

 ### 1. 基本属性から派生した統計 (再計算、真実として保存しない)

```python
# Pseudocode. Base attributes are the only "truth"; combat stats are derived each time.
def derive(base, mods):
    s = apply_modifiers(base, mods)          # base + flat adds + percent, then clamp
    return {
        "max_hp":  20 + s["VIT"] * 8,
        "attack":  s["STR"] * 2,
        "defense": s["VIT"] + s["AGI"] * 0.5,
    }
# Equipping pushes a modifier; unequipping pops it. HP/attack recompute automatically.
```

### 2. XP カーブ + レベルアップ

```python
# Pseudocode. Quadratic curve: fast early levels, long late ones.
def xp_to_next(level, base=100): return base * level * level

def gain_xp(actor, amount):
    actor.xp += amount
    while actor.xp >= xp_to_next(actor.level):
        actor.xp -= xp_to_next(actor.level)
        actor.level += 1
        actor.base["STR"] += 2; actor.base["VIT"] += 2   # grant gains / skill points
        on_level_up(actor)                                # heal, unlock, notify
```

### 3. ゲーム イベントによるクエスト目標の更新

```python
# Pseudocode. Game events advance matching objectives; completion grants rewards.
def on_event(kind, data):
    for q in active_quests:
        for obj in q.objectives:
            if obj.event == kind and matches(obj, data) and not obj.done:
                obj.count += 1
                if obj.count >= obj.needed: obj.done = True
        if all(o.done for o in q.objectives):
            q.state = "complete"                # turn-in grants xp/gold/items
```

## 落とし穴 / 失敗モード

 - **バフ/ギアの基本ステータスの編集** → 保存/再ロード時に値がドリフトして破損します。
モディファイア レイヤを保持します。プッシュ/ポップします(パターン1)。
- **派生統計を真実として保存** → 統計変更後に非同期。ベースから再計算します。
- **暴走 XP/ダメージ数** → 上限のない指数曲線、または巨大な値での減算
式のいずれか。カーブと数式ファミリーを慎重に選択します (参照)。
- **コードとしてのコンテンツ** → すべてのアイテム/クエストがハードコーディングされています。アイテム、敵、クエストを
**データ** (`godot-resources` / `unity-scriptableobjects`) として定義します。
- **バージョン フィールドのない保存形式** → 更新時に古い保存が中断される。初日から `version` および
移行パスを追加します (`save-systems` を参照)。
- **結果のない選択** → すぐに再収束する対話の分岐は空虚に感じられます。
後のクエスト/世界の状態を実際に変更するフラグを設定します。
- **クエストの進行状況が保持されない** → リロードするとクエスト途中の状態が失われます。
完了だけではなく、クエストの状態を保存します。

 ## 構成 (これらのスキルから構築)

 - **ダイアログ:** `dialogue-systems` (糸紡ぎ / インク) — 分岐線、条件、変数。
- **永続性:** `save-systems` — キャラクター、インベントリ、クエスト フラグ、世界状態、バージョン管理。
- **コンテンツ データ:** `godot-resources` / `unity-scriptableobjects` — アセットとしてのアイテム、敵、クエスト、スキル。
- **戦闘 AI:** 敵の行動については `game-ai`。ターン順序については、`roguelike` のスケジューラのアイデアを再利用します。
- **UI:** `game-ui-ux` (HUD/メニュー レイアウト、解像度スケーリング、コントローラー/キーボード ナビゲーション用)。具体的なインベントリ、クエストログ、キャラクターシート、ダイアログボックスについては、`godot-ui-control`。
- **ワールド:** `level-design` とエンジンのタイルマップ/3D スキル (`godot-tilemap`、`godot-3d-essentials`)。

 ## 参考資料

 - ステータス/ダメージの計算式、レベリングカーブ、ターン対アクションの戦闘タイムライン、インベントリ/装備の
データ形状、クエスト状態モデルについては、`references/stats-combat-quests.md` を参照してください。 
