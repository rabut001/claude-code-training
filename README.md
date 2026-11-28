# Claude認定試験 日本語問題集

Anthropic の Claude 認定試験（CCDV-F・CCAR-P）の練習問題を日本語に訳し、
スマホで解けるようにした非公式の問題集アプリです。

- **CCDV-F**（Claude Certified Developer – Foundations）：180問
- **CCAR-P**（Claude Certified Architect – Professional）：228問

問題は MIT ライセンスで公開されている問題集を和訳したものです。出典と著作権表示は [NOTICE.md](NOTICE.md) を参照してください。
本番の試験問題ではありません。Anthropic とは関係のない、個人の学習用プロジェクトです。

## 使い方

公開 URL：**https://rabut001.github.io/claude-code-training/**

スマホでこの URL を開き、「ホーム画面に追加」してください。一度開けばオフラインでも使えます。

## 開発

ルールと分担は [AGENTS.md](AGENTS.md) にまとめています。
Python などは Docker コンテナの中で動かします（Docker と Docker Compose が必要です）。

```bash
./dev check    # テスト → 検証 → ビルド
./dev serve    # http://localhost:8000 で確認
./dev help     # すべてのコマンド
```

## ライセンス

このアプリ（コード、ツール、ドキュメント、問題の日本語訳と補足）は [MIT ライセンス](LICENSE) で公開しています。

- 問題の英語の原文の著作権は、元の問題集の作者にあります（どちらも MIT ライセンス）。日本語訳と補足は原文をもとに作ったものなので、問題を利用するときは、[NOTICE.md](NOTICE.md) にある元の問題集の著作権表示とライセンス文も残してください。
- リンク先の外部のドキュメント、試験ガイドからの引用、商標は、このライセンスの対象外です。それぞれの権利者に帰属します。「Claude」は Anthropic, PBC の商標です。
