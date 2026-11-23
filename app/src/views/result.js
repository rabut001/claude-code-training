// 結果画面

import { el, percent, formatClock } from "../util.js";
import { loadExam } from "../data.js";
import { getLastResult, getSettings, setSession, getSession } from "../storage.js";
import { createSession, MODES } from "../quiz.js";
import { bar, questionCard, emptyState, domainLabel } from "../components.js";

export async function resultView(ctx) {
  const result = getLastResult();
  if (!result) {
    ctx.setTop({ title: "結果", back: "#/" });
    ctx.render(emptyState("まだ結果がありません", null, el("a", { class: "btn", href: "#/" }, "ホームへ")));
    return;
  }
  const data = await loadExam(result.exam);
  const exam = data.exam;
  ctx.setTop({ title: `${exam.code}・結果`, back: `#/exam/${exam.id}` });

  const lang = getSettings().lang;
  const wrongIds = result.items.filter((i) => !i.correct).map((i) => i.id).filter((id) => data.byId.has(id));

  const retry = () => {
    const existing = getSession();
    if (existing && Object.keys(existing.answers).length > 0 && !confirm("解いている途中の問題を破棄して始めますか？")) return;
    const picked = wrongIds.map((id) => data.byId.get(id));
    setSession(createSession(exam, picked, { mode: "review", shuffleOptions: getSettings().shuffleOptions }));
    ctx.navigate("#/quiz");
  };

  const rate = percent(result.correct, result.total);
  let judge = null;
  if (result.mode === "mock") {
    const line = Math.round(result.passEstimate * 100);
    judge = el(
      "p",
      { class: `judge ${result.passed ? "judge--ok" : "judge--ng"}` },
      result.passed ? `合格の目安（${line}%）に届いています` : `合格の目安（${line}%）まで あと${Math.max(0, line - rate)}ポイント`,
    );
  }

  const domains = el(
    "ul",
    { class: "domains" },
    result.byDomain.map((d) =>
      el(
        "li",
        { class: "domain" },
        el("div", { class: "domain__head" }, el("span", { class: "domain__name", text: d.name.ja }), el("span", { class: "domain__weight", text: `${d.correct} / ${d.total}` })),
        bar(d.correct, d.total, { label: `${d.name.ja} の正答率`, tone: d.correct === d.total ? "ok" : "accent" }),
      ),
    ),
  );

  const list = el(
    "ol",
    { class: "review-list" },
    result.items.map((item, i) => {
      const q = data.byId.get(item.id);
      if (!q) return null;
      const mark = item.correct ? "✓" : item.answered ? "✗" : "−";
      return el(
        "li",
        {},
        el(
          "details",
          { class: `review ${item.correct ? "review--ok" : "review--ng"}` },
          el(
            "summary",
            {},
            el("span", { class: "review__mark", "aria-label": item.correct ? "正解" : item.answered ? "不正解" : "未回答", text: mark }),
            el("span", { class: "review__no", text: `${i + 1}` }),
            el("span", { class: "review__domain", text: domainLabel(data, q.domain) }),
          ),
          questionCard(data, q, { lang, selected: item.selected, reveal: true }),
        ),
      );
    }),
  );

  ctx.render(
    el(
      "div",
      { class: "stack" },
      el(
        "section",
        { class: "summary summary--center" },
        el("p", { class: "summary__sub", text: MODES[result.mode]?.label ?? "" }),
        el("p", { class: "score" }, el("span", { class: "score__num", text: `${rate}` }), el("span", { class: "score__unit", text: "%" })),
        el("p", { class: "summary__foot", text: `${result.total}問中 ${result.correct}問 正解・所要時間 ${formatClock(result.finishedAt - result.startedAt)}` }),
        judge,
      ),
      el(
        "div",
        { class: "actions" },
        wrongIds.length
          ? el(
              "button",
              { type: "button", class: "btn btn--primary", onclick: retry },
              result.items.some((i) => !i.answered) ? `まちがえた・未回答の ${wrongIds.length}問を解き直す` : `まちがえた ${wrongIds.length}問を解き直す`,
            )
          : null,
        el("a", { class: "btn", href: `#/exam/${exam.id}` }, "試験のトップへ"),
      ),
      el("section", { class: "stack" }, el("h2", { class: "section-title", text: "分野ごとの結果" }), domains),
      el("section", { class: "stack" }, el("h2", { class: "section-title", text: "問題ごとの結果（押すと解説）" }), list),
    ),
  );
}
