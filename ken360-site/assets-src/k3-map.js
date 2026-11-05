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

})();
