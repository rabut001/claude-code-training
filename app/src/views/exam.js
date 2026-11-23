// 試験のトップ：出題モードの選択と分野ごとの学習状況

import { el, percent } from "../util.js";
import { loadExam } from "../data.js";
import { getProgress, getSession, setSession, getSettings } from "../storage.js";
import { overallStats, pickQuestions, createSession, wrongQuestions } from "../quiz.js";
import { bar } from "../components.js";

export async function examView(ctx, examId) {
  const data = await loadExam(examId);
  const exam = data.exam;
  ctx.setTop({ title: exam.code, back: "#/" });

  const progress = getProgress(examId);
  const stats = overallStats(exam, data.questions, progress);
  const wrongCount = wrongQuestions(data.questions, progress).length;

  const start = (options) => {
    const existing = getSession();
    if (existing && Object.keys(existing.answers).length > 0) {
      if (!confirm("解いている途中の問題があります。破棄して新しく始めますか？")) return;
    }
    const picked = pickQuestions(exam, data.questions, getProgress(examId), options);
    if (!picked.length) {
      alert("出題できる問題がありません。");
      return;
    }
    const session = createSession(exam, picked, { ...options, shuffleOptions: getSettings().shuffleOptions });
    setSession(session);
    ctx.navigate("#/quiz");
  };

  const modeButton = (title, sub, options, { disabled = false, primary = false } = {}) =>
    el(
      "button",
      { type: "button", class: `mode${primary ? " mode--primary" : ""}`, disabled, onclick: () => start(options) },
      el("span", { class: "mode__title", text: title }),
      el("span", { class: "mode__sub", text: sub }),
    );

  const mockCount = exam.domains.reduce((n, d) => n + d.mock_items, 0);

  const modes = el(
    "section",
    { class: "stack" },
    el("h2", { class: "section-title", text: "出題モード" }),
    modeButton("クイック10問", "まだ解いていない問題・前回まちがえた問題を優先", { mode: "quick", count: 10 }, { primary: true }),
    modeButton(
      "間違えた問題の復習",
      wrongCount ? `前回まちがえた ${wrongCount}問` : "前回まちがえた問題はありません",
      { mode: "review", count: 0 },
      { disabled: wrongCount === 0 },
    ),
    modeButton("本番形式の模試", `${mockCount}問・${exam.exam.minutes}分・分野の配分どおり（途中で答え合わせなし）`, { mode: "mock" }),
  );

  const rows = stats.rows.map((r) =>
    el(
      "li",
      { class: "domain" },
      el(
        "div",
        { class: "domain__head" },
        el("span", { class: "domain__name" }, `${r.name.ja}`),
        el("span", { class: "domain__weight", text: `配分 ${r.weight}%` }),
      ),
      bar(r.mastered, r.total, { label: `${r.name.ja} の正解済みの割合` }),
      el(
        "div",
        { class: "domain__foot" },
        el("span", { text: `前回正解 ${r.mastered} / ${r.total}問${r.wrong ? `・まちがい ${r.wrong}問` : ""}` }),
        el(
          "span",
          { class: "domain__actions" },
          el("button", { type: "button", class: "chip", disabled: r.total === 0, onclick: () => start({ mode: "drill", domain: r.id, count: 10 }) }, "10問"),
          el("button", { type: "button", class: "chip", disabled: r.total === 0, onclick: () => start({ mode: "drill", domain: r.id, count: 0 }) }, "全問"),
        ),
      ),
    ),
  );

  ctx.render(
    el(
      "div",
      { class: "stack" },
      el(
        "section",
        { class: "summary" },
        el("p", { class: "summary__title", text: exam.name.ja }),
        el("p", { class: "summary__sub", text: exam.name.en }),
        bar(stats.mastered, stats.total, { label: "正解済みの割合" }),
        el("p", { class: "summary__foot", text: `前回正解 ${stats.mastered} / ${stats.total}問（${percent(stats.mastered, stats.total)}%）・解いた ${stats.seen}問` }),
      ),
      modes,
      el("section", { class: "stack" }, el("h2", { class: "section-title", text: "分野別ドリル" }), el("ul", { class: "domains" }, rows)),
    ),
  );
}
