// Service Worker：オフラインでも使えるようにする。
// 方針：ネットワークを優先し、取れたものはキャッシュに保存する。オフラインのときはキャッシュから返す。
// （問題データやアプリを更新したとき、オンラインなら必ず新しいものが表示される）

const CACHE = "ccq-v1";
const SHELL = [
  "./",
  "index.html",
  "manifest.webmanifest",
  "styles/app.css",
  "src/main.js",
  "src/util.js",
  "src/storage.js",
  "src/data.js",
  "src/quiz.js",
  "src/components.js",
  "src/views/home.js",
  "src/views/exam.js",
  "src/views/quiz.js",
  "src/views/result.js",
  "src/views/settings.js",
  "icons/icon.svg",
  "icons/icon-192.png",
  "icons/apple-touch-icon.png",
  "data/index.json",
  "data/NOTICE.md",
];
const NETWORK_TIMEOUT_MS = 4000;

self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE);
      // 1つ失敗しても他は保存する
      await Promise.all(SHELL.map((url) => cache.add(url).catch(() => undefined)));
      // 試験データ本体も先に保存しておく（初回からオフラインで解けるように）
      try {
        const res = await fetch("data/index.json", { cache: "no-cache" });
        const index = await res.json();
        await Promise.all(index.exams.map((e) => cache.add(`data/${e.file}`).catch(() => undefined)));
      } catch {
        /* オフラインなどで取れなければ、次に開いたときに保存される */
      }
      await self.skipWaiting();
    })(),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
      await self.clients.claim();
    })(),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // 参考資料など外部のリンクは触らない
  event.respondWith(networkFirst(req));
});

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const res = await withTimeout(fetch(req, { cache: "no-cache" }), NETWORK_TIMEOUT_MS);
    if (res.ok) cache.put(req, res.clone());
    return res;
  } catch {
    const hit = await cache.match(req, { ignoreSearch: true });
    if (hit) return hit;
    if (req.mode === "navigate") {
      const shell = await cache.match("index.html");
      if (shell) return shell;
    }
    return new Response("オフラインのため読み込めません", { status: 503, headers: { "Content-Type": "text/plain; charset=utf-8" } });
  }
}

function withTimeout(promise, ms) {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error("timeout")), ms);
    promise.then(
      (v) => {
        clearTimeout(t);
        resolve(v);
      },
      (e) => {
        clearTimeout(t);
        reject(e);
      },
    );
  });
}
