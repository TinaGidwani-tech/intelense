"""Product UI kit for module visuals: a dark app with large rounded cards, big numbers with trend pills,
a highlighted line chart, an activity feed, event cards, bar charts and ring gauges.

build.py sets `icon` after import so this module can reuse the site icon set.
"""

icon = None  # set by build.py

EXTRA_ICONS = {
    'grid': '<rect x="4" y="4" width="7" height="7" rx="2"/><rect x="13" y="4" width="7" height="7" rx="2"/><rect x="4" y="13" width="7" height="7" rx="2"/><rect x="13" y="13" width="7" height="7" rx="2"/>',
    'cog': '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>',
    'cam': '<rect x="3" y="7" width="13" height="10" rx="2"/><path d="M16 11l5-3v8l-5-3"/>',
    'alert': '<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17h.01"/>',
    'check': '<circle cx="12" cy="12" r="9"/><path d="M8 12.5l2.6 2.5L16 9.5"/>',
    'doc': '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 12h5M10 16h5"/>',
    'star': '<path d="M12 4l2.4 5 5.4.6-4 3.7 1.1 5.3L12 16l-4.9 2.6 1.1-5.3-4-3.7 5.4-.6z"/>',
    'cart': '<path d="M3 4h2l2.4 11h10.2L20 7H6.2"/><circle cx="9" cy="19" r="1.4"/><circle cx="17" cy="19" r="1.4"/>',
    'drop': '<path d="M12 3c3.5 4.5 6 7.8 6 11a6 6 0 0 1-12 0c0-3.2 2.5-6.5 6-11z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    'battery': '<rect x="3" y="8" width="16" height="8" rx="2"/><path d="M21 11v2M6 11v2M9 11v2"/>',
}

TONES = {  # pill background, text, mark colour
    'pos': ('rgba(115,196,197,.16)', '#93e3e4', '#73C4C5'),
    'neg': ('rgba(255,121,83,.16)', '#ffa58b', '#FF7953'),
    'info': ('rgba(84,112,255,.18)', '#a9b8ff', '#5b7cff'),
    'violet': ('rgba(124,40,233,.22)', '#c9a8ff', '#a26bf2'),
    'warn': ('rgba(242,210,138,.16)', '#f2d28a', '#f2d28a'),
    'mute': ('rgba(255,255,255,.07)', '#b4b6c4', '#8d8f9e'),
}


def ic(name):
    if name in EXTRA_ICONS:
        return '<svg viewBox="0 0 24 24" aria-hidden="true">' + EXTRA_ICONS[name] + '</svg>'
    return icon(name)


def pill(text, tone='pos'):
    return f'<span class="ap-pill {tone}">{text}</span>'


def _smooth(pts):
    # Catmull-Rom spline through the points, as cubic Bezier segments.
    d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f' C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}'
    return d


def spark(vals, tone='pos', uid='s'):
    w, h = 160, 44
    lo, hi = min(vals), max(vals)
    pts = [(i * w / (len(vals) - 1), h - 6 - (v - lo) / ((hi - lo) or 1) * (h - 14)) for i, v in enumerate(vals)]
    col = TONES[tone][2]
    line = _smooth(pts)
    return (f'<svg class="ap-spark" viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true">'
            f'<defs><linearGradient id="sp-{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" stop-opacity=".28"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>'
            f'<path d="{line} L{w},{h} L0,{h} Z" fill="url(#sp-{uid})"/>'
            f'<path d="{line}" fill="none" stroke="{col}" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>')


def line_chart(labels, vals, hi, tip, uid, ticks, prev=None, every=1):
    """Wide chart for desktop plus a narrower copy with larger relative text for phones."""
    return (_line(labels, vals, hi, tip, uid, ticks, prev, every, 680, 250, 'ap-lg')
            + _line(labels, vals, hi, tip, uid + 'm', ticks, prev, every * 2, 380, 230, 'ap-sm'))


def _line(labels, vals, hi, tip, uid, ticks, prev, every, w, h, cls):
    """Smooth line with an area fill and one highlighted column, in the style of a hero finance chart."""
    l, r, t, b = 40, 20, 44, 30
    lo, top = ticks[0], ticks[-1]
    x = lambda i: l + i * (w - l - r) / (len(vals) - 1)
    y = lambda v: t + (1 - (v - lo) / (top - lo)) * (h - t - b)
    out = [f'<svg class="ap-chart {cls}" viewBox="0 0 {w} {h}" role="img" aria-label="{tip}">',
           f'<defs><linearGradient id="ar-{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5b7cff" stop-opacity=".32"/><stop offset="1" stop-color="#5b7cff" stop-opacity="0"/></linearGradient>'
           f'<linearGradient id="ln-{uid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#5b7cff"/><stop offset=".55" stop-color="#a26bf2"/><stop offset="1" stop-color="#FF7953"/></linearGradient>'
           f'<linearGradient id="hb-{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF7953"/><stop offset=".5" stop-color="#7C28E9"/><stop offset="1" stop-color="#0A34ED" stop-opacity=".15"/></linearGradient>'
           f'<filter id="gl-{uid}" x="-200%" y="-20%" width="500%" height="140%"><feGaussianBlur stdDeviation="9"/></filter></defs>']
    for v in ticks:
        out.append(f'<line x1="{l}" x2="{w - r}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#2a2b31" stroke-dasharray="2 5"/>'
                   f'<text x="{l - 10}" y="{y(v) + 4:.1f}" text-anchor="end" class="ap-tick">{v:g}</text>')
    for i, lab in enumerate(labels):
        if i == hi or (i % every == 0 and abs(i - hi) >= max(2, every)):
            out.append(f'<text x="{x(i):.1f}" y="{h - 8}" text-anchor="middle" class="ap-tick{" on" if i == hi else ""}">{lab}</text>')
    hx, hy = x(hi), y(vals[hi])
    base = y(lo)
    out.append(f'<rect x="{hx - 14:.1f}" y="{hy:.1f}" width="28" height="{base - hy:.1f}" rx="10" fill="url(#hb-{uid})" filter="url(#gl-{uid})" opacity=".85"/>'
               f'<rect x="{hx - 11:.1f}" y="{hy:.1f}" width="22" height="{base - hy:.1f}" rx="9" fill="url(#hb-{uid})"/>')
    if prev:
        pp = [(x(i), y(v)) for i, v in enumerate(prev)]
        out.append(f'<path d="{_smooth(pp)}" fill="none" stroke="#5a5c68" stroke-width="1.5" stroke-dasharray="4 5"/>')
    pts = [(x(i), y(v)) for i, v in enumerate(vals)]
    line = _smooth(pts)
    out.append(f'<path d="{line} L{pts[-1][0]:.1f},{base:.1f} L{pts[0][0]:.1f},{base:.1f} Z" fill="url(#ar-{uid})"/>'
               f'<path d="{line}" fill="none" stroke="url(#ln-{uid})" stroke-width="2.5" stroke-linecap="round"/>'
               f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="6" fill="#0c0d10" stroke="#fff" stroke-width="2.5"/>')
    tw = 16 + len(tip) * 7.3
    tx = min(max(hx - tw / 2, l), w - r - tw)
    out.append(f'<rect x="{tx:.1f}" y="{hy - 40:.1f}" width="{tw:.1f}" height="26" rx="13" fill="#fff"/>'
               f'<text x="{tx + tw / 2:.1f}" y="{hy - 23:.1f}" text-anchor="middle" class="ap-tip">{tip}</text></svg>')
    return ''.join(out)


def bar_chart(labels, vals, hi, fmt, uid, w=320, h=210):
    """Rounded columns in a muted tone with one highlighted, labelled column."""
    t, b = 34, 28
    n = len(vals)
    gap = (w / n) * 0.34
    bw = w / n - gap
    top = max(vals) * 1.05
    out = [f'<svg class="ap-chart" viewBox="0 0 {w} {h}" role="img" aria-label="{labels[hi]}: {fmt(vals[hi])}">'
           f'<defs><linearGradient id="bh-{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF7953"/><stop offset=".55" stop-color="#7C28E9"/><stop offset="1" stop-color="#0A34ED"/></linearGradient></defs>']
    for i, v in enumerate(vals):
        bh = v / top * (h - t - b)
        bx = gap / 2 + i * (bw + gap)
        by = h - b - bh
        fill = f'url(#bh-{uid})' if i == hi else '#26272d'
        out.append(f'<path d="M{bx:.1f},{h - b} V{by + 8:.1f} q0,-8 8,-8 h{bw - 16:.1f} q8,0 8,8 V{h - b} Z" fill="{fill}"/>'
                   f'<text x="{bx + bw / 2:.1f}" y="{h - 8}" text-anchor="middle" class="ap-tick{" on" if i == hi else ""}">{labels[i]}</text>')
        if i == hi:
            s = fmt(v)
            tw = 16 + len(s) * 7.3
            px = min(max(bx + bw / 2 - tw / 2, 1), w - tw - 1)
            out.append(f'<rect x="{px:.1f}" y="{by - 30:.1f}" width="{tw:.1f}" height="22" rx="11" fill="#fff"/>'
                       f'<text x="{px + tw / 2:.1f}" y="{by - 15:.1f}" text-anchor="middle" class="ap-tip">{s}</text>')
    out.append('</svg>')
    return ''.join(out)


def ring(pct, big, label, uid, tone='brand'):
    r, c = 46, 2 * 3.14159 * 46
    fs = ' style="font-size:19px"' if len(big) > 4 else ''
    stroke = f'url(#rg-{uid})' if tone == 'brand' else TONES[tone][2]
    return (f'<div class="ap-ring"><svg viewBox="0 0 120 120" role="img" aria-label="{label}: {big}">'
            f'<defs><linearGradient id="rg-{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A34ED"/><stop offset=".5" stop-color="#7C28E9"/><stop offset="1" stop-color="#FF7953"/></linearGradient></defs>'
            f'<circle cx="60" cy="60" r="{r}" fill="none" stroke="#26272d" stroke-width="10"/>'
            f'<circle cx="60" cy="60" r="{r}" fill="none" stroke="{stroke}" stroke-width="10" stroke-linecap="round" stroke-dasharray="{c * pct / 100:.1f} {c:.1f}" transform="rotate(-90 60 60)"/>'
            f'<text x="60" y="66" text-anchor="middle" class="ap-ring-n"{fs}>{big}</text></svg><span>{label}</span></div>')


# ---------------------------------------------------------------- cards

def card(title, body, sub='', action='', cls=''):
    act = f'<span class="ap-act">{action}</span>' if action else ''
    sb = f'<p class="ap-csub">{sub}</p>' if sub else ''
    return f'<div class="ap-card {cls}"><div class="ap-ch"><div><h4>{title}</h4>{sb}</div>{act}</div>{body}</div>'


def kpi(k, uid):
    ico, label, value, delta, tone, vs, vals = k
    sp = spark(vals, 'neg' if tone == 'neg' else 'pos' if tone == 'pos' else 'info', uid) if vals else ''
    dl = pill(delta, tone) if delta else ''
    return (f'<div class="ap-card ap-kpi"><div class="ap-kh"><span class="ap-ic">{ic(ico)}</span><span>{label}</span></div>'
            f'<b class="ap-big">{value}</b><div class="ap-kf">{dl}<span class="ap-vs">{vs}</span></div>{sp}</div>')


def feed(items, title='Activity', action='See all'):
    lis = ''.join(f'<li><span class="ap-av {tone}">{ic(ico)}</span><p>{text}</p><time>{t}</time></li>' for ico, tone, text, t in items)
    return card(title, f'<ul class="ap-feed">{lis}</ul>', action=action)


def events(items, title='Latest events'):
    cards = ''.join(
        f'<div class="ap-card ap-ev"><div class="ap-evh">{pill(tag, tone)}<span class="ap-ic">{ic(ico)}</span></div>'
        f'<p class="ap-evt">{name}</p><b class="ap-evn {tone}">{value}</b><p class="ap-evm">{meta}</p></div>'
        for tag, tone, ico, name, value, meta in items)
    return f'<div class="ap-sec"><div class="ap-ch"><h4>{title}</h4><span class="ap-act">See all</span></div><div class="ap-evs">{cards}</div></div>'


def tasks(rows, title, action='', cls='ap-wide'):
    """Rows of (name, sub, tag, tag_tone, progress or None, status, status_tone)."""
    lis = []
    for name, sub, tag, tt, prog, st, stt in rows:
        bar = f'<span class="ap-prog"><i style="width:{prog}%"></i></span>' if prog is not None else '<span></span>'
        lis.append(f'<li><div><b>{name}</b><small>{sub}</small></div>{pill(tag, tt)}{bar}{pill(st, stt)}</li>')
    return card(title, f'<ul class="ap-tasks">{"".join(lis)}</ul>', action=action, cls=cls)


def main(title, big, delta, tone, vs, legend, chart):
    """Hero chart card: a big number with a trend pill, a legend and the chart."""
    lg = ''.join(f'<span><i class="{"prev" if prev else ""}"></i>{lab}</span>' for lab, prev in legend)
    dl = pill(delta, tone) if delta else ''
    return card(title, f'<div class="ap-mhead"><b>{big}</b>{dl}<span class="ap-vs">{vs}</span><span class="ap-legend">{lg}</span></div>{chart}')


def media(title, html, tag=('Live', 'neg'), cls='', foot=()):
    act = pill(tag[0], tag[1]) if tag else ''
    ft = f'<div class="ap-mfoot">{"".join(pill(t, tone) for t, tone in foot)}</div>' if foot else ''
    return f'<div class="ap-card ap-media {cls}"><div class="ap-ch"><h4>{title}</h4>{act}</div><div class="ap-mbody">{html}</div>{ft}</div>'


# ---------------------------------------------------------------- full app and hero

def dash(c):
    """c: logo, alt, hello, sub, range, nav (icon names, first active), kpis, main, side, events, bottom (list of card html)."""
    nav = ''.join(f'<span class="ap-nav{" on" if i == 0 else ""}">{ic(n)}</span>' for i, n in enumerate(c['nav']))
    kpis = ''.join(kpi(k, f'{c["uid"]}{i}') for i, k in enumerate(c['kpis']))
    return f'''<div class="ap" role="img" aria-label="{c['aria']}">
        <aside class="ap-side"><span class="ap-mark">{ic(c['nav'][0])}</span>{nav}<span class="ap-me">{c['me']}</span></aside>
        <div class="ap-main">
          <div class="ap-head">
            <div><img class="ap-logo" src="assets/logos/{c['logo']}-light.png" alt="{c['alt']}" height="22"><p class="ap-hello">{c['hello']}</p><p class="ap-sub">{c['sub']}</p></div>
            <div class="ap-tools"><span class="ap-select">{c['range']} <i>▾</i></span><span class="ap-live">Live</span><span class="ap-clock" id="clock">14:32:09</span></div>
          </div>
          <div class="ap-kpis">{kpis}</div>
          <div class="ap-row">{c['main']}{c['side']}</div>
          {c['events']}
          <div class="ap-bottom">{''.join(c['bottom'])}</div>
        </div>
      </div>'''


def hero(c):
    """Compact app frame for module heroes: live media, two KPI cards and one alert."""
    kpis = ''.join(kpi(k, f'h{c["uid"]}{i}') for i, k in enumerate(c['kpis']))
    tag, tone, ico, text, t = c['alert']
    aria = f' role="img" aria-label="{c["aria"]}"' if c.get('aria') else ''
    return f'''<div class="ap ap-hero">
          <div class="ap-hbar"><img class="ap-logo" src="assets/logos/{c['logo']}-light.png" alt="" height="20"><span class="ap-site">{c['site']}</span><span class="ap-live">Live</span></div>
          <div class="ap-card ap-media ap-hmedia"{aria}>{c['media']}</div>
          <div class="ap-hrow">{kpis}<div class="ap-card ap-alert"><div class="ap-evh">{pill(tag, tone)}<time>{t}</time></div><div class="ap-arow"><span class="ap-av {tone}">{ic(ico)}</span><p>{text}</p></div></div></div>
        </div>'''
