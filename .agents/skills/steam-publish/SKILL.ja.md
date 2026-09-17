---
name: steam-publish
description: >
  Publish or update a game on Steam with Steamworks and SteamPipe: configure depots and
  packages, upload builds with steamcmd, set a build live on a branch, and run the release
  checklists. Use for Steam publishing, app_build.vdf/steamcmd uploads, depots, beta branches,
  or a store page release.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # Steam Publish (Steamworks + SteamPipe)

 完成したビルドをライブ Steam ストア ページに移動します。 2 つのトラックが並行して実行され、リリース前に両方とも
承認される必要があります: **ストア ページ** (プレゼンス) と **ビルド** (SteamPipe アップロード +
リリース チェックリスト)。このスキルは運用チェックリストです。詳細なビルド スクリプト、
 CI/CD、トラブルシューティングの詳細は `references/steampipe-build-scripts.md` にあります。

 ##

 を使用する場合 - Steam アプリのセットアップ、ストア ページの構築/編集、デポと
パッケージの構成、SteamPipe/steamcmd 経由でのビルドのアップロード、ベータ ブランチの管理、または
のリリースと Steam タイトルの更新時に使用します。
- トリガー: `steam_appid.txt`、Steamworks SDK `tools/ContentBuilder`、`app_build_*.vdf`、
 `steamcmd`、「Steam で公開」、「デポ」、「ビルドライブ設定」。

 **使用しない*場合:** itch.io で公開する (`itch-publish` を使用する)。ゲーム内で
Steamworks **API** を作成します (アチーブメント/クラウド/オーバーレイはエンジン SDK 統合でライブになっており、ここでは
ではありません)。店舗/財務 *アドバイス* (価格戦略、税金) — ユーザーを Steamworks ドキュメント
および自身の弁護士に誘導します。

 ## 前提条件 (順番に一度実行してください)

 1. **パートナー アカウント + Steam ダイレクト料金** 新しいアプリごとに、Steam ダイレクトで回収可能な
料金 (執筆時点ではアプリごとに 100 米ドル) が必要です。 **アプリ ID** を受け取ります。
 Steamworks ホームページで確認できます。アプリ ID を以下のすべてのキーとして扱います。
2. **最小限の権限を持つ専用のビルド アカウント。** ビルドには、**アプリ メタデータの編集**および**アプリの変更を Steam に公開**できる、
 パートナー グループの Steam アカウントが必要です。これらの権限のみ (管理者ログインではない) を持つ
*別の* ビルド アカウントを作成します。
アプリをリリースするには、**価格設定と割引の管理**がさらに必要です。
3. **Steamworks SDK** をアップロード マシンにダウンロードします。 SteamPipe ツールは
`tools/ContentBuilder/` の下にあります。

 > セキュリティ上の注意: アカウントのパスワードや `config.vdf` ログイン トークンをリポジトリに決してコミットしないでください。
> サポートされているトークン ワークフローについては、リファレンスの CI/CD セクションを参照してください。

 ## コア ワークフロー

1. **アプリを構成します (アプリ管理)。**
- *インストール* で **起動オプション** (OS ごとの実行可能パス + 引数) を設定します。
サブフォルダー exe の場合は、サブフォルダーを [実行可能ファイル] フィールドに入力します (先頭にスラッシュ/ドットは付けません)。
- *デポ* ページに **デポ** を追加します (デポはファイルのバケットです)。各デポに
(「ベース コンテンツ」、「Windows コンテンツ」) という名前を付けます。
デポが本当に OS または言語固有でない限り、*[すべての言語]* / *[すべての OS]* のままにしておきます。
- **デポを自分に付与します:**
*関連パッケージと DLC* ページの **Developer Comp** パッケージにデポを追加します。そうしないと、アップロードしたコンテンツを所有できなくなります。
- 構成を**公開**します。未公開の構成は、
 のアップロードが失敗する最も一般的な原因です。
2. **ストア ページ (プレゼンス トラック) を構築します。** グラフィック アセット、説明、タグ、
 トレーラー、システム要件を入力します。完了したら、[**レビューの準備ができたとマークする**] をクリックします。
ストアのレビューには最大 3 ～ 5 営業日かかります。公開する場合は少なくとも **7 日前**までに送信してください。
は、リリース前に少なくとも **2 週間****近日公開**になる必要があります。
3. **ビルド スクリプトを作成します。** 以下のパターンの単純なアプリ ビルド `.vdf` から始めます。マルチデポ/マルチプラットフォーム アプリの
は、デポ スクリプトを使用します (リファレンスを参照)。スクリプトは、
 ローカル ファイルをデポとビルド出力/ログの保存先の名前にマップします。
4. **steamcmd をブートストラップしてアップロードします。** `steamcmd` を 1 回実行して自己更新し、ビルド
(パターン) を実行します。 steamcmd はファイル (~1 MB) をチャンクし、変更されたチャンクのみをアップロードし、
 グローバル **BuildID** を登録します。
5. **ブランチでビルドをライブに設定します。** `https://partner.steamgames.com/apps/builds/<AppID>` に移動し、
 でビルドを選択し、**変更をプレビュー**して、ブランチに **今すぐビルドをライブに設定**します。最初に
ベータ ブランチでテストします (ブランチのセットアップについては `references/steampipe-build-scripts.md` を参照してください)。
6. **ゲーム ビルド チェックリストを実行**し、**レビュー準備完了としてマーク**します (ストア プレゼンスは、ビルド レビューの*前*に
で送信されている必要があります)。両方のトラックが承認される必要があります。
7. **手動でリリースします。** 承認され、近日公開が完了したら、緑色の
**アプリをリリース** ボタン → **今すぐ公開** → **今すぐリリース** を使用します。承認されたタイトルは、
 によって自動的にリリースされません**。
8. **後で更新**するには、新しいビルドをアップロードして `default` (手動) でライブ設定するか、最初にベータ ブランチに出荷する
を設定します。 `references/steampipe-build-scripts.md`を参照してください。

 ## パターン

 ### 1. SteamPipe ContentBuilder レイアウト (Steamworks SDK)

```text
tools/ContentBuilder/
  builder/         steamcmd.exe (Windows)   <- run once to bootstrap
  builder_linux/   steamcmd (Linux)
  builder_osx/     steamcmd (macOS)
  content/         <- your final, runnable build goes here (the files players get)
  output/          build logs + chunk cache (safe to delete; speeds up re-uploads)
  scripts/         <- your *.vdf build scripts live here
```

### 2. 最小限のアプリ構築スクリプト — `app_build_1000.vdf`

```text
// AppID 1000 with one depot (1001): upload everything under ../content recursively.
// VDF is Valve KeyValues: "key" "value", braces for nesting. Adjust IDs to your app.
"AppBuild"
{
    "AppID"       "1000"                 // your App ID
    "Desc"        "1.0.0 launch build"   // internal only; visible in Your Builds

    "ContentRoot" "..\content\"          // root of files to upload (relative to this file)
    "BuildOutput" "..\output\"           // logs + chunk cache

    "Depots"
    {
        "1001"                           // your Depot ID
        {
            "FileMapping"
            {
                "LocalPath"  "*"         // all files from ContentRoot
                "DepotPath"  "."         // mapped to the depot root
                "recursive"  "1"         // include subfolders
            }
        }
    }
}
```

### 3. ビルドをアップロードします (Windows。プラットフォーム ビルダーを他の場所に置き換えます)

```bat
REM Run from the SDK. Bootstrap once, then build. Use a build account, not your admin login.
tools\ContentBuilder\builder\steamcmd.exe ^
  +login <build_account> <password> ^
  +run_app_build ..\scripts\app_build_1000.vdf ^
  +quit
```

```text
What happens: steamcmd self-updates -> logs in -> for each depot, hashes files into ~1 MB
chunks -> uploads only NEW chunks -> writes a depot manifest -> finishes with a global
BuildID. The build is NOT live yet; set it live per the workflow above.
```

### 4. プレビュー ビルドを安全に反復します (何もアップロードしません)

```text
// Add to the AppBuild block to validate file mappings without uploading:
"Preview" "1"     // outputs logs + a file manifest into BuildOutput only
// And to auto-set live on a BETA branch after a successful build (never 'default'):
"SetLive" "beta-qa"
```

## 落とし穴

 - **`default` ブランチは自動的にライブに設定できません。** `SetLive` は
*ベータ* ブランチでのみ機能します。 App Admin でデフォルト (顧客) ビルドを手動でライブに設定する必要があります。これを中心に
リリースを計画します。
- **ストア ページはビルド前に承認される必要があります。** ストアの存在が送信されるまで、レビュー用にビルドを送信できません。両方とも合格する必要があり、Coming Soon は最大 2 週間実行する必要があります。
- **タイトルは自動リリースされません。** 承認後でも、選択した時点で人間が
に **アプリをリリース** をクリックする必要があります。
- **Mac/Linux は何もインストールしません。** ほとんどの場合、OS 固有のデポはパッケージに含まれていません。
*関連パッケージと DLC* のパッケージにすべてのデポを追加します。
- **未公開のアプリ構成** 「アプリケーション情報の取得に失敗しました」/ビルド エラーは通常、
 デポ、起動オプション、またはアプリ ID 構成が **公開されていない**ことを意味します。
- **ビルド時の `status = 6`。** ビルド アカウントにアプリ ID に対する権限がないか、
 `ContentRoot`/`LocalPath` が間違った (空の) パスを指しています。
- **ログイン トークンをコミットしています。** `config.vdf` Steam Guard トークンとアカウント パスワードは
シークレットです。それらをリポジトリから遠ざけてください。リファレンスの CI ワークフローを使用してください。
- **リリースされたアプリの安全性の遅延。** ビルド アカウントの電子メール/電話番号を変更すると、*リリースされた* アプリのビルドをライブに設定できるようになるまでに **3 日間**
待機する必要があります。起動直前にアカウント
を再構成しないでください。

 ## 参考資料

 - 高度なマルチデポ/マルチプラットフォーム ビルド スクリプト、`FileExclusion`/`FileProperties`、
 ベータブランチ セットアップ、CI/CD ログイン トークン ワークフロー、および SteamPipe トラブルシューティング テーブル、
 読み取り`references/steampipe-build-scripts.md`。
- 主なドキュメント: Steamworks 「Steam へのアップロード」 (`partner.steamgames.com/doc/sdk/uploading`)、
 「リリース プロセス」 (`/doc/store/releasing`)、「ブランチ (ベータ)」 (`/doc/store/application/branches`)、
 「デポ」 (`/doc/store/application/depots`)。

 ## 関連スキル

 - `itch-publish` — 同じゲームが itch.io で `butler` とともに出荷されます (多くの場合、Steam と一緒に行われます)。
- `game-jam` / `prototype-fast` — 同じプロジェクトのライフサイクルの初期段階。 
