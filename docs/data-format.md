# 問題データの仕様（schema 1）

アプリ（Claude Code 担当）と問題データ（Codex 担当）の**共通の取り決め**です。
変更するときは、先にユーザーの承認を得てください。
検証の正本は `tools/validate.py` です。`schema/*.json` は同じ内容を JSON Schema で書いた参考資料です。

## 1. ファイルの置き場所

```
data/exams/<exam>.json                         試験の情報
data/questions/<exam>/<domain>/<id>.json       1問1ファイル
```

- `<exam>` は試験の `id` です（`ccdv-f`、`ccar-p` など。`data/exams/` にあるもの）。
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
| `exam` | 文字列 | ✅ | 試験の `id`（`ccdv-f` など）。`data/exams/` にあるもの |
| `domain` | 文字列 | ✅ | 分野ID。`data/exams/<exam>.json` の `domains[].id` のどれか |
| `subdomain` | 文字列 / null | ✅ | 分野の中の小項目（英語のまま）。なければ `null` |
| `type` | 文字列 | ✅ | `single`（1つ選ぶ）/ `multi`（複数選ぶ） |
| `select` | 整数 | ✅ | 選ぶ数。`single` なら `1`、`multi` なら `answer` の数と同じ（2以上） |
| `difficulty` | 整数 / null | ✅ | `1`（基礎）・`2`（標準）・`3`（応用）。元データにない場合は `null` |
| `tags` | 文字列の配列 | ✅ | 元データのタグ。なければ `[]` |
| `answer` | 文字列の配列 | ✅ | 正解の選択肢の `id`。**番号ではなく id で持つ**（シャッフルしてもずれないように） |
| `en` | オブジェクト | ✅ | 英語の原文（「2-1」）。元の問題集のまま |
| `ja` | オブジェクト | ✅ | 日本語訳（「2-2」） |
| `supplement` | オブジェクト | 任意 | このアプリの作成者による補足（「2-4」）。補足がない問題では書かない |
| `references` | 配列 | ✅ | 参考資料 `{ "title", "url" }`。url は `https://` で始める。なければ `[]` |
| `source` | オブジェクト | ✅ | 出典（「2-3」） |

上の表にないフィールドは書かないでください（検証でエラーになります）。
フィールドの並び順は、上の表の順にそろえます（`supplement` は `ja` のすぐ後ろ）。

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

### 2-4. `supplement`（このアプリの作成者による補足）

元の問題集の文章（`en`）とその訳（`ja`）とは別に、**このアプリの作成者が書き足す補足**です。
原文の説明が足りない、紛らわしいなど、補足したほうがよい問題にだけ書きます。

```json
"supplement": {
  "ja": "{c} も、ワークフローを選ぶ理由にはなりますが、…",
  "en": "Option {c} can also be a reason to choose a workflow, but …"
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `ja` | 文字列 | ✅ | 補足の本文（日本語）。空にしない |
| `en` | 文字列 | ✅ | 補足の本文（英語）。`ja` と同じ内容。空にしない |

- **原文や和訳の中に補足を混ぜない**でください。元の作者の文章と、このアプリの作成者の文章を区別するためです。
- 補足を書く・変えるときは、**文面をユーザーに確認してもらってから**にします。
- アプリは、答え合わせのときに解説の下へ表示します。日本語で表示しているときは `ja` を「補足（このアプリの作成者による追記）」、英語で表示しているときは `en` を「Supplement (added by the author of this app)」という見出しで出します。
- 書式は `en` / `ja` と同じです（プレーンテキスト、バッククォートだけ使える、改行なし）。
- **選択肢を指すときは `{a}`・`{b}` のように、波かっこで選択肢の `id` を囲みます。** アプリは選択肢の並び順を入れ替えて A, B, C, … と振り直すので、表示のときに、いま画面に出ている記号に置き換えます。「c」のように直接書くと、並びが変わったときに別の選択肢を指してしまいます。
- 取り込みスクリプトをもう一度実行しても、補足は消えません。

## 3. ID の決め方

`<試験の略号>-<出典の略号>-<元のIDを小文字にしたもの>` とします。使える文字は `a-z 0-9 . -` だけです。
試験の略号は、試験ファイルの `id_prefix` です。

| 試験 | 出典 | 元のID | 問題ID |
|---|---|---|---|
| CCDV-F（`ccdvf`） | Breeganzo（`bz`） | `D2-001` | `ccdvf-bz-d2-001` |
| CCAR-P（`ccarp`） | bajor（`bj`） | `ccarp-1.1-outcome-before-interface` | `ccarp-bj-1.1-outcome-before-interface` |

bajor の元のIDは `ccarp-` で始まるので、その部分を取り除いてから付け直します。

## 4. 試験ファイル（`data/exams/<exam>.json`）

| フィールド | 説明 |
|---|---|
| `id` / `code` | `ccdv-f` / `CCDV-F` など。`id` は英小文字・数字をハイフンでつないだもの。**一度決めたら変えない**（学習記録のキー） |
| `name.en` / `name.ja` | 試験名 |
| `edition.from` / `edition.until` | その試験ガイドで受験できる期間（`YYYY-MM-DD`、両端を含む）。決まっていない側は `null`（「4-1」） |
| `id_prefix` | 問題IDの先頭に付ける試験の略号（`ccdvf` など）。試験ごとに重複しない |
| `exam.questions` / `exam.minutes` | 本番の問題数と制限時間 |
| `exam.pass_scaled` / `scale_min` / `scale_max` | 合格ライン（スケールスコア） |
| `exam.pass_raw_estimate` | 正答率で見た合格の目安（`(720-100)/900`。公式の値ではない） |
| `domains[]` | 分野。`id`、`name.en` / `name.ja`、`weight`（配分 %）、`mock_items`（模試での出題数。合計は `exam.questions` と同じ） |
| `sources[]` | 出典。`abbr`、`repo`、`commit`、`license`、`questions`（取り込む問題数） |

### 4-1. 試験ガイドの版（`edition`）

本番の試験は、試験ガイドの改訂で範囲・分野の配分・問題数が変わることがあります。
このアプリでは、**試験ガイドの版が違えば別の試験として扱います**。問題データも版ごとに持ちます（同じ元問題を二重に持ってかまいません）。

- いまある試験の `id`・`id_prefix`・問題IDは変えません。
- 新しい版を足すときは、元の `id` に新しいガイドが有効になる年月（`YYMM`）を付けた試験を作ります。
  `id_prefix` にも同じ年月を付けます。

| 試験 | `id` | `id_prefix` | `edition` |
|---|---|---|---|
| CCDV-F（2026/12/06 以前） | `ccdv-f` | `ccdvf` | `{ "from": null, "until": "2026-12-06" }` |
| CCDV-F（2026/12/07 以降）※例 | `ccdv-f-2612` | `ccdvf2612` | `{ "from": "2026-12-07", "until": null }` |

- アプリは `edition` から「2026/12/06 以前」「2026/12/07 以降」のような表示を作り、試験名に添えます。
  `until` がある試験には、範囲が変わること（過ぎたあとは旧版であること）を、その試験の画面に表示します。
- 改訂の予定がない試験は `{ "from": null, "until": null }` にします。

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
