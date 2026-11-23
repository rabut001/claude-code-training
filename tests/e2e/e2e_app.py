"""アプリの E2E テスト（Playwright + Chromium。コンテナで実行する）。

    ./dev e2e

サンプル問題（tests/fixtures/questions）でビルドしたアプリを一時フォルダに用意し、
スマホと同じ画面幅（390×844）のブラウザで操作して確かめる。
"""
import functools
import http.server
import json
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import build  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "questions"
VIEWPORT = {"width": 390, "height": 844}


def fixture_questions():
    qs = {}
    for p in FIXTURES.rglob("*.json"):
        q = json.loads(p.read_text(encoding="utf-8"))
        qs[q["id"]] = q
    return qs


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


class AppTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.site = cls.tmp / "app"
        shutil.copytree(ROOT / "app", cls.site, ignore=shutil.ignore_patterns("data"))
        assert build.build(ROOT / "data", FIXTURES, cls.site / "data") == 0
        handler = functools.partial(QuietHandler, directory=str(cls.site))
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        # Service Worker は localhost でだけ登録されるので、127.0.0.1 ではなく localhost を使う
        cls.url = f"http://localhost:{cls.server.server_address[1]}/"
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()
        cls.questions = fixture_questions()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        shutil.rmtree(cls.tmp)

    def setUp(self):
        self.context = self.browser.new_context(viewport=VIEWPORT, locale="ja-JP", service_workers="block")
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.page.on("console", lambda m: self.errors.append(m.text) if m.type == "error" else None)
        self.page.on("dialog", lambda d: d.accept())
        # 選択肢の並びを固定して、正解の位置が分かるようにする
        self.page.add_init_script(
            "if (!localStorage.getItem('ccq:v1:settings')) localStorage.setItem('ccq:v1:settings', JSON.stringify({lang:'ja', shuffleOptions:false}));"
        )

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [], "ブラウザでエラーが出ています")

    # ---- 道具 ----
    def open(self, hash_="#/"):
        self.page.goto(self.url + hash_)

    def session(self):
        return self.page.evaluate("JSON.parse(localStorage.getItem('ccq:v1:session'))")

    def current_question(self):
        s = self.session()
        return self.questions[s["ids"][s["index"]]]

    def click_options(self, letters):
        for letter in letters:
            idx = ord(letter) - ord("a")
            self.page.locator(".option").nth(idx).click()

    def wrong_letters(self, q):
        ids = [o["id"] for o in q["en"]["options"]]
        wrong = [i for i in ids if i not in q["answer"]]
        return wrong[: q["select"]]

    # ---- テスト ----
    def test_home_lists_exams(self):
        self.open()
        cards = self.page.locator("a.card")
        expect(cards).to_have_count(2)
        expect(cards.nth(0)).to_contain_text("CCDV-F")
        expect(cards.nth(0)).to_contain_text("2問")
        expect(cards.nth(1)).to_contain_text("CCAR-P")
        expect(cards.nth(1)).to_contain_text("和訳済み 0問")

    def test_quick_quiz_records_progress(self):
        self.open("#/exam/ccdv-f")
        self.page.get_by_role("button", name="クイック10問").click()
        expect(self.page.locator(".counter")).to_have_text("1 / 2")

        results = []
        for i in range(2):
            q = self.current_question()
            answer_right = i == 0
            letters = sorted(q["answer"]) if answer_right else self.wrong_letters(q)
            submit = self.page.locator(".actions .btn--primary")
            if q["type"] == "multi":
                self.click_options(letters[:1])
                expect(submit).to_have_text("あと1つ選んでください")
                expect(submit).to_be_disabled()
                self.click_options(letters[1:])
            else:
                self.click_options(letters)
            expect(submit).to_have_text("回答する")
            submit.click()
            expect(self.page.locator(".verdict")).to_have_text("正解" if answer_right else "不正解")
            expect(self.page.locator(".explain")).to_be_visible()
            results.append((q["id"], answer_right))
            self.page.locator(".actions .btn--primary").click()  # 次の問題へ／結果を見る

        expect(self.page).to_have_url(self.url + "#/result")
        expect(self.page.locator(".score__num")).to_have_text("50")
        expect(self.page.get_by_role("button", name="まちがえた 1問を解き直す")).to_be_visible()

        progress = self.page.evaluate("JSON.parse(localStorage.getItem('ccq:v1:progress:ccdv-f'))")
        self.assertEqual({k: v["last"] for k, v in progress.items()}, dict(results))
        self.assertIsNone(self.session(), "終わったセッションは消える")

        self.open("#/exam/ccdv-f")
        expect(self.page.locator(".summary__foot")).to_contain_text("前回正解 1 / 2問")
        expect(self.page.get_by_role("button", name="間違えた問題の復習")).to_be_enabled()

    def test_untranslated_question_falls_back_to_english(self):
        self.open("#/exam/ccar-p")
        self.page.get_by_role("button", name="クイック10問").click()
        expect(self.page.locator(".qcard")).to_contain_text("未訳のため英語で表示")
        expect(self.page.locator(".qtext")).to_contain_text("An onboarding team asks for a Claude chatbot")

    def test_language_toggle(self):
        self.open("#/exam/ccdv-f")
        self.page.get_by_role("button", name="クイック10問").click()
        q = self.current_question()
        expect(self.page.locator(".qtext")).to_have_text(q["ja"]["question"])
        self.page.get_by_role("button", name="表示する言語を切り替える").click()
        expect(self.page.locator(".qtext")).to_have_text(q["en"]["question"])
        expect(self.page.locator(".qcard")).to_have_attribute("lang", "en")

    def test_mock_exam_without_answers(self):
        self.open("#/exam/ccdv-f")
        self.page.get_by_role("button", name="本番形式の模試").click()
        expect(self.page.locator(".timer")).to_contain_text("残り")
        expect(self.page.locator(".verdict")).to_have_count(0)
        # サンプルは d2 と d7 に1問ずつなので、模試も2問になる
        expect(self.page.locator(".counter")).to_have_text("1 / 2")
        self.page.get_by_role("button", name="ここで採点する").click()  # 未回答の確認ダイアログは accept
        expect(self.page).to_have_url(self.url + "#/result")
        expect(self.page.locator(".score__num")).to_have_text("0")
        expect(self.page.locator(".judge")).to_contain_text("合格の目安（69%）")

    def test_mock_answers_are_kept_when_moving(self):
        self.open("#/exam/ccdv-f")
        self.page.get_by_role("button", name="本番形式の模試").click()
        q = self.current_question()
        self.click_options(sorted(q["answer"]))
        self.page.get_by_role("button", name="次へ").click()
        self.page.get_by_role("button", name="前へ").click()
        for letter in q["answer"]:
            expect(self.page.locator(".option").nth(ord(letter) - ord("a"))).to_have_attribute("aria-checked", "true")

    def test_resume_after_reload(self):
        self.open("#/exam/ccdv-f")
        self.page.get_by_role("button", name="本番形式の模試").click()
        self.click_options(["a"])
        self.open("#/")
        self.page.reload()
        resume = self.page.locator(".card--resume")
        expect(resume).to_contain_text("続きから")
        expect(resume).to_contain_text("1 / 2問 回答済み")
        resume.click()
        expect(self.page.locator(".timer")).to_be_visible()

    def test_settings_shows_notice(self):
        self.open("#/settings")
        notice = self.page.locator(".notice")
        expect(notice).to_contain_text("Breeganzo/CCDV-F-Preparation")
        expect(notice).to_contain_text("MIT License")
        self.page.get_by_role("radio", name="英語（本番と同じ）").click()
        settings = self.page.evaluate("JSON.parse(localStorage.getItem('ccq:v1:settings'))")
        self.assertEqual(settings["lang"], "en")

    def test_quiz_logic(self):
        self.open()
        out = self.page.evaluate(
            """async () => {
              const m = await import('./src/quiz.js');
              const q = { answer: ['a', 'c'] };
              const exam = { domains: [{ id: 'd1', mock_items: 2 }, { id: 'd2', mock_items: 1 }] };
              const qs = [{ id: '1', domain: 'd1' }, { id: '2', domain: 'd1' }, { id: '3', domain: 'd1' }, { id: '4', domain: 'd2' }];
              const mock = m.pickMock(exam, qs);
              const prog = { '1': { last: true }, '2': { last: false } };
              const order = m.prioritize(qs, prog).map((x) => x.id);
              return {
                exact: m.isCorrect(q, ['c', 'a']),
                partial: m.isCorrect(q, ['a']),
                extra: m.isCorrect(q, ['a', 'b', 'c']),
                mockD1: mock.filter((x) => x.domain === 'd1').length,
                mockD2: mock.filter((x) => x.domain === 'd2').length,
                firstTwoUnseen: order.slice(0, 2).every((id) => id === '3' || id === '4'),
                thenWrong: order[2] === '2',
                lastRight: order[3] === '1',
              };
            }"""
        )
        self.assertEqual(
            out,
            {"exact": True, "partial": False, "extra": False, "mockD1": 2, "mockD2": 1,
             "firstTwoUnseen": True, "thenWrong": True, "lastRight": True},
        )

    def test_works_offline_after_first_visit(self):
        ctx = self.browser.new_context(viewport=VIEWPORT, locale="ja-JP")
        page = ctx.new_page()
        try:
            page.goto(self.url)
            page.evaluate("navigator.serviceWorker.ready.then(() => true)")
            page.reload()  # Service Worker の管理下で読み直す
            page.wait_for_function("navigator.serviceWorker.controller !== null")
            expect(page.locator("a.card")).to_have_count(2)
            ctx.set_offline(True)
            page.reload()
            expect(page.locator("a.card")).to_have_count(2)
            page.locator("a.card").first.click()
            expect(page.get_by_role("button", name="クイック10問")).to_be_visible()
        finally:
            ctx.close()


if __name__ == "__main__":
    unittest.main()
