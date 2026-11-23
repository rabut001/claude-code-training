// 出題と採点の仕組み（画面に依存しない部分）

import { shuffle } from "./util.js";

// feedback：問題ごとに「正解を表示」できるか（模試はできない）
export const MODES = {
  quick: { label: "クイック10問", feedback: true },
  drill: { label: "分野別ドリル", feedback: true },
  mock: { label: "本番形式の模試", feedback: false },
};

/**
 * まだ解いていない問題 → 前回まちがえた問題 → 前回正解した問題 の順に優先して並べる。
 * 同じ優先度の中はランダム。
 */
export function prioritize(questions, progress, random = Math.random) {
  const rank = (q) => {
    const p = progress[q.id];
    if (!p) return 0;
    return p.last ? 2 : 1;
  };
  return shuffle(questions, random).sort((a, b) => rank(a) - rank(b));
}

/**
 * クイック10問の対象になる問題。
 * pool: { unanswered: 未回答, wrong: 前回まちがえた, checked: チェックした } のうち true のものを合わせる。
 */
export function quickPool(questions, progress, checks, pool) {
  return questions.filter((q) => {
    const p = progress[q.id];
    return (pool.unanswered && !p) || (pool.wrong && p && p.last === false) || (pool.checked && Boolean(checks[q.id]));
  });
}

/** 模試の問題を、分野ごとの出題数（mock_items）どおりに選ぶ。問題が足りない分野はある分だけ。 */
export function pickMock(exam, questions, random = Math.random) {
  const picked = [];
  for (const d of exam.domains) {
    const pool = shuffle(questions.filter((q) => q.domain === d.id), random);
    picked.push(...pool.slice(0, d.mock_items));
  }
  return shuffle(picked, random);
}

/**
 * 出題する問題を選ぶ。
 * options: { mode, domain, count, checks, pool }
 *   quick：pool に当てはまる問題からランダムに count 問
 *   drill：その分野の全問（未回答 → 前回まちがい → 前回正解 の順）
 *   mock ：分野の配分どおり
 */
export function pickQuestions(exam, questions, progress, { mode, domain = null, count = 10, checks = {}, pool = {} }, random = Math.random) {
  switch (mode) {
    case "quick":
      return shuffle(quickPool(questions, progress, checks, pool), random).slice(0, count);
    case "drill":
      return prioritize(questions.filter((q) => q.domain === domain), progress, random);
    case "mock":
      return pickMock(exam, questions, random);
    default:
      throw new Error(`不明なモード: ${mode}`);
  }
}

/** 新しいセッション（解いている途中の状態）を作る。選択肢の並び順もここで決めて保存する。 */
export function createSession(exam, picked, { mode, domain = null, shuffleOptions = true }, now = Date.now(), random = Math.random) {
  const order = {};
  for (const q of picked) {
    const ids = q.en.options.map((o) => o.id);
    order[q.id] = shuffleOptions ? shuffle(ids, random) : ids;
  }
  return {
    v: 2,
    exam: exam.id,
    mode,
    domain,
    ids: picked.map((q) => q.id),
    order,
    index: 0,
    sel: {}, // 選んでいる選択肢 { [id]: [...] }。採点していなくても残す
    graded: {}, // 採点した問題 { [id]: { correct, prev } }。prev は採点前の学習記録（取り消し用）
    checks: {}, // 模試の間だけのチェック { [id]: true }。練習ではチェックを直接保存する
    startedAt: now,
    deadline: mode === "mock" ? now + exam.exam.minutes * 60 * 1000 : null,
  };
}

/** 選んだ選択肢が正解か。複数選択は、正解の組み合わせと完全に一致したときだけ正解。 */
export function isCorrect(question, selected) {
  const a = [...question.answer].sort();
  const s = [...new Set(selected)].sort();
  return a.length === s.length && a.every((x, i) => x === s[i]);
}

/** 問題番号のボタンに出す状態："correct" / "wrong"（採点済み）、"draft"（選んだが未採点）、"none" */
export function questionState(session, id) {
  const g = session.graded[id];
  if (g) return g.correct ? "correct" : "wrong";
  return session.sel[id] && session.sel[id].length ? "draft" : "none";
}

/**
 * セッションの結果をまとめる。採点していない問題は未回答（不正解として数える）。
 * checks：結果に出すチェックの状態 { [id]: true }
 */
export function summarize(session, exam, byId, checks = {}) {
  const domains = new Map(exam.domains.map((d) => [d.id, { id: d.id, name: d.name, correct: 0, total: 0 }]));
  let correct = 0;
  const items = [];
  for (const id of session.ids) {
    const q = byId.get(id);
    if (!q) continue;
    const g = session.graded[id];
    const ok = Boolean(g && g.correct);
    if (ok) correct += 1;
    const d = domains.get(q.domain);
    if (d) {
      d.total += 1;
      if (ok) d.correct += 1;
    }
    items.push({ id, domain: q.domain, answered: Boolean(g), correct: ok, selected: g ? session.sel[id] || [] : [], checked: Boolean(checks[id]) });
  }
  const total = items.length;
  const rate = total ? correct / total : 0;
  return {
    exam: session.exam,
    mode: session.mode,
    domain: session.domain,
    correct,
    total,
    rate,
    passEstimate: exam.exam.pass_raw_estimate,
    passed: session.mode === "mock" ? rate >= exam.exam.pass_raw_estimate : null,
    byDomain: [...domains.values()].filter((d) => d.total > 0),
    items,
    startedAt: session.startedAt,
    finishedAt: Date.now(),
  };
}

/** 試験全体と分野ごとの学習状況（問題数・回答済み）と、クイック10問の対象の数 */
export function overallStats(exam, questions, progress, checks = {}) {
  const rows = exam.domains.map((d) => ({ id: d.id, name: d.name, total: 0, seen: 0 }));
  const byId = new Map(rows.map((r) => [r.id, r]));
  let wrong = 0;
  let checked = 0;
  for (const q of questions) {
    const r = byId.get(q.domain);
    if (!r) continue;
    r.total += 1;
    const p = progress[q.id];
    if (p) {
      r.seen += 1;
      if (p.last === false) wrong += 1;
    }
    if (checks[q.id]) checked += 1;
  }
  const total = rows.reduce((n, r) => n + r.total, 0);
  const seen = rows.reduce((n, r) => n + r.seen, 0);
  return { rows, total, seen, unanswered: total - seen, wrong, checked };
}
