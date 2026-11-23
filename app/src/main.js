// アプリの入口：画面の切り替え（#/… のハッシュで管理）と Service Worker の登録

import { el } from "./util.js";
import { homeView } from "./views/home.js";
import { examView } from "./views/exam.js";
import { quickView } from "./views/quick.js";
import { quizView } from "./views/quiz.js";
import { resultView } from "./views/result.js";
import { settingsView } from "./views/settings.js";

const app = document.getElementById("app");
const titleEl = document.getElementById("title");
const backEl = document.getElementById("back");
const settingsEl = document.getElementById("settings");
const actionEl = document.getElementById("topAction");

const routes = [
  [/^#?\/?$/, () => homeView],
  [/^#\/exam\/([a-z0-9-]+)$/, () => examView],
  [/^#\/quick\/([a-z0-9-]+)$/, () => quickView],
  [/^#\/quiz$/, () => quizView],
  [/^#\/result$/, () => resultView],
  [/^#\/settings$/, () => settingsView],
];

let cleanups = [];
let renderToken = 0;

function navigate(hash) {
  if (location.hash === hash) route();
  else location.hash = hash;
}

async function route() {
  const token = ++renderToken;
  cleanups.forEach((fn) => fn());
  cleanups = [];

  const hash = location.hash || "#/";
  let view = null;
  let params = [];
  for (const [re, getView] of routes) {
    const m = hash.match(re);
    if (m) {
      view = getView();
      params = m.slice(1);
      break;
    }
  }

  const ctx = {
    render(node) {
      if (token !== renderToken) return; // 古い画面の描画は捨てる
      app.replaceChildren(node);
    },
    /**
     * 上部バーを設定する。
     *   title   見出し（文字列）。titleNode を渡すと、見出しの中身をその要素にする（模試の残り時間など）
     *   back    戻る先のハッシュ。null なら戻るボタンを出さない
     *   onBack  戻るボタンを押したときに先に呼ぶ。false を返すと戻らない（模試の確認など）
     *   action  右端に出すボタン { label, onClick }。null なら設定（⚙）を出す
     */
    setTop({ title, titleNode = null, back, onBack = null, action = null }) {
      if (token !== renderToken) return;
      titleEl.replaceChildren(titleNode || title);
      document.title = title === "Claude認定 問題集" ? title : `${title}｜Claude認定 問題集`;
      backEl.hidden = !back;
      backEl.onclick = back
        ? () => {
            if (onBack && onBack() === false) return;
            navigate(back);
          }
        : null;
      settingsEl.hidden = Boolean(action);
      actionEl.hidden = !action;
      actionEl.textContent = action ? action.label : "";
      actionEl.onclick = action ? action.onClick : null;
    },
    navigate,
    onCleanup(fn) {
      cleanups.push(fn);
    },
  };

  if (!view) {
    ctx.setTop({ title: "見つかりません", back: "#/" });
    ctx.render(el("p", { class: "empty" }, "ページが見つかりません。", el("a", { href: "#/" }, "ホームへ")));
    return;
  }

  try {
    await view(ctx, ...params);
    if (token === renderToken) {
      window.scrollTo({ top: 0 });
      app.focus({ preventScroll: true });
    }
  } catch (err) {
    console.error(err);
    ctx.setTop({ title: "エラー", back: "#/" });
    ctx.render(
      el(
        "div",
        { class: "empty" },
        el("p", { class: "empty__title", text: "読み込みに失敗しました" }),
        el("p", { text: String(err.message || err) }),
        el("button", { type: "button", class: "btn", onclick: () => location.reload() }, "再読み込み"),
      ),
    );
  }
}

window.addEventListener("hashchange", route);
route();

if ("serviceWorker" in navigator && (location.protocol === "https:" || location.hostname === "localhost")) {
  navigator.serviceWorker.register("sw.js").catch((err) => console.warn("Service Worker を登録できませんでした", err));
}
