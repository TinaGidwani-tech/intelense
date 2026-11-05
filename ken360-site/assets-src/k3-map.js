/* Product-style screens: incident picker (hero), alerts view toggle, module switches. */
(function () {
  'use strict';
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;

  $$('[data-incidents]').forEach(function (root) {
    var rows = $$('.ir', root), panes = $$('.ip', root);
    rows.forEach(function (r) {
      r.addEventListener('click', function () {
        var i = r.getAttribute('data-i');
        rows.forEach(function (x) { x.classList.toggle('on', x === r); });
        panes.forEach(function (p) { p.classList.toggle('on', p.getAttribute('data-p') === i); });
      });
    });
  });

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

  $$('[data-mods]').forEach(function (root) {
    var sws = $$('.sw', root), out = root.querySelector('[data-mcount]');
    sws.forEach(function (s) {
      s.addEventListener('click', function () {
        s.setAttribute('aria-checked', s.getAttribute('aria-checked') === 'true' ? 'false' : 'true');
        s.closest('li').classList.toggle('off', s.getAttribute('aria-checked') !== 'true');
        out.textContent = sws.filter(function (x) { return x.getAttribute('aria-checked') === 'true'; }).length + ' of ' + sws.length;
      });
    });
  });
})();
