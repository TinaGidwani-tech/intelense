// Builds site/content/worldmap.json: a dotted world map (land only) with pixel positions for the two offices.
// Needs: npm i world-atlas@2 topojson-client@3 d3-geo@3 (in any scratch folder) and run: node make_worldmap.mjs <out.json>
// Map data: Natural Earth (public domain) via the world-atlas package.
import { createRequire } from 'module';
import fs from 'fs';
const require = createRequire(process.cwd() + '/');
const { geoNaturalEarth1, geoContains } = require('d3-geo');
const topojson = require('topojson-client');
const land = topojson.feature(require('world-atlas/land-50m.json'), 'land');
const W = 1000, STEP = 9;
const proj = geoNaturalEarth1().rotate([-10, 0]).fitExtent([[0, 0], [W, 560]], { type: 'Sphere' });
const top = proj([0, 76])[1], bottom = proj([0, -56])[1];
const H = Math.round(bottom - top);
const dots = [];
for (let y = top + STEP / 2; y < bottom; y += STEP) {
  const row = Math.round((y - top) / STEP);
  for (let x = (row % 2 ? STEP / 2 : 0) + 2; x < W - 2; x += STEP) {
    const ll = proj.invert([x, y]);
    if (!ll || !isFinite(ll[0])) continue;
    if (geoContains(land, ll)) dots.push([x, y - top]);
  }
}
const GROUPS = 8;
const groups = Array.from({ length: GROUPS }, () => []);
for (const [x, y] of dots) groups[Math.min(GROUPS - 1, Math.floor((x / W) * GROUPS))].push(`M${x.toFixed(1)} ${y.toFixed(1)}h0`);
const pt = ([lon, lat]) => { const p = proj([lon, lat]); return { x: +p[0].toFixed(1), y: +(p[1] - top).toFixed(1) }; };
const ca = pt([-79.337, 43.856]), inn = pt([77.536, 12.887]);
const mx = (ca.x + inn.x) / 2, dist = Math.hypot(inn.x - ca.x, inn.y - ca.y);
const cy = Math.min(ca.y, inn.y) - dist * 0.32;
const arc = `M${ca.x} ${ca.y}Q${mx.toFixed(1)} ${cy.toFixed(1)} ${inn.x} ${inn.y}`;
fs.writeFileSync(process.argv[2], JSON.stringify({ w: W, h: H, dots: dots.length, groups: groups.map((g) => g.join('')), pins: { ca, in: inn }, arc }));
console.log('dots', dots.length, 'size', W, H, 'ca', ca, 'in', inn);
