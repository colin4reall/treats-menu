/* Treats Cafe menu - offline cache.
   Network-first for the page (so updates land), stale-while-revalidate for assets. */
const CACHE = "treats-menu-v1";
const PRECACHE = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./assets/icon-192.png",
  "./assets/icon-512.png",
  "./assets/icon-180.png",
  "./assets/crepe-brownie.jpg",
  "./assets/crepe-lotus.jpg",
  "./assets/crepe-nutella.jpg",
  "./assets/crepe-pistachio.jpg",
  "./assets/drinks-strip.jpg",
  "./assets/logo.jpg",
  "./assets/mocktails-row.jpg",
  "./assets/pancake-biscoff.jpg",
  "./assets/pancake-oreo.jpg",
  "./assets/pancake-pistachio.jpg",
  "./assets/pancake-strawberry.jpg",
  "./assets/shake-mango.jpg",
  "./assets/shake-oreo.jpg",
  "./assets/shake-strawberry.jpg",
  "./assets/shake-vanilla.jpg",
  "./assets/slushies-row.jpg",
  "./assets/waffle-lotus.jpg",
  "./assets/waffle-oreo.jpg",
  "./assets/posters/IMG_3649.jpg",
  "./assets/posters/IMG_3650.jpg",
  "./assets/posters/IMG_3651.jpg",
  "./assets/posters/IMG_3652.jpg",
  "./assets/posters/IMG_3653.jpg",
  "./assets/posters/IMG_3654.jpg",
  "./assets/posters/IMG_3655.jpg",
  "./assets/posters/IMG_3656.jpg",
  "./assets/posters/IMG_3657.jpg",
  "./assets/posters/IMG_3658.jpg"
];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(PRECACHE.map((u) => new Request(u, {cache: "reload"}))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  // navigations: try the network, fall back to the cached page
  if (req.mode === "navigate") {
    e.respondWith(
      fetch(req).catch(() => caches.match("./index.html", {ignoreSearch: true}))
    );
    return;
  }

  // assets: serve from cache instantly, refresh in the background
  e.respondWith(
    caches.match(req).then((hit) => {
      const net = fetch(req).then((res) => {
        if (res && res.status === 200) {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      }).catch(() => hit);
      return hit || net;
    })
  );
});
