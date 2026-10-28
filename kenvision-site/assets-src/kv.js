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
      entries.forEach(function (en) { if (en.isIntersecting) { var t = en.target; t.classList.add('in'); io.unobserve(t); setTimeout(function () { t.style.setProperty('--d', '0ms'); }, 1500); } });
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

  // Overlay engine: draws boxes (tracks) or labelled zones over a photo or video. On a photo the counts drift on a clock; on a video they follow the playhead.
  // Shared by the compare slider and the live pictures. Everything it draws is illustrative.
  function overlay(v, svg, hud) {
    var NS = 'http://www.w3.org/2000/svg', cur = null, els = [], hudEls = {}, t0 = performance.now(), isVid = v.tagName === 'VIDEO';
    function mk(tag, cls) { var e = document.createElementNS(NS, tag); if (cls) e.setAttribute('class', cls); return e; }
    function build(sc) {
      cur = sc; svg.innerHTML = ''; hud.innerHTML = ''; els = []; hudEls = {};
      svg.setAttribute('viewBox', '0 0 ' + sc.w + ' ' + sc.h);
      (sc.tracks || []).forEach(function (t) {
        var g = mk('g', 'bx ' + t.kind), rect = mk('rect', 'r'), tag = mk('rect', 't'), txt = mk('text');
        rect.setAttribute('rx', 8); tag.setAttribute('rx', 14); tag.setAttribute('height', 34); tag.setAttribute('width', 26 + t.label.length * 12.6); txt.textContent = t.label;
        if (!t.label) { tag.style.display = 'none'; txt.style.display = 'none'; }
        g.appendChild(rect); g.appendChild(tag); g.appendChild(txt); svg.appendChild(g); els.push({ t: t, g: g, rect: rect, tag: tag, txt: txt });
      });
      (sc.zones || []).forEach(function (z) {
        var g = mk('g', 'zn ' + z.kind), rect = mk('rect', 'r'), tag = mk('rect', 't'), txt = mk('text');
        rect.setAttribute('rx', 24); rect.setAttribute('x', z.x); rect.setAttribute('y', z.y); rect.setAttribute('width', z.w); rect.setAttribute('height', z.h);
        tag.setAttribute('rx', 16); tag.setAttribute('height', 38); tag.setAttribute('x', z.x + 14); tag.setAttribute('y', z.y + 14);
        txt.setAttribute('x', z.x + 30); txt.setAttribute('y', z.y + 40);
        g.appendChild(rect); g.appendChild(tag); g.appendChild(txt); svg.appendChild(g); els.push({ z: z, g: g, tag: tag, txt: txt });
      });
      (sc.hud || []).forEach(function (h) { var s = document.createElement('span'); s.appendChild(document.createTextNode(h[1])); var b = document.createElement('b'); b.textContent = '0'; s.appendChild(b); hud.appendChild(s); hudEls[h[0]] = { b: b, suf: h[2] || '' }; });
    }
    function at(k, time) {
      if (time < k[0][0] || time > k[k.length - 1][0]) return null;
      for (var i = 1; i < k.length; i++) if (time <= k[i][0]) {
        var a = k[i - 1], b = k[i], f = (time - a[0]) / (b[0] - a[0] || 1);
        return [1, 2, 3, 4].map(function (j) { return a[j] + (b[j] - a[j]) * f; });
      }
      return null;
    }
    function draw() {
      if (!cur) return;
      var time = (isVid ? (v.currentTime || 0) : (performance.now() - t0) / 1000) % cur.dur, n = {}, total = 0, zc = 0, peak = null;
      els.forEach(function (o) {
        if (o.t) {
          var b = at(o.t.k, time);
          if (!b || b[2] < 0 || b[0] > cur.w) { o.g.style.display = 'none'; return; }
          o.g.style.display = '';
          o.rect.setAttribute('x', b[0]); o.rect.setAttribute('y', b[1]); o.rect.setAttribute('width', b[2] - b[0]); o.rect.setAttribute('height', b[3] - b[1]);
          o.tag.setAttribute('x', b[0]); o.tag.setAttribute('y', b[1] - 36); o.txt.setAttribute('x', b[0] + 13); o.txt.setAttribute('y', b[1] - 12);
          n[o.t.kind] = (n[o.t.kind] || 0) + 1;
        } else {
          var z = o.z, c = Math.round(z.base + z.amp * Math.sin(time * 0.9 + z.ph) + (z.amp / 3) * Math.sin(time * 2.3 + z.ph * 2));
          if (z.pct) c = Math.max(5, Math.min(99, c));
          var label = z.label + ' \u00b7 ' + c + (z.pct ? '%' : '');
          o.txt.textContent = label; o.tag.setAttribute('width', 34 + label.length * 12.2);
          o.g.style.setProperty('--heat', (0.10 + 0.18 * c / (z.base + z.amp)).toFixed(3));
          total += c; zc++; if (!peak || c > peak[0]) peak = [c, z.label];
        }
      });
      if (cur.zones) { n.total = cur.zones[0] && cur.zones[0].pct ? Math.round(total / Math.max(zc, 1)) : total; if (hudEls.peak) hudEls.peak.b.textContent = peak ? peak[1] : '-'; }
      Object.keys(hudEls).forEach(function (k) { if (k !== 'peak') hudEls[k].b.textContent = (n[k] || 0) + hudEls[k].suf; });
    }
    function loop() { draw(); if (!v.paused) requestAnimationFrame(loop); }
    if (isVid) { v.addEventListener('play', loop); v.addEventListener('seeked', draw); v.addEventListener('timeupdate', draw); v.addEventListener('loadeddata', draw); }
    else if (!reduce && 'IntersectionObserver' in window) {
      var timer = 0;
      new IntersectionObserver(function (es) {
        es.forEach(function (en) { clearInterval(timer); if (en.isIntersecting) timer = setInterval(draw, 250); });
      }, { threshold: 0.1 }).observe(svg);
    }
    return { build: function (sc) { build(sc); draw(); }, draw: draw };
  }

  // Compare slider on stock photos. Right of the handle the overlay is drawn over the photo; data comes from data-scenes.
  $$('[data-compare]').forEach(function (box) {
    var r = box.querySelector('.rng');
    function set() { box.style.setProperty('--pos', r.value + '%'); }
    r.addEventListener('input', set); set();
    var v = box.querySelector('.cv'), svg = box.querySelector('.ov'), hud = box.querySelector('.hud');
    if (!v || !svg || !box.dataset.scenes) return;
    var scenes = JSON.parse(box.dataset.scenes), ov = overlay(v, svg, hud);
    function load(i) {
      var sc = scenes[i]; ov.build(sc);
      v.setAttribute('alt', sc.alt); v.src = sc.src;
    }
    var seg = box.parentNode.querySelector('.kx-seg');
    if (seg) $$('button', seg).forEach(function (btn) {
      btn.addEventListener('click', function () {
        $$('button', seg).forEach(function (o) { o.setAttribute('aria-selected', o === btn ? 'true' : 'false'); });
        load(+btn.dataset.scene);
      });
    });
    ov.build(scenes[0]);
  });

  // Live pictures: a stock photo with KenVision's illustrative overlay on top (solution pages and cards). data-scene holds one scene.
  $$('[data-live]').forEach(function (box) {
    var v = box.querySelector('video, img'), svg = box.querySelector('.ov'), hud = box.querySelector('.hud');
    if (!v || !svg || !box.dataset.scene) return;
    overlay(v, svg, hud).build(JSON.parse(box.dataset.scene));
    var clock = box.querySelector('[data-clock]');
    if (clock) { var tick = function () { var d = new Date(); clock.textContent = d.toISOString().slice(0, 10).replace(/-/g, '/') + '  ' + d.toTimeString().slice(0, 8); }; tick(); setInterval(tick, 1000); }
  });

  // Live dashboard: the figures drift, the hourly bars breathe and the alert cycles, only while the dashboard is on screen
  $$('[data-dash]').forEach(function (d) {
    if (reduce) return;
    var ppl = 1248, dwell = 252, q = 3, kp = {}, bars = $$('[data-bars] i', d), base = bars.map(function (b) { return parseFloat(b.style.getPropertyValue('--h')); });
    $$('[data-kp]', d).forEach(function (b) { kp[b.getAttribute('data-kp')] = b; });
    var toast = d.querySelector('.toast'), msgs = [['Queue alert', 'Checkout 2 \u00b7 long wait'], ['Busy zone', 'Entrance \u00b7 above average'], ['Dwell spike', 'Display wall \u00b7 +40%']], mi = 0, n = 0;
    function tick() {
      n++;
      ppl += Math.round(Math.random() * 9 - 2); dwell = Math.max(200, Math.min(320, dwell + Math.round(Math.random() * 10 - 5))); q = Math.max(2, Math.min(5, q + (Math.random() < .3 ? (Math.random() < .5 ? -1 : 1) : 0)));
      if (kp.people) kp.people.textContent = ppl.toLocaleString('en-US');
      if (kp.dwell) kp.dwell.textContent = Math.floor(dwell / 60) + 'm ' + String(dwell % 60).padStart(2, '0') + 's';
      if (kp.queue) kp.queue.textContent = q + ' min';
      bars.forEach(function (b, i) { b.style.setProperty('--h', Math.max(18, Math.min(98, base[i] + (Math.random() * 14 - 7))).toFixed(0) + '%'); });
      if (toast && n % 4 === 0) {
        mi = (mi + 1) % msgs.length; toast.style.opacity = 0;
        setTimeout(function () { toast.querySelector('b').textContent = msgs[mi][0]; toast.querySelector('small').textContent = msgs[mi][1]; toast.style.opacity = ''; }, 300);
      }
    }
    var timer = 0;
    if ('IntersectionObserver' in window) new IntersectionObserver(function (es) { es.forEach(function (en) { clearInterval(timer); if (en.isIntersecting) timer = setInterval(tick, 1800); }); }, { threshold: 0.2 }).observe(d);
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
  $$('video.kx-vid, .bgv video, video.cv, .kx-live video').forEach(function (v) {
    if (reduce) { v.removeAttribute('autoplay'); v.pause(); return; }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (es) { es.forEach(function (en) { var p = en.isIntersecting ? v.play() : v.pause(); if (p && p.catch) p.catch(function () {}); }); }, { threshold: 0.2 }).observe(v);
    }
  });

  // Sticky header: compact, frosted and hairline-ruled once the page scrolls
  var nav = document.querySelector('header.nav');
  if (nav) {
    var navTick = false;
    var navUpd = function () { navTick = false; nav.classList.toggle('stuck', window.scrollY > 24); };
    addEventListener('scroll', function () { if (!navTick) { navTick = true; requestAnimationFrame(navUpd); } }, { passive: true });
    navUpd();
  }
})();
