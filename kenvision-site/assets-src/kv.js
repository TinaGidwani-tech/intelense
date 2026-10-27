/* KenVision micro-interactions: scroll reveal, count-up, spotlight cards, tilt, magnetic buttons, tabs, scroll progress.
   Everything is progressive: without this script the page is fully visible and usable. */
(function () {
  'use strict';
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  var fine = window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // Scroll reveal
  var revealEls = $$('[data-r]');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  // Count-up for figures such as 99%, +40%, < 2s, 10X
  var counters = $$('[data-count]');
  function runCount(el) {
    var m = /^([^0-9]*)(\d+(?:\.\d+)?)(.*)$/.exec(el.getAttribute('data-final') || el.textContent.trim());
    if (!m) return;
    var pre = m[1], end = parseFloat(m[2]), post = m[3], t0 = null, dur = 1300;
    el.setAttribute('data-final', el.textContent.trim());
    function frame(t) {
      if (t0 === null) t0 = t;
      var p = Math.min(1, (t - t0) / dur), eased = 1 - Math.pow(1 - p, 3);
      el.textContent = pre + Math.round(end * eased) + post;
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  if ('IntersectionObserver' in window && !reduce) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { runCount(en.target); cio.unobserve(en.target); } });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  // Cursor spotlight on cards
  if (fine) {
    var raf = 0;
    document.addEventListener('pointermove', function (e) {
      if (raf) return;
      raf = requestAnimationFrame(function () {
        raf = 0;
        var t = e.target && e.target.closest && e.target.closest('.spot');
        if (!t) return;
        var r = t.getBoundingClientRect();
        t.style.setProperty('--mx', (e.clientX - r.left) + 'px');
        t.style.setProperty('--my', (e.clientY - r.top) + 'px');
      });
    }, { passive: true });

    // Tilt on the hero picture
    $$('[data-tilt]').forEach(function (el) {
      var host = el.closest('.page-hero') || el;
      host.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        el.style.setProperty('--ry', (x * 7).toFixed(2) + 'deg');
        el.style.setProperty('--rx', (-y * 5).toFixed(2) + 'deg');
      });
      host.addEventListener('pointerleave', function () { el.style.setProperty('--ry', '0deg'); el.style.setProperty('--rx', '0deg'); });
    });

    // Magnetic primary buttons
    $$('.hero-ctas .btn-blue, .cta .btn-blue').forEach(function (b) {
      b.addEventListener('pointermove', function (e) {
        var r = b.getBoundingClientRect();
        b.style.transform = 'translate(' + ((e.clientX - r.left - r.width / 2) * 0.12).toFixed(1) + 'px,' + ((e.clientY - r.top - r.height / 2) * 0.22).toFixed(1) + 'px)';
      });
      b.addEventListener('pointerleave', function () { b.style.transform = ''; });
    });
  }

  // Tabs (keyboard accessible). data-auto: advance by itself until the visitor takes over.
  $$('[data-tabs]').forEach(function (box) {
    var tabs = $$('[role="tab"]', box), panels = $$('[data-panel]', box), label = box.querySelector('[data-label]');
    var auto = box.hasAttribute('data-auto');
    function set(n, byUser) {
      tabs.forEach(function (t, k) { t.setAttribute('aria-selected', k === n ? 'true' : 'false'); t.tabIndex = k === n ? 0 : -1; });
      panels.forEach(function (p, k) { p.classList.toggle('off', k !== n); if (k !== n) p.setAttribute('aria-hidden', 'true'); else p.removeAttribute('aria-hidden'); });
      box.setAttribute('data-i', n);
      if (label) label.textContent = tabs[n].querySelector('.t').textContent;
      if (byUser && auto) { auto = false; box.classList.add('manual'); }
    }
    tabs.forEach(function (t, k) {
      t.addEventListener('click', function () { set(k, true); });
      if (box.classList.contains('std')) t.addEventListener('mouseenter', function () { if (fine) set(k, true); });
      t.addEventListener('keydown', function (e) {
        var d = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0;
        if (!d) return;
        e.preventDefault();
        var n = (k + d + tabs.length) % tabs.length;
        set(n, true); tabs[n].focus();
      });
      var bar = t.querySelector('.bar');
      if (bar) bar.addEventListener('animationend', function () { if (auto && t.getAttribute('aria-selected') === 'true') set((k + 1) % tabs.length, false); });
    });
    if (reduce) { auto = false; box.classList.add('manual'); }
    set(0, false);
  });

  // "How it works": the line fills as the section scrolls past and lights each step when the line reaches its dot
  $$('[data-how]').forEach(function (box) {
    var lis = $$('.stp > li', box), mq = window.matchMedia('(min-width: 801px)'), ticking = false;
    function upd() {
      ticking = false;
      var r = box.getBoundingClientRect(), vh = window.innerHeight;
      var p = reduce ? 1 : Math.max(0, Math.min(1, (vh * 0.7 - r.top) / (r.height * 0.8)));
      box.style.setProperty('--p', p.toFixed(3));
      var horiz = mq.matches, end = p * (horiz ? r.width : r.height);
      lis.forEach(function (li) {
        var lr = li.getBoundingClientRect(), pos = horiz ? lr.left - r.left : lr.top - r.top;
        li.classList.toggle('on', end >= pos + 6);
      });
    }
    function queue() { if (!ticking) { ticking = true; requestAnimationFrame(upd); } }
    addEventListener('scroll', queue, { passive: true });
    addEventListener('resize', queue);
    upd();
  });

  // Compare slider
  $$('[data-compare]').forEach(function (box) {
    var r = box.querySelector('.rng');
    function set() { box.style.setProperty('--pos', r.value + '%'); }
    r.addEventListener('input', set); set();
  });

  // Sector carousel
  $$('[data-car]').forEach(function (car) {
    var tr = car.querySelector('.track'), cards = $$('.cc', car), dots = car.querySelector('.dots');
    cards.forEach(function () { dots.appendChild(document.createElement('i')); });
    var di = $$('i', dots);
    function step() { return cards[0].getBoundingClientRect().width + 20; }
    function upd() { var n = Math.round(tr.scrollLeft / step()); di.forEach(function (d, k) { d.classList.toggle('on', k === Math.min(n, di.length - 1)); }); }
    car.querySelector('[data-prev]').addEventListener('click', function () { tr.scrollBy({ left: -step(), behavior: reduce ? 'auto' : 'smooth' }); });
    car.querySelector('[data-next]').addEventListener('click', function () { tr.scrollBy({ left: step(), behavior: reduce ? 'auto' : 'smooth' }); });
    tr.addEventListener('scroll', function () { requestAnimationFrame(upd); }, { passive: true });
    upd();
  });

  // Clips: stay on the poster for reduced motion, otherwise play only while on screen
  $$('video.kx-vid, .bgv video').forEach(function (v) {
    if (reduce) { v.removeAttribute('autoplay'); v.pause(); return; }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { es.forEach(function (en) { var p = en.isIntersecting ? v.play() : v.pause(); if (p && p.catch) p.catch(function () {}); }); }, { threshold: 0.2 }).observe(v);
    }
  });

  // Thin progress bar under the top edge
  var bar = document.createElement('div');
  bar.className = 'kx-progress';
  bar.setAttribute('aria-hidden', 'true');
  document.body.appendChild(bar);
  var ticking = false;
  function prog() {
    var h = document.documentElement.scrollHeight - innerHeight;
    bar.style.transform = 'scaleX(' + (h > 0 ? Math.min(1, scrollY / h) : 0) + ')';
    ticking = false;
  }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(prog); } }, { passive: true });
  prog();
})();
