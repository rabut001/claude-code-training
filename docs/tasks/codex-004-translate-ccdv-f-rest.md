# codex-004：CCDV-F の残り（6分野・91問）を和訳する

- 状態：未着手
- 担当：Codex
- ブランチ：`content/translate-ccdv-f-rest`（作成済み。`main` の `c173813`（d5 のマージ後）から作り、この指示書だけをコミットしてある）
- 作業フォルダ：`~/repos/claude-code-training.codex`（Codex 用の worktree）
- 前提：`AGENTS.md`、`docs/data-format.md`、`docs/translation-guide.md`、`docs/glossary.md` を読んでいること。進め方は `docs/tasks/codex-003-translate-ccdv-f-d5.md` と同じです

## 背景

これまでは1分野ごとにブランチを分けていましたが、今回は **CCDV-F の残りの6分野を、この1つのブランチで**和訳します。
これが終わると、CCDV-F の180問がすべて訳済みになります。
（「1つのブランチでは1つの作業」の「1つの作業」は、今回は「CCDV-F の残りの和訳」です）

Claude Code は、`app/ui-fixes` ブランチで UI の見直しを並行して進めています。

## 始めかた

```bash
cd ~/repos/claude-code-training.codex
git status                        # 変更が残っていないことを確認する
git switch content/translate-ccdv-f-rest
git log --oneline -3              # 先頭がこの指示書のコミットであることを確認する
```

- 前の作業ブランチ `content/translate-ccdv-f-d5` は `main` にマージ済みです。そのままにしておいてかまいません（削除はユーザーが判断します）。
- 作業の途中で `main` が更新されたら、`git merge main` で取り込みます。

## やること

次の6分野の `ja` を埋め、`ja.status` を `draft` にします。**上から順に**進めます（本番での配分が大きい順）。

| 順 | 分野 | 問題数 | 内訳 |
|---|---|---|---|
| 1 | d1 Agents and Workflows | 26 | single 25、multi 1 |
| 2 | d6 Prompt and Context Engineering | 20 | single 19、multi 1 |
| 3 | d8 Tools and MCPs | 19 | single 18、multi 1 |
| 4 | d7 Security and Safety | 15 | single 14、multi 1 |
| 5 | d3 Claude Code | 6 | single 6 |
| 6 | d4 Eval, Testing, and Debugging | 5 | single 5 |
| | **合計** | **91** | |

- 和訳のしかたは `docs/translation-guide.md` に従います。特に「1. いちばん大事なこと」（ヒントを足さない、選択肢の長さのバランスを崩さない、意味を変えない）を守ってください。
- 訳語は `docs/glossary.md` に合わせます。d2・d5 で追加した訳語も使い、分野をまたいで訳語をそろえます。新しく訳した用語は glossary に追記します。
- 訳の例は `tests/fixtures/questions/ccdv-f/` の2問と、和訳済みの `data/questions/ccdv-f/d2/`・`d5/` です。
- `en`、ID、正解、出典など、`ja` 以外のフィールドは変更しません。和訳済みの d2・d5 も変更しません（訳語の不統一に気づいたら、直さずに作業メモに書きます）。
- `reviewed` は付けません（ユーザーが確認してから付けます）。

### 原文の誤りや、補足が必要そうな問題

- 原文（`en`）の誤りに気づいても、`en` も訳も直しません。下の「作業メモ」に問題 ID と内容を書きます。
- 説明が足りない・紛らわしい問題があっても、**`supplement` は書きません**。作業メモに「補足の候補」として、問題 ID と理由を書いてください。補足の文面はユーザーが確認してから決めます（`docs/data-format.md` の「2-4」）。

### 並行作業での注意

- 変更してよいのは、`data/questions/ccdv-f/` の上の6分野（`d1`、`d3`、`d4`、`d6`、`d7`、`d8`）、`docs/glossary.md`、この指示書の「状態」と「作業メモ」だけです。
- `app/`、`schema/`、`tools/validate.py`、`tools/build.py`、`tests/` は Claude Code の担当です。`./dev check` がこれらの側の理由で失敗したら、直さずに作業メモに書いて、ユーザーに伝えてください。
- `./dev serve` でアプリを確認する場合は、worktree の `.env` のとおり **8001番**（http://localhost:8001）を使います。

## 確認

各分野を終えるたびに、次の2つを実行します。

```bash
./dev check
./dev validate --strict-counts
```

**完了の条件**：6分野の91問がすべて `draft`（CCDV-F の180問すべてが訳済み）で、上の2つがエラー0件で通ること。

## コミット

- **分野ごとに1コミット**にします（例：「CCDV-F d1 を和訳（26問）」）。d3 と d4 は1コミットにまとめてもかまいません（「CCDV-F d3・d4 を和訳（11問）」）。
- 各コミットの前に、上の「確認」を通します。途中で作業が止まっても、コミット済みの分野は残るようにするためです。
- この指示書の「状態」と「作業メモ」の更新も、このブランチでコミットします。分野が終わるたびに、下の表の「状態」も更新してください。
- push と `main` へのマージはしません。6分野がすべて終わったら、ユーザーにマージを依頼します。
- 途中の分野まででマージしたいとユーザーから言われたら、その時点までのコミットでマージを依頼してかまいません。

## 作業メモ（Codex が書く）

| 順 | 分野 | 状態 | 問題数 | コミット | メモ |
|---|---|---|---|---|---|
| 1 | d1 | 未着手 | 26 | | |
| 2 | d6 | 未着手 | 20 | | |
| 3 | d8 | 未着手 | 19 | | |
| 4 | d7 | 未着手 | 15 | | |
| 5 | d3 | 未着手 | 6 | | |
| 6 | d4 | 未着手 | 5 | | |

（分野ごとに、やったこと、新しく追加した訳語の数、原文の誤り、補足の候補、`./dev check` の結果を書く）
