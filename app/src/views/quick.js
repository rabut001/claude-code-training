// クイック10問：出題する問題（未回答・誤答・チェック）を選んでから始める

import { el } from "../util.js";
import { loadExam } from "../data.js";
import { getProgress, getChecks, getSettings, setSettings } from "../storage.js";
import { overallStats, quickPool } from "../quiz.js";
import { tick } from "../components.js";
import { startSession } from "./exam.js";

const COUNT = 10;

export async function quickView(ctx, examId) {
  const data = await loadExam(examId);
  const exam = data.exam;
  ctx.setTop({ title: `${exam.code}・クイック10問`, back: `#/exam/${examId}` });

  const progress = getProgress(examId);
  const checks = getChecks(examId);
  const stats = overallStats(exam, data.questions, progress, checks);

  const draw = () => {
    const pool = getSettings().quickPool;
    const n = quickPool(data.questions, progress, checks, pool).length;
    const take = Math.min(COUNT, n);

    const row = (key, label, count) =>
      el(
        "li",
        {},
        el(
          "button",
          {
            type: "button",
            class: "checkrow",
            role: "checkbox",
            "aria-checked": pool[key] ? "true" : "false",
            onclick: () => {
              setSettings({ quickPool: { ...pool, [key]: !pool[key] } });
              draw();
            },
          },
          tick(pool[key]),
          el("span", { class: "checkrow__label", text: label }),
          el("span", { class: "checkrow__count", text: `${count}問` }),
        ),
      );

    const anySelected = pool.unanswered || pool.wrong || pool.checked;
    const message = !anySelected
      ? "1つ以上選んでください。"
      : n === 0
        ? "対象の問題がありません。"
        : `対象の ${n}問から、${take}問をランダムに出題します。`;

    ctx.render(
      el(
        "div",
        { class: "stack" },
        el("h2", { class: "section-title", text: "出題する問題" }),
        el(
          "ul",
          { class: "checks" },
          row("unanswered", "未回答", stats.unanswered),
          row("wrong", "誤答（前回まちがえた問題）", stats.wrong),
          row("checked", "チェックした問題", stats.checked),
        ),
        el("p", { class: "hint", "aria-live": "polite", text: message }),
        el(
          "button",
          {
            type: "button",
            class: "btn btn--primary",
            disabled: n === 0,
            onclick: () => startSession(ctx, data, { mode: "quick", count: COUNT, pool }),
          },
          n ? `${take}問を始める` : "始める",
        ),
      ),
    );
  };

  draw();
}
