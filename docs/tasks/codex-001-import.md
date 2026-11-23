# codex-001：英語の問題を取り込む

- 状態：未着手
- 担当：Codex
- ブランチ：`content/import`
- 前提：`AGENTS.md`、`docs/data-format.md` を読んでいること

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
python3 tools/import_breeganzo.py
python3 tools/import_bajor.py
python3 tools/validate.py --strict-counts
python3 tools/build.py
python3 -m unittest discover -s tests
```

**完了の条件**

- `validate.py --strict-counts` がエラー0件で通る（ccdv-f が180問、ccar-p が228問）
- 正解がずれていない。CCDV-F・CCAR-P それぞれ5問ほどを元データと見比べて確認し、確認した問題の ID を作業メモに書く
- 複数選択の問題（CCDV-F は9問、CCAR-P は63問の予定）が、`type: "multi"` になっている

### 4. コミット

- `data/questions/` と `tools/import_*.py` だけをコミットします。
- コミットメッセージの例：「CCDV-F と CCAR-P の英語の問題を取り込み（180問・228問）」

## 作業メモ（Codex が書く）

- （ここに、やったこと、問題数、確認した問題の ID、気づいたこと（元データの誤りなど）を書く）
