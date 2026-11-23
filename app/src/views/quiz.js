// 出題画面

import { el, formatClock } from "../util.js";
import { loadExam } from "../data.js";
import { getSession, setSession, getSettings, recordAnswer, setLastResult } from "../storage.js";
import { isCorrect, summarize, MODES } from "../quiz.js";
import { questionCard, emptyState } from "../components.js";

export async function quizView(ctx) {
  let session = getSession();
  if (!session) {
    ctx.setTop({ title: "出題", back: "#/" });
    ctx.render(emptyState("解いている問題はありません", "ホームから出題モードを選んでください。", el("a", { class: "btn", href: "#/" }, "ホームへ")));
    return;
  }

  const data = await loadExam(session.exam);
  const exam = data.exam;
  const mode = MODES[session.mode] || MODES.quick;
  const feedback = mode.feedback;
  session.ids = session.ids.filter((id) => data.byId.has(id)); // データの更新で消えた問題を除く
  if (!session.lang) session.lang = getSettings().lang;
  if (session.index >= session.ids.length) session.index = Math.max(0, session.ids.length - 1);

  ctx.setTop({ title: `${exam.code}・${mode.label}`, back: `#/exam/${exam.id}` });

  let pending = []; // 練習モードで、回答する前に選んでいる選択肢

  const save = () => setSession(session);

  const finish = () => {
    if (session.mode === "mock") {
      const at = Date.now();
      for (const id of session.ids) {
        const a = session.answers[id];
        if (a && a.selected.length) recordAnswer(exam.id, id, a.correct, at);
      }
    }
    setLastResult(summarize(session, exam, data.byId));
    setSession(null);
    ctx.navigate("#/result");
  };

  const quit = () => {
    const msg = session.mode === "mock"
      ? "模試をやめますか？（ここまでの回答は記録されません）"
      : "やめますか？（ここまでに回答した問題の記録は残ります）";
    if (!confirm(msg)) return;
    setSession(null);
    ctx.navigate(`#/exam/${exam.id}`);
  };

  // 模試の残り時間
  let timerText = null;
  if (session.deadline) {
    timerText = el("span", { class: "timer", "aria-live": "off" });
    const tick = () => {
      const left = session.deadline - Date.now();
      timerText.textContent = `残り ${formatClock(left)}`;
      timerText.classList.toggle("timer--low", left < 5 * 60 * 1000);
      if (left <= 0) {
        clearInterval(handle);
        alert("時間になりました。採点します。");
        finish();
      }
    };
    const handle = setInterval(tick, 1000);
    ctx.onCleanup(() => clearInterval(handle));
    tick();
  }

  const draw = () => {
    const id = session.ids[session.index];
    const q = data.byId.get(id);
    if (!q) {
      ctx.render(emptyState("問題が見つかりません", "データが更新された可能性があります。", el("button", { class: "btn", type: "button", onclick: quit }, "やめる")));
      return;
    }
    const answered = session.answers[id];
    const reveal = feedback && Boolean(answered);
    const selected = feedback ? (answered ? answered.selected : pending) : answered ? answered.selected : [];
    const last = session.index === session.ids.length - 1;

    const toggle = (optId) => {
      let next;
      if (q.type === "multi") next = selected.includes(optId) ? selected.filter((x) => x !== optId) : [...selected, optId];
      else next = [optId];
      if (feedback) {
        pending = next;
      } else if (next.length) {
        session.answers[id] = { selected: next, correct: isCorrect(q, next) };
        save();
      } else {
        delete session.answers[id];
        save();
      }
      draw();
    };

    const submit = () => {
      const correct = isCorrect(q, pending);
      session.answers[id] = { selected: pending, correct };
      recordAnswer(exam.id, id, correct);
      pending = [];
      save();
      draw();
      window.scrollTo({ top: 0, behavior: "smooth" }); // 正解・不正解は問題の上に出る
    };

    const go = (delta) => {
      session.index = Math.min(Math.max(0, session.index + delta), session.ids.length - 1);
      pending = [];
      save();
      draw();
      window.scrollTo({ top: 0 });
    };

    const grade = () => {
      const unanswered = session.ids.filter((x) => !session.answers[x]).length;
      if (unanswered && !confirm(`未回答が ${unanswered}問あります。採点しますか？`)) return;
      finish();
    };

    const counter = el("span", { class: "counter", text: `${session.index + 1} / ${session.ids.length}` });
    const card = questionCard(data, q, {
      lang: session.lang,
      order: session.order[id],
      selected,
      reveal,
      onToggle: reveal ? null : toggle,
      onLang: () => {
        session.lang = session.lang === "ja" ? "en" : "ja";
        save();
        draw();
      },
    });

    let verdict = null;
    let actions;
    if (feedback) {
      if (reveal) {
        verdict = el(
          "div",
          { class: `verdict ${answered.correct ? "verdict--ok" : "verdict--ng"}`, role: "status" },
          answered.correct ? "正解" : "不正解",
        );
        actions = el(
          "div",
          { class: "actions" },
          el("button", { type: "button", class: "btn btn--primary", onclick: () => (last ? finish() : go(1)) }, last ? "結果を見る" : "次の問題へ"),
        );
      } else {
        const need = q.select - selected.length;
        actions = el(
          "div",
          { class: "actions" },
          el(
            "button",
            { type: "button", class: "btn btn--primary", disabled: need !== 0, onclick: submit },
            need > 0 && q.type === "multi" ? `あと${need}つ選んでください` : need < 0 ? `${q.select}つまで選べます` : "回答する",
          ),
        );
      }
    } else {
      const grid = el(
        "div",
        { class: "grid" },
        session.ids.map((qid, i) =>
          el(
            "button",
            {
              type: "button",
              class: `grid__cell${session.answers[qid] ? " is-done" : ""}${i === session.index ? " is-current" : ""}`,
              "aria-label": `${i + 1}問目${session.answers[qid] ? "（回答済み）" : ""}`,
              onclick: () => go(i - session.index),
            },
            String(i + 1),
          ),
        ),
      );
      actions = el(
        "div",
        { class: "stack" },
        el(
          "div",
          { class: "actions actions--split" },
          el("button", { type: "button", class: "btn", disabled: session.index === 0, onclick: () => go(-1) }, "前へ"),
          last
            ? el("button", { type: "button", class: "btn btn--primary", onclick: grade }, "採点する")
            : el("button", { type: "button", class: "btn btn--primary", onclick: () => go(1) }, "次へ"),
        ),
        el("details", { class: "jump" }, el("summary", { text: `問題一覧（回答済み ${Object.keys(session.answers).length} / ${session.ids.length}）` }), grid),
        el("button", { type: "button", class: "btn btn--ghost", onclick: grade }, "ここで採点する"),
      );
    }

    ctx.render(
      el(
        "div",
        { class: "stack" },
        el("div", { class: "quizbar" }, counter, timerText),
        verdict,
        card,
        actions,
        el("button", { type: "button", class: "linkbtn", onclick: quit }, "やめる"),
      ),
    );
  };

  draw();
}
