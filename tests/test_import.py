"""tools/import_breeganzo.py の書き出し部分（write_questions）のテスト。

取り込み直したときに、訳済みの ja と補足（supplement）が消えないことを確かめる。
元リポジトリは使わず、問題データを直接渡す。
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
import import_breeganzo  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "questions" / "ccdv-f" / "d2" / "ccdvf-bz-d2-001.json"


class WriteQuestions(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.path = self.tmp / "ccdv-f" / "d2" / "ccdvf-bz-d2-001.json"
        fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        # 取り込み直後の形（未訳）
        self.fresh = copy.deepcopy(fixture)
        self.fresh["ja"] = {"status": "todo"}
        self.translated_ja = fixture["ja"]

    def write(self, question):
        import_breeganzo.write_questions([copy.deepcopy(question)], self.tmp, expected=1)
        return json.loads(self.path.read_text(encoding="utf-8"))

    def test_new_file_is_todo_without_supplement(self):
        out = self.write(self.fresh)
        self.assertEqual(out["ja"], {"status": "todo"})
        self.assertNotIn("supplement", out)

    def test_keeps_translation_and_supplement_in_order(self):
        existing = copy.deepcopy(self.fresh)
        existing["ja"] = self.translated_ja
        existing = import_breeganzo.insert_after(existing, "ja", "supplement", {"ja": "補足です。", "en": "A supplement."})
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        out = self.write(self.fresh)
        self.assertEqual(out["ja"], self.translated_ja)
        self.assertEqual(out["supplement"], {"ja": "補足です。", "en": "A supplement."})
        keys = list(out)
        self.assertEqual(keys.index("supplement"), keys.index("ja") + 1)
        # 取り込み直しても中身が変わらない
        self.assertEqual(self.path.read_text(encoding="utf-8"), json.dumps(existing, ensure_ascii=False, indent=2) + "\n")

    def test_keeps_supplement_even_when_untranslated(self):
        existing = import_breeganzo.insert_after(copy.deepcopy(self.fresh), "ja", "supplement", {"ja": "補足です。", "en": "A supplement."})
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        out = self.write(self.fresh)
        self.assertEqual(out["ja"], {"status": "todo"})
        self.assertEqual(out["supplement"], {"ja": "補足です。", "en": "A supplement."})

    def test_rejects_broken_supplement(self):
        existing = copy.deepcopy(self.fresh)
        existing["supplement"] = "補足"
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "supplement が不正"):
            self.write(self.fresh)


if __name__ == "__main__":
    unittest.main()
