// ホーム：試験の一覧と「続きから」

import { el } from "../util.js";
import { loadIndex, loadExam } from "../data.js";
import { getProgress, getSession } from "../storage.js";
import { overallStats } from "../quiz.js";
import { card, countText, editionLabel, editionNotice, emptyState, examTitle, sessionLabel } from "../components.js";

export async function homeView(ctx) {
  ctx.setTop({ title: "Claude認定資格 問題集", back: null });
  const index = await loadIndex();

  const session = getSession();
  let resume = null;
  if (session) {
    const entry = index.exams.find((e) => e.id === session.exam);
    if (entry) {
      const exam = await loadExam(entry.id);
      const done = session.mode === "mock"
        ? `${session.ids.filter((id) => (session.sel[id] || []).length).length} / ${session.ids.length}問 回答済み`
        : `${Object.keys(session.graded).length} / ${session.ids.length}問 採点済み`;
      resume = card(
        { href: "#/quiz", className: "card--resume" },
        el("p", { class: "card__eyebrow", text: "続きから" }),
        el("p", { class: "card__title", text: `${examTitle(entry)}・${sessionLabel(exam, session)}` }),
        el("p", { class: "card__sub", text: done }),
      );
    }
  }

  const cards = [];
  for (const entry of index.exams) {
    const exam = await loadExam(entry.id);
    const stats = overallStats(exam.exam, exam.questions, getProgress(entry.id));
    const edition = editionLabel(entry.edition);
    const notice = editionNotice(entry.edition);
    cards.push(
      card(
        { href: `#/exam/${entry.id}`, className: "card--exam" },
        el("p", { class: "card__code", text: entry.code }),
        edition ? el("p", { class: "card__edition", text: `${edition}の試験向け` }) : null,
        el("p", { class: "card__en", lang: "en", text: entry.name.en }),
        el("p", { class: "card__count", text: countText(stats.total, stats.seen) }),
        notice ? el("p", { class: "card__alert", text: notice.short }) : null,
      ),
    );
  }

  ctx.render(
    el(
      "div",
      { class: "stack" },
      resume,
      resume ? el("h2", { class: "section-title", text: "試験" }) : null,
      cards.length ? cards : emptyState("問題データがありません", "tools/build.py でデータを生成してください。"),
      el("p", { class: "fineprint" }, "非公式の練習問題です。本番の試験問題ではありません。", el("a", { href: "#/settings" }, "出典とライセンス")),
    ),
  );
}
