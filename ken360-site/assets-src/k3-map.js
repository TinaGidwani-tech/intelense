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


  /* Ken360 engine: static connector lines from the core to each module */
  $$('[data-story]').forEach(function (root) {
    var lis = $$('.mods7 li', root), ring = root.querySelector('[data-ring]'), g = root.querySelector('[data-wires]'), eng = root.querySelector('.k3-engine');
    var NS = 'http://www.w3.org/2000/svg';
    function build() {
      g.innerHTML = '';
      if (window.innerWidth <= 860) return;
      var b = eng.getBoundingClientRect(), r = ring.getBoundingClientRect();
      var x1 = r.right - b.left - r.width * .02, y1 = r.top - b.top + r.height / 2;
      lis.forEach(function (li) {
        var l = li.getBoundingClientRect(), x2 = l.left - b.left, y2 = l.top - b.top + l.height / 2, dx = (x2 - x1) * .55;
        var p = document.createElementNS(NS, 'path'); p.setAttribute('d', 'M' + x1 + ' ' + y1 + ' C' + (x1 + dx) + ' ' + y1 + ' ' + (x2 - dx) + ' ' + y2 + ' ' + x2 + ' ' + y2);
        p.style.stroke = li.style.getPropertyValue('--c'); g.appendChild(p);
      });
    }
    if ('ResizeObserver' in window) new ResizeObserver(build).observe(eng);
    addEventListener('resize', build); build();
  });
})();
