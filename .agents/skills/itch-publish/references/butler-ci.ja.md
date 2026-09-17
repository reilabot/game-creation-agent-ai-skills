# butler: CI/CD、完全なフラグ参照、および更新チェック API

 `itch-publish` の深さ。自動アップロード、完全な `butler push` フラグ
の設定、およびプレーヤーへの更新の通知については、これをお読みください。主要ドキュメント
[the butler manual](https://itch.io/docs/butler) (インストール、ログイン、プッシュ) に対して検証します。

 ## 1. CI の認証 (`BUTLER_API_KEY`)

 インタラクティブ `butler login` はブラウザを開きます。CI では役に立ちません。代わりに、
 **`BUTLER_API_KEY`** 環境変数を設定すると、バトラーはそれを自動的に使用します。

 キーの取得場所:
- `butler login` をローカルで 1 回実行し、creds ファイルから読み取ります:
- Linux: `~/.config/itch/butler_creds`
- macOS: `~/Library/Application Support/itch/butler_creds`
- Windows: `%USERPROFILE%\.config\itch\butler_creds`
- または、itch.io **API キー** ページ (`itch.io/user/settings/api-keys`) で生成します。
 関連キーのソースは `wharf` に設定されています。

 CI シークレットとして保存します。 **決して**印刷しないでください。パブリック ビルド ログに漏洩したキーは
に侵害されています。API キー ページですぐに取り消してください。

 ## 2. CI へのバトラーのインストール (ページ リンクではなく、`broth` を使用)

 `itchio.itch.io/butler` ダウンロード リンクは **期限切れ**であるため、ハードコードすることはできません。
の永久 **ブロス** URL を使用します。これは常にチャンネルの最新の安定したビルドを提供します:

```bash
# Example: latest stable Linux amd64 butler. Substitute the channel for your runner OS.
curl -L -o butler.zip "https://broth.itch.zone/butler/linux-amd64/LATEST/archive/default"
unzip butler.zip
chmod +x butler
./butler -V        # prints version; confirms it runs
```

一般的なブロス チャネル: `linux-amd64`、`windows-amd64`、`darwin-amd64`。 `-head` チャネル
は最先端です。他は安定しています。この zip には 2 つの 7-zip ヘルパー ライブラリも含まれています。
 は無害であり、`butler push` には必要ありません。

 ## 3. GitHub アクションの例

```yaml
name: Publish to itch.io
on:
  push:
    tags: ["v*"]            # publish when you tag a release
jobs:
  butler:
    runs-on: ubuntu-latest
    env:
      BUTLER_API_KEY: ${{ secrets.BUTLER_API_KEY }}   # set in repo secrets; never echoed
    steps:
      - uses: actions/checkout@v4
      # ... your build steps produce ./build/windows, ./build/linux, etc. ...
      - name: Install butler
        run: |
          curl -L -o butler.zip "https://broth.itch.zone/butler/linux-amd64/LATEST/archive/default"
          unzip butler.zip && chmod +x butler
      - name: Push builds
        run: |
          VERSION="${GITHUB_REF_NAME#v}"     # tag v1.2.0 -> 1.2.0
          ./butler push ./build/windows leafy/my-game:windows --userversion "$VERSION"
          ./butler push ./build/linux   leafy/my-game:linux   --userversion "$VERSION"
```

GitLab CI は同等です。マスクされた CI/CD 変数として `BUTLER_API_KEY` を設定し、ジョブ スクリプトで同じ
install + `butler push` コマンドを実行します。

 ## 4. `butler push` フラグのリファレンス (検証済み)

 |旗 |目的 |
|---|---|
| `--userversion <v>` | itch の自動インクリメント整数の代わりに、明示的なバージョン文字列を設定します。 |
| `--userversion-file <f>` |ファイルからバージョン文字列を読み取ります (単一行、UTF-8、BOM なし)。 |
| `--if-changed` |内容が最新のビルドと同一の場合は、プッシュをスキップします (no-op パッチを減らします)。 |
| `--hidden` |プッシュによって *新しい* チャネルが作成された場合のみ、アップロードを非表示にマークします。既存のもののエラー。 |
| `--ignore '<glob>'` |一致するファイルを除外します。繰り返し可能 (`--ignore '*.pdb' --ignore '*.dSYM'`)。ダッシュ 2 つ。 |
| `--dry-run` |プッシュされるすべてのファイルをリストします (+ 概要)。何もアップロードしません。 |
| `--no-auto-unzip` |単一の `.zip` フォルダーを、解凍する代わりに 1 つの不透明なファイルとしてプッシュします。 |
| `--dereference` |シンボリックリンクをたどり、そのターゲットのコピーをアップロードします (より大きなビルド。注意して使用してください)。 |
| `--fix-permissions` |ウォーク中にファイルのアクセス許可を正規化します。 |
| `--auto-wrap` |プッシュする前に、単一のルース ファイルをフォルダーにラップします。 |

 関連コマンド:

 |コマンド |目的 |
|---|---|
| `butler login` / `butler logout` |ローカル認証情報を承認/クリアします (ブラウザー フロー)。 |
| `butler version` |バトラーのバージョンを出力します (インストール + PATH を確認します)。 |
| `butler which` |実行中のバトラー バイナリへのフル パスを出力します。 |
| `butler status <user>/<game>` |チャネルとその最新のビルド/バージョンをリストします。 |
| `butler push-preview <dir> <user>/<game>:<ch>` | `NEW/MODIFIED/DELETED/SAME` と最後のビルドを比較します。 `--changes-only` を追加して未変更を非表示にします。何もアップロードしません。 |
| `butler upgrade` | Butler本体を最新版にアップデートしてください。 |

 注:
- 処理: プッシュ後、ビルドは高速な「デフォルト」パッチを介してすぐにライブになります。次に、itch.io
は、最適化された (より小さい) パッチをバックグラウンドで再生成します。どちらも
プレーヤーには透過的です。
- リモート/SSH ホストからの作業: `butler login` は URL を出力します。それをローカルで開き、
 リダイレクトされた (非ロード) ページのアドレスをコピーして、ターミナルに貼り付け直します。

 ## 5. プレーヤーに更新を通知します (認証は必要ありません)

 (itch アプリ経由ではなく) 直接ダウンロードしたプレーヤーは自動更新されません。チャンネルの最新の
ユーザー バージョンをクエリし、ゲーム内でプロンプトを表示します:

```text
GET https://api.itch.io/wharf/latest?target=<user>/<game>&channel_name=<channel>
# or by numeric game_id (from the Edit game page URL):
GET https://api.itch.io/wharf/latest?game_id=<id>&channel_name=<channel>

Response: { "latest": "1.2.0" }   // omitted if the latest build has no user-version
```

`latest` をビルドのバージョン (`--userversion` でプッシュ) と比較し、
 の「アップデートが利用可能」メッセージを表示します。プライベート ゲームは、
 未リリース タイトルの漏洩を避けるために「無効なゲーム」エラーを返します。 
