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
