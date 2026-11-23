# AGENTS.md

このファイルがリポジトリの**正本**です。Claude Code も Codex もここに従います。
（`CLAUDE.md` は `@AGENTS.md` を読み込むだけのファイルです。ルールは必ずここに書いてください。）

## 1. このリポジトリは何か

Anthropic の Claude 認定試験（**CCDV-F** と **CCAR-P**）の練習問題を日本語に訳し、
スマホの空き時間に解ける **PWA（静的Webアプリ）** として GitHub Pages で公開するプロジェクトです。

- 本番の試験は英語なので、アプリでは英語の原文も表示できるようにします。
- 問題の出典は、MIT ライセンスで公開されている2つの問題集**だけ**です（「3. 問題の出典」を参照）。

## 2. 分担（並行開発）

| 担当 | 主な作業 | 編集してよい場所 |
|---|---|---|
| **Claude Code** | アプリ本体、データ仕様、検証・ビルドの仕組み | `app/`、`schema/`、`tools/validate.py`、`tools/build.py`、`tests/`、`.github/` |
| **Codex** | 問題の取り込みと和訳 | `data/questions/`、`tools/import_*.py`、`docs/glossary.md`、`docs/tasks/` の自分の作業メモ |
| **ユーザー** | 方針の決定、`main` へのマージ | すべて |

- **担当外のファイルは編集しない**でください。必要なら `docs/tasks/` に依頼を書くか、ユーザーに相談します。
- 次のファイルは**共通の取り決め**です。変える場合は、先にユーザーの承認を得てください。
  - `AGENTS.md`、`docs/data-format.md`、`docs/translation-guide.md`、`schema/`、`data/exams/`

### ブランチ

- Claude Code は `app/<内容>`、Codex は `content/<内容>` というブランチで作業します。
- `main` に直接コミットしません。`main` へのマージはユーザーが行います。
- 1つのブランチでは1つの作業だけを行います（例：`content/import-ccdv-f`、`content/translate-ccdv-f-d2`）。

## 3. 問題の出典（ユーザーが決定済み。勝手に増やさない）

| 試験 | 出典 | commit | 問題数 | ライセンス | IDの略号 |
|---|---|---|---|---|---|
| CCDV-F | [Breeganzo/CCDV-F-Preparation](https://github.com/Breeganzo/CCDV-F-Preparation) | `f3f7759c4fff3244ff88ae9bafeb1a2a72890180` | 180 | MIT | `bz` |
| CCAR-P | [bajor/claude-architect-professional-quiz](https://github.com/bajor/claude-architect-professional-quiz) | `05b068db2529b69ea76a2104dae0fd4c197d4d98` | 228 | MIT | `bj` |

- 取り込むときは、必ず上の commit を使ってください（`git checkout <commit>`）。
- clone 先は `.cache/upstream/`（git の管理対象外）にします。
- 問題の著作権表示は `NOTICE.md` にあります。出典を増やしたら `NOTICE.md` も更新が必要です。

### 使ってはいけないもの

- **Udemy などの有料教材**：利用規約で複製・改変が禁止されています。
- **「dumps」「real exam questions」をうたう教材**：本番問題の流出物であれば、受験者の秘密保持契約（NDA）に違反します。
- **ライセンス表記のない問題集**：アプリを公開するので使えません。
- 品質の基準（正解の選択肢の長さや位置に偏りがないことなど）を満たさない問題集は使いません。

## 4. フォルダ構成

```
AGENTS.md              正本（このファイル）
CLAUDE.md              @AGENTS.md の1行だけ
NOTICE.md              元の問題集の著作権表示とライセンス文
docs/
  data-format.md       問題データの仕様（共通の取り決め）
  translation-guide.md 和訳のルール（共通の取り決め）
  glossary.md          訳語の対応表（Codex が育てる）
  tasks/               作業指示書と作業メモ
schema/                JSON Schema（仕様をまとめた参考資料。検証の正本は tools/validate.py）
data/
  exams/<exam>.json    試験の情報（問題数、時間、分野と配分）
  questions/<exam>/<domain>/<id>.json   1問1ファイル
tools/
  validate.py          データの検証
  build.py             data/ から app/data/ を生成
  import_*.py          元リポジトリからの取り込み
tests/fixtures/        アプリ開発用のサンプル問題
app/                   PWA 本体（app/data/ は生成物。手で編集しない）
.github/workflows/     GitHub Pages への公開
```

## 5. コマンド

Python 3.10 以上、標準ライブラリだけで動きます（`pip install` は不要です）。

```bash
python3 tools/validate.py                          # data/ を検証する（コミット前に必ず実行）
python3 tools/validate.py --questions tests/fixtures/questions   # サンプル問題を検証する
python3 tools/build.py                             # app/data/ を生成する
python3 tools/build.py --questions tests/fixtures/questions      # サンプル問題でビルドする
python3 -m unittest discover -s tests              # validate.py / build.py のテスト
python3 -m http.server 8000 -d app                 # http://localhost:8000 でアプリを確認する
```

## 6. 守ること

- コミットする前に `python3 tools/validate.py` を通してください。エラーが残ったままコミットしません。
- `app/data/` は生成物です。git で管理せず、GitHub Actions が公開のたびに作ります。
- 問題の **ID は一度決めたら変えません**（アプリの学習記録のキーになっているため）。
- 英語の原文（`en`）は**元の問題集のまま**にします。誤りを見つけても書き換えず、`docs/tasks/` に報告してください。
- 和訳（`ja`）は `docs/translation-guide.md` に従います。
- 本番の試験問題を思い出して書いたものや、他の問題集から持ってきた問題を混ぜてはいけません。
- 外部に公開・送信する操作（push、リポジトリの設定変更など）は、ユーザーの指示があるときだけ行います。

## 7. 作業の受け渡し

- 作業指示は `docs/tasks/<担当>-<番号>-<内容>.md` に書きます（例：`codex-001-import.md`）。
- 指示書の冒頭にある「状態」を、作業の進み具合に合わせて更新してください（`未着手` → `作業中` → `完了`）。
- 終わったら、指示書の末尾の「作業メモ」に、やったこと、問題数、気づいたこと（元データの誤りなど）を書きます。
