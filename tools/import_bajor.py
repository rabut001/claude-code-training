#!/usr/bin/env python3
"""指定コミットの bajor 問題集を取り込む（元の JavaScript は実行しない）。

    ./dev py tools/import_bajor.py

先に .cache/upstream/bajor で COMMIT を checkout しておく。
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

from import_breeganzo import (
    ROOT, LiteralParser, answer_ids, check_checkout, text, write_questions,
)


REPO = "bajor/claude-architect-professional-quiz"
COMMIT = "05b068db2529b69ea76a2104dae0fd4c197d4d98"
DIFFICULTIES = {"foundational": 1, "intermediate": 2, "advanced": 3}
TYPES = {"single": "single", "multiple": "multi"}


def read_objectives(path: Path) -> dict[str, tuple[int, str]]:
    # blueprint.js の静的な domains 配列だけを読む。
    # 後続の flatMap 等の JavaScript を評価せず、Python で目標 ID を付ける。
    content = path.read_text(encoding="utf-8")
    match = re.search(r"\bconst\s+domains\s*=", content)
    if not match:
        raise ValueError(f"{path}: domains 配列が見つかりません")
    parser = LiteralParser(content)
    parser.pos = match.end()
    domains = parser.value()
    parser.expect(";")
    objectives = {}
    domain_ids = set()
    for domain in domains:
        domain_id = domain["id"]
        if type(domain_id) is not int or not 1 <= domain_id <= 7 or domain_id in domain_ids:
            raise ValueError(f"{path}: 不正または重複する分野: {domain_id!r}")
        domain_ids.add(domain_id)
        for i, statement in enumerate(domain["objectives"], start=1):
            objective_id = f"{domain_id}.{i}"
            objectives[objective_id] = (domain_id, f"{objective_id} {text(statement)}")
    if domain_ids != set(range(1, 8)):
        raise ValueError(f"{path}: 分野が不足しています")
    return objectives


def read_sources(upstream: Path) -> dict[str, dict]:
    sources = {}
    for path in sorted((upstream / "data/sources").glob("*.json")):
        for source in json.loads(path.read_text(encoding="utf-8")):
            source_id = source["id"]
            if source_id in sources:
                raise ValueError(f"{path}: 参考資料 ID の重複: {source_id}")
            sources[source_id] = {"title": text(source["name"]), "url": source["url"]}
    return sources


def collect(upstream: Path) -> list[dict]:
    check_checkout(upstream, COMMIT)
    objectives = read_objectives(upstream / "blueprint.js")
    sources = read_sources(upstream)
    questions = []
    for path in sorted((upstream / "data/questions").glob("*.json")):
        for raw in json.loads(path.read_text(encoding="utf-8")):
            orig_id = raw["id"]
            if not re.fullmatch(r"ccarp-[a-z0-9.-]+", orig_id):
                raise ValueError(f"{path}: 問題 ID が不正です: {orig_id!r}")
            domain, subdomain = objectives[raw["objectiveId"]]
            if raw["domain"] != domain:
                raise ValueError(f"{orig_id}: 目標と分野が一致しません")
            difficulty = raw["difficulty"]
            if difficulty not in DIFFICULTIES:
                raise ValueError(f"{orig_id}: 未対応の difficulty: {difficulty!r}")
            qtype = TYPES[raw["type"]]
            if qtype == "single":
                if "correctIndices" in raw:
                    raise ValueError(f"{orig_id}: single に correctIndices があります")
                indices = [raw["correct"]]
            else:
                if "correct" in raw:
                    raise ValueError(f"{orig_id}: multiple に correct があります")
                indices = raw["correctIndices"]
            options = raw["answers"]
            answer = answer_ids(indices, len(options), qtype, len(indices))
            questions.append({
                "schema": 1,
                "id": "ccarp-bj-" + orig_id.removeprefix("ccarp-"),
                "exam": "ccar-p",
                "domain": f"d{domain}",
                "subdomain": subdomain,
                "type": qtype,
                "select": len(indices),
                "difficulty": DIFFICULTIES[difficulty],
                "tags": raw.get("tags", []),
                "answer": answer,
                "en": {
                    "question": text(raw["prompt"]),
                    "options": [
                        {"id": chr(ord("a") + i), "text": text(option["text"]),
                         "note": text(option["explanation"])}
                        for i, option in enumerate(options)
                    ],
                    "explanation": "",
                },
                "ja": {"status": "todo"},
                "references": [sources[source_id] for source_id in raw["sourceIds"]],
                "source": {
                    "repo": REPO, "commit": COMMIT,
                    "path": path.relative_to(upstream).as_posix(),
                    "orig_id": orig_id, "license": "MIT",
                },
            })
    return questions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, default=ROOT / ".cache/upstream/bajor")
    parser.add_argument("--out", type=Path, default=ROOT / "data/questions", help="問題フォルダ")
    args = parser.parse_args()
    try:
        write_questions(collect(args.upstream), args.out, expected=228)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"取り込みエラー: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
