"""tools/validate.py と tools/build.py のテスト。

    python3 -m unittest discover -s tests
"""
import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402
import validate  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "questions"
SINGLE = "ccdv-f/d2/ccdvf-bz-d2-001.json"
MULTI = "ccdv-f/d7/ccdvf-bz-d7-005.json"
TODO = "ccar-p/d1/ccarp-bj-1.1-outcome-before-interface.json"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.qdir = self.tmp / "questions"
        shutil.copytree(FIXTURES, self.qdir)

    def load(self, rel):
        return json.loads((self.qdir / rel).read_text(encoding="utf-8"))

    def save(self, rel, q, *, new_rel=None):
        path = self.qdir / (new_rel or rel)
        if new_rel:
            (self.qdir / rel).unlink()
            path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def errors(self, **kw):
        report, _ = validate.validate(ROOT / "data", self.qdir, **kw)
        return report.errors

    def assertError(self, fragment, **kw):
        errs = self.errors(**kw)
        self.assertTrue(any(fragment in e for e in errs), f"'{fragment}' を含むエラーがありません: {errs}")


class ValidFixtures(Base):
    def test_fixtures_are_valid(self):
        self.assertEqual(self.errors(), [])

    def test_repo_data_is_valid(self):
        report, _ = validate.validate(ROOT / "data", ROOT / "data" / "questions")
        self.assertEqual(report.errors, [])


class InvalidQuestions(Base):
    def test_unknown_field(self):
        q = self.load(SINGLE); q["hint"] = "x"; self.save(SINGLE, q)
        self.assertError("仕様にないフィールド 'hint'")

    def test_answer_not_in_options(self):
        q = self.load(SINGLE); q["answer"] = ["z"]; self.save(SINGLE, q)
        self.assertError("en.options にない id")

    def test_option_ids_must_be_sequential(self):
        q = self.load(SINGLE); q["en"]["options"][1]["id"] = "c"; self.save(SINGLE, q)
        self.assertError("'b' にしてください")

    def test_single_with_two_answers(self):
        q = self.load(SINGLE); q["answer"] = ["a", "b"]; self.save(SINGLE, q)
        self.assertError("single の問題は")

    def test_multi_select_mismatch(self):
        q = self.load(MULTI); q["select"] = 3; self.save(MULTI, q)
        self.assertError("multi の問題は")

    def test_ja_option_ids_must_match_en(self):
        q = self.load(SINGLE); q["ja"]["options"].pop(); self.save(SINGLE, q)
        self.assertError("選択肢の id が en と一致しません")

    def test_ja_note_required_when_en_has_note(self):
        q = self.load(SINGLE); q["ja"]["options"][1]["note"] = ""; self.save(SINGLE, q)
        self.assertError("en に note があるので")

    def test_draft_requires_translation(self):
        q = self.load(TODO); q["ja"] = {"status": "draft"}; self.save(TODO, q)
        self.assertError("必須フィールド 'question'")

    def test_explanation_or_notes_required(self):
        q = self.load(TODO); q["en"]["options"][1]["note"] = ""; self.save(TODO, q)
        self.assertError("explanation が空の場合は")

    def test_newline_rejected(self):
        q = self.load(SINGLE); q["ja"]["question"] = "一行目\n二行目"; self.save(SINGLE, q)
        self.assertError("改行が含まれています")

    def test_wrong_folder(self):
        q = self.load(SINGLE)
        self.save(SINGLE, q, new_rel="ccdv-f/d3/ccdvf-bz-d2-001.json")
        self.assertError("置き場所を ccdv-f/d2/")

    def test_filename_must_match_id(self):
        q = self.load(SINGLE)
        self.save(SINGLE, q, new_rel="ccdv-f/d2/other.json")
        self.assertError("ファイル名を ccdvf-bz-d2-001.json にしてください")

    def test_duplicate_source_question(self):
        q = copy.deepcopy(self.load(SINGLE)); q["id"] = "ccdvf-bz-d2-999"
        self.save(SINGLE, q, new_rel="ccdv-f/d2/ccdvf-bz-d2-999.json")
        (self.qdir / SINGLE).write_text(json.dumps(self.load("ccdv-f/d2/ccdvf-bz-d2-999.json") | {"id": "ccdvf-bz-d2-001"}, ensure_ascii=False), encoding="utf-8")
        self.assertError("同じ元問題")

    def test_commit_must_match_exam_source(self):
        q = self.load(SINGLE); q["source"]["commit"] = "0" * 40; self.save(SINGLE, q)
        self.assertError("commit と一致しません")

    def test_unknown_source_abbr(self):
        q = self.load(SINGLE); q["id"] = "ccdvf-xx-d2-001"
        self.save(SINGLE, q, new_rel="ccdv-f/d2/ccdvf-xx-d2-001.json")
        self.assertError("出典の略号 'xx'")

    def test_non_mit_license(self):
        q = self.load(SINGLE); q["source"]["license"] = "CC-BY-4.0"; self.save(SINGLE, q)
        self.assertError("MIT 以外の出典は使えません")

    def test_broken_json(self):
        (self.qdir / SINGLE).write_text("{", encoding="utf-8")
        self.assertError("JSON の構文エラー")

    def test_supplement_is_optional_and_accepted(self):
        q = self.load(SINGLE)
        q = {**{k: v for k, v in q.items() if k not in ("references", "source")},
             "supplement": {"ja": "{a} が正解です。", "en": "{a} is correct."},
             "references": q["references"], "source": q["source"]}
        self.save(SINGLE, q)
        self.assertEqual(self.errors(), [])

    def test_supplement_rejects_unknown_keys(self):
        q = self.load(SINGLE); q["supplement"] = {"ja": "補足", "en": "note", "fr": "x"}; self.save(SINGLE, q)
        self.assertError("仕様にないフィールド 'fr'")

    def test_supplement_must_not_be_empty(self):
        q = self.load(SINGLE); q["supplement"] = {"ja": " ", "en": "note"}; self.save(SINGLE, q)
        self.assertError("supplement.ja: 空です")

    def test_supplement_requires_ja_and_en(self):
        q = self.load(SINGLE); q["supplement"] = {"ja": "補足"}; self.save(SINGLE, q)
        self.assertError("必須フィールド 'en'")

    def test_supplement_option_ref_must_exist(self):
        q = self.load(SINGLE); q["supplement"] = {"ja": "{z} は誤りです。", "en": "{z} is wrong."}; self.save(SINGLE, q)
        self.assertError("{z} は en.options にない選択肢です")

    def test_strict_counts(self):
        self.assertEqual(self.errors(), [])
        self.assertError("問題数が", strict_counts=True)


class Exams(Base):
    """試験ファイル（data/exams/）の検証。data/ を一時フォルダに複製して書き換える。"""

    def setUp(self):
        super().setUp()
        self.data = self.tmp / "data"
        shutil.copytree(ROOT / "data" / "exams", self.data / "exams")

    def exam(self, exam_id):
        return json.loads((self.data / "exams" / f"{exam_id}.json").read_text(encoding="utf-8"))

    def save_exam(self, ex):
        (self.data / "exams" / f"{ex['id']}.json").write_text(json.dumps(ex, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def errors(self, **kw):
        report, _ = validate.validate(self.data, self.qdir, **kw)
        return report.errors

    def test_repo_exams_are_valid(self):
        self.assertEqual(self.errors(), [])

    def test_edition_is_required(self):
        ex = self.exam("ccdv-f"); del ex["edition"]; self.save_exam(ex)
        self.assertError("必須フィールド 'edition'")

    def test_edition_date_must_exist(self):
        ex = self.exam("ccdv-f"); ex["edition"]["until"] = "2026-02-30"; self.save_exam(ex)
        self.assertError("YYYY-MM-DD の日付か null")

    def test_edition_from_must_not_be_after_until(self):
        ex = self.exam("ccdv-f"); ex["edition"] = {"from": "2026-12-07", "until": "2026-12-06"}; self.save_exam(ex)
        self.assertError("from が until より後")

    def test_question_id_must_use_exam_prefix(self):
        ex = self.exam("ccdv-f"); ex["id_prefix"] = "ccdvx"; self.save_exam(ex)
        self.assertError("'ccdvx-' で始めてください")

    def test_id_prefix_must_be_unique(self):
        ex = self.exam("ccar-p"); ex["id_prefix"] = "ccdvf"; self.save_exam(ex)
        self.assertError("id_prefix 'ccdvf' が複数の試験")

    def test_unknown_exam_option(self):
        self.assertError("試験 'nope' がありません", only_exam="nope")

    def test_new_edition_can_hold_same_source_question(self):
        """試験ガイドの新しい版は別の試験として足す。同じ元問題を二重に持ってよい。"""
        old = self.exam("ccdv-f")
        old["edition"]["until"] = "2026-12-06"
        new = {**copy.deepcopy(old), "id": "ccdv-f-2612", "id_prefix": "ccdvf2612",
               "edition": {"from": "2026-12-07", "until": None}}
        self.save_exam(old)
        self.save_exam(new)
        q = self.load(SINGLE)
        q["id"], q["exam"] = "ccdvf2612-bz-d2-001", "ccdv-f-2612"
        target = self.qdir / "ccdv-f-2612/d2/ccdvf2612-bz-d2-001.json"
        target.parent.mkdir(parents=True)
        target.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        self.assertEqual(self.errors(), [])


class Build(Base):
    def test_build_outputs_bundles(self):
        out = self.tmp / "out"
        self.assertEqual(build.build(ROOT / "data", self.qdir, out), 0)
        index = json.loads((out / "index.json").read_text(encoding="utf-8"))
        counts = {e["id"]: (e["count"], e["translated"]) for e in index["exams"]}
        self.assertEqual(counts, {"ccdv-f": (2, 2), "ccar-p": (1, 0)})
        self.assertEqual(index["exams"][0]["edition"], {"from": None, "until": "2026-12-06"})
        bundle = json.loads((out / "ccdv-f.json").read_text(encoding="utf-8"))
        self.assertEqual([q["id"] for q in bundle["questions"]], ["ccdvf-bz-d2-001", "ccdvf-bz-d7-005"])
        self.assertTrue((out / "NOTICE.md").exists())

    def test_build_is_deterministic(self):
        a, b = self.tmp / "a", self.tmp / "b"
        build.build(ROOT / "data", self.qdir, a)
        build.build(ROOT / "data", self.qdir, b)
        for name in ("index.json", "ccdv-f.json", "ccar-p.json"):
            self.assertEqual((a / name).read_bytes(), (b / name).read_bytes())

    def test_build_stops_on_error(self):
        q = self.load(SINGLE); q["answer"] = ["z"]; self.save(SINGLE, q)
        out = self.tmp / "out"
        self.assertEqual(build.build(ROOT / "data", self.qdir, out), 1)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
