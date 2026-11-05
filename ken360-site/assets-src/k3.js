/* Scroll reveals (fade and rise, staggered). Respects reduced motion. */
(function () {
  'use strict';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var sel = '.k3-hero .wrap > *, .head, .k3-cols > div, .k3-rows li, .k3-combos li, .k3-def, .k3-note, section.block .chips, section.block h3, details, .cta .wrap, .foot > div';
  var els = [].slice.call(document.querySelectorAll(sel));
  if (reduce || !('IntersectionObserver' in window)) { els.forEach(function (el) { el.classList.add('rv', 'in'); }); return; }
  var seen = new Map();
  els.forEach(function (el) {
    var p = el.parentElement, n = seen.get(p) || 0; seen.set(p, n + 1);
    el.classList.add('rv'); el.style.setProperty('--d', Math.min(n, 6) * 80 + 'ms');
  });
  var io = new IntersectionObserver(function (en) {
    en.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } });
  }, { threshold: .12, rootMargin: '0px 0px -6% 0px' });
  els.forEach(function (el) { io.observe(el); });
})();
