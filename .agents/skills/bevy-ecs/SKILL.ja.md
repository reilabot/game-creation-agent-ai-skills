---
name: bevy-ecs
description: >
  Structure a Bevy app around its Entity Component System: build the App with
  plugins, define Component/Resource types, write systems with Query/Res/Commands,
  filter and order systems, and use the Time resource for frame-rate-independent
  motion. Use when building or debugging a Bevy game in Rust — when the user
  mentions Bevy, ECS, App::new, add_systems, Query, Commands, components/systems,
  or a Cargo.toml depending on bevy.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # Bevy ECS

 エンティティ コンポーネント システム (`App` および
プラグイン、コンポーネントとリソース、クエリを備えたシステム、スケジューリング、および
フレーム レートに依存しない更新) を中心に、Rust で Bevy ゲームを構築します。新しい例は **Bevy 0.19** をターゲットとしています。プロジェクト
がすでに別のリリースを固定している場合は、そのリリースを保持し、対応する移行ガイドを使用してください。

 ##

 を使用する場合 - Bevy `App` を配線する場合、`Component`/`Resource` タイプを定義する場合、エンティティをクエリする
システムを作成する場合、システムの順序付け/フィルター処理を行う場合、または
借用競合パニックを修正する場合に使用します。そしてフレームに依存した動き。
- `Cargo.toml` が `bevy` に依存しており、コードが `App::new()`、
 `add_systems`、`Query`、または `Commands` を呼び出す場合に使用します。

 **使用しない*場合:** これは ECS コアです。ディープ レンダリング、カスタム シェーダー/
 パイプライン、UI レイアウト、オーディオは別の問題です。エンジンに依存しない AI または
手続き型アルゴリズムの場合は、`game-ai` / `procedural-gen` と組み合わせます。

 ## コア ワークフロー

 1. **バージョンを検出して固定します。** 最初に `Cargo.toml` と `Cargo.lock` を読み取ります。
の新しいプロジェクトの場合は、`bevy = "0.19"` を使用します。既存のプロジェクト
を Bevy マイナー リリースにサイレントに移行しないでください。一致するドキュメントと移行ガイドを真実として扱います。
2. **`App` を構築します。** `App::new().add_plugins(DefaultPlugins)` は、ウィンドウ処理、
 入力、レンダリング、時間などを提供します。 システムをスケジュールに登録します: `Startup` (1 回)
および `Update` (フレームごと)。
3. **コンポーネントとしてのモデル データ、リソースとしてのグローバル。** エンティティごとの
データの場合は `#[derive(Component)]`。ユニークなデータの `#[derive(Resource)]` (スコア、設定、
、`Time` クロック)。 0.19 では、`Resource` は `Component` を拡張するため、両方を導出しないでください。
4. **システムをプレーン関数として記述します。** パラメーターはデータ アクセスを宣言します: エンティティの場合は `Query<...>` 
、リソースの場合は `Res<T>`/`ResMut<T>`、遅延
の生成/デスポーンの場合は `Commands`。システムは、アクセスが競合しない場合には並行して実行されます。
5. **`time.delta_secs()` によってモーションを駆動する**ため、速度はフレームレートに依存しません。
6. `.chain()` または明示的な制約を使用して、**注文する必要があるものだけを注文します**。 `run_if` を備えた
ゲート システム。関連するセットアップを `Plugin` にグループ化します。
`cargo run` でビルドし、パニックを読み取ります — Bevy は起動時に競合するクエリを報告します。

 ## パターン

 ### 1. Cargo.toml + 最小限のアプリ

```toml
# Cargo.toml — pin the version; the API differs across minor releases.
[dependencies]
bevy = "0.19"
```

```rust
// main.rs
use bevy::prelude::*;

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)            // window, input, render, time, ...
        .add_systems(Startup, setup)            // runs once at startup
        .add_systems(Update, move_players)      // runs every frame
        .run();
}
```

### 2. コンポーネント、リソース、および生成

```rust
#[derive(Component)]
struct Player;

#[derive(Component)]
struct Velocity(Vec2);

#[derive(Resource)]
struct Score(u32);

fn setup(mut commands: Commands) {
    commands.insert_resource(Score(0));

    // Camera2d is a component with required components (bundles removed in 0.16);
    // spawning it pulls in Transform, Camera, etc. automatically.
    commands.spawn(Camera2d);

    // Spawn an entity as a tuple of components.
    commands.spawn((
        Player,
        Velocity(Vec2::new(150.0, 0.0)),
        Transform::from_xyz(0.0, 0.0, 0.0),
    ));
}
```

### 3. クエリ + 時間リソースを備えたシステム

```rust
// Iterate every entity that has BOTH Velocity and Transform; mutate Transform.
fn move_players(time: Res<Time>, mut query: Query<(&Velocity, &mut Transform)>) {
    for (velocity, mut transform) in &mut query {
        // delta_secs() is f32 seconds (renamed from delta_seconds() in 0.16).
        transform.translation += velocity.0.extend(0.0) * time.delta_secs();
    }
}
```

### 4. クエリフィルター (あり/なし/変更あり)

```rust
// Only entities tagged Player (the Player component itself isn't read).
fn aim_player(mut q: Query<&mut Transform, With<Player>>) { /* ... */ }

// Disjoint two mutable Transform queries so they don't conflict at runtime.
fn separate(
    mut players: Query<&mut Transform, With<Player>>,
    mut enemies: Query<&mut Transform, Without<Player>>,
) { /* ... */ }

// React only when Health changed since last run (change detection).
fn on_health_change(q: Query<&Health, Changed<Health>>) {
    for health in &q { /* update the HUD, etc. */ }
}
```

### 5. リソース: 読み取りおよび書き込み

```rust
fn add_points(mut score: ResMut<Score>) {
    score.0 += 10;                 // ResMut = write access
}

fn show_score(score: Res<Score>) {
    info!("score: {}", score.0);   // Res = read access
}
```

### 6. 順序、実行条件、およびプラグイン

```rust
fn main() {
    App::new()
        .add_plugins((DefaultPlugins, GameplayPlugin))
        // .chain() forces order: damage resolves before death is checked.
        .add_systems(Update, (apply_damage, check_deaths).chain())
        // run_if gates a system on a condition each frame.
        .add_systems(Update, spawn_wave.run_if(wave_timer_finished))
        .run();
}

struct GameplayPlugin;
impl Plugin for GameplayPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(Score(0))
           .add_systems(Startup, setup)
           .add_systems(Update, (move_players, add_points));
    }
}
```

## 落とし穴

 - **`delta_seconds()` が見つかりません** → 0.16 では `time.delta_secs()` (および
`elapsed_secs()`) に名前変更されました。古い名前を使用するとコンパイルに失敗します。
- **移動速度はフレーム レートに応じて変化します** → フレームごとの変化に
`time.delta_secs()` を掛けます。固定フレーム時間を決して想定しないでください。
- **パニック: "アクセスの競合" / "&mut T と &mut T"** → 1 つの
システム内の 2 つの `Query` が両方とも同じコンポーネントを書き込むか、一方が読み取り中にもう一方が重複する
エンティティを書き込みます。 `With`/`Without` と切り離すか、`ParamSet` を使用してください。
- **`Camera2dBundle`/`SpriteBundle` が見つかりません** → バンドルは 0.15 で非推奨となり、
 は 0.16 で削除されました。
コンポーネントを直接生成します (`Camera2d`、`Sprite`、`Transform`)。必要な
コンポーネントが残りを埋めます。
- **「特性 `Component` は実装されていません」** → `#[derive(Component)]`
(リソースの場合は `#[derive(Resource)]`) を忘れました。
- **生成されたエンティティは同じフレーム内の後のクエリには表示されません** → `Commands` は
延期され、次の同期ポイントで適用されます。エンティティを生成したシステムではなく、後続のシステム
でエンティティを読み取ります。
- **システムの順序は想定されていますが、強制されていません** → システムはデフォルトで並行して実行されます。
`B` が `A` の後に続く必要がある場合は、`(A, B).chain()` または明示的な順序制約を追加します。
- **0.19 で `Resource` と `Component` の両方を導出** → `Resource` は
`Component` を拡張するようになりました。競合する実装を避けるために、`Resource` を単独で導出します。
- **古い Bevy スニペットをコピーして貼り付ける** → API はマイナー バージョン間で移行します。
バッファリングされたイベント システムは、最近のリリースではメッセージ システムになりました。 *あなたの*固定バージョンのドキュメントと移行ガイドを
と照合して確認します。バージョンを混合しないでください。

 ## 参照

 - スケジュールおよび `SystemSet` 順序の場合、`States`/`OnEnter`/`OnExit`、
 検出、`Commands` ライフサイクルおよび同期ポイントの変更、競合する
クエリについては `ParamSet`、イベント/オブザーバー API のバージョン ノートについては、
 `references/queries-and-scheduling.md` を参照してください。

 ## 関連スキル

 - `game-ai` — ECS に実装する移植可能な概念としての FSM/ビヘイビア ツリー/ステアリング。
- `procedural-gen` — システムから駆動するノイズ/RNG/生成アルゴリズム。
- `pygame-core` / `love2d-core` — 小規模プロジェクト向けの軽量エンジン。 
