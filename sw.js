const CACHE = 'astraeon-static-v13';
const FILES = ['./', './index.html', './style.css', './style.css?v=13', './game.js', './game.js?v=13', './manifest.webmanifest', './icon.svg', './assets/astral-outpost.webp', './assets/hero-atlas.webp', './assets/astral-wolf.webp', './assets/grassland-ground.webp'];

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(FILES)));
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('astraeon-static-') && key !== CACHE).map(key => caches.delete(key)))));
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const request = event.request;
  if (request.method !== 'GET' || new URL(request.url).origin !== self.location.origin) return;
  event.respondWith(caches.match(request).then(cached => cached || fetch(request).then(response => {
    if (response.ok) {
      const copy = response.clone();
      caches.open(CACHE).then(cache => cache.put(request, copy));
    }
    return response;
  }).catch(() => caches.match('./index.html'))));
});
