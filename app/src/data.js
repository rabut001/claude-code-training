// 問題データの読み込み（build.py が生成した app/data/ を読む）

let indexCache = null;
const examCache = new Map();

async function fetchJson(path) {
  const res = await fetch(path, { cache: "no-cache" });
  if (!res.ok) throw new Error(`${path} を読み込めませんでした（${res.status}）`);
  return res.json();
}

/** 試験の一覧。表示順は CCDV-F → CCAR-P に固定する。 */
export async function loadIndex() {
  if (!indexCache) {
    const index = await fetchJson("data/index.json");
    const order = ["ccdv-f", "ccar-p"];
    index.exams.sort((a, b) => order.indexOf(a.id) - order.indexOf(b.id));
    indexCache = index;
  }
  return indexCache;
}

/** 試験1つ分（試験情報と全問題）。問題は id で引けるようにしておく。 */
export async function loadExam(examId) {
  if (!examCache.has(examId)) {
    const index = await loadIndex();
    const entry = index.exams.find((e) => e.id === examId);
    if (!entry) throw new Error(`試験 ${examId} が見つかりません`);
    const bundle = await fetchJson(`data/${entry.file}`);
    const byId = new Map(bundle.questions.map((q) => [q.id, q]));
    const domains = new Map(bundle.exam.domains.map((d) => [d.id, d]));
    examCache.set(examId, { ...bundle, byId, domains });
  }
  return examCache.get(examId);
}

export async function loadNotice() {
  const index = await loadIndex();
  const res = await fetch(`data/${index.notice}`, { cache: "no-cache" });
  if (!res.ok) throw new Error("NOTICE.md を読み込めませんでした");
  return res.text();
}

export function isTranslated(question) {
  return question.ja && question.ja.status !== "todo";
}

/**
 * 表示する言語の文面を返す。和訳がない問題は英語にする。
 * 返り値の lang は実際に表示する言語、fallback は「日本語を希望したが未訳だった」か。
 */
export function textOf(question, wantLang) {
  const useJa = wantLang === "ja" && isTranslated(question);
  const t = useJa ? question.ja : question.en;
  return {
    lang: useJa ? "ja" : "en",
    fallback: wantLang === "ja" && !useJa,
    question: t.question,
    options: t.options,
    explanation: t.explanation,
  };
}
