// 設定・アプリについて・出典とライセンス

import { el } from "../util.js";
import { loadIndex, loadNotice } from "../data.js";
import { examTitle } from "../components.js";
import { getSettings, setSettings, resetProgress, isPersistent } from "../storage.js";

export async function settingsView(ctx) {
  ctx.setTop({ title: "設定", back: "#/" });
  const index = await loadIndex();

  const draw = async () => {
    const s = getSettings();

    const langGroup = el(
      "div",
      { class: "segmented", role: "radiogroup", "aria-label": "表示する言語" },
      [
        ["ja", "日本語（未訳は英語）"],
        ["en", "英語（本番と同じ）"],
      ].map(([value, label]) =>
        el(
          "button",
          {
            type: "button",
            role: "radio",
            "aria-checked": s.lang === value ? "true" : "false",
            class: s.lang === value ? "is-on" : "",
            onclick: () => {
              setSettings({ lang: value });
              draw();
            },
          },
          label,
        ),
      ),
    );

    const shuffleToggle = el(
      "label",
      { class: "switch" },
      el("input", {
        type: "checkbox",
        checked: s.shuffleOptions,
        onchange: (e) => setSettings({ shuffleOptions: e.target.checked }),
      }),
      el("span", { text: "選択肢の順番を毎回入れ替える" }),
    );

    const resets = index.exams.map((e) =>
      el(
        "button",
        {
          type: "button",
          class: "btn btn--danger",
          onclick: () => {
            if (confirm(`${examTitle(e)} の学習記録とチェックをすべて消しますか？（元に戻せません）`)) {
              resetProgress(e.id);
              alert(`${examTitle(e)} の学習記録とチェックを消しました。`);
            }
          },
        },
        `${examTitle(e)} の学習記録を消す`,
      ),
    );

    let notice;
    try {
      notice = renderMarkdown(await loadNotice());
    } catch {
      notice = el("p", { text: "出典の情報を読み込めませんでした。" });
    }

    ctx.render(
      el(
        "div",
        { class: "stack" },
        el("section", { class: "settings-section" }, el("h2", { class: "section-title", text: "表示する言語" }), langGroup, el("p", { class: "hint", text: "出題中も、問題ごとに「English / 日本語」ボタンで切り替えられます。" })),
        el("section", { class: "settings-section" }, el("h2", { class: "section-title", text: "出題" }), shuffleToggle),
        el(
          "section",
          { class: "settings-section" },
          el("h2", { class: "section-title", text: "学習記録" }),
          el("p", { class: "hint", text: isPersistent() ? "学習記録はこの端末のブラウザに保存されます（ほかの端末とは共有されません）。" : "この環境では学習記録を保存できません。ページを閉じると消えます。" }),
          resets,
        ),
        el(
          "section",
          { class: "settings-section" },
          el("h2", { class: "section-title", text: "スマホのホーム画面に追加する" }),
          el("p", { class: "hint", text: "iPhone：Safari の共有ボタン →「ホーム画面に追加」。Android：Chrome のメニュー →「ホーム画面に追加」または「アプリをインストール」。一度開いたあとはオフラインでも使えます。" }),
        ),
        el("section", { class: "settings-section notice" }, el("h2", { class: "section-title", text: "出典とライセンス" }), notice),
      ),
    );
  };

  await draw();
}

/** NOTICE.md 用のごく小さな Markdown 表示（見出し・コードブロック・箇条書き・段落・URL だけ） */
function renderMarkdown(md) {
  const root = el("div", { class: "md" });
  const lines = md.replace(/\r\n/g, "\n").split("\n");
  let para = [];
  let list = null;
  const flushPara = () => {
    if (para.length) root.append(el("p", {}, linkify(para.join(" "))));
    para = [];
  };
  const flushList = () => {
    if (list) root.append(list);
    list = null;
  };
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (line.startsWith("```")) {
      flushPara();
      flushList();
      const code = [];
      for (i++; i < lines.length && !lines[i].startsWith("```"); i++) code.push(lines[i]);
      root.append(el("pre", {}, el("code", { text: code.join("\n") })));
      continue;
    }
    const h = line.match(/^(#{1,3})\s+(.*)$/);
    if (h) {
      flushPara();
      flushList();
      root.append(el(`h${Math.min(4, h[1].length + 2)}`, { text: h[2] }));
      continue;
    }
    if (/^---+\s*$/.test(line)) {
      flushPara();
      flushList();
      root.append(el("hr"));
      continue;
    }
    const li = line.match(/^\s*[-*]\s+(.*)$/);
    if (li) {
      flushPara();
      if (!list) list = el("ul");
      list.append(el("li", {}, linkify(li[1])));
      continue;
    }
    if (!line.trim()) {
      flushPara();
      flushList();
      continue;
    }
    para.push(line.trim());
  }
  flushPara();
  flushList();
  return root;
}

function linkify(text) {
  const frag = document.createDocumentFragment();
  const parts = text.replace(/\*\*/g, "").split(/(https?:\/\/[^\s）)]+)/g);
  for (const p of parts) {
    if (/^https?:\/\//.test(p)) frag.append(el("a", { href: p, target: "_blank", rel: "noopener" }, p));
    else if (p) frag.append(document.createTextNode(p));
  }
  return frag;
}
