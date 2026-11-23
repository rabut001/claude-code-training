// 出題と採点の仕組み（画面に依存しない部分）

import { shuffle } from "./util.js";

export const MODES = {
  quick: { label: "クイック10問", feedback: true },
  drill: { label: "分野別ドリル", feedback: true },
  review: { label: "間違えた問題の復習", feedback: true },
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

/** 前回まちがえた問題（復習モードの対象） */
export function wrongQuestions(questions, progress) {
  return questions.filter((q) => progress[q.id] && progress[q.id].last === false);
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
 * options: { mode, domain, count }
 */
export function pickQuestions(exam, questions, progress, { mode, domain = null, count = 10 }, random = Math.random) {
  switch (mode) {
    case "quick":
      return prioritize(questions, progress, random).slice(0, count);
    case "drill": {
      const pool = questions.filter((q) => q.domain === domain);
      return prioritize(pool, progress, random).slice(0, count || pool.length);
    }
    case "review":
      return shuffle(wrongQuestions(questions, progress), random).slice(0, count || undefined);
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
    v: 1,
    exam: exam.id,
    mode,
    domain,
    ids: picked.map((q) => q.id),
    order,
    index: 0,
    answers: {}, // { [id]: { selected: [...], correct: bool } }
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

/** セッションの結果をまとめる。未回答は不正解として数える。 */
export function summarize(session, exam, byId) {
  const domains = new Map(exam.domains.map((d) => [d.id, { id: d.id, name: d.name, correct: 0, total: 0 }]));
  let correct = 0;
  const items = [];
  for (const id of session.ids) {
    const q = byId.get(id);
    if (!q) continue;
    const a = session.answers[id];
    const ok = Boolean(a && a.correct);
    if (ok) correct += 1;
    const d = domains.get(q.domain);
    if (d) {
      d.total += 1;
      if (ok) d.correct += 1;
    }
    items.push({ id, domain: q.domain, answered: Boolean(a), correct: ok, selected: a ? a.selected : [] });
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

/** 試験全体の学習状況（分野ごとの「解いた数」「前回正解した数」） */
export function overallStats(exam, questions, progress) {
  const rows = exam.domains.map((d) => ({ id: d.id, name: d.name, weight: d.weight, total: 0, seen: 0, mastered: 0, wrong: 0 }));
  const byId = new Map(rows.map((r) => [r.id, r]));
  for (const q of questions) {
    const r = byId.get(q.domain);
    if (!r) continue;
    r.total += 1;
    const p = progress[q.id];
    if (p) {
      r.seen += 1;
      if (p.last) r.mastered += 1;
      else r.wrong += 1;
    }
  }
  const sum = (k) => rows.reduce((n, r) => n + r[k], 0);
  return { rows, total: sum("total"), seen: sum("seen"), mastered: sum("mastered"), wrong: sum("wrong") };
}
