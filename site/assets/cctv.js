// Simulated CCTV feeds for the KenVision console. Each scene paints a soft, low-res frame
// (upscaled for that camera look), then crisp detections and an on-screen display on top.
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var COL = { person: '#73C4C5', vehicle: '#78AFCF', alert: '#FF7953', crowd: '#A98BF5', object: '#A98BF5', ok: '#73C4C5' };
  var BASE = 14 * 3600 + 32 * 60 + 9, T0 = performance.now();

  function rng(seed) { return function () { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; }; }
  function lerp(a, b, t) { return a + (b - a) * t; }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function stamp(sec) { var s = Math.floor(BASE + sec); return '2026-10-16  ' + pad(Math.floor(s / 3600) % 24) + ':' + pad(Math.floor(s / 60) % 60) + ':' + pad(s % 60); }
  function mk(w, h) { var c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
  function rrect(c, x, y, w, h, r) { c.beginPath(); c.moveTo(x + r, y); c.arcTo(x + w, y, x + w, y + h, r); c.arcTo(x + w, y + h, x, y + h, r); c.arcTo(x, y + h, x, y, r); c.arcTo(x, y, x + w, y, r); c.closePath(); }
  function glow(c, x, y, r, a) { var g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, 'rgba(255,250,235,' + a + ')'); g.addColorStop(1, 'rgba(255,250,235,0)'); c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2); }
  function speckle(c, w, h, y0, n, R, a) { for (var i = 0; i < n; i++) { c.fillStyle = (R() > .5 ? 'rgba(255,255,255,' : 'rgba(0,0,0,') + (a * R()) + ')'; c.fillRect(R() * w, y0 + R() * (h - y0), 1 + R() * 1.5, 1 + R() * 1.5); } }

  // A person standing on (x, y) with height H. o: vest colour, hat, phase (walk), back (facing away)
  function person(c, x, y, H, o) {
    var st = Math.sin(o.phase || 0) * H * 0.07, sw = o.walk === false ? 0 : st;
    c.fillStyle = 'rgba(0,0,0,.32)'; c.beginPath(); c.ellipse(x + H * .1, y, H * .2, H * .05, 0, 0, 7); c.fill();
    c.fillStyle = o.legs || '#2a2d33';
    c.fillRect(x - H * .1 + sw, y - H * .48, H * .085, H * .48);
    c.fillRect(x + H * .02 - sw, y - H * .48, H * .085, H * .48);
    c.fillStyle = '#18191b'; c.fillRect(x - H * .11 + sw, y - H * .03, H * .11, H * .03); c.fillRect(x + H * .01 - sw, y - H * .03, H * .11, H * .03);
    c.fillStyle = o.arm || o.vest; c.fillRect(x - H * .19, y - H * .8 - sw * .3, H * .07, H * .34); c.fillRect(x + H * .12, y - H * .8 + sw * .3, H * .07, H * .34);
    c.fillStyle = o.vest; rrect(c, x - H * .14, y - H * .84, H * .28, H * .4, H * .05); c.fill();
    if (o.stripe) { c.fillStyle = 'rgba(235,235,220,.85)'; c.fillRect(x - H * .14, y - H * .62, H * .28, H * .035); c.fillRect(x - H * .14, y - H * .54, H * .28, H * .03); }
    c.fillStyle = o.back ? '#2b2420' : '#a4836c'; c.beginPath(); c.arc(x, y - H * .9, H * .075, 0, 7); c.fill();
    if (o.hat) { c.fillStyle = o.hat; c.beginPath(); c.ellipse(x, y - H * .935, H * .09, H * .055, 0, Math.PI, 0); c.fill(); c.fillRect(x - H * .1, y - H * .94, H * .2, H * .018); }
    else if (!o.back) { c.fillStyle = '#2b2420'; c.beginPath(); c.arc(x, y - H * .92, H * .072, Math.PI * 1.05, Math.PI * 1.95); c.fill(); }
    return [x - H * .2, y - H * 1.0, H * .4, H * 1.02];
  }
  function cuboid(c, x, y, w, h, d, col, top, side) {
    c.fillStyle = side; c.beginPath(); c.moveTo(x + w, y); c.lineTo(x + w + d, y - d * .6); c.lineTo(x + w + d, y - h - d * .6); c.lineTo(x + w, y - h); c.fill();
    c.fillStyle = top; c.beginPath(); c.moveTo(x, y - h); c.lineTo(x + d, y - h - d * .6); c.lineTo(x + w + d, y - h - d * .6); c.lineTo(x + w, y - h); c.fill();
    c.fillStyle = col; c.fillRect(x, y - h, w, h);
  }
  function car(c, x, y, w, h, col) { // seen from a high angle, nose pointing down
    c.fillStyle = 'rgba(0,0,0,.4)'; rrect(c, x - w * .02, y + h * .06, w * 1.04, h, w * .2); c.fill();
    c.fillStyle = col; rrect(c, x, y, w, h, w * .22); c.fill();
    c.fillStyle = 'rgba(255,255,255,.12)'; rrect(c, x + w * .12, y + h * .32, w * .76, h * .34, w * .12); c.fill();
    c.fillStyle = 'rgba(10,12,14,.75)'; rrect(c, x + w * .12, y + h * .18, w * .76, h * .16, w * .06); c.fill(); rrect(c, x + w * .14, y + h * .68, w * .72, h * .12, w * .05); c.fill();
    return [x - w * .04, y - h * .04, w * 1.08, h * 1.1];
  }

  var SCENES = {
    dock: {
      osd: 'CAM-04  LOADING DOCK B',
      bg: function (c, w, h) {
        var R = rng(7), u = w / 480, hz = h * .46, g;
        g = c.createLinearGradient(0, 0, 0, hz); g.addColorStop(0, '#2a2d2f'); g.addColorStop(1, '#3d4042'); c.fillStyle = g; c.fillRect(0, 0, w, hz);
        c.fillStyle = 'rgba(255,255,255,.05)'; for (var i = 0; i < 12; i++) c.fillRect(i * w / 12, 0, 1, hz);
        for (i = 0; i < 3; i++) {
          var dx = w * (.1 + i * .29), dw = w * .21, dt = h * .1;
          c.fillStyle = '#1b1c1d'; c.fillRect(dx - 3 * u, dt - 3 * u, dw + 6 * u, hz - dt + 3 * u);
          if (i === 1) {
            c.fillStyle = '#0c0d0e'; c.fillRect(dx, dt, dw, hz - dt);
            c.fillStyle = '#26282a'; c.fillRect(dx + dw * .08, dt + 4 * u, dw * .84, hz - dt - 8 * u);
            c.fillStyle = '#121314'; c.fillRect(dx + dw * .12, dt + 8 * u, dw * .76, hz - dt - 12 * u);
            cuboid(c, dx + dw * .18, hz - 6 * u, dw * .22, 22 * u, 6 * u, '#5d5143', '#6e604f', '#463d33');
            cuboid(c, dx + dw * .5, hz - 6 * u, dw * .26, 30 * u, 6 * u, '#655847', '#776855', '#4c4236');
          } else {
            c.fillStyle = '#6a6e70'; c.fillRect(dx, dt, dw, hz - dt);
            c.fillStyle = 'rgba(0,0,0,.18)'; for (var y = dt; y < hz; y += 4 * u) c.fillRect(dx, y, dw, 1.2 * u);
            g = c.createLinearGradient(dx, 0, dx + dw, 0); g.addColorStop(0, 'rgba(0,0,0,.15)'); g.addColorStop(.5, 'rgba(255,255,255,.06)'); g.addColorStop(1, 'rgba(0,0,0,.2)'); c.fillStyle = g; c.fillRect(dx, dt, dw, hz - dt);
          }
          c.fillStyle = '#9b8f45'; c.fillRect(dx - 9 * u, hz - 30 * u, 5 * u, 30 * u); c.fillRect(dx + dw + 4 * u, hz - 30 * u, 5 * u, 30 * u);
          c.fillStyle = '#111'; c.fillRect(dx, hz - 6 * u, dw, 6 * u);
          c.fillStyle = '#c9c4b0'; c.fillRect(dx + dw * .4, dt - 14 * u, dw * .2, 8 * u); c.fillStyle = '#222'; c.font = (6 * u) + 'px sans-serif'; c.fillText('D' + (i + 3), dx + dw * .45, dt - 8 * u);
        }
        g = c.createLinearGradient(0, hz, 0, h); g.addColorStop(0, '#4f5151'); g.addColorStop(1, '#6f716f'); c.fillStyle = g; c.fillRect(0, hz, w, h - hz);
        speckle(c, w, h, hz, 2600, R, .12);
        for (i = 0; i < 9; i++) { c.fillStyle = 'rgba(0,0,0,' + (.04 + R() * .05) + ')'; c.beginPath(); c.ellipse(R() * w, hz + R() * (h - hz), 20 * u + R() * 40 * u, 6 * u + R() * 10 * u, 0, 0, 7); c.fill(); }
        c.fillStyle = '#d8d6cf'; c.fillRect(0, hz + 6 * u, w, 2 * u);
        c.strokeStyle = 'rgba(176,160,74,.9)'; c.lineWidth = 3 * u;
        c.beginPath(); c.moveTo(w * .02, h); c.lineTo(w * .3, hz + 10 * u); c.stroke();
        c.beginPath(); c.moveTo(w * .5, h); c.lineTo(w * .56, hz + 10 * u); c.stroke();
        c.save(); c.beginPath(); c.moveTo(w * .62, h * .55); c.lineTo(w * .88, h * .55); c.lineTo(w * .99, h * .86); c.lineTo(w * .63, h * .86); c.closePath();
        c.fillStyle = 'rgba(176,160,74,.08)'; c.fill(); c.clip(); c.strokeStyle = 'rgba(176,160,74,.5)'; c.lineWidth = 4 * u;
        for (var k = -h; k < w; k += 14 * u) { c.beginPath(); c.moveTo(k, h); c.lineTo(k + h, 0); c.stroke(); } c.restore();
        c.strokeStyle = 'rgba(176,160,74,.9)'; c.lineWidth = 2 * u; c.beginPath(); c.moveTo(w * .62, h * .55); c.lineTo(w * .88, h * .55); c.lineTo(w * .99, h * .86); c.lineTo(w * .63, h * .86); c.closePath(); c.stroke();
        cuboid(c, w * .03, h * .7, w * .1, 26 * u, 10 * u, '#7b6a54', '#907e65', '#5d5141');
        cuboid(c, w * .03, h * .7 - 26 * u, w * .1, 18 * u, 10 * u, '#83725a', '#99876c', '#625645');
        cuboid(c, w * .16, h * .64, w * .08, 20 * u, 8 * u, '#766652', '#8b7a62', '#5a4e3f');
        c.fillStyle = '#4a3f33'; c.fillRect(w * .03, h * .7, w * .1, 4 * u); c.fillRect(w * .16, h * .64, w * .08, 3 * u);
        for (i = 0; i < 3; i++) { c.fillStyle = '#f2efe6'; c.fillRect(w * (.18 + i * .3), 2 * u, w * .1, 3 * u); }
        c.globalCompositeOperation = 'lighter'; for (i = 0; i < 3; i++) glow(c, w * (.23 + i * .3), 6 * u, w * .16, .22); c.globalCompositeOperation = 'source-over';
      },
      frame: function (c, w, h, t) {
        var u = w / 480, d = [], items = [];
        var fx = w * (.3 + .1 * Math.sin(t * .22)), fy = h * .66, dir = Math.cos(t * .22) > 0 ? 1 : -1;
        items.push({ y: fy, f: function () {
          var L = 78 * u, H = 44 * u, x = fx - L / 2, y = fy;
          c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.ellipse(fx, y, L * .62, 8 * u, 0, 0, 7); c.fill();
          c.fillStyle = '#7d6237'; rrect(c, x, y - H, L * .72, H * .78, 4 * u); c.fill();
          c.fillStyle = '#5c4728'; c.fillRect(x, y - H * .5, L * .72, H * .3);
          c.fillStyle = '#1d1e20'; c.fillRect(x + L * .08, y - H * 1.45, 3 * u, H * .7); c.fillRect(x + L * .5, y - H * 1.45, 3 * u, H * .7); c.fillRect(x + L * .08, y - H * 1.47, L * .45, 3 * u);
          var mx = dir > 0 ? x + L * .72 : x - L * .06;
          c.fillStyle = '#262729'; c.fillRect(mx, y - H * 1.6, L * .06, H * 1.55);
          c.fillStyle = '#3a3b3d'; c.fillRect(dir > 0 ? mx : mx - L * .26, y - 5 * u, L * .32, 3 * u);
          c.fillStyle = '#a4836c'; c.beginPath(); c.arc(x + L * .32, y - H * 1.02, 6 * u, 0, 7); c.fill();
          c.fillStyle = '#e4e0d2'; c.beginPath(); c.ellipse(x + L * .32, y - H * 1.07, 7 * u, 4 * u, 0, Math.PI, 0); c.fill();
          c.fillStyle = '#121212'; c.beginPath(); c.arc(x + L * .14, y - 4 * u, 8 * u, 0, 7); c.arc(x + L * .58, y - 4 * u, 8 * u, 0, 7); c.fill();
          d.push({ b: [x - L * .32, y - H * 1.7, L * 1.4, H * 1.75], l: 'Forklift', p: 91, k: 'vehicle' });
        } });
        var cyc = (t % 16) / 16, ax = lerp(w * .08, w * .56, cyc), ay = h * .9;
        items.push({ y: ay, f: function () { d.push({ b: person(c, ax, ay, 92 * u, { vest: '#a8b34e', stripe: 1, hat: '#e8e4d6', phase: t * 7 }), l: 'Person', p: 97, k: 'person' }); } });
        var bx = w * .76 + Math.sin(t * .6) * 4 * u, by = h * .76;
        items.push({ y: by, f: function () { d.push({ b: person(c, bx, by, 80 * u, { vest: '#b0b84f', stripe: 1, hat: null, phase: 0, walk: false }), l: 'No hard hat', p: 94, k: 'alert' }); } });
        items.sort(function (a, b) { return a.y - b.y; }).forEach(function (i) { i.f(); });
        return d;
      }
    },
    aisle: {
      osd: 'CAM-11  AISLE 7',
      bg: function (c, w, h) {
        var R = rng(11), vx = w * .5, vy = h * .34, f = w * .5;
        function P(x, y, z) { return [vx + x * f / z, vy + y * f / z]; }
        c.fillStyle = '#1e2022'; c.fillRect(0, 0, w, h);
        var a = P(-1.6, 2.8, 1.1), b = P(1.6, 2.8, 1.1), cc = P(1.6, 2.8, 40), dd = P(-1.6, 2.8, 40);
        var g = c.createLinearGradient(0, h, 0, vy); g.addColorStop(0, '#77786f'); g.addColorStop(1, '#3b3c39'); c.fillStyle = g;
        c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.lineTo(cc[0], cc[1]); c.lineTo(dd[0], dd[1]); c.fill();
        speckle(c, w, h, vy, 900, R, .1);
        c.strokeStyle = 'rgba(190,175,90,.55)'; c.lineWidth = 1.5;
        [-1.45, 1.45].forEach(function (x) { var p = P(x, 2.8, 1.1), q = P(x, 2.8, 40); c.beginPath(); c.moveTo(p[0], p[1]); c.lineTo(q[0], q[1]); c.stroke(); });
        var bays = []; for (var z = 40; z > 1.2; z -= 2.6) bays.push(z);
        [-1, 1].forEach(function (s) {
          bays.forEach(function (z) {
            var z2 = Math.max(z - 2.6, 1.15), x0 = 1.6 * s, x1 = 2.7 * s;
            [2.8, 1.55, .3, -.95].forEach(function (lv, li) {
              if (li === 0) return;
              var top = lv - 1.0;
              for (var n = 0; n < 3; n++) {
                if (R() < .22) continue;
                var za = lerp(z, z2, n / 3 + .03), zb = lerp(z, z2, (n + 1) / 3 - .03), ht = .55 + R() * .45;
                var p1 = P(x0, lv, za), p2 = P(x0, lv, zb), p3 = P(x0, lv - ht, zb), p4 = P(x0, lv - ht, za);
                var tone = 95 + R() * 40; c.fillStyle = 'rgb(' + (tone + 10 | 0) + ',' + (tone - 8 | 0) + ',' + (tone - 32 | 0) + ')';
                c.beginPath(); c.moveTo(p1[0], p1[1]); c.lineTo(p2[0], p2[1]); c.lineTo(p3[0], p3[1]); c.lineTo(p4[0], p4[1]); c.fill();
                c.fillStyle = 'rgba(0,0,0,' + (Math.min(.6, z / 40)) + ')'; c.fill();
              }
              var b1 = P(x0, lv, z), b2 = P(x0, lv, z2), b3 = P(x0, lv - .12, z2), b4 = P(x0, lv - .12, z);
              c.fillStyle = '#93582c'; c.beginPath(); c.moveTo(b1[0], b1[1]); c.lineTo(b2[0], b2[1]); c.lineTo(b3[0], b3[1]); c.lineTo(b4[0], b4[1]); c.fill();
            });
            var u1 = P(x0, 2.8, z), u2 = P(x0, -1.9, z), uw = Math.max(1, .08 * f / z);
            c.fillStyle = '#3d5672'; c.fillRect(u1[0] - uw / 2, u2[1], uw, u1[1] - u2[1]);
          });
        });
        for (z = 36; z > 2; z -= 5) { var L = P(0, -2.3, z), lw = 1.2 * f / z; c.fillStyle = '#f4f1e8'; c.fillRect(L[0] - lw / 2, L[1], lw, Math.max(1, .06 * f / z)); c.globalCompositeOperation = 'lighter'; glow(c, L[0], L[1], lw * 1.2, .16); c.globalCompositeOperation = 'source-over'; }
        g = c.createRadialGradient(vx, vy, 0, vx, vy, w * .2); g.addColorStop(0, 'rgba(0,0,0,.5)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.fillRect(0, 0, w, h);
      },
      frame: function (c, w, h, t) {
        var vx = w * .5, vy = h * .34, f = w * .5, d = [];
        function P(x, y, z) { return [vx + x * f / z, vy + y * f / z]; }
        var z1 = 4.6; var p1 = P(1.3, 2.8, z1);
        d.push({ b: person(c, p1[0], p1[1], 1.75 * f / z1, { vest: '#4e5560', hat: null, phase: 0, walk: false, back: true }), l: 'Person', p: 88, k: 'person' });
        var z = 20 - (t * 1.1) % 16, p = P(-.4, 2.8, z);
        d.push({ b: person(c, p[0], p[1], 1.75 * f / z, { vest: '#aab54f', stripe: 1, hat: '#e8e4d6', phase: t * 6 }), l: 'Person', p: 95, k: 'person' });
        return d;
      }
    },
    lot: {
      osd: 'CAM-02  NORTH PARKING', ir: true,
      bg: function (c, w, h) {
        var R = rng(5), u = w / 480;
        c.fillStyle = '#2f3031'; c.fillRect(0, 0, w, h);
        c.fillStyle = '#1f2421'; c.fillRect(0, 0, w, h * .12);
        for (var i = 0; i < 14; i++) { c.fillStyle = 'rgba(40,48,42,' + (.6 + R() * .4) + ')'; c.beginPath(); c.arc(R() * w, h * .05 + R() * h * .06, 10 * u + R() * 16 * u, 0, 7); c.fill(); }
        c.fillStyle = '#5a5b58'; c.fillRect(0, h * .12, w, 3 * u);
        speckle(c, w, h, h * .12, 3000, R, .14);
        c.strokeStyle = 'rgba(210,210,200,.7)'; c.lineWidth = 2 * u;
        for (var r = 0; r < 2; r++) { var y0 = h * (.18 + r * .34), y1 = y0 + h * .2; for (var x = -w * .05; x < w * 1.05; x += w * .1) { c.beginPath(); c.moveTo(x + (x - w / 2) * .04, y0); c.lineTo(x + (x - w / 2) * .1, y1); c.stroke(); } c.beginPath(); c.moveTo(0, r ? y0 : y1); c.lineTo(w, r ? y0 : y1); c.stroke(); }
        c.fillStyle = 'rgba(220,220,210,.55)'; c.fillRect(0, h * .9, w, 4 * u);
        c.save(); c.translate(w * .2, h * .84); c.transform(1, 0, -.35, .6, 0, 0); c.font = '700 ' + (22 * u) + 'px sans-serif'; c.fillStyle = 'rgba(225,225,215,.45)'; c.fillText('FIRE LANE', 0, 0); c.fillText('FIRE LANE', w * .55, 0); c.restore();
        var cols = ['#5b5e61', '#2a2b2d', '#8d8f8f', '#44474a', '#6f6c68', '#1f2022', '#9b9d9c'];
        [[.03, .19], [.13, .2], [.33, .19], [.53, .2], [.73, .19], [.83, .2], [.08, .54], [.28, .53], [.48, .54], [.88, .53]].forEach(function (p, i) { car(c, w * p[0], h * p[1], w * .07, h * .17, cols[i % cols.length]); });
        c.globalCompositeOperation = 'lighter'; glow(c, w * .25, h * .45, w * .3, .2); glow(c, w * .8, h * .5, w * .28, .18); c.globalCompositeOperation = 'source-over';
      },
      frame: function (c, w, h, t) {
        var d = [], u = w / 480;
        d.push({ b: car(c, w * .58, h * .76, w * .2, h * .12, '#7b7d7d'), l: 'Vehicle · fire lane', p: 96, k: 'alert' });
        if (Math.floor(t * 1.5) % 2) { c.fillStyle = 'rgba(255,255,240,.85)'; c.fillRect(w * .58, h * .79, 4 * u, 3 * u); c.fillRect(w * .58, h * .84, 4 * u, 3 * u); }
        var cy = (t % 18) / 18, px = lerp(w * .95, w * .2, cy), py = lerp(h * .48, h * .52, cy);
        d.push({ b: person(c, px, py, 42 * u, { vest: '#3c3f44', arm: '#3c3f44', hat: null, phase: t * 7 }), l: 'Person', p: 92, k: 'person' });
        return d;
      }
    },
    lobby: {
      osd: 'CAM-07  MAIN ENTRANCE',
      bg: function (c, w, h) {
        var R = rng(3), u = w / 480, hz = h * .5, g;
        c.fillStyle = '#6c6862'; c.fillRect(0, 0, w, hz);
        c.fillStyle = '#5e5a55'; c.fillRect(0, hz - 10 * u, w, 10 * u);
        var dx = w * .27, dw = w * .46, dt = h * .1;
        c.fillStyle = '#1a1b1c'; c.fillRect(dx - 5 * u, dt - 5 * u, dw + 10 * u, hz - dt + 5 * u);
        g = c.createLinearGradient(0, dt, 0, hz); g.addColorStop(0, '#f4f6f5'); g.addColorStop(1, '#d9dedb'); c.fillStyle = g; c.fillRect(dx, dt, dw, hz - dt);
        for (var i = 0; i < 6; i++) { c.fillStyle = 'rgba(120,135,125,' + (.15 + R() * .2) + ')'; c.beginPath(); c.arc(dx + R() * dw, dt + hz * .35 + R() * 20 * u, 12 * u + R() * 18 * u, 0, 7); c.fill(); }
        c.fillStyle = '#1a1b1c'; for (i = 1; i < 4; i++) c.fillRect(dx + dw * i / 4 - 2 * u, dt, 4 * u, hz - dt);
        c.fillStyle = '#2a2b2c'; c.fillRect(dx + dw * .2, dt + (hz - dt) * .5, 2 * u, 18 * u); c.fillRect(dx + dw * .3, dt + (hz - dt) * .5, 2 * u, 18 * u);
        c.fillStyle = '#232323'; c.fillRect(w * .4, dt - 22 * u, w * .2, 12 * u); c.fillStyle = '#d6d6d0'; c.font = '600 ' + (7 * u) + 'px sans-serif'; c.fillText('ENTRANCE', w * .455, dt - 13 * u);
        g = c.createLinearGradient(0, hz, 0, h); g.addColorStop(0, '#77736c'); g.addColorStop(1, '#9a958c'); c.fillStyle = g; c.fillRect(0, hz, w, h - hz);
        c.strokeStyle = 'rgba(40,38,35,.25)'; c.lineWidth = 1;
        for (i = 0; i <= 12; i++) { c.beginPath(); c.moveTo(w / 2 + (i - 6) * w * .03, hz); c.lineTo(w / 2 + (i - 6) * w * .16, h); c.stroke(); }
        for (var y = hz, s = 6 * u; y < h; y += s, s *= 1.25) { c.beginPath(); c.moveTo(0, y); c.lineTo(w, y); c.stroke(); }
        g = c.createLinearGradient(0, hz, 0, h); g.addColorStop(0, 'rgba(255,255,255,.35)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g;
        c.beginPath(); c.moveTo(dx, hz); c.lineTo(dx + dw, hz); c.lineTo(dx + dw * 1.25, h); c.lineTo(dx - dw * .25, h); c.fill();
        speckle(c, w, h, hz, 900, R, .08);
        [[.2, .74], [.62, .74]].forEach(function (p) { cuboid(c, w * p[0], h * p[1], w * .16, 26 * u, 8 * u, '#3a3b3d', '#55575a', '#2b2c2e'); c.fillStyle = 'rgba(200,215,220,.35)'; c.fillRect(w * (p[0] + .16), h * p[1] - 30 * u, 3 * u, 22 * u); });
      },
      frame: function (c, w, h, t) {
        var d = [], u = w / 480, cyc = (t % 10) / 10;
        function walker(off, x0, x1, o, lab, k, pct) {
          var q = (cyc + off + 1) % 1, y = lerp(h * .52, h * 1.02, q), x = lerp(w * x0, w * x1, q), H = lerp(40, 120, q) * u;
          if (q < .97) d.push({ b: person(c, x, y, H, o), l: lab, p: pct, k: k });
        }
        walker(-.2, .36, .3, { vest: '#5a6270', arm: '#5a6270', hat: null, phase: t * 7 }, 'Tailgating', 'alert', 89);
        walker(0, .56, .66, { vest: '#2f3338', arm: '#2f3338', hat: null, phase: t * 7 + 1 }, 'Person', 'person', 98);
        return d;
      }
    },
    plaza: {
      osd: 'CAM-21  CENTRAL PLAZA',
      bg: function (c, w, h) {
        var R = rng(21), u = w / 480, g;
        c.fillStyle = '#3e403f'; c.fillRect(0, 0, w, h * .16);
        for (var i = 0; i < 8; i++) { c.fillStyle = 'rgba(25,26,27,.8)'; c.fillRect(i * w / 8 + 6 * u, h * .03, w / 8 - 12 * u, h * .09); }
        g = c.createLinearGradient(0, h * .16, 0, h); g.addColorStop(0, '#8c8b85'); g.addColorStop(1, '#a9a79f'); c.fillStyle = g; c.fillRect(0, h * .16, w, h);
        c.strokeStyle = 'rgba(60,58,54,.25)'; c.lineWidth = 1;
        for (i = -10; i <= 20; i++) { c.beginPath(); c.moveTo(w / 2 + i * w * .05, h * .16); c.lineTo(w / 2 + i * w * .09, h); c.stroke(); }
        for (var y = h * .16, s = 8 * u; y < h; y += s, s *= 1.12) { c.beginPath(); c.moveTo(0, y); c.lineTo(w, y); c.stroke(); }
        speckle(c, w, h, h * .16, 2200, R, .1);
        c.fillStyle = '#6d6c67'; c.beginPath(); c.ellipse(w * .3, h * .55, w * .12, h * .1, 0, 0, 7); c.fill();
        c.fillStyle = '#4e5a5c'; c.beginPath(); c.ellipse(w * .3, h * .55, w * .1, h * .08, 0, 0, 7); c.fill();
        c.fillStyle = 'rgba(255,255,255,.18)'; c.beginPath(); c.ellipse(w * .29, h * .53, w * .05, h * .03, 0, 0, 7); c.fill();
        [[.08, .32], [.88, .3], [.1, .85], [.9, .86]].forEach(function (p) { c.fillStyle = 'rgba(0,0,0,.3)'; c.beginPath(); c.ellipse(w * p[0] + 6 * u, h * p[1] + 6 * u, 22 * u, 12 * u, 0, 0, 7); c.fill(); c.fillStyle = '#4a5546'; c.beginPath(); c.ellipse(w * p[0], h * p[1], 22 * u, 13 * u, 0, 0, 7); c.fill(); c.fillStyle = '#5c6a55'; c.beginPath(); c.arc(w * p[0] - 4 * u, h * p[1] - 4 * u, 10 * u, 0, 7); c.fill(); });
      },
      init: function (w, h) {
        var R = rng(99), P = [];
        for (var i = 0; i < 46; i++) {
          var cl = i < 26;
          P.push({ x: cl ? w * (.56 + R() * .3) : w * (.08 + R() * .84), y: cl ? h * (.4 + R() * .32) : h * (.25 + R() * .7), a: R() * 7, sp: .2 + R() * .6, v: ['#3a3f47', '#6b4b45', '#2c2e31', '#7a7f86', '#4d5a6b', '#8a7a5c'][i % 6], cl: cl });
        }
        return P;
      },
      frame: function (c, w, h, t, st) {
        var u = w / 480, d = [];
        st.P.forEach(function (p) {
          var dx = Math.cos(p.a + t * .1) * p.sp * .15, dy = Math.sin(p.a + t * .13) * p.sp * .1;
          p.x += dx * u; p.y += dy * u;
          if (p.cl) { p.x = Math.min(w * .88, Math.max(w * .54, p.x)); p.y = Math.min(h * .74, Math.max(h * .38, p.y)); }
          else { p.x = Math.min(w * .95, Math.max(w * .05, p.x)); p.y = Math.min(h * .97, Math.max(h * .22, p.y)); }
        });
        st.P.slice().sort(function (a, b) { return a.y - b.y; }).forEach(function (p) {
          var H = lerp(20, 44, (p.y - h * .2) / (h * .8)) * u;
          person(c, p.x, p.y, H, { vest: p.v, arm: p.v, hat: null, phase: t * 4 * p.sp + p.a, walk: true });
        });
        var n = st.P.filter(function (p) { return p.x > w * .54 && p.x < w * .88 && p.y > h * .38 && p.y < h * .74; }).length;
        st.count = n;
        d.push({ zone: [.52, .3, .38, .48], l: 'Zone A', k: 'crowd' });
        st.P.forEach(function (p) { d.push({ dot: [p.x / w, (p.y - lerp(20, 44, (p.y - h * .2) / (h * .8)) * u * .9) / h] }); });
        return d;
      },
      heat: true
    }
  };


  // Doorbell camera on a front porch (KenHome)
  SCENES.porch = {
    osd: 'FRONT DOOR',
    bg: function (c, w, h) {
      var R = rng(31), u = w / 480, g;
      g = c.createLinearGradient(0, 0, 0, h * .2); g.addColorStop(0, '#9fb0b8'); g.addColorStop(1, '#c4cdd0'); c.fillStyle = g; c.fillRect(0, 0, w, h * .2);
      [[.05, .1, .2], [.3, .08, .22], [.6, .11, .18], [.82, .09, .2]].forEach(function (b) { c.fillStyle = '#7d756c'; c.fillRect(w * b[0], h * b[1], w * b[2], h * .1); c.fillStyle = '#5a4e46'; c.beginPath(); c.moveTo(w * b[0] - 4 * u, h * b[1]); c.lineTo(w * (b[0] + b[2] / 2), h * b[1] - 14 * u); c.lineTo(w * (b[0] + b[2]) + 4 * u, h * b[1]); c.fill(); c.fillStyle = '#3c3a38'; c.fillRect(w * (b[0] + .03), h * (b[1] + .03), w * .03, h * .04); });
      c.fillStyle = '#55595a'; c.fillRect(0, h * .2, w, h * .07);
      g = c.createLinearGradient(0, h * .27, 0, h * .62); g.addColorStop(0, '#5a6a4c'); g.addColorStop(1, '#6f8259'); c.fillStyle = g; c.fillRect(0, h * .27, w, h * .35);
      speckle(c, w, h * .62, h * .27, 1600, R, .14);
      c.fillStyle = '#9a978f'; c.beginPath(); c.moveTo(w * .47, h * .27); c.lineTo(w * .53, h * .27); c.lineTo(w * .72, h * .62); c.lineTo(w * .36, h * .62); c.fill();
      c.strokeStyle = 'rgba(60,58,54,.3)'; for (var y = h * .3, st = 6 * u; y < h * .62; y += st, st *= 1.15) { c.beginPath(); c.moveTo(0, y); c.lineTo(w, y); c.stroke(); }
      g = c.createLinearGradient(0, h * .62, 0, h * .77); g.addColorStop(0, '#46553d'); g.addColorStop(1, '#3a4733'); c.fillStyle = g; c.fillRect(0, h * .62, w, h * .15);
      for (var j = 0; j < 22; j++) { c.fillStyle = 'rgba(30,40,26,.7)'; c.beginPath(); c.arc(R() * w, h * (.64 + R() * .1), 6 * u + R() * 10 * u, 0, 7); c.fill(); }
      for (var i = 0; i < 3; i++) { c.fillStyle = i % 2 ? '#8b877e' : '#a29e95'; c.fillRect(w * (.3 - i * .03), h * (.62 + i * .05), w * (.44 + i * .06), h * .05); c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(w * (.3 - i * .03), h * (.66 + i * .05), w * (.44 + i * .06), h * .01); }
      g = c.createLinearGradient(0, h * .77, 0, h); g.addColorStop(0, '#6e5a46'); g.addColorStop(1, '#816a53'); c.fillStyle = g; c.fillRect(0, h * .77, w, h * .23);
      c.strokeStyle = 'rgba(30,22,16,.35)'; for (i = 0; i < 9; i++) { c.beginPath(); c.moveTo(0, h * (.78 + i * .028)); c.lineTo(w, h * (.78 + i * .028)); c.stroke(); }
      c.fillStyle = '#e9e6dc'; c.fillRect(0, h * .3, w * .06, h * .5); c.fillRect(w * .94, h * .3, w * .06, h * .5);
      c.fillStyle = '#3d4a37'; c.beginPath(); c.arc(w * .14, h * .55, 26 * u, 0, 7); c.arc(w * .86, h * .55, 24 * u, 0, 7); c.fill();
      c.fillStyle = '#4e3b2d'; rrect(c, w * .38, h * .9, w * .24, h * .07, 4 * u); c.fill();
    },
    frame: function (c, w, h, t) {
      var u = w / 480, d = [], cyc = (t % 14) / 14, q = Math.min(1, cyc / .7);
      var x = lerp(w * .5, w * .52, q), y = lerp(h * .3, h * .76, q), H = lerp(28, 150, q * q) * u;
      d.push({ b: cuboid(c, w * .63, h * .76, w * .07, 20 * u, 8 * u, '#8b7457', '#a08867', '#6c5a44') || [w * .63, h * .76 - 30 * u, w * .1, 32 * u], l: 'Package', p: 91, k: 'object' });
      d.push({ b: person(c, x, y, H, { vest: '#3f4a5c', arm: '#3f4a5c', hat: null, phase: q < 1 ? t * 6 : 0, walk: q < 1 }), l: 'Person at door', p: 95, k: 'alert' });
      return d;
    }
  };

  // Dusk thermal view across a field (KenAgri)
  SCENES.field = {
    osd: 'FIELD 3  NORTH FENCE', ir: true,
    bg: function (c, w, h) {
      var R = rng(41), u = w / 480, hz = h * .32, g;
      g = c.createLinearGradient(0, 0, 0, hz); g.addColorStop(0, '#2b2f30'); g.addColorStop(1, '#55595a'); c.fillStyle = g; c.fillRect(0, 0, w, hz);
      for (var i = 0; i < 40; i++) { c.fillStyle = 'rgba(25,28,27,.9)'; c.beginPath(); c.arc(R() * w, hz - 4 * u - R() * 10 * u, 8 * u + R() * 14 * u, 0, 7); c.fill(); }
      g = c.createLinearGradient(0, hz, 0, h); g.addColorStop(0, '#3c4038'); g.addColorStop(1, '#4d5246'); c.fillStyle = g; c.fillRect(0, hz, w, h - hz);
      for (i = -14; i <= 14; i++) { c.strokeStyle = 'rgba(120,130,110,.55)'; c.lineWidth = 3 * u; c.beginPath(); c.moveTo(w * .5 + i * w * .012, hz); c.lineTo(w * .5 + i * w * .11, h); c.stroke(); c.strokeStyle = 'rgba(20,22,18,.6)'; c.lineWidth = 2 * u; c.beginPath(); c.moveTo(w * .5 + (i + .5) * w * .012, hz); c.lineTo(w * .5 + (i + .5) * w * .11, h); c.stroke(); }
      speckle(c, w, h, hz, 2400, R, .16);
      c.fillStyle = 'rgba(150,145,95,.25)'; c.beginPath(); c.moveTo(w * .18, h * .55); c.lineTo(w * .36, h * .55); c.lineTo(w * .4, h * .72); c.lineTo(w * .14, h * .72); c.fill();
      c.strokeStyle = '#2a2b28'; c.lineWidth = 1.2 * u;
      for (i = 0; i < 9; i++) { var fx = w * (.62 + i * .05), fy = hz + i * h * .07, fh = 18 * u + i * 5 * u; c.fillStyle = '#2a2b28'; c.fillRect(fx, fy - fh, 2 * u + i * .4 * u, fh); }
      [.55, .75].forEach(function (k) { c.beginPath(); c.moveTo(w * .62, hz - 18 * u * k); c.lineTo(w * 1.02, hz + h * .6 - 58 * u * k); c.stroke(); });
    },
    frame: function (c, w, h, t) {
      var u = w / 480, d = [], cyc = (t % 20) / 20, x = lerp(w * .9, w * .58, cyc), y = lerp(h * .74, h * .5, cyc), s = lerp(1.3, .8, cyc) * u, ph = Math.sin(t * 6);
      c.fillStyle = 'rgba(0,0,0,.3)'; c.beginPath(); c.ellipse(x, y, 26 * s, 5 * s, 0, 0, 7); c.fill();
      c.fillStyle = '#d9dcd6';
      c.fillRect(x - 18 * s + ph * 2 * s, y - 22 * s, 3 * s, 22 * s); c.fillRect(x - 10 * s - ph * 2 * s, y - 22 * s, 3 * s, 22 * s); c.fillRect(x + 10 * s + ph * 2 * s, y - 22 * s, 3 * s, 22 * s); c.fillRect(x + 17 * s - ph * 2 * s, y - 22 * s, 3 * s, 22 * s);
      c.beginPath(); c.ellipse(x, y - 28 * s, 24 * s, 11 * s, 0, 0, 7); c.fill();
      c.beginPath(); c.moveTo(x - 18 * s, y - 32 * s); c.lineTo(x - 28 * s, y - 52 * s); c.lineTo(x - 22 * s, y - 54 * s); c.lineTo(x - 12 * s, y - 36 * s); c.fill();
      c.beginPath(); c.ellipse(x - 28 * s, y - 55 * s, 7 * s, 5 * s, -.4, 0, 7); c.fill();
      d.push({ b: [x - 38 * s, y - 64 * s, 66 * s, 66 * s], l: 'Animal · deer', p: 90, k: 'alert' });
      d.push({ zone: [.14, .53, .27, .2], l: 'Crop stress · row 14', k: 'crowd' });
      return d;
    }
  };

  // Front camera of an autonomous robot in an aisle (KenRobotics)
  SCENES.robot = {
    osd: 'ROBOT-03  FRONT CAMERA',
    bg: function (c, w, h) {
      SCENES.aisle.bg(c, w, h);
      var vx = w * .5, vy = h * .34, f = w * .5, z = 7, sx = vx + (-.6) * f / z, sy = vy + 2.8 * f / z, s = f / z;
      cuboid(c, sx, sy, 1.1 * s, .25 * s, .3 * s, '#7a6852', '#8f7c63', '#5b4d3d');
      cuboid(c, sx + .1 * s, sy - .25 * s, .9 * s, .75 * s, .3 * s, '#857358', '#9a876b', '#635440');
    },
    frame: function (c, w, h, t) {
      var vx = w * .5, vy = h * .34, f = w * .5, d = [], s = f / 7;
      c.save(); c.setLineDash([6, 6]); c.lineDashOffset = -t * 20; c.strokeStyle = 'rgba(115,196,197,.9)'; c.lineWidth = 3;
      c.beginPath(); c.moveTo(w * .55, h); c.bezierCurveTo(w * .6, h * .8, w * .62, h * .7, w * .56, h * .58); c.lineTo(w * .52, h * .45); c.stroke(); c.restore();
      d.push({ b: [vx - .6 * s - 2, vy + 2.8 * s - 1.05 * s, 1.45 * s, 1.08 * s], l: 'Obstacle · pallet', p: 93, k: 'alert' });
      var z = 22 - (t * 1.1) % 14, p = [vx + .45 * f / z, vy + 2.8 * f / z];
      d.push({ b: person(c, p[0], p[1], 1.75 * f / z, { vest: '#aab54f', stripe: 1, hat: '#e8e4d6', phase: t * 6 }), l: 'Person', p: 95, k: 'person' });
      return d;
    }
  };


  // Overhead people-counting camera in a retail store (KenVision)
  function shopper(c, x, y, r, col, ang) {
    c.fillStyle = 'rgba(0,0,0,.28)'; c.beginPath(); c.ellipse(x + r * .35, y + r * .35, r * 1.05, r * .7, ang, 0, 7); c.fill();
    c.fillStyle = col; c.beginPath(); c.ellipse(x, y, r, r * .62, ang, 0, 7); c.fill();
    c.fillStyle = '#2b2420'; c.beginPath(); c.arc(x, y, r * .44, 0, 7); c.fill();
    c.fillStyle = 'rgba(255,255,255,.15)'; c.beginPath(); c.arc(x - r * .12, y - r * .12, r * .18, 0, 7); c.fill();
  }
  var STORE_PATHS = [
    [[.47, 1.05], [.48, .8], [.3, .76], [.06, .76], [.06, .415], [.3, .415], [.52, .415], [.6, .62], [.53, .82], [.53, 1.05]],
    [[.52, 1.05], [.55, .84], [.62, .5], [.66, .46], [.66, .46], [.66, .46], [.74, .62], [.7, .86], [.5, 1.05]],
    [[.5, 1.05], [.44, .8], [.3, .585], [.1, .585], [.1, .245], [.4, .245], [.56, .3], [.6, .8], [.46, 1.05]],
    [[.44, 1.05], [.4, .76], [.2, .755], [.2, .585], [.44, .585], [.5, .7], [.44, 1.05]],
    [[.56, 1.05], [.6, .7], [.52, .245], [.24, .245], [.24, .415], [.5, .5], [.58, 1.05]],
    [[.5, 1.05], [.58, .62], [.7, .4], [.64, .38], [.64, .38], [.56, .6], [.52, 1.05]]
  ];
  function along(path, q) {
    var segs = [], tot = 0;
    for (var i = 1; i < path.length; i++) { var d = Math.hypot(path[i][0] - path[i - 1][0], path[i][1] - path[i - 1][1]) + .02; segs.push(d); tot += d; }
    var tgt = q * tot;
    for (i = 0; i < segs.length; i++) {
      if (tgt <= segs[i]) { var a = path[i], b = path[i + 1], k = tgt / segs[i]; return [lerp(a[0], b[0], k), lerp(a[1], b[1], k), Math.atan2(b[1] - a[1], b[0] - a[0])]; }
      tgt -= segs[i];
    }
    var e = path[path.length - 1]; return [e[0], e[1], 0];
  }
  SCENES.store = {
    osd: 'CAM-02  STORE FLOOR',
    bg: function (c, w, h) {
      var R = rng(52), u = w / 480, i;
      c.fillStyle = '#c9c6bf'; c.fillRect(0, 0, w, h);
      c.strokeStyle = 'rgba(80,76,70,.18)'; c.lineWidth = 1;
      for (i = 0; i < w; i += 18 * u) { c.beginPath(); c.moveTo(i, 0); c.lineTo(i, h); c.stroke(); }
      for (i = 0; i < h; i += 18 * u) { c.beginPath(); c.moveTo(0, i); c.lineTo(w, i); c.stroke(); }
      speckle(c, w, h, 0, 1400, R, .08);
      c.fillStyle = '#6d6a64'; c.fillRect(0, 0, w, h * .05); c.fillRect(0, h * .95, w * .38, h * .05); c.fillRect(w * .62, h * .95, w * .38, h * .05);
      c.fillStyle = '#3f3c38'; c.fillRect(w * .4, h * .9, w * .2, h * .1);
      var cols = ['#b4473a', '#3f6f9a', '#d0a43a', '#4f8a54', '#8b5aa8', '#d9d4c8', '#c26d2c'];
      [.15, .32, .49, .66].forEach(function (gy) {
        c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(w * .085, h * gy + 3 * u, w * .42, h * .075);
        c.fillStyle = '#e6e3dc'; c.fillRect(w * .08, h * gy, w * .42, h * .075);
        for (var k = 0; k < 18; k++) { c.fillStyle = cols[(k * 3 + gy * 100 | 0) % cols.length]; c.fillRect(w * (.085 + k * .023), h * (gy + .008), w * .02, h * .026); c.fillStyle = cols[(k * 5 + 2) % cols.length]; c.fillRect(w * (.085 + k * .023), h * (gy + .041), w * .02, h * .026); }
      });
      c.fillStyle = 'rgba(0,0,0,.25)'; c.beginPath(); c.arc(w * .665, h * .455, w * .055, 0, 7); c.fill();
      c.fillStyle = '#e8e2d4'; c.beginPath(); c.arc(w * .66, h * .45, w * .055, 0, 7); c.fill();
      for (i = 0; i < 8; i++) { c.fillStyle = cols[i % cols.length]; c.beginPath(); c.arc(w * .66 + Math.cos(i * .8) * w * .03, h * .45 + Math.sin(i * .8) * w * .03, w * .011, 0, 7); c.fill(); }
      [[.16], [.7]].forEach(function (cy) { c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(w * .845, h * cy[0] + 3 * u, w * .12, h * .08); c.fillStyle = '#3b3f45'; c.fillRect(w * .84, h * cy[0], w * .12, h * .08); c.fillStyle = '#9aa3ad'; c.fillRect(w * .86, h * (cy[0] + .015), w * .03, h * .03); });
      c.fillStyle = '#c3c0b8'; c.fillRect(w * .815, h * .26, w * .01, h * .36);
    },
    frame: function (c, w, h, t) {
      var u = w / 480, d = [], r = 9 * u;
      shopper(c, w * .9, h * .11, r, '#2f5d7c', Math.PI / 2);
      var Q = [[.89, .3], [.89, .38], [.885, .46], [.89, .54]];
      Q.forEach(function (q, i) { var x = w * q[0] + Math.sin(t * .8 + i) * 1.5 * u, y = h * q[1]; shopper(c, x, y, r, ['#7a4b3a', '#5d6b7a', '#7c7a3e', '#4d4d63'][i], -Math.PI / 2); d.push({ b: [x - r * 1.3, y - r * 1.3, r * 2.6, r * 2.6], l: '', k: 'person' }); });
      var clr = ['#3e5f8a', '#8a3e3e', '#4f6b46', '#6b4f7a', '#8a6a3e', '#3e7a7a', '#5a5a5a'];
      STORE_PATHS.forEach(function (path, i) {
        for (var n = 0; n < (i < 2 ? 2 : 1); n++) {
          var q = ((t / (34 + i * 3)) + i * .17 + n * .5) % 1, pos = along(path, q), x = pos[0] * w, y = pos[1] * h;
          if (y > h * 1.02) continue;
          shopper(c, x, y, r, clr[(i + n * 3) % clr.length], pos[2]);
          d.push({ b: [x - r * 1.3, y - r * 1.3, r * 2.6, r * 2.6], l: '', k: 'person' });
        }
      });
      d.push({ zone: [.82, .25, .14, .34], l: 'Queue · 4 · ~3 min', k: 'alert' });
      d.push({ zone: [.56, .32, .2, .26], l: 'Promo display · dwell 1m 42s', k: 'crowd' });
      d.push({ line: [.38, .86, .62, .86], l: 'Entry · IN ' + (412 + Math.floor(t / 2.5)), k: 'ok' });
      return d;
    }
  };

  // Warehouse floor with a forklift lane (KenSafety real-world example)
  function forklift(c, fx, fy, u, dir) {
    var L = 78 * u, H = 44 * u, x = fx - L / 2, y = fy;
    c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.ellipse(fx, y, L * .62, 8 * u, 0, 0, 7); c.fill();
    c.fillStyle = '#7d6237'; rrect(c, x, y - H, L * .72, H * .78, 4 * u); c.fill();
    c.fillStyle = '#5c4728'; c.fillRect(x, y - H * .5, L * .72, H * .3);
    c.fillStyle = '#1d1e20'; c.fillRect(x + L * .08, y - H * 1.45, 3 * u, H * .7); c.fillRect(x + L * .5, y - H * 1.45, 3 * u, H * .7); c.fillRect(x + L * .08, y - H * 1.47, L * .45, 3 * u);
    var mx = dir > 0 ? x + L * .72 : x - L * .06;
    c.fillStyle = '#262729'; c.fillRect(mx, y - H * 1.6, L * .06, H * 1.55);
    c.fillStyle = '#3a3b3d'; c.fillRect(dir > 0 ? mx : mx - L * .26, y - 5 * u, L * .32, 3 * u);
    c.fillStyle = '#a4836c'; c.beginPath(); c.arc(x + L * .32, y - H * 1.02, 6 * u, 0, 7); c.fill();
    c.fillStyle = '#e4e0d2'; c.beginPath(); c.ellipse(x + L * .32, y - H * 1.07, 7 * u, 4 * u, 0, Math.PI, 0); c.fill();
    c.fillStyle = '#121212'; c.beginPath(); c.arc(x + L * .14, y - 4 * u, 8 * u, 0, 7); c.arc(x + L * .58, y - 4 * u, 8 * u, 0, 7); c.fill();
    return [x - L * .32, y - H * 1.7, L * 1.4, H * 1.75];
  }
  SCENES.whse = {
    osd: 'CAM-09  AISLE 3 · VEHICLE LANE',
    bg: function (c, w, h) {
      var R = rng(63), u = w / 480, hz = h * .42, g, i, k;
      c.fillStyle = '#2d3033'; c.fillRect(0, 0, w, hz);
      for (i = 0; i < 6; i++) {
        var x0 = i * w / 6 + 4 * u, bw = w / 6 - 8 * u;
        [.05, .17, .29].forEach(function (ly) {
          for (k = 0; k < 3; k++) { if (R() < .2) continue; var bh = h * (.06 + R() * .04), tone = 100 + R() * 40; c.fillStyle = 'rgb(' + (tone + 12 | 0) + ',' + (tone - 6 | 0) + ',' + (tone - 34 | 0) + ')'; c.fillRect(x0 + k * bw / 3 + 2 * u, h * (ly + .1) - bh, bw / 3 - 4 * u, bh); }
          c.fillStyle = '#93582c'; c.fillRect(x0, h * (ly + .1), bw, 3 * u);
        });
        c.fillStyle = '#3d5672'; c.fillRect(x0 - 3 * u, 0, 4 * u, hz); c.fillRect(x0 + bw - 1 * u, 0, 4 * u, hz);
      }
      g = c.createLinearGradient(0, hz, 0, h); g.addColorStop(0, '#55585a'); g.addColorStop(1, '#717371'); c.fillStyle = g; c.fillRect(0, hz, w, h - hz);
      speckle(c, w, h, hz, 2400, R, .12);
      c.fillStyle = 'rgba(176,160,74,.12)'; c.fillRect(0, h * .52, w, h * .2);
      c.fillStyle = 'rgba(190,172,80,.95)'; c.fillRect(0, h * .52, w, 3 * u); c.fillRect(0, h * .72, w, 3 * u);
      c.fillStyle = 'rgba(225,222,210,.55)';
      for (i = 0; i < 4; i++) { var ax = w * (.12 + i * .25), ay = h * .62; c.beginPath(); c.moveTo(ax, ay - 6 * u); c.lineTo(ax + 22 * u, ay - 6 * u); c.lineTo(ax + 22 * u, ay - 12 * u); c.lineTo(ax + 34 * u, ay); c.lineTo(ax + 22 * u, ay + 12 * u); c.lineTo(ax + 22 * u, ay + 6 * u); c.lineTo(ax, ay + 6 * u); c.fill(); }
      c.fillStyle = 'rgba(80,140,95,.35)'; c.fillRect(0, h * .8, w, h * .12);
      c.fillStyle = 'rgba(100,170,115,.9)'; c.fillRect(0, h * .8, w, 2 * u); c.fillRect(0, h * .92, w, 2 * u);
      cuboid(c, w * .02, h * .99, w * .12, 22 * u, 10 * u, '#7b6a54', '#907e65', '#5d5141');
      cuboid(c, w * .86, h * .99, w * .12, 30 * u, 10 * u, '#83725a', '#99876c', '#625645');
      c.globalCompositeOperation = 'lighter'; for (i = 0; i < 3; i++) glow(c, w * (.2 + i * .3), 0, w * .18, .18); c.globalCompositeOperation = 'source-over';
    },
    frame: function (c, w, h, t) {
      var u = w / 480, d = [], items = [];
      var fx = w * (.5 + .3 * Math.sin(t * .28)), dir = Math.cos(t * .28) > 0 ? 1 : -1;
      items.push({ y: h * .68, f: function () { d.push({ b: forklift(c, fx, h * .68, u, dir), l: 'Forklift', p: 92, k: 'vehicle' }); } });
      var cyc = (t % 12) / 12, q = cyc < .5 ? cyc * 2 : 2 - cyc * 2, py = lerp(h * .9, h * .62, Math.min(1, q * 1.3)), px = w * .62;
      var inLane = py < h * .72;
      items.push({ y: py, f: function () { d.push({ b: person(c, px, py, 74 * u, { vest: '#b0b84f', stripe: 1, hat: '#e8e4d6', phase: q > 0 && q < .77 ? t * 6 : 0, walk: q < .77 }), l: inLane ? 'Person in vehicle zone' : 'Person', p: 96, k: inLane ? 'alert' : 'person' }); } });
      var bx = w * .2 + Math.sin(t * .5) * 3 * u;
      items.push({ y: h * .5, f: function () { d.push({ b: person(c, bx, h * .5, 62 * u, { vest: '#3a3f47', arm: '#3a3f47', hat: '#e8e4d6', phase: 0, walk: false }), l: 'No hi-vis vest', p: 91, k: 'alert' }); } });
      items.sort(function (a, b) { return a.y - b.y; }).forEach(function (i) { i.f(); });
      d.push({ zone: [0.005, .52, .99, .2], l: 'Vehicle zone', k: 'crowd' });
      return d;
    }
  };

  // Living room camera with a fall and inactivity event (KenHome)
  SCENES.living = {
    osd: 'LIVING ROOM',
    bg: function (c, w, h) {
      var R = rng(71), u = w / 480, hz = h * .55, g, i;
      g = c.createLinearGradient(0, 0, 0, hz); g.addColorStop(0, '#b9ad9c'); g.addColorStop(1, '#a89c8b'); c.fillStyle = g; c.fillRect(0, 0, w, hz);
      c.fillStyle = '#efeee8'; c.fillRect(w * .06, h * .08, w * .22, h * .32); c.fillStyle = '#d9dcd6'; c.fillRect(w * .07, h * .09, w * .2, h * .3);
      c.fillStyle = '#8d8274'; c.fillRect(w * .169, h * .08, 3 * u, h * .32); c.fillRect(w * .06, h * .235, w * .22, 3 * u);
      c.globalCompositeOperation = 'lighter'; glow(c, w * .17, h * .24, w * .22, .18); c.globalCompositeOperation = 'source-over';
      c.fillStyle = '#6f6556'; c.fillRect(w * .58, h * .12, w * .16, h * .14); c.fillStyle = '#a99a7d'; c.fillRect(w * .59, h * .13, w * .14, h * .12);
      g = c.createLinearGradient(0, hz, 0, h); g.addColorStop(0, '#7a5f45'); g.addColorStop(1, '#94765a'); c.fillStyle = g; c.fillRect(0, hz, w, h - hz);
      c.strokeStyle = 'rgba(40,28,18,.35)'; c.lineWidth = 1;
      for (i = -8; i <= 16; i++) { c.beginPath(); c.moveTo(w * .5 + i * w * .04, hz); c.lineTo(w * .5 + i * w * .12, h); c.stroke(); }
      speckle(c, w, h, hz, 900, R, .08);
      c.fillStyle = 'rgba(160,150,135,.85)'; c.beginPath(); c.ellipse(w * .5, h * .8, w * .3, h * .11, 0, 0, 7); c.fill();
      c.fillStyle = '#2d2f33'; c.fillRect(w * .03, h * .42, w * .18, h * .16); c.fillStyle = '#121315'; c.fillRect(w * .05, h * .27, w * .14, h * .14);
      c.fillStyle = '#5d6b78'; c.fillRect(w * .66, h * .5, w * .32, h * .2); c.fillStyle = '#6c7b88'; c.fillRect(w * .66, h * .42, w * .32, h * .1); c.fillStyle = '#4e5a65'; c.fillRect(w * .64, h * .44, w * .04, h * .26); c.fillRect(w * .96, h * .44, w * .04, h * .26);
      cuboid(c, w * .44, h * .7, w * .14, 14 * u, 8 * u, '#6b5440', '#7d644d', '#544232');
      c.fillStyle = '#3b3a37'; c.fillRect(w * .9, h * .2, 2 * u, h * .3); c.fillStyle = '#e8dcc0'; c.beginPath(); c.moveTo(w * .875, h * .2); c.lineTo(w * .93, h * .2); c.lineTo(w * .915, h * .13); c.lineTo(w * .89, h * .13); c.fill();
    },
    frame: function (c, w, h, t) {
      var u = w / 480, d = [], cyc = (t % 16) / 16, H = 96 * u;
      var o = { vest: '#7a6a8a', arm: '#7a6a8a', legs: '#4b4f57', hat: null, phase: t * 4 };
      if (cyc < .5) {
        var x = lerp(w * .22, w * .52, cyc / .5), y = h * .82;
        d.push({ b: person(c, x, y, H, o), l: 'Person', p: 97, k: 'person' });
      } else {
        var lx = w * .52, ly = h * .86, secs = Math.floor((cyc - .5) * 16 * 15);
        c.save(); c.translate(lx, ly); c.rotate(-Math.PI / 2 + .08); o.walk = false; o.phase = 0; person(c, 0, 0, H, o); c.restore();
        d.push({ b: [lx - H * 1.02, ly - H * .26, H * 1.08, H * .4], l: 'Possible fall · inactive ' + secs + 's', p: 92, k: 'alert' });
      }
      return d;
    }
  };

  // Driveway camera at night (KenHome)
  SCENES.drive = {
    osd: 'DRIVEWAY', ir: true,
    bg: function (c, w, h) {
      var R = rng(81), u = w / 480, g, i;
      c.fillStyle = '#5b5c58'; c.fillRect(0, 0, w, h * .34);
      c.fillStyle = '#7a7b77'; c.fillRect(w * .3, h * .06, w * .4, h * .28);
      c.strokeStyle = 'rgba(0,0,0,.25)'; for (i = 1; i < 7; i++) { c.beginPath(); c.moveTo(w * .3, h * (.06 + i * .04)); c.lineTo(w * .7, h * (.06 + i * .04)); c.stroke(); }
      c.fillStyle = '#4a4b48'; c.fillRect(w * .76, h * .1, w * .08, h * .24); c.fillStyle = '#e9e9dc'; c.fillRect(w * .86, h * .12, 4 * u, 6 * u);
      c.globalCompositeOperation = 'lighter'; glow(c, w * .865, h * .14, w * .2, .25); c.globalCompositeOperation = 'source-over';
      c.fillStyle = '#3e4a3c'; c.fillRect(0, h * .34, w, h * .66);
      speckle(c, w, h, h * .34, 1800, R, .16);
      g = c.createLinearGradient(0, h * .34, 0, h); g.addColorStop(0, '#77776f'); g.addColorStop(1, '#8a8a82'); c.fillStyle = g;
      c.beginPath(); c.moveTo(w * .28, h * .34); c.lineTo(w * .72, h * .34); c.lineTo(w * .86, h); c.lineTo(w * .14, h); c.fill();
      c.fillStyle = '#9a9a92'; c.beginPath(); c.moveTo(w * .76, h * .34); c.lineTo(w * .84, h * .34); c.lineTo(w * .98, h); c.lineTo(w * .92, h); c.fill();
      for (i = 0; i < 6; i++) { c.fillStyle = 'rgba(40,52,38,.9)'; c.beginPath(); c.arc(w * (.05 + i * .04), h * .4, 12 * u, 0, 7); c.fill(); }
      car(c, w * .42, h * .45, w * .16, h * .34, '#6c6e70');
    },
    frame: function (c, w, h, t) {
      var u = w / 480, d = [], cyc = (t % 14) / 14, q = cyc < .6 ? cyc / .6 : 1;
      d.push({ b: [w * .41, h * .44, w * .18, h * .38], l: 'Vehicle · parked', p: 98, k: 'vehicle' });
      var x = lerp(w * .04, w * .36, q), y = lerp(h * .95, h * .72, q), near = q > .7;
      d.push({ b: person(c, x, y, 70 * u, { vest: '#3c3f44', arm: '#3c3f44', hat: null, phase: q < 1 ? t * 6 : 0, walk: q < 1 }), l: near ? 'Person near vehicle' : 'Person', p: 94, k: near ? 'alert' : 'person' });
      return d;
    }
  };
  var noise = {};
  function noiseFrames(w, h) {
    var k = w + 'x' + h; if (noise[k]) return noise[k];
    var out = [];
    for (var n = 0; n < 4; n++) {
      var cv = mk(w, h), x = cv.getContext('2d'), id = x.createImageData(w, h), D = id.data;
      for (var i = 0; i < D.length; i += 4) { var v = 128 + (Math.random() - .5) * 150; D[i] = D[i + 1] = D[i + 2] = v; D[i + 3] = 255; }
      x.putImageData(id, 0, 0); out.push(cv);
    }
    return (noise[k] = out);
  }

  var cams = [];
  document.querySelectorAll('canvas.cctv').forEach(function (cv) {
    var sc = SCENES[cv.dataset.scene]; if (!sc) return;
    var W = cv.width, H = cv.height, bw = W / 2 | 0, bh = H / 2 | 0;
    var bg = mk(bw, bh); sc.bg(bg.getContext('2d'), bw, bh);
    var buf = mk(bw, bh);
    if (cv.dataset.osd) sc = Object.assign({}, sc, { osd: cv.dataset.osd });
    var cam = { cv: cv, ctx: cv.getContext('2d'), sc: sc, bg: bg, buf: buf, b: buf.getContext('2d'), bw: bw, bh: bh, vis: true, st: {} };
    if (sc.init) cam.st.P = sc.init(bw, bh);
    cams.push(cam);
  });
  var byScene = {}; cams.forEach(function (c) { byScene[c.cv.dataset.scene] = c; });

  function render(cam, t, fi) {
    var c = cam.ctx, W = cam.cv.width, H = cam.cv.height, sc = cam.sc, b = cam.b;
    b.globalCompositeOperation = 'source-over'; b.globalAlpha = 1; b.drawImage(cam.bg, 0, 0);
    var dets = sc.frame(b, cam.bw, cam.bh, t, cam.st) || [];
    c.imageSmoothingEnabled = true; c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
    c.filter = 'blur(' + (W / 960).toFixed(2) + 'px)'; c.drawImage(cam.buf, 0, 0, W, H); c.filter = 'none';
    c.globalCompositeOperation = 'saturation'; c.globalAlpha = sc.ir ? 1 : .55; c.fillStyle = 'hsl(0,0%,50%)'; c.fillRect(0, 0, W, H);
    if (sc.ir) { c.globalCompositeOperation = 'multiply'; c.globalAlpha = .6; c.fillStyle = '#d3dcd5'; c.fillRect(0, 0, W, H); c.globalCompositeOperation = 'screen'; c.globalAlpha = .12; c.fillStyle = '#9fb2a6'; c.fillRect(0, 0, W, H); }
    else { c.globalCompositeOperation = 'soft-light'; c.globalAlpha = .35; c.fillStyle = '#6d7f8c'; c.fillRect(0, 0, W, H); }
    c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
    if (sc.heat) heat(c, W, H, cam);
    var g = c.createRadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, W * .72); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.55)'); c.fillStyle = g; c.fillRect(0, 0, W, H);
    var nf = noiseFrames(W / 2 | 0, H / 2 | 0); c.globalCompositeOperation = 'overlay'; c.globalAlpha = sc.ir ? .5 : .28; c.drawImage(nf[fi % 4], 0, 0, W, H);
    c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1;
    var sx = W / cam.bw, sy = H / cam.bh, lw = Math.max(1.5, W / 400), fs = Math.round(W < 700 ? W / 30 : W / 52);
    dets.forEach(function (d) {
      if (d.dot) { c.fillStyle = 'rgba(115,196,197,.95)'; c.beginPath(); c.arc(d.dot[0] * W, d.dot[1] * H, Math.max(1.5, W / 320), 0, 7); c.fill(); return; }
      if (d.line) {
        var lx1 = d.line[0] * W, ly1 = d.line[1] * H, lx2 = d.line[2] * W, ly2 = d.line[3] * H;
        c.strokeStyle = COL[d.k]; c.lineWidth = lw * 1.5; c.setLineDash([8, 6]); c.beginPath(); c.moveTo(lx1, ly1); c.lineTo(lx2, ly2); c.stroke(); c.setLineDash([]);
        c.font = '600 ' + fs + 'px Montserrat, system-ui, sans-serif';
        var lt = c.measureText(d.l).width + fs * .8; c.fillStyle = COL[d.k]; c.fillRect(lx1, ly1 - fs * 1.5 - 4, lt, fs * 1.5); c.fillStyle = '#101114'; c.fillText(d.l, lx1 + fs * .4, ly1 - 4 - fs * .42);
        return;
      }
      var col = COL[d.k], x, y, w, h;
      if (d.zone) { x = d.zone[0] * W; y = d.zone[1] * H; w = d.zone[2] * W; h = d.zone[3] * H; c.setLineDash([6, 4]); }
      else { x = d.b[0] * sx; y = d.b[1] * sy; w = d.b[2] * sx; h = d.b[3] * sy; }
      c.strokeStyle = col; c.lineWidth = lw; c.strokeRect(x, y, w, h); c.setLineDash([]);
      if (!d.l) return;
      var lab = d.l + (d.p ? '  ' + d.p + '%' : '');
      c.font = '600 ' + fs + 'px Montserrat, system-ui, sans-serif';
      var tw = c.measureText(lab).width + fs * .8, th = fs * 1.5, ly = y - th - 2 > 0 ? y - th - 2 : y + 2;
      var lx = Math.max(0, Math.min(x - lw / 2, W - tw));
      c.fillStyle = col; c.fillRect(lx, ly, tw, th); c.fillStyle = '#101114'; c.fillText(lab, lx + fs * .4, ly + fs * 1.08);
    });
    c.font = '600 ' + fs + 'px Montserrat, system-ui, sans-serif'; c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 3; c.fillStyle = 'rgba(255,255,255,.92)';
    c.fillText(sc.osd, fs, fs * 1.7); var ts = stamp(t); c.fillText(ts, W - c.measureText(ts).width - fs, fs * 1.7); c.shadowBlur = 0;
    if (sc.heat && cam.onCount) cam.onCount(cam.st.count);
  }

  function heat(c, W, H, cam) {
    var P = cam.st.P, cols = 12, rows = 8, grid = new Array(cols * rows).fill(0);
    P.forEach(function (p) { var i = Math.min(cols - 1, p.x / cam.bw * cols | 0), j = Math.min(rows - 1, p.y / cam.bh * rows | 0); grid[j * cols + i]++; });
    c.globalCompositeOperation = 'screen';
    for (var j = 0; j < rows; j++) for (var i = 0; i < cols; i++) {
      var n = grid[j * cols + i]; if (!n) continue;
      var cx = (i + .5) * W / cols, cy = (j + .5) * H / rows, r = W / cols * 1.4;
      var col = n >= 4 ? '255,121,83' : n >= 2 ? '124,40,233' : '115,196,197', a = Math.min(.55, .18 + n * .08);
      var g = c.createRadialGradient(cx, cy, 0, cx, cy, r); g.addColorStop(0, 'rgba(' + col + ',' + a + ')'); g.addColorStop(1, 'rgba(' + col + ',0)');
      c.fillStyle = g; c.fillRect(cx - r, cy - r, r * 2, r * 2);
    }
    c.globalCompositeOperation = 'source-over';
  }

  var thumbs = [].slice.call(document.querySelectorAll('canvas.thumb'));
  function drawThumbs() {
    thumbs.forEach(function (tc) {
      var src = byScene[tc.dataset.from]; if (!src) return;
      var cr = tc.dataset.crop.split(',').map(Number), W = src.cv.width, H = src.cv.height;
      tc.getContext('2d').drawImage(src.cv, cr[0] * W, cr[1] * H, cr[2] * W, cr[2] * W * 9 / 16, 0, 0, tc.width, tc.height);
    });
  }

  var plaza = byScene.plaza, countEl = document.getElementById('crowd-count');
  if (plaza && countEl) plaza.onCount = function (n) { countEl.textContent = n; };

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { cams.forEach(function (c) { if (c.cv === e.target) c.vis = e.isIntersecting; }); }); });
    cams.forEach(function (c) { io.observe(c.cv); });
  }

  var fi = 0, last = 0, lastThumb = 0;
  function tick(now) {
    if (now - last > 80) {
      last = now; fi++;
      var t = (now - T0) / 1000 + 3;
      cams.forEach(function (c) { if (c.vis) render(c, t, fi); });
      if (now - lastThumb > 400) { lastThumb = now; drawThumbs(); }
    }
    requestAnimationFrame(tick);
  }
  function first() { cams.forEach(function (c) { render(c, 3, 0); }); drawThumbs(); }
  first();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(first);
  if (!reduce) requestAnimationFrame(tick);

  // Hourly detections chart
  var bars = document.getElementById('bars');
  if (bars) {
    var V = [6, 4, 3, 3, 4, 9, 22, 48, 74, 88, 92, 81, 70, 79, 86, 64, 0, 0, 0, 0, 0, 0, 0, 0], max = 92, NS = 'http://www.w3.org/2000/svg', bwid = 300 / 24, s = '';
    s += '<defs><linearGradient id="barg" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#0A34ED"/><stop offset="1" stop-color="#7C28E9"/></linearGradient></defs>';
    V.forEach(function (v, i) {
      var hgt = v / max * 72, x = i * bwid + 1.5;
      s += '<rect x="' + x + '" y="' + (78 - Math.max(hgt, 1.5)) + '" width="' + (bwid - 3) + '" height="' + Math.max(hgt, 1.5) + '" rx="2" fill="' + (i === 14 ? '#FF7953' : v ? 'url(#barg)' : '#2a2c33') + '"/>';
    });
    ['00', '06', '12', '18'].forEach(function (l, i) { s += '<text x="' + (i * 6 * bwid + 1.5) + '" y="93">' + l + ':00</text>'; });
    bars.innerHTML = s;
  }
})();
