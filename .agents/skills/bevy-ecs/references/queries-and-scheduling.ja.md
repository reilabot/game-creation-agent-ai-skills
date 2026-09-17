# Bevy クエリとスケジュールの詳細 (0.19)

 ECS スキルの詳細: クエリ フィルターとアクセス、スケジュールと順序付け、
 状態、変更検出、および `Commands` ライフサイクル。固定された Bevy バージョンのドキュメントと照らし合わせて境界線にある API
を確認します。マイナー リリースでは状況が変わります。

 ## クエリの構造

 `Query<D, F>` には、**データ** 部分 `D` (読み取り/書き込み対象) と、オプションの
**フィルター** 部分 `F` (データをフェッチしないエンティティ) があります。

```rust
// Data: read Name, write Transform. Filter: must have Player, must NOT have Frozen.
Query<(&Name, &mut Transform), (With<Player>, Without<Frozen>)>
```

共通フィルター:

 - `With<T>` / `Without<T>` — エンティティにはコンポーネントがある、またはコンポーネントがありません (データはフェッチされません)。
- `Added<T>` — このシステムが最後に実行されてから、`T` が追加されました。
- `Changed<T>` — `T` は、最後の実行 (変更検出) 以降に追加または変更可能にアクセスされました。
- `Or<(...)>` — フィルタを選言的に結合します。

 データ部分のオプションおよびエンティティ アクセス:

```rust
Query<(Entity, &Transform, Option<&Velocity>)>  // Entity id; Velocity may be absent
```

### 単一エンティティ アクセス

 1 つのエンティティ (プレーヤーなど) に正確に一致すると予想されるクエリの場合、0.16 以降では、`single()`
および `single_mut()` は `Result` を返します (古い
を置き換えました) `get_single`/パニック状態 `single`):

```rust
fn read_player(q: Query<&Transform, With<Player>>) {
    if let Ok(transform) = q.single() {
        // exactly one Player matched
    }
}
```

`for x in &query` の反復は常に有効であり、最も安全なデフォルトです。

 ## アクセスの競合の回避

 2 つのシステムは、データ アクセスが競合しない場合にのみ並列実行できます。 **1 つのシステム内**で 2 つの
クエリがあり、どちらも同じコンポーネントに変更可能にアクセスすると、起動時に
がパニックになります。修正:

 1. **フィルターとの不整合** — `With<Player>` と `Without<Player>` では、
 セットが決して重複しないことが保証されるため、両方が `&mut` になる可能性があります。
2. **`ParamSet`** — セットが重複する *可能性がある*場合、一度に 1 つずつアクセスします:

```rust
fn swap(mut set: ParamSet<(
    Query<&mut Transform, With<A>>,
    Query<&mut Transform, With<B>>,
)>) {
    for mut t in &mut set.p0() { /* ... */ }
    for mut t in &mut set.p1() { /* ... */ }
}
```

## スケジュールと順序

 最もよく使用する組み込みスケジュール:

 - `Startup` — 最初の `Update` の前に 1 回。
- `Update` — すべてのフレーム。
- `FixedUpdate` — 固定タイムステップ。
決定論を必要とする物理学/ゲームプレイに使用してください (ここでも `time.delta_secs()` をお読みください。これは固定ステップです)。
- `PreUpdate` / `PostUpdate` — セットアップ/ティアダウン順序の場合は `Update` あたり。

 スケジュール内の注文:

```rust
// Explicit pairwise order.
app.add_systems(Update, (input, movement, collision).chain());

// Named constraints.
app.add_systems(Update, movement.before(collision));
app.add_systems(Update, camera_follow.after(movement));
```

### システムは

 システムを `SystemSet` にグループ化し、フェーズ全体を順序付けし、共有実行
条件を付加します:

```rust
#[derive(SystemSet, Debug, Clone, PartialEq, Eq, Hash)]
enum GameSet { Input, Logic, Render }

app.configure_sets(Update, (GameSet::Input, GameSet::Logic, GameSet::Render).chain());
app.add_systems(Update, read_input.in_set(GameSet::Input));
app.add_systems(Update, (move_units, resolve).in_set(GameSet::Logic));
```

### 実行条件

```rust
app.add_systems(Update, pause_menu.run_if(in_state(AppState::Paused)));
app.add_systems(Update, autosave.run_if(on_timer(Duration::from_secs(30))));
```

##

 `States` モデルのアプリ全体のモード (メニュー、再生、一時停止) を示します。 `OnEnter`/`OnExit`
スケジュールを遷移ロジックに使用し、`in_state` を使用して `Update` システムをゲートします。

```rust
#[derive(States, Default, Debug, Clone, PartialEq, Eq, Hash)]
enum AppState { #[default] Menu, Playing }

app.init_state::<AppState>()
   .add_systems(OnEnter(AppState::Playing), spawn_level)
   .add_systems(OnExit(AppState::Playing), cleanup_level)
   .add_systems(Update, gameplay.run_if(in_state(AppState::Playing)));

// Transition from a system:
fn start(mut next: ResMut<NextState<AppState>>) { next.set(AppState::Playing); }
```

## 変更検出

 `Changed<T>` / `Added<T>` フィルターと `Ref<T>`/`Mut<T>` ラッパーを使用すると、システム
は変更されたデータにのみ反応するため、フレームごとに再計算するよりもコストがかかりません。注: `&mut T` を介して
を書き込むと、値が同じであっても変更されたことがマークされます。それが重要かどうかを
値でガードしてチェックしてください。

 ## コマンド ライフサイクル

 `Commands` キュー構造の変更 (スポーン、デスポーン、コンポーネントの挿入/削除、
 リソースの挿入)。これらは **延期**され、次の同期ポイント
(スケジュール ステージの終わり) で適用されます。つまり、

 - このフレームで生成されたエンティティは、後のシステム/ステージまでクエリに含まれません。
- `commands.entity(e).despawn()` はエンティティを削除します。 0.16 以降では、その
の子も削除されます (古い明示的な `despawn_recursive` は組み込まれていました)。

```rust
fn spawn_bullet(mut commands: Commands) {
    let id = commands.spawn((Bullet, Transform::default())).id();
    commands.entity(id).insert(Velocity(Vec2::Y * 500.0));
}
```

`World` 全体に即座に排他的にアクセスするには (1 回限りのセットアップ、複雑な
クエリ)、排他的システム `fn(&mut World)` を使用します。これは並行して実行できないため、
 は控えめに使用します。

 ## メッセージ/オブザーバー — バージョンに関する注意

 Bevy のバッファー イベント API は最近のリリースでメッセージ API に進化しましたが、
 オブザーバーは引き続きイベント指向です。システムでバッファリングされた通信が必要な場合は、別のバージョンから
の例をコピーするのではなく、固定されたリリースの正確なメッセージ/オブザーバー API を
で検索します。 
