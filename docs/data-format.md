# 問題データの仕様（schema 1）

アプリ（Claude Code 担当）と問題データ（Codex 担当）の**共通の取り決め**です。
変更するときは、先にユーザーの承認を得てください。
検証の正本は `tools/validate.py` です。`schema/*.json` は同じ内容を JSON Schema で書いた参考資料です。

## 1. ファイルの置き場所

```
data/exams/<exam>.json                         試験の情報
data/questions/<exam>/<domain>/<id>.json       1問1ファイル
```

- `<exam>` は `ccdv-f` か `ccar-p` です。
- `<domain>` は試験ファイルの分野ID（`d1`, `d2`, …）です。
- ファイル名は、問題の `id` に `.json` を付けたものです。
- 文字コードは UTF-8、インデントは2スペース、末尾に改行を入れます。`ensure_ascii` は使わず、日本語はそのまま書きます。

## 2. 問題ファイル

```json
{
  "schema": 1,
  "id": "ccdvf-bz-d2-001",
  "exam": "ccdv-f",
  "domain": "d2",
  "subdomain": "Claude API Mechanics",
  "type": "single",
  "select": 1,
  "difficulty": 2,
  "tags": [],
  "answer": ["a"],
  "en": {
    "question": "Your service calls the Messages API ...",
    "options": [
      { "id": "a", "text": "Execute the requested tools ...", "note": "" },
      { "id": "b", "text": "Append an assistant turn ...", "note": "Prose loses the tool_use_id linkage ..." }
    ],
    "explanation": "The protocol is specific: ..."
  },
  "ja": {
    "status": "draft",
    "question": "あなたのサービスは…",
    "options": [
      { "id": "a", "text": "…", "note": "" },
      { "id": "b", "text": "…", "note": "…" }
    ],
    "explanation": "…"
  },
  "references": [
    { "title": "Anthropic docs — Tool use", "url": "https://docs.anthropic.com/en/docs/build-with-claude/tool-use" }
  ],
  "source": {
    "repo": "Breeganzo/CCDV-F-Preparation",
    "commit": "f3f7759c4fff3244ff88ae9bafeb1a2a72890180",
    "path": "data/questions-d2-apps.js",
    "orig_id": "D2-001",
    "license": "MIT"
  }
}
```

### フィールド

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `schema` | 整数 | ✅ | いまは `1` |
| `id` | 文字列 | ✅ | 問題ID（「3. ID の決め方」）。**一度決めたら変えない** |
| `exam` | 文字列 | ✅ | `ccdv-f` / `ccar-p` |
| `domain` | 文字列 | ✅ | 分野ID。`data/exams/<exam>.json` の `domains[].id` のどれか |
| `subdomain` | 文字列 / null | ✅ | 分野の中の小項目（英語のまま）。なければ `null` |
| `type` | 文字列 | ✅ | `single`（1つ選ぶ）/ `multi`（複数選ぶ） |
| `select` | 整数 | ✅ | 選ぶ数。`single` なら `1`、`multi` なら `answer` の数と同じ（2以上） |
| `difficulty` | 整数 / null | ✅ | `1`（基礎）・`2`（標準）・`3`（応用）。元データにない場合は `null` |
| `tags` | 文字列の配列 | ✅ | 元データのタグ。なければ `[]` |
| `answer` | 文字列の配列 | ✅ | 正解の選択肢の `id`。**番号ではなく id で持つ**（シャッフルしてもずれないように） |
| `en` | オブジェクト | ✅ | 英語の原文（「2-1」）。元の問題集のまま |
| `ja` | オブジェクト | ✅ | 日本語訳（「2-2」） |
| `references` | 配列 | ✅ | 参考資料 `{ "title", "url" }`。url は `https://` で始める。なければ `[]` |
| `source` | オブジェクト | ✅ | 出典（「2-3」） |

上の表にないフィールドは書かないでください（検証でエラーになります）。

### 2-1. `en`（英語の原文）

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `question` | 文字列 | ✅ | 問題文（空にしない） |
| `options` | 配列 | ✅ | 選択肢。2〜6個 |
| `options[].id` | 文字列 | ✅ | `a`, `b`, `c`, … の順に付ける（元の並び順のまま） |
| `options[].text` | 文字列 | ✅ | 選択肢の文（空にしない） |
| `options[].note` | 文字列 | ✅ | その選択肢が正しい・誤りである理由。なければ `""` |
| `explanation` | 文字列 | ✅ | 問題全体の解説。なければ `""` |

- `explanation` が `""` の場合は、**正解の選択肢すべてに `note` が必要**です（解説が何もない問題を作らないため）。
- 文章は**プレーンテキスト**です。Markdown は使いません。ただし、コードや識別子をバッククォートで囲む書き方（`` `tool_use` ``）だけは使えます。アプリはバッククォートの部分を等幅フォントで表示します。
- 改行は使いません（元データに改行があれば半角スペースに置き換えます）。

### 2-2. `ja`（日本語訳）

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `status` | 文字列 | ✅ | `todo`（未訳）/ `draft`（訳した）/ `reviewed`（人が確認した） |
| `question` | 文字列 | `todo` 以外で必須 | 問題文の訳 |
| `options` | 配列 | `todo` 以外で必須 | `en.options` と**同じ数・同じ id・同じ順番** |
| `options[].text` | 文字列 | `todo` 以外で必須 | 選択肢の訳 |
| `options[].note` | 文字列 | `todo` 以外で必須 | `en` の `note` が空でなければ、訳も空にしない |
| `explanation` | 文字列 | `todo` 以外で必須 | `en.explanation` が空でなければ、訳も空にしない |

- 未訳のときは `{ "status": "todo" }` だけを書きます。
- `draft` にするのは訳し終えたとき、`reviewed` にするのは人（ユーザー）が確認したときです。Codex は `reviewed` を付けません。
- アプリは、`status` が `todo` の問題を英語で表示します。

### 2-3. `source`（出典）

| フィールド | 説明 |
|---|---|
| `repo` | 元リポジトリ（`owner/name`） |
| `commit` | 取り込みに使った commit（40桁）。`data/exams/<exam>.json` の `sources[].commit` と同じ |
| `path` | 元リポジトリ内のファイルパス |
| `orig_id` | 元データでの ID |
| `license` | `MIT` |

## 3. ID の決め方

`<試験の略号>-<出典の略号>-<元のIDを小文字にしたもの>` とします。使える文字は `a-z 0-9 . -` だけです。

| 試験 | 出典 | 元のID | 問題ID |
|---|---|---|---|
| CCDV-F（`ccdvf`） | Breeganzo（`bz`） | `D2-001` | `ccdvf-bz-d2-001` |
| CCAR-P（`ccarp`） | bajor（`bj`） | `ccarp-1.1-outcome-before-interface` | `ccarp-bj-1.1-outcome-before-interface` |

bajor の元のIDは `ccarp-` で始まるので、その部分を取り除いてから付け直します。

## 4. 試験ファイル（`data/exams/<exam>.json`）

| フィールド | 説明 |
|---|---|
| `id` / `code` | `ccdv-f` / `CCDV-F` など |
| `name.en` / `name.ja` | 試験名 |
| `exam.questions` / `exam.minutes` | 本番の問題数と制限時間 |
| `exam.pass_scaled` / `scale_min` / `scale_max` | 合格ライン（スケールスコア） |
| `exam.pass_raw_estimate` | 正答率で見た合格の目安（`(720-100)/900`。公式の値ではない） |
| `domains[]` | 分野。`id`、`name.en` / `name.ja`、`weight`（配分 %）、`mock_items`（模試での出題数。合計は `exam.questions` と同じ） |
| `sources[]` | 出典。`abbr`、`repo`、`commit`、`license`、`questions`（取り込む問題数） |

## 5. 元データとの対応

### Breeganzo（CCDV-F）— `data/questions-*.js`

| 元データ | このデータ |
|---|---|
| `id`（`D2-001`） | `id` = `ccdvf-bz-d2-001`、`source.orig_id` = `D2-001` |
| `d`（1〜8） | `domain` = `d1`〜`d8` |
| `s` | `subdomain` |
| `diff` | `difficulty` |
| `type`、`n` | `type`、`select` |
| `stem` | `en.question` |
| `opts`（配列） | `en.options`（先頭から `a`, `b`, …） |
| `correct`（番号の配列） | `answer`（id の配列） |
| `why` | `en.explanation` |
| `wrong`（`{番号: 理由}`） | 該当する選択肢の `note`。それ以外は `""` |
| `doc`（`{t, u}`） | `references` = `[{ "title": t, "url": u }]` |

`data/questions-r2-supplement.js` の問題も、`d` の値に従って各分野に振り分けます。

### bajor（CCAR-P）— `data/questions/*.json`

| 元データ | このデータ |
|---|---|
| `id` | `id` = `ccarp-bj-…`、`source.orig_id` = 元の値 |
| `domain`（1〜7） | `domain` = `d1`〜`d7` |
| `objectiveId` と目標の文 | `subdomain` = `"1.1 Translate business problems into Claude-based AI solutions"`（目標の文は `blueprint.js` から取る） |
| `difficulty`（文字列） | `difficulty`：`foundational` → `1`、`intermediate` → `2`、`advanced` → `3`（それ以外の値があれば作業メモに報告） |
| `type` | `type`。`select` は正解の数 |
| `prompt` | `en.question` |
| `answers[].text` / `answers[].explanation` | `en.options[].text` / `en.options[].note` |
| `correct`（番号）または `correctIndices`（番号の配列） | `answer`（id の配列） |
| （なし） | `en.explanation` = `""`（正解の選択肢の `note` が解説の代わりになる） |
| `tags` | `tags` |
| `sourceIds` | `references`。`data/sources/*.json` の `id` で引いて `{ "title": name, "url": url }` にする |
