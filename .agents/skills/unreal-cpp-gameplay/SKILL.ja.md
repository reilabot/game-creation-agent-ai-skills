---
name: unreal-cpp-gameplay
description: >
  Write Unreal Engine 5 C++ gameplay code: the UCLASS/UPROPERTY/UFUNCTION reflection macros,
  the Gameplay Framework (GameMode, Pawn, Character, PlayerController, Actor components), and
  the module Build.cs. Use when writing or debugging UE C++, deriving from AActor/ACharacter/
  AGameModeBase, exposing properties to the editor or Blueprints, or when the user mentions
  Unreal C++, UCLASS, GENERATED_BODY, GameMode, ACharacter, or .Build.cs.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # Unreal C++ ゲームプレイ

 正しい UE5 ゲームプレイ C++ を作成します: C++ をエディターと
ブループリントに接続するリフレクション マクロ、ゲームプレイ フレームワーク クラスのロール、およびモジュールの依存関係。 **UE 5.8** をターゲットとしています。

 ##

 を使用する場合 - C++ ゲームプレイ クラス (`AActor`、`APawn`、`ACharacter`、`AGameModeBase`、
 `UActorComponent`) を作成し、プロパティ/関数を公開するときに使用します。 `UPROPERTY`/`UFUNCTION`、
 ゲームモードのデフォルト クラスを設定する、または `*.Build.cs` にモジュールの依存関係を追加します。
- プロジェクトに、`UCLASS` および `*.Build.cs` を使用する `*.h`/`*.cpp` を持つ `Source/` ツリーがある場合に使用します。

 **使用しない場合:** デザイナー向けのビジュアル ロジック → `unreal-blueprints`。プレーヤー入力
バインディング詳細 → `unreal-enhanced-input`。 AIロジック→`unreal-behavior-trees`。このスキルは、その上に構築される C++ クラス/リフレクション基盤である
を所有します。

 ## コア ワークフロー

 1. **正しい接頭辞を付けた名前。** `A` = アクター派生、`U` = `UObject`/コンポーネント派生、
 `F` = プレーン構造体、`E` = 列挙型、`I` = インターフェイス。プレフィックスは基本クラスと一致する必要があります。
2. **リフレクション マクロを使用してクラスを宣言します。** クラスの上に `UCLASS()`、本文の最初の行として `GENERATED_BODY()` 
、ヘッダーの **最後の**
インクルードとして `#include "ClassName.generated.h"`。
3. **`UPROPERTY`** (エディター/ブループリントの可視性 * および* ガベージ コレクション
追跡) でデータを公開し、`UFUNCTION` (`BlueprintCallable` など) で動作を公開します。
4. **コンストラクターでコンポーネントを作成**、`CreateDefaultSubobject<T>(TEXT("Name"))` および
は `RootComponent` を設定します。
5. **フレームワークの役割を理解する:** `AGameModeBase` はルールとデフォルトのクラスを設定します。 `APawn`/
`ACharacter` は制御可能な本体です。 `APlayerController` はプレイヤーの意志です。
`UActorComponent` は再利用可能な動作です。
6. **モジュールの依存関係を追加**して `*.Build.cs` (例: `EnhancedInput`) または未解決のシンボル
リンク エラーが続きます。
7. コンパイル (関数本体の場合はライブ コーディング `Ctrl+Alt+F11`、
 ヘッダー/UPROPERTY の変更については完全な再構築) し、エディターに表示されるクラス/プロパティを確認することで **検証** します。

 ## パターン

 ### 1. 最小限のアクター クラス (ヘッダー + ソース)

```cpp
// Pickup.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Pickup.generated.h"          // MUST be the last include

UCLASS()
class MYGAME_API APickup : public AActor   // MYGAME_API = your module's export macro
{
    GENERATED_BODY()
public:
    APickup();

    // EditAnywhere = tweak per-instance & on the CDO; BlueprintReadWrite = BP get/set.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Pickup")
    int32 ScoreValue = 10;

    // UPROPERTY on a UObject* pointer is what keeps it from being garbage-collected.
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UStaticMeshComponent> Mesh;   // UE5: TObjectPtr instead of raw UStaticMeshComponent*

    UFUNCTION(BlueprintCallable, Category = "Pickup")
    void Collect();

protected:
    virtual void BeginPlay() override;
};
```

```cpp
// Pickup.cpp
#include "Pickup.h"
#include "Components/StaticMeshComponent.h"

APickup::APickup()
{
    Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
    RootComponent = Mesh;                     // the mesh is this actor's root
}

void APickup::BeginPlay() { Super::BeginPlay(); }   // always call Super
void APickup::Collect()   { Destroy(); }
```

### 2. GameMode のデフォルト クラスの接続

```cpp
// MyGameMode.cpp — set in the constructor so the engine spawns your classes.
AMyGameMode::AMyGameMode()
{
    DefaultPawnClass      = AMyCharacter::StaticClass();
    PlayerControllerClass = AMyPlayerController::StaticClass();
}
```

### 3. Build.cs のモジュールの依存関係

```csharp
// MyGame.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core", "CoreUObject", "Engine", "InputCore", "EnhancedInput"
});
```

## 落とし穴

 - **`generated.h` が最後ではない/見つからない** — 「生成されたヘッダーが見つかりません」または
「インクルードが必要です」などのコンパイル エラー。これはヘッダーの最後のインクルードである必要があります。
- **`GENERATED_BODY()` を忘れています** — UHT (Unreal Header Tool) エラー。これは、クラス本体内の最初の
である必要があります。
- **`UPROPERTY` のない生の `UObject*`** — ガベージ コレクターはそれを認識しないため、ユーザーの下から
を破棄する可能性があります。 `UPROPERTY` を使用してすべての UObject ポインターを追跡します (UE5 では `TObjectPtr` を使用します)。
- **ライブ コーディングによるヘッダー/UPROPERTY 編集** - ライブ コーディングは関数本体を処理しますが、
 から `UCLASS`/`UPROPERTY`/ヘッダーへの変更には、エディターの完全な再起動と再構築が必要です。
- **間違ったクラス プレフィックス** — アクター `UFoo` (またはコンポーネント `AFoo`) に名前を付けると UHT が壊れます。
プレフィックスを基本タイプに一致させます。
- **リンクで未解決の外部シンボル** - API を提供するモジュールが `Build.cs`
`PublicDependencyModuleNames` にありません。
- **オーバーライドされた `BeginPlay`/`Tick` などで `Super::` を呼び出していません**。エンジンのセットアップをスキップします。

 ## 参照

 - `UActorComponent` の作成/添付、`UPROPERTY` ガベージ コレクション所有権ルール
(`TObjectPtr`、`TArray<TObjectPtr<>>`、`AddToRoot`)、およびレプリケーションの場合プライマー、
 `references/components-and-gc.md` と読みます。
- 主要ドキュメント: 「Unreal Engine CPP クイック スタート」および「ゲームプレイ フレームワーク」
(`https://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-framework-in-unreal-engine`)。

 ## 関連スキル

 - `unreal-blueprints` — C++ をデザイナーに公開します。 BP/C++ 相互運用性。
- `unreal-enhanced-input` — C++ ポーン/キャラクターでのバインディング入力。
- `unreal-behavior-trees` — ビヘイビア ツリーから駆動される C++ AI タスク。 
