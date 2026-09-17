# コンポーネント、ガベージ コレクション、レプリケーションの入門書 (UE 5.8 C++)

 `unreal-cpp-gameplay` の深さ。ゲームプレイ フレームワークのドキュメントと UE5
C++ プログラミング リファレンスに対して検証済み。コンポーネントの作成/添付、初心者をつまずかせる UPROPERTY/GC 所有権
ルール、および最小限のレプリケーションの例について説明します。

 ## コンポーネントの作成とアタッチ

 デフォルトのサブオブジェクトはコンストラクターで作成されます。ランタイム コンポーネントは、`NewObject` +
`RegisterComponent` を使用します。

```cpp
// In the constructor — built into the Class Default Object, editable in the Blueprint subclass.
ACharacterBase::ACharacterBase()
{
    SpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArm"));
    SpringArm->SetupAttachment(RootComponent);          // attach to an existing component
    SpringArm->TargetArmLength = 300.f;

    Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
    Camera->SetupAttachment(SpringArm);                 // socket chain: root -> arm -> camera
}
```

```cpp
// At runtime (e.g. add a component after spawn):
UAudioComponent* Audio = NewObject<UAudioComponent>(this);
Audio->RegisterComponent();                              // required, or it won't tick/render
Audio->AttachToComponent(RootComponent, FAttachmentTransformRules::KeepRelativeTransform);
```

- `CreateDefaultSubobject` はコンストラクター内で**のみ**有効です。それを後で使用するとアサートされます。
- `SetupAttachment` はコンストラクター時の階層用です。 `AttachToComponent` はランタイム呼び出しです。

 ## ガベージ コレクションの所有権 (#1 の新参者クラッシュ)

 UE ガベージ コレクターは、反映された
参照を通じて到達できる場合にのみ、`UObject` を存続させます。 `UPROPERTY` ではない生の `UObject*` メンバーは GC には見えず、ダングリング ポインターを残して
収集される可能性があります。

```cpp
UPROPERTY()                                  // GC sees it -> stays alive while this owner lives
TObjectPtr<UMyDataObject> Data;

UPROPERTY()
TArray<TObjectPtr<AActor>> Tracked;          // containers of UObjects also need UPROPERTY

UMyDataObject* Raw;                           // BUG: not tracked; may be GC'd -> crash
```

ルール:
- 永続化する必要があるすべての `UObject`/Actor ポインターは、`UPROPERTY` を取得します (
 UE5 では `TObjectPtr<T>` を使用します。生のポインターは引き続きコンパイルされますが、`TObjectPtr` はエディターでアクセス追跡を追加します)。
- プレーン C++ データ (POD の ints、FStrings、FVectors、USTRUCTs) にはこれは必要ありません。
 値によって所有されます。
- UPROPERTY 所有者を持たない作成した UObject の場合 (まれに)、`AddToRoot()` がそれを固定し、
 `RemoveFromRoot()` がそれを解放します。ただし、適切な所有権が優先されます。

 ## 反映されたデータの USTRUCT および UENUM

```cpp
UENUM(BlueprintType)
enum class EWeaponType : uint8 { Pistol, Rifle, Shotgun };

USTRUCT(BlueprintType)
struct FWeaponStats
{
    GENERATED_BODY()
    UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 Damage = 10;
    UPROPERTY(EditAnywhere, BlueprintReadWrite) float FireRate = 0.25f;
};
```

`BlueprintType` は、enum/struct をブループリント変数として使用できるようにします。

 ## 最小限のレプリケーション (マルチプレイヤー)

```cpp
// Header
UPROPERTY(ReplicatedUsing = OnRep_Health)
float Health = 100.f;

UFUNCTION()
void OnRep_Health();                          // client callback when Health replicates

// Source
#include "Net/UnrealNetwork.h"
void AMyActor::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& Out) const
{
    Super::GetLifetimeReplicatedProps(Out);
    DOREPLIFETIME(AMyActor, Health);          // register the property for replication
}
```

- アクターがレプリケートできるようにコンストラクターで `bReplicates = true;` を設定します。
- サーバー権限: ゲームプレイの変更はサーバー上で行われます。クライアントは複製された状態を受け取り、
 は `OnRep_` コールバックで反応します。

 ## 注意点

 - `RegisterComponent` なしの `NewObject` は、コンポーネントは存在しますが、ティックや
レンダリングは行われません。
- `#include "Net/UnrealNetwork.h"` を忘れると、`DOREPLIFETIME` が壊れます。
- `TObjectPtr` は呼び出し用の生のポインターに暗黙的に変換されるため、既存の `->`/`.` の使用法は
のままです。違いは GC の可視性とエディター ツールであり、呼び出しサイトの構文ではありません。 
