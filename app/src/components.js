// 複数の画面で使う部品
//
// 部品の使い分け（どれが押せるかを見た目で分ける）
//   白い角丸の箱（card）……… 押すと別の画面へ移る。右端に › を付ける
//   ボタン（btn）…………… その場で操作する。塗りつぶし（btn--primary）は画面に1つまで
//   チェックボックス（tick）… オン・オフする。色は付けず、黒の ✔ で示す
//   選択肢（option）………… 白い箱。採点後は押せないので、箱をやめて色だけにする
//   枠なし ……………………… 表示するだけのもの
// 色の使い分け
//   青（accent）＝選んでいるもの・いまの問題・主な操作、緑（ok）＝正解、赤（ng）＝不正解・注意・削除、それ以外は黒と灰

import { el, richText } from "./util.js";
import { textOf } from "./data.js";

export function domainLabel(exam, domainId) {
  const d = exam.domains.get ? exam.domains.get(domainId) : exam.exam.domains.find((x) => x.id === domainId);
  return d ? d.name.ja : domainId;
}

/** セッションの名前（上部バーや「続きから」に出す）。分野別ドリルは分野名 */
export function sessionLabel(exam, session) {
  if (session.mode === "drill" && session.domain) return domainLabel(exam, session.domain);
  return { quick: "クイック10問", mock: "本番形式の模試" }[session.mode] || "";
}

// ---- 試験ガイドの版（data/exams/<exam>.json の edition。docs/data-format.md「4-1」） ----
// 試験ガイドの版が違えば別の試験として扱うので、試験名には対応する期間を添える。

/** "2026-12-06" → "2026/12/06" */
function slashDate(iso) {
  return iso.replaceAll("-", "/");
}

/** "2026-12-06" → "2026-12-07" */
function nextDay(iso) {
  const [y, m, d] = iso.split("-").map(Number);
  return new Date(Date.UTC(y, m - 1, d + 1)).toISOString().slice(0, 10);
}

/** この端末の今日の日付（"YYYY-MM-DD"） */
export function todayIso(now = new Date()) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

/** 対応する期間の表示。「2026/12/06 以前」「2026/12/07 以降」。期間が決まっていなければ "" */
export function editionLabel(edition) {
  const { from = null, until = null } = edition || {};
  if (from && until) return `${slashDate(from)}〜${slashDate(until)}`;
  if (until) return `${slashDate(until)} 以前`;
  if (from) return `${slashDate(from)} 以降`;
  return "";
}

/** 試験の名前。「CCDV-F（2026/12/06 以前）」。index.json の試験・試験情報のどちらも渡せる */
export function examTitle(exam) {
  const label = editionLabel(exam.edition);
  return label ? `${exam.code}（${label}）` : exam.code;
}

/**
 * 試験ガイドの版についての注意。注意がなければ null。
 *   short：ホームの試験カードに出す1行、long：試験のトップに出す文
 */
export function editionNotice(edition, today = todayIso()) {
  const { from = null, until = null } = edition || {};
  if (until && today > until) {
    return {
      state: "outdated",
      short: "旧版：いまの試験とは範囲が異なります",
      long: `この問題集は ${slashDate(until)} 以前の試験ガイドに基づく旧版です。いまの試験とは、出題範囲・分野の配分・問題数が異なります。`,
    };
  }
  if (from && today < from) {
    return {
      state: "upcoming",
      short: `${slashDate(from)} 以降の試験向けです`,
      long: `この問題集は ${slashDate(from)} 以降に受験する試験向けです。それより前に受験する場合は、出題範囲・分野の配分・問題数が異なります。`,
    };
  }
  if (until) {
    const next = slashDate(nextDay(until));
    return {
      state: "changing",
      short: `${next} から試験の範囲が変わります`,
      long: `この問題集は ${slashDate(until)} 以前の試験ガイドに基づいています。${next} 以降に受験する場合は、出題範囲・分野の配分・問題数が変わるため、公式の試験ガイドを確認してください。`,
    };
  }
  return null;
}

/** 「180問 (回答済: 59問)」 */
export function countText(total, seen) {
  return `${total}問 (回答済: ${seen}問)`;
}

/**
 * 押すと別の画面へ移る箱。href を渡すとリンク、onClick を渡すとボタンになる。
 * body には中身（文字列・要素・配列）を渡す。
 */
export function card({ href = null, onClick = null, className = "", label = null }, ...body) {
  const props = { class: `card ${className}`.trim(), "aria-label": label };
  const chev = el("span", { class: "card__chev", "aria-hidden": "true" }, "›");
  const inner = el("div", { class: "card__body" }, ...body);
  return href ? el("a", { ...props, href }, inner, chev) : el("button", { ...props, type: "button", onclick: onClick }, inner, chev);
}

/** チェックボックスの四角（オンなら黒の ✔） */
export function tick(on) {
  return el("span", { class: "tick", "aria-hidden": "true" }, on ? "✔" : "");
}

/**
 * 問題（問題文・選択肢・解説・補足）。枠では囲まず、選択肢だけを白い箱にする。
 * opts:
 *   lang        表示したい言語（"ja" / "en"）
 *   order       選択肢の並び順（id の配列）
 *   selected    選んでいる選択肢の id の配列
 *   reveal      正解と解説を表示するか
 *   onToggle    選択肢を押したときに呼ぶ（id を渡す）。null なら押せない
 */
export function questionCard(exam, q, { lang, order, selected = [], reveal = false, onToggle = null }) {
  const t = textOf(q, lang);
  const optById = new Map(t.options.map((o) => [o.id, o]));
  const ids = order && order.length ? order : t.options.map((o) => o.id);
  const multi = q.type === "multi";
  const chosen = new Set(selected);
  const answer = new Set(q.answer);

  const list = el("div", { class: "options", role: multi ? "group" : "radiogroup", "aria-label": "選択肢" });
  ids.forEach((id, i) => {
    const o = optById.get(id);
    if (!o) return;
    const isChosen = chosen.has(id);
    const isAnswer = answer.has(id);
    let cls = "option";
    if (reveal) {
      cls += " is-rev";
      if (isAnswer) cls += " is-correct";
      else if (isChosen) cls += " is-wrong";
    } else if (isChosen) {
      cls += " is-chosen";
    }
    const mark = reveal ? (isAnswer ? "✓" : isChosen ? "✗" : "") : "";
    const btn = el(
      "button",
      {
        type: "button",
        class: cls,
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

  // このアプリの作成者による補足（元の問題集の文章とは区別して表示する）。表示中の言語に合わせる
  let supplement = null;
  if (reveal && q.supplement) {
    const supLang = t.lang === "en" && q.supplement.en ? "en" : "ja";
    const body = q.supplement[supLang];
    if (body) {
      supplement = el(
        "aside",
        { class: "supplement", lang: supLang },
        el("h3", { text: supLang === "en" ? "Supplement (added by the author of this app)" : "補足（このアプリの作成者による追記）" }),
        el("p", {}, richText(resolveOptionRefs(body, ids))),
      );
    }
  }

  return el(
    "article",
    { class: "qcard", lang: t.lang },
    t.fallback ? el("p", { class: "qnote", lang: "ja", text: "未訳のため英語で表示しています" }) : null,
    el("p", { class: "qtext" }, richText(t.question)),
    multi ? el("p", { class: "qneed", lang: "ja", text: `選択肢から${q.select}つ選ぶ` }) : null,
    list,
    explanation,
    supplement,
  );
}

/**
 * 補足の中の {a}・{b} などを、画面に出ている選択肢の記号（A, B, …）に置き換える。
 * 選択肢は並び順を入れ替えて表示するので、id ではなく表示した位置で記号が決まる。
 */
export function resolveOptionRefs(text, displayedIds) {
  return String(text).replace(/\{([a-z])\}/g, (whole, id) => {
    const i = displayedIds.indexOf(id);
    return i >= 0 ? String.fromCharCode(65 + i) : whole;
  });
}

export function emptyState(title, body, action = null) {
  return el("div", { class: "empty" }, el("p", { class: "empty__title", text: title }), body ? el("p", { text: body }) : null, action);
}
