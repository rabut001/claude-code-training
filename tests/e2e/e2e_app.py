"""アプリの E2E テスト（Playwright + Chromium。コンテナで実行する）。

    ./dev e2e

サンプル問題（tests/fixtures/questions）でビルドしたアプリを一時フォルダに用意し、
スマホと同じ画面幅（390×844）のブラウザで操作して確かめる。
サンプルは CCDV-F が2問（d2-001：1つ選ぶ、d7-005：2つ選ぶ）、CCAR-P が1問（未訳）。
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
SUPPLEMENT = {"ja": "テスト用の補足です。{c} ではなく {a} を選びます。", "en": "A test supplement. Choose {a}, not {c}."}
SINGLE = "ccdvf-bz-d2-001"
MULTI = "ccdvf-bz-d7-005"


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
        # サンプル問題をコピーし、1問にだけ補足（supplement）を付けてからビルドする
        qdir = cls.tmp / "questions"
        shutil.copytree(FIXTURES, qdir)
        sup_path = qdir / "ccdv-f" / "d7" / f"{MULTI}.json"
        q = json.loads(sup_path.read_text(encoding="utf-8"))
        q = {**{k: v for k, v in q.items() if k not in ("references", "source")},
             "supplement": SUPPLEMENT, "references": q["references"], "source": q["source"]}
        sup_path.write_text(json.dumps(q, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        assert build.build(ROOT / "data", qdir, cls.site / "data") == 0
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
        # 確認ダイアログ：既定では OK を押す。self.accept_dialogs = False にするとキャンセルを押す
        self.accept_dialogs = True
        self.dialogs = []

        def on_dialog(d):
            self.dialogs.append(d.message)
            d.accept() if self.accept_dialogs else d.dismiss()

        self.page.on("dialog", on_dialog)
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

    def preset(self, key, value):
        """ページを開く前に localStorage へ値を入れておく（最初の読み込みのときだけ）"""
        self.page.add_init_script(
            f"if (!sessionStorage.getItem('preset:{key}')) {{ localStorage.setItem('ccq:v1:{key}', {json.dumps(json.dumps(value))}); sessionStorage.setItem('preset:{key}', '1'); }}"
        )

    def stored(self, key):
        return self.page.evaluate(f"JSON.parse(localStorage.getItem('ccq:v1:{key}'))")

    def session(self):
        return self.stored("session")

    def current_question(self):
        s = self.session()
        return self.questions[s["ids"][s["index"]]]

    def click_options(self, letters):
        for letter in letters:
            idx = ord(letter) - ord("a")
            self.page.locator(".option").nth(idx).click()

    def letters_for(self, q, right):
        if right:
            return sorted(q["answer"])
        ids = [o["id"] for o in q["en"]["options"]]
        return [i for i in ids if i not in q["answer"]][: q["select"]]

    def start_quick(self, exam="ccdv-f"):
        self.open(f"#/exam/{exam}")
        self.page.get_by_role("link", name="クイック10問").click()
        expect(self.page).to_have_url(self.url + f"#/quick/{exam}")
        self.page.locator(".btn--primary").click()
        expect(self.page).to_have_url(self.url + "#/quiz")

    def start_mock(self):
        self.open("#/exam/ccdv-f")
        self.page.get_by_role("button", name="本番形式の模試").click()
        expect(self.page).to_have_url(self.url + "#/quiz")

    def btn(self, name):
        return self.page.get_by_role("button", name=name, exact=True)

    def nums(self):
        return self.page.locator(".strip .num")

    # ---- ホーム・試験トップ ----
    def test_home_lists_exams(self):
        self.open()
        expect(self.page.locator("#title")).to_have_text("Claude認定資格 問題集")
        expect(self.page).to_have_title("Claude認定資格 問題集")
        cards = self.page.locator("a.card--exam")
        expect(cards).to_have_count(2)
        expect(cards.nth(0).locator(".card__code")).to_have_text("CCDV-F")
        expect(cards.nth(0).locator(".card__en")).to_have_text("Claude Certified Developer – Foundations")
        expect(cards.nth(0).locator(".card__count")).to_have_text("2問 (回答済: 0問)")
        # 試験ガイドの版は試験ごとに表示する（ホーム全体へのお知らせにはしない）
        expect(cards.nth(0).locator(".card__edition")).to_have_text("2026/12/06 以前の試験向け")
        expect(cards.nth(0).locator(".card__alert")).to_contain_text("範囲")
        expect(cards.nth(1).locator(".card__edition")).to_have_text("2026/12/06 以前の試験向け")
        expect(cards.nth(1).locator(".card__code")).to_have_text("CCAR-P")
        expect(cards.nth(1).locator(".card__count")).to_have_text("1問 (回答済: 0問)")
        expect(self.page.locator(".bar")).to_have_count(0)  # 進捗バーは出さない

    def test_exam_top(self):
        self.open("#/exam/ccdv-f")
        expect(self.page.locator(".summary__title")).to_have_text("Claude Certified Developer – Foundations")
        expect(self.page.locator(".summary__sub")).to_have_text("2問 (回答済: 0問)")
        expect(self.page.locator(".summary__edition")).to_have_text("2026/12/06 以前の試験向け")
        expect(self.page.locator(".alert")).to_contain_text("2026/12/06 以前の試験ガイドに基づ")
        domain = self.page.locator(".card--domain").filter(has_text="アプリケーションと統合")
        expect(domain).to_contain_text("1問 (回答済: 0問)")
        expect(domain).to_be_enabled()
        # 問題のない分野は押せない
        expect(self.page.locator(".card--domain").filter(has_text="エージェントとワークフロー")).to_be_disabled()
        expect(self.page.get_by_role("button", name="本番形式の模試")).to_contain_text("問・120分")
        expect(self.page.get_by_text("間違えた問題の復習")).to_have_count(0)

    def test_domain_card_starts_all_questions_of_domain(self):
        self.open("#/exam/ccdv-f")
        self.page.locator(".card--domain").filter(has_text="アプリケーションと統合").click()
        expect(self.page).to_have_url(self.url + "#/quiz")
        s = self.session()
        self.assertEqual((s["mode"], s["domain"], s["ids"]), ("drill", "d2", [SINGLE]))
        expect(self.page.locator("#title")).to_have_text("CCDV-F・アプリケーションと統合")

    # ---- クイック10問 ----
    def test_quick_pool_selection(self):
        self.preset("progress:ccdv-f", {SINGLE: {"n": 1, "ok": 0, "last": False, "at": 1}})
        self.preset("checks:ccdv-f", {MULTI: True})
        self.open("#/quick/ccdv-f")
        rows = self.page.locator(".checkrow")
        expect(rows.nth(0)).to_contain_text("未回答")
        expect(rows.nth(0)).to_contain_text("1問")
        expect(rows.nth(1)).to_contain_text("1問")
        expect(rows.nth(2)).to_contain_text("1問")
        start = self.page.locator(".btn--primary")
        expect(start).to_have_text("2問を始める")

        rows.nth(0).click()  # 未回答を外す
        rows.nth(1).click()  # 誤答を外す → チェックだけ
        expect(rows.nth(0)).to_have_attribute("aria-checked", "false")
        expect(start).to_have_text("1問を始める")
        rows.nth(2).click()  # チェックも外す
        expect(start).to_be_disabled()
        expect(self.page.locator(".hint")).to_have_text("1つ以上選んでください。")

        rows.nth(2).click()
        self.assertEqual(self.stored("settings")["quickPool"], {"unanswered": False, "wrong": False, "checked": True})
        start.click()
        self.assertEqual(self.session()["ids"], [MULTI])

    def test_practice_show_answer_undo_check_and_bulk_grade(self):
        self.start_quick()
        expect(self.nums()).to_have_count(2)
        expect(self.page.locator(".counter")).to_have_text("問1 / 2")
        expect(self.page.locator(".qhead")).not_to_contain_text("アプリケーションと統合")  # 分野は出さない

        q1 = self.current_question()
        self.click_options(self.letters_for(q1, True))
        expect(self.nums().nth(0)).to_have_class("num is-draft is-current")
        self.btn("正解を表示").click()
        expect(self.page.locator(".verdict")).to_have_text("○ 正解")
        expect(self.page.locator(".explain")).to_be_visible()
        expect(self.nums().nth(0)).to_have_attribute("aria-label", "問1、正解")
        self.assertTrue(self.stored("progress:ccdv-f")[q1["id"]]["last"])

        # 採点取消：選んだ選択肢はそのまま、学習記録は採点前（記録なし）に戻る
        self.btn("採点取消").click()
        expect(self.page.locator(".verdict")).to_have_count(0)
        expect(self.page.locator(".explain")).to_have_count(0)
        for letter in q1["answer"]:
            expect(self.page.locator(".option").nth(ord(letter) - ord("a"))).to_have_attribute("aria-checked", "true")
        expect(self.nums().nth(0)).to_have_attribute("aria-label", "問1、選択中")
        self.assertNotIn(q1["id"], self.stored("progress:ccdv-f") or {})
        self.btn("正解を表示").click()
        expect(self.page.locator(".verdict")).to_have_text("○ 正解")

        # 未回答のまま次の問題へ進み、チェックを付ける
        self.btn("次へ").click()
        q2 = self.current_question()
        expect(self.page.locator(".counter")).to_have_text("問2 / 2")
        expect(self.btn("正解を表示")).to_be_disabled()
        check = self.page.get_by_role("checkbox", name="チェック", exact=True)
        check.click()
        expect(check).to_have_attribute("aria-checked", "true")
        expect(self.nums().nth(1).locator(".num__check")).to_have_text("✔")
        self.assertEqual(self.stored("checks:ccdv-f"), {q2["id"]: True})

        # 番号ボタンで問1へ戻れる
        self.nums().nth(0).click()
        expect(self.page.locator(".counter")).to_have_text("問1 / 2")
        expect(self.page.locator(".verdict")).to_have_text("○ 正解")

        self.btn("一括採点").click()
        expect(self.page).to_have_url(self.url + "#/result")
        expect(self.page.locator(".score__num")).to_have_text("50")
        expect(self.page.locator(".summary")).to_contain_text("未回答 1問")
        expect(self.page.locator(".review").nth(1).locator(".review__check")).to_have_text("✔")
        progress = self.stored("progress:ccdv-f")
        self.assertEqual(list(progress), [q1["id"]])
        self.assertIsNone(self.session(), "終わったセッションは消える")

        self.open("#/exam/ccdv-f")
        expect(self.page.locator(".summary__sub")).to_have_text("2問 (回答済: 1問)")

    def test_bulk_grade_grades_selected_questions(self):
        self.start_quick()
        q1 = self.current_question()
        self.click_options(self.letters_for(q1, False))
        self.btn("次へ").click()
        self.btn("一括採点").click()
        expect(self.page).to_have_url(self.url + "#/result")
        expect(self.page.locator(".score__num")).to_have_text("0")
        expect(self.page.locator(".review--ng")).to_have_count(1)
        self.assertEqual({k: v["last"] for k, v in self.stored("progress:ccdv-f").items()}, {q1["id"]: False})

    def test_last_question_goes_to_result_after_grading_all(self):
        self.start_quick()
        for i in range(2):
            q = self.current_question()
            self.click_options(self.letters_for(q, True))
            self.btn("正解を表示").click()
            if i == 0:
                expect(self.btn("結果へ")).to_have_count(0)
                self.btn("次へ").click()
        # 最後の問題では「次へ」が「結果へ」になり、採点したら主ボタンの色になる
        expect(self.btn("次へ")).to_have_count(0)
        expect(self.btn("結果へ")).to_have_class("btn btn--primary")
        self.btn("結果へ").click()
        expect(self.page).to_have_url(self.url + "#/result")
        expect(self.page.locator(".score__num")).to_have_text("100")
        self.assertEqual(self.dialogs, [], "全問を採点済みなら確認しない")

    def test_last_question_result_button_asks_about_unanswered(self):
        self.start_quick()
        self.btn("次へ").click()  # 問1は未回答のまま
        result = self.btn("結果へ")
        expect(result).to_have_class("btn")  # 最後の問題を採点するまでは普通の色
        self.accept_dialogs = False
        result.click()
        expect(self.page).to_have_url(self.url + "#/quiz")  # キャンセルしたら残る
        self.assertEqual(self.dialogs, ["未回答の 2問は未回答のままです。結果画面へ進みますか？"])

        q = self.current_question()
        self.click_options(self.letters_for(q, True))  # 選んだが、正解は表示しない
        self.accept_dialogs = True
        result.click()
        expect(self.page).to_have_url(self.url + "#/result")
        self.assertEqual(
            self.dialogs[1], "選んだまま正解を表示していない 1問を採点します。未回答の 1問は未回答のままです。結果画面へ進みますか？"
        )
        expect(self.page.locator(".score__num")).to_have_text("50")

    def test_multi_needs_the_right_number_of_choices(self):
        self.open("#/exam/ccdv-f")
        self.page.locator(".card--domain").filter(has_text="セキュリティと安全性").click()
        expect(self.page.locator(".qneed")).to_have_text("選択肢から2つ選ぶ")
        show = self.btn("正解を表示")
        self.click_options(["a"])
        expect(self.page.locator(".bottombar__hint")).to_have_text("あと1つ選んでください")
        expect(show).to_be_disabled()
        self.click_options(["b"])
        expect(show).to_be_enabled()
        expect(show).to_have_class("btn btn--primary")

    def test_supplement_is_shown_after_answering(self):
        # 選択肢の並びを入れ替える設定にして、{a}・{c} が画面の記号に置き換わることを確かめる
        self.page.add_init_script(
            "localStorage.setItem('ccq:v1:settings', JSON.stringify({lang:'ja', shuffleOptions:true}));"
        )
        self.open("#/exam/ccdv-f")
        self.page.locator(".card--domain").filter(has_text="セキュリティと安全性").click()
        expect(self.page.locator(".supplement")).to_have_count(0)  # 回答前は出さない
        s = self.session()
        qid = s["ids"][s["index"]]
        order = s["order"][qid]
        letter = {oid: chr(ord("A") + i) for i, oid in enumerate(order)}
        q = self.questions[qid]
        for oid in sorted(q["answer"]):
            self.page.locator(".option").nth(order.index(oid)).click()
        self.btn("正解を表示").click()

        sup = self.page.locator(".supplement")
        expect(sup).to_contain_text("補足（このアプリの作成者による追記）")
        expect(sup).to_contain_text(f"テスト用の補足です。{letter['c']} ではなく {letter['a']} を選びます。")
        # 補足の位置は解説の後ろ
        classes = self.page.evaluate("[...document.querySelectorAll('.qcard > *')].map((e) => e.className)")
        self.assertLess(classes.index("explain"), classes.index("supplement"))

        # 英語表示では英語版の補足
        self.page.get_by_role("button", name="表示する言語を切り替える").click()
        expect(sup).to_contain_text("Supplement (added by the author of this app)")
        expect(sup).to_contain_text(f"A test supplement. Choose {letter['a']}, not {letter['c']}.")
        expect(sup).to_have_attribute("lang", "en")

    def test_untranslated_question_falls_back_to_english(self):
        self.start_quick("ccar-p")
        expect(self.page.locator(".qnote")).to_have_text("未訳のため英語で表示しています")
        expect(self.page.locator(".qtext")).to_contain_text("An onboarding team asks for a Claude chatbot")

    def test_language_toggle(self):
        self.start_quick()
        q = self.current_question()
        expect(self.page.locator(".qtext")).to_have_text(q["ja"]["question"])
        toggle = self.page.get_by_role("button", name="表示する言語を切り替える")
        expect(toggle).to_have_text("English")
        toggle.click()
        expect(self.page.locator(".qtext")).to_have_text(q["en"]["question"])
        expect(self.page.locator(".qcard")).to_have_attribute("lang", "en")
        expect(toggle).to_have_text("日本語")

    # ---- 模試 ----
    def test_mock_hides_states_and_overwrites_records(self):
        # 模試の前から付いていたチェック（模試中は出さず、採点のときに模試の状態で上書きされる）
        self.preset("checks:ccdv-f", {SINGLE: True, MULTI: True})
        self.start_mock()
        expect(self.page.locator(".timer")).to_contain_text("残り")
        expect(self.nums()).to_have_count(2)
        expect(self.btn("正解を表示")).to_have_count(0)

        q = self.current_question()
        check = self.page.get_by_role("checkbox", name="チェック", exact=True)
        expect(check).to_have_attribute("aria-checked", "false")
        self.click_options(self.letters_for(q, True))
        check.click()
        expect(check).to_have_attribute("aria-checked", "true")
        # 番号ボタンには、選択中もチェックも出さない
        expect(self.nums().nth(0)).to_have_class("num is-current")
        expect(self.page.locator(".num__check")).to_have_count(0)
        expect(self.page.locator(".verdict")).to_have_count(0)

        self.btn("一括採点").click()  # 未回答の確認ダイアログは accept
        expect(self.page).to_have_url(self.url + "#/result")
        expect(self.page.locator(".score__num")).to_have_text("50")
        expect(self.page.locator(".judge")).to_contain_text("合格の目安（69%）")
        self.assertEqual(self.stored("checks:ccdv-f"), {q["id"]: True})
        self.assertEqual({k: v["last"] for k, v in self.stored("progress:ccdv-f").items()}, {q["id"]: True})

    def test_mock_last_question_goes_to_result(self):
        self.start_mock()
        self.btn("次へ").click()
        result = self.btn("結果へ")
        expect(result).to_have_class("btn")
        q = self.current_question()
        self.click_options(self.letters_for(q, True))
        expect(result).to_have_class("btn btn--primary")  # 選んだら主ボタンの色
        result.click()  # 模試の確認ダイアログは accept
        expect(self.page).to_have_url(self.url + "#/result")
        self.assertEqual(len(self.dialogs), 1)
        self.assertIn("学習記録を上書きしますか", self.dialogs[0])
        expect(self.page.locator(".score__num")).to_have_text("50")

    def test_mock_answers_are_kept_when_moving(self):
        self.start_mock()
        q = self.current_question()
        self.click_options(sorted(q["answer"]))
        self.btn("次へ").click()
        self.btn("前へ").click()
        for letter in q["answer"]:
            expect(self.page.locator(".option").nth(ord(letter) - ord("a"))).to_have_attribute("aria-checked", "true")

    def test_resume_after_reload(self):
        self.start_mock()
        self.click_options(["a"])
        self.open("#/")
        self.page.reload()
        resume = self.page.locator(".card--resume")
        expect(resume).to_contain_text("続きから")
        expect(resume).to_contain_text("CCDV-F（2026/12/06 以前）・本番形式の模試")
        expect(resume).to_contain_text("1 / 2問 回答済み")
        resume.click()
        expect(self.page.locator(".timer")).to_be_visible()

    def test_back_from_practice_keeps_session_without_confirm(self):
        self.start_quick()
        q = self.current_question()
        self.click_options(self.letters_for(q, True))
        self.btn("正解を表示").click()
        expect(self.page.get_by_text("このセッションをやめる")).to_have_count(0)
        self.page.locator("#back").click()
        expect(self.page).to_have_url(self.url + "#/exam/ccdv-f")
        self.assertEqual(self.dialogs, [], "練習では確認を出さない")
        self.assertIsNotNone(self.session(), "セッションは残り、続きから再開できる")
        self.assertIn(q["id"], self.stored("progress:ccdv-f"))

    def test_back_from_mock_asks_and_discards(self):
        self.start_mock()
        self.click_options(["a"])
        back = self.page.locator("#back")
        expect(back).to_be_visible()

        self.accept_dialogs = False  # キャンセル → 模試を続ける
        back.click()
        expect(self.page).to_have_url(self.url + "#/quiz")
        self.assertIn("残り時間もリセット", self.dialogs[-1])
        self.assertIsNotNone(self.session())

        self.accept_dialogs = True  # OK → 中断して試験のトップへ。回答は記録しない
        back.click()
        expect(self.page).to_have_url(self.url + "#/exam/ccdv-f")
        self.assertIsNone(self.session())
        self.assertIsNone(self.stored("progress:ccdv-f"))

    def test_browser_back_from_mock_asks_too(self):
        self.start_mock()
        self.click_options(["a"])

        self.accept_dialogs = False  # ブラウザの「戻る」→ 確認でキャンセル → 模試を続ける
        self.page.go_back()
        expect(self.page.locator(".timer")).to_be_visible()
        self.page.wait_for_function("() => history.state && history.state.mockGuard")
        self.assertEqual(len(self.dialogs), 1)
        self.assertIn("残り時間もリセット", self.dialogs[0])
        expect(self.page).to_have_url(self.url + "#/quiz")
        self.assertIsNotNone(self.session())

        self.accept_dialogs = True  # もう一度「戻る」→ OK → 中断して試験のトップへ
        self.page.go_back()
        expect(self.page).to_have_url(self.url + "#/exam/ccdv-f")
        self.assertEqual(len(self.dialogs), 2)
        self.assertIsNone(self.session())
        self.assertIsNone(self.stored("progress:ccdv-f"))

    def test_browser_back_from_practice_does_not_ask(self):
        self.start_quick()
        self.page.go_back()
        expect(self.page).to_have_url(self.url + "#/quick/ccdv-f")
        self.assertEqual(self.dialogs, [])
        self.assertIsNotNone(self.session())

    def test_old_session_is_discarded(self):
        self.preset("session", {"v": 1, "exam": "ccdv-f", "mode": "review", "ids": [SINGLE], "order": {}, "index": 0, "answers": {}})
        self.open("#/quiz")
        expect(self.page.locator(".empty__title")).to_have_text("解いている問題はありません")
        self.assertIsNone(self.session())

    # ---- 設定・そのほか ----
    def test_settings_shows_notice(self):
        self.open("#/settings")
        notice = self.page.locator(".notice")
        expect(notice).to_contain_text("Breeganzo/CCDV-F-Preparation")
        expect(notice).to_contain_text("MIT License")
        self.page.get_by_role("radio", name="英語（本番と同じ）").click()
        self.assertEqual(self.stored("settings")["lang"], "en")
        expect(self.btn("CCDV-F（2026/12/06 以前） の学習記録を消す")).to_be_visible()

    def test_edition_logic(self):
        self.open()
        out = self.page.evaluate(
            """async () => {
              const c = await import('./src/components.js');
              const old = { from: null, until: '2026-12-06' };
              const next = { from: '2026-12-07', until: null };
              const state = (ed, today) => (c.editionNotice(ed, today) || { state: null }).state;
              return {
                labelOld: c.editionLabel(old),
                labelNext: c.editionLabel(next),
                labelBoth: c.editionLabel({ from: '2026-12-07', until: '2027-12-06' }),
                labelNone: c.editionLabel({ from: null, until: null }),
                title: c.examTitle({ code: 'CCDV-F', edition: next }),
                titleNone: c.examTitle({ code: 'CCDV-F', edition: { from: null, until: null } }),
                lastDay: state(old, '2026-12-06'),
                lastDayText: c.editionNotice(old, '2026-12-06').short,
                dayAfter: state(old, '2026-12-07'),
                beforeStart: state(next, '2026-12-06'),
                started: state(next, '2026-12-07'),
                none: state({ from: null, until: null }, '2026-12-07'),
                monthEnd: c.editionNotice({ from: null, until: '2026-12-31' }, '2026-12-01').short,
                today: /^\\d{4}-\\d{2}-\\d{2}$/.test(c.todayIso()),
              };
            }"""
        )
        self.assertEqual(
            out,
            {"labelOld": "2026/12/06 以前", "labelNext": "2026/12/07 以降", "labelBoth": "2026/12/07〜2027/12/06",
             "labelNone": "", "title": "CCDV-F（2026/12/07 以降）", "titleNone": "CCDV-F",
             "lastDay": "changing", "lastDayText": "2026/12/07 から試験の範囲が変わります", "dayAfter": "outdated",
             "beforeStart": "upcoming", "started": None, "none": None,
             "monthEnd": "2027/01/01 から試験の範囲が変わります", "today": True},
        )

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
              const checks = { '1': true };
              const order = m.prioritize(qs, prog).map((x) => x.id);
              const pool = (p) => m.quickPool(qs, prog, checks, p).map((x) => x.id).sort();
              return {
                exact: m.isCorrect(q, ['c', 'a']),
                partial: m.isCorrect(q, ['a']),
                extra: m.isCorrect(q, ['a', 'b', 'c']),
                mockD1: mock.filter((x) => x.domain === 'd1').length,
                mockD2: mock.filter((x) => x.domain === 'd2').length,
                firstTwoUnseen: order.slice(0, 2).every((id) => id === '3' || id === '4'),
                thenWrong: order[2] === '2',
                lastRight: order[3] === '1',
                poolUnanswered: pool({ unanswered: true }),
                poolWrong: pool({ wrong: true }),
                poolChecked: pool({ checked: true }),
                poolAll: pool({ unanswered: true, wrong: true, checked: true }),
              };
            }"""
        )
        self.assertEqual(
            out,
            {"exact": True, "partial": False, "extra": False, "mockD1": 2, "mockD2": 1,
             "firstTwoUnseen": True, "thenWrong": True, "lastRight": True,
             "poolUnanswered": ["3", "4"], "poolWrong": ["2"], "poolChecked": ["1"], "poolAll": ["1", "2", "3", "4"]},
        )

    def test_works_offline_after_first_visit(self):
        ctx = self.browser.new_context(viewport=VIEWPORT, locale="ja-JP")
        page = ctx.new_page()
        try:
            page.goto(self.url)
            page.evaluate("navigator.serviceWorker.ready.then(() => true)")
            page.reload()  # Service Worker の管理下で読み直す
            page.wait_for_function("navigator.serviceWorker.controller !== null")
            expect(page.locator("a.card--exam")).to_have_count(2)
            ctx.set_offline(True)
            page.reload()
            expect(page.locator("a.card--exam")).to_have_count(2)
            page.locator("a.card--exam").first.click()
            page.get_by_role("link", name="クイック10問").click()
            expect(page.locator(".checkrow")).to_have_count(3)
        finally:
            ctx.close()


if __name__ == "__main__":
    unittest.main()
