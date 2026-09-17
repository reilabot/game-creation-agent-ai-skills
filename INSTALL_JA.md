# Game Dev Super Stack 導入指示（日本語）

この文書は、人間向け説明であると同時に、AIコーディングエージェントへそのまま渡せる完全な導入指示です。対象ゲームプロジェクトのルートでAIにこの文書のURLまたは全文を渡し、次のように依頼してください。

```text
このINSTALL_JA.mdを最後まで読み、記載された安全条件を守って、現在のゲームプロジェクトへGame Dev Super Stackを導入・検証してください。
```

## AIへの実行指示

あなたは現在のゲームプロジェクトへGame Dev Super Stackを導入します。設計案だけで終了せず、取得、配置、既存内容との安全な統合、検証まで実行してください。

配布元:

```text
https://github.com/reilabot/game-creation-agent-ai-skills
```

### 安全条件

1. 作業前にプロジェクトルート、`AGENTS.md`、`.agents/`、`scripts/`、`tests/`、未コミット変更を確認する。
2. 既存ファイルを無条件で上書きしない。同名ファイルが異なる場合は差分を確認し、既存内容を保持して統合する。
3. `.env`、認証情報、DB、セーブデータ、秘密鍵、独自ゲームコードを配布元へ送信しない。
4. ダウンロードは一時ディレクトリへ行い、配布元のゲーム開発Stack関連ファイルだけを対象プロジェクトへ移す。
5. `AGENTS.md`が既にある場合は置換せず、Game Dev Super Stack用の指示だけを統合する。
6. 導入後にvalidatorを実行し、失敗を隠さない。

### 取得

Gitが利用可能なら、一時ディレクトリへcloneします。

```bash
git clone --depth 1 https://github.com/reilabot/game-creation-agent-ai-skills.git <temporary-directory>
```

Gitがなければ、次のアーカイブを一時ディレクトリへ取得・展開します。

```text
https://github.com/reilabot/game-creation-agent-ai-skills/archive/refs/heads/main.zip
```

### 対象プロジェクトへ配置

一時展開した配布物から、次だけを対象プロジェクトへ統合します。

```text
.agents/
scripts/build_gamedev_stack.py
scripts/gamedev_router.py
scripts/install_stack.py
scripts/validate_stack.py
tests/router-fixtures.json
docs/
LICENSE
LICENSES/
ORIGINAL_SKILLS_LICENSE.en.md
ORIGINAL_SKILLS_LICENSE.ja.md
TERMS_OF_USE.en.md
TERMS_OF_USE.ja.md
THIRD_PARTY_NOTICES.md
```

`AGENTS.md`には、次のプロジェクト指示を既存内容と両立する形で追加します。

```markdown
## Game Dev Super Stack

- For substantial game work, begin with `.agents/skills/game-studio-director/SKILL.md`.
- Analyze the project, confirm or select the language, and route only the necessary engine and cross-cutting skills.
- Keep simulation truth separate from presentation and connect feedback systems through explicit contracts.
- Finish playable increments with `game-qa-playtest` and `gamedev-quality-gate`.
- Require explicit approval before publishing, deployment, purchases, credential use, or production/player-data mutation.
```

### AIクライアント別の認識

正本は常に`.agents/skills/`です。

- OpenAI Codex: `.agents/skills/`と`AGENTS.md`を使用する。
- Cursor: `.agents/skills/`をプロジェクトSkillとして使用する。
- Gemini CLI: `.agents/skills/`を使用し、`/skills`で確認する。
- Google Antigravity: `.agents/skills/`をworkspace Skillとして使用する。
- GitHub Copilot: `.agents/skills/`をプロジェクトSkillとして使用する。
- Claude Code: 環境が`.agents/skills/`を検出しない場合だけ、`.claude/skills`から`.agents/skills`へのjunctionまたはsymlinkを作る。Skillを複製しない。
- その他: Agent Skills対応AIの探索先へ`.agents/skills`を登録する。

### 検証

対象プロジェクトのルートで実行します。

```bash
python scripts/validate_stack.py
```

成功条件:

```text
skills=109 fixtures=17 errors=0
```

Routerも確認します。

```bash
python scripts/gamedev_router.py "four-player online survival crafting game with a dedicated server" --engine unreal
```

結果に`engine`、`language_selection`、`skills`、`roles`、`model_classes`、`tools`、`dependency_order`が含まれることを確認します。

### 完了報告

AIは最後に次を報告してください。

1. 導入先のプロジェクト相対パス
2. 新規作成・統合したファイル
3. Skill数とfixture数
4. validator結果
5. 既存ファイルとの競合と統合内容
6. 利用するAIでSkillが認識されたか
7. 残る制限または手動操作

`skills=109 fixtures=17 errors=0`を確認できない場合は、導入完了と報告しないでください。
