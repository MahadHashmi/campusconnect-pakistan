const CACHE_NAME = 'campusconnect-v1';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Let network requests pass through normally
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request)));
});
