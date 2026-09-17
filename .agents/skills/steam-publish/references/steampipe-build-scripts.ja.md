# SteamPipe: 高度なビルド スクリプト、ブランチ、CI/CD、トラブルシューティング

 `steam-publish` の深さ。 1 つのデポと 1 つの `app_build.vdf` では不十分な場合、つまり複数のプラットフォーム/言語、ファイル フィルタリング、ベータ ブランチ、自動アップロード、または
ビルドが完了しない場合に、これをお読みください。すべてのファイル形式は Valve **KeyValues (VDF)** です。プライマリ ドキュメント: Steamworks → SDK → [Uploading to Steam](https://partner.steamgames.com/doc/sdk/uploading) を
と照合して確認します。

 ## 1. 個別のデポ スクリプトを使用したアプリ ビルド スクリプト

 複数のデポを持つアプリの場合は、アプリ スクリプトを薄くし、
 デポごとに 1 つのデポ スクリプトを参照します。規則: `app_build_<AppID>.vdf` および `depot_build_<DepotID>.vdf`。

```text
// scripts/app_build_1000.vdf  — game 1000 with a Windows depot (1001) and a content depot (1002).
"AppBuild"
{
    "AppID"       "1000"
    "Desc"        "1.2.0"
    "ContentRoot" "..\content\"
    "BuildOutput" "..\output\"

    // Optional top-level switches:
    // "Preview" "1"          // dry run: write manifest/logs, upload nothing
    // "SetLive" "beta-qa"    // auto-set live on this BETA branch (never "default")
    // "Local"   "..\..\ContentServer\htdocs"   // build to a Local Content Server instead

    "Depots"
    {
        "1001" "depot_build_1001.vdf"   // reference external depot scripts
        "1002" "depot_build_1002.vdf"
    }
}
```

```text
// scripts/depot_build_1002.vdf — file mapping, exclusions, and special file flags.
"DepotBuild"
{
    "DepotID" "1002"

    // Map a subtree into a folder inside the depot.
    "FileMapping"
    {
        "LocalPath" "bin\*"          // wildcards '*' and '?' allowed
        "DepotPath" "executables\"
        "Recursive" "1"
    }

    "FileExclusion" "*.pdb"          // drop debug symbols everywhere
    "FileExclusion" "bin\tools\*"    // drop a whole subtree

    // Mark files that the game/user writes at runtime so updates don't clobber them:
    "FileProperties"
    {
        "LocalPath"  "settings.cfg"
        "Attributes" "userconfig"    // user-modified: never overwritten, never flagged on verify
    }
    // "versionedconfig" is like userconfig but IS overwritten when you change it in the depot
    // (use only for genuine format changes/bug fixes).
}
```

注:
- `ContentRoot` は、`DepotBuild` 内のデポごとにオーバーライドできます。
- `InstallScript "<file.vdf>"` は、Steam クライアントがデポ (前提条件、レジストリ、ショートカット) をマウントする
アプリに対して実行するインストール スクリプトをマークし、署名します。ほとんどのゲームでは必要ありません。
- スクリプトには任意の名前を付けることができます。 `app_build_<AppID>` / `depot_build_<DepotID>` 規則
は、複数のアプリのビルド マシンを整理するだけです。

 ## 2. ビルドの実行 (プラットフォームごと)

```bash
# Windows
tools\ContentBuilder\builder\steamcmd.exe +login <account> <password> +run_app_build ..\scripts\app_build_1000.vdf +quit

# Linux / macOS (bootstrap once, then build)
./tools/ContentBuilder/builder_linux/steamcmd.sh +login <account> <password> +run_app_build ../scripts/app_build_1000.vdf +quit
```

macOS の初回実行ブートストラップ: `cd tools/ContentBuilder/builder_osx`、`chmod +x steamcmd`、
 `bash ./steamcmd.sh`、その後、`Steam>` プロンプトに達したら `exit`。

 ## 3. ブランチ (ベータ版) — 顧客に表示される前にテストする

 **デフォルト** ブランチが顧客に提供されます。常に最初にベータ ブランチでビルドを検証してください。

 1. アプリ管理の **ビルド** ページにブランチを作成します。 **スペースを含まない**名前を使用してください。プライベートにする必要がある場合は、
 **パスワード**を追加します (プレイヤーは *プロパティ → ベータ* で入力します)。
2. ビルドをアップロードするか (上記の steamcmd)、または `"SetLive" "<branch>"` で自動ターゲットを設定します。
3. [ビルド] ページで、[*ブランチにビルドをライブに設定…*]、**変更のプレビュー**、
 でブランチを選択し、**今すぐビルドをライブに設定**します。
4. Steam クライアント経由でオプトインします。ゲームを右クリック → *プロパティ* → *ベータ* →
ブランチを選択します。 Steam はそれをダウンロードし、インストールされているブランチを置き換えます。

 リマインダー: `default` ブランチをライブに自動設定する方法は**ありません**。自信がある場合は、テスト済みのベータ版
ビルドを手動でデフォルトにプロモートしてください。

 ## 4. CI/CD アップロード (トークンベースのログイン、スクリプトにパスワードなし)

 steamcmd は、Steam
ガードによる対話型ログインが成功した後、ログイン トークンを `config.vdf` に保存します。 CI はパスワードの代わりにそのトークンを再利用します。

 1. ビルド マシン上で (またはローカルで一度) `steamcmd +login <username>` を実行し、
 パスワードと Steam ガード コードを入力し、「接続済み」を確認するために `info` と入力してから、`quit` と入力します。
2. **CI 実行間で `<Steam>/config/config.vdf` を保持します** (シークレット アーティファクトとしてキャッシュします)。
このファイルには、更新されたログイン トークンが保持されます。
3. 以降の実行では、**パスワードなし**でログインします: `steamcmd +login <username>`。

```yaml
# GitHub Actions sketch — restore the token, then build. Never echo the token.
# Store the base64 of config.vdf as a repo secret (e.g. STEAM_CONFIG_VDF).
- name: Restore steam login token
  run: |
    mkdir -p ~/Steam/config
    echo "${{ secrets.STEAM_CONFIG_VDF }}" | base64 -d > ~/Steam/config/config.vdf
- name: Upload build to Steam
  run: |
    steamcmd +login "${{ secrets.STEAM_BUILD_ACCOUNT }}" \
      +run_app_build "$PWD/scripts/app_build_1000.vdf" +quit
```

- ビルド実行で `Account Login Denied` が出力される場合、Steam ガードがブロックしています。 steamcmd (アカウントの電子メールからのコード) で
`set_steam_guard_code <code>` を実行し、ログインを再試行します。
- パスワードを再入力すると、**新しい** Steam Guard トークンが発行され、キャッシュされたトークンが無効になります。
 は CI でこれを回避します。
- `config.vdf`、アカウント パスワード、または Steam ガード コードを印刷またはコミットしないでください。
漏洩したトークンを侵害されたものとして扱い、アカウントを再保護します。

 ## 5. パッチサイズの衛生管理 (更新を小規模に保つ)

 SteamPipe は ~1 MB チャンク粒度で差分を行い、変更されたチャンクのみを出荷します。
更新の肥大化を回避するには:

 - アセットの境界を越える方法で独自のパック ファイルを圧縮または暗号化しないでください。
 に小さな変更を加えると、圧縮された BLOB 全体が書き換えられます。 Steam 側で圧縮を行います。
- パック ファイル内のアセットの変更をローカライズします。資産の順序を入れ替えないようにします。パック ファイルを
~1 ～ 2 GB に保ち、レベル/機能ごとにグループ化します。
が既存の大きなファイルを書き換えるのではなく、新しいコンテンツ用に **新しい** パック ファイルを追加します。
- **Unreal Engine** パック アライメント: `-patchpaddingalign=1048576 -blocksize=1048576`
でビルドするため、再アライメントは SteamPipe のブロック サイズによってシフトされ、パッチは小さいままになります。

 ## 6. トラブルシューティング表

 |症状 |考えられる原因 |修正 |
|---|---|---|
| `Failed to get application info for app NNNNN` |アプリ ID が間違っています。アカウントがアプリを所有していないか、構成が公開されていません。スクリプト内のアプリ ID を確認します。所有権を確認する。 **アプリ管理でアプリ構成を公開**します。
| `ERROR! Failed 'DepotBuild …' status = 6` |ビルド アカウントに権限がないか、`ContentRoot`/`LocalPath` が間違っているか空です | *アプリのメタデータの編集* + *アプリの変更の公開* を付与します。パスがスクリプトに対して相対的であり、ファイルが含まれていることを確認してください。
| steamcmd の `Account Login Denied` | Steam ガードが自動ログインをブロック | `set_steam_guard_code <code>` してから再試行してください。将来の実行のために `config.vdf` を保存します。
|ビルドはアップロードされましたが、プレイヤーはそれを理解できません |ビルドをライブに設定しない、またはベータ ブランチでのみライブに設定する | [ビルド] ページから正しいブランチ (デフォルト = 手動) にライブを設定します。
| Windows はインストールしますが、Mac/Linux はファイルをインストールしません | OS デポがパッケージに追加されない | *関連パッケージと DLC* | すべてのデポをパッケージに追加します。
|起動時の「無効なコンテンツ構成」 |選択したブランチにビルド セットが存在しないか、起動オプションが正しくありません。ビルドをライブに設定します。 *インストール* 起動オプションを確認する |
| steamcmd コマンドの構文を忘れた | — | `Steam>` プロンプトで `find <partial>` (例: `find build_installer`) を実行して、一致するコマンド + 引数 | を出力します。

 `BuildOutput` (コンソールではなく) の `*.log` ファイルをチェックして、
 失敗したビルドに関する権限のあるエラーを確認します。 
