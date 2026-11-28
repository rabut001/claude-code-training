# Claude認定試験 日本語問題集

Anthropic の Claude 認定試験（CCDV-F・CCAR-P）の練習問題を日本語に訳し、
スマホで解けるようにした非公式の問題集アプリです。

- **CCDV-F**（Claude Certified Developer – Foundations）：180問（2026/12/06 以前の試験ガイドに対応）
- **CCAR-P**（Claude Certified Architect – Professional）：228問（2026/12/06 以前の試験ガイドに対応）

どちらの試験も、2026/12/07 から試験ガイドが改訂され、出題範囲・分野の配分・問題数が変わります。
この問題集は改訂後の試験には対応していません。改訂後の試験に対応するときは、アプリの中で別の試験（例：「CCDV-F（2026/12/07 以降）」）として追加します。

問題は MIT ライセンスで公開されている問題集を和訳したものです。出典と著作権表示は [NOTICE.md](NOTICE.md) を参照してください。
本番の試験問題ではありません。Anthropic とは関係のない、個人の学習用プロジェクトです。

## 使い方

GitHub Pages で公開した URL をスマホで開き、「ホーム画面に追加」してください。一度開けばオフラインでも使えます。

## 開発

ルールと分担は [AGENTS.md](AGENTS.md) にまとめています。
Python などは Docker コンテナの中で動かします（Docker と Docker Compose が必要です）。

```bash
./dev check    # テスト → 検証 → ビルド
./dev serve    # http://localhost:8000 で確認
./dev help     # すべてのコマンド
```
