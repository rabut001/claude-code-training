# codex-003：CCDV-F d5 を和訳する

- 状態：未着手
- 担当：Codex
- ブランチ：`content/translate-ccdv-f-d5`（作成済み。`main` の `5237bad` から作成し、この指示書だけをコミットしてある）
- 作業フォルダ：`~/repos/claude-code-training.codex`（Codex 用の worktree）
- 前提：`AGENTS.md`、`docs/data-format.md`、`docs/translation-guide.md`、`docs/glossary.md` を読んでいること。進め方の全体は `docs/tasks/codex-002-translate.md` と同じです

## 背景

Claude Code は `app/ui-fixes` ブランチでアプリの UI を見直しています。
Codex はそれと**並行して**、和訳を次の分野へ進めます。
編集する場所が分かれている（Claude Code は `app/` など、Codex は `data/questions/` など）ので、ぶつかりません。

## 始めかた

Codex 用の worktree の中で、作成済みのブランチに切り替えます。

```bash
cd ~/repos/claude-code-training.codex
git status                        # 変更が残っていないことを確認する
git switch content/translate-ccdv-f-d5
git log --oneline -3              # 先頭がこの指示書のコミットであることを確認する
```

- 前の作業ブランチ `content/translate-ccdv-f-d2` は `main` にマージ済みです。そのままにしておいてかまいません（削除はユーザーが判断します）。
- 作業の途中で `main` が更新されたら、`git merge main` で取り込みます。

## やること

`data/questions/ccdv-f/d5/` の **30問**（`ccdvf-bz-d5-001`〜`030`。single 29問、multi 1問）の `ja` を埋め、`ja.status` を `draft` にします。

- 和訳のしかたは `docs/translation-guide.md` に従います。特に「1. いちばん大事なこと」（ヒントを足さない、選択肢の長さのバランスを崩さない、意味を変えない）を守ってください。
- 訳語は `docs/glossary.md` に合わせます。d2 で追加した訳語（指数バックオフ、冪等性、較正など）も使います。新しく訳した用語は glossary に追記します。
- 訳の例は `tests/fixtures/questions/ccdv-f/` の2問と、和訳済みの `data/questions/ccdv-f/d2/` です。
- `en`、ID、正解、出典など、`ja` 以外のフィールドは変更しません。
- `reviewed` は付けません（ユーザーが確認してから付けます）。

### 原文の誤りや、補足が必要そうな問題

- 原文（`en`）の誤りに気づいても、`en` も訳も直しません。下の「作業メモ」に問題 ID と内容を書きます。
- 説明が足りない・紛らわしい問題があっても、**`supplement` は書きません**。作業メモに「補足の候補」として、問題 ID と理由を書いてください。補足の文面はユーザーが確認してから決めます（`docs/data-format.md` の「2-4」）。

### 並行作業での注意

- 変更してよいのは `data/questions/ccdv-f/d5/`、`docs/glossary.md`、この指示書の「状態」と「作業メモ」だけです。
- `app/`、`schema/`、`tools/validate.py`、`tools/build.py`、`tests/` は Claude Code の担当です。`./dev check` がこれらの側の理由で失敗したら、直さずに作業メモに書いて、ユーザーに伝えてください。
- `./dev serve` でアプリを確認する場合は、worktree の `.env` のとおり **8001番**（http://localhost:8001）を使います。Claude Code は 8000番を使っています。

## 確認

```bash
./dev check
./dev validate --strict-counts
```

**完了の条件**：d5 の30問がすべて `draft` で、上の2つがエラー0件で通ること。

## コミット

- 和訳は1コミットにします（例：「CCDV-F d5 を和訳（30問）」）。
- この指示書の「状態」と「作業メモ」の更新も、同じブランチでコミットします（和訳と同じコミットでも、別のコミットでもかまいません）。
- push と `main` へのマージはしません。終わったらユーザーにマージを依頼します。
- 次の分野（CCDV-F d1、26問）は、この分野がマージされたあとに、ユーザーの指示で始めます。

## 作業メモ（Codex が書く）

（やったこと、問題数、新しく追加した訳語の数、原文の誤り、補足の候補、`./dev check` の結果を書く）
