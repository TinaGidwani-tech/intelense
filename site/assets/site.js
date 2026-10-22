// Shared page behaviour: mobile menu, the sensor-to-response diagram, the console clock and the contact form.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Mobile menu
  var btn = document.querySelector('.menu-btn'), menu = document.getElementById('mobile-menu');
  if (btn && menu) {
    btn.addEventListener('click', function () {
      var open = btn.getAttribute('aria-expanded') === 'true';
      btn.setAttribute('aria-expanded', String(!open));
      menu.hidden = open;
    });
  }

  // Sensor-to-response diagram: curved gradient lines with travelling dots
  var flow = document.getElementById('flow'), svg = document.getElementById('lines'), hub = document.getElementById('hub');
  if (flow && svg && hub) {
    var NS = 'http://www.w3.org/2000/svg';
    var add = function (x1, y1, x2, y2, i, out) {
      var mx = (x1 + x2) / 2, p = document.createElementNS(NS, 'path');
      p.setAttribute('d', 'M' + x1 + ',' + y1 + ' C' + mx + ',' + y1 + ' ' + mx + ',' + y2 + ' ' + x2 + ',' + y2);
      p.setAttribute('id', 'fp' + i);
      svg.appendChild(p);
      if (reduce) return;
      var c = document.createElementNS(NS, 'circle'), m = document.createElementNS(NS, 'animateMotion'), mp = document.createElementNS(NS, 'mpath');
      c.setAttribute('r', '3');
      m.setAttribute('dur', (2.6 + (i % 3) * 0.5) + 's');
      m.setAttribute('begin', (out ? 1.4 : 0) + (i * 0.35) + 's');
      m.setAttribute('repeatCount', 'indefinite');
      mp.setAttribute('href', '#fp' + i);
      m.appendChild(mp); c.appendChild(m); svg.appendChild(c);
    };
    var draw = function () {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      if (getComputedStyle(svg).display === 'none') return;
      var r = flow.getBoundingClientRect(), defs = document.createElementNS(NS, 'defs'), lg = document.createElementNS(NS, 'linearGradient');
      lg.setAttribute('id', 'flow-g'); lg.setAttribute('gradientUnits', 'userSpaceOnUse');
      lg.setAttribute('x1', 0); lg.setAttribute('y1', 0); lg.setAttribute('x2', r.width); lg.setAttribute('y2', 0);
      [['0', '#0A34ED'], ['.25', '#7C28E9'], ['.5', '#FF7953'], ['.75', '#78AFCF'], ['1', '#73C4C5']].forEach(function (st) {
        var e = document.createElementNS(NS, 'stop'); e.setAttribute('offset', st[0]); e.setAttribute('stop-color', st[1]); lg.appendChild(e);
      });
      defs.appendChild(lg); svg.appendChild(defs);
      var h = hub.querySelector('.hub-core').getBoundingClientRect();
      svg.setAttribute('viewBox', '0 0 ' + r.width + ' ' + r.height);
      var hx1 = h.left - r.left, hx2 = h.right - r.left, hy = h.top + h.height / 2 - r.top, i = 0;
      flow.querySelectorAll('.col.in .node').forEach(function (n) { var b = n.getBoundingClientRect(); add(b.right - r.left, b.top + b.height / 2 - r.top, hx1, hy, i++, false); });
      flow.querySelectorAll('.col.out .node').forEach(function (n) { var b = n.getBoundingClientRect(); add(hx2, hy, b.left - r.left, b.top + b.height / 2 - r.top, i++, true); });
    };
    var t;
    window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(draw, 120); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(draw);
    draw();
  }

  // Console clock
  var clock = document.getElementById('clock');
  if (clock && !reduce) {
    var s = 14 * 3600 + 32 * 60 + 9;
    var pad = function (n) { return (n < 10 ? '0' : '') + n; };
    setInterval(function () { s++; clock.textContent = pad(Math.floor(s / 3600) % 24) + ':' + pad(Math.floor(s / 60) % 60) + ':' + pad(s % 60); }, 1000);
  }

  // Hover tooltips for chart marks
  var tip = null;
  document.addEventListener('pointerover', function (e) {
    var el = e.target.closest && e.target.closest('[data-tip]');
    if (!el) { if (tip) tip.hidden = true; return; }
    if (!tip) { tip = document.createElement('div'); tip.className = 'tip'; tip.setAttribute('role', 'status'); document.body.appendChild(tip); }
    tip.textContent = el.getAttribute('data-tip'); tip.hidden = false;
  });
  document.addEventListener('pointermove', function (e) { if (tip && !tip.hidden) { tip.style.left = e.clientX + 'px'; tip.style.top = e.clientY + 'px'; } });

  // Live sensor stream (KenIoT): signal inside an expected band, with periodic drift outside it
  document.querySelectorAll('canvas[data-iotstream]').forEach(function (cv) {
    var c = cv.getContext('2d'), W = cv.width, H = cv.height, N = 160, pts = [], t = 0, dark = cv.dataset.iotstream === 'dark';
    var mid = H * .6, band = H * .16;
    function sample(i) {
      var cyc = (i % 420) / 420, drift = cyc > .62 ? Math.sin((cyc - .62) / .38 * Math.PI) * band * 2.1 : 0;
      return mid - drift + Math.sin(i * .35) * band * .35 + Math.sin(i * 1.7) * band * .18 + (Math.random() - .5) * band * .3;
    }
    for (var i = 0; i < N; i++) pts.push(sample(i));
    t = N;
    function draw() {
      c.clearRect(0, 0, W, H);
      c.fillStyle = dark ? 'rgba(115,196,197,.10)' : 'rgba(115,196,197,.16)'; c.fillRect(0, mid - band, W, band * 2);
      c.strokeStyle = dark ? 'rgba(115,196,197,.5)' : 'rgba(30,95,96,.45)'; c.setLineDash([5, 5]); c.lineWidth = 1;
      c.beginPath(); c.moveTo(0, mid - band); c.lineTo(W, mid - band); c.moveTo(0, mid + band); c.lineTo(W, mid + band); c.stroke(); c.setLineDash([]);
      c.font = '600 11px Montserrat, system-ui, sans-serif'; c.fillStyle = dark ? '#9fe0e1' : '#1e5f60'; c.fillText('Expected range', 8, mid - band - 6);
      c.lineWidth = 2; c.lineJoin = 'round';
      for (var k = 1; k < N; k++) {
        var x0 = (k - 1) / (N - 1) * W, x1 = k / (N - 1) * W, out = Math.abs(pts[k] - mid) > band;
        c.strokeStyle = out ? '#FF7953' : (dark ? '#5b7cff' : '#0A34ED');
        c.beginPath(); c.moveTo(x0, pts[k - 1]); c.lineTo(x1, pts[k]); c.stroke();
      }
      var last = pts[N - 1], anomaly = Math.abs(last - mid) > band;
      c.fillStyle = anomaly ? '#FF7953' : (dark ? '#5b7cff' : '#0A34ED'); c.beginPath(); c.arc(W - 4, last, 4, 0, 7); c.fill();
      var tag = cv.parentElement && cv.parentElement.querySelector('[data-iotstatus]');
      if (tag) { tag.textContent = anomaly ? 'Anomaly detected' : 'Within expected range'; tag.classList.toggle('bad', anomaly); }
    }
    draw();
    if (!reduce) setInterval(function () { pts.shift(); pts.push(sample(t++)); draw(); }, 90);
  });

  // Live conversation reveal (KenVoice): lines and insights appear in order, then loop
  document.querySelectorAll('[data-convo]').forEach(function (box) {
    var lines = [].slice.call(box.querySelectorAll('[data-step]'));
    var max = lines.reduce(function (m, el) { return Math.max(m, +el.dataset.step); }, 0);
    function show(n) { lines.forEach(function (el) { el.classList.toggle('on', +el.dataset.step <= n); }); }
    if (reduce) { show(max); return; }
    var n = 0; show(0);
    setInterval(function () { n = n >= max + 2 ? 0 : n + 1; show(n); }, 1700);
  });

  // Fleet map (KenRobotics): robots follow planned routes, detour around an obstacle and slow near a person
  document.querySelectorAll('canvas[data-fleet]').forEach(function (cv) {
    var c = cv.getContext('2d'), W = cv.width, H = cv.height, sx = W / 100, sy = H / 60;
    var ROUTES = [
      { id: 'R-01', col: '#5b7cff', sp: 7, pts: [[8, 6], [92, 6], [92, 30], [80, 30], [76, 32.6], [68, 32.6], [64, 30], [8, 30]] },
      { id: 'R-02', col: '#a98bf5', sp: 6, pts: [[50, 54], [50, 18], [92, 18], [92, 54]] },
      { id: 'R-03', col: '#73C4C5', sp: 6.5, pts: [[8, 42], [50, 42], [50, 6], [8, 6]] },
      { id: 'R-04', col: '#78AFCF', sp: 5.5, pts: [[8, 54], [86, 54], [86, 42], [8, 42]] }
    ];
    ROUTES.forEach(function (r) {
      r.seg = []; r.len = 0;
      for (var i = 0; i < r.pts.length; i++) { var a = r.pts[i], b = r.pts[(i + 1) % r.pts.length], d = Math.hypot(b[0] - a[0], b[1] - a[1]); r.seg.push(d); r.len += d; }
      r.d = Math.random() * r.len;
    });
    function at(r, dist) {
      dist = ((dist % r.len) + r.len) % r.len;
      for (var i = 0; i < r.seg.length; i++) {
        if (dist <= r.seg[i]) { var a = r.pts[i], b = r.pts[(i + 1) % r.pts.length], k = dist / r.seg[i]; return [a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, Math.atan2(b[1] - a[1], b[0] - a[0])]; }
        dist -= r.seg[i];
      }
      return [r.pts[0][0], r.pts[0][1], 0];
    }
    var person = { t: 0 };
    function X(v) { return v * sx; } function Y(v) { return v * sy; }
    function frame(dt) {
      person.t += dt;
      var py = 30 + Math.sin(person.t * .35) * 11, px = 50 + Math.sin(person.t * .9) * .6;
      c.fillStyle = '#16171b'; c.fillRect(0, 0, W, H);
      c.strokeStyle = 'rgba(255,255,255,.04)'; c.lineWidth = 1;
      for (var g = 0; g <= 100; g += 4) { c.beginPath(); c.moveTo(X(g), 0); c.lineTo(X(g), H); c.stroke(); }
      for (g = 0; g <= 60; g += 4) { c.beginPath(); c.moveTo(0, Y(g)); c.lineTo(W, Y(g)); c.stroke(); }
      [[10, 14], [22, 26], [34, 38], [46, 50]].forEach(function (row) {
        [[15, 46], [54, 85]].forEach(function (span) { c.fillStyle = '#2c2e35'; c.fillRect(X(span[0]), Y(row[0]), X(span[1] - span[0]), Y(row[1] - row[0])); c.fillStyle = '#3a3c44'; for (var k = span[0] + 1; k < span[1]; k += 3) c.fillRect(X(k), Y(row[0] + .6), X(2), Y(row[1] - row[0] - 1.2)); });
      });
      c.save(); c.beginPath(); c.rect(X(88), Y(44), X(11), Y(14)); c.clip(); c.strokeStyle = 'rgba(255,121,83,.35)'; c.lineWidth = 3;
      for (var hx = -60; hx < 100; hx += 2.4) { c.beginPath(); c.moveTo(X(hx), Y(60)); c.lineTo(X(hx + 20), Y(40)); c.stroke(); } c.restore();
      c.strokeStyle = '#FF7953'; c.setLineDash([6, 4]); c.lineWidth = 1.5; c.strokeRect(X(88), Y(44), X(11), Y(14)); c.setLineDash([]);
      c.fillStyle = 'rgba(115,196,197,.12)'; c.fillRect(X(1), Y(46), X(5), Y(12)); c.strokeStyle = 'rgba(115,196,197,.6)'; c.strokeRect(X(1), Y(46), X(5), Y(12));
      c.font = '600 ' + Math.round(H / 26) + 'px Montserrat, system-ui, sans-serif';
      c.fillStyle = '#ffb39b'; c.textAlign = 'right'; c.fillText('Restricted', X(99), Y(43)); c.textAlign = 'left';
      c.fillStyle = '#9fe0e1'; c.fillText('Charging', X(1), Y(45));
      c.fillStyle = '#7a5f45'; c.fillRect(X(70), Y(28.6), X(3.2), Y(2.8)); c.strokeStyle = '#FF7953'; c.lineWidth = 1.5; c.strokeRect(X(69.4), Y(28), X(4.4), Y(4)); c.fillStyle = '#ffb39b'; c.fillText('Obstacle', X(66), Y(27.2));
      c.strokeStyle = 'rgba(255,121,83,.55)'; c.setLineDash([4, 4]); c.beginPath(); c.arc(X(px), Y(py), X(3.2), 0, 7); c.stroke(); c.setLineDash([]);
      c.strokeStyle = 'rgba(115,196,197,.5)'; c.beginPath(); c.arc(X(px), Y(py), X(6.5), 0, 7); c.stroke();
      c.fillStyle = '#e9e9ec'; c.beginPath(); c.arc(X(px), Y(py), X(.9), 0, 7); c.fill();
      c.fillStyle = '#e9e9ec'; c.fillText('Person', X(px + 1.6), Y(py - 1.2));
      ROUTES.forEach(function (r) {
        var p = at(r, r.d), near = Math.hypot(p[0] - px, (p[1] - py) * 1) < 6.5;
        r.speed = near ? r.sp * .3 : r.sp; r.d += r.speed * dt; r.near = near;
        c.strokeStyle = r.col; c.globalAlpha = .55; c.setLineDash([5, 5]); c.lineWidth = 1.5; c.beginPath();
        for (var k = 0; k <= 26; k += 1) { var q = at(r, r.d + k); if (k === 0) c.moveTo(X(q[0]), Y(q[1])); else c.lineTo(X(q[0]), Y(q[1])); }
        c.stroke(); c.setLineDash([]); c.globalAlpha = 1;
        p = at(r, r.d);
        c.fillStyle = r.col; c.beginPath(); c.arc(X(p[0]), Y(p[1]), X(1.5), 0, 7); c.fill();
        c.strokeStyle = '#101114'; c.lineWidth = 2; c.beginPath(); c.moveTo(X(p[0]), Y(p[1])); c.lineTo(X(p[0] + Math.cos(p[2]) * 1.5), Y(p[1] + Math.sin(p[2]) * 1.5)); c.stroke();
        c.fillStyle = '#e9e9ec'; c.fillText(r.id, X(p[0] + 1.8), Y(p[1] - 1.6));
        var el = document.querySelector('[data-fleet-status="' + r.id + '"]');
        if (el) { el.textContent = near ? 'Slowing' : (Math.abs(p[1] - 30) < 3 && p[0] > 62 && p[0] < 82 ? 'Rerouting' : 'On route'); el.className = near ? 'warn' : ''; }
      });
    }
    var last = performance.now();
    frame(0);
    if (!reduce) (function loop(now) { var dt = Math.min(.05, (now - last) / 1000); last = now; frame(dt); requestAnimationFrame(loop); })(last);
  });

  // Offices: highlight the matching marker on the world map while its card is hovered or focused
  var wm = document.querySelector('.worldmap');
  if (wm) {
    document.querySelectorAll('.office[data-pin]').forEach(function (card) {
      var cls = 'is-' + card.getAttribute('data-pin');
      ['mouseenter', 'focusin'].forEach(function (ev) { card.addEventListener(ev, function () { wm.classList.add(cls); }); });
      ['mouseleave', 'focusout'].forEach(function (ev) { card.addEventListener(ev, function () { wm.classList.remove(cls); }); });
    });
  }

  // Light / dark toggle: remembers the choice in this browser, and tells the cursor grid to redraw in the new colour
  var themeBtn = document.querySelector('.theme-btn');
  if (themeBtn) {
    var root = document.documentElement;
    var label = function () {
      var dark = root.dataset.theme === 'dark';
      themeBtn.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
      themeBtn.setAttribute('title', dark ? 'Switch to light mode' : 'Switch to dark mode');
    };
    label();
    themeBtn.addEventListener('click', function () {
      var next = root.dataset.theme === 'dark' ? 'light' : 'dark';
      root.dataset.theme = next;
      try { localStorage.setItem('theme', next); } catch (e) {}
      label();
      window.dispatchEvent(new Event('themechange'));
    });
  }

  // Contact form: validates in the page, then posts to /send-message.php on this site, which emails enquiries@intelense.ca
  var form = document.getElementById('demo-form');
  if (form) {
    var note = document.getElementById('form-status');
    var btn = form.querySelector('button[type="submit"]');
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var data = {};
      ['first_name', 'last_name', 'email', 'company', 'interest', 'message', '_honey'].forEach(function (n) { data[n] = form.elements[n] ? form.elements[n].value : ''; });
      btn.disabled = true;
      if (note) note.textContent = 'Sending...';
      fetch('/send-message.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { return r.json().then(function (j) { if (!r.ok || !j.ok) throw new Error(j.error || 'send failed'); }); })
        .then(function () {
          var done = document.getElementById('form-done');
          form.hidden = true;
          if (done) { done.hidden = false; done.focus(); }
        })
        .catch(function (err) {
          btn.disabled = false;
          if (note) note.textContent = (err && err.message && err.message.indexOf('Please') === 0 ? err.message + ' ' : 'We could not send that. ') + 'You can also email enquiries@intelense.ca.';
        });
    });
  }
})();

// Live clock on real camera feeds
(function () {
  var els = document.querySelectorAll('[data-feed-clock]');
  if (!els.length) return;
  function tick() { var t = new Date().toTimeString().slice(0, 8); els.forEach(function (e) { e.textContent = t; }); }
  tick(); setInterval(tick, 1000);
})();
