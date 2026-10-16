// Cursor-reactive grid background.
// Cells near the pointer light up, hold briefly, then fade; a click sends a ring of light across the grid.
// Usage: const destroy = initCursorGrid(container, { color: '#0a0a0a' }); ... destroy();

const DEFAULTS = {
  cellSize: 60,
  color: '#0a0a0a',
  radius: 160,
  falloff: 'smooth', // 'smooth' | 'linear' | 'sharp'
  holdTime: 300, // ms a cell stays at its peak after the cursor last touched it
  fadeDuration: 700, // ms to fade from peak to zero
  lineWidth: 1,
  maxOpacity: 0.3,
  fillOpacity: 0, // 0 = outline only
  gridOpacity: 0, // 0 = no always-visible grid
  cellRadius: 4,
  clickPulse: true,
  pulseSpeed: 700, // px per second
};

const FALLOFF = {
  smooth: (t) => t * t * (3 - 2 * t),
  linear: (t) => t,
  sharp: (t) => t * t * t,
};

function hexToRgb(hex) {
  let h = String(hex).replace('#', '');
  if (h.length === 3) h = h.split('').map((c) => c + c).join('');
  const n = parseInt(h, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

export function initCursorGrid(container, options = {}) {
  const noop = () => {};
  if (!container || typeof window === 'undefined') return noop;
  const mq = (q) => window.matchMedia && window.matchMedia(q).matches;
  // Respect reduced motion and skip touch-only devices, where there is no cursor to follow.
  if (mq('(prefers-reduced-motion: reduce)') || mq('(hover: none)')) return noop;

  const o = { ...DEFAULTS, ...options };
  const ease = FALLOFF[o.falloff] || FALLOFF.smooth;
  const [r, g, b] = hexToRgb(o.color);
  const rgb = `${r},${g},${b}`;

  const canvas = document.createElement('canvas');
  canvas.setAttribute('aria-hidden', 'true');
  canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;display:block;';
  container.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  let width = 0, height = 0, dpr = 1;
  let cols = 0, rows = 0, offsetX = 0, offsetY = 0;
  let peak = new Float32Array(0); // brightness each cell reached (0..1)
  let touched = new Float64Array(0); // timestamp the cell was last lit
  let pulses = []; // { x, y, start }
  let rafId = 0;
  let pointer = null; // last pointer position in container coordinates
  const life = o.holdTime + o.fadeDuration;

  function build() {
    const rect = container.getBoundingClientRect();
    width = Math.max(1, Math.round(rect.width));
    height = Math.max(1, Math.round(rect.height));
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(height * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // Centre the grid and overhang by a partial cell on each side so it fills edge to edge.
    cols = Math.ceil(width / o.cellSize) + 1;
    rows = Math.ceil(height / o.cellSize) + 1;
    offsetX = (width - cols * o.cellSize) / 2;
    offsetY = (height - rows * o.cellSize) / 2;
    peak = new Float32Array(cols * rows);
    touched = new Float64Array(cols * rows);
    draw(performance.now());
  }

  // Current brightness of a cell: its peak, held, then faded out.
  function level(i, now) {
    const p = peak[i];
    if (!p) return 0;
    const age = now - touched[i];
    if (age <= o.holdTime) return p;
    if (age >= life) { peak[i] = 0; return 0; }
    return p * (1 - (age - o.holdTime) / o.fadeDuration);
  }

  // Raise a cell to `v` (never dims it while the cursor is near).
  function light(i, v, now) {
    const cur = level(i, now);
    if (v >= cur) { peak[i] = v; touched[i] = now; }
    else if (cur > 0 && v > 0) { touched[i] = now; peak[i] = cur; }
  }

  function lightAround(x, y, now) {
    const rad = o.radius, cs = o.cellSize;
    const c0 = Math.max(0, Math.floor((x - rad - offsetX) / cs));
    const c1 = Math.min(cols - 1, Math.floor((x + rad - offsetX) / cs));
    const r0 = Math.max(0, Math.floor((y - rad - offsetY) / cs));
    const r1 = Math.min(rows - 1, Math.floor((y + rad - offsetY) / cs));
    for (let row = r0; row <= r1; row++) {
      const cy = offsetY + row * cs + cs / 2;
      for (let col = c0; col <= c1; col++) {
        const cx = offsetX + col * cs + cs / 2;
        const d = Math.hypot(cx - x, cy - y);
        if (d < rad) light(row * cols + col, ease(1 - d / rad), now);
      }
    }
  }

  // Flash every cell whose centre the ring has passed since the previous frame.
  function advancePulses(now) {
    if (!pulses.length) return;
    const cs = o.cellSize, maxR = Math.hypot(width, height);
    pulses = pulses.filter((p) => {
      const rNow = ((now - p.start) / 1000) * o.pulseSpeed;
      const rPrev = p.prev;
      p.prev = rNow;
      const c0 = Math.max(0, Math.floor((p.x - rNow - offsetX) / cs));
      const c1 = Math.min(cols - 1, Math.floor((p.x + rNow - offsetX) / cs));
      const r0 = Math.max(0, Math.floor((p.y - rNow - offsetY) / cs));
      const r1 = Math.min(rows - 1, Math.floor((p.y + rNow - offsetY) / cs));
      for (let row = r0; row <= r1; row++) {
        const cy = offsetY + row * cs + cs / 2;
        for (let col = c0; col <= c1; col++) {
          const d = Math.hypot(offsetX + col * cs + cs / 2 - p.x, cy - p.y);
          if (d >= rPrev && d < rNow) light(row * cols + col, 1, now);
        }
      }
      return rPrev < maxR;
    });
  }

  function cellPath(x, y, s, rad) {
    ctx.beginPath();
    if (ctx.roundRect) ctx.roundRect(x, y, s, s, rad);
    else ctx.rect(x, y, s, s);
  }

  function draw(now) {
    ctx.clearRect(0, 0, width, height);
    const cs = o.cellSize, inset = o.lineWidth / 2, s = cs - o.lineWidth;
    ctx.lineWidth = o.lineWidth;

    if (o.gridOpacity > 0) {
      ctx.strokeStyle = `rgba(${rgb},${o.gridOpacity})`;
      for (let row = 0; row < rows; row++) {
        for (let col = 0; col < cols; col++) {
          cellPath(offsetX + col * cs + inset, offsetY + row * cs + inset, s, o.cellRadius);
          ctx.stroke();
        }
      }
    }

    let active = false;
    for (let i = 0; i < peak.length; i++) {
      if (!peak[i]) continue;
      const v = level(i, now);
      if (v <= 0.001) continue;
      active = true;
      const col = i % cols, row = (i / cols) | 0;
      const x = offsetX + col * cs + inset, y = offsetY + row * cs + inset;
      const a = v * o.maxOpacity;
      // Radial stroke: brightest at mid-side, fading toward the corners.
      const cx = x + s / 2, cy = y + s / 2;
      const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, s * 0.72);
      grad.addColorStop(0, `rgba(${rgb},${a})`);
      grad.addColorStop(0.68, `rgba(${rgb},${a})`);
      grad.addColorStop(1, `rgba(${rgb},0)`);
      cellPath(x, y, s, o.cellRadius);
      if (o.fillOpacity > 0) { ctx.fillStyle = `rgba(${rgb},${v * o.fillOpacity})`; ctx.fill(); }
      ctx.strokeStyle = grad;
      ctx.stroke();
    }
    return active || pulses.length > 0;
  }

  function cursorGridFrame(now) {
    rafId = 0;
    advancePulses(now);
    if (pointer) lightAround(pointer.x, pointer.y, now);
    pointer = null;
    // Keep the loop alive only while something is still visible.
    if (draw(now)) rafId = requestAnimationFrame(cursorGridFrame);
  }

  function wake() {
    if (!rafId) rafId = requestAnimationFrame(cursorGridFrame);
  }

  function local(e) {
    const rect = container.getBoundingClientRect();
    return { x: e.clientX - rect.left, y: e.clientY - rect.top };
  }

  // How far a point lies outside the container (0 when inside).
  function outside(p) {
    const dx = Math.max(0, -p.x, p.x - width), dy = Math.max(0, -p.y, p.y - height);
    return Math.hypot(dx, dy);
  }

  function onMove(e) {
    if (e.pointerType === 'touch') return;
    const p = local(e);
    if (outside(p) >= o.radius) return; // too far away to light any cell
    pointer = p;
    wake();
  }

  function onDown(e) {
    if (!o.clickPulse || e.pointerType === 'touch') return;
    const p = local(e);
    if (outside(p) > 0) return; // only clicks inside the container send a ring
    pulses.push({ x: p.x, y: p.y, start: performance.now(), prev: 0 });
    wake();
  }

  const ro = new ResizeObserver(() => build());
  ro.observe(container);
  build();
  window.addEventListener('pointermove', onMove, { passive: true });
  window.addEventListener('pointerdown', onDown, { passive: true });

  return function destroy() {
    window.removeEventListener('pointermove', onMove);
    window.removeEventListener('pointerdown', onDown);
    ro.disconnect();
    if (rafId) cancelAnimationFrame(rafId);
    rafId = 0;
    canvas.remove();
  };
}
