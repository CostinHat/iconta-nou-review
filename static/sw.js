// Service worker v2 (bon_flux_e4_v1): JS/CSS/imagini merg DIRECT la server
// (prospetimea o decide serverul prin antete). SW pastreaza doar fallback
// offline pentru navigare. Bump-ul de versiune curata cache-ul v1 la activare.
const CACHE = "iconta-v2";
self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(["/"])));
  self.skipWaiting();
});
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) =>
    Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  if (e.request.mode === "navigate") {
    e.respondWith(fetch(e.request).catch(() => caches.match("/")));
  }
  // restul cererilor: netratate de SW -> browser + server, fara cache paralel
});
