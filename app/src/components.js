// 複数の画面で使う部品

import { el, richText, percent } from "./util.js";
import { textOf } from "./data.js";

/** 進み具合のバー */
export function bar(value, max, { label = "", tone = "accent" } = {}) {
  const p = percent(value, max);
  return el(
    "div",
    { class: `bar bar--${tone}`, role: "progressbar", "aria-valuemin": 0, "aria-valuemax": max, "aria-valuenow": value, "aria-label": label },
    el("div", { class: "bar__fill", style: `width:${p}%` }),
  );
}

export function badge(text, tone = "muted") {
  return el("span", { class: `badge badge--${tone}`, text });
}

export function domainLabel(exam, domainId) {
  const d = exam.domains.get ? exam.domains.get(domainId) : exam.exam.domains.find((x) => x.id === domainId);
  return d ? d.name.ja : domainId;
}

/**
 * 問題カード。
 * opts:
 *   lang        表示したい言語（"ja" / "en"）
 *   order       選択肢の並び順（id の配列）
 *   selected    選んでいる選択肢の id の配列
 *   reveal      正解と解説を表示するか
 *   onToggle    選択肢を押したときに呼ぶ（id を渡す）。null なら押せない
 *   onLang      言語切り替えボタンを押したときに呼ぶ。null ならボタンを出さない
 */
export function questionCard(exam, q, { lang, order, selected = [], reveal = false, onToggle = null, onLang = null, header = null }) {
  const t = textOf(q, lang);
  const optById = new Map(t.options.map((o) => [o.id, o]));
  const ids = order && order.length ? order : t.options.map((o) => o.id);
  const multi = q.type === "multi";
  const chosen = new Set(selected);
  const answer = new Set(q.answer);

  const meta = el(
    "div",
    { class: "qmeta" },
    header,
    badge(domainLabel(exam, q.domain)),
    multi ? badge(`${q.select}つ選択`, "warn") : null,
    t.fallback ? badge("未訳のため英語で表示", "muted") : null,
  );

  const langBtn = onLang
    ? el("button", { class: "chip", type: "button", onclick: onLang, "aria-label": "表示する言語を切り替える" }, t.lang === "ja" ? "English" : "日本語")
    : null;

  const list = el("div", { class: "options", role: multi ? "group" : "radiogroup", "aria-label": "選択肢" });
  ids.forEach((id, i) => {
    const o = optById.get(id);
    if (!o) return;
    const isChosen = chosen.has(id);
    const isAnswer = answer.has(id);
    let state = "";
    if (reveal) {
      if (isAnswer) state = "correct";
      else if (isChosen) state = "wrong";
    }
    const mark = reveal ? (isAnswer ? "✓" : isChosen ? "✗" : "") : "";
    const btn = el(
      "button",
      {
        type: "button",
        class: `option${isChosen ? " is-chosen" : ""}${state ? ` is-${state}` : ""}`,
        role: multi ? "checkbox" : "radio",
        "aria-checked": isChosen ? "true" : "false",
        disabled: !onToggle,
        onclick: onToggle ? () => onToggle(id) : null,
      },
      el("span", { class: "option__key", "aria-hidden": "true" }, mark || String.fromCharCode(65 + i)),
      el(
        "span",
        { class: "option__text" },
        richText(o.text),
        reveal && isChosen ? el("span", { class: "option__you", text: "あなたの回答" }) : null,
      ),
    );
    const note = reveal && o.note ? el("p", { class: "option__note" }, richText(o.note)) : null;
    list.append(el("div", { class: "option-wrap" }, btn, note));
  });

  let explanation = null;
  if (reveal) {
    const refs = q.references && q.references.length
      ? el(
          "ul",
          { class: "refs" },
          q.references.map((r) => el("li", {}, el("a", { href: r.url, target: "_blank", rel: "noopener" }, r.title))),
        )
      : null;
    explanation = t.explanation || refs
      ? el("section", { class: "explain" }, el("h3", { text: "解説" }), t.explanation ? el("p", {}, richText(t.explanation)) : null, refs ? el("h3", { text: "参考資料" }) : null, refs)
      : null;
  }

  return el(
    "article",
    { class: "qcard", lang: t.lang },
    el("div", { class: "qcard__head" }, meta, langBtn),
    el("p", { class: "qtext" }, richText(t.question)),
    list,
    explanation,
  );
}

export function emptyState(title, body, action = null) {
  return el("div", { class: "empty" }, el("p", { class: "empty__title", text: title }), body ? el("p", { text: body }) : null, action);
}
