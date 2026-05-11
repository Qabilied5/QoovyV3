// ═══════════════════════════════════════════
//  QOOVY PWA — SERVICE WORKER
//  Version: 1.0.0
// ═══════════════════════════════════════════

const CACHE_NAME = 'qoovy-v1';
const STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

// ── INSTALL: cache static assets
self.addEventListener('install', function(event) {
  console.log('[QoovySW] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(STATIC_ASSETS);
    }).then(function() {
      console.log('[QoovySW] Static assets cached.');
      return self.skipWaiting();
    })
  );
});

// ── ACTIVATE: clean up old caches
self.addEventListener('activate', function(event) {
  console.log('[QoovySW] Activating...');
  event.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(key) { return key !== CACHE_NAME; })
            .map(function(key) { return caches.delete(key); })
      );
    }).then(function() {
      console.log('[QoovySW] Old caches cleared.');
      return self.clients.claim();
    })
  );
});

// ── FETCH: cache-first for shell, network-first for API
self.addEventListener('fetch', function(event) {
  var url = event.request.url;

  // Skip non-GET requests and browser extensions
  if (event.request.method !== 'GET') return;
  if (url.startsWith('chrome-extension://')) return;

  // Skip YouTube, Google APIs (streaming — don't cache)
  if (
    url.includes('youtube.com') ||
    url.includes('ytimg.com') ||
    url.includes('googleapis.com') ||
    url.includes('googlevideo.com') ||
    url.includes('corsproxy.io') ||
    url.includes('allorigins.win')
  ) {
    // Pass through directly — no cache
    return;
  }

  // App shell / static assets → Cache First with network fallback
  event.respondWith(
    caches.match(event.request).then(function(cachedResponse) {
      if (cachedResponse) {
        // Return cached, but also refresh in background
        var fetchPromise = fetch(event.request).then(function(networkResponse) {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, networkResponse.clone());
            });
          }
          return networkResponse;
        }).catch(function() {});
        return cachedResponse;
      }
      // Not in cache → try network
      return fetch(event.request).then(function(networkResponse) {
        if (networkResponse && networkResponse.status === 200) {
          var cloned = networkResponse.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, cloned);
          });
        }
        return networkResponse;
      }).catch(function() {
        // Offline fallback
        if (event.request.mode === 'navigate') {
          return caches.match('./index.html');
        }
      });
    })
  );
});

// ── BACKGROUND SYNC (future use)
self.addEventListener('sync', function(event) {
  console.log('[QoovySW] Background sync:', event.tag);
});

// ── PUSH NOTIFICATIONS (future use)
self.addEventListener('push', function(event) {
  if (!event.data) return;
  var data = event.data.json();
  self.registration.showNotification(data.title || 'Qoovy', {
    body: data.body || '',
    icon: './icons/icon-192.png',
    badge: './icons/icon-96.png',
    vibrate: [100, 50, 100],
    data: { url: data.url || './' }
  });
});

self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data.url || './')
  );
});