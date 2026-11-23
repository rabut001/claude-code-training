# codex-001：英語の問題を取り込む

- 状態：完了
- 担当：Codex
- ブランチ：`content/import`
- 作業フォルダ：`~/repos/claude-code-training.codex`（Codex 用の worktree。作成済みで、`content/import` がチェックアウトされています）
- 前提：`AGENTS.md`（特に「作業フォルダ（git worktree）」）、`docs/data-format.md` を読んでいること

作業はすべて上の作業フォルダの中で行います。統合用のフォルダ（`~/repos/claude-code-training`）では作業しません。
始める前に `git merge main` で最新の `main` を取り込んでください。

## やること

2つの元リポジトリから英語の問題を取り込み、`data/questions/` に1問1ファイルで出力します。
**和訳はこのタスクではしません**（すべて `"ja": { "status": "todo" }` にします）。和訳は codex-002 で行います。

### 1. 元リポジトリを用意する

```bash
mkdir -p .cache/upstream
git clone https://github.com/Breeganzo/CCDV-F-Preparation.git .cache/upstream/breeganzo
git -C .cache/upstream/breeganzo checkout f3f7759c4fff3244ff88ae9bafeb1a2a72890180
git clone https://github.com/bajor/claude-architect-professional-quiz.git .cache/upstream/bajor
git -C .cache/upstream/bajor checkout 05b068db2529b69ea76a2104dae0fd4c197d4d98
```

`.cache/` は git の管理対象外です。元リポジトリのファイルはコミットしません。
（`.cache/` は worktree ごとに別なので、Codex 用の worktree の中に clone します）

### 2. 取り込みスクリプトを書く

- `tools/import_breeganzo.py`（CCDV-F）と `tools/import_bajor.py`（CCAR-P）を作ります。
- Python 3.10 以上、**標準ライブラリだけ**で書いてください。
- 元リポジトリのコードは**実行しないでください**（`node` で読み込む、`eval` するなど）。
  Breeganzo の `data/questions-*.js` は、`(window.CCDV_QUESTIONS = …).push({ … }, …)` という形の JavaScript です。
  キーに引用符がない、コメントがある、などの点に注意して、**小さなパーサーを書いて読み取って**ください。
- 元データとの対応は `docs/data-format.md` の「5. 元データとの対応」のとおりです。
- 出力の形式：UTF-8、`json.dumps(..., ensure_ascii=False, indent=2)`、末尾に改行。
- 何度実行しても同じ結果になるようにします（すでにあるファイルは上書き）。
- **既存のファイルの `ja` は上書きしない**でください。`ja.status` が `todo` 以外のファイルは、`ja` を残したまま `en` などだけを更新します（和訳を始めたあとにもう一度取り込んでも、訳が消えないように）。
- 英語の文は、元データの文字をそのまま使います。直してよいのは次の2つだけです。
  - 改行を半角スペースに置き換える
  - 前後の空白を取り除く

### 3. 実行して検証する

```bash
./dev py tools/import_breeganzo.py
./dev py tools/import_bajor.py
./dev validate --strict-counts
./dev check
```

（`docker` が使えない場合は、AGENTS.md の「5. 開発環境とコマンド」のとおり、`python3 tools/…` を直接実行してかまいません）

**完了の条件**

- `./dev validate --strict-counts` がエラー0件で通る（ccdv-f が180問、ccar-p が228問）
- 正解がずれていない。CCDV-F・CCAR-P それぞれ5問ほどを元データと見比べて確認し、確認した問題の ID を作業メモに書く
- 複数選択の問題（CCDV-F は9問、CCAR-P は63問の予定）が、`type: "multi"` になっている

### 4. コミット

- `data/questions/` と `tools/import_*.py` だけをコミットします。
- コミットメッセージの例：「CCDV-F と CCAR-P の英語の問題を取り込み（180問・228問）」

## 作業メモ（Codex が書く）

- 完了日：2026-11-23。Codex 用 worktree の `content/import` で実施。作業中に更新された `main`（`3f556c3`）も取り込み済み。
- 両出典を `.cache/upstream/` に clone し、指定コミットに checkout。元コードは実行せず、MIT ライセンスと既存 `NOTICE.md` の対応も確認。
- `tools/import_breeganzo.py` と `tools/import_bajor.py` を作成。Python 3.10 以上の標準ライブラリだけを使用。既定の出力先は `data/questions/`。`--upstream` と `--out` で入力・出力先を指定可能。
- JavaScript はデータリテラル専用パーサーで読み取り。bajor の `blueprint.js` は静的な `domains` 配列だけを読み、全38目標の文を対応付けた。
- CCDV-F：180問（single 171問、multi 9問）。分野別：d1=26、d2=59、d3=6、d4=5、d5=30、d6=20、d7=15、d8=19。補足ファイルの問題も元の `d` に従って配置。
- CCAR-P：228問（single 165問、multi 63問）。分野別：d1=39、d2=30、d3=43、d4=36、d5=32、d6=32、d7=16。
- 全408問の `ja` は `{ "status": "todo" }`。和訳は実施していない。UTF-8、2スペースのインデント、末尾改行で出力。
- 確認結果：`./dev validate --strict-counts` 成功（エラー・警告0件）。`./dev check` 成功（23テスト、検証、ビルド）。いずれも Docker 内で実行し、最新 `main` 反映後も再確認。
- 元データとの全件照合：英文の問題文・選択肢・各選択肢の理由・全体解説、正解番号と選択肢IDの対応、選択形式、難易度、参考資料を照合。CCDV-F は取り込み本体とは別のトークン分割で読み取り、全180問の一致を確認。CCAR-P は元JSONの全228問の一致を確認。
- 抜き取りで元ファイルと見比べた CCDV-F の ID と正解：
  - `ccdvf-bz-d2-001`：`[0]` → `["a"]`
  - `ccdvf-bz-d2-003`：`[1]` → `["b"]`
  - `ccdvf-bz-d2-005`：`[0,1]` → `["a","b"]`
  - `ccdvf-bz-d2-006`：`[3]` → `["d"]`
  - `ccdvf-bz-d2-054`：`[0,1]` → `["a","b"]`（補足ファイル）
  - `ccdvf-bz-d7-005`：`[0,1]` → `["a","b"]`
  - `ccdvf-bz-d8-007`：`[0,1]` → `["a","b"]`
- 抜き取りで元ファイルと見比べた CCAR-P の ID と正解：
  - `ccarp-bj-1.1-outcome-before-interface`：`1` → `["b"]`
  - `ccarp-bj-1.1-live-availability-boundary`：`3` → `["d"]`
  - `ccarp-bj-1.1-settlement-assistance-scope`：`[0,2]` → `["a","c"]`
  - `ccarp-bj-7.1-whole-session-isolation`：`[0,1,3]` → `["a","b","d"]`（3つ選択）
  - `ccarp-bj-7.3-api-versus-tool-outcomes`：`2` → `["c"]`
- 再取り込みの確認：両スクリプトの再実行前後で全408ファイルのハッシュが一致。別の一時出力先で `draft` と `reviewed` の和訳全体を保持しつつ英語を更新できること、既存JSONが壊れている場合に他ファイルの書き換え前に中止することを確認。確認用スクリプトは `.cache/verify_import.py`（管理対象外）。
- 気づいたこと：bajor の元の `type` は `single` / `multiple` のため、`multiple` を仕様の `multi` に変換した。難易度は指定された3種類だけだった。英語原文は許可された改行・前後空白の処理以外は変更していない。取り込みを妨げる元データの不整合は見つからなかった。
- 本体コミット：`44e7527`「CCDV-F と CCAR-P の英語の問題を取り込み（180問・228問）」。`data/questions/` と `tools/import_*.py` を収録。この作業メモは、今回に限る例外としてユーザーの指示により別コミットに収録する。コミット対象のルールは変更しない。`.cache/`、`app/data/` は管理対象外。push・`main` へのマージは実施していない。
