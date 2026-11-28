// 試験のトップ：出題モードの選択と分野別ドリル

import { el } from "../util.js";
import { loadExam } from "../data.js";
import { getProgress, getChecks, getSession, setSession, getSettings } from "../storage.js";
import { overallStats, pickQuestions, createSession } from "../quiz.js";
import { card, countText, editionLabel, editionNotice } from "../components.js";

/**
 * 新しいセッションを始めて出題画面へ移る。解いている途中のセッションがあれば確認する。
 * options：pickQuestions に渡すもの（mode, domain, count, pool）
 */
export function startSession(ctx, data, options) {
  const existing = getSession();
  if (existing && (Object.keys(existing.graded).length > 0 || Object.keys(existing.sel).length > 0)) {
    if (!confirm("解いている途中の問題があります。破棄して新しく始めますか？")) return;
  }
  const examId = data.exam.id;
  const picked = pickQuestions(data.exam, data.questions, getProgress(examId), { ...options, checks: getChecks(examId) });
  if (!picked.length) {
    alert("出題できる問題がありません。");
    return;
  }
  setSession(createSession(data.exam, picked, { ...options, shuffleOptions: getSettings().shuffleOptions }));
  ctx.navigate("#/quiz");
}

export async function examView(ctx, examId) {
  const data = await loadExam(examId);
  const exam = data.exam;
  ctx.setTop({ title: exam.code, back: "#/" });

  const stats = overallStats(exam, data.questions, getProgress(examId));
  const edition = editionLabel(exam.edition);
  const notice = editionNotice(exam.edition);
  const mockCount = exam.domains.reduce((n, d) => n + d.mock_items, 0);

  const domains = stats.rows.map((r) =>
    card(
      {
        onClick: () => startSession(ctx, data, { mode: "drill", domain: r.id }),
        className: "card--domain",
      },
      el("p", { class: "card__title", text: r.name.ja }),
      el("p", { class: "card__sub", text: countText(r.total, r.seen) }),
    ),
  );
  domains.forEach((c, i) => {
    if (stats.rows[i].total === 0) c.disabled = true;
  });

  ctx.render(
    el(
      "div",
      { class: "stack" },
      el(
        "section",
        { class: "summary" },
        el("p", { class: "summary__title", lang: "en", text: exam.name.en }),
        edition ? el("p", { class: "summary__edition", text: `${edition}の試験向け` }) : null,
        el("p", { class: "summary__sub", text: countText(stats.total, stats.seen) }),
      ),
      notice ? el("p", { class: "alert", role: "note", text: notice.long }) : null,
      el("h2", { class: "section-title", text: "出題モード" }),
      card(
        { href: `#/quick/${examId}` },
        el("p", { class: "card__title", text: "クイック10問" }),
        el("p", { class: "card__sub", text: "未回答・誤答・チェックした問題から出題" }),
      ),
      card(
        { onClick: () => startSession(ctx, data, { mode: "mock" }) },
        el("p", { class: "card__title", text: "本番形式の模試" }),
        el("p", { class: "card__sub", text: `${mockCount}問・${exam.exam.minutes}分` }),
      ),
      el("h2", { class: "section-title", text: "分野別ドリル（その分野の全問）" }),
      domains,
    ),
  );
}
