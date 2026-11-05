/* Product-style screens: incident picker (hero), alerts view toggle, module switches. */
(function () {
  'use strict';
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  $$('[data-inbox]').forEach(function (root) {
    var tabs = $$('.u-tabs button', root), panes = $$('.u-pane', root), touched = false;
    function show(v) {
      tabs.forEach(function (t) { t.setAttribute('aria-pressed', t.getAttribute('data-v') === v ? 'true' : 'false'); });
      panes.forEach(function (p) { p.classList.toggle('on', p.getAttribute('data-pane') === v); });
    }
    tabs.forEach(function (t) { t.addEventListener('click', function () { touched = true; show(t.getAttribute('data-v')); }); });
    if (!reduce && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (en) {
        if (en[0].isIntersecting) { io.disconnect(); setTimeout(function () { if (!touched) show('b'); }, 2200); }
      }, { threshold: .6 });
      io.observe(root);
    }
  });


  /* Ken360 engine: wires from the core to each module, one module lit at a time (auto-cycles until the visitor takes over) */
  $$('[data-engine]').forEach(function (root) {
    var lis = $$('.mods7 li', root), sats = $$('.orbit i', root), ring = root.querySelector('[data-ring]'), g = root.querySelector('[data-wires]');
    var pulse = root.querySelector('.pulse'), anim = pulse.querySelector('animateMotion'), from = root.querySelector('[data-from]'), live = root.querySelector('.live');
    var NS = 'http://www.w3.org/2000/svg', paths = [], cur = -1, timer = null, paused = false, visible = false;
    function build() {
      g.innerHTML = ''; paths = [];
      if (window.innerWidth <= 860) return;
      var b = root.getBoundingClientRect(), r = ring.getBoundingClientRect();
      var x1 = r.right - b.left - r.width * .02, y1 = r.top - b.top + r.height / 2;
      lis.forEach(function (li) {
        var l = li.getBoundingClientRect(), x2 = l.left - b.left - (li.classList.contains('on') ? 0 : 0), y2 = l.top - b.top + l.height / 2, dx = (x2 - x1) * .55;
        var p = document.createElementNS(NS, 'path'); p.setAttribute('d', 'M' + x1 + ' ' + y1 + ' C' + (x1 + dx) + ' ' + y1 + ' ' + (x2 - dx) + ' ' + y2 + ' ' + x2 + ' ' + y2);
        p.style.setProperty('--c', li.style.getPropertyValue('--c')); g.appendChild(p); paths.push(p);
      });
      if (cur >= 0) set(cur, true);
    }
    function set(i, force) {
      if (i === cur && !force) return; cur = i;
      lis.forEach(function (l, n) { l.classList.toggle('on', n === i); });
      sats.forEach(function (s, n) { s.classList.toggle('on', n === i); });
      paths.forEach(function (p, n) { p.classList.toggle('on', n === i); });
      var col = lis[i].style.getPropertyValue('--c'); live.style.setProperty('--c', col);
      from.textContent = lis[i].querySelector('.wm').textContent.replace('by Intelense', '').trim();
      if (paths[i]) { anim.setAttribute('path', paths[i].getAttribute('d')); pulse.style.fill = col; root.classList.add('run'); if (anim.beginElement) { try { anim.beginElement(); } catch (e) {} } } else root.classList.remove('run');
    }
    function tick() { if (!paused && visible) set((cur + 1) % lis.length); }
    function start() { if (!reduce && !timer) timer = setInterval(tick, 2600); }
    lis.forEach(function (li, n) {
      li.addEventListener('mouseenter', function () { paused = true; set(n); });
      li.addEventListener('mouseleave', function () { paused = false; });
      li.addEventListener('focusin', function () { paused = true; set(n); });
      li.addEventListener('focusout', function () { paused = false; });
      li.addEventListener('click', function (e) { if (!e.target.closest('a')) { var a = li.querySelector('a'); if (window.innerWidth > 860) { set(n); } else a.click(); } });
    });
    sats.forEach(function (s, n) { s.style.pointerEvents = 'auto'; s.addEventListener('mouseenter', function () { paused = true; set(n); }); s.addEventListener('mouseleave', function () { paused = false; }); });
    if ('ResizeObserver' in window) new ResizeObserver(build).observe(root); addEventListener('resize', build);
    build(); set(0, true);
    if ('IntersectionObserver' in window) new IntersectionObserver(function (en) { visible = en[0].isIntersecting; if (visible) start(); }, { threshold: .3 }).observe(root); else { visible = true; start(); }
  });
})();
