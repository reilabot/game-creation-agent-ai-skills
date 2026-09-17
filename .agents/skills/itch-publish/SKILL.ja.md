---
name: itch-publish
description: >
  Publish and update a game on itch.io: create the project page and upload builds with the
  butler CLI (butler push) to named channels. Use for itch.io publishing, butler push,
  channel naming for Windows/macOS/Linux/HTML5, versioning uploads, or shipping a jam or
  release build to itch.io.
---
> 日本語参考訳です。Agent Skillsの実行時は同じディレクトリの`SKILL.md`を正本として使用してください。


 # itch.io 公開 (バトラー)

 itch.io ページにビルドを取得し、更新し続けます。ページはブラウザで作成されます。すべての
アップロードは、itch.io のコマンドライン ツールである **butler** を経由します。1 つのコマンド (`butler push`) で、
 を永久に使用できます。 butler は以前のビルドとの差分を取り、
 が変更したもののみをアップロードします。詳しい CI/CD とフラグの詳細は `references/butler-ci.md` にあります。

 ##
を使用する場合
- itch.io プロジェクト ページの作成/更新、バトラーのインストールまたはログイン、`butler push` でビルドをアップロードする 
、チャンネル名の選択、アップロードのバージョン管理、またはジャム/デモ/リリース ビルドを
に送信するときに使用します。かゆみ。
- トリガー: `butler push`、`butler login`、チャネル、`.itch.toml`、「itch で公開」、
 「itch にアップロード」。

 **使用しない*場合:** Steam で公開する (`steam-publish` を使用する)。 jam *範囲/計画* (
 `game-jam` を使用します。このスキルはアップロードの仕組みのみです)。ゲーム自体の構築 (
 スキルのエンジン)。

 ## コア ワークフロー

 1. `itch.io/game/new` で **プロジェクト ページを作成**します。 **プロジェクトの種類**を設定します。ネイティブ ビルドの場合は
*ダウンロード可能* のままにするか、ブラウザでプレイ可能なゲームの場合は **HTML** を選択します (これは Web ビルドに必要な
です。「落とし穴」を参照)。価格設定/可視性を設定します (準備が整うまで下書きします)。
2. **バトラーをインストールしてログインします。** `itchio.itch.io/butler` からダウンロードし、`PATH`、
、`butler login` に追加します (認証するためにブラウザーが開きます)。 `butler version`で確認します。
CI の場合は、代わりに `BUTLER_API_KEY` を使用してください。リファレンスを参照してください。
3. **ポータブル ビルド フォルダーを準備します** — プレーヤーが実行する正確なファイルであり、余分なものは何もありません。
**フォルダー** (またはそのフォルダー * の単一 `.zip`) をプッシュします。**インストーラー** ではなく、****
 圧縮済みのアーカイブ アーカイブでもありません** (パッチ適用に問題があります。「落とし穴」を参照)。
4. **チャネルにプッシュします:** `butler push <dir> <user>/<game>:<channel>`。チャネル名
によってプラットフォーム タグが決まります (「パターン」を参照)。最初のプッシュですべてがアップロードされます。その後、
 が同じチャネルにプッシュして差分のみをアップロードします。
5. チャンネルに
が正しく自動タグ付けされていない場合は、*ゲームの編集* ページで **プラットフォーム/HTML タグを設定**し、**保存**します。ブラウザ ゲームの場合は、ページを **HTML** に切り替え、*ブラウザで再生可能な
チャンネルにタグを付けます*。
6. **ビルドのバージョン管理** (オプションですが推奨): `--userversion 1.2.0` または
`--userversion-file build.txt` これにより、バージョン文字列プレーヤーと更新
API を制御できます。
7. *同じ* チャンネルにもう一度プッシュして、**後で更新**します。 `butler status <user>/<game>`
を使用してチャネル/ビルドを確認し、`butler push-preview` を使用して、
 がプッシュを送信する前にプッシュによってどのような変化が生じるかを確認します。

 ## パターン

 ### 1. 必要なコマンドは 1 つ — `butler push`

```bash
# butler push <directory-or-zip> <user>/<game>:<channel>
butler push ./build/windows leafy/my-game:windows
butler push ./build/mac     leafy/my-game:osx
butler push ./build/linux   leafy/my-game:linux
butler push ./web           leafy/my-game:html   # browser build (also set page Kind = HTML)
```

### 2. チャネルの名前付けはプラットフォーム タグを制御します (ケバブケース、小文字)

```text
Substring in channel name -> auto-applied tag:
  win / windows  -> Windows        linux -> Linux
  mac / osx      -> macOS          android -> Android
Multiple platforms in one channel are allowed: e.g. a Java jar:
  butler push ./jar leafy/my-game:win-linux-mac
Convention: lowercase words separated by dashes (windows-beta, osx-demo, soundtrack).
Tags are only the INITIAL guess — fix them anytime on the Edit game page (then Save).
```

### 3. バージョン、検証、プレビュー

```bash
butler version                              # print version; confirms install + PATH
butler login                                # authorize this machine (opens browser)

# Set an explicit version string instead of itch's auto-incrementing integer:
butler push ./build leafy/my-game:windows --userversion 1.2.0
butler push ./build leafy/my-game:windows --userversion-file build_number.txt

butler status leafy/my-game                 # list channels + latest builds/versions
butler push-preview ./build leafy/my-game:windows   # NEW/MODIFIED/DELETED/SAME, uploads nothing
```

### 4. 初回、非表示、フィルター処理されたプッシュ

```bash
# Hide a brand-new channel from the page until you're ready (NEW channels only):
butler push ./build leafy/my-game:windows-beta --hidden

# Exclude files from the upload without copying the folder (--ignore is repeatable):
butler push ./build leafy/my-game:windows --ignore '*.pdb' --ignore '*.dSYM'

# Preview exactly what would be sent, without sending it:
butler push ./build leafy/my-game:windows --dry-run
```

## 落とし穴

 - **インストーラーのプッシュ** itch.io パッチ *ポータブル* ビルド。インストーラー (`.exe`/`.msi`)
はパッチ適用と itch アプリの自動更新を無効にし、
 プレイヤーが持っていない管理者権限が必要になる場合があります。代わりに、抽出された実行可能なフォルダーをプッシュします。
- **事前圧縮されたビルド。** 高度に圧縮されたアーカイブ (またはアーカイブのアーカイブ) をプッシュすると、
 はパッチを巨大なものにします。小さな変更により、圧縮された BLOB 全体が書き換えられます。非圧縮
ファイルをプッシュします。 itch.io は横に圧縮されます。
- **`.zip`.** を 1 つだけ含むフォルダー。** バトラーはそれを自動解凍し、内容
をプッシュします (「zip の中に zip」を避けるため)。 zip アップロードされた
を 1 つの不透明なファイルとして本当に必要な場合にのみ、`--no-auto-unzip` を渡します。
- **HTML5 ゲームがダウンロードとして表示されます。** 2 つのスイッチが必要です。ページ **種類** を
*HTML* に設定し、最初の
プッシュ後に *ゲームの編集* ページでチャンネルに *ブラウザーで再生可能* タグを付けます。どちらもチャンネル名から自動的に行われません。
- **既存のチャネルでの `--hidden` エラー。** これは、プッシュによって新しい
チャネルが *作成*される場合にのみ適用されます。後で *ゲームの編集* から再表示します。
- **チャンネルのタイプミスによりスロットが重複します。** `windows` と `win-final` は異なるチャンネルであり、
 は個別のダウンロードを作成します。チャンネル名を事前に決めて再利用します。
- **30 GB の上限** itch.io は、*非圧縮* 合計サイズが 30 GB を超えるビルドを拒否します。
- **CI ログの秘密** 公開ログに出力された `BUTLER_API_KEY` は侵害されています。API キー ページですぐに
を取り消してください。 CI を安全に使用するためのリファレンスを参照してください。

 ## 参照

 - `BUTLER_API_KEY` を使用した CI/CD (GitHub Actions/GitLab)、`broth` による自動インストール、
 の完全なフラグ リスト、および更新チェック API については、`references/butler-ci.md` を参照してください。
- 主要ドキュメント: バトラー マニュアル — `itch.io/docs/butler` (インストール、ログイン、プッシュ)。

 ## 関連スキル

 - `steam-publish` — SteamPipe 経由で Steam 上にある同じゲーム (多くの場合、itch.io と一緒に出荷されます)。
- `game-jam` — ほとんどのジャムは itch.io でホストされています。このスキルはアップロード手順を処理します。
- `prototype-fast` — プレイテスト用に、ドラフト/制限付きのページで初期のプロトタイプを共有します。 
