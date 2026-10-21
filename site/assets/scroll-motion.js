// Scroll-motion layer for index.html. Vanilla JS, one passive scroll listener, one rAF loop.
// Writes progress into CSS custom properties and class toggles; only transform-family properties and opacity animate.
// The first block runs in <head> so content is never hidden after it has painted; the rest runs on DOMContentLoaded.

// ---- Tuning (speed, stagger, pin length) ----
var CONFIG = {
  PIN_VH: 2.8,            // height of the "How it works" scroll track, in viewport heights (about 250 to 300vh)
  PIN_TOP_VH: 6,          // where the pinned diagram sticks, as vh from the top
  STAGGER_MS: 75,         // card and chip stagger (60 to 90ms)
  HERO_LINE_MS: 90,       // delay between lines of the hero headline and lede
  PARALLAX: { washA: 0.12, washB: 0.2, washC: 0.25, media: 0.1 }, // fraction of scroll distance (keep within 0.10 to 0.25)
  THUMB_SHIFT: 7,         // module photo parallax travel, percent of the photo height each way
  MARQUEE_GAIN: 0.8,      // how strongly scroll velocity (px/ms) speeds up the logo marquee
  MARQUEE_MAX: 2.6,       // marquee speed ceiling, 1 = normal speed
  MARQUEE_EASE: 0.08,     // how quickly the marquee eases back to normal (per frame)
  CTA_SCALE: [0.8, 1.25], // CTA gradient scale at far / at viewport centre
  TC_TOTAL_SEC: 150,      // timecode value at the bottom of the page (00:02:30)
  WIDE_QUERY: '(min-width: 900px) and (hover: hover) and (pointer: fine)' // parallax, pinning and timecode only here
};

(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (reduce.matches || !('IntersectionObserver' in window)) return; // everything stays static and visible
  root.classList.add('js-motion');
  setTimeout(function () { root.classList.add('mo-ready'); }, 2500); // safety net if the script below fails

  var wideMQ = window.matchMedia(CONFIG.WIDE_QUERY);
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return [].slice.call((c || document).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return v < a ? a : v > b ? b : v; };
  var pad = function (n) { return (n < 10 ? '0' : '') + n; };

  function init() {
    var hero = $('.hero');
    var sy = window.pageYOffset;

    // ---------- Mode: wide pointer devices get parallax, pinning and the timecode ----------
    function applyMode() {
      root.classList.toggle('js-motion-wide', wideMQ.matches);
      root.classList.toggle('js-pin', wideMQ.matches && !!pin);
      measure();
    }

    // ---------- Hero: masked line reveal on load ----------
    function splitWords(el) {
      var words = [];
      (function walk(node) {
        [].slice.call(node.childNodes).forEach(function (n) {
          if (n.nodeType === 3) {
            var frag = document.createDocumentFragment();
            n.nodeValue.split(/(\s+)/).forEach(function (part) {
              if (!part) return;
              if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
              var w = document.createElement('span'), i = document.createElement('span');
              w.className = 'mw'; i.textContent = part; w.appendChild(i); frag.appendChild(w); words.push(w);
            });
            node.replaceChild(frag, n);
          } else if (n.nodeType === 1 && n.tagName !== 'BR') walk(n);
        });
      })(el);
      // group into visual lines, then stagger line by line
      var tops = words.map(function (w) { return w.offsetTop; }), lines = [];
      tops.forEach(function (t) { if (lines.indexOf(t) < 0) lines.push(t); });
      words.forEach(function (w, i) { w.firstChild.style.setProperty('--d', (lines.indexOf(tops[i]) * CONFIG.HERO_LINE_MS) + 'ms'); });
      return lines.length;
    }
    if (hero) {
      var h1 = $('h1', hero), lede = $('.lede', hero), n1 = h1 ? splitWords(h1) : 0, n2 = 0;
      if (lede) {
        n2 = splitWords(lede);
        $$('.mw > span', lede).forEach(function (s) { s.style.setProperty('--d', (parseFloat(s.style.getPropertyValue('--d')) + n1 * CONFIG.HERO_LINE_MS + 120) + 'ms'); });
      }
      var base = (n1 + n2) * CONFIG.HERO_LINE_MS + 160, k = 0;
      $$('.eyebrow, .hero-ctas, .hero-meta', hero).forEach(function (el) { el.classList.add('rv-hero'); el.style.setProperty('--d', (el.classList.contains('eyebrow') ? 0 : base + (k++) * CONFIG.STAGGER_MS) + 'ms'); });
      var hm = $('.hero-media', hero);
      if (hm) { var f = $('.feed', hm); if (f) { f.classList.add('rv-clip'); f.style.setProperty('--d', (base + 2 * CONFIG.STAGGER_MS) + 'ms'); f.style.setProperty('--r', '32px'); } }
      root.classList.add('mo-ready');
      requestAnimationFrame(function () { requestAnimationFrame(function () {
        root.classList.add('hero-in');
        if (f) f.classList.add('is-in');
      }); });
    } else root.classList.add('mo-ready');

    // ---------- Generic reveals (play once) ----------
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        if (e.target.matches('.card.feature')) e.target.classList.add('tags-in');
        io.unobserve(e.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    function reveal(el, delay, cls) {
      if (!el) return;
      el.classList.add(cls || 'rv');
      if (delay) el.style.setProperty('--d', delay + 'ms');
      io.observe(el);
    }
    $$('.head').forEach(function (h) { [].slice.call(h.children).forEach(function (c, i) { reveal(c, i * CONFIG.STAGGER_MS); }); });
    $$('#modules .modules > .card').forEach(function (c, i) { reveal(c, i === 0 ? 0 : ((i - 1) % 3) * CONFIG.STAGGER_MS); });
    $$('.card.feature .feed-tag').forEach(function (t, i) { t.style.setProperty('--d', (260 + i * 90) + 'ms'); });
    var clients = $('#clients .clients'); if (clients) { clients.style.setProperty('--r', '36px'); reveal(clients, 0, 'rv-clip'); }
    $$('#clients .client-sectors > *').forEach(function (c, i) { reveal(c, i * 50); });
    $$('#sectors .sectors > *').forEach(function (c, i) { reveal(c, i * 45); });
    $$('#sectors .proof, #platform > .wrap > p').forEach(function (c) { reveal(c, 0); });
    $$('#sectors img, #sectors .feed, .cta img, .cta .feed').forEach(function (c, i) { reveal(c, i * CONFIG.STAGGER_MS, 'rv-clip'); });
    $$('#faq .faq-grid > *').forEach(function (c, i) { reveal(c, i * CONFIG.STAGGER_MS); });
    $$('.cta .wrap > *').forEach(function (c, i) { reveal(c, i * CONFIG.STAGGER_MS); });

    // ---------- "How it works": pinned, scroll-scrubbed ----------
    var flow = $('#flow'), steps = $('#platform .steps'), pin = null, pinStage = null, wrapTop = 0, wrapH = 0, stageH = 0, pinTopPx = 0;
    var inNodes = [], outNodes = [], hubEl = null, stepEls = [], paths = [], pathsKey = null, last = { nodes: -1, hub: -1, step: -1, run: -1, out: -1 }, drawn = [];
    if (flow && steps) {
      pin = document.createElement('div'); pin.className = 'pin-wrap';
      pinStage = document.createElement('div'); pinStage.className = 'pin-stage';
      flow.parentNode.insertBefore(pin, flow); pin.appendChild(pinStage); pinStage.appendChild(flow); pinStage.appendChild(steps);
      pin.style.setProperty('--pin-vh', CONFIG.PIN_VH); pin.style.setProperty('--pin-top', CONFIG.PIN_TOP_VH + 'vh');
      inNodes = $$('.col.in .node', flow); outNodes = $$('.col.out .node', flow); hubEl = $('#hub', flow); stepEls = $$('div', steps);
    }
    function refreshPaths() {
      var svg = $('#lines'); if (!svg) return;
      var list = $$('path', svg);
      if (list[0] === pathsKey) return; // site.js redraws the lines on resize; pick the new ones up
      pathsKey = list[0]; paths = list; drawn = [];
      list.forEach(function (p) { p.setAttribute('pathLength', '1'); });
    }
    var T = { nodeStart: 0.04, nodeStep: 0.055, inDraw: [0.10, 0.05, 0.22], hub: 0.52, outDraw: [0.56, 0.04, 0.20], outStart: 0.74, outStep: 0.05, run: 0.9, steps: [0.03, 0.50, 0.74] };
    function scrub(p) {
      refreshPaths();
      var i, v, lit;
      // nodes in
      lit = 0; inNodes.forEach(function (n, j) { var on = p >= T.nodeStart + j * T.nodeStep; n.classList.toggle('is-lit', on); if (on) lit++; });
      // lines drawing toward the hub, then away from it
      paths.forEach(function (path, j) {
        var o = j >= inNodes.length, k = o ? j - inNodes.length : j, cfg = o ? T.outDraw : T.inDraw;
        v = clamp((p - (cfg[0] + k * cfg[1])) / cfg[2], 0, 1);
        if (drawn[j] === undefined || Math.abs(drawn[j] - v) > 0.002) { drawn[j] = v; path.style.setProperty('--draw', v.toFixed(3)); }
      });
      // hub
      var hubOn = p >= T.hub ? 1 : 0;
      if (hubOn !== last.hub && hubEl) {
        hubEl.classList.toggle('is-on', !!hubOn);
        hubEl.classList.remove('is-pulse');
        if (hubOn) { void hubEl.offsetWidth; hubEl.classList.add('is-pulse'); }
        last.hub = hubOn;
      }
      // nodes out
      outNodes.forEach(function (n, j) { n.classList.toggle('is-lit', p >= T.outStart + j * T.outStep); });
      // dots travel only once everything is lit
      var run = p >= T.run ? 1 : 0; if (run !== last.run) { pinStage.classList.toggle('flow-run', !!run); last.run = run; }
      // steps
      var cur = p >= T.steps[2] ? 2 : p >= T.steps[1] ? 1 : p >= T.steps[0] ? 0 : -1;
      if (cur !== last.step) {
        stepEls.forEach(function (s, j) { s.classList.toggle('is-on', j <= cur); s.classList.toggle('is-now', j === cur); });
        last.step = cur;
      }
    }

    // ---------- Module photo parallax ----------
    var thumbs = $$('.thumb-photo').map(function (el) { return { el: el, card: el.closest('.card'), vis: false, v: null }; });
    var tio = new IntersectionObserver(function (es) { es.forEach(function (e) { thumbs.forEach(function (t) { if (t.el === e.target) t.vis = e.isIntersecting; }); }); }, { rootMargin: '10% 0px' });
    thumbs.forEach(function (t) { tio.observe(t.el); });

    // ---------- Marquee speed follows scroll velocity ----------
    var anims = [];
    function findAnims() { anims = []; $$('#clients .marquee').forEach(function (m) { m.getAnimations().forEach(function (a) { if (a.animationName === 'marquee') anims.push(a); }); }); }
    var rate = 1;

    // ---------- CTA gradient ----------
    var cta = $('.cta'), ctaWashes = cta ? $$('.wash', cta) : [], ctaTop = 0, ctaH = 0;

    // ---------- Timecode ----------
    var tc = null, tcFill, tcLine, tcTime, tcTicks = [], sections = $$('main > section'), tickPos = [], footer = $('footer');
    function buildTimecode() {
      tc = document.createElement('div'); tc.className = 'scroll-tc'; tc.setAttribute('aria-hidden', 'true');
      tc.innerHTML = '<span class="tc-line"></span><span class="tc-chip"><span class="rec"></span><span>Scroll</span><span class="tc-track"><span class="tc-fill"></span></span><span class="tc-time">00:00:00</span></span>';
      document.body.appendChild(tc);
      tcLine = $('.tc-line', tc); tcFill = $('.tc-fill', tc); tcTime = $('.tc-time', tc);
      var track = $('.tc-track', tc);
      tcTicks = sections.map(function () { var t = document.createElement('i'); t.className = 'tc-tick'; track.appendChild(t); return t; });
      if (footer) new IntersectionObserver(function (es) { tc.classList.toggle('is-hidden', es[0].isIntersecting); }).observe(footer);
    }
    var tcOn = false;
    function toggleTimecode() {
      var want = wideMQ.matches; if (want && !tc) buildTimecode();
      tcOn = want && !!tc; if (tc) tc.style.display = tcOn ? '' : 'none';
      if (tcOn && !tcTicks[0].style.left) measure();
    }

    // ---------- Measurements (read once, not per frame) ----------
    var docMax = 1, vh = window.innerHeight, heroH = 800;
    function measure() {
      vh = window.innerHeight; sy = window.pageYOffset; if (hero) heroH = hero.offsetHeight;
      docMax = Math.max(1, document.documentElement.scrollHeight - vh);
      if (pin && wideMQ.matches) {
        var r = pin.getBoundingClientRect(); wrapTop = r.top + sy; wrapH = r.height; stageH = pinStage.offsetHeight; pinTopPx = vh * CONFIG.PIN_TOP_VH / 100;
      }
      if (cta) { var c = cta.getBoundingClientRect(); ctaTop = c.top + sy; ctaH = c.height; }
      tickPos = sections.map(function (s) { return clamp((s.getBoundingClientRect().top + sy) / docMax, 0, 1); });
      tcTicks.forEach(function (t, i) { t.style.left = (tickPos[i] * 100) + '%'; });
      findAnims();
    }

    // ---------- The frame loop ----------
    var ticking = false, lastY = sy, lastT = 0, vel = 0;
    function frame(ts) {
      ticking = false;
      var y = window.pageYOffset, dt = Math.max(1, ts - lastT), wide = wideMQ.matches;
      vel += ((Math.abs(y - lastY) / dt) - vel) * 0.35; lastY = y; lastT = ts;

      // reads
      var thumbRects = wide ? thumbs.map(function (t) { return t.vis ? t.card.getBoundingClientRect() : null; }) : [];

      // writes
      if (wide && hero) hero.style.setProperty('--hy', Math.min(y, heroH + 200).toFixed(1));
      if (wide && pin) scrub(clamp((y + pinTopPx - wrapTop) / Math.max(1, wrapH - stageH), 0, 1));
      thumbRects.forEach(function (r, i) {
        if (!r) return;
        var q = clamp(((r.top + r.height / 2) - vh / 2) / (vh / 2 + r.height / 2), -1, 1), v = (q * -CONFIG.THUMB_SHIFT).toFixed(2);
        if (thumbs[i].v !== v) { thumbs[i].v = v; thumbs[i].el.style.setProperty('--tp', v); }
      });
      if (wide && cta) {
        var mid = ctaTop + ctaH / 2 - y - vh / 2, near = 1 - clamp(Math.abs(mid) / vh, 0, 1), s = CONFIG.CTA_SCALE[0] + (CONFIG.CTA_SCALE[1] - CONFIG.CTA_SCALE[0]) * near;
        ctaWashes.forEach(function (w) { w.style.setProperty('--cs', s.toFixed(3)); });
      }
      if (tcOn) {
        var pr = clamp(y / docMax, 0, 1), sec = Math.round(pr * CONFIG.TC_TOTAL_SEC);
        tcLine.style.setProperty('--tp', pr.toFixed(4)); tcFill.style.setProperty('--tp', pr.toFixed(4));
        tcTime.textContent = '00:' + pad(Math.floor(sec / 60)) + ':' + pad(sec % 60);
        tcTicks.forEach(function (t, i) { t.classList.toggle('is-past', pr >= tickPos[i] - 0.001); });
      }
      // marquee: speed up with scroll velocity, ease back to 1
      var target = 1 + Math.min(vel * CONFIG.MARQUEE_GAIN, CONFIG.MARQUEE_MAX - 1);
      rate += (target - rate) * (target > rate ? 0.25 : CONFIG.MARQUEE_EASE);
      if (target < 1.005 && rate < 1.01) rate = 1;
      anims.forEach(function (a) { a.playbackRate = rate; });
      if (rate !== 1 || vel > 0.001) { vel *= 0.9; request(); }
    }
    function request() { if (!ticking) { ticking = true; requestAnimationFrame(frame); } }

    window.addEventListener('scroll', request, { passive: true });
    var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { measure(); request(); }, 120); });
    if (window.ResizeObserver) { var ro, rr; ro = new ResizeObserver(function () { clearTimeout(rr); rr = setTimeout(function () { measure(); request(); }, 150); }); ro.observe(document.body); }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { measure(); request(); });
    window.addEventListener('load', function () { measure(); request(); });
    wideMQ.addEventListener ? wideMQ.addEventListener('change', function () { applyMode(); toggleTimecode(); request(); }) : wideMQ.addListener(function () { applyMode(); toggleTimecode(); request(); });
    reduce.addEventListener ? reduce.addEventListener('change', function () { location.reload(); }) : null;

    applyMode(); toggleTimecode(); request();

    // The pin wrapper adds height; if the page opened on an anchor, re-aim once layout is final.
    if (location.hash && location.hash.length > 1) {
      window.addEventListener('load', function () { var t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) t.scrollIntoView(); });
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
