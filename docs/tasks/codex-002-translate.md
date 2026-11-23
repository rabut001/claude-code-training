# codex-002：問題を和訳する

- 状態：未着手（codex-001 が `main` にマージされてから始める）
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
- `data/questions/` と `docs/glossary.md` 以外は変更しません。

## 作業メモ（Codex が書く）

| 試験 | 分野 | 状態 | 問題数 | メモ |
|---|---|---|---|---|
| | | | | |
