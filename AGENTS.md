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
| **Claude Code** | アプリ本体、データ仕様、検証・ビルドの仕組み、開発環境 | `app/`、`schema/`、`tools/validate.py`、`tools/build.py`、`tests/`、`.github/`、`Dockerfile`、`compose.yaml`、`dev`、`requirements-dev.txt` |
| **Codex** | 問題の取り込みと和訳 | `data/questions/`、`tools/import_*.py`、`docs/glossary.md`、`docs/tasks/` の自分の作業メモ |
| **ユーザー** | 方針の決定、`main` へのマージ | すべて |

- **担当外のファイルは編集しない**でください。必要なら `docs/tasks/` に依頼を書くか、ユーザーに相談します。
- 次のファイルは**共通の取り決め**です。変える場合は、先にユーザーの承認を得てください。
  - `AGENTS.md`、`docs/data-format.md`、`docs/translation-guide.md`、`schema/`、`data/exams/`

### ブランチ

- Claude Code は `app/<内容>`、Codex は `content/<内容>` というブランチで作業します。
- `main` に直接コミットしません。`main` へのマージはユーザーが行います。
- 1つのブランチでは1つの作業だけを行います（例：`content/import-ccdv-f`、`content/translate-ccdv-f-d2`）。

### 作業フォルダ（git worktree）

Claude Code と Codex は、**git worktree で分けたそれぞれのフォルダ**で作業します。
1つのフォルダでブランチを切り替えると、相手が編集中のファイルが入れ替わってしまうためです。

| フォルダ | ブランチ | 使う人 |
|---|---|---|
| `~/repos/claude-code-training` | `main` | 統合・マージ用（ユーザー） |
| `~/repos/claude-code-training.claude` | `app/*` | Claude Code |
| `~/repos/claude-code-training.codex` | `content/*` | Codex |

worktree は、統合用のフォルダで次のように作ります。

```bash
git worktree add ../claude-code-training.claude -b app/<内容> main
git worktree add ../claude-code-training.codex -b content/<内容> main
```

- **自分の worktree の中だけで作業します。** 統合用のフォルダや相手の worktree のファイルは編集しません。統合用のフォルダでブランチを切り替えることもしません。
- 1つのブランチは、1つの worktree でしかチェックアウトできません。新しい作業を始めるときは、自分の worktree の中で新しいブランチを作ります（`git switch -c content/<内容> main`）。
- 作業を始めるとき、また `main` が更新されたときは、自分のブランチに `main` を取り込みます（`git merge main`）。
- 作業が一段落したら `docs/tasks/` の指示書に状況を書き、ユーザーにマージを依頼します。マージは統合用のフォルダで行います。
- `.cache/`（元リポジトリの clone、PDF など）と `app/data/` は worktree ごとに別々です。必要な worktree の中に置きます。
- 不要になった worktree は `git worktree remove <フォルダ>` で削除します（フォルダを直接消さない）。

#### Docker を worktree ごとに分ける

`./dev serve` を複数の worktree で同時に動かすと、コンテナの名前とポートがぶつかります。
そこで、各 worktree の直下に `.env`（git の管理対象外）を置いて分けます。コンテナのイメージは共通なので、作り直す必要はありません。

| worktree | `.env` の中身 |
|---|---|
| `.claude` | `COMPOSE_PROJECT_NAME=claude-cert-quiz-claude` と `WEB_PORT=8000` |
| `.codex` | `COMPOSE_PROJECT_NAME=claude-cert-quiz-codex` と `WEB_PORT=8001` |
| 統合用 | 置かない（既定の `claude-cert-quiz`、8000番。`.claude` と同時に serve しない） |

#### Codex の設定（実行制限）

worktree でコミットすると、git は統合用フォルダの `.git`（`~/repos/claude-code-training/.git`）に書き込みます。
Codex の実行制限で書き込める場所が起動フォルダの中だけになっていると、コミットが失敗します。
その場合は、Codex の設定で書き込み可能な場所に `~/repos/claude-code-training/.git` を追加してください。

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
LICENSE                このアプリの MIT ライセンス（コード・ドキュメント・和訳・補足）
NOTICE.md              このアプリと元の問題集の著作権表示とライセンス文
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
Dockerfile、compose.yaml、dev、requirements-dev.txt   開発用コンテナ（「5. 開発環境とコマンド」）
.cache/                作業用ファイル（元リポジトリの clone、PDF など。git の管理対象外）
.env                   worktree ごとの Docker の設定（git の管理対象外。「作業フォルダ（git worktree）」）
```

## 5. 開発環境とコマンド

**作業は Linux（WSL）上で行い、Python・PDF の処理・開発サーバーは Docker コンテナの中で動かします。**
コンテナは `./dev` から使います。git・gh・Claude Code・Codex は Linux 側のものを使います。

| ツール | 置き場所 |
|---|---|
| Python 3.12、poppler-utils（PDF の読み取り）、Playwright + Chromium（ブラウザでのテスト） | コンテナ（`Dockerfile`） |
| Docker / Docker Compose、git、gh、Claude Code、Codex | Linux |

```bash
./dev check                                        # テスト → 検証 → ビルド（コミット前に必ず実行。CI と同じ内容）
./dev validate                                     # data/ を検証する
./dev validate --questions tests/fixtures/questions   # サンプル問題を検証する
./dev validate --strict-counts                     # 問題数が出典どおりかも確認する
./dev build                                        # app/data/ を生成する
./dev build --questions tests/fixtures/questions   # サンプル問題でビルドする
./dev test                                         # validate.py / build.py のテスト
./dev serve                                        # http://localhost:8000 でアプリを確認する
./dev pdf .cache/guide.pdf .cache/guide.txt        # PDF をテキストにする
./dev py tools/import_bajor.py                     # 任意の Python スクリプトを実行する
./dev help                                         # すべてのコマンド
```

- コンテナからはリポジトリの中しか見えません。PDF などの作業用ファイルは `.cache/`（git の管理対象外）に置きます。
- 初回は、イメージを作るのに数分かかります（`./dev image` で作り直せます）。
- Python のパッケージを Linux 側に `pip install` しないでください。必要なら `requirements-dev.txt` に追加します（Claude Code の担当）。
- **`docker` が使えない環境の場合**（Codex の実行制限など）に限って、`tools/` のスクリプトを Linux 側の `python3` で直接実行してかまいません（標準ライブラリだけで動き、Python 3.10 以上が対象です）。
  例：`python3 tools/validate.py`、`python3 -m unittest discover -s tests`。ブラウザでのテストはコンテナでしか動きません。

## 6. 守ること

- コミットする前に `./dev check` を通してください。エラーが残ったままコミットしません。
- `app/data/` は生成物です。git で管理せず、GitHub Actions が公開のたびに作ります。
- 問題の **ID は一度決めたら変えません**（アプリの学習記録のキーになっているため）。
- 英語の原文（`en`）は**元の問題集のまま**にします。誤りを見つけても書き換えず、`docs/tasks/` に報告してください。
- 原文の説明が足りない・紛らわしい問題には、`supplement`（このアプリの作成者による補足）を書けます。原文や和訳の中には補足を混ぜません。補足の文面は、ユーザーの確認を得てから書きます（`docs/data-format.md` の「2-4」）。
- 和訳（`ja`）は `docs/translation-guide.md` に従います。
- 本番の試験問題を思い出して書いたものや、他の問題集から持ってきた問題を混ぜてはいけません。
- 外部に公開・送信する操作（push、リポジトリの設定変更など）は、ユーザーの指示があるときだけ行います。

## 7. 作業の受け渡し

- 作業指示は `docs/tasks/<担当>-<番号>-<内容>.md` に書きます（例：`codex-001-import.md`）。
- 指示書の冒頭にある「状態」を、作業の進み具合に合わせて更新してください（`未着手` → `作業中` → `完了`）。
- 終わったら、指示書の末尾の「作業メモ」に、やったこと、問題数、気づいたこと（元データの誤りなど）を書きます。
