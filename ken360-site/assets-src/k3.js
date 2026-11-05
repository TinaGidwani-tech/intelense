/* Ken360 home page: scroll reveal, scroll-linked "how it works", and the combinations picker. Everything is visible without JavaScript. */
(function () {
  'use strict';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // Scroll reveal
  var els = $$('[data-r]');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } }); }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    els.forEach(function (el) { io.observe(el); });
  } else { els.forEach(function (el) { el.classList.add('in'); }); }

  // "How it works": the line fills as the section scrolls past and each step lights up
  $$('[data-how]').forEach(function (box) {
    var lis = $$('.stp > li', box), mq = window.matchMedia('(min-width: 801px)'), ticking = false;
    function upd() {
      ticking = false;
      var r = box.getBoundingClientRect(), vh = window.innerHeight;
      var p = reduce ? 1 : Math.max(0, Math.min(1, (vh * 0.7 - r.top) / (r.height * 0.8)));
      box.style.setProperty('--p', p.toFixed(3));
      var horiz = mq.matches, end = p * (horiz ? r.width : r.height);
      lis.forEach(function (li) { var lr = li.getBoundingClientRect(), pos = horiz ? lr.left - r.left : lr.top - r.top; li.classList.toggle('on', end >= pos + 6); });
    }
    function queue() { if (!ticking) { ticking = true; requestAnimationFrame(upd); } }
    addEventListener('scroll', queue, { passive: true }); addEventListener('resize', queue); upd();
  });

  // Combinations picker
  $$('[data-combos]').forEach(function (box) {
    var data = JSON.parse(box.dataset.set), names = JSON.parse(box.dataset.names), cols = JSON.parse(box.dataset.cols);
    var chips = $$('.mt', box), list = box.querySelector('.list'), sum = box.querySelector('.sum');
    function on() { return chips.filter(function (c) { return c.getAttribute('aria-pressed') === 'true'; }).map(function (c) { return c.dataset.k; }); }
    function render() {
      var sel = on(), hits = data.filter(function (d) { return sel.indexOf(d.a) > -1 && sel.indexOf(d.b) > -1; });
      var n = sel.length;
      sum.innerHTML = '<b>' + hits.length + '</b><span>' + (hits.length === 1 ? 'combination' : 'combinations') + ' unlocked by ' + n + ' module' + (n === 1 ? '' : 's') + '</span>';
      if (!hits.length) {
        list.innerHTML = '<div class="empty">' + (n < 2 ? 'Switch on at least two modules to see what they can catch together.' : 'These modules run side by side. We will go through what they can catch together on your site in a demo.') + '</div>';
        return;
      }
      list.innerHTML = hits.map(function (d) {
        return '<div class="cmb"><div class="pair"><span><i class="md" style="--c:' + cols[d.a] + '"></i>' + names[d.a] + '</span><em>+</em><span><i class="md" style="--c:' + cols[d.b] + '"></i>' + names[d.b] + '</span></div>' +
          '<h3>' + d.t + '</h3><p>' + d.p + '</p>' + (d.ok ? '' : '<span class="dr">Draft example</span>') + '</div>';
      }).join('');
    }
    chips.forEach(function (c) { c.addEventListener('click', function () { c.setAttribute('aria-pressed', c.getAttribute('aria-pressed') === 'true' ? 'false' : 'true'); render(); }); });
    render();
  });
})();
