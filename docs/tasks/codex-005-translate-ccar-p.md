# codex-005：CCAR-P の全228問を和訳する

- 状態：作業中
- 担当：Codex
- ブランチ：`content/translate-ccar-p`（作成済み。`main` の `06e2980`（CCDV-F の残り91問のマージ後）から作り、この指示書だけをコミットしてある）
- 作業フォルダ：`~/repos/claude-code-training.codex`（Codex 用の worktree）
- 前提：`AGENTS.md`、`docs/data-format.md`、`docs/translation-guide.md`、`docs/glossary.md` を読んでいること。進め方は `docs/tasks/codex-004-translate-ccdv-f-rest.md` と同じです

## 背景

CCDV-F の180問は、すべて訳し終わりました。次は **CCAR-P の228問（7分野）を、この1つのブランチで**和訳します。
これが終わると、2つの試験の408問がすべて訳済みになります。
（「1つのブランチでは1つの作業」の「1つの作業」は、今回は「CCAR-P の和訳」です）

## 始めかた

```bash
cd ~/repos/claude-code-training.codex
git status                        # 変更が残っていないことを確認する
git switch content/translate-ccar-p
git log --oneline -3              # 先頭がこの指示書のコミットであることを確認する
```

- 前の作業ブランチ `content/translate-ccdv-f-rest` は `main` にマージ済みです。そのままにしておいてかまいません（削除はユーザーが判断します）。
- 作業の途中で `main` が更新されたら、`git merge main` で取り込みます。

## やること

CCAR-P の7分野の `ja` を埋め、`ja.status` を `draft` にします。**上から順に**進めます（本番での配分が大きい順）。

| 順 | 分野 | 配分 | 問題数 | 内訳 |
|---|---|---|---|---|
| 1 | d3 Integration | 19% | 43 | single 31、multi 12 |
| 2 | d1 Solution Design & Architecture | 17% | 39 | single 28、multi 11 |
| 3 | d4 Evaluation, Testing & Optimization | 16% | 36 | single 26、multi 10 |
| 4 | d5 Governance, Safety & Risk Management | 14% | 32 | single 23、multi 9 |
| 5 | d6 Stakeholder Communication & Lifecycle Management | 14% | 32 | single 23、multi 9 |
| 6 | d2 Claude Models, Prompting & Context Engineering | 13% | 30 | single 22、multi 8 |
| 7 | d7 Developer Productivity & Operational Enablement | 7% | 16 | single 12、multi 4 |
| | **合計** | | **228** | **single 165、multi 63** |

- 和訳のしかたは `docs/translation-guide.md` に従います。特に「1. いちばん大事なこと」（ヒントを足さない、選択肢の長さのバランスを崩さない、意味を変えない）を守ってください。
- 訳語は `docs/glossary.md` に合わせます。CCDV-F で追加した訳語も使い、試験をまたいで訳語をそろえます。新しく訳した用語は glossary に追記します。分野名の訳は `data/exams/ccar-p.json` の `name.ja` に合わせます。
- 訳の例は、和訳済みの `data/questions/ccdv-f/` です。
- `en`、ID、正解、`subdomain`、`tags`、出典など、`ja` 以外のフィールドは変更しません（13用語の `supplement` を足すことだけは例外です。下の「用語の補足（13用語）」）。CCDV-F の問題も変更しません（訳語の不統一に気づいたら、直さずに作業メモに書きます）。
- `reviewed` は付けません（ユーザーが確認してから付けます）。

### CCAR-P で CCDV-F と違うところ

- **全228問の `en.explanation` が空（`""`）です。** そのため `ja.explanation` も `""` にします。各選択肢の `note`（理由）が解説の代わりになるので、`note` は4つとも訳を空にしません。
- **`note` も長さのバランスに気をつけます。** 解説がない分、`note` が答え合わせの中心になります。正解の選択肢の `note` だけを丁寧に訳して長くしないでください。
- **複数選択の問題（63問）は、問題文の最後が「Select 2 answers.」「Select 3 answers.」です**（2つ選択が48問、3つ選択が15問）。CCDV-F の「(Select 2)」と同じく、文末を「（2つ選択）」「（3つ選択）」にします。数は `select` の値と一致させます。
  - 例：「Which actions turn the request into defensible architectural constraints? Select 2 answers.」→「要求を根拠のあるアーキテクチャ上の制約に落とし込む行動はどれですか？（2つ選択）」
- 問題文が長く、業務の条件（予算、契約、監査、承認の手順など）が細かく書かれています。条件を落としたり、まとめたりせずに訳してください。条件の1つが正解を決める手がかりになっていることがあります。

### 原文の誤りや、補足が必要そうな問題

- 原文（`en`）の誤りに気づいても、`en` も訳も直しません。下の「作業メモ」に問題 ID と内容を書きます。
- 説明が足りない・紛らわしい問題があっても、**`supplement` は書きません**。作業メモに「補足の候補」として、問題 ID と理由を書いてください。補足の文面はユーザーが確認してから決めます（`docs/data-format.md` の「2-4」）。
- **例外として、CCDV-F で補足を付けた13用語は、ユーザーの承認済みなので、確認を待たずに補足を付けます。** 下の「用語の補足（13用語）」に従ってください。
- 13用語以外で、名前だけでは意味が分かりにくい英語の用語・略語に気づいたら、補足は書かずに、作業メモに用語と問題 ID を書きます。

### 用語の補足（13用語）

対象の用語：temperature、few-shot、top_p、p95、p99、OCR、SKU、CI、I/O、base64、extended thinking、Plan mode、Headless mode

- **文面は CCDV-F と同じものを使います。** 日本語・英語とも、CCDV-F の問題の `supplement` にある各用語の説明をそのまま使い、言い回しを変えたり、説明を足したりしません（例：OCR と base64 は `data/questions/ccdv-f/d2/ccdvf-bz-d2-008.json`）。codex-004 の作業で作った `.cache/bulk-term-definitions.json` も使えますが、CCDV-F の問題データと食い違う場合は問題データのほうに合わせます。
- **対象の問題**：和訳した `ja` の問題文・選択肢・理由（`note`）のどこかに、その用語が出てくる問題です。補足そのものに出てくる用語で、対象を増やしません。
  - 別の単語の一部に含まれているだけのもの（例：大文字の「CI」を含む別の略語）は対象にしません。文脈を見て、その用語として使われているかを確かめます。
- 1つの問題に複数の用語が出てくる場合は、CCDV-F と同じく、各用語の説明を1つの `supplement` にまとめます（例：`data/questions/ccdv-f/d5/ccdvf-bz-d5-017.json`）。
- 補足は、その分野の和訳と同じコミットに含めます。
- 作業メモには、分野ごとに、用語ごとの補足を付けた問題数を書きます。最後に、全体の「用語 → 問題 ID」の一覧も書きます。

### 並行作業での注意

- 変更してよいのは、`data/questions/ccar-p/`、`docs/glossary.md`、この指示書の「状態」と「作業メモ」だけです。
- `app/`、`schema/`、`tools/validate.py`、`tools/build.py`、`tests/` は Claude Code の担当です。`./dev check` がこれらの側の理由で失敗したら、直さずに作業メモに書いて、ユーザーに伝えてください。
- `./dev serve` でアプリを確認する場合は、worktree の `.env` のとおり **8001番**（http://localhost:8001）を使います。

## 確認

各分野を終えるたびに、次の2つを実行します。

```bash
./dev check
./dev validate --strict-counts
```

- 加えて、codex-004 と同じように、変更前の全408問を `.cache/` に保存しておき、**訳した問題の `ja` と `supplement` 以外のフィールドが変わっていないこと**、**`supplement` が13用語の説明だけでできていて、CCDV-F の文面と一致していること**、**他の問題（CCDV-F、未着手の分野）がバイト単位で変わっていないこと**を照合してください。

**完了の条件**：CCAR-P の228問がすべて `draft`（2つの試験の408問すべてが訳済み）で、上の確認がすべてエラー0件で通ること。

## コミット

- **分野ごとに1コミット**にします（例：「CCAR-P d3 を和訳（43問）」）。
- 各コミットの前に、上の「確認」を通します。途中で作業が止まっても、コミット済みの分野は残るようにするためです。
- この指示書の「状態」と「作業メモ」の更新も、このブランチでコミットします。分野が終わるたびに、下の表の「状態」も更新してください。
- push と `main` へのマージはしません。7分野がすべて終わったら、ユーザーにマージを依頼します。
- 途中の分野まででマージしたいとユーザーから言われたら、その時点までのコミットでマージを依頼してかまいません。

## 作業メモ（Codex が書く）

| 順 | 分野 | 状態 | 問題数 | コミット | メモ |
|---|---|---|---|---|---|
| 1 | d3 | 完了 | 43 | `04db453` | 全問 draft、全検証成功。temperature 1問、p95 4問に補足 |
| 2 | d1 | 完了 | 39 | `6406ca5` | 全問 draft、全検証成功。用語の補足対象なし |
| 3 | d4 | 完了 | 36 | `753c978` | 全問 draft、全検証成功。4用語各1問に補足 |
| 4 | d5 | 完了 | 32 | `6b6a8ab` | 全問 draft、全検証成功。OCR 1問に補足 |
| 5 | d6 | 完了 | 32 | この分野のコミット | 全問 draft、全検証成功。用語の補足対象なし |
| 6 | d2 | 未着手 | 30 | | |
| 7 | d7 | 未着手 | 16 | | |

### 共通の確認方法

- 作業開始時のHEADは `bfd20ae`。`git merge main` は `Already up to date.` だった。
- 変更前の全408問を `.cache/ccarp-original/` に保存。照合用の `.cache/ccarp_work.py` で、訳した問題の `ja` と `supplement` 以外のフィールド、他の問題のバイト列、選択肢のID・順序・空欄、複数選択の数、バッククォート、JSON書式を確認する。
- 13用語の定義は `.cache/bulk-term-definitions.json` の日英両方をCCDV-Fの問題データと照合して一致を確認した。補足は該当する定義の連結だけで構成されていることを検証する。これらの作業用ファイルは管理対象外。

### d3（2026-11-23）

- 43問（single 31、multi 12）の問題文、選択肢、全選択肢の理由を和訳。`ja.explanation` はすべて空文字のまま。選択肢の長さ・理由の密度を原文に合わせ、業務条件とバージョン指定を保持した。
- `./dev check` 成功（32テスト、検証、ビルド）、`./dev validate --strict-counts` 成功、全408問との照合成功。
- 用語の補足：temperature 1問、p95 4問、ほか11用語は0問。
- 原文の明らかな誤記は見つからなかった。MCP 2026-07-28、Messages API 2026-10-21などの特定バージョンを前提にした設問は、番号・記述をそのまま訳した。
- 補足の候補（未追加）：BM25（`ccarp-bj-3.5-context-before-indexing`、`ccarp-bj-3.5-contextualizer-provenance-contamination`、`ccarp-bj-3.5-searchable-context-and-provenance`、`ccarp-bj-3.6-current-structured-aggregation`、`ccarp-bj-3.6-exact-part-identifier-retrieval`、`ccarp-bj-3.6-hybrid-rank-fusion-and-deduplication`、`ccarp-bj-3.6-policy-paraphrase-semantic-matching`）、PKCE・S256（`ccarp-bj-3.2-pkce-metadata-gap`）、SSE（`ccarp-bj-3.7-mcp-current-transport-contract`）、A2A（`ccarp-bj-3.7-direct-api-client-tool-loop`、`ccarp-bj-3.7-independent-agent-coordination`）。名前や略語だけでは仕組みが分かりにくいため記録した。承認済み13用語以外の補足は書いていない。

### d1（2026-11-23）

- 39問（single 28、multi 11）の問題文・全選択肢・全理由を和訳し、draftにした。業務の権限、復旧条件、共有資源、コスト・時間・精度の値と分母を保持した。
- `./dev check` 成功（32テスト、検証、ビルド）、`./dev validate --strict-counts` 成功、全408問との照合成功。CCAR-Pは計82問draft。
- 用語の補足：13用語すべて0問。新たな原文の誤りや補足候補は見つからなかった。

### d4（2026-11-23）

- 36問（single 26、multi 10）をdraftにした。全選択肢の理由を訳し、計算式・数値・評価の分母と観測期間を保持した。
- `./dev check` 成功（32テスト、検証、ビルド）、`./dev validate --strict-counts` 成功、全408問との照合成功。CCAR-Pは計118問draft。
- 用語の補足：few-shot、temperature、top_p、p95が各1問、ほか9用語は0問。
- 原文の明らかな誤りは見つからなかった。補足の候補（未追加）：pass@3・pass^3（`ccarp-bj-4.3-match-attempt-budgets`）、top_k（`ccarp-bj-4.4-diagnose-versioned-sampling-rejection`）。記号や名前だけでは意味が分かりにくいため記録した。

### d5（2026-11-23）

- 32問（single 23、multi 9）をdraftにした。全選択肢の理由を訳し、承認の時点・実行回数・契約や法令の適用条件・公平性の評価条件を保持した。
- `./dev check` 成功（32テスト、検証、ビルド）、`./dev validate --strict-counts` 成功、全408問との照合成功。CCAR-Pは計150問draft。
- 用語の補足：OCR 1問、ほか12用語は0問。原文の明らかな誤りは見つからなかった。
- 補足の候補（未追加）：HIPAA・ePHI（`ccarp-bj-5.4-encrypted-ephi-custodian`、`ccarp-bj-5.4-hipaa-feature-path-change`）、BAA（`ccarp-bj-5.4-hipaa-feature-path-change`）、DPIA（`ccarp-bj-5.4-gdpr-significant-decision-gates`）、FedRAMP（`ccarp-bj-5.4-federal-internal-search-boundary`）。原文にある展開形は和訳し、それ以外の説明は足していない。

### d6（2026-11-23）

- 32問（single 23、multi 9）をdraftにした。全選択肢の理由を訳し、人員と処理能力の計算、実測と予測、承認条件、引き継ぎ・廃止・復旧の範囲を保持した。
- `./dev check` 成功（32テスト、検証、ビルド）、`./dev validate --strict-counts` 成功、全408問との照合成功。CCAR-Pは計182問draft。
- 用語の補足：13用語すべて0問。原文の明らかな誤りは見つからなかった。
- 補足の候補（未追加）：SLI・SLO・SLA（`ccarp-bj-6.3-service-commitment-definitions`）、SLA（`ccarp-bj-6.3-language-expansion-gates`）、エラーバジェット（`ccarp-bj-6.3-breach-response-authority`）。原文にある展開形と区別の説明はそのまま訳した。

### 用語 → 問題 ID（完了分野）

- temperature：`ccarp-bj-3.3-output-cap-truncation`、`ccarp-bj-4.4-diagnose-versioned-sampling-rejection`
- p95：`ccarp-bj-3.3-parallel-independent-tool-latency`、`ccarp-bj-3.3-quality-and-tail-latency-gates`、`ccarp-bj-3.3-reranking-complete-tradeoff`、`ccarp-bj-3.3-route-specific-model-tradeoffs`、`ccarp-bj-4.5-reranking-overhead-versus-token-savings`
- few-shot：`ccarp-bj-4.2-protect-heldout-incident-families`
- top_p：`ccarp-bj-4.4-diagnose-versioned-sampling-rejection`
- OCR：`ccarp-bj-5.4-hipaa-feature-path-change`
