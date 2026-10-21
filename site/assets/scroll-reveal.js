// Subtle scroll reveal for index.html: elements fade up once as they enter the viewport.
// Runs in <head> so nothing is hidden after it has painted. Static when JS is off or reduced motion is on.
var REVEAL = {
  STAGGER_MS: 70,   // delay between siblings revealed together (60 to 90ms)
  THRESHOLD: 0.12,  // how much of an element must be visible before it reveals
  MARGIN: '0px 0px -6% 0px'
};

(function () {
  var root = document.documentElement;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) return;
  root.classList.add('js-reveal');

  function init() {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { threshold: REVEAL.THRESHOLD, rootMargin: REVEAL.MARGIN });
    // Reveal every match of a selector; delay(i, el) gives each its stagger in ms
    function group(sel, delay) {
      [].slice.call(document.querySelectorAll(sel)).forEach(function (el, i) {
        el.classList.add('rv');
        var d = delay ? delay(i, el) : 0;
        if (d) el.style.setProperty('--d', d + 'ms');
        io.observe(el);
      });
    }
    var step = function (i) { return i * REVEAL.STAGGER_MS; };

    group('.hero .eyebrow, .hero h1, .hero .lede, .hero .hero-ctas, .hero .hero-meta, .hero-media', step);
    group('.head > *', function (i, el) { return [].indexOf.call(el.parentNode.children, el) * REVEAL.STAGGER_MS; });
    group('#modules .modules > .card', function (i) { return i === 0 ? 0 : ((i - 1) % 3) * REVEAL.STAGGER_MS; });
    group('#platform .flow', null);
    group('#platform .steps > div', step);
    group('#clients .clients', null);
    group('#clients .client-sectors > *, #sectors .sectors > *', function (i) { return Math.min(i, 6) * 45; });
    group('#sectors .proof, #faq .faq-grid > *', function (i, el) { return [].indexOf.call(el.parentNode.children, el) * REVEAL.STAGGER_MS; });
    group('.cta .wrap > *', step);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
