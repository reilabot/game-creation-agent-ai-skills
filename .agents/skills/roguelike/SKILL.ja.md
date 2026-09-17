---
name: roguelike
description: >
  Build a roguelike: turn-based grid movement, procedural dungeons, permadeath, field-of-view,
  and loot tables. Use for a roguelike/roguelite or turn-based grid dungeon crawler with procedural levels.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # ローグライク

 ローグライクのプレイブック — ターン エンジン、プロシージャル ダンジョン、フィールド オブ ビュー、パーマデス、
、ラン エコノミー。これは **構成** スキルです。手続き型生成、
 タイルマップ、保存処理、および AI を調整して実行ベースのゲームに組み込みます。ノイズ/RNG または
タイルマップ API を再教育するものではありません。それは、「実行」を魅力的にするループとシステムを定義します。

 ##

 を使用する場合 - **ターンベース、グリッドベース**のダンジョン クローラーを構築する場合に使用します。このダンジョン クローラーでは、死亡するたびに
の実行が終了し、世界が再生されます。ローグライクまたは「ローグライト」 (メタ プログレッションあり)。
- 手続き型ダンジョン、FOV/戦場の霧、パーマデス ステークス、戦利品テーブルを設計するときに使用します。

 **使用しない*場合:** ローグライク *ドレッシング* によるリアルタイム アクション → アクション ジャンル
(`platformer`/`fps-shooter`) を構築し、`procedural-gen` をレイヤー化します。 
パーマデス→`rpg`なしの詳細な統計/クエスト/ダイアログ。オープンワールドのニーズ/クラフト → `survival-crafting`。

 ## ローグライクの理由 (デザイン アンカー)

 コミュニティの参照は、**ベルリン解釈** (RogueBasin、IRDC 2008) です。チェックリストではなく、一連の
「ローグライク性」要素です。価値の高いものは設計ターゲットです:
**ランダム環境生成、パーマデス、ターンベース、グリッドベース、非モーダル** (1 つのモードですべてのアクション 
)、**複雑さ** (多くのアイテム/モンスターの相互作用)、**リソース管理**、
 **ハックアンドスラッシュ**、**探索と発見**。これらに身を乗り出して、ローグライクな気分を味わいましょう。意図的に保持する
を選択します。 「ローグライト」は通常、メタ進行でパーマデスを緩和します。

 ## コアループ

 **ターンを取る (移動 / 戦闘 / 使用) → 世界がターンを解決 → 新しい状態を見る → 降下 /
略奪 / 生き残る → 死んで新しいダンジョンで再開。** リプレイ性は、プレイヤーが固定レイアウトを記憶するのではなく、実行ごとに変更される *ワールド*
によってもたらされます。

 ## 必須のシステム

 1. **スケジューラーを回す** — エネルギー/イニシアチブ システムなので、素早いアクターがより頻繁に行動します (パターン 2)。
2. **グリッド マップ + 移動** — タイル座標。衝突から攻撃。ブロックされた/ウォーク可能なクエリ。
3. **手続き型ダンジョン ジェネレーター** — 部屋 + 廊下、または BSP/携帯電話。接続を保証します。
4. **視野 + 探索された記憶** — 今見えているものと前に見えていたもの (パターン 3 / 参照)。
5. **戦闘 + エンティティ** — HP、攻撃/防御、ステータス。モンスターはプレイヤーと同じルールに従います。
6. **戦利品 + ドロップ テーブル** — 重み付けされ、深度スケールされたアイテム/モンスターのスポーン (参照)。
7. **パーマデス + (オプション) メタプログレッション** — ランをワイプします。永続化はロック解除/スコアのみを保持します。
8. **メッセージ ログ + 明確な UI** — プレイヤーはテキスト/状態から理由を判断します。表面の数字と出来事。

 ## デザインノブ

 |ノブ |効果 |メモ |
|------|--------|----------|
|ダンジョンの広さ・部屋数 |ランレングス、密度 |奥行きのあるスケール。 |
|接続性の保証 |到達できない部屋はありません |生成後は必ず到達可能性を検証してください。 |
|モンスター密度/深度曲線 |難易度ランプ |深さ重み付けテーブルによってスポーンします。 |
|戦利品のレアリティの重み |電力分散 |レア = スイングが大きい。識別することで発見が追加されます。 |
| FOV 半径 / 照明 |緊張、情報 |半径が小さい = より怖く、より遅くなります。 |
|資源不足 (食料/HP/弾薬) |下降への圧力 |クラシック RL のコア テンション レバー。 |
|パーマデス vs メタプログレッション |ランステークスとリテンション |ローグライトは壁を柔らかくします。 |
|識別/不明 |探索値 |未確認アイテムは実験の報酬となります。 |
|シード可能な RNG |毎日の実行、デバッグ |常に固定シードを許可します (`procedural-gen` を参照)。 |

 ## パターン

 ### 1. 決定的でシード可能な実行 RNG

```python
# Pseudocode. One seeded RNG per run makes dungeons reproducible (daily runs, bug repro).
run_seed = chosen_seed or random_seed()
rng = Rng(run_seed)                 # use your engine's seedable RNG, not global random
dungeon = generate_dungeon(rng, depth)   # same seed + depth => same dungeon
# Persist run_seed in the save so a crash can resume the same world (see save-systems).
```

### 2. エネルギーベースのターン スケジューラ (速度は異なります)

```python
# Pseudocode. Each actor gains energy each tick and acts when it has enough.
# Faster actors gain more per tick, so they act more often — no fixed "player then enemies".
TURN_COST = 100
def next_actor(actors):
    while True:
        for a in actors:                 # stable order avoids ties favoring one side
            a.energy += a.speed          # e.g. speed 100 = normal, 150 = hasted
            if a.energy >= TURN_COST:
                a.energy -= TURN_COST
                return a                 # this actor takes exactly one action now
```

### 3. 視野 + 探索された記憶

```python
# Pseudocode. Recompute visibility from the player each time they move.
visible = compute_fov(map, player.pos, radius=8)   # symmetric shadowcasting (see refs)
for cell in visible:
    explored.add(cell)                  # remember it forever (dim "fog of war")
# Render: visible -> lit; explored-but-not-visible -> dim; never-seen -> hidden.
```

実績のある FOV アルゴリズム (再帰的シャドウキャストまたは対称シャドウキャスト) を使用します。
はセルごとの単純なレイキャストをロールしないでください。非対称の「点滅する」視覚が生成されます。参考文献を参照してください。

 ## 落とし穴/失敗モード

 - **切断されたダンジョン** → プレイヤーが到達できない部屋。常に接続/フラッドフィル
パスを実行し、すべての歩行可能なセルに到達できるまでコリドーを切り開きます。
- **単純な FOV** → ちらつく、または非対称な視覚 (あなたには彼らが見えますが、彼らにはあなたが見えません)。
シャドウキャストを使用します。対称性をテストします。
- **ターンベースを装ったリアルタイム ループ** → 入力レースとダブルムーブ。一度に 1 つの
個別ターンを解決します。キュー入力。
- **難易度フラット** → 降下プレッシャーなし。深さに応じてモンスターや戦利品をスケールし、リソースを不足させません。
- **メタアンロックを消去するパーマデス** → 欲求不満。保存時に *run* 状態 (ワイプ) を
*profile* 状態 (ロック解除、スコア) から分離します (`save-systems` を参照)。
- **「パーマデス」ゲームをセーブする** →
本当のパーマデスを望む場合は、ロード時のセーブ実行を削除または無効にします。プロフィールだけを残しておきます。
- **読み取り不能状態** → プレイヤーは計画を立てることができません。 HP、ターン結果、メッセージログを表示します。

 ## 構成 (これらのスキルから構築)

 - **生成:** `procedural-gen` (ノイズ、シードされた RNG、ダンジョン/ルーム アルゴリズム) — リプレイ性のエンジン。
- **地図のレンダリング:** グリッドの `godot-tilemap` / `unity-tilemap-2d`。 `level-design` セットピース ルーム/ボールト用。
- **敵:** モンスターの意思決定のための `game-ai` (多くの場合、グリッド上で単純です: 探索/逃走/パトロール)。
- **永続性:** 実行再開、プロファイル/メタプログレッション、および真の永久消去用の `save-systems`。
- **スクリプト/データ:** `godot-resources` / `unity-scriptableobjects` アイテム、モンスター、ドロップ テーブルをデータとして定義します。
- **UI:** メッセージ ログ、インベントリ、および HUD 用の `godot-ui-control`。
- **感触:** ヒット/デス ジュース用の `game-feel` — ターンベースのグリッドにインパクトを与える画面の揺れとヒット ストップ。

 ## 参考資料

 - ダンジョン生成アルゴリズム (部屋と廊下、BSP、セル オートマトン、接続)、
 FOV (シャドウキャスティング)、および加重戦利品/スポーン テーブルについては、`references/generation-fov-loot.md` を参照してください。 
