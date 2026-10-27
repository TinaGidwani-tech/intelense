"""Drawn scenes for kenvision.ai: plan-view illustrations of a store, a building, a city junction and a warehouse.
Pure SVG, animated with CSS (see kv.css .sc-*), colours come from the page theme. Every scene exists in a 'raw' form
(what the camera sees) and a 'ken' form (with detections, heat and labels added by KenVision)."""

W, H = 800, 500


def _defs(uid):
    return (f'<defs><radialGradient id="h1{uid}"><stop offset="0" stop-color="#FF7953" stop-opacity=".55"/><stop offset="1" stop-color="#FF7953" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="h2{uid}"><stop offset="0" stop-color="#7C28E9" stop-opacity=".4"/><stop offset="1" stop-color="#7C28E9" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="h3{uid}"><stop offset="0" stop-color="#0A34ED" stop-opacity=".35"/><stop offset="1" stop-color="#0A34ED" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="fv{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0A34ED" stop-opacity=".28"/><stop offset="1" stop-color="#0A34ED" stop-opacity="0"/></linearGradient></defs>')


def _box(x, y, w, h, label, cls='b'):
    lw = 18 + len(label) * 7.4
    return (f'<g class="sc-box {cls}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6"/>'
            f'<rect class="sc-tag" x="{x}" y="{y - 20}" width="{lw:.0f}" height="18" rx="9"/><text x="{x + 8}" y="{y - 7}">{label}</text></g>')


def _person(cx, cy, cls=''):
    return f'<circle class="sc-p {cls}" cx="{cx}" cy="{cy}" r="7"/>'


def retail(ken=True, uid='a'):
    s = [f'<svg class="sc" viewBox="0 0 {W} {H}" role="img" aria-label="Plan view of a store with shoppers, aisles and checkout">', _defs(uid)]
    s.append('<rect class="sc-floor" x="20" y="20" width="760" height="460" rx="30"/>')
    s.append('<rect class="sc-door" x="350" y="474" width="100" height="12" rx="6"/>')
    pal = ('#FF7953', '#78AFCF', '#7C28E9', '#0A34ED')
    for x in (95, 235, 375):
        s.append(f'<rect class="sc-shelf" x="{x}" y="70" width="64" height="300" rx="14"/>')
        s.append(''.join(f'<rect x="{x + 9}" y="{84 + j * 35}" width="46" height="22" rx="6" fill="{pal[(j + x // 140) % 4]}" opacity=".35"/>' for j in range(8)))
    for y in (110, 190, 270):
        s.append(f'<rect class="sc-shelf" x="620" y="{y}" width="110" height="44" rx="12"/>')
    s.append('<rect class="sc-shelf" x="520" y="70" width="64" height="150" rx="14"/>')
    if ken:
        s.append(f'<circle cx="310" cy="230" r="120" fill="url(#h1{uid})"/><circle cx="165" cy="330" r="90" fill="url(#h2{uid})"/><circle cx="590" cy="300" r="90" fill="url(#h3{uid})"/>')
    # shoppers walking the aisles
    s.append(f'<g class="mv m1">{_box(158, 168, 34, 46, "Footfall") if ken else ""}{_person(175, 200)}</g>')
    s.append(f'<g class="mv m2">{_box(298, 238, 34, 46, "Dwell") if ken else ""}{_person(315, 270)}</g>')
    s.append(f'<g class="mv m3">{_person(450, 160)}</g><g class="mv m4">{_person(205, 400)}</g><g class="mv m5">{_person(345, 120)}</g>')
    s.append(f'<g class="mv m6">{_person(480, 300)}</g><g class="mv m7">{_person(560, 360)}</g>')
    for i, y in enumerate((132, 212, 292)):  # queue at the counters
        s.append(_person(600, y + 22, 'still'))
        if i == 0:
            s.append(_person(580, y + 22, 'still') + _person(560, y + 22, 'still'))
    if ken:
        s.append(_box(542, 118, 68, 44, 'Queue', 'b warn'))
    s.append('</svg>')
    return ''.join(s)


def buildings(ken=True, uid='b'):
    s = [f'<svg class="sc" viewBox="0 0 {W} {H}" role="img" aria-label="Plan view of a building floor with occupied and empty rooms">', _defs(uid)]
    s.append('<rect class="sc-floor" x="20" y="20" width="760" height="460" rx="30"/>')
    rooms = [(50, 50, 220, 190, 1), (290, 50, 220, 190, 0), (530, 50, 220, 190, 1), (50, 260, 220, 190, 0), (290, 260, 220, 190, 1), (530, 260, 220, 190, 0)]
    for i, (x, y, w, h, on) in enumerate(rooms):
        cls = 'sc-room on' if (on and ken) else 'sc-room'
        s.append(f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="22"/>')
        if ken:
            s.append(f'<text class="sc-t2" x="{x + 18}" y="{y + 32}">{"Occupied" if on else "Empty"}</text>')
    # desks and people
    for (x, y, w, h, on) in rooms:
        for dx in (50, 130):
            s.append(f'<rect class="sc-desk" x="{x + dx}" y="{y + 90}" width="56" height="30" rx="8"/>')
    for k, (cx, cy) in enumerate([(100, 150), (180, 150), (590, 140), (670, 160), (340, 380), (420, 360)]):
        s.append(f'<g class="mv s{k % 3 + 1}">{_person(cx, cy)}</g>')
    if ken:
        s.append(_box(560, 118, 54, 44, 'Occupancy'))
        s.append('<g class="sc-hvac"><rect x="318" y="206" width="164" height="26" rx="13"/><text x="400" y="224" text-anchor="middle">HVAC follows people</text></g>')
    s.append('</svg>')
    return ''.join(s)


def cities(ken=True, uid='c'):
    s = [f'<svg class="sc" viewBox="0 0 {W} {H}" role="img" aria-label="Plan view of a city junction with traffic and a crowd at the crossing">', _defs(uid)]
    s.append('<rect class="sc-floor" x="20" y="20" width="760" height="460" rx="30"/>')
    for (x, y, w, h) in ((50, 50, 290, 160), (460, 50, 290, 160), (50, 290, 290, 160), (460, 290, 290, 160)):
        s.append(f'<rect class="sc-block" x="{x}" y="{y}" width="{w}" height="{h}" rx="22"/>')
    s.append('<rect class="sc-road" x="20" y="215" width="760" height="70"/><rect class="sc-road" x="365" y="20" width="70" height="460"/>')
    s.append('<line class="sc-lane" x1="20" y1="250" x2="780" y2="250"/><line class="sc-lane" x1="400" y1="20" x2="400" y2="480"/>')
    for i in range(5):
        s.append(f'<rect class="sc-zebra" x="{338 + i * 0}" y="{222 + i * 13}" width="22" height="8" rx="3"/><rect class="sc-zebra" x="{440}" y="{222 + i * 13}" width="22" height="8" rx="3"/>')
    for k, (x, y) in enumerate([(60, 228), (170, 262), (620, 228), (700, 262)]):
        s.append(f'<rect class="sc-car car{k % 2 + 1}" x="{x}" y="{y}" width="34" height="18" rx="6"/>')
    for k, (x, y) in enumerate([(373, 70), (409, 400), (373, 330)]):
        s.append(f'<rect class="sc-car cv{k % 2 + 1}" x="{x}" y="{y}" width="18" height="34" rx="6"/>')
    crowd = [(470, 190), (486, 200), (502, 188), (520, 198), (478, 214), (498, 218), (516, 214), (534, 190), (546, 208), (462, 204)]
    if ken:
        s.append(f'<circle cx="500" cy="204" r="95" fill="url(#h2{uid})"/>')
    for (x, y) in crowd:
        s.append(f'<circle class="sc-p pulse" cx="{x}" cy="{y}" r="6"/>')
    if ken:
        s.append(_box(452, 166, 108, 62, 'Crowd density', 'b warn'))
        s.append(_box(86, 214, 86, 40, 'Flow'))
    s.append('</svg>')
    return ''.join(s)


def surveillance(ken=True, uid='d'):
    s = [f'<svg class="sc" viewBox="0 0 {W} {H}" role="img" aria-label="Plan view of a warehouse with a camera, a forklift and a worker">', _defs(uid)]
    s.append('<rect class="sc-floor" x="20" y="20" width="760" height="460" rx="30"/>')
    for x in (70, 160, 250):
        s.append(f'<rect class="sc-shelf" x="{x}" y="120" width="56" height="330" rx="12"/>')
    for x in (560, 650):
        s.append(f'<rect class="sc-shelf" x="{x}" y="120" width="56" height="330" rx="12"/>')
    s.append('<rect class="sc-door" x="350" y="474" width="100" height="12" rx="6"/>')
    if ken:
        s.append(f'<polygon class="sc-fov" points="400,60 190,470 610,470" fill="url(#fv{uid})"/>')
    s.append('<g class="sc-cam"><rect x="380" y="34" width="40" height="26" rx="8"/><circle cx="400" cy="47" r="6"/></g>')
    s.append('<rect class="sc-fork mv f1" x="360" y="340" width="54" height="30" rx="8"/>')
    s.append(f'<g class="mv m2">{_box(448, 238, 38, 58, "PPE check", "b warn") if ken else ""}{_person(467, 280)}</g>')
    s.append(f'<g class="mv m4">{_person(330, 190)}</g><g class="mv m6">{_person(520, 400)}</g>')
    if ken:
        s.append('<g class="sc-alert"><circle cx="520" cy="262" r="14"/><text x="520" y="267" text-anchor="middle">!</text></g>')
    s.append('</svg>')
    return ''.join(s)


SCENES = {'retail-analytics': retail, 'commercial-buildings': buildings, 'smart-cities': cities, 'video-surveillance': surveillance}


def scene(key, ken=True, uid=''):
    return SCENES[key](ken=ken, uid=uid or key[:2])


# ---- small illustrations for the capability explorer ----

def mini(kind, uid='x'):
    if kind == 'paths':
        return ('<svg class="sc" viewBox="0 0 800 500" role="img" aria-label="Movement paths and dwell points"><rect class="sc-floor" x="20" y="20" width="760" height="460" rx="30"/>'
                '<path class="sc-path" d="M60 420 C180 380 200 260 320 250 S470 330 560 220 S700 120 740 90"/><path class="sc-path v" d="M80 90 C200 140 260 120 340 180 S470 170 560 330 S690 400 740 440"/>'
                '<path class="sc-path c" d="M60 250 C160 230 240 300 330 330 S470 420 540 400"/>'
                '<circle class="sc-dwell" cx="320" cy="250" r="34"/><circle class="sc-dwell v" cx="560" cy="330" r="26"/><circle class="sc-dwell c" cx="340" cy="180" r="20"/>'
                '<text class="sc-t2" x="268" y="300">Dwell</text></svg>')
    if kind == 'heat':
        return (f'<svg class="sc" viewBox="0 0 800 500" role="img" aria-label="Heatmap of a floor"><rect class="sc-floor" x="20" y="20" width="760" height="460" rx="30"/>{_defs(uid)}'
                f'<rect class="sc-shelf" x="95" y="70" width="64" height="300" rx="14"/><rect class="sc-shelf" x="235" y="70" width="64" height="300" rx="14"/><rect class="sc-shelf" x="375" y="70" width="64" height="300" rx="14"/><rect class="sc-shelf" x="515" y="70" width="64" height="300" rx="14"/>'
                f'<circle cx="330" cy="260" r="150" fill="url(#h1{uid})"/><circle cx="460" cy="180" r="110" fill="url(#h1{uid})"/><circle cx="190" cy="330" r="110" fill="url(#h2{uid})"/><circle cx="640" cy="330" r="90" fill="url(#h3{uid})"/></svg>')
    if kind == 'anomaly':
        dots = ''.join(f'<circle class="sc-p flow" style="--i:{i}" cx="{90 + (i % 6) * 110}" cy="{120 + (i // 6) * 90}" r="9"/>' for i in range(24))
        return (f'<svg class="sc" viewBox="0 0 800 500" role="img" aria-label="Normal flow with one unusual movement"><rect class="sc-floor" x="20" y="20" width="760" height="460" rx="30"/>{dots}'
                '<g class="sc-alert big"><circle cx="560" cy="380" r="24"/><text x="560" y="390" text-anchor="middle">!</text></g><text class="sc-t2" x="470" y="440">Unusual movement</text></svg>')
    if kind == 'dash':
        bars = ''.join(f'<rect class="sc-bar" style="--i:{i}" x="{70 + i * 46}" y="{330 - h}" width="30" height="{h}" rx="8"/>' for i, h in enumerate([70, 110, 90, 150, 190, 130, 100, 160]))
        return ('<svg class="sc" viewBox="0 0 800 500" role="img" aria-label="Charts and reports"><rect class="sc-floor" x="20" y="20" width="760" height="460" rx="30"/>'
                f'{bars}<path class="sc-line" d="M70 130 C140 100 180 160 250 120 S360 70 440 110 S560 150 640 90"/>'
                '<circle class="sc-ring" cx="640" cy="320" r="70"/><circle class="sc-ring on" cx="640" cy="320" r="70"/><text class="sc-t2" x="70" y="390">Footfall by hour</text><text class="sc-t2" x="590" y="425">Report</text></svg>')
    if kind == 'alerts':
        rows = [('neg', 'Queue building', 'Checkout 2 · now'), ('warn', 'Zone 3 over capacity', 'Ground floor · 2 min'), ('info', 'Unusual movement', 'Display case · 9 min')]
        r = ''.join(f'<g class="sc-note {c}" style="--i:{i}"><rect x="170" y="{80 + i * 120}" width="460" height="92" rx="22"/><circle cx="212" cy="{126 + i * 120}" r="9"/><text class="sc-t3" x="240" y="{120 + i * 120}">{t}</text><text class="sc-t2" x="240" y="{146 + i * 120}">{m}</text></g>' for i, (c, t, m) in enumerate(rows))
        return f'<svg class="sc" viewBox="0 0 800 500" role="img" aria-label="Alert notifications"><rect class="sc-floor" x="20" y="20" width="760" height="460" rx="30"/>{r}</svg>'
    return ''
