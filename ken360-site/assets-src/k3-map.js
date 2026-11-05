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


  /* Ken360 engine: on desktop the modules join the core one by one as the visitor scrolls (calm, no looping motion) */
  $$('[data-story]').forEach(function (root) {
    var stage = root.querySelector('.stage'), lis = $$('.mods7 li', root), ring = root.querySelector('[data-ring]'), g = root.querySelector('[data-wires]');
    var eng = root.querySelector('.k3-engine'), cap = root.querySelector('[data-cap]'), cnt = root.querySelector('[data-count]'), bars = $$('.prog i', root);
    var NS = 'http://www.w3.org/2000/svg', paths = [], step = -1, capT;
    var mq = window.matchMedia('(min-width:861px)');
    function on() { return mq.matches && !reduce; }
    function build() {
      g.innerHTML = ''; paths = [];
      if (window.innerWidth <= 860) return;
      var b = eng.getBoundingClientRect(), r = ring.getBoundingClientRect();
      var x1 = r.right - b.left - r.width * .02, y1 = r.top - b.top + r.height / 2;
      lis.forEach(function (li) {
        var l = li.getBoundingClientRect(), x2 = l.left - b.left, y2 = l.top - b.top + l.height / 2, dx = (x2 - x1) * .55;
        var p = document.createElementNS(NS, 'path'); p.setAttribute('d', 'M' + x1 + ' ' + y1 + ' C' + (x1 + dx) + ' ' + y1 + ' ' + (x2 - dx) + ' ' + y2 + ' ' + x2 + ' ' + y2);
        p.style.stroke = li.style.getPropertyValue('--c'); g.appendChild(p); paths.push(p);
        var len = p.getTotalLength(); p.style.strokeDasharray = len; p.setAttribute('data-len', len);
      });
      apply(step < 0 ? 0 : step, true);
    }
    function text(n) {
      if (n === 0) return 'Ken360 is the core AI technology from Intelense. Every Ken module runs on it.';
      if (n === 7) return 'Seven modules, one engine, one picture of your site.';
      var name = lis[n - 1].getAttribute('data-n'), add = lis[n - 1].getAttribute('data-add').split(':')[0].toLowerCase();
      return n === 1 ? name + ' joins first. It feeds ' + add + ' into the shared data model.' : name + ' joins the same engine. Ken360 can now compare its ' + add + ' with what ' + (n === 2 ? 'the first module sees.' : 'the other ' + (n - 1) + ' see.');
    }
    function apply(n, force) {
      if (!on()) { root.classList.remove('story-on'); lis.forEach(function (l) { l.classList.remove('joined', 'new'); }); paths.forEach(function (p) { p.style.strokeDashoffset = 0; }); cnt.textContent = '7'; return; }
      root.classList.add('story-on');
      if (n === step && !force) return;
      var changed = n !== step; step = n;
      lis.forEach(function (l, i) { l.classList.toggle('joined', i < n); l.classList.toggle('new', i === n - 1 && n < 7); });
      paths.forEach(function (p, i) { p.style.strokeDashoffset = i < n ? 0 : p.getAttribute('data-len'); });
      cnt.textContent = n; bars.forEach(function (b, i) { b.classList.toggle('on', i <= n); });
      if (changed) { cap.classList.add('sw'); clearTimeout(capT); capT = setTimeout(function () { cap.textContent = text(n); cap.classList.remove('sw'); }, 180); }
    }
    function upd() {
      if (!on()) { apply(7, true); return; }
      var r = root.getBoundingClientRect(), span = r.height - stage.offsetHeight;
      var p = Math.max(0, Math.min(1, -r.top / Math.max(span, 1)));
      apply(Math.min(7, Math.floor(p * 8)));
    }
    var tick = false; function req() { if (!tick) { tick = true; requestAnimationFrame(function () { tick = false; upd(); }); } }
    addEventListener('scroll', req, { passive: true });
    addEventListener('resize', function () { build(); upd(); });
    apply(on() ? 0 : 7, true); build(); upd();
  });
})();
