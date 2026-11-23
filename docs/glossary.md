# 訳語の対応表

和訳で使う訳語をそろえるための表です。Codex が和訳しながら追記していきます。
「英語のまま」は、訳さずにそのまま書く用語です。

| 英語 | 訳語 | メモ |
|---|---|---|
| agent | エージェント | |
| workflow | ワークフロー | |
| orchestrator / worker | オーケストレーター / ワーカー | |
| prompt | プロンプト | |
| system prompt | システムプロンプト | API の `system` パラメーターは英語のまま |
| context window | コンテキストウィンドウ | |
| context engineering | コンテキストエンジニアリング | |
| token | トークン | |
| prompt caching | プロンプトキャッシュ | |
| tool | ツール | |
| tool use | ツール使用 | `tool_use` ブロックは英語のまま |
| guardrail | ガードレール | |
| prompt injection | プロンプトインジェクション | |
| human-in-the-loop | ヒューマンインザループ（人による確認） | 初出だけ括弧で補足してよい |
| evaluation / eval | 評価 | 「eval」を名詞で使う場合も「評価」 |
| latency | レイテンシ | |
| throughput | スループット | |
| retrieval | 検索（リトリーバル） | RAG の文脈では「検索」 |
| hallucination | ハルシネーション | |
| stakeholder | ステークホルダー | |
| least privilege | 最小権限 | |
| Messages API | 英語のまま | |
| Message Batches API | 英語のまま | |
| MCP server | MCP サーバー | |
| context | コンテキスト | |
| turn | ターン | user / assistant は、説明文ではユーザー / アシスタント。API の値として記す場合は英語のまま |
| content block | コンテンツブロック | |
| delta | 差分 | ストリーミングの文脈 |
| streaming | ストリーミング | |
| blocking | ブロッキング | |
| asynchronous / synchronous | 非同期 / 同期 | |
| concurrency | 並行処理 / 並行数 | 処理方式か同時実行数かに応じて使い分ける |
| exponential backoff | 指数バックオフ | |
| jitter | ジッター | |
| rate limiting | レート制限 | |
| retry | 再試行 | |
| truncation | 出力の途切れ | 出力上限などで生成が途中で切れること |
| stop sequence | 停止シーケンス | API の識別子は英語のまま |
| token counting | トークンカウント | |
| extended thinking | 英語のまま | 機能名 |
| payload | ペイロード | |
| endpoint | エンドポイント | |
| schema | スキーマ | |
| typed contract | 型で定めた契約 | |
| regression | リグレッション | |
| held-out set | 調整用とは別のセット | プロンプトなどの調整用データから分離した評価用データ |
| ground truth | 正解データ | |
| mock | モック | 動詞は「モック化する」 |
| unit test / integration test | 単体テスト / 結合テスト | |
| deterministic / probabilistic | 決定論的 / 確率的 | |
| idempotency / idempotency key | 冪等性 / 冪等性キー | |
| observability | 可観測性 | |
| operability | 運用のしやすさ | |
| structured log | 構造化ログ | |
| secret store | シークレットストア | |
| credential | 認証情報 | |
| authorisation | 認可 | |
| authentication | 認証 | |
| invariant | 不変条件 | |
| circuit breaker | サーキットブレーカー | |
| stateless | ステートレス | |
| compaction | 圧縮 | 会話履歴を要約する文脈 |
| grounding | グラウンディング | |
| citation | 引用 | 根拠となる検索箇所などの引用 |
| fine-tuning | ファインチューニング | |
| few-shot | 英語のまま | |
| untrusted data | 信頼できないデータ | |
| blast radius | 被害の影響範囲 / 影響範囲 | 文脈に応じて使い分ける |
| calibration / calibrated | 較正 / 較正された | 確信度の文脈 |
| confidence | 確信度 | |
| acceptance criteria | 受け入れ基準 | |
| data residency | データレジデンシー | |
| deployment topology | デプロイ構成 | |
| prefix | プレフィックス | |
| alias | エイリアス | |
| pin a version | バージョンを固定する | |
| rollout / rollback | 展開 / ロールバック | |
| staging | ステージング | |
| graceful degradation | 適切な機能の縮退 | 動詞句は「適切に機能を縮退させる」 |
| parser / schema validator | パーサー / スキーマバリデーター | |
| memory file | メモリーファイル | CLAUDE.md などを指す一般名詞 |
| sampling | サンプリング | |
| greedy | 貪欲法による | |
| greedy decoding | 貪欲デコーディング | |
| logit | ロジット | |
| floating-point arithmetic | 浮動小数点演算 | |
| serving stack | 配信基盤 | モデルを実行して応答を提供する基盤 |
| training corpus | 学習コーパス | |
| next-token prediction | 次トークン予測 | |
| thinking token | 思考トークン | |
| reasoning token | 推論トークン | |
| overfitting | 過学習 | |
| generalisation | 汎化 | |
| cache breakpoint | キャッシュの区切り | |
| cache hit | キャッシュへのヒット | |
| cache read / cache write | キャッシュ読み取り / キャッシュ書き込み | 文中では「キャッシュの読み取り / 書き込み」としてもよい |
| model tier | モデル階層 | |
| time-to-first-token | 最初のトークンまでの時間 | |
| harness | 実行基盤 | エージェントの実行を制御する仕組み |
| synthesis | 情報統合 | 複数の情報をまとめて結論を出す文脈 |
| tenant | テナント | |
| knowledge base | ナレッジベース | |
| parametric memory | パラメーターに蓄えた記憶 | |
| sentiment tagging | 感情ラベル付け | |
| boilerplate | 定型文 | |
| frontier model | 最先端のモデル | |
| cost attribution | 費用の配賦 | 機能などへの費用の割り当て |
| tokenisation | トークン化 | |
| subagent / sub-agent | サブエージェント | |
| autonomy / agency | 自律性 | |
| routing | ルーティング | 動詞は「振り分ける」 |
| prompt chaining | プロンプトチェーン | |
| parallelisation | 並列化 | |
| voting | 投票 | |
| sectioning | 分割 | 並列化の方式 |
| evaluator-optimiser / evaluator-optimizer | 評価者・最適化者 | ワークフローパターン |
| hook | フック | |
| side effect | 副作用 | |
| control flow | 制御フロー | |
| trace | トレース | |
| self-hosted / self-hosting | セルフホスト | |
| managed deployment | マネージド環境へのデプロイ | |
| context isolation | コンテキストの分離 | |
| entity | エンティティー | |
| context pruning | コンテキストの枝刈り | |
| context bloat | コンテキストの肥大化 | |
| task isolation | タスクの分離 | |
| prefill / prefilling | 事前入力 | アシスタントターンの冒頭を指定する文脈 |
| defensive parsing | 防御的な解析 | |
| chain of thought / chain-of-thought | 思考の連鎖 | |
| true positive | 真陽性 | |
| near-miss case | 紛らわしい非該当ケース | 分類の境界を説明する文脈 |
| delimiter | 区切り | |
| code fence | コードフェンス | |
| structural / semantic validation | 構造の検証 / 意味の検証 | |
| client-side tool / server-side tool | クライアント側ツール / サーバー側ツール | |
| built-in tool / custom tool | 組み込みツール / カスタムツール | |
| pagination | ページ分割 | |
| attack surface | 攻撃対象領域 | |
| primitive | 基本要素 | MCP の文脈 |
| resource | リソース | MCP の文脈 |
| transport | トランスポート | |
| embedding | 埋め込み | |
| parameterised query | パラメーター化クエリー | |
| sanitise | 無害化する | |
| indirect prompt injection | 間接的なプロンプトインジェクション | |
| jailbreak | ジェイルブレイク | |
| exfiltration | データ流出 | |
| data minimisation | データ最小化 | |
| redact | 秘匿化する | |
| entitlement | アクセス権 | |
| defence in depth | 多層防御 | |
| capability restriction | 機能制限 | |
| content moderation | コンテンツモデレーション | |
| fail-open / fail-closed | フェイルオープン / フェイルクローズ | |
| linting | 静的検査 | |
| secret manager | シークレットマネージャー | |
| delegated token | 委任トークン | |
| principal | 主体 | 認可の文脈 |
| identity model | アイデンティティーモデル | |
| rotation | ローテーション | キーや認証情報の更新 |
| Plan mode | 英語のまま | 機能名 |
| Headless mode | 英語のまま | 機能名 |
| custom slash command | カスタムスラッシュコマンド | |
| project memory | プロジェクトメモリー | |
| agent memory | エージェントメモリー | |
| integration layer | 連携層 | |
| parametric knowledge | パラメーター内の知識 | |
| quota | 割り当て量 | |
