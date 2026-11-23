// ホーム：試験の一覧と「続きから」

import { el, percent } from "../util.js";
import { loadIndex, loadExam } from "../data.js";
import { getProgress, getSession } from "../storage.js";
import { overallStats, MODES } from "../quiz.js";
import { bar, emptyState } from "../components.js";

export async function homeView(ctx) {
  ctx.setTop({ title: "Claude認定 問題集", back: null });
  const index = await loadIndex();

  const session = getSession();
  let resume = null;
  if (session) {
    const entry = index.exams.find((e) => e.id === session.exam);
    if (entry) {
      const done = Object.keys(session.answers).length;
      resume = el(
        "a",
        { class: "card card--resume", href: "#/quiz" },
        el("p", { class: "card__eyebrow", text: "続きから" }),
        el("p", { class: "card__title", text: `${entry.code}・${MODES[session.mode]?.label ?? ""}` }),
        el("p", { class: "card__sub", text: `${done} / ${session.ids.length}問 回答済み` }),
      );
    }
  }

  const cards = [];
  for (const entry of index.exams) {
    const exam = await loadExam(entry.id);
    const stats = overallStats(exam.exam, exam.questions, getProgress(entry.id));
    cards.push(
      el(
        "a",
        { class: "card", href: `#/exam/${entry.id}` },
        el("p", { class: "card__eyebrow", text: entry.code }),
        el("p", { class: "card__title", text: entry.name.ja }),
        el(
          "p",
          { class: "card__sub" },
          `${entry.count}問`,
          entry.translated < entry.count ? `（和訳済み ${entry.translated}問）` : "",
        ),
        bar(stats.mastered, stats.total, { label: "正解済みの割合" }),
        el("p", { class: "card__foot", text: `前回正解 ${stats.mastered}問・解いた ${stats.seen}問（${percent(stats.seen, stats.total)}%）` }),
      ),
    );
  }

  ctx.render(
    el(
      "div",
      { class: "stack" },
      resume,
      cards.length ? cards : emptyState("問題データがありません", "tools/build.py でデータを生成してください。"),
      el("p", { class: "fineprint" }, "非公式の練習問題です。本番の試験問題ではありません。", el("a", { href: "#/settings" }, "出典とライセンス")),
    ),
  );
}
