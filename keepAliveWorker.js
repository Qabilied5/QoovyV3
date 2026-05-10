//  QOOVY — KEEPALIVE WORKER
//  Berjalan di background thread, tidak terpengaruh
//  Page Visibility / browser minimize
//  --- REFERENCE

var tickInterval = null;
var heartbeatInterval = null;

// Tick setiap 500ms — kirim sinyal ke main thread
function startTick() {
  if (tickInterval) return;
  tickInterval = setInterval(function () {
    self.postMessage({ type: 'TICK', ts: Date.now() });
  }, 500);
}

function stopTick() {
  if (tickInterval) { clearInterval(tickInterval); tickInterval = null; }
}

// Heartbeat lebih jarang — untuk keepalive SW
function startHeartbeat() {
  if (heartbeatInterval) return;
  heartbeatInterval = setInterval(function () {
    self.postMessage({ type: 'HEARTBEAT', ts: Date.now() });
  }, 20000);
}

function stopHeartbeat() {
  if (heartbeatInterval) { clearInterval(heartbeatInterval); heartbeatInterval = null; }
}

self.addEventListener('message', function (e) {
  var msg = e.data;
  if (!msg) return;

  switch (msg.type) {
    case 'START':
      startTick();
      startHeartbeat();
      self.postMessage({ type: 'WORKER_READY' });
      break;
    case 'STOP':
      stopTick();
      stopHeartbeat();
      break;
    case 'PING':
      self.postMessage({ type: 'PONG', ts: Date.now() });
      break;
  }
});

// Auto-start
startTick();
startHeartbeat();