// 出題画面
//
// 上部：問題番号の帯（横にスクロール）。練習では 正解○・不正解×・選択中• とチェック✔ を出す。模試では何も出さない
// 下部：前へ・正解を表示（練習だけ）・次へ。未回答のまま次の問題へ進める。最後の問題では「次へ」が「結果へ」になる
// 右上：一括採点

import { el, formatClock } from "../util.js";
import { loadExam } from "../data.js";
import {
  getSession,
  setSession,
  getSettings,
  getProgress,
  recordAnswer,
  restoreProgress,
  getChecks,
  setCheck,
  setChecks,
  setLastResult,
} from "../storage.js";
import { isCorrect, summarize, questionState, MODES } from "../quiz.js";
import { questionCard, emptyState, sessionLabel, tick } from "../components.js";

const MARKS = { correct: "○", wrong: "×", draft: "•", none: "" };
const STATE_LABELS = { correct: "正解", wrong: "不正解", draft: "選択中", none: "未回答" };

export async function quizView(ctx) {
  const session = getSession();
  if (!session) {
    ctx.setTop({ title: "出題", back: "#/" });
    ctx.render(emptyState("解いている問題はありません", "ホームから出題モードを選んでください。", el("a", { class: "btn", href: "#/" }, "ホームへ")));
    return;
  }

  const data = await loadExam(session.exam);
  const exam = data.exam;
  const isMock = session.mode === "mock";
  const feedback = (MODES[session.mode] || MODES.quick).feedback;
  session.ids = session.ids.filter((id) => data.byId.has(id)); // データの更新で消えた問題を除く
  if (!session.lang) session.lang = getSettings().lang;
  if (session.index >= session.ids.length) session.index = Math.max(0, session.ids.length - 1);

  // 練習のチェックは端末に直接保存する。模試のチェックは採点するまでセッションの中だけに持つ
  let savedChecks = getChecks(exam.id);
  const isChecked = (id) => (isMock ? Boolean(session.checks[id]) : Boolean(savedChecks[id]));

  const save = () => setSession(session);
  const selOf = (id) => session.sel[id] || [];

  /** 練習で1問を採点する。取り消せるように、採点前の学習記録を残しておく */
  const grade = (id) => {
    const q = data.byId.get(id);
    const prev = getProgress(exam.id)[id] || null;
    const correct = isCorrect(q, selOf(id));
    recordAnswer(exam.id, id, correct);
    session.graded[id] = { correct, prev };
  };

  /** 採点を取り消す。選んだ選択肢はそのままにして、学習記録を採点前に戻す */
  const ungrade = (id) => {
    const g = session.graded[id];
    if (!g) return;
    restoreProgress(exam.id, id, g.prev);
    delete session.graded[id];
  };

  const finish = () => {
    let checksForResult = savedChecks;
    if (isMock) {
      // 模試の結果とチェックの状態で、学習記録を上書きする（未回答の問題の正誤の記録はそのまま）
      const at = Date.now();
      for (const id of session.ids) {
        const sel = selOf(id);
        if (!sel.length) continue;
        const correct = isCorrect(data.byId.get(id), sel);
        recordAnswer(exam.id, id, correct, at);
        session.graded[id] = { correct, prev: null };
      }
      setChecks(exam.id, Object.fromEntries(session.ids.map((id) => [id, Boolean(session.checks[id])])));
      checksForResult = session.checks;
    }
    setLastResult(summarize(session, exam, data.byId, checksForResult));
    setSession(null);
    ctx.navigate("#/result");
  };

  const bulkGrade = () => {
    if (isMock) {
      const un = session.ids.filter((id) => !selOf(id).length).length;
      const msg = `${un ? `未回答が ${un}問あります。` : ""}採点して、この模試の結果とチェックの状態で学習記録を上書きしますか？`;
      if (!confirm(msg)) return;
    } else {
      // 全問を採点し終えていれば、確認せずに結果画面へ進む
      const drafts = session.ids.filter((id) => !session.graded[id] && selOf(id).length);
      const un = session.ids.filter((id) => !session.graded[id] && !selOf(id).length).length;
      if (drafts.length || un) {
        const msg = `${drafts.length ? `選んだまま正解を表示していない ${drafts.length}問を採点します。` : ""}${un ? `未回答の ${un}問は未回答のままです。` : ""}結果画面へ進みますか？`;
        if (!confirm(msg)) return;
      }
      drafts.forEach(grade);
    }
    finish();
  };

  // 問題が見つからないとき（データの更新などで）に、セッションを捨てて戻る
  const quit = () => {
    setSession(null);
    ctx.navigate(`#/exam/${exam.id}`);
  };

  // 戻る操作。練習は確認しない（採点とチェックはその場で保存済みで、セッションも「続きから」で再開できるため）。
  // 模試は戻ると中断になる（回答とチェックは記録せず、残り時間もリセット）ので、確認してからセッションを捨てる。
  // ブラウザの「戻る」やスマホの戻るジェスチャーでも確認を出すため、模試の画面では履歴に「見張り」を1つ積んでおく。
  // 戻る操作をすると、まず見張りの1つ前（同じ #/quiz）に戻るだけなので、画面を離れる前に確認を出せる
  let onBack = null;
  if (isMock) {
    const GUARD = { mockGuard: true };
    const isGuard = (state) => Boolean(state && state.mockGuard);
    const leave = () => {
      setSession(null);
      location.replace(`#/exam/${exam.id}`); // 見張りの分の履歴を増やさないよう、置き換えで移る
    };
    const ask = () => confirm("模試を中断して戻りますか？\nここまでの回答とチェックは記録されず、残り時間もリセットされます。");

    if (!isGuard(history.state)) history.pushState(GUARD, "", location.href);
    const onPop = (e) => {
      if (isGuard(e.state) || location.hash !== "#/quiz" || !getSession()) return;
      if (ask()) leave();
      else history.pushState(GUARD, "", location.href); // 続けるので、見張りを積み直す
    };
    window.addEventListener("popstate", onPop);
    ctx.onCleanup(() => window.removeEventListener("popstate", onPop));

    // 上部の ‹ も、ブラウザの「戻る」と同じ流れにする（見張りがなければ、その場で確認する）
    onBack = () => {
      if (isGuard(history.state)) history.back();
      else if (ask()) leave();
      return false;
    };
  }

  // 上部バー：模試は残り時間も出す
  const label = sessionLabel(data, session);
  let titleNode = null;
  if (session.deadline) {
    const timer = el("span", { class: "timer", "aria-live": "off" });
    titleNode = el("span", {}, "模試", timer);
    const tick_ = () => {
      const left = session.deadline - Date.now();
      timer.textContent = `残り ${formatClock(left)}`;
      timer.classList.toggle("timer--low", left < 5 * 60 * 1000);
      if (left <= 0) {
        clearInterval(handle);
        alert("時間になりました。採点します。");
        finish();
      }
    };
    const handle = setInterval(tick_, 1000);
    ctx.onCleanup(() => clearInterval(handle));
    tick_();
  }
  ctx.setTop({ title: `${exam.code}・${label}`, titleNode, back: `#/exam/${exam.id}`, onBack, action: { label: "一括採点", onClick: bulkGrade } });

  const draw = ({ toTop = false } = {}) => {
    const id = session.ids[session.index];
    const q = data.byId.get(id);
    if (!q) {
      ctx.render(emptyState("問題が見つかりません", "データが更新された可能性があります。", el("button", { class: "btn", type: "button", onclick: quit }, "やめる")));
      return;
    }
    const sel = selOf(id);
    const graded = session.graded[id];
    const reveal = feedback && Boolean(graded);
    const first = session.index === 0;
    const last = session.index === session.ids.length - 1;

    const go = (i) => {
      session.index = Math.min(Math.max(0, i), session.ids.length - 1);
      save();
      draw({ toTop: true });
    };

    const toggle = (optId) => {
      const next = q.type === "multi" ? (sel.includes(optId) ? sel.filter((x) => x !== optId) : [...sel, optId]) : [optId];
      if (next.length) session.sel[id] = next;
      else delete session.sel[id];
      save();
      draw();
    };

    // 問題番号の帯
    const strip = el(
      "nav",
      { class: "strip", "aria-label": "問題番号" },
      session.ids.map((qid, i) => {
        const state = isMock ? "none" : questionState(session, qid);
        const checked = !isMock && isChecked(qid);
        const current = i === session.index;
        const desc = isMock ? "" : `、${STATE_LABELS[state]}${checked ? "、チェック済み" : ""}`;
        return el(
          "button",
          {
            type: "button",
            class: `num${state !== "none" ? ` is-${state}` : ""}${current ? " is-current" : ""}`,
            "aria-label": `問${i + 1}${desc}`,
            "aria-current": current ? "true" : null,
            onclick: () => go(i),
          },
          el("span", { text: String(i + 1) }),
          el("span", { class: "num__mark", "aria-hidden": "true", text: MARKS[state] }),
          checked ? el("span", { class: "num__check", "aria-hidden": "true", text: "✔" }) : null,
        );
      }),
    );

    const checked = isChecked(id);
    const head = el(
      "div",
      { class: "qhead" },
      el("span", { class: "counter", text: `問${session.index + 1} / ${session.ids.length}` }),
      el(
        "div",
        { class: "qhead__tools" },
        el(
          "button",
          {
            type: "button",
            class: "btn btn--sm",
            "aria-label": "表示する言語を切り替える",
            onclick: () => {
              session.lang = session.lang === "ja" ? "en" : "ja";
              save();
              draw();
            },
          },
          session.lang === "ja" ? "English" : "日本語",
        ),
        el(
          "button",
          {
            type: "button",
            class: "btn btn--sm checkbtn",
            role: "checkbox",
            "aria-checked": checked ? "true" : "false",
            onclick: () => {
              if (isMock) {
                if (checked) delete session.checks[id];
                else session.checks[id] = true;
                save();
              } else {
                setCheck(exam.id, id, !checked);
                savedChecks = getChecks(exam.id);
              }
              draw();
            },
          },
          tick(checked),
          "チェック",
        ),
      ),
    );

    const verdict = reveal
      ? el("p", { class: `verdict ${graded.correct ? "verdict--ok" : "verdict--ng"}`, role: "status" }, graded.correct ? "○ 正解" : "× 不正解")
      : null;

    const card = questionCard(data, q, {
      lang: session.lang,
      order: session.order[id],
      selected: sel,
      reveal,
      onToggle: reveal ? null : toggle,
    });

    // 画面の下に固定する操作
    const prev = el("button", { type: "button", class: "btn", disabled: first, onclick: () => go(session.index - 1) }, "前へ");
    // 最後の問題では「次へ」の代わりに「結果へ」を出す（押したときは一括採点と同じ）。
    // 最後の問題を終えたら（練習は採点、模試は選択肢を選んだら）、主ボタンの色にする
    const next = last
      ? el("button", { type: "button", class: `btn${(feedback ? reveal : sel.length > 0) ? " btn--primary" : ""}`, onclick: bulkGrade }, "結果へ")
      : el("button", { type: "button", class: "btn", onclick: () => go(session.index + 1) }, "次へ");
    let middle = null;
    let hint = "";
    if (feedback) {
      if (reveal) {
        hint = "取り消すと、選んだ選択肢はそのままで採点前に戻ります";
        middle = el("button", { type: "button", class: "btn", onclick: () => { ungrade(id); save(); draw(); } }, "採点取消");
      } else {
        const need = q.select - sel.length;
        if (q.type === "multi" && need > 0 && sel.length > 0) hint = `あと${need}つ選んでください`;
        if (need < 0) hint = `${q.select}つまで選べます`;
        middle = el(
          "button",
          {
            type: "button",
            class: `btn${need === 0 ? " btn--primary" : ""}`,
            disabled: need !== 0,
            onclick: () => {
              grade(id);
              save();
              draw({ toTop: true }); // 正解・不正解は問題の上に出る
            },
          },
          "正解を表示",
        );
      }
    }
    const bottombar = el(
      "div",
      { class: "bottombar" },
      el(
        "div",
        { class: "bottombar__inner" },
        feedback ? el("p", { class: "bottombar__hint", "aria-live": "polite", text: hint }) : null,
        el("div", { class: `bottombar__btns${feedback ? "" : " bottombar__btns--two"}` }, prev, middle, next),
      ),
    );

    ctx.render(
      el(
        "div",
        { class: "stack quiz" },
        strip,
        head,
        verdict,
        card,
        bottombar,
      ),
    );

    // いまの問題の番号が帯の中央に来るようにする
    const current = strip.querySelector(".is-current");
    if (current) strip.scrollLeft = current.offsetLeft - strip.offsetLeft - (strip.clientWidth - current.offsetWidth) / 2;
    if (toTop) window.scrollTo({ top: 0 });
  };

  draw();
}
