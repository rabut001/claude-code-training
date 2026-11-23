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
const DEFAULT_SETTINGS = { lang: "ja", shuffleOptions: true };

export function getSettings() {
  return { ...DEFAULT_SETTINGS, ...load("settings", {}) };
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

export function resetProgress(examId) {
  remove(`progress:${examId}`);
}

// ---- 解いている途中のセッション（1つだけ保持） ----
export function getSession() {
  return load("session", null);
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
