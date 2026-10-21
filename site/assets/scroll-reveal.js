// Subtle scroll reveal for index.html: elements fade up once as they enter the viewport.
// Runs in <head> so nothing is hidden after it has painted. Static when JS is off or reduced motion is on.
// Wide fine-pointer screens also get a heading mask rise, an image settle and a drawn divider rule;
// narrow or touch screens get the plain fade-up only.
var REVEAL = {
  STAGGER_MS: 70,   // delay between siblings revealed together (60 to 90ms)
  THRESHOLD: 0.12,  // how much of an element must be visible before it reveals
  MARGIN: '0px 0px -6% 0px',
  RICH_QUERY: '(min-width: 901px) and (hover: hover) and (pointer: fine)'
};

(function () {
  var root = document.documentElement;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  root.classList.add('js-reveal');
  var rich = window.matchMedia(REVEAL.RICH_QUERY);
  function setRich() { root.classList.toggle('js-reveal-rich', rich.matches); }
  setRich();
  if (rich.addEventListener) rich.addEventListener('change', setRich);

  function init() {
    // One observer; class changes are batched into a single animation frame
    var pending = [], queued = false;
    function flush() { queued = false; pending.splice(0).forEach(function (el) { el.classList.add('is-in'); }); }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { pending.push(e.target); io.unobserve(e.target); } });
      if (pending.length && !queued) { queued = true; requestAnimationFrame(flush); }
    }, { threshold: REVEAL.THRESHOLD, rootMargin: REVEAL.MARGIN });
    // Reveal every match of a selector; delay(i, el) gives each its stagger in ms
    function group(sel, delay, cls) {
      [].slice.call(document.querySelectorAll(sel)).forEach(function (el, i) {
        el.classList.add(cls || 'rv');
        var d = delay ? delay(i, el) : 0;
        if (d) el.style.setProperty('--d', d + 'ms');
        io.observe(el);
      });
    }
    var step = function (i) { return i * REVEAL.STAGGER_MS; };
    var sib = function (i, el) { return [].indexOf.call(el.parentNode.children, el) * REVEAL.STAGGER_MS; };
    // Wrap a heading's contents so the inner line can rise through the heading's own box
    function mask(sel, delay) {
      [].slice.call(document.querySelectorAll(sel)).forEach(function (h) {
        var s = document.createElement('span');
        s.className = 'rv-in-line';
        while (h.firstChild) s.appendChild(h.firstChild);
        h.appendChild(s);
      });
      group(sel, delay, 'rv-mask');
    }

    group('.hero .eyebrow, .hero h1, .hero .lede, .hero .hero-ctas, .hero .hero-meta', step);
    group('.hero-media', step);
    group('.hero-media .feed', function () { return 140; }, 'rv-img');
    // Section headers: eyebrow, then the heading rising through its mask, then the lede
    group('.head .eyebrow', null);
    mask('.head h2, .cta h2', function () { return REVEAL.STAGGER_MS; });
    group('.head > .lede', function () { return REVEAL.STAGGER_MS * 2; });
    group('#modules .modules > .card', function (i) { return i === 0 ? 0 : ((i - 1) % 3) * REVEAL.STAGGER_MS; });
    group('.thumb-photo', null, 'rv-img');
    group('#platform .flow', null);
    group('#platform .steps > div', step);
    group('#clients .clients', null);
    group('#sectors .sectors > *', function (i) { return Math.min(i, 6) * 45; });
    group('#sectors .proof', null, 'rv-rule');
    group('#sectors .proof > *, #faq .faq-grid > *', sib);
    group('.cta .eyebrow, .cta .hero-ctas', step);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
