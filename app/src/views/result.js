// 結果画面

import { el, percent, formatClock } from "../util.js";
import { loadExam } from "../data.js";
import { getLastResult, getSettings } from "../storage.js";
import { questionCard, emptyState, domainLabel, sessionLabel } from "../components.js";

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
  const rate = percent(result.correct, result.total);
  const unanswered = result.items.filter((i) => !i.answered).length;

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
    { class: "rows" },
    result.byDomain.map((d) =>
      el("li", { class: "row" }, el("span", { class: "row__name", text: d.name.ja }), el("span", { class: "row__value", text: `${d.correct} / ${d.total}` })),
    ),
  );

  const list = el(
    "ol",
    { class: "review-list" },
    result.items.map((item, i) => {
      const q = data.byId.get(item.id);
      if (!q) return null;
      const [tone, mark, label] = item.correct ? ["ok", "○", "正解"] : item.answered ? ["ng", "×", "不正解"] : ["none", "−", "未回答"];
      return el(
        "li",
        {},
        el(
          "details",
          { class: `review review--${tone}` },
          el(
            "summary",
            {},
            el("span", { class: "review__mark", "aria-label": label, text: mark }),
            el("span", { class: "review__no", text: `${i + 1}` }),
            el("span", { class: "review__domain", text: domainLabel(data, q.domain) }),
            el("span", { class: "review__check", "aria-label": item.checked ? "チェック済み" : null, text: item.checked ? "✔" : "" }),
            el("span", { class: "review__chev", "aria-hidden": "true", text: "›" }),
          ),
          questionCard(data, q, { lang, selected: item.selected || [], reveal: true }),
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
        el("p", { class: "summary__sub", text: sessionLabel(data, result) }),
        el("p", { class: "score" }, el("span", { class: "score__num", text: `${rate}` }), el("span", { class: "score__unit", text: "%" })),
        el(
          "p",
          { class: "summary__sub" },
          `${result.total}問中 ${result.correct}問 正解${unanswered ? `・未回答 ${unanswered}問` : ""}・所要時間 ${formatClock(result.finishedAt - result.startedAt)}`,
        ),
        judge,
      ),
      el("a", { class: "btn btn--primary", href: `#/exam/${exam.id}` }, "試験のトップへ"),
      el("h2", { class: "section-title", text: "分野ごとの結果" }),
      domains,
      el("h2", { class: "section-title", text: "問題ごとの結果（押すと解説）" }),
      list,
    ),
  );
}
