# codex-002：問題を和訳する

- 状態：完了（本ブランチの対象：CCDV-F d2 の59問。他分野の和訳は未着手）
- 担当：Codex
- ブランチ：分野ごとに `content/translate-<exam>-<domain>`（例：`content/translate-ccdv-f-d2`）。Codex 用の worktree の中で `git switch -c content/translate-<exam>-<domain> main` として作る
- 作業フォルダ：`~/repos/claude-code-training.codex`（Codex 用の worktree）
- 前提：`AGENTS.md`、`docs/data-format.md`、`docs/translation-guide.md`、`docs/glossary.md` を読んでいること

## やること

`data/questions/` の各問題の `ja` を埋めて、`status` を `draft` にします。

### 進める順番

本番での配分が大きい分野から進めます。1つの分野が終わるごとにコミットします。

| 順 | 試験 | 分野 | 問題数（予定） |
|---|---|---|---|
| 1 | ccdv-f | d2 Applications and Integration | 59 |
| 2 | ccdv-f | d5 Model Selection and Optimization | 30 |
| 3 | ccdv-f | d1 Agents and Workflows | 26 |
| 4 | ccdv-f | d6 Prompt and Context Engineering | 20 |
| 5 | ccdv-f | d8 Tools and MCPs | 19 |
| 6 | ccdv-f | d7 Security and Safety | 15 |
| 7 | ccdv-f | d3 Claude Code / d4 Eval, Testing, and Debugging | 6 / 5 |
| 8 | ccar-p | d3 → d1 → d4 → d5 → d6 → d2 → d7 | 43 / 39 / 36 / 32 / 32 / 30 / 16 |

（問題数は元データの数です。取り込みの結果と違っていたら、取り込みの結果に従います）

### 和訳のしかた

- `docs/translation-guide.md` に従います。特に「1. いちばん大事なこと」（ヒントを足さない、選択肢の長さのバランスを崩さない、意味を変えない）を守ってください。
- 訳の例は `tests/fixtures/questions/ccdv-f/` にある2問を参考にしてください。
- `en` は変更しません。原文の誤りに気づいたら、作業メモに書きます。
- 新しく訳した用語は `docs/glossary.md` に追記します。

### 確認

```bash
./dev check
```

**完了の条件**：その分野の全問が `draft` になっていて、`./dev check` がエラー0件で通ること。

### コミット

- 分野ごとに1コミットにします（例：「CCDV-F d2 を和訳（59問）」）。
- 変更してよいのは `data/questions/`、`docs/glossary.md`、この指示書の「状態」と「作業メモ」だけです。
- 指示書の「状態」と「作業メモ」の更新も、同じブランチでコミットします（和訳と同じコミットでも、別のコミットでもかまいません）。

## 作業メモ（Codex が書く）

| 試験 | 分野 | 状態 | 問題数 | メモ |
|---|---|---|---|---|
| ccdv-f | d2 Applications and Integration | 完了 | 59 | 全問 `draft`。検証済み。作業完了をユーザー確認済み。`main` へのマージ待ち |

### CCDV-F d2（2026-11-23）

- 作業ブランチ：`content/translate-ccdv-f-d2`。Codex 用 worktree 内で `git merge main` を実行し、ローカル `main` と同じ `b5cce46` から開始した。
- `ccdvf-bz-d2-001`〜`ccdvf-bz-d2-059` の59問（single 55問、multi 4問）について、問題文、選択肢、各選択肢の理由、全体解説を和訳し、全問の `ja.status` を `draft` にした。`reviewed` は付けていない。
- `docs/glossary.md` に、指数バックオフ、冪等性、較正、データレジデンシーなど57行を追記した。機能名の extended thinking と、原文の識別子・ファイル名は英語のまま保持した。
- 全59問を開始時のコミットと照合し、`ja` 以外の全フィールド（`en`、ID、正解、出典など）が完全一致することを確認した。選択肢の数・ID・順序、理由と解説の空欄の対応、識別子・数値・バッククォートの保持、UTF-8・2スペース・末尾改行も確認した。
- 選択肢の長さを原文に対する比率でも見直し、説明を足さずに一部の表現を簡潔にした。045 の正解には長い設定ファイル名が2つあるため、英語の識別子の保持による比率の違いは残した。追加のヒントは入れていない。
- 最終確認：Docker 内で `./dev check` 成功（23テスト、データ検証、ビルド）。`./dev validate --strict-counts` も成功し、CCDV-F 180問・CCAR-P 228問を維持している。全体の訳済みは59問、未訳は349問。
- 実行環境：サンドボックス内では Docker ソケットへの接続が拒否されたため、初期確認には AGENTS.md で認められたホスト Python の代替手順を使用した。その後、権限付き実行で Docker を利用できたため、最終確認は Docker 内で実施した。
- 原文の留意点：`ccdvf-bz-d2-039` の選択肢 c は誤答扱いだが、その `note` は処理量の増加もワークフローを支持すると説明している。設問は「最も明確に」支持する要件を問うため正解 a と直ちに矛盾するとまでは断定しないが、誤答理由の明確さに確認の余地がある。英文、正解、和訳での意味は変更していない。
- 照合用の原文スナップショットとスクリプトは `.cache/d2-original/`、`.cache/verify_d2_translation.py` に保存した（管理対象外）。`app/data/` は `./dev check` が生成したもので、手動編集・コミットしていない。
- 次の分野は CCDV-F d5（30問）。この分野のユーザーレビュー・マージ後、更新された `main` から次の分野用ブランチを作る。
- 本体コミット：`8e0f83b`「CCDV-F d2 を和訳（59問）」。対象は、指示書どおり d2 の問題59ファイルと `docs/glossary.md` のみ。この指示書の状態・作業メモは、今回に限る例外としてユーザーの指示により別コミットに収録する。コミット対象のルールは変更しない。push・`main` へのマージは実施していない。
