# codex-003：CCDV-F d5 を和訳する

- 状態：完了
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

### 作業結果（2026-11-23）

- `content/translate-ccdv-f-d5` の Codex 用 worktree で作業した。開始時の `git merge main` は `Already up to date.` で、開始時の HEAD は指示書のコミット `c1a930c`。
- `ccdvf-bz-d5-001`〜`030` の30問（single 29問、multi 1問）について、問題文、選択肢、選択肢ごとの理由、全体解説を和訳し、すべて `ja.status: draft` にした。`reviewed` は付けていない。
- `docs/glossary.md` に27行を追加した。貪欲デコーディング、ロジット、過学習、思考トークン、モデル階層などの訳語を整理した。
- 全30問を変更前のスナップショットと照合し、`ja` 以外の全フィールド（`en`、ID、正解、出典、参考資料など）が完全一致することを確認した。選択肢の数・ID・順序、理由と解説の空欄の対応、識別子とバッククォート、UTF-8・2スペース・末尾改行も確認した。
- 全問の訳を原文と見直し、数値・割合・条件を保持した。選択肢の長さは原文に対する比率でも確認し、006 と029の表現を調整した。識別子の英語表記と、翻訳ガイドで認められた human-in-the-loop の初出の括弧説明による長さの違いは残している。正解だけに説明は足していない。
- 確認結果：Docker 内で `./dev check` 成功（32テスト、データ検証、ビルド）。`./dev validate --strict-counts` も成功し、CCDV-F 180問・CCAR-P 228問を維持している。全体では訳済み89問、未訳319問。`git diff --check` も成功。
- 実行環境：サンドボックス内では Docker ソケットへの接続が拒否されたため、承認付き実行で Docker を使用した。Python の処理はすべて Docker 内で行った。
- 作業用の訳案、変更前のスナップショット、反映・照合スクリプトは `.cache/d5-translations.json`、`.cache/d5-original/`、`.cache/apply_d5_translation.py`、`.cache/verify_d5_translation.py` に保存した（管理対象外）。訳案ファイルは初稿であり、最終の訳は `data/questions/ccdv-f/d5/` の JSON を参照する。`app/data/` はビルドによる生成物で、手動編集・コミットしていない。

### 原文の留意点・補足の候補

以下は当初の和訳時に原文を読んで見つけた確認候補で、外部資料との照合による正誤判定はしていない。当初の和訳では原文・正解・訳の意味を保持し、`supplement` は追加しなかった。後続のユーザーレビューによる結論は各項目と `codex-004-translate-ccdv-f-rest.md` の作業メモに記録する。

- 確認終了（ユーザーレビュー）：`ccdvf-bz-d5-012` は、応答開始までの時間を短くする方法を問う問題であり、max_tokens の増加がその対策にはならないことから、追加の補足は不要と判断した。既存の few-shot・extended thinking の用語説明は保持する。
- 確認終了（ユーザーレビュー）：`ccdvf-bz-d5-018` は、最低正答率の前提について根拠の取れない補足を加えることを避け、ユーザーの判断により現状を維持する。「97%なら一般に十分」「97%が限界」などの一般論を確認済みの事実としては扱わない。
- 確認終了（ユーザーレビュー）：`ccdvf-bz-d5-024` は、事前の消費量確認・確保について原文の想定を裏付けられないため、ユーザーの判断により追加の補足は作成せず、現状を維持する。
- 対応済み（ユーザーレビュー）：`ccdvf-bz-d5-028` に、残り容量2万トークンに達する前に回答が完了すれば正常終了するモデルもあることを日英で補足した。送信時に拒否するモデルもあるため、「2万を超える場合のみエラー」とは限定せず、受付時の拒否と生成中の停止を区別した。
- 対応済み（ユーザーレビュー）：`ccdvf-bz-d5-029` に、注意書きを表示するだけでは存在しない判例の生成そのものを減らせない、という問題の要点を日英で補足した。免責表示による法的な効果について新たな断定は加えず、既存の temperature の用語説明を保持した。

### 受け渡し

- 和訳30問、用語集、この指示書の更新を1コミットにまとめる。push と `main` へのマージは実施しない。
- ユーザーによるレビューと `main` へのマージ待ち。次の CCDV-F d1 は、マージ後にユーザーの指示を受けてから開始する。
