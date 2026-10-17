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

  // Contact form: validates in the page; not wired to a mail service yet
  var form = document.getElementById('demo-form');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var done = document.getElementById('form-done');
      form.hidden = true;
      if (done) { done.hidden = false; done.focus(); }
    });
  }
})();
