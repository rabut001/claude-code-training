// 端末への保存（localStorage）。読めない・書けない環境でもアプリが止まらないようにする。

const PREFIX = "ccq:v1:";
const memory = new Map(); // localStorage が使えないときの代わり（ページを閉じると消える）

export function load(key, fallback) {
  try {
    const raw = localStorage.getItem(PREFIX + key);
    if (raw !== null) return JSON.parse(raw);
  } catch {
    if (memory.has(key)) return structuredClone(memory.get(key));
  }
  return structuredClone(fallback);
}

export function save(key, value) {
  try {
    localStorage.setItem(PREFIX + key, JSON.stringify(value));
  } catch {
    memory.set(key, structuredClone(value));
  }
}

export function remove(key) {
  try {
    localStorage.removeItem(PREFIX + key);
  } catch {
    /* 何もしない */
  }
  memory.delete(key);
}

/** localStorage が永続的に使えるか（設定画面の表示用） */
export function isPersistent() {
  try {
    const k = PREFIX + "__probe";
    localStorage.setItem(k, "1");
    localStorage.removeItem(k);
    return true;
  } catch {
    return false;
  }
}

// ---- 設定 ----
// quickPool：クイック10問で出題の対象にする問題（未回答・誤答・チェック）。前回選んだものを覚えておく
const DEFAULT_SETTINGS = { lang: "ja", shuffleOptions: true, quickPool: { unanswered: true, wrong: true, checked: true } };

export function getSettings() {
  const s = { ...DEFAULT_SETTINGS, ...load("settings", {}) };
  s.quickPool = { ...DEFAULT_SETTINGS.quickPool, ...(s.quickPool || {}) };
  return s;
}

export function setSettings(patch) {
  const next = { ...getSettings(), ...patch };
  save("settings", next);
  return next;
}

// ---- 学習記録（試験ごと） ----
// { [questionId]: { n: 回答回数, ok: 正解回数, last: 最後に正解したか, at: 最後に解いた時刻 } }
export function getProgress(examId) {
  return load(`progress:${examId}`, {});
}

export function recordAnswer(examId, questionId, correct, at = Date.now()) {
  const progress = getProgress(examId);
  const p = progress[questionId] || { n: 0, ok: 0, last: null, at: 0 };
  p.n += 1;
  if (correct) p.ok += 1;
  p.last = correct;
  p.at = at;
  progress[questionId] = p;
  save(`progress:${examId}`, progress);
  return p;
}

/** 1問分の学習記録を、指定した状態に戻す（採点の取り消しで使う）。entry が null なら記録を消す */
export function restoreProgress(examId, questionId, entry) {
  const progress = getProgress(examId);
  if (entry) progress[questionId] = entry;
  else delete progress[questionId];
  save(`progress:${examId}`, progress);
}

export function resetProgress(examId) {
  remove(`progress:${examId}`);
  remove(`checks:${examId}`);
}

// ---- チェック（後から見返したい問題。試験ごと） ----
// { [questionId]: true }
export function getChecks(examId) {
  return load(`checks:${examId}`, {});
}

export function setCheck(examId, questionId, on) {
  setChecks(examId, { [questionId]: on });
}

/** 複数の問題のチェックをまとめて付け外しする。states: { [questionId]: true / false } */
export function setChecks(examId, states) {
  const checks = getChecks(examId);
  for (const [id, on] of Object.entries(states)) {
    if (on) checks[id] = true;
    else delete checks[id];
  }
  save(`checks:${examId}`, checks);
}

// ---- 解いている途中のセッション（1つだけ保持） ----
export const SESSION_VERSION = 2;

/** 保存してあるセッション。形式の古いもの（以前のアプリで始めたもの）は捨てる */
export function getSession() {
  const s = load("session", null);
  if (s && s.v !== SESSION_VERSION) {
    remove("session");
    return null;
  }
  return s;
}

export function setSession(session) {
  if (session) save("session", session);
  else remove("session");
}

// ---- 直近の結果（結果画面で使う） ----
export function getLastResult() {
  return load("lastResult", null);
}

export function setLastResult(result) {
  save("lastResult", result);
}
