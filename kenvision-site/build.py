#!/usr/bin/env python3
"""Static generator for kenvision.ai, in the same design language as www.intelense.com.

It reuses the Intelense stylesheet, script and components (site/), adds kenvision-site/assets-src/kv.css and renders the pages from
content/pages.json (text copied word for word from the old site by tools/extract_old.py).

    python3 kenvision-site/build.py --deploy DIR [--preview] [--no-dark]

--deploy DIR writes the site for the host: the same URLs as the old site (/, /solutions/, /solutions/*.html, /company.html, /contact.html),
root-relative links, sitemap.xml, robots.txt, .htaccess, send-message.php.  --preview writes relative links instead, so the folder can be
opened from disk or from a preview host.
"""
import hashlib
import html as H
import importlib.util
import scenes
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE_DIR = HERE.parent / 'site'
sys.path.insert(0, str(SITE_DIR))
_spec = importlib.util.spec_from_file_location('intelense_build', SITE_DIR / 'build.py')
IB = importlib.util.module_from_spec(_spec)
sys.modules['intelense_build'] = IB
_spec.loader.exec_module(IB)  # only defines things; nothing is written

icon, OFFICES, world_map = IB.icon, IB.OFFICES, IB.world_map
CONTENT = json.loads((HERE / 'content' / 'pages.json').read_text(encoding='utf-8'))
ENABLE_THEME = '--dark' in sys.argv  # the light/dark toggle is off by default
PREVIEW = '--preview' in sys.argv

SITE_URL = 'https://kenvision.ai'
INTELENSE = 'https://www.intelense.com'
LINKEDIN = 'https://www.linkedin.com/company/intelense/'
XURL = 'https://x.com/Intelenseinc'
LOGIN_URL = 'https://kenanalytic.com/'
BLOG_URL = 'https://blog.kenvision.ai'
# Set to '' to send every "Book a 30-min Demo" button to the contact form instead of the Calendly page
CALENDLY_URL = 'https://calendly.com/enquiries-intelense/30min'

# token -> (preview file, public path)
LINKS = {
    'index': ('index.html', '/'),
    'solutions': ('solutions/index.html', '/solutions/'),
    'retail-analytics': ('solutions/retail-analytics.html', '/solutions/retail-analytics.html'),
    'commercial-buildings': ('solutions/commercial-buildings.html', '/solutions/commercial-buildings.html'),
    'smart-cities': ('solutions/smart-cities.html', '/solutions/smart-cities.html'),
    'video-surveillance': ('solutions/video-surveillance.html', '/solutions/video-surveillance.html'),
    'company': ('company.html', '/company.html'),
    'contact': ('contact.html', '/contact.html'),
}
SOLUTIONS = [
    ('retail-analytics', 'Retail Analytics', 'Footfall, heatmaps, dwell and queues'),
    ('commercial-buildings', 'Commercial Buildings', 'Occupancy and space utilization'),
    ('smart-cities', 'Smart Cities', 'Crowds, traffic and public safety'),
    ('video-surveillance', 'Video Surveillance', 'Detection, alerts and response'),
]
IMG_DIR = HERE / 'assets'

# Old pages hotlinked these Unsplash photos; the same local pictures stand in for them (no outside image hosts)
UNSPLASH = {
    '1486406146926': 'assets/commercial-buildings.webp', '1480714378408': 'assets/smart-city-street.webp',
    '1557597774': 'assets/alert-dashboard.webp', '1460925895917': 'assets/mall-escalators.webp',
    '1563986768609': 'assets/surveillance-camera.webp', '1551288049': 'assets/images/dashboards/analytics-dashboard.webp',
    '1534452203293': 'assets/retail-ai-view.webp', '1497366216548': 'assets/images/dashboards/kenvision-dashboard-elite.webp',
    '1581091226825': 'assets/images/icons/dashboard.webp',
}
CONTAIN = ('dashboards/', 'icons/', 'core-heatmaps')


def e(s):
    return H.escape(s or '', quote=False)


def ea(s):
    return H.escape(s or '', quote=True)


def local(src):
    """Local path of an old image (outside hosts replaced)."""
    if src.startswith('http'):
        for k, v in UNSPLASH.items():
            if k in src:
                return v
        raise SystemExit('no local image for ' + src)
    return src


def img(src, alt='', cls='', lazy=True, prio=False, attrs=''):
    src = local(src)
    from PIL import Image
    p = IMG_DIR / src.replace('assets/', '', 1)
    w, h = Image.open(p if p.exists() else SITE_DIR / src).size
    return (f'<img src="@a/{src[7:]}" alt="{ea(alt)}" width="{w}" height="{h}"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}'
            f'{" fetchpriority=" + chr(34) + "high" + chr(34) if prio else (" loading=" + chr(34) + "lazy" + chr(34) + " decoding=" + chr(34) + "async" + chr(34) if lazy else "")}{attrs}>')


def fits(src):
    return ' fit' if any(k in local(src) for k in CONTAIN) else ''


def vid(name, alt, cls='kx-vid'):
    """Muted looping clip from the shared footage library (Pexels). kv.js leaves it on the poster for visitors who prefer reduced motion."""
    return (f'<video class="{cls}" muted loop playsinline autoplay preload="metadata" poster="@a/footage/{name}-poster.jpg" aria-label="{ea(alt)}">'
            f'<source src="@a/footage/{name}.mp4" type="video/mp4"></video>')


def demo_href():
    return (CALENDLY_URL, ' target="_blank" rel="noopener"') if CALENDLY_URL else ('@contact', '')


def demo_btn(label='Book a 30-min Demo', cls='btn btn-blue'):
    href, extra = demo_href()
    return f'<a class="{cls}" href="{href}"{extra}>{label}</a>'


# ---------------------------------------------------------------- shared fragments

def header(active):
    items = ''.join(f'<li><a href="@{k}" style="--mod:#0A34ED"><i></i>{n}<small>{d}</small></a></li>' for k, n, d in SOLUTIONS)
    items += '<li><a class="all" href="@solutions">All solutions</a></li>'

    def cur(k):
        return ' aria-current="page"' if active == k else ''
    links = (f'<li class="has-menu"><a href="@solutions"{cur("solutions") or (" aria-current=" + chr(34) + "page" + chr(34) if active in dict((s[0], 1) for s in SOLUTIONS) else "")}>Solutions</a><div class="dropdown"><ul>{items}</ul></div></li>'
             f'<li><a href="@company"{cur("company")}>Company</a></li>'
             f'<li><a href="{INTELENSE}/ken360" rel="noopener">Intelense</a></li>'
             f'<li><a href="{BLOG_URL}" rel="noopener">Blog</a></li>')
    mobile = (f'<a href="@index">Home</a><a href="@solutions">Solutions</a>' + ''.join(f'<a class="sub" href="@{k}">{n}</a>' for k, n, _ in SOLUTIONS)
              + f'<a href="@company">Company</a><a href="{INTELENSE}/ken360">Intelense</a><a href="{BLOG_URL}">Blog</a><a href="{LOGIN_URL}">Login</a>')
    return f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="brand-g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0A34ED"/><stop offset=".3" stop-color="#7C28E9"/><stop offset=".6" stop-color="#FF7953"/><stop offset=".82" stop-color="#78AFCF"/><stop offset="1" stop-color="#73C4C5"/>
    </linearGradient>
  </defs>
</svg>

<div class="announce">
  <div class="wrap">
    <span><span class="tag-new">By Intelense</span>&nbsp; KenVision is the AI video intelligence product from Intelense</span>
    <a class="pill" href="{INTELENSE}/">Explore Intelense</a>
  </div>
</div>

<header class="nav">
  <div class="wrap">
    <a class="logo" href="@index"><img class="kv-logo logo-light" src="@a/logos/kenvision.png" alt="KenVision by Intelense, home" width="131" height="48"><img class="kv-logo logo-dark" src="@a/logos/kenvision-light.png" alt="" aria-hidden="true" width="131" height="48"></a>
    <ul class="nav-links">
      {links}
    </ul>
    <div class="nav-cta">
      {IB.THEME_BUTTON if ENABLE_THEME else ''}
      <a class="btn btn-ghost" href="{LOGIN_URL}" target="_blank" rel="noopener">Login</a>
      <a class="btn btn-blue" href="@contact">Request a demo</a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Menu"><span></span></button>
    </div>
  </div>
  <nav class="mobile-menu" id="mobile-menu" hidden aria-label="Mobile">
    <div class="wrap">
      {mobile}
      <a class="btn btn-blue" href="@contact">Request a demo</a>
    </div>
  </nav>
</header>
'''


def footer():
    sol = ''.join(f'<li><a href="@{k}">{n}</a></li>' for k, n, _ in SOLUTIONS)
    return f'''<footer>
  <div class="wrap">
    <div class="foot kx-foot">
      <div>
        <a class="logo" href="@index"><img class="kv-logo" src="@a/logos/kenvision-light.png" alt="KenVision by Intelense, home" width="153" height="56"></a>
        <p style="margin-top:16px;max-width:34ch">Turn data into insights. KenVision is the AI video intelligence product from Intelense.</p>
        <a class="by-link" href="{INTELENSE}/" rel="noopener">Visit Intelense</a>
      </div>
      <div>
        <h4>Solutions</h4>
        <ul>{sol}</ul>
      </div>
      <div>
        <h4>KenVision</h4>
        <ul><li><a href="@index">Home</a></li><li><a href="@company">Company</a></li><li><a href="@contact">Contact</a></li><li><a href="{BLOG_URL}" rel="noopener">Blog</a></li><li><a href="{LOGIN_URL}" rel="noopener">Login</a></li><li><a href="{demo_href()[0]}"{demo_href()[1]}>Request Demo</a></li></ul>
      </div>
      <div>
        <h4>Intelense</h4>
        <ul><li><a href="{INTELENSE}/">Intelense home</a></li><li><a href="{INTELENSE}/ken360">Ken360 platform</a></li><li><a href="{INTELENSE}/kenvision">KenVision on intelense.com</a></li><li><a href="{INTELENSE}/modules">All Ken modules</a></li><li><a href="{INTELENSE}/industries">Industries</a></li><li><a href="{INTELENSE}/about">About Intelense</a></li></ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul><li class="email">enquiries@intelense.ca</li><li class="email">dinesh@intelense.com</li><li><a href="tel:+12895523165">+1 (289) 552-3165</a> Canada</li><li><a href="tel:+919342810422">+91 93428 10422</a> India</li><li>Markham, Ontario, Canada</li><li>Bengaluru, India</li><li><a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn</a></li><li><a href="{XURL}" target="_blank" rel="noopener noreferrer">X</a></li></ul>
      </div>
    </div>
    <div class="legal"><span>© 2026 Intelense Inc. · <a href="{INTELENSE}/privacy" rel="noopener">Privacy</a> · <a href="{INTELENSE}/terms" rel="noopener">Terms</a></span><span>KenVision is a product of <a href="{INTELENSE}/">Intelense</a> · Photography: <a href="https://www.pexels.com" rel="noopener">Pexels</a> and <a href="https://unsplash.com" rel="noopener">Unsplash</a></span></div>
  </div>
</footer>
'''


def crumbs(*items):
    out = ['<li><a href="@index">Home</a></li>']
    for href, label in items:
        out.append(f'<li><a href="{href}">{label}</a></li>' if href else f'<li aria-current="page">{label}</li>')
    return f'<ol class="crumbs" aria-label="Breadcrumb">{"".join(out)}</ol>'


def hero(crumb, eyebrow, h1, lede, ctas, media='', extra='', center=False, below=''):
    copy = f'''{crumb}
      {eyebrow}
      <h1>{h1}</h1>
      <p class="lede">{lede}</p>
      <div class="hero-ctas">{ctas}</div>
      {extra}'''
    cls = 'page-hero kv-hero kx-hero' if media else ('page-hero hero-center kx-hero' if center else 'page-hero kx-hero')
    if below:
        inner = f'<div class="wrap">\n      {copy}\n      <div class="kx-below">{below}</div>\n    </div>'
    elif media:
        inner = f'<div class="wrap kv-hero-grid">\n      <div class="kv-hero-copy">\n      {copy}\n      </div>\n      <div class="kv-hero-visual">{media}</div>\n    </div>'
    else:
        inner = f'<div class="wrap">\n      {copy}\n    </div>'
    return f'''<section class="{cls}">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    {inner}
  </section>'''


def head_block(eyebrow, h2, lede=''):
    lede_html = f'<p class="lede">{lede}</p>' if lede else ''
    return f'''<div class="head">
        <div>
          <span class="eyebrow">{eyebrow}</span>
          <h2>{h2}</h2>
        </div>
        {lede_html}
      </div>'''


def block(inner, sid='', extra_cls=''):
    return f'<section class="block{" " + extra_cls if extra_cls else ""}"{f" id={chr(34)}{sid}{chr(34)}" if sid else ""}>\n    <div class="wrap">\n      {inner}\n    </div>\n  </section>'


def faq_block(items, title, lede=''):
    det = ''.join(f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary><p>{e(a)}</p></details>' for i, (q, a) in enumerate(items))
    return f'''<section class="block" id="faq">
    <div class="wrap faq-grid">
      <div>
        <span class="eyebrow">FAQ</span>
        <h2 style="margin-top:18px">{e(title)}</h2>
        {f'<p class="lede" style="margin-top:16px">{e(lede)}</p>' if lede else ''}
      </div>
      <div>{det}</div>
    </div>
  </section>'''


def cta_band(h2, lede, second=None, video=None):
    second = second or ('<a class="btn btn-black" href="@contact">Contact sales</a>')
    if video:
        second = second.replace('btn-black', 'btn-ghost')
    bg = f'<div class="bgv" aria-hidden="true">{vid(video, "")}</div>' if video else ''
    return f'''<section class="cta{" has-vid" if video else ""}">
    {bg}
    <div class="wash wash-b" aria-hidden="true" style="top:10%;right:20%"></div>
    <div class="wash wash-a" aria-hidden="true" style="top:30%;left:20%"></div>
    <div class="wrap">
      <span class="eyebrow">Get started</span>
      <h2 style="margin-top:20px">{e(h2)}</h2>
      <p class="lede" style="margin:22px auto 0">{e(lede)}</p>
      <div class="hero-ctas">
        {demo_btn("Book a 30-min Demo")}
        {second}
      </div>
    </div>
  </section>'''


def ticker(words):
    cells = ''.join(f'<li>{e(w)}</li>' for w in words)
    return f'<section class="kx-ticker" aria-label="{ea(", ".join(words))}"><div class="track"><ul>{cells}</ul><ul aria-hidden="true">{cells}</ul><ul aria-hidden="true">{cells}</ul><ul aria-hidden="true">{cells}</ul></div></section>'


MODULE_LINKS = [('KenSafety', 'kensafety'), ('KenHome', 'kenhome'), ('KenAgri', 'kenagri'), ('KenIoT', 'keniot'), ('KenRobotics', 'kenrobotics'), ('KenVoice', 'kenvoice')]


CLIENTS = [('swarovski', 'Swarovski'), ('giva', 'GIVA'), ('mia', 'Mia by Tanishq'), ('hyou', 'HYOU Fine Jewelry'), ('rado', 'Rado'), ('tissot', 'Tissot'), ('seiko', 'Seiko'), ('caratlane', 'CaratLane'), ('prestige', 'Prestige Group')]


def clients_band(eyebrow='Deployed with retail brands', note='KenVision runs on the existing cameras in their stores.', h2='Trusted where it counts: the shop floor.'):
    from PIL import Image
    tiles = ''
    for i, (slug, name) in enumerate(CLIENTS):
        w, h = Image.open(IMG_DIR / 'clients' / f'{slug}.png').size
        tiles += (f'<li class="cl-t spot t{i}"{rv(i)}><img data-c="{slug}" src="@a/clients/{slug}.png" alt="{ea(name)}" width="{w}" height="{h}" loading="lazy" decoding="async"></li>')
    names = ', '.join(n for _, n in CLIENTS)
    return (f'<section class="block kx-clients" id="clients"><div class="wash wash-a" aria-hidden="true" style="top:10%;left:-8%;opacity:.55"></div><div class="wash wash-b" aria-hidden="true" style="bottom:-10%;right:-6%;opacity:.55"></div>'
            f'<div class="wrap"><div class="cl-head"><span class="eyebrow">{eyebrow}</span><h2>{h2}</h2><p>{note}</p></div>'
            f'<ul class="cl-row" aria-label="Retail brands using KenVision: {names}">{tiles}</ul></div></section>')


def by_intelense():
    mods = ''.join(f'<a href="{INTELENSE}/{k}">{n}</a>' for n, k in MODULE_LINKS)
    return f'''<section class="block" id="by-intelense">
    <div class="wrap">
      <div class="kx-by">
        <div class="wash wash-b" aria-hidden="true" style="top:-30%;right:-10%"></div>
        <div>
          <img class="by-logo" src="@a/logos/intelense-light.png" alt="Intelense" width="194" height="30">
          <span class="eyebrow">KenVision by Intelense</span>
          <h2 style="margin-top:16px">Part of the Intelense platform.</h2>
          <p>Building real-time intelligence systems for video, sensors, and autonomous platforms. KenVision is the business-intelligence module of the <a href="{INTELENSE}/ken360" style="color:var(--lake-blue);font-weight:600">Intelense Ken platform</a>, and it runs alongside the other Ken modules.</p>
          <div class="kx-modules" aria-label="Other Intelense modules">{mods}</div>
        </div>
        <ul class="links">
          <li><a href="{INTELENSE}/"><span>Explore Intelense<small>AI video analytics and intelligence at the edge</small></span></a></li>
          <li><a href="{INTELENSE}/kenvision"><span>KenVision on intelense.com<small>How KenVision fits the wider platform</small></span></a></li>
          <li><a href="{INTELENSE}/ken360"><span>The Ken360 platform<small>One engine behind every module</small></span></a></li>
          <li><a href="{INTELENSE}/about"><span>About Intelense<small>The team, offices and story</small></span></a></li>
        </ul>
      </div>
    </div>
  </section>'''


HOME_STATS = [('99%', 'AI Accuracy', 'Anomaly Detection'), ('10X', 'Scalability', 'Distributed Architecture'), ('+40%', 'ROI Increase', 'Operational Efficiency'),
              ('80%', 'Faster Deployment', 'Cloud-Edge Integration'), ('< 2s', 'Real-Time Latency', 'Low Bandwidth Ready')]


def rv(i=0):
    """Scroll-reveal hook (kv.js adds the .in class; without JS everything is simply visible)."""
    return f' data-r style="--d:{i * 70}ms"'


def stats(items):
    return '<div class="kx-statband">' + ''.join(f'<div{rv(i)}><b data-count>{e(v)}</b><span>{e(l)}</span><small>{e(s)}</small></div>' for i, (v, l, s) in enumerate(items)) + '</div>'


# Overlays for the two slider photos. Drawn from data on a 1280 x 720 canvas, not produced by a model running on the photo (illustrative).
def _t(label, kind, x1, y1, x2, y2, dur=10):
    """A fixed box on a still photo (two identical keyframes so the overlay engine keeps it on screen)."""
    return {'label': label, 'kind': kind, 'k': [[0, x1, y1, x2, y2], [dur, x1, y1, x2, y2]]}


MALL = {'id': 'mall', 'name': 'Shopping mall', 'src': '@a/photos/slider-mall.webp', 'w': 1280, 'h': 720, 'dur': 10, 'hud': [['p', 'People'], ['peak', 'Busiest zone']],
        'alt': 'Shoppers and visitors on escalators and a lounge in a bright shopping mall atrium',
        'tracks': [_t('Visitor', 'p', 378, 516, 446, 686), _t('Visitor', 'p', 706, 563, 842, 694), _t('', 'p', 196, 452, 252, 548), _t('', 'p', 1048, 462, 1104, 568)],
        'zones': [{'label': 'West escalator', 'x': 20, 'y': 290, 'w': 470, 'h': 330, 'base': 12, 'amp': 4, 'ph': 0.0, 'kind': 'b'},
                  {'label': 'Lounge', 'x': 480, 'y': 470, 'w': 430, 'h': 220, 'base': 8, 'amp': 3, 'ph': 1.7, 'kind': 'v'},
                  {'label': 'East escalator', 'x': 840, 'y': 300, 'w': 420, 'h': 330, 'base': 9, 'amp': 3, 'ph': 3.1, 'kind': 'b'}]}
STREET = {'id': 'street', 'name': 'City street', 'src': '@a/photos/slider-street.webp', 'w': 1280, 'h': 720, 'dur': 10, 'hud': [['v', 'Vehicles'], ['peak', 'Busiest zone']],
          'alt': 'Overhead view of a city junction with crosswalks and cars',
          'tracks': [_t('Car', 'v', 718, 76, 760, 124), _t('Car', 'v', 836, 402, 884, 430), _t('Car', 'v', 924, 396, 992, 422), _t('', 'v', 516, 22, 542, 70), _t('', 'v', 514, 74, 540, 120),
                     _t('', 'v', 514, 124, 540, 170), _t('', 'v', 736, 126, 762, 174), _t('', 'v', 146, 438, 208, 464)],
          'zones': [{'label': 'Junction', 'x': 480, 'y': 250, 'w': 330, 'h': 270, 'base': 6, 'amp': 2, 'ph': 0.0, 'kind': 'b'},
                    {'label': 'Northbound lane', 'x': 480, 'y': 10, 'w': 330, 'h': 200, 'base': 14, 'amp': 3, 'ph': 2.0, 'kind': 'v'},
                    {'label': 'East approach', 'x': 840, 'y': 340, 'w': 410, 'h': 150, 'base': 5, 'amp': 2, 'ph': 3.6, 'kind': 'b'}]}


def compare():
    """Before/after slider on real photos. Left of the handle: the plain photo. Right: the same photo with KenVision's overlay drawn on top (see kv.js)."""
    import json as _j
    scenes_ = [MALL, STREET]
    sw = ''.join(f'<button type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}" data-scene="{i}">{sc["name"]}</button>' for i, sc in enumerate(scenes_))
    first = scenes_[0]
    return (f"<div class=\"kx-cmpwrap\"{rv()}><div class=\"kx-seg\" role=\"tablist\" aria-label=\"Demo photos\">{sw}</div>"
            f"<div class=\"kx-compare vid\" data-compare data-scenes='{_j.dumps(scenes_)}'>"
            f'<img class="cv" src="{first["src"]}" width="1600" height="900" alt="{ea(first["alt"])}">'
            '<div class="layer ken"><span class="tint"></span><svg class="ov" viewBox="0 0 1280 720" preserveAspectRatio="xMidYMid slice" aria-hidden="true"></svg>'
            '<div class="hud" aria-hidden="true"></div></div>'
            '<span class="lab l">Camera view</span><span class="lab r">With KenVision</span><span class="handle" aria-hidden="true"></span>'
            '<input class="rng" type="range" min="0" max="100" value="50" aria-label="Compare the camera view with the KenVision view"></div>'
            '</div>')


def points4(points):
    return '<div class="kx-pts">' + ''.join(f'<div{rv(i)}><h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, (t, d) in enumerate(points)) + '</div>'


# One photo per solution, each with its own overlay (illustrative: drawn from data, not a model reading the photo). 1280 x 720 canvas.
def _z(label, x, y, w, h, base, amp, ph, kind='b', pct=False):
    return {'label': label, 'x': x, 'y': y, 'w': w, 'h': h, 'base': base, 'amp': amp, 'ph': ph, 'kind': kind, 'pct': pct}


LIVE = {
    'retail-analytics': dict(photo='retail-aisle', alt='Shoppers browsing a busy supermarket aisle', w=1280, h=720, dur=10, cctv=False,
                             hud=[['p', 'Shoppers in view'], ['peak', 'Busiest zone']],
                             tracks=[_t('Shopper', 'p', 520, 330, 600, 532), _t('', 'p', 436, 348, 480, 472), _t('Staff', 'v', 698, 314, 738, 394), _t('', 'p', 410, 362, 438, 428)],
                             zones=[_z('Sauce aisle', 330, 420, 340, 260, 24, 6, 0.0), _z('Promo display', 740, 430, 270, 240, 31, 7, 2.4, 'v')]),
    'commercial-buildings': dict(photo='building-atrium', alt='Visitors in a multi-level building atrium with lounge seating', w=1280, h=720, dur=10, cctv=False,
                                 hud=[['total', 'Avg. occupancy', '%'], ['peak', 'Busiest area']],
                                 tracks=[_t('Visitor', 'p', 256, 484, 302, 592), _t('', 'p', 910, 560, 960, 664), _t('', 'p', 498, 446, 540, 488), _t('', 'p', 820, 500, 864, 548),
                                         _t('', 'p', 1078, 40, 1112, 138)],
                                 zones=[_z('Level 3 lounge', 700, 40, 430, 210, 38, 8, 0.4, 'v', True), _z('Lounge A', 322, 416, 270, 160, 32, 8, 2.2, 'b', True),
                                        _z('Lounge B', 766, 466, 280, 200, 54, 9, 3.6, 'b', True)]),
    'smart-cities': dict(photo='city-station', alt='Commuters crossing a busy station concourse seen from above', w=1280, h=720, dur=10, cctv=False,
                         hud=[['p', 'People tracked'], ['peak', 'Busiest zone']],
                         tracks=[_t('Person', 'p', 558, 286, 626, 464), _t('', 'p', 628, 258, 726, 432), _t('', 'p', 858, 228, 930, 374), _t('', 'p', 1080, 420, 1188, 628),
                                 _t('', 'p', 370, 410, 450, 586), _t('', 'p', 202, 250, 272, 414), _t('', 'p', 786, 148, 846, 302), _t('', 'p', 96, 432, 182, 604), _t('', 'p', 1016, 150, 1086, 300)],
                         zones=[_z('Platform A', 10, 120, 300, 340, 20, 6, 0.8), _z('Main concourse', 420, 236, 490, 320, 44, 10, 2.6, 'v'), _z('Platform B', 980, 120, 290, 330, 28, 7, 4.0)]),
    'video-surveillance': dict(photo='surveillance-yard', alt='Two workers beside a forklift between racking, seen by a fixed camera from above', w=1280, h=720, dur=10, cctv=True, cam='CAM 04 \u00b7 LOADING BAY',
                               hud=[['neg', 'PPE alerts'], ['v', 'Vehicles'], ['p', 'People']],
                               tracks=[_t('No helmet', 'neg', 812, 266, 978, 472), _t('Person', 'p', 934, 374, 1118, 604), _t('Forklift', 'v', 394, 306, 916, 720)]),
}


def live_block(L, scene=True, cctv=None, extra='', dim=False):
    """A photo with an overlay (scene data), optional CCTV styling and extra HTML on top. The overlay is illustrative."""
    import json as _j
    cctv = L.get('cctv') if cctv is None else cctv
    data = {k: L[k] for k in ('w', 'h', 'dur', 'hud', 'zones', 'tracks') if k in L} if scene else None
    cam = (f'<div class="cam" aria-hidden="true"><span>{L["cam"]}</span><span class="rec"><i></i>REC</span><span class="clk" data-clock></span></div>') if cctv else ''
    attrs = f" data-live data-scene='{_j.dumps(data)}'" if data else ' data-live'
    return (f"<div class=\"kx-live still{' cctv' if cctv else ''}{' dim' if dim else ''}\"{attrs}>"
            f'<div class="stack">{img("assets/photos/" + L["photo"] + ".webp", L["alt"], lazy=False)}<svg class="ov" viewBox="0 0 {L["w"]} {L["h"]}" preserveAspectRatio="xMidYMid slice" aria-hidden="true"></svg></div>'
            f'{cam}<div class="hud" aria-hidden="true"></div>{extra}</div>')


def sol_pic(key, uid, compact=False):
    return live_block(LIVE[key])


def carousel(items):
    """Sector cards with a drawn scene each; scroll or use the arrows."""
    cards = ''.join(f'<a class="cc" href="@{k}"><span class="pic">{sol_pic(k, "c" + k[:3])}</span><h3>{e(t)}</h3><p>{e(p)}</p><span class="go">Learn more</span></a>' for k, t, p in items)
    return (f'<div class="kx-car" data-car{rv()}><div class="track" tabindex="0" aria-label="Solutions">{cards}</div>'
            '<div class="ctl"><button type="button" data-prev aria-label="Previous">←</button><span class="dots" aria-hidden="true"></span><button type="button" data-next aria-label="Next">→</button></div></div>')


def explorer(items):
    """Six capabilities: pick one and the picture changes."""
    pics = [('assets/footage/ken-detect.jpg', 'KenVision camera reading a clothing store, with boxes on customers, staff and a loitering alert', 'Every person detected and classified'),
            ('assets/footage/ken-dwell.jpg', 'Shoppers in a mall store zone with dwell time and visitor figures', 'Dwell time and visitors per zone'),
            ('assets/footage/ken-aisle-heat.jpg', 'Supermarket aisle with a heatmap on the floor showing where shoppers walk', 'Where shoppers walk and stop'),
            ('assets/footage/ken-loiter.jpg', 'Two camera views: a person loitering in a mall and shoplifting detected in a clothing store', 'Loitering and theft flagged'),
            ('DASH', 'KenVision store dashboard with live camera, heatmap and footfall chart', 'Your store at a glance'),
            ('assets/footage/ken-anomaly.jpg', 'KenVision alert for suspicious object concealment in a supermarket aisle', 'Alert with the evidence attached')]
    def _fig(p, i):
        if p[0] == 'DASH':
            return f'<figure class="fx-pic dashfig">{dash()}<figcaption>{e(p[2])}</figcaption></figure>'
        return f'<figure class="fx-pic">{img(p[0], p[1], lazy=i > 0)}<figcaption>{e(p[2])}</figcaption></figure>'
    kinds = [(lambda p=p, i=i: _fig(p, i)) for i, p in enumerate(pics)]
    btns = ''.join(f'<button type="button" role="tab" id="fx-t{i}" aria-controls="fx-p{i}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}"><span class="t">{e(t)}</span><span class="d">{e(d)}</span></button>' for i, (t, d) in enumerate(items))
    panels = ''.join(f'<div class="fx-p{" off" if i else ""}" role="tabpanel" id="fx-p{i}" aria-labelledby="fx-t{i}" data-panel{" aria-hidden=" + chr(34) + "true" + chr(34) if i else ""}>{kinds[i]()}</div>' for i in range(len(items)))
    return f'<div class="kx-tabs fx" data-tabs><div class="tablist" role="tablist" aria-label="Capabilities">{btns}</div><div class="stage">{panels}</div></div>'


def cap_rows(items):
    """Core capabilities as one typographic list: icon, title, text and what it produces. No pictures."""
    outs = [['Events', 'Movement', 'Anomalies'], ['Movement', 'Dwell', 'Interaction'], ['Traffic flow', 'Engagement zones', 'Underused areas'],
            ['Unusual behaviour', 'Abnormal conditions'], ['Dashboards', 'Reports', 'Insights'], ['Right team', 'Right time']]
    ics = ['pulse', 'users', 'zone', 'search', 'chart', 'bell']
    rows_ = ''.join(f'<article class="cap-card"{rv(i)}><span class="ic">{icon(ics[i])}</span><h3>{e(t)}</h3><p>{e(d)}</p>'
                    f'<p class="outs"><span>Gives you</span>{" \u00b7 ".join(outs[i])}</p></article>' for i, (t, d) in enumerate(items))
    return f'<div class="cap-grid">{rows_}</div>'


def rows(items):
    """Sector list: one clean row per solution, picture on the left, arrow on the right."""
    out = ''.join(f'<a class="kx-row" href="@{k}"{rv(i)}><span class="pic">{src if src.lstrip().startswith("<") else img(src, t)}</span><span class="tx"><h3>{e(t)}</h3><p>{e(p)}</p></span><span class="go" aria-hidden="true"></span></a>' for i, (k, src, t, p) in enumerate(items))
    return f'<div class="kx-rows">{out}</div>'


def bento(items):
    """Capability grid: equal cards with a picture on top (3 columns for 6 items, 4 for 8)."""
    out = []
    for i, c in enumerate(items):
        media = f'<div class="media{fits(c["img"]["src"])}">{img(c["img"]["src"], c["img"]["alt"])}</div>' if c.get('img') else ''
        out.append(f'<article class="kx-b spot"{rv(i)}>{media}<div class="body"><h3>{e(c["t"])}</h3><p>{e(c["p"])}</p></div></article>')
    return f'<div class="kx-bentogrid c{4 if len(items) % 4 == 0 else 3}">' + ''.join(out) + '</div>'


def dash():
    """KenVision dashboard drawn in HTML/CSS (sharp at any size, follows the light/dark theme). Figures are sample data."""
    feed = img('assets/retail-ai-view.webp', 'Live camera view with people detected', lazy=False)
    heat = img('assets/images/retail-heatmap-update.webp', 'Store heatmap', lazy=False)
    hours = [34, 46, 41, 58, 72, 92, 70, 54, 64, 80, 57, 40]
    bars = ''.join(f'<i style="--h:{h}%"{" class=pk" if h == 92 else ""}></i>' for h in hours)
    nav = [('Overview', 'chart', ' on'), ('Heatmaps', 'eye', ''), ('Alerts', 'bell', ''), ('Reports', 'text', ''), ('Cameras', 'plug', '')]
    side = ''.join(f'<span class="ni{on}">{icon(ic)}{lb}</span>' for lb, ic, on in nav)
    kp = [('People in', '1,248', 'M0 22 L12 18 L24 20 L36 11 L48 14 L60 5'), ('Avg. dwell', '4m 12s', 'M0 14 L12 16 L24 9 L36 12 L48 8 L60 10'), ('Queue wait', '3 min', 'M0 6 L12 9 L24 8 L36 15 L48 13 L60 19')]
    keys = ['people', 'dwell', 'queue']
    tiles = ''.join(f'<div class="kp"><span>{l}</span><b data-kp="{keys[i]}">{v}</b><svg viewBox="0 0 60 26" aria-hidden="true"><path d="{d}"/></svg></div>' for i, (l, v, d) in enumerate(kp))
    return f'''<div class="kx-dash" data-dash role="img" aria-label="Illustration of the KenVision dashboard with live camera view, heatmap and footfall">
      <div class="dh"><span class="dots"><i></i><i></i><i></i></span><span class="ttl">Store overview</span><span class="smp">Sample data</span><span class="lv"><i></i>Live</span></div>
      <div class="db">
        <div class="ds">{side}</div>
        <div class="dm">
          <div class="kps">{tiles}</div>
          <div class="dr">
            <div class="fd">{feed}<span class="tg"><i></i>CAM-02 · Entrance</span></div>
            <div class="rc">
              <div class="ht">{heat}<span>Heatmap</span></div>
              <div class="hb"><span>Footfall by hour</span><div class="bars" data-bars>{bars}</div></div>
            </div>
          </div>
        </div>
        <div class="toast"><i></i><div><b>Queue alert</b><small>Checkout 2 · long wait</small></div></div>
      </div>
    </div>'''


def screens():
    """Four small UI scenes, one per tab of 'Cameras are everywhere'."""
    feed = img('assets/retail-ai-view.webp', 'Live camera view', lazy=False)
    heat = img('assets/images/retail-heatmap-update.webp', 'Heatmap')
    s0 = f'<div class="scr s0"><div class="fd">{feed}<span class="tg"><i></i>LIVE · CAM-02 Entrance</span><span class="ch c1">People counting</span><span class="ch c2">Dwell time</span></div></div>'
    al = [('neg', 'Queue building', 'Checkout 2 · Camera 04', 'now'), ('warn', 'Zone 3 over capacity', 'Ground floor · Camera 11', '2 min'), ('info', 'Unusual movement', 'Display case · Camera 07', '9 min')]
    s1 = '<div class="scr s1"><span class="st">Alerts</span>' + ''.join(f'<div class="al {c}"{" data-new" if i == 0 else ""}><i></i><div><b>{t}</b><small>{m}</small></div><em>{w}</em></div>' for i, (c, t, m, w) in enumerate(al)) + '</div>'
    stp = ['Event detected on camera', 'Right team notified', 'Action taken on site', 'Logged for review']
    s2 = '<div class="scr s2"><span class="st">Response</span><ol>' + ''.join(f'<li style="--i:{i}"><i></i>{t}</li>' for i, t in enumerate(stp)) + '</ol><span class="lat">Alert in &lt; 2s</span></div>'
    bars = ''.join(f'<i style="--h:{h}%"{" class=pk" if h == 92 else ""}></i>' for h in [34, 46, 41, 58, 72, 92, 70, 54, 64, 80, 57, 40])
    s3 = f'<div class="scr s3"><span class="st">Insights</span><div class="g"><div class="hb"><span>Footfall by hour</span><div class="bars" data-bars>{bars}</div></div><div class="ht">{heat}<span>Heatmap</span></div></div></div>'
    return s0 + s1 + s2 + s3


def tabs_standard(points):
    """The four ideas of 'Cameras are everywhere' as tabs that cycle by themselves, each with its own scene."""
    btns = ''.join(f'<button type="button" role="tab" id="std-t{i}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}"><span class="t">{e(t)}</span><span class="d">{e(d)}</span><i class="bar" aria-hidden="true"></i></button>' for i, (t, d) in enumerate(points))
    return f'''<div class="kx-tabs std" data-tabs data-auto data-i="0">
        <div class="tablist" role="tablist" aria-label="What KenVision does">{btns}</div>
        <div class="stage"><div class="frame kx-screens"><span class="pill" data-label></span>{screens()}</div></div>
      </div>'''


DEPLOY_FACTS = {'Edge': ('Lowest latency · Works offline', ['Cameras', 'Edge device', 'Dashboards & alerts']),
                'On-Premise': ('Raw footage never leaves the building', ['Cameras', 'Your data centre', 'Dashboards & alerts']),
                'Cloud': ('Add cameras and locations instantly', ['Cameras', 'Cloud', 'Dashboards & alerts']),
                'Hybrid': ('One platform, mixed architecture', ['Cameras', 'Edge or on-prem + cloud', 'Dashboards & alerts'])}


def tabs_deploy(items):
    btns = ''.join(f'<button type="button" role="tab" id="dep-t{i}" aria-controls="dep-p{i}" aria-selected="{"true" if i == 0 else "false"}" tabindex="{0 if i == 0 else -1}"><b>{n}</b>{e(t)}</button>' for i, (n, t, d) in enumerate(items))
    panels = ''
    for i, (n, t, d) in enumerate(items):
        badge, nodes = DEPLOY_FACTS[t]
        ns = ''.join(f'<span class="dn{" mid" if k == 1 else ""}">{x}</span>' + ('<i class="dl" aria-hidden="true"></i>' if k < 2 else '') for k, x in enumerate(nodes))
        panels += f'''<div class="panel-d{" off" if i else ""}" role="tabpanel" id="dep-p{i}" aria-labelledby="dep-t{i}" data-panel{' aria-hidden="true"' if i else ''}>
          <div class="txt"><span class="kx-num">{n}</span><h3>{e(t)}</h3><p>{e(d)}</p><span class="badge">{badge}</span></div>
          <div class="dg" aria-hidden="true">{ns}</div>
        </div>'''
    return f'<div class="kx-tabs dep" data-tabs><div class="tablist seg" role="tablist" aria-label="Deployment models">{btns}</div><div class="panels">{panels}</div></div>'


def how_s(items):
    """'How it works' as a scroll-linked pipeline: the line fills as you scroll and lights each step in turn.
    Step 1: sources feeding live streams. Step 2: a camera carrying the KenVision logo. Step 3: the dashboard."""
    # three different Pexels photos: capture, processing, outputs. Boxes and cards are illustrative (drawn here, not read by a model)
    pic = lambda n, alt: img(f'assets/photos/{n}.webp', alt, lazy=True)

    def box(x, y, w, h, label, cls='p'):
        tw = 26 + len(label) * 12.6
        return (f'<g class="bx {cls}"><rect class="r" x="{x}" y="{y}" width="{w}" height="{h}" rx="8"/><rect class="t" x="{x}" y="{y - 36}" width="{tw:.0f}" height="34" rx="14"/>'
                f'<text x="{x + 13}" y="{y - 12}">{label}</text></g>')
    boxes = box(360, 70, 240, 640, 'Shopper', 'p') + box(862, 130, 230, 520, 'Dwell 42 s', 'p') + box(1156, 264, 82, 156, 'Staff', 'v')

    def still(photo, alt, svg='', cctv=False, dim=False, extra='', cam='CAM 07 \u00b7 MAIN ST'):
        cam_ = f'<div class="cam" aria-hidden="true"><span>{cam}</span><span class="rec"><i></i>REC</span><span class="clk" data-clock></span></div>' if cctv else ''
        return (f'<div class="kx-live still{" cctv" if cctv else ""}{" dim" if dim else ""}"{" data-live" if cctv else ""}><div class="stack">{pic(photo, alt)}'
                f'<svg class="ov" viewBox="0 0 1280 720" preserveAspectRatio="xMidYMid slice" aria-hidden="true">{svg}</svg></div>{cam_}{extra}</div>')
    v1 = still('how-feed', 'Pedestrians walking along a shopping street, the view an existing camera captures', cctv=True, extra='<span class="kx-chip-live"><i></i>Live stream from an existing camera</span>')
    v2 = still('how-read', 'Two shoppers browsing clothing rails in a boutique, with detection boxes drawn over them', svg=boxes,
               extra='<span class="kx-chip-ken"><img src="@a/logos/kenvision.png" alt="KenVision" width="86" height="32"><b>Reading every frame</b></span>')
    notes = ('<div class="kx-notes"><div class="nt neg"><i></i><div><b>Shopper waiting for help</b><small>Womenswear \u00b7 CAM 03 \u00b7 just now</small></div></div>'
             '<div class="nt"><i></i><div><b>Womenswear busier than usual</b><small>Ground floor \u00b7 CAM 03 \u00b7 4 min ago</small></div></div>'
             '<span class="sent">Sent to the store manager</span></div>')
    v3 = still('how-dash', 'A laptop showing an analytics dashboard with charts', dim=True, extra=notes)
    vis = [v1, v2, v3]
    lis = ''.join(f'<li{rv(i)}><span class="dot"></span><div class="vis v{i + 1}">{vis[i]}</div><h3>{e(s["t"])}</h3><p>{e(s["p"])}</p></li>' for i, s in enumerate(items))
    return f'<div class="kx-how" data-how><div class="track" aria-hidden="true"><i class="fill"></i></div><ol class="stp">{lis}</ol></div>'


def mini_cards(items, cols=4, icons=None):
    icons = icons or ['layers', 'filter', 'bolt', 'plug', 'chart']
    return f'<div class="kx-grid c{cols}">' + ''.join(f'<div class="kx-mini spot"{rv(i)}><span class="ic">{icon(icons[i % len(icons)])}</span><h3>{e(x["t"])}</h3><p>{e(x["p"])}</p></div>' for i, x in enumerate(items)) + '</div>'


def why_panel(eyebrow, h2, items):
    cells = ''.join(f'<div class="cell"{rv(i)}>{icon(ic)}<h3>{e(t)}</h3><p>{e(d)}</p></div>' for i, (ic, t, d) in enumerate(items))
    return f'''<section class="block" id="why"><div class="wrap"><div class="kx-dark">
        <div class="wash wash-b" aria-hidden="true" style="top:-30%;right:-8%;opacity:.55"></div>
        <span class="eyebrow">{eyebrow}</span><h2>{h2}</h2>
        <div class="cells n{len(items)}">{cells}</div>
      </div></div></section>'''


def issues(items):
    ic = ['eye', 'clock', 'filter', 'layers']
    return '<div class="kx-issues">' + ''.join(f'<div class="kx-issue"{rv(i)}><span class="ic">{icon(ic[i % 4])}</span><h3>{e(x["t"])}</h3><p>{e(x["p"])}</p></div>' for i, x in enumerate(items)) + '</div>'


def outcomes(items):
    return '<div class="kx-outcomes">' + ''.join(f'<div{rv(i)}><span class="tick" aria-hidden="true"></span><h3>{e(x["t"])}</h3><p>{e(x["p"])}</p></div>' for i, x in enumerate(items)) + '</div>'


# ---------------------------------------------------------------- JSON-LD

def norm_ld(o):
    s = json.dumps(o, ensure_ascii=False)
    s = s.replace('https://kenvision.ai/index.html', 'https://kenvision.ai/').replace('https://kenvision.ai/solutions/index.html', 'https://kenvision.ai/solutions/')
    s = s.replace('"https://intelense.com"', f'"{INTELENSE}/"')
    return json.loads(s)


INTELENSE_ORG = {'@type': 'Organization', 'name': 'Intelense', 'legalName': 'Intelense Inc.', 'url': INTELENSE + '/', 'sameAs': [LINKEDIN, XURL]}


def patch_ld(key, ld):
    ld = norm_ld(ld)
    t = ld.get('@type')
    if key == 'home' and t == 'Organization':
        ld.update({'alternateName': 'KenVision by Intelense', 'parentOrganization': INTELENSE_ORG, 'sameAs': [INTELENSE + '/kenvision', LINKEDIN, XURL]})
    if key == 'home' and t == 'WebSite':
        ld.pop('potentialAction', None)  # the old data pointed to a /search page this site does not have
        ld['alternateName'] = 'KenVision by Intelense'
    if key == 'home' and t == 'SoftwareApplication':
        ld.update({'alternateName': 'KenVision by Intelense', 'provider': INTELENSE_ORG, 'publisher': INTELENSE_ORG, 'sameAs': [INTELENSE + '/kenvision']})
    if t == 'Product' and 'brand' in ld:
        ld['brand'] = {'@type': 'Brand', 'name': 'KenVision', 'url': SITE_URL + '/'}
        ld['manufacturer'] = INTELENSE_ORG
    return ld


# ---------------------------------------------------------------- pages

def page_home():
    c = CONTENT['home']
    floats = ('<span class="kx-float f1"><i></i>People counting</span><span class="kx-float f2"><i></i>Heatmaps</span><span class="kx-float f3"><i></i>Smart alerts</span>')
    h = hero('', '<span class="kx-byline">KenVision by <a href="' + INTELENSE + '/">Intelense</a></span>',
             'Turn the cameras you <em>already own</em> into real-time intelligence.',
             'KenVision applies advanced AI to your existing CCTV — counting people, mapping behaviour, spotting risk and measuring engagement — without replacing a single camera. Privacy-first, on-prem or edge, running in days.',
             demo_btn() + '<a class="btn btn-ghost" href="@solutions">See solutions</a>',
             center=True, below='<div class="kx-stage" data-tilt><div class="kx-shot">' + dash() + '</div>' + floats + '</div>',
             extra='<div class="kx-trust"><span>Works with existing CCTV</span><span>Privacy-first &amp; on-prem</span><span>Camera-agnostic</span></div>')
    st = f'<section class="kx-proof"><div class="wrap">{stats(HOME_STATS)}</div></section>'
    sectors = ['Electronics retail', 'Jewellery chains', 'FMCG activations', 'Commercial buildings', 'Smart cities', 'Worksite safety']
    strip = ticker(sectors).replace('<section class="kx-ticker"', '<section class="kx-ticker lbl"', 1).replace('<div class="track">', '<span class="lead">Reading existing cameras across</span><div class="track">', 1)
    partners = [('oce', 'OCE'), ('prestige', 'Prestige Group'), ('risingstar', 'RisingStar'), ('google-cloud', 'Google Cloud'), ('aws', 'AWS'), ('nvidia', 'NVIDIA'), ('mars', 'MaRS'), ('ibm', 'IBM'), ('f6s', 'F6S')]
    cells = ''.join(f'<li>{img(f"assets/images/partners/{s}.webp", n, lazy=False)}</li>' for s, n in partners)
    band = f'''<section class="block kx-partners" id="partners" style="padding-block:clamp(32px,4vw,56px)">
    <div class="wrap">
      <ul class="kx-logos" aria-label="Partners and programs: {", ".join(n for _, n in partners)}">{cells}</ul>
    </div>
  </section>'''
    pts = [('Real-Time Video Analysis', 'Cameras don’t just record. KenVision continuously analyzes live video streams to understand activity as it happens.'),
           ('Automated Detection & Alerts', 'Eliminate manual footage review. KenVision detects events instantly and notifies teams in real time.'),
           ('Instant Response Enablement', 'Identify incidents the moment they occur and act within seconds—not hours.'),
           ('Actionable Intelligence', 'Transform raw video into structured insights that support faster, smarter decision-making.')]
    standard = block(head_block('The KenVision standard', 'Cameras Are Everywhere. <em>Intelligence Is Not.</em>', '') + compare() + points4(pts), 'standard')
    sec = [('retail-analytics', '', 'Retail Analytics', 'Optimize store performance using footfall, dwell time, heatmaps, and shopper behavior insights.', 'a'),
           ('commercial-buildings', '', 'Commercial Buildings', 'Understand occupancy, space utilization, access patterns, and asset movement.', 'b'),
           ('smart-cities', '', 'Smart Cities', 'Monitor crowds, traffic flow, and public safety conditions in real time.', 'b'),
           ('video-surveillance', '', 'Video Surveillance', 'Enhance surveillance systems with intelligent detection, alerts, and analytics.', 'a')]
    sectors_html = block(head_block('Solutions', 'Intelligence Across Sectors', 'KenVision adapts to different environments by contextualizing intelligence for each industry.')
                         + carousel([(k, t, p) for k, i, t, p, cl in sec]), 'sectors')
    steps_html = block(head_block('How it works', 'How KenVision Turns Video into Action', '')
                       + how_s(CONTENT['retail-analytics']['steps']), 'how')
    core = [('Real-Time Video Analytics', 'Detect events, movement, and anomalies as they happen — not after review.', 'assets/images/core-analytics.webp'),
            ('Behavior & Pattern Analysis', 'Understand how people and objects move, dwell, and interact within spaces.', 'https://images.unsplash.com/photo-1460925895917-afdab827c52f'),
            ('Heatmaps & Movement Tracking', 'Visualize traffic flow, engagement zones, and underutilized areas.', 'assets/images/retail-heatmap-update.webp'),
            ('Anomaly Detection', 'Identify unusual behavior or conditions that deviate from normal patterns.', 'https://images.unsplash.com/photo-1563986768609'),
            ('Dashboards & Reports', 'Clean, visual dashboards that turn complex video data into insights teams can act on.', 'https://images.unsplash.com/photo-1551288049'),
            ('Smart Alerts', 'Automated notifications ensure the right teams are informed at the right time.', 'assets/images/core-alerts.webp')]
    core_html = block(head_block('Platform', 'Core Capabilities', '') + cap_rows([(t, p) for t, p, i in core]), 'capabilities')
    why = [('layers', 'Existing Infrastructure', 'Deploy using current systems without replacement.'), ('bolt', 'Fast Deployment', 'Operational within days, not months.'),
           ('chart', 'Scalable by Design', 'From single locations to city-wide scale.'), ('filter', 'Privacy-First', 'On-premise processing options for data sovereignty.'),
           ('patrol', 'Enterprise-Ready', 'Built for reliability and long-term security.')]
    why_html = why_panel('Why KenVision', 'Why Organizations Choose KenVision', why)
    dep = [('01', 'Edge', 'AI runs directly on a device at your site. Lowest latency, works offline, ideal where bandwidth is constrained or privacy is paramount.'),
           ('02', 'On-Premise', 'Full processing inside your data centre. Raw footage never leaves the building — the right choice for regulated industries and data-sovereignty requirements.'),
           ('03', 'Cloud', 'Elastic, multi-site scale with no on-site servers. Add cameras and locations instantly, and let infrastructure grow with your rollout.'),
           ('04', 'Hybrid', 'Edge or on-prem for sensitive streams, cloud for aggregation and reporting. One platform, mixed architecture — no compromise on privacy or scale.')]
    dep_html = block(head_block('Deployment', 'Deploy KenVision Your Way', '') + tabs_deploy(dep), 'deploy')
    quote = f'''<section class="block kx-pq" id="principle"><div class="wrap"><figure class="pq"{rv()}>
        <div class="wash wash-a" aria-hidden="true"></div><div class="wash wash-b" aria-hidden="true"></div>
        <div class="side"><span class="eyebrow">Product principle</span>
          <div class="pflow" aria-hidden="true"><span class="chip">{icon("eye")}Already on your wall</span><i class="arrow"></i><span class="chip on">KenVision software</span></div></div>
        <div class="body"><blockquote><p>\u201cThe best camera for your AI is the one <b>already on your wall</b>. Everything after that should be <b>software</b> \u2014 not another hardware project.\u201d</p></blockquote>
        <figcaption><img class="on-light" src="@a/logos/intelense.png" alt="" width="97" height="15"><span>KenVision product principle, by <a href="{INTELENSE}/">Intelense</a></span></figcaption></div>
      </figure></div></section>'''
    faq = faq_block([(x['q'], x['a']) for x in c['faq']], c['faq_h']['h'], c['faq_h']['p'])
    cta = cta_band('Ready to Unlock Intelligence from Video?', 'See how KenVision transforms everyday video into insights that improve safety, efficiency, and decision-making.')
    body = '\n\n  '.join([h, st, clients_band(), strip, standard, sectors_html, steps_html, core_html, why_html, dep_html, by_intelense(), quote, faq, cta])
    return page('index', 'index.html', 'KenVision by Intelense | AI-Powered Video Intelligence Platform', c['meta'], body, 'home')


def page_solutions():
    c = CONTENT['solutions-index']
    h = hero(crumbs((None, 'Solutions')), '<span class="eyebrow">Solutions</span>', c['h1'], c['lede'], demo_btn('Request Demo'),
             media='<div class="kx-stage" data-tilt><figure class="kx-shot round">' + img('assets/images/solutions-hero-collage.webp', c['hero_img']['alt'], lazy=False, prio=True) + '</figure></div>')
    cards = [('retail-analytics', '', 'Retail Analytics', 'Understand shopper behavior using footfall analysis and heatmaps.', 'a'),
             ('commercial-buildings', '', 'Commercial Buildings', 'Gain real-time visibility into occupancy and space utilization.', 'b'),
             ('smart-cities', '', 'Smart Cities', 'Monitor traffic flow and public safety at city-wide scale.', 'b'),
             ('video-surveillance', '', 'Intelligent Surveillance', 'Enhance existing systems with real-time detection and alerts.', 'a')]
    sec = block(head_block('Solutions', 'Intelligence Across Sectors', '') + rows([(k, sol_pic(k, 'r' + k[:3]), t, p) for k, i, t, p, cl in cards]), 'sectors')
    tick = ticker(['Real-time video analytics', 'Behavioral understanding', 'Anomaly detection', 'Heatmaps & tracking', 'Dashboards & reports', 'Edge + cloud deployment'])
    onep = f'<section class="block" style="padding-block:clamp(40px,5vw,72px)"><div class="wrap"><h2 class="kx-h2"{rv()} style="font-size:clamp(24px,3vw,36px)">One Platform. Multiple Solutions.</h2></div></section>'
    scale = [('Single Site', 'Deploy KenVision in individual locations with focused intelligence and minimal setup.'), ('Multi-Location', 'Scale insights across multiple sites with centralized dashboards and unified reporting.'),
             ('Enterprise Scale', 'Unify intelligence across large, distributed environments with city-wide AI orchestration.')]
    dep = [('Edge Processing', 'Low latency intelligence processed directly where your cameras are located.'), ('On-Premise', 'Deploy on your own infrastructure for maximum data control and military-grade security.'),
           ('Cloud & Hybrid', 'Scale infinitely with flexible cloud models tailored to your global enterprise needs.')]
    ladder = '<ol class="kx-ladder">' + ''.join(f'<li{rv(i)} style="--s:{i + 1}"><h3>{e(t)}</h3><p>{e(p)}</p></li>' for i, (t, p) in enumerate(scale)) + '</ol>'
    sc = block(head_block('Scale', 'Scalability &amp; Deployment', '') + ladder + mini_cards([{'t': t, 'p': p} for t, p in dep], 3, ['bolt', 'patrol', 'layers']), 'scale')
    cta = cta_band('Find the Right Solution for Your Environment', 'Tell us about your cameras and sites and we will point you to the right starting point.')
    cta = cta.replace('Book a 30-min Demo', 'Talk to an Expert')
    body = '\n\n  '.join([h, sec, onep, tick, sc, by_intelense(), cta])
    return page('solutions', 'solutions/index.html', c['meta']['title'], c['meta'], body, 'solutions', depth=1)


# panels for the "in the field" / "why it matters" block
def vis(caption):
    def bar(label, w, style=''):
        return f'<div class="kx-bar"><span>{label}</span><i style="--w:{w}%;{style}"></i></div>'
    if caption == 'Shopper funnel':
        rows = [('Footfall: entered store', 100), ('Engaged a zone', 72), ('High dwell', 46), ('Converted', 24)]
        return '<div class="kx-vis" data-r role="img" aria-label="Shopper funnel: entered store, engaged a zone, high dwell, converted"><span class="cap-t">Shopper funnel</span>' + ''.join(bar(l, w) for l, w in rows) + '</div>'
    if caption == 'Occupancy-driven energy':
        return ('<div class="kx-vis" data-r><span class="cap-t">Occupancy-driven energy</span><ul class="kx-flow"><li>Cameras · live occupancy</li><li>KenVision · occupancy API</li><li>BMS / HVAC · setpoints</li><li class="on">Conditioning only occupied zones</li></ul>'
                + bar('Always-on', 100, 'background:var(--ash)') + bar('Occupancy-led', 58) + '<span class="kx-save">↓ less wasted energy</span></div>')
    if caption == 'From signal to standard response':
        return ('<div class="kx-vis" data-r><span class="cap-t">From signal to standard response</span><ul class="kx-flow"><li class="on">Detection · suspicious behaviour at display case</li><li>Alert nearest trained staff (camera + zone)</li><li>Approach, assist, observe per SOP</li><li>Escalate &amp; log if risk persists</li></ul></div>')
    if caption == 'Crowd density over time':
        return ('<div class="kx-vis" data-r role="img" aria-label="Crowd density over time with an alert threshold"><span class="cap-t">Crowd density over time</span>'
                '<svg viewBox="0 0 400 190" aria-hidden="true"><line class="axis" x1="30" y1="160" x2="390" y2="160"/><line class="axis" x1="30" y1="20" x2="30" y2="160"/>'
                '<line class="thr" x1="30" y1="52" x2="390" y2="52"/><text x="34" y="46">alert threshold</text>'
                '<path class="area" d="M30 150 C70 146 90 140 120 128 S170 96 200 84 S250 50 280 62 S340 110 390 124 L390 160 L30 160 Z"/>'
                '<text x="30" y="178">time</text></svg></div>')
    return ''


SOL_MEDIA = {
    'retail-analytics': dict(chips=['Footfall', 'Dwell time'], scale=('scale-retail', 'Shoppers and storefronts on a busy retail street', 'Every store, one view')),
    'commercial-buildings': dict(chips=['Occupancy', 'Utilization'], scale=('scale-building', 'Glass office tower rising into a bright sky', 'Whole portfolios, one view')),
    'smart-cities': dict(chips=['Crowd density', 'Flow'], scale=('scale-city', 'Aerial view of city blocks, a parking lot and the roads around them', 'City-wide, one platform')),
    'video-surveillance': dict(chips=['Smart alerts', 'PPE check'], scale=('scale-yard', 'Aerial view of rows of trucks and trailers in a logistics yard', 'Every site, one console')),
}


def page_solution(key):
    c = CONTENT[key]
    name = dict((k, n) for k, n, _ in SOLUTIONS)[key]
    hm = SOL_MEDIA[key]
    pic = sol_pic(key, 'h')
    chips = ''.join(f'<span class="kx-float f{i + 1}"><i></i>{t}</span>' for i, t in enumerate(hm['chips']))
    h = hero(crumbs(('@solutions', 'Solutions'), (None, name)), '<span class="eyebrow">Solutions</span>', e(c['h1']), e(c['lede']), demo_btn('Request Demo'),
             media='<div class="kx-stage" data-tilt><figure class="kx-shot round">' + pic + '</figure>' + chips + '</div>')
    pain = block(f'''<div class="kx-side"><div class="sticky"><span class="eyebrow">The challenge</span><h2 style="margin-top:18px">{e(c['pain']['h'])}</h2></div>{issues(c['pain']['items'])}</div>''', 'challenge')
    how = block(head_block('How it works', e(c['how_h']), '') + how_s(c['steps']), 'how')
    core_h = f'{c["core"]["h"]} {c["core"]["h2b"][0]}' if c['core']['h2b'] else c['core']['h']
    core = block(head_block('Capabilities', e(core_h), '') + mini_cards(c['core']['items'], 4 if len(c['core']['items']) % 4 == 0 else 3, ['eye', 'pulse', 'gauge', 'bell', 'chart', 'layers', 'search', 'timeline']), 'capabilities')
    impact = block(head_block('Impact', e(c['impact']['h']), '') + outcomes(c['impact']['items']), 'impact')
    ticks = ''.join(f"<li><span>{re.sub(r'^([^:]+:)', r'<strong>\1</strong>', e(x))}</span></li>" for x in c['scale']['li'])
    scale = block(f'''<div class="kx-split"><div{rv()}><span class="eyebrow">Scale</span><h2 style="margin-top:18px">{e(c['scale']['h'])}</h2>
        <ul class="kx-ticks">{ticks}</ul></div>
        <div class="kx-frame"{rv(2)}>{img('assets/photos/' + hm['scale'][0] + '.webp', hm['scale'][1], 'photo')}<span class="kx-chip-live"><i></i>{hm['scale'][2]}</span></div></div>''', 'scale')
    f = c['field']

    def lead(li):
        t = li.lstrip('✓').strip()
        m = re.match(r'^(.{3,60}?[.:])\s+(.*)$', t)
        return f'<li><span><strong>{e(m.group(1))}</strong> {e(m.group(2))}</span></li>' if m else f'<li><span>{e(t)}</span></li>'
    field = block(f'''<div class="kx-split flip"><div{rv()}><span class="eyebrow">{e(f['eyebrow'])}</span><h2 style="margin-top:18px">{e(f['h'])}</h2><p class="lede" style="margin-top:18px">{e(f['lede'])}</p>
        <ul class="kx-ticks">{"".join(lead(x) for x in f['li'])}</ul></div>
        {vis(f['caption'])}</div>''', 'field')
    strip_words = {'retail-analytics': ['Existing CCTV', 'Edge/On-Prem/Cloud', 'Privacy-First'], 'commercial-buildings': ['Existing CCTV', 'Flexible Deploy', 'Privacy-First'],
                   'smart-cities': ['Existing Networks', 'Hybrid Deployment', 'Privacy-First'], 'video-surveillance': ['Existing CCTV', 'Edge/Cloud Hybrid', 'Privacy-First']}[key]
    why = block(head_block('Why KenVision', e(c['why']['h']), '') + mini_cards(c['why']['items'], 4), 'why')
    faq = faq_block([(x['q'], x['a']) for x in c['faq']], c['faq_h']['h'], c['faq_h']['p'])
    cta = cta_band(c['cta']['h'], c['cta']['p'])
    body = '\n\n  '.join(x for x in [h, pain, how, core, impact, scale, field, ticker(strip_words), why, faq, by_intelense(), cta] if x)
    return page(key, f'solutions/{key}.html', c['meta']['title'], c['meta'], body, key, depth=1)


def page_company():
    c = CONTENT['company']
    h = hero(crumbs((None, 'Company')), '<span class="kx-byline">KenVision by <a href="' + INTELENSE + '/about">Intelense</a></span>', 'The cameras you already own can do more',
             'KenVision is the AI video intelligence layer built by <a href="' + INTELENSE + '/" style="color:var(--lake-blue);font-weight:600">Intelense</a> that turns existing CCTV into real-time insight — footfall, occupancy, crowd safety and loss prevention — without new hardware and without storing raw footage.',
             demo_btn() + f'<a class="btn btn-ghost" href="{INTELENSE}/">Explore Intelense</a>',
             media='<div class="kx-stage" data-tilt><div class="kx-shot">' + dash() + '</div></div>')
    cog = block(f'''<div class="kx-split"><div><span class="eyebrow">KEN AI</span><h2 style="margin-top:18px">Cognitive Intelligence</h2>
        <p class="lede" style="margin-top:18px">We build device-agnostic AI platforms that make existing camera networks intelligent. Our core technology, KEN AI, processes video feeds in real-time to detect threats, anomalies, and safety hazards without requiring new infrastructure.</p>
        <div class="kx-chips"><span>Privacy-First Design</span><span>No Hardware Upgrades</span><span>Seamless Integration</span></div></div>
        <div class="kx-frame"{rv(2)}>{img('assets/retail-ai-view.webp', 'KEN AI detecting people in a live camera feed', 'photo')}</div></div>''', 'cognitive')
    st = block(stats([HOME_STATS[2], HOME_STATS[3], HOME_STATS[4], HOME_STATS[0], HOME_STATS[1]]), 'numbers')
    st = st.replace('class="block"', 'class="block" style="padding-block:clamp(40px,5vw,72px)"', 1)
    glob = block(head_block('Global Operations', 'Two offices, one team.', 'KenVision is built by Intelense in Canada and India.') + world_map() + '<div class="offices">' + ''.join(
        f'''<article class="office" data-pin="{o['pin']}" tabindex="0"><h3>{"Headquarters" if o["pin"] == "ca" else "Innovation Hub"}</h3><p>{o['city']}</p><p>{o['addr']}</p></article>''' for o in OFFICES) + '</div>', 'offices')
    cta = cta_band('See what your cameras already know', "Book a 30-minute demo and we'll walk through the use cases that matter most for your sites — and how fast you can stand them up.",
                   '<a class="btn btn-black" href="@contact">Contact Sales</a>')
    body = '\n\n  '.join([h, cog, st, glob, by_intelense(), cta])
    return page('company', 'company.html', 'Company | KenVision - About Intelense', c['meta'], body, 'company')


def page_contact():
    c = CONTENT['contact']
    h = hero(crumbs((None, 'Contact')), '<span class="eyebrow">Get in touch</span>', "Let's talk about your cameras",
             'Book a 30-minute demo and we\'ll show KenVision running on cameras like yours — or send us a message and we\'ll get back within one business day.',
             '<a class="btn btn-blue" href="#form">Send an enquiry</a>' + (f'<a class="btn btn-ghost" href="{CALENDLY_URL}" target="_blank" rel="noopener">Book a 30-min demo</a>' if CALENDLY_URL else ''), center=True)
    opts = ''.join(f'<option>{o}</option>' for o in ['Retail analytics', 'Commercial buildings / occupancy', 'Smart cities / traffic', 'Safety & security', 'Something else'])
    book = ''
    if CALENDLY_URL:
        book = f'''<div class="panel kx-book"><h2 style="font-size:28px">Book a 30-min demo</h2><p>Pick a slot and we'll show footfall, occupancy or safety analytics running live on cameras like yours — tailored to your use case.</p>
        <a class="btn btn-blue" href="{CALENDLY_URL}" target="_blank" rel="noopener">Choose a time</a></div>'''
    form = f'''<section class="block" id="form">
    <div class="wrap contact-grid">
      <div style="display:grid;gap:24px;align-content:start">
      {book}
      <div class="panel">
        <h2 style="font-size:28px;margin-bottom:6px">Send an enquiry</h2>
        <p style="color:var(--graphite);margin:0 0 24px">Not ready to book? Tell us about your setup and we'll come back with the right starting point.</p>
        <form class="form" id="demo-form" novalidate aria-label="Contact form">
          <div class="field"><label for="f-first">First name <span class="req">*</span></label><input id="f-first" name="first_name" autocomplete="given-name" required></div>
          <div class="field"><label for="f-last">Last name <span class="req">*</span></label><input id="f-last" name="last_name" autocomplete="family-name" required></div>
          <div class="field full"><label for="f-email">Work email <span class="req">*</span></label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
          <div class="field"><label for="f-company">Company</label><input id="f-company" name="company" autocomplete="organization"></div>
          <div class="field"><label for="f-interest">I'm interested in</label><select id="f-interest" name="interest"><option value="">— select a use case —</option>{opts}</select></div>
          <div class="field full"><label for="f-msg">Message <span class="req">*</span></label><textarea id="f-msg" name="message" required></textarea></div>
          <input type="text" name="_honey" value="" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0">
          <div class="full" style="display:flex;gap:16px;align-items:center;flex-wrap:wrap"><button class="btn btn-blue" type="submit">Send message</button><span class="form-note" id="form-status" role="status" aria-live="polite"></span></div>
          <p class="form-note full">By submitting, you agree to the <a href="{INTELENSE}/privacy">Intelense Privacy Policy</a>. We never share your data.</p>
        </form>
        <div class="form-done" id="form-done" hidden tabindex="-1">
          <h3>Thanks, we have your message.</h3>
          <p>Our team will reply to you within one business day.</p>
          <p style="margin-top:18px"><a class="link-arrow" href="@solutions">Explore KenVision solutions while you wait</a></p>
        </div>
      </div>
      </div>
      <aside class="panel">
        <ul class="info-list">
          <li><span>Email</span><b class="email">enquiries@intelense.ca</b><b class="email">dinesh@intelense.com</b></li>
          <li><span>Phone</span><b><a href="tel:+12895523165">+1 (289) 552-3165</a> <small>Canada</small></b><b><a href="tel:+919342810422">+91 93428 10422</a> <small>India</small></b></li>
          <li><span>Offices</span><b>{OFFICES[0]['addr']}</b><b>{OFFICES[1]['addr']}</b></li>
          <li><span>Response time</span><b>Within one business day</b></li>
        </ul>
        <p style="margin-top:24px;color:var(--graphite)">KenVision is a product of <a href="{INTELENSE}/" style="color:var(--lake-blue);font-weight:600">Intelense</a>. For the wider platform, see <a href="{INTELENSE}/contact" style="color:var(--lake-blue);font-weight:600">Intelense contact</a>.</p>
      </aside>
    </div>
  </section>'''
    body = '\n\n  '.join([h, form])
    return page('contact', 'contact.html', 'Contact | KenVision AI Video Intelligence', c['meta'], body, 'contact')


def page_404():
    body = f'''<section class="kx-404"><div class="wrap"><div class="big">404</div><h1>Page Not Found</h1><p>The page you're looking for doesn't exist or has been moved.</p>
    <div class="hero-ctas"><a class="btn btn-blue" href="@index">Back to Home</a><a class="btn btn-ghost" href="@solutions">See solutions</a></div></div></section>'''
    return page('404', '404.html', 'Page Not Found | KenVision', CONTENT['404']['meta'], body, '404', noindex=True)


def page(key, file, title, meta, body, active, depth=0, noindex=False):
    return dict(key=key, file=file, title=title, meta=meta, body=body, active=active, depth=depth, noindex=noindex)


# ---------------------------------------------------------------- render

def canonical(p):
    return SITE_URL + (LINKS[p['key']][1] if p['key'] in LINKS else '/')


def head(p):
    m = p['meta']
    desc = m['description'] or 'KenVision by Intelense: AI video intelligence on the cameras you already own.'
    parts = [IB.THEME_BOOT if ENABLE_THEME else '', f'<title>{e(p["title"])}</title>', f'<meta name="description" content="{ea(desc)}">',
             '<meta name="author" content="Intelense Inc.">', '<meta name="theme-color" content="#0A34ED">', ICON_LINKS]
    if p['noindex']:
        parts.append('<meta name="robots" content="noindex, follow">')
    else:
        url = canonical(p)
        og_desc = m.get('og_description') or desc
        og_img = m.get('og_image') or SITE_URL + '/assets/images/dashboards/kenvision-imac-dashboard.webp'
        parts += ['<meta name="robots" content="index, follow">', f'<link rel="canonical" href="{url}">', '<meta property="og:type" content="website">',
                  '<meta property="og:site_name" content="KenVision by Intelense">', f'<meta property="og:url" content="{url}">',
                  f'<meta property="og:title" content="{ea(p["title"])}">', f'<meta property="og:description" content="{ea(og_desc)}">', f'<meta property="og:image" content="{og_img}">',
                  '<meta name="twitter:card" content="summary_large_image">', f'<meta name="twitter:title" content="{ea(p["title"])}">',
                  f'<meta name="twitter:description" content="{ea(og_desc)}">', f'<meta name="twitter:image" content="{og_img}">']
        for ld in m.get('jsonld', []):
            parts.append('<script type="application/ld+json">' + json.dumps(patch_ld(p['key'], ld), ensure_ascii=False).replace('</', '<\\/') + '</script>')
    parts += [IB.FONTS, '<script>document.documentElement.classList.add("js")</script>', '<link rel="stylesheet" href="@a/site.css">']
    return '\n'.join(x for x in parts if x)


ICON_LINKS = ('<link rel="icon" href="@a/icons/favicon.ico" sizes="any">\n<link rel="icon" type="image/png" sizes="32x32" href="@a/icons/favicon-32.png">\n'
              '<link rel="icon" type="image/png" sizes="48x48" href="@a/icons/favicon-48.png">\n<link rel="icon" type="image/png" sizes="96x96" href="@a/icons/favicon-96.png">\n'
              '<link rel="icon" type="image/png" sizes="192x192" href="@a/icons/icon-192.png">\n<link rel="apple-touch-icon" href="@a/icons/apple-touch-icon.png">')


def no_dashes(html):
    """No long dashes anywhere in the copy: a comma (or a colon after a name) reads the same and stays consistent."""
    html = html.replace('<option value="">— select a use case —</option>', '<option value="">Select a use case</option>').replace('Intelense — ', 'Intelense: ')
    return re.sub(r'\s*[\u2014\u2013]\s*', ', ', html)


def render(p):
    scripts = ('<script src="@a/site.js" defer></script>\n<script src="@a/kv.js" defer></script>\n<script type="module">\nimport { initCursorGrid } from \'@a/cursor-grid.js\';\n'
               + IB.GRID_START % IB.GRID_OPTS + '\n</script>')
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head(p)}\n</head>\n<body>\n'
            f'{header(p["active"])}\n<main id="top">\n  {p["body"]}\n</main>\n\n{footer()}\n{scripts}\n</body>\n</html>\n')


def resolve(html, depth, version):
    pre = '../' * depth

    def link(m):
        k = m.group(1)
        if k not in LINKS:
            raise SystemExit('unknown link token @' + k)
        return pre + LINKS[k][0] if PREVIEW else LINKS[k][1]
    html = re.sub(r'(?<=href=")@([a-z-]+)(?=")', link, html)
    base = (pre or './') + 'assets/' if PREVIEW else '/assets/'
    html = html.replace('@a/', base)
    if version:
        html = re.sub(r'((?:href|src)="[^"]*assets/[a-z-]+\.(?:css|js))"', lambda m: m.group(1) + '?v=' + version + '"', html)
        html = re.sub(r"(from '[^']*assets/cursor-grid\.js)'", lambda m: m.group(1) + '?v=' + version + "'", html)
    return html


def sitemap(pages):
    import datetime
    today = datetime.date.today().isoformat()
    pr = {'index': ('1.0', 'weekly'), 'solutions': ('0.9', 'weekly'), 'company': ('0.7', 'monthly'), 'contact': ('0.6', 'monthly')}
    urls = ''.join(f'  <url>\n    <loc>{canonical(p)}</loc>\n    <lastmod>{today}</lastmod>\n    <changefreq>{pr.get(p["key"], ("0.8", "monthly"))[1]}</changefreq>\n    <priority>{pr.get(p["key"], ("0.8", "monthly"))[0]}</priority>\n  </url>\n'
                   for p in pages if not p['noindex'])
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


USED = re.compile(r'@a/([A-Za-z0-9_./-]+\.(?:webp|png|ico|jpg|svg|css|js|mp4))')


def deploy(out):
    out.mkdir(parents=True, exist_ok=True)
    pages = [page_home(), page_solutions()] + [page_solution(k) for k, _, _ in SOLUTIONS] + [page_company(), page_contact(), page_404()]
    css = (SITE_DIR / 'assets' / 'site.css').read_text() + '\n' + (HERE / 'assets-src' / 'kv.css').read_text()
    version = hashlib.md5((css + (SITE_DIR / 'assets' / 'site.js').read_text() + (HERE / 'assets-src' / 'kv.js').read_text()).encode()).hexdigest()[:8]
    a = out / 'assets'
    a.mkdir(exist_ok=True)
    (a / 'site.css').write_text(css)
    for f in ('site.js', 'cursor-grid.js'):
        shutil.copy(SITE_DIR / 'assets' / f, a / f)
    used = set()
    for p in pages:
        html = no_dashes(render(p))
        used |= set(USED.findall(html))
        d = out / p['file']
        d.parent.mkdir(parents=True, exist_ok=True)
        d.write_text(resolve(html, p['depth'], version if not PREVIEW else None))
    for rel in sorted(used):
        if rel in ('site.css', 'site.js', 'cursor-grid.js'):
            continue
        src = HERE / 'assets' / rel
        if not src.exists():
            src = HERE / 'assets-src' / rel
        if not src.exists():
            src = SITE_DIR / 'assets' / rel
        if not src.exists():
            raise SystemExit('missing asset ' + rel)
        (a / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, a / rel)
    if not PREVIEW:
        (out / 'sitemap.xml').write_text(sitemap(pages))
        (out / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n')
        shutil.copy(HERE / 'server' / '.htaccess', out / '.htaccess')
        php = (SITE_DIR / 'server' / 'send-message.php').read_text()
        php = php.replace('website@intelense.com', 'website@kenvision.ai').replace('via intelense.com', 'via kenvision.ai').replace('intelense.com contact form', 'kenvision.ai contact form').replace('Intelense website', 'KenVision website')
        php = php.replace('intelense-form-', 'kenvision-form-').replace('intelense-contact-form', 'kenvision-contact-form').replace('intelense contact form', 'kenvision contact form')
        (out / 'send-message.php').write_text(php)
        shutil.copy(a / 'icons' / 'favicon.ico', out / 'favicon.ico')
    print('wrote', len(pages), 'pages and', len(used), 'assets to', out)


if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if not x.startswith('--')]
    if '--deploy' not in sys.argv:
        raise SystemExit(__doc__)
    deploy(Path(sys.argv[sys.argv.index('--deploy') + 1]))
