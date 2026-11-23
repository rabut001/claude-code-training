// 画面づくりの小さな道具

/**
 * 要素を作る。props の on* はイベント、class / text / html 以外は属性として設定する。
 * children には文字列・Node・配列・null を渡せる。
 */
export function el(tag, props = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(props || {})) {
    if (value === undefined || value === null || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (key === "dataset") Object.assign(node.dataset, value);
    else if (key.startsWith("on") && typeof value === "function") node.addEventListener(key.slice(2), value);
    else if (value === true) node.setAttribute(key, "");
    else node.setAttribute(key, String(value));
  }
  append(node, children);
  return node;
}

function append(node, children) {
  for (const child of children.flat(Infinity)) {
    if (child === undefined || child === null || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
}

/** 問題文などの文字列を表示用にする。バッククォートで囲んだ部分だけを <code> にする（Markdown は解釈しない）。 */
export function richText(text) {
  const frag = document.createDocumentFragment();
  const parts = String(text ?? "").split(/(`[^`\n]+`)/g);
  for (const part of parts) {
    if (!part) continue;
    if (part.length > 2 && part.startsWith("`") && part.endsWith("`")) {
      frag.append(el("code", { text: part.slice(1, -1) }));
    } else {
      frag.append(document.createTextNode(part));
    }
  }
  return frag;
}

/** Fisher–Yates でシャッフルした新しい配列を返す。 */
export function shuffle(items, random = Math.random) {
  const a = items.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export function formatClock(ms) {
  const total = Math.max(0, Math.ceil(ms / 1000));
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const mm = String(m).padStart(2, "0");
  const ss = String(s).padStart(2, "0");
  return h > 0 ? `${h}:${mm}:${ss}` : `${mm}:${ss}`;
}

export function percent(n, d) {
  return d > 0 ? Math.round((n / d) * 100) : 0;
}

export function formatDate(ts) {
  const d = new Date(ts);
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}
