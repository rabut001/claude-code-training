# Claude認定試験 日本語問題集

Anthropic の Claude 認定試験（CCDV-F・CCAR-P）の練習問題を日本語に訳し、
スマホで解けるようにした非公式の問題集アプリです。

- **CCDV-F**（Claude Certified Developer – Foundations）：180問
- **CCAR-P**（Claude Certified Architect – Professional）：228問

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
