#!/usr/bin/env python3
"""data/ からアプリ用のデータ（app/data/）を生成する。

使い方:
    python3 tools/build.py                                     # data/questions から生成
    python3 tools/build.py --questions tests/fixtures/questions  # サンプル問題で生成

出力:
    app/data/index.json      試験の一覧（問題数、和訳の進み具合、各ファイルの version）
    app/data/<exam>.json     試験の情報と全問題
    app/data/NOTICE.md       出典と著作権表示（アプリの「ライセンス・出典」画面で表示）

先に tools/validate.py と同じ検証を行い、エラーがあれば何も出力しない。
同じ入力からは、いつも同じ出力になる（日時などは含めない）。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate  # noqa: E402

ROOT = validate.ROOT
BUNDLE_SCHEMA = 1


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=False)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def build(data_dir: Path, questions_dir: Path, out_dir: Path) -> int:
    report, ds = validate.validate(data_dir, questions_dir)
    if report.errors:
        print(f"検証エラーが {len(report.errors)} 件あるため、ビルドを中止しました。")
        print("python3 tools/validate.py で内容を確認してください。")
        return 1

    out_resolved = out_dir.resolve()
    if out_resolved in (ROOT, *ROOT.parents) or (out_dir.exists() and not out_dir.is_dir()):
        print(f"出力先が不正です: {out_dir}")
        return 1
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    index_exams = []
    for exam_id in sorted(ds.exams):
        exam = ds.exams[exam_id]
        domain_order = {d["id"]: i for i, d in enumerate(exam["domains"])}
        questions = sorted(
            (q for _, q in ds.questions if q["exam"] == exam_id),
            key=lambda q: (domain_order[q["domain"]], q["id"]),
        )
        body = {"schema": BUNDLE_SCHEMA, "exam": exam, "questions": questions}
        version = digest(dumps(body))
        text = dumps({**body, "version": version})
        (out_dir / f"{exam_id}.json").write_text(text + "\n", encoding="utf-8")

        translated = sum(1 for q in questions if q["ja"]["status"] != "todo")
        index_exams.append({
            "id": exam_id,
            "code": exam["code"],
            "name": exam["name"],
            "file": f"{exam_id}.json",
            "version": version,
            "count": len(questions),
            "translated": translated,
        })
        print(f"  {exam_id}: {len(questions)}問（和訳済み {translated}） → {validate.rel(out_dir / (exam_id + '.json'))}")

    notice = ROOT / "NOTICE.md"
    shutil.copyfile(notice, out_dir / "NOTICE.md")

    index_body = {"schema": BUNDLE_SCHEMA, "exams": index_exams, "notice": "NOTICE.md"}
    index_version = digest(dumps(index_body) + notice.read_text(encoding="utf-8"))
    (out_dir / "index.json").write_text(dumps({**index_body, "version": index_version}) + "\n", encoding="utf-8")
    print(f"  index.json（version {index_version}） → {validate.rel(out_dir / 'index.json')}")
    if report.warnings:
        print(f"（警告が {len(report.warnings)} 件あります。python3 tools/validate.py で確認できます）")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="アプリ用のデータを生成する")
    ap.add_argument("--data", type=Path, default=ROOT / "data", help="data フォルダ（既定: data）")
    ap.add_argument("--questions", type=Path, default=None, help="問題フォルダ（既定: <data>/questions）")
    ap.add_argument("--out", type=Path, default=ROOT / "app" / "data", help="出力先（既定: app/data）")
    args = ap.parse_args(argv)
    return build(args.data, args.questions or args.data / "questions", args.out)


if __name__ == "__main__":
    sys.exit(main())
