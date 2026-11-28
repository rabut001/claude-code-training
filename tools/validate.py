#!/usr/bin/env python3
"""問題データを検証する（仕様: docs/data-format.md）。

使い方（開発用コンテナ経由。AGENTS.md「5. 開発環境とコマンド」）:
    ./dev validate                                             # data/ を検証
    ./dev validate --questions tests/fixtures/questions
    ./dev validate --exam ccdv-f --strict-counts               # 問題数が出典どおりかも確認

エラーが1つでもあれば終了コード 1 を返す。標準ライブラリだけで動くので、
docker が使えない環境では python3 tools/validate.py で直接実行してもよい。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_VERSION = 1
JA_STATUSES = ("todo", "draft", "reviewed")
OPTION_IDS = "abcdef"
ID_RE = re.compile(r"^([a-z][a-z0-9]*)-([a-z]{2})-[a-z0-9][a-z0-9.-]*$")
EXAM_ID_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
ID_PREFIX_RE = re.compile(r"^[a-z][a-z0-9]*$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
DOMAIN_RE = re.compile(r"^d[0-9]+$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")

QUESTION_KEYS = {"schema", "id", "exam", "domain", "subdomain", "type", "select", "difficulty",
                 "tags", "answer", "en", "ja", "supplement", "references", "source"}
QUESTION_REQUIRED = QUESTION_KEYS - {"supplement"}
SUPPLEMENT_KEYS = {"ja", "en"}
OPTION_REF_RE = re.compile(r"\{([a-z])\}")  # 補足の中で選択肢を指す目印（{a} など）
EN_KEYS = {"question", "options", "explanation"}
JA_KEYS = {"status", "question", "options", "explanation"}
OPTION_KEYS = {"id", "text", "note"}
SOURCE_KEYS = {"repo", "commit", "path", "orig_id", "license"}
REFERENCE_KEYS = {"title", "url"}
EXAM_KEYS = {"schema", "id", "code", "name", "edition", "id_prefix", "exam", "domains", "sources"}
EDITION_KEYS = {"from", "until"}
EXAM_INFO_KEYS = {"questions", "minutes", "pass_scaled", "scale_min", "scale_max", "pass_raw_estimate"}
DOMAIN_KEYS = {"id", "name", "weight", "mock_items"}
EXAM_SOURCE_KEYS = {"abbr", "repo", "commit", "license", "questions"}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


@dataclass
class Dataset:
    exams: dict[str, dict]
    questions: list[tuple[Path, dict]]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def nonempty_str(v) -> bool:
    return isinstance(v, str) and v.strip() != ""


def check_keys(r: Report, where: str, obj, allowed: set[str], required: set[str] | None = None) -> bool:
    if not isinstance(obj, dict):
        r.error(where, "オブジェクトではありません")
        return False
    required = allowed if required is None else required
    for k in sorted(required - obj.keys()):
        r.error(where, f"必須フィールド '{k}' がありません")
    for k in sorted(obj.keys() - allowed):
        r.error(where, f"仕様にないフィールド '{k}' があります")
    return True


def check_text(r: Report, where: str, v, *, allow_empty: bool = False) -> None:
    if not isinstance(v, str):
        r.error(where, "文字列ではありません")
        return
    if not allow_empty and v.strip() == "":
        r.error(where, "空です")
    if "\n" in v or "\r" in v:
        r.error(where, "改行が含まれています（半角スペースに置き換えてください）")
    if v != v.strip():
        r.warn(where, "前後に空白があります")


def load_json(r: Report, path: Path):
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        r.error(rel(path), "UTF-8 として読めません")
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        r.error(rel(path), f"JSON の構文エラー（{e.lineno}行 {e.colno}列）: {e.msg}")
        return None
    if not text.endswith("\n"):
        r.warn(rel(path), "末尾に改行がありません")
    return data


# ---------------------------------------------------------------- 試験ファイル

def check_i18n(r: Report, where: str, v) -> None:
    if check_keys(r, where, v, {"en", "ja"}):
        for lang in ("en", "ja"):
            if lang in v:
                check_text(r, f"{where}.{lang}", v[lang])


def check_date(r: Report, where: str, v) -> bool:
    """YYYY-MM-DD の実在する日付か。null は呼び出し側で扱う。"""
    if isinstance(v, str) and DATE_RE.match(v):
        try:
            date.fromisoformat(v)
            return True
        except ValueError:
            pass
    r.error(where, f"YYYY-MM-DD の日付か null にしてください: {v!r}")
    return False


def check_edition(r: Report, where: str, ed) -> None:
    """その試験ガイドで受験できる期間。from・until は両端を含む。決まっていない側は null。"""
    if not check_keys(r, where, ed, EDITION_KEYS):
        return
    ok = {k: ed.get(k) is None or check_date(r, f"{where}.{k}", ed.get(k)) for k in ("from", "until")}
    if ok["from"] and ok["until"] and ed.get("from") and ed.get("until") and ed["from"] > ed["until"]:
        r.error(where, "from が until より後になっています")


def check_exam(r: Report, path: Path, ex: dict) -> None:
    w = rel(path)
    if not check_keys(r, w, ex, EXAM_KEYS):
        return
    if ex.get("schema") != SCHEMA_VERSION:
        r.error(w, f"schema は {SCHEMA_VERSION} にしてください")
    if not isinstance(ex.get("id"), str) or not EXAM_ID_RE.match(ex["id"]):
        r.error(w, f"id が不正です: {ex.get('id')!r}（英小文字・数字をハイフンでつないだもの）")
    elif path.stem != ex["id"]:
        r.error(w, f"ファイル名と id が一致しません（{ex['id']}.json にしてください）")
    if not nonempty_str(ex.get("code")):
        r.error(f"{w}.code", "空です")
    if "name" in ex:
        check_i18n(r, f"{w}.name", ex["name"])
    if "id_prefix" in ex and (not isinstance(ex["id_prefix"], str) or not ID_PREFIX_RE.match(ex["id_prefix"])):
        r.error(f"{w}.id_prefix", f"英小文字で始まる英小文字・数字にしてください: {ex['id_prefix']!r}")
    if "edition" in ex:
        check_edition(r, f"{w}.edition", ex["edition"])

    info = ex.get("exam")
    if check_keys(r, f"{w}.exam", info, EXAM_INFO_KEYS):
        for k in EXAM_INFO_KEYS - {"pass_raw_estimate"}:
            if k in info and not is_int(info[k]):
                r.error(f"{w}.exam.{k}", "整数ではありません")
        p = info.get("pass_raw_estimate")
        if not isinstance(p, (int, float)) or isinstance(p, bool) or not 0 < p <= 1:
            r.error(f"{w}.exam.pass_raw_estimate", "0より大きく1以下の数にしてください")

    domains = ex.get("domains")
    if not isinstance(domains, list) or not domains:
        r.error(f"{w}.domains", "1つ以上の分野が必要です")
    else:
        ids = []
        for i, d in enumerate(domains):
            dw = f"{w}.domains[{i}]"
            if not check_keys(r, dw, d, DOMAIN_KEYS):
                continue
            if not isinstance(d.get("id"), str) or not DOMAIN_RE.match(d["id"]):
                r.error(f"{dw}.id", f"d1, d2, … の形にしてください: {d.get('id')!r}")
            ids.append(d.get("id"))
            if "name" in d:
                check_i18n(r, f"{dw}.name", d["name"])
            if not isinstance(d.get("weight"), (int, float)) or isinstance(d.get("weight"), bool) or d["weight"] <= 0:
                r.error(f"{dw}.weight", "正の数にしてください")
            if not is_int(d.get("mock_items")) or d["mock_items"] < 0:
                r.error(f"{dw}.mock_items", "0以上の整数にしてください")
        for dup, n in Counter(ids).items():
            if n > 1:
                r.error(f"{w}.domains", f"分野ID '{dup}' が重複しています")
        if isinstance(info, dict) and is_int(info.get("questions")):
            total = sum(d.get("mock_items", 0) for d in domains if isinstance(d, dict) and is_int(d.get("mock_items")))
            if total != info["questions"]:
                r.error(f"{w}.domains", f"mock_items の合計（{total}）が exam.questions（{info['questions']}）と一致しません")
        weight = sum(d.get("weight", 0) for d in domains if isinstance(d, dict) and isinstance(d.get("weight"), (int, float)))
        if abs(weight - 100) > 0.5:
            r.warn(f"{w}.domains", f"weight の合計が {weight:g} です（100 になる想定）")

    sources = ex.get("sources")
    if not isinstance(sources, list) or not sources:
        r.error(f"{w}.sources", "1つ以上の出典が必要です")
    else:
        abbrs = []
        for i, s in enumerate(sources):
            sw = f"{w}.sources[{i}]"
            if not check_keys(r, sw, s, EXAM_SOURCE_KEYS):
                continue
            abbrs.append(s.get("abbr"))
            if not isinstance(s.get("abbr"), str) or not re.fullmatch(r"[a-z]{2}", s["abbr"]):
                r.error(f"{sw}.abbr", "英小文字2文字にしてください")
            if not isinstance(s.get("commit"), str) or not COMMIT_RE.match(s["commit"]):
                r.error(f"{sw}.commit", "40桁の commit ハッシュにしてください")
            if s.get("license") != "MIT":
                r.error(f"{sw}.license", "MIT 以外の出典は使えません（AGENTS.md）")
            if not is_int(s.get("questions")) or s["questions"] < 0:
                r.error(f"{sw}.questions", "0以上の整数にしてください")
        for dup, n in Counter(abbrs).items():
            if n > 1:
                r.error(f"{w}.sources", f"abbr '{dup}' が重複しています")


# ---------------------------------------------------------------- 問題ファイル

def check_options(r: Report, where: str, opts, *, expect_ids: list[str] | None = None) -> list[str]:
    if not isinstance(opts, list):
        r.error(where, "配列ではありません")
        return []
    if not 2 <= len(opts) <= len(OPTION_IDS):
        r.error(where, f"選択肢は2〜{len(OPTION_IDS)}個にしてください（いま {len(opts)} 個）")
    ids = []
    for i, o in enumerate(opts):
        ow = f"{where}[{i}]"
        if not check_keys(r, ow, o, OPTION_KEYS):
            continue
        ids.append(o.get("id"))
        if i < len(OPTION_IDS) and o.get("id") != OPTION_IDS[i]:
            r.error(f"{ow}.id", f"'{OPTION_IDS[i]}' にしてください（a, b, c, … の順）")
        if "text" in o:
            check_text(r, f"{ow}.text", o["text"])
        if "note" in o:
            check_text(r, f"{ow}.note", o["note"], allow_empty=True)
    if expect_ids is not None and ids != expect_ids:
        r.error(where, f"選択肢の id が en と一致しません（en: {expect_ids}、ja: {ids}）")
    return ids


def check_question(r: Report, path: Path, q: dict, exams: dict[str, dict], questions_root: Path) -> None:
    w = rel(path)
    if not check_keys(r, w, q, QUESTION_KEYS, QUESTION_REQUIRED):
        return

    if q.get("schema") != SCHEMA_VERSION:
        r.error(f"{w}.schema", f"{SCHEMA_VERSION} にしてください")

    qid, exam_id, domain = q.get("id"), q.get("exam"), q.get("domain")
    exam = exams.get(exam_id) if isinstance(exam_id, str) else None
    if exam is None:
        r.error(f"{w}.exam", f"data/exams/ にない試験です: {exam_id!r}")

    m = ID_RE.match(qid) if isinstance(qid, str) else None
    if not m:
        r.error(f"{w}.id", f"ID の形式が不正です: {qid!r}（docs/data-format.md の「3. ID の決め方」）")
    else:
        if path.name != f"{qid}.json":
            r.error(w, f"ファイル名を {qid}.json にしてください")
        prefix = exam.get("id_prefix") if exam is not None else None
        if isinstance(prefix, str) and m.group(1) != prefix:
            r.error(f"{w}.id", f"{exam_id} の問題は '{prefix}-' で始めてください")

    if exam is not None:
        domain_ids = [d.get("id") for d in exam.get("domains", []) if isinstance(d, dict)]
        if domain not in domain_ids:
            r.error(f"{w}.domain", f"{exam_id} にない分野です: {domain!r}（{', '.join(map(str, domain_ids))}）")
        try:
            parts = path.resolve().relative_to(questions_root.resolve()).parts
        except ValueError:
            parts = ()
        if len(parts) != 3 or parts[0] != exam_id or parts[1] != domain:
            r.error(w, f"置き場所を {exam_id}/{domain}/{path.name} にしてください")

    if q.get("subdomain") is not None:
        check_text(r, f"{w}.subdomain", q["subdomain"])
    if q.get("difficulty") not in (1, 2, 3, None) or isinstance(q.get("difficulty"), bool):
        r.error(f"{w}.difficulty", "1・2・3・null のどれかにしてください")
    tags = q.get("tags")
    if not isinstance(tags, list) or not all(nonempty_str(t) for t in tags):
        r.error(f"{w}.tags", "空でない文字列の配列にしてください")

    # en
    en = q.get("en")
    en_ids: list[str] = []
    if check_keys(r, f"{w}.en", en, EN_KEYS):
        if "question" in en:
            check_text(r, f"{w}.en.question", en["question"])
        if "explanation" in en:
            check_text(r, f"{w}.en.explanation", en["explanation"], allow_empty=True)
        en_ids = check_options(r, f"{w}.en.options", en.get("options"))

    # answer / type / select
    answer, qtype, select = q.get("answer"), q.get("type"), q.get("select")
    if not isinstance(answer, list) or not answer or not all(isinstance(a, str) for a in answer):
        r.error(f"{w}.answer", "選択肢 id の配列にしてください")
        answer = []
    else:
        if len(set(answer)) != len(answer):
            r.error(f"{w}.answer", "id が重複しています")
        for a in answer:
            if en_ids and a not in en_ids:
                r.error(f"{w}.answer", f"en.options にない id です: {a!r}")
    if qtype not in ("single", "multi"):
        r.error(f"{w}.type", "single か multi にしてください")
    if not is_int(select):
        r.error(f"{w}.select", "整数にしてください")
    elif qtype == "single" and (select != 1 or len(answer) != 1):
        r.error(w, "single の問題は select が 1、answer が1つです")
    elif qtype == "multi":
        if select < 2 or len(answer) != select:
            r.error(w, f"multi の問題は select が2以上で、answer の数（{len(answer)}）と同じです")
        if en_ids and select >= len(en_ids):
            r.error(w, "multi の問題は、選択肢の数が select より多い必要があります")

    if isinstance(en, dict) and en.get("explanation", "") == "" and isinstance(en.get("options"), list):
        notes = {o.get("id"): o.get("note", "") for o in en["options"] if isinstance(o, dict)}
        if any(not nonempty_str(notes.get(a, "")) for a in answer):
            r.error(f"{w}.en", "explanation が空の場合は、正解の選択肢すべてに note が必要です")

    # ja
    ja = q.get("ja")
    if isinstance(ja, dict):
        status = ja.get("status")
        if status not in JA_STATUSES:
            r.error(f"{w}.ja.status", f"{' / '.join(JA_STATUSES)} のどれかにしてください")
        elif status == "todo":
            check_keys(r, f"{w}.ja", ja, JA_KEYS, {"status"})
            if ja.keys() - {"status"}:
                r.warn(f"{w}.ja", "status が todo なのに訳が入っています（訳し終えたら draft にしてください）")
        else:
            if check_keys(r, f"{w}.ja", ja, JA_KEYS):
                if "question" in ja:
                    check_text(r, f"{w}.ja.question", ja["question"])
                check_options(r, f"{w}.ja.options", ja.get("options"), expect_ids=en_ids or None)
                if "explanation" in ja:
                    check_text(r, f"{w}.ja.explanation", ja["explanation"], allow_empty=True)
                if isinstance(en, dict):
                    if nonempty_str(en.get("explanation", "")) and not nonempty_str(ja.get("explanation", "")):
                        r.error(f"{w}.ja.explanation", "en に解説があるので、訳も空にしないでください")
                    en_opts = {o.get("id"): o for o in en.get("options", []) if isinstance(o, dict)}
                    for i, o in enumerate(ja.get("options") or []):
                        if not isinstance(o, dict):
                            continue
                        eo = en_opts.get(o.get("id"), {})
                        if nonempty_str(eo.get("note", "")) and not nonempty_str(o.get("note", "")):
                            r.error(f"{w}.ja.options[{i}].note", "en に note があるので、訳も空にしないでください")
                        if not nonempty_str(eo.get("note", "")) and nonempty_str(o.get("note", "")):
                            r.warn(f"{w}.ja.options[{i}].note", "en に note がないのに訳に note があります")
    else:
        r.error(f"{w}.ja", "オブジェクトではありません（未訳なら {\"status\": \"todo\"}）")

    # supplement（任意。このアプリの作成者による補足）
    if "supplement" in q:
        sup = q["supplement"]
        if check_keys(r, f"{w}.supplement", sup, SUPPLEMENT_KEYS):
            for lang in ("ja", "en"):
                if lang not in sup:
                    continue
                check_text(r, f"{w}.supplement.{lang}", sup[lang])
                if isinstance(sup[lang], str):
                    for ref in OPTION_REF_RE.findall(sup[lang]):
                        if en_ids and ref not in en_ids:
                            r.error(f"{w}.supplement.{lang}", f"{{{ref}}} は en.options にない選択肢です")
            refs_ja = sorted(set(OPTION_REF_RE.findall(sup.get("ja", "") if isinstance(sup.get("ja"), str) else "")))
            refs_en = sorted(set(OPTION_REF_RE.findall(sup.get("en", "") if isinstance(sup.get("en"), str) else "")))
            if refs_ja != refs_en:
                r.warn(f"{w}.supplement", f"ja と en で指している選択肢が違います（ja: {refs_ja}、en: {refs_en}）")

    # references
    refs = q.get("references")
    if not isinstance(refs, list):
        r.error(f"{w}.references", "配列にしてください")
    else:
        for i, ref in enumerate(refs):
            rw = f"{w}.references[{i}]"
            if check_keys(r, rw, ref, REFERENCE_KEYS):
                if "title" in ref:
                    check_text(r, f"{rw}.title", ref["title"])
                if not isinstance(ref.get("url"), str) or not ref["url"].startswith("https://"):
                    r.error(f"{rw}.url", "https:// で始まる URL にしてください")

    # source
    src = q.get("source")
    if check_keys(r, f"{w}.source", src, SOURCE_KEYS):
        for k in ("repo", "path", "orig_id"):
            if not nonempty_str(src.get(k)):
                r.error(f"{w}.source.{k}", "空です")
        if src.get("license") != "MIT":
            r.error(f"{w}.source.license", "MIT 以外の出典は使えません")
        if not isinstance(src.get("commit"), str) or not COMMIT_RE.match(src["commit"]):
            r.error(f"{w}.source.commit", "40桁の commit ハッシュにしてください")
        if exam is not None and m:
            known = {s.get("abbr"): s for s in exam.get("sources", []) if isinstance(s, dict)}
            s = known.get(m.group(2))
            if s is None:
                r.error(f"{w}.id", f"出典の略号 '{m.group(2)}' が data/exams/{exam_id}.json の sources にありません")
            else:
                if src.get("repo") != s.get("repo"):
                    r.error(f"{w}.source.repo", f"'{s.get('repo')}' にしてください（略号 {m.group(2)}）")
                if src.get("commit") != s.get("commit"):
                    r.error(f"{w}.source.commit", f"data/exams/{exam_id}.json の commit と一致しません")


# ---------------------------------------------------------------- 全体

def load_dataset(r: Report, data_dir: Path, questions_dir: Path, only_exam: str | None = None) -> Dataset:
    exams: dict[str, dict] = {}
    exam_dir = data_dir / "exams"
    if not exam_dir.is_dir():
        r.error(rel(exam_dir), "フォルダがありません")
    else:
        for path in sorted(exam_dir.glob("*.json")):
            ex = load_json(r, path)
            if ex is None:
                continue
            check_exam(r, path, ex)
            if isinstance(ex, dict) and isinstance(ex.get("id"), str):
                exams[ex["id"]] = ex
        prefixes = Counter(ex.get("id_prefix") for ex in exams.values() if isinstance(ex.get("id_prefix"), str))
        for dup, n in prefixes.items():
            if n > 1:
                r.error(rel(exam_dir), f"id_prefix '{dup}' が複数の試験で使われています")

    questions: list[tuple[Path, dict]] = []
    if questions_dir.is_dir():
        for path in sorted(questions_dir.rglob("*")):
            if path.is_dir():
                continue
            if path.suffix != ".json":
                if path.name not in (".gitkeep",):
                    r.warn(rel(path), "JSON 以外のファイルがあります")
                continue
            if only_exam and path.relative_to(questions_dir).parts[0] != only_exam:
                continue
            q = load_json(r, path)
            if q is not None:
                questions.append((path, q))
    return Dataset(exams, questions)


def validate(data_dir: Path, questions_dir: Path, *, only_exam: str | None = None,
             strict_counts: bool = False) -> tuple[Report, Dataset]:
    r = Report()
    ds = load_dataset(r, data_dir, questions_dir, only_exam)
    if only_exam and only_exam not in ds.exams:
        r.error(rel(data_dir / "exams"), f"試験 '{only_exam}' がありません（{', '.join(sorted(ds.exams))}）")
    seen: dict[str, Path] = {}
    origin: dict[tuple, Path] = {}
    for path, q in ds.questions:
        check_question(r, path, q, ds.exams, questions_dir)
        if isinstance(q, dict):
            qid = q.get("id")
            if isinstance(qid, str):
                if qid in seen:
                    r.error(rel(path), f"ID '{qid}' が {rel(seen[qid])} と重複しています")
                seen.setdefault(qid, path)
            src = q.get("source")
            if isinstance(src, dict):
                # 試験ガイドの版ごとに試験を分けるので、同じ元問題を別の試験に入れるのはよい
                key = (q.get("exam"), src.get("repo"), src.get("orig_id"))
                if key in origin:
                    r.error(rel(path), f"同じ元問題（{key[1]} {key[2]}）が {rel(origin[key])} にもあります")
                origin.setdefault(key, path)

    for exam_id, ex in ds.exams.items():
        if only_exam and exam_id != only_exam:
            continue
        for s in ex.get("sources", []):
            if not isinstance(s, dict):
                continue
            n = sum(1 for _, q in ds.questions if isinstance(q, dict) and q.get("exam") == exam_id
                    and isinstance(q.get("source"), dict) and q["source"].get("repo") == s.get("repo"))
            if n != s.get("questions"):
                msg = f"{s.get('repo')} の問題数が {n} です（予定は {s.get('questions')}）"
                (r.error if strict_counts else r.warn)(f"data/exams/{exam_id}.json", msg)
    return r, ds


def summarize(ds: Dataset) -> str:
    lines = []
    for exam_id in sorted(ds.exams):
        qs = [q for _, q in ds.questions if isinstance(q, dict) and q.get("exam") == exam_id]
        st = Counter((q.get("ja") or {}).get("status", "?") for q in qs if isinstance(q.get("ja"), dict))
        lines.append(f"  {exam_id}: {len(qs)}問（未訳 {st['todo']}・訳済み {st['draft']}・確認済み {st['reviewed']}）")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="問題データを検証する")
    ap.add_argument("--data", type=Path, default=ROOT / "data", help="data フォルダ（既定: data）")
    ap.add_argument("--questions", type=Path, default=None, help="問題フォルダ（既定: <data>/questions）")
    ap.add_argument("--exam", help="この試験だけを検証する（試験ID。例: ccdv-f）")
    ap.add_argument("--strict-counts", action="store_true", help="問題数が出典の予定数と違えばエラーにする")
    ap.add_argument("-q", "--quiet", action="store_true", help="警告を表示しない")
    args = ap.parse_args(argv)
    questions_dir = args.questions or args.data / "questions"

    r, ds = validate(args.data, questions_dir, only_exam=args.exam, strict_counts=args.strict_counts)
    if r.warnings and not args.quiet:
        print(f"警告 {len(r.warnings)} 件:")
        for m in r.warnings:
            print(f"  ⚠ {m}")
    if r.errors:
        print(f"エラー {len(r.errors)} 件:")
        for m in r.errors:
            print(f"  ✗ {m}")
    print(summarize(ds))
    print("NG" if r.errors else "OK")
    return 1 if r.errors else 0


if __name__ == "__main__":
    sys.exit(main())
