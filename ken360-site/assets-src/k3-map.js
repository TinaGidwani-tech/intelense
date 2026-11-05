/* Hero site map: each Ken module is a layer on the same floor plan. Starts with Video + Safety, then the other layers join one by one until the visitor takes over. */
(function () {
  'use strict';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  $$('[data-map]').forEach(function (box) {
    var chips = $$('.lt', box), count = box.querySelector('[data-count]'), card = box.querySelector('[data-card]');
    var layers = {}; chips.forEach(function (c) { layers[c.dataset.k] = $$('[data-l="' + c.dataset.k + '"]', box); });
    var rings = $$('[data-ring]', box), auto = !reduce, timers = [];
    function chip(k) { return chips.filter(function (x) { return x.dataset.k === k; })[0]; }
    function isOn(k) { return chip(k).getAttribute('aria-pressed') === 'true'; }
    function refresh() {
      var n = chips.filter(function (x) { return x.getAttribute('aria-pressed') === 'true'; }).length;
      if (count) count.textContent = n + ' of ' + chips.length;
      var both = isOn('kenvision') && isOn('kensafety');
      rings.forEach(function (r) { r.classList.toggle('on', both); });
      card.classList.toggle('on', both);
    }
    function set(k, on) {
      chip(k).setAttribute('aria-pressed', on ? 'true' : 'false');
      (layers[k] || []).forEach(function (g) { g.classList.toggle('on', on); });
      refresh();
    }
    function stop() { auto = false; timers.forEach(clearTimeout); timers = []; }
    chips.forEach(function (c) { c.addEventListener('click', function () { stop(); set(c.dataset.k, c.getAttribute('aria-pressed') !== 'true'); }); });
    if (reduce) { chips.forEach(function (c) { set(c.dataset.k, true); }); return; }
    chips.forEach(function (c) { set(c.dataset.k, c.dataset.k === 'kenvision' || c.dataset.k === 'kensafety'); });
    ['keniot', 'kenrobotics', 'kenvoice', 'kenhome', 'kenagri'].forEach(function (k, i) {
      timers.push(setTimeout(function () { if (auto) set(k, true); }, 2200 + i * 1500));
    });
  });
})();
