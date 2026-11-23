#!/usr/bin/env python3
"""指定コミットの Breeganzo 問題集を取り込む（元の JavaScript は実行しない）。

    ./dev py tools/import_breeganzo.py

先に .cache/upstream/breeganzo で COMMIT を checkout しておく。
LiteralParser と出力処理は import_bajor.py からも利用する。
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
REPO = "Breeganzo/CCDV-F-Preparation"
COMMIT = "f3f7759c4fff3244ff88ae9bafeb1a2a72890180"


class LiteralParser:
    """この出典のデータリテラルだけを読む、小さな再帰下降パーサー。

    JSON の値に加え、引用符のないキー・数値キー・コメント・末尾カンマを
    許可する。文字列は出典で使われる JSON 互換の二重引用符形式に限定し、
    式・関数呼び出し・テンプレート文字列などは受け付けない。
    """

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.decoder = json.JSONDecoder()

    def error(self, message: str) -> ValueError:
        line = self.text.count("\n", 0, self.pos) + 1
        return ValueError(f"{line}行目（位置 {self.pos}）: {message}")

    def skip(self) -> None:
        while self.pos < len(self.text):
            if self.text[self.pos].isspace():
                self.pos += 1
            elif self.text.startswith("//", self.pos):
                end = self.text.find("\n", self.pos + 2)
                self.pos = len(self.text) if end < 0 else end + 1
            elif self.text.startswith("/*", self.pos):
                end = self.text.find("*/", self.pos + 2)
                if end < 0:
                    raise self.error("閉じていないコメント")
                self.pos = end + 2
            else:
                break

    def take(self, token: str) -> bool:
        self.skip()
        if not self.text.startswith(token, self.pos):
            return False
        self.pos += len(token)
        return True

    def expect(self, token: str) -> None:
        if not self.take(token):
            raise self.error(f"{token!r} が必要です")

    def sequence(self, closing: str) -> list:
        values = []
        while not self.take(closing):
            values.append(self.value())
            if self.take(closing):
                break
            self.expect(",")
        return values

    def value(self):
        self.skip()
        if self.take("{"):
            result = {}
            while not self.take("}"):
                self.skip()
                if self.text.startswith('"', self.pos):
                    key, self.pos = self.decoder.raw_decode(self.text, self.pos)
                else:
                    match = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*|[0-9]+").match(self.text, self.pos)
                    if not match:
                        raise self.error("オブジェクトのキーが必要です")
                    key = match.group()
                    self.pos = match.end()
                if key in result:
                    raise self.error(f"キーの重複: {key}")
                self.expect(":")
                result[key] = self.value()
                if self.take("}"):
                    break
                self.expect(",")
            return result
        if self.take("["):
            return self.sequence("]")
        # JSONDecoder はデータリテラルのみを読み、コードを評価しない。
        if self.pos < len(self.text) and self.text[self.pos] in '"-0123456789tfn':
            try:
                value, self.pos = self.decoder.raw_decode(self.text, self.pos)
                return value
            except json.JSONDecodeError as exc:
                raise self.error("未対応または不正なリテラル") from exc
        raise self.error("未対応または不正なリテラル")

    def end(self) -> None:
        self.skip()
        if self.pos != len(self.text):
            raise self.error("データの後ろに未対応の構文があります")


def read_questions(path: Path) -> list[dict]:
    parser = LiteralParser(path.read_text(encoding="utf-8"))
    # ラッパーも既知の構文だけを受け付け、後続のコードを見逃さない。
    for token in ("(", "window", ".", "CCDV_QUESTIONS", "=", "window", ".",
                  "CCDV_QUESTIONS", "||", "[", "]", ")", ".", "push", "("):
        parser.expect(token)
    questions = parser.sequence(")")
    parser.expect(";")
    parser.end()
    if not all(isinstance(q, dict) for q in questions):
        raise ValueError(f"{path}: 問題がオブジェクトではありません")
    return questions


def check_checkout(upstream: Path, commit: str) -> None:
    # コンテナには git を要求しない。指示どおり detached HEAD に固定した
    # clone を受け付ける（元ファイルを変更せずに実行すること）。
    head = upstream / ".git" / "HEAD"
    if head.read_text(encoding="ascii").strip() != commit:
        raise ValueError(f"{upstream}: 先に git checkout {commit} を実行してください")


def text(value: str) -> str:
    """許可された改行の置換と前後の空白除去だけを行う。"""
    return value.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").strip()


def answer_ids(indices: list[int], option_count: int, qtype: str, select: int) -> list[str]:
    if (not isinstance(indices, list) or not indices
            or any(type(i) is not int or not 0 <= i < option_count for i in indices)
            or len(set(indices)) != len(indices)):
        raise ValueError(f"正解番号が不正です: {indices!r}")
    if (qtype not in ("single", "multi") or type(select) is not int
            or select != len(indices)
            or (qtype == "single" and select != 1)
            or (qtype == "multi" and not 2 <= select < option_count)):
        raise ValueError(f"選択形式が不正です: {qtype!r}, select={select!r}")
    return [chr(ord("a") + i) for i in indices]


def insert_after(obj: dict, after: str, key: str, value) -> dict:
    """after のキーのすぐ後ろに key を入れた新しい dict を返す（JSON の並び順をそろえるため）。"""
    out = {}
    for k, v in obj.items():
        if k == key:
            continue
        out[k] = v
        if k == after:
            out[key] = value
    return out


def write_questions(questions: list[dict], output: Path, expected: int) -> None:
    if len(questions) != expected:
        raise ValueError(f"問題数が {len(questions)} です（予定は {expected}）")
    seen = set()
    pending = []
    for question in questions:
        qid = question["id"]
        if not re.fullmatch(r"[a-z0-9.-]+", qid) or qid in seen:
            raise ValueError(f"問題 ID の形式または重複: {qid!r}")
        seen.add(qid)
        domain = question["domain"]
        if not re.fullmatch(r"d[1-8]", domain):
            raise ValueError(f"分野が不正です: {domain!r}")
        path = output / question["exam"] / domain / f"{qid}.json"
        if path.exists():
            existing = json.loads(path.read_text(encoding="utf-8"))
            if existing.get("id") != qid:
                raise ValueError(f"{path}: 既存ファイルの ID が一致しません")
            ja = existing["ja"]
            if not isinstance(ja, dict) or ja.get("status") not in ("todo", "draft", "reviewed"):
                raise ValueError(f"{path}: 既存の ja が不正です。上書きを中止します")
            if ja["status"] != "todo":
                question["ja"] = ja
            # このアプリの作成者による補足（docs/data-format.md「2-4」）も残す。並び順は ja のすぐ後ろ
            if "supplement" in existing:
                supplement = existing["supplement"]
                if not isinstance(supplement, dict) or not isinstance(supplement.get("ja"), str):
                    raise ValueError(f"{path}: 既存の supplement が不正です。上書きを中止します")
                question = insert_after(question, "ja", "supplement", supplement)
        pending.append((path, json.dumps(question, ensure_ascii=False, indent=2) + "\n"))
    # 読み取り・変換のエラーは、書き出しを始める前に検出する。
    for path, body in pending:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    multi = sum(q["type"] == "multi" for q in questions)
    print(f"{questions[0]['exam']}: {len(questions)}問（複数選択 {multi}問） → {output}")
    print("  分野別: " + ", ".join(f"{d}={n}" for d, n in sorted(Counter(q["domain"] for q in questions).items())))


def collect(upstream: Path) -> list[dict]:
    check_checkout(upstream, COMMIT)
    questions = []
    for path in sorted((upstream / "data").glob("questions-*.js")):
        for raw in read_questions(path):
            orig_id = raw["id"]
            if not re.fullmatch(r"D[1-8]-[0-9]{3}", orig_id) or orig_id[1] != str(raw["d"]):
                raise ValueError(f"{path}: 問題 ID と分野が不正です: {orig_id!r}")
            options = raw["opts"]
            answer = answer_ids(raw["correct"], len(options), raw["type"], raw["n"])
            wrong = raw.get("wrong", {})
            if any(not k.isdigit() or not 0 <= int(k) < len(options) for k in wrong):
                raise ValueError(f"{orig_id}: wrong の選択肢番号が不正です")
            doc = raw.get("doc")
            questions.append({
                "schema": 1,
                "id": "ccdvf-bz-" + orig_id.lower(),
                "exam": "ccdv-f",
                "domain": f"d{raw['d']}",
                "subdomain": text(raw["s"]) if raw.get("s") is not None else None,
                "type": raw["type"],
                "select": raw["n"],
                "difficulty": raw.get("diff"),
                "tags": [],
                "answer": answer,
                "en": {
                    "question": text(raw["stem"]),
                    "options": [
                        {"id": chr(ord("a") + i), "text": text(option),
                         "note": text(wrong.get(str(i), ""))}
                        for i, option in enumerate(options)
                    ],
                    "explanation": text(raw.get("why", "")),
                },
                "ja": {"status": "todo"},
                "references": [{"title": text(doc["t"]), "url": doc["u"]}] if doc else [],
                "source": {
                    "repo": REPO, "commit": COMMIT,
                    "path": path.relative_to(upstream).as_posix(),
                    "orig_id": orig_id, "license": "MIT",
                },
            })
    return questions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, default=ROOT / ".cache/upstream/breeganzo")
    parser.add_argument("--out", type=Path, default=ROOT / "data/questions", help="問題フォルダ")
    args = parser.parse_args()
    try:
        write_questions(collect(args.upstream), args.out, expected=180)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"取り込みエラー: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
