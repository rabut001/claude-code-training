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

以下は原文を読んで見つけた確認候補で、外部資料との照合による正誤判定はしていない。原文・正解は変更せず、訳でも意味を修正していない。`supplement` は追加していない。

- `ccdvf-bz-d5-012`：選択肢 a の理由は、max_tokens の増加と extended thinking の有効化が「どちらもレイテンシを増やす」と述べている。max_tokens の上限と実際の生成量の関係、設問で問う最初のトークンまでの時間との関係が省略されているため、補足の候補。013では未使用の上限分は課金されないと説明している。
- `ccdvf-bz-d5-018`：設問には必要な最低正答率が書かれていないが、正解 c と解説は97%で品質要件を満たすと扱っている。要件の前提を明確にする補足の候補。訳で最低正答率を追加していない。
- `ccdvf-bz-d5-024`：「絶対に予算を超えない」要件に対し、正解 a は使い切った後の拒否を述べるだけで、発行予定リクエストの消費量や同時実行時の扱いを説明していない。厳格な予算管理の実装条件を明確にする補足の候補。
- `ccdvf-bz-d5-028`：正解 b は「失敗するか、出力が途切れる」としているが、対象モデルや超過時の挙動の条件が特定されていない。どの挙動を想定するかを明確にする補足の候補。
- `ccdvf-bz-d5-029`：選択肢 d の理由は、免責事項について「責任を転嫁する」と一律に述べている。原文にはその裏付けや適用条件が示されていないため、技術的な正確さへの効果と責任についての主張を区別する補足の候補。

### 受け渡し

- 和訳30問、用語集、この指示書の更新を1コミットにまとめる。push と `main` へのマージは実施しない。
- ユーザーによるレビューと `main` へのマージ待ち。次の CCDV-F d1 は、マージ後にユーザーの指示を受けてから開始する。
