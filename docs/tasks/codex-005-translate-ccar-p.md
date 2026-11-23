# codex-005：CCAR-P の全228問を和訳する

- 状態：未着手
- 担当：Codex
- ブランチ：`content/translate-ccar-p`（作成済み。`main` の `06e2980`（CCDV-F の残り91問のマージ後）から作り、この指示書だけをコミットしてある）
- 作業フォルダ：`~/repos/claude-code-training.codex`（Codex 用の worktree）
- 前提：`AGENTS.md`、`docs/data-format.md`、`docs/translation-guide.md`、`docs/glossary.md` を読んでいること。進め方は `docs/tasks/codex-004-translate-ccdv-f-rest.md` と同じです

## 背景

CCDV-F の180問は、すべて訳し終わりました。次は **CCAR-P の228問（7分野）を、この1つのブランチで**和訳します。
これが終わると、2つの試験の408問がすべて訳済みになります。
（「1つのブランチでは1つの作業」の「1つの作業」は、今回は「CCAR-P の和訳」です）

## 始めかた

```bash
cd ~/repos/claude-code-training.codex
git status                        # 変更が残っていないことを確認する
git switch content/translate-ccar-p
git log --oneline -3              # 先頭がこの指示書のコミットであることを確認する
```

- 前の作業ブランチ `content/translate-ccdv-f-rest` は `main` にマージ済みです。そのままにしておいてかまいません（削除はユーザーが判断します）。
- 作業の途中で `main` が更新されたら、`git merge main` で取り込みます。

## やること

CCAR-P の7分野の `ja` を埋め、`ja.status` を `draft` にします。**上から順に**進めます（本番での配分が大きい順）。

| 順 | 分野 | 配分 | 問題数 | 内訳 |
|---|---|---|---|---|
| 1 | d3 Integration | 19% | 43 | single 31、multi 12 |
| 2 | d1 Solution Design & Architecture | 17% | 39 | single 28、multi 11 |
| 3 | d4 Evaluation, Testing & Optimization | 16% | 36 | single 26、multi 10 |
| 4 | d5 Governance, Safety & Risk Management | 14% | 32 | single 23、multi 9 |
| 5 | d6 Stakeholder Communication & Lifecycle Management | 14% | 32 | single 23、multi 9 |
| 6 | d2 Claude Models, Prompting & Context Engineering | 13% | 30 | single 22、multi 8 |
| 7 | d7 Developer Productivity & Operational Enablement | 7% | 16 | single 12、multi 4 |
| | **合計** | | **228** | **single 165、multi 63** |

- 和訳のしかたは `docs/translation-guide.md` に従います。特に「1. いちばん大事なこと」（ヒントを足さない、選択肢の長さのバランスを崩さない、意味を変えない）を守ってください。
- 訳語は `docs/glossary.md` に合わせます。CCDV-F で追加した訳語も使い、試験をまたいで訳語をそろえます。新しく訳した用語は glossary に追記します。分野名の訳は `data/exams/ccar-p.json` の `name.ja` に合わせます。
- 訳の例は、和訳済みの `data/questions/ccdv-f/` です。
- `en`、ID、正解、`subdomain`、`tags`、出典など、`ja` 以外のフィールドは変更しません。CCDV-F の問題も変更しません（訳語の不統一に気づいたら、直さずに作業メモに書きます）。
- `reviewed` は付けません（ユーザーが確認してから付けます）。

### CCAR-P で CCDV-F と違うところ

- **全228問の `en.explanation` が空（`""`）です。** そのため `ja.explanation` も `""` にします。各選択肢の `note`（理由）が解説の代わりになるので、`note` は4つとも訳を空にしません。
- **`note` も長さのバランスに気をつけます。** 解説がない分、`note` が答え合わせの中心になります。正解の選択肢の `note` だけを丁寧に訳して長くしないでください。
- **複数選択の問題（63問）は、問題文の最後が「Select 2 answers.」「Select 3 answers.」です**（2つ選択が48問、3つ選択が15問）。CCDV-F の「(Select 2)」と同じく、文末を「（2つ選択）」「（3つ選択）」にします。数は `select` の値と一致させます。
  - 例：「Which actions turn the request into defensible architectural constraints? Select 2 answers.」→「要求を根拠のあるアーキテクチャ上の制約に落とし込む行動はどれですか？（2つ選択）」
- 問題文が長く、業務の条件（予算、契約、監査、承認の手順など）が細かく書かれています。条件を落としたり、まとめたりせずに訳してください。条件の1つが正解を決める手がかりになっていることがあります。

### 原文の誤りや、補足が必要そうな問題

- 原文（`en`）の誤りに気づいても、`en` も訳も直しません。下の「作業メモ」に問題 ID と内容を書きます。
- 説明が足りない・紛らわしい問題があっても、**`supplement` は書きません**。作業メモに「補足の候補」として、問題 ID と理由を書いてください。補足の文面はユーザーが確認してから決めます（`docs/data-format.md` の「2-4」）。
- **用語の補足も、まだ書きません。** CCDV-F では、temperature、few-shot、top_p、p95、p99、OCR、SKU、CI、I/O、base64、extended thinking、Plan mode、Headless mode の13用語に補足を付けました（文面は CCDV-F の各問題の `supplement` にあります）。CCAR-P でこれらの用語が出てくる問題は、作業メモに用語ごとの問題 ID を書いておいてください。同じ文面を使うかどうかは、ユーザーが決めます。
- 上の13用語以外で、名前だけでは意味が分かりにくい英語の用語・略語にも気づいたら、同じように作業メモに書きます。

### 並行作業での注意

- 変更してよいのは、`data/questions/ccar-p/`、`docs/glossary.md`、この指示書の「状態」と「作業メモ」だけです。
- `app/`、`schema/`、`tools/validate.py`、`tools/build.py`、`tests/` は Claude Code の担当です。`./dev check` がこれらの側の理由で失敗したら、直さずに作業メモに書いて、ユーザーに伝えてください。
- `./dev serve` でアプリを確認する場合は、worktree の `.env` のとおり **8001番**（http://localhost:8001）を使います。

## 確認

各分野を終えるたびに、次の2つを実行します。

```bash
./dev check
./dev validate --strict-counts
```

- 加えて、codex-004 と同じように、変更前の全408問を `.cache/` に保存しておき、**訳した問題の `ja` 以外のフィールドが変わっていないこと**と、**他の問題（CCDV-F、未着手の分野）がバイト単位で変わっていないこと**を照合してください。

**完了の条件**：CCAR-P の228問がすべて `draft`（2つの試験の408問すべてが訳済み）で、上の確認がすべてエラー0件で通ること。

## コミット

- **分野ごとに1コミット**にします（例：「CCAR-P d3 を和訳（43問）」）。
- 各コミットの前に、上の「確認」を通します。途中で作業が止まっても、コミット済みの分野は残るようにするためです。
- この指示書の「状態」と「作業メモ」の更新も、このブランチでコミットします。分野が終わるたびに、下の表の「状態」も更新してください。
- push と `main` へのマージはしません。7分野がすべて終わったら、ユーザーにマージを依頼します。
- 途中の分野まででマージしたいとユーザーから言われたら、その時点までのコミットでマージを依頼してかまいません。

## 作業メモ（Codex が書く）

| 順 | 分野 | 状態 | 問題数 | コミット | メモ |
|---|---|---|---|---|---|
| 1 | d3 | 未着手 | 43 | | |
| 2 | d1 | 未着手 | 39 | | |
| 3 | d4 | 未着手 | 36 | | |
| 4 | d5 | 未着手 | 32 | | |
| 5 | d6 | 未着手 | 32 | | |
| 6 | d2 | 未着手 | 30 | | |
| 7 | d7 | 未着手 | 16 | | |
