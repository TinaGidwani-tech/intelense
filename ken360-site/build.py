#!/usr/bin/env python3
"""Static generator for ken360.ai: a simple multi-page site in the Intelense design language (Montserrat, brand blue, brand gradient).

Reuses the Intelense stylesheet and script (site/) and adds ken360-site/assets-src/k3.css.

    python3 ken360-site/build.py --deploy DIR [--preview]

--preview writes relative .html links so the folder opens from disk or a preview host (home page is home.html).
"""
import hashlib
import html as H
import importlib.util
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
_spec.loader.exec_module(IB)

PREVIEW = '--preview' in sys.argv
SITE_URL = 'https://ken360.ai'
INTELENSE = 'https://www.intelense.com'
LINKEDIN = 'https://www.linkedin.com/company/intelense/'
DEMO = INTELENSE + '/contact'


def e(s):
    return H.escape(s, quote=False)


def ea(s):
    return H.escape(s, quote=True)


# ---------------------------------------------------------------- content

# key, name, use case, what it feeds into Ken360, colour, site
MODS = [
    ('kenvision', 'KenVision', 'Video analytics for retail, malls, QSR and public spaces', 'People, vehicles, objects and zones seen by your cameras', '#0A34ED', 'https://kenvision.ai/'),
    ('kensafety', 'KenSafety', 'Workplace and road safety for fleets, construction and industry', 'PPE, restricted areas and unsafe acts', '#FF7953', INTELENSE + '/kensafety'),
    ('kenhome', 'KenHome', 'Home, vehicle and asset security', 'Entry, motion, vehicle and asset alerts', '#78AFCF', INTELENSE + '/kenhome'),
    ('kenagri', 'KenAgri', 'Farm and crop monitoring', 'Crop, soil and weather signals', '#368736', INTELENSE + '/kenagri'),
    ('keniot', 'KenIoT', 'Predictive maintenance for machines and plants', 'Temperature, vibration and machine readings', '#7C28E9', INTELENSE + '/keniot'),
    ('kenrobotics', 'KenRobotics', 'Autonomous mobile robots and drones', 'Robot and drone position, route and status', '#6C6E82', INTELENSE + '/kenrobotics'),
    ('kenvoice', 'KenVoice', 'Conversation intelligence', 'Queues, requests and tone in conversations', '#5466DD', INTELENSE + '/kenvoice'),
]
MOD = {m[0]: m for m in MODS}

DEFINITION = ('Ken360 is the core AI technology from Intelense. It powers all seven Ken modules: '
              'KenVision, KenSafety, KenHome, KenAgri, KenIoT, KenRobotics and KenVoice.')

# The first three are from the current ken360.ai page; the rest are DRAFT examples to be approved before launch.
COMBOS = [
    (('kenvision', 'kensafety'), 'One incident, not two alerts', 'Crowd density rises in a zone where PPE compliance has just dropped. Ken360 raises it as one incident.', True),
    (('keniot', 'kenrobotics'), 'Rerouted before the line stops', 'A predicted conveyor failure reroutes the robot fleet before the line stops.', True),
    (('kenagri', 'keniot'), 'Checked before irrigation starts', 'Crop stress seen from the air is checked against soil moisture before irrigation starts.', True),
    (('kensafety', 'kenrobotics'), 'Robots that slow for people', 'A person enters a robot lane without protective gear. The robot slows and the safety lead is told.', False),
    (('kenvision', 'kenvoice'), 'The queue and the conversation, together', 'A queue builds at the counter and the conversation there shows where service is slowing. The manager sees both.', False),
    (('keniot', 'kensafety'), 'A reading with people in the zone', 'A temperature reading climbs in a zone where the camera sees people working. The alert goes to that zone supervisor.', False),
]

FAQ = [
    ('If we only use two modules, is Ken360 still useful?', 'Yes. You still get one dashboard, shared alerts and one API instead of two separate setups. What the modules can catch together grows as you add more.'),
    ("Can one module's data affect another?", 'Each module keeps its own data and decisions. They share a read-only layer, and what they see together appears only as a visible insight. You can switch off any pairing.'),
    ('Can different sites run different modules?', 'Yes. Each site shows only the modules it has, and portfolio views leave out the rest.'),
    ('Does Ken360 send our video to the cloud?', 'Not unless you choose to. Ken360 can run at the edge, on your servers, in your private cloud, or a mix. In an on-premise setup the video stays on site, and only events and derived data move.'),
    ('How long does a rollout take?', 'It depends on the site and the modules. Ken360 connects to the cameras, sensors and systems you already run, so there is no replacement phase before you see results.'),
    ('Can we white-label the dashboard?', 'Yes, on the enterprise tier. Your logo, colours and domain go on the dashboard. The API stays the same.'),
    ('What does the support agreement cover?', 'Each module is covered separately, so one module going down does not affect another. Terms are set in the contract. Ask us for the current terms.'),
    ('Who builds Ken360?', 'Intelense, an applied AI company working in industrial and operational environments. The same team builds every Ken module.'),
]

NAV = [('platform', 'Platform'), ('modules', 'Modules'), ('combinations', 'Combinations'), ('deployment', 'Deployment'), ('about', 'About')]


# ---------------------------------------------------------------- parts

def link(name):
    return '@index' if name == 'index' else f'@p/{name}'


def dot(c):
    return f'<span class="md" style="--c:{c}"></span>'


def header(current):
    links = ''.join(f'<li><a href="{link(n)}"{" aria-current=page" if n == current else ""}>{t}</a></li>' for n, t in NAV)
    mobile = ''.join(f'<a href="{link(n)}">{t}</a>' for n, t in NAV)
    return f'''<div class="announce"><div class="wrap"><span><span class="tag-new">Intelense</span>&nbsp; Ken360 is the core technology behind all seven Ken modules</span><a class="pill" href="{INTELENSE}/">Visit Intelense</a></div></div>
<header class="nav"><div class="wrap"><a class="logo k3-logo" href="@index" aria-label="Ken360 by Intelense, home"><img src="@a/logos/ken360.png" alt="Ken360 by Intelense" width="168" height="64"></a>
    <ul class="nav-links">{links}</ul>
    <div class="nav-cta"><a class="btn btn-blue" href="{DEMO}" target="_blank" rel="noopener">Book a demo</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Menu"><span></span></button></div></div>
  <nav class="mobile-menu" id="mobile-menu" hidden aria-label="Mobile"><div class="wrap">{mobile}<a class="btn btn-blue" href="{DEMO}" target="_blank" rel="noopener">Book a demo</a></div></nav>
</header>
'''


def footer():
    mods = ''.join(f'<li><a href="{m[5]}" rel="noopener">{m[1]}</a></li>' for m in MODS)
    pages = ''.join(f'<li><a href="{link(n)}">{t}</a></li>' for n, t in NAV) + f'<li><a href="{link("contact")}">Contact</a></li>'
    return f'''<footer><div class="wrap"><div class="foot k3-foot">
      <div><a class="logo k3-logo" href="@index" aria-label="Ken360 by Intelense, home"><img src="@a/logos/ken360-light.png" alt="Ken360 by Intelense" width="168" height="64"></a>
        <p style="margin-top:16px;max-width:36ch">Ken360 is the core AI technology from Intelense, behind all seven Ken modules.</p></div>
      <div><h4>Ken360</h4><ul>{pages}</ul></div>
      <div><h4>Ken modules</h4><ul>{mods}</ul></div>
      <div><h4>Intelense</h4><ul><li><a href="{INTELENSE}/">intelense.com</a></li><li><a href="{INTELENSE}/about">About Intelense</a></li><li><a href="{INTELENSE}/contact">Book a demo</a></li></ul></div>
      <div><h4>Contact</h4><ul><li class="email">enquiries@intelense.ca</li><li class="email">dinesh@intelense.com</li><li><a href="tel:+12895523165">+1 (289) 552-3165</a> Canada</li><li><a href="tel:+919342810422">+91 93428 10422</a> India</li><li><a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn</a></li></ul></div>
    </div><div class="legal"><span>© 2026 Intelense Inc. · <a href="{INTELENSE}/privacy">Privacy</a> · <a href="{INTELENSE}/terms">Terms</a></span><span>Ken360 is an Intelense technology</span></div></div></footer>
'''


def head_block(eyebrow, h2, lede=''):
    lede_html = f'<p class="lede">{lede}</p>' if lede else ''
    return f'<div class="head"><div><span class="eyebrow">{eyebrow}</span><h2>{h2}</h2></div>{lede_html}</div>'


def block(inner, sid=''):
    return f'<section class="block"{f" id={chr(34)}{sid}{chr(34)}" if sid else ""}><div class="wrap">{inner}</div></section>'


def page_hero(eyebrow, h1, lede, ctas=True):
    btn = f'<div class="hero-ctas"><a class="btn btn-blue" href="{DEMO}" target="_blank" rel="noopener">Book a demo</a><a class="btn btn-ghost" href="{link("platform")}">How it works</a></div>' if ctas else ''
    return f'''<section class="page-hero k3-hero"><div class="wash wash-a" aria-hidden="true"></div><div class="wash wash-b" aria-hidden="true"></div>
    <div class="wrap"><span class="eyebrow">{eyebrow}</span><h1>{h1}</h1><p class="lede">{lede}</p>{btn}</div></section>'''


def cols(items, n=3):
    cells = ''.join(f'<div><h3>{t}</h3><p>{p}</p></div>' for t, p in items)
    return f'<div class="k3-cols c{n}">{cells}</div>'


def steps(items):
    cells = ''.join(f'<div><span class="num">0{i + 1}</span><h3>{t}</h3><p>{p}</p></div>' for i, (t, p) in enumerate(items))
    return f'<div class="k3-cols c{len(items)} numbered">{cells}</div>'


def mod_rows(show_feed=False):
    rows = ''
    for k, n, job, feed, c, u in MODS:
        extra = f'<small>Feeds Ken360 with: {feed}</small>' if show_feed else ''
        rows += f'<li><span class="mn">{dot(c)}<b>{n}</b></span><span class="mj">{job}{extra}</span><a class="link-arrow" href="{u}" rel="noopener">Visit {n}</a></li>'
    return f'<ul class="k3-rows">{rows}</ul>'


def faq(items, title='Questions buyers ask'):
    det = ''.join(f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary><p>{e(a)}</p></details>' for i, (q, a) in enumerate(items))
    return f'<section class="block" id="faq"><div class="wrap faq-grid"><div><span class="eyebrow">FAQ</span><h2 style="margin-top:18px">{title}</h2></div><div>{det}</div></div></section>'


def cta(h='Start with one module. <span class="hl">Add the rest when you are ready.</span>'):
    return f'''<section class="cta"><div class="wrap"><h2>{h}</h2>
    <p class="lede" style="margin:22px auto 0">Ken360 is useful from the first deployment, not only at full scale.</p>
    <div class="hero-ctas"><a class="btn btn-blue" href="{DEMO}" target="_blank" rel="noopener">Book a demo</a><a class="btn btn-ghost" href="mailto:enquiries@intelense.ca">Email us</a></div></div></section>'''


# ---------------------------------------------------------------- pages

def page_index():
    hero = f'''<section class="hero k3-hero"><div class="wash wash-a" aria-hidden="true"></div><div class="wash wash-b" aria-hidden="true"></div>
    <div class="wrap"><span class="eyebrow">Core technology by Intelense</span>
      <h1>The AI engine behind <span class="hl">every Ken module</span>.</h1>
      <p class="lede">Ken360 is the core AI technology from Intelense. It connects your cameras, sensors, drones, robots and voice systems, understands what they see, and sends one clear alert to the right person.</p>
      <div class="hero-ctas"><a class="btn btn-blue" href="{DEMO}" target="_blank" rel="noopener">Book a demo</a><a class="btn btn-ghost" href="{link("platform")}">How it works</a></div>
      <div class="hero-meta"><span>Built by Intelense</span><span>Seven Ken modules</span><span>Edge, on-premise or cloud</span></div></div></section>'''
    what = block(head_block('What Ken360 is', 'One technology, <span class="hl">seven modules</span>.',
                            'The Ken modules are the products you use on site. Ken360 is what runs inside every one of them.')
                 + cols([('One engine', 'Every module runs on the same core: a shared data model, the AI engine, alerts and one dashboard.'),
                         ('Seven modules', 'Start with the one you need. Each new module joins the same engine, so what one learns is available to the rest.'),
                         ('Built by Intelense', 'Ken360 is an Intelense technology. The same team builds Ken360 and every module on it.')])
                 + f'<p class="k3-def">{DEFINITION}</p>', 'what')
    mods = block(head_block('The Ken modules', 'Pick what your site needs.', 'Every module is useful on its own and runs on Ken360.') + mod_rows()
                 + f'<p style="margin-top:32px"><a class="link-arrow" href="{link("modules")}">See what each module feeds into Ken360</a></p>', 'modules')
    how = block(head_block('How it works', 'Connect. Understand. <span class="hl">Act.</span>', 'Everything on a site flows through the same three steps.')
                + steps([('Connect', 'Plug in cameras, sensors, drones, robots and building systems. Ken360 turns every stream into one shared format. No rip-and-replace.'),
                         ('Understand', 'AI reads each stream, then compares them. It can run at the edge, on your servers or in the cloud.'),
                         ('Act', 'The right person gets one clear alert with the context attached. The team spends its time deciding, not watching.')])
                + f'<p style="margin-top:32px"><a class="link-arrow" href="{link("platform")}">More about the platform</a></p>', 'how')
    why = block(head_block('Why Ken360', 'Fewer screens. <span class="hl">Clearer alerts.</span>')
                + cols([('One dashboard', 'Cameras, sensors, robots and conversations in one place instead of several separate tools.'),
                        ('Alerts with context', 'When two modules see related things, Ken360 raises one incident instead of two alerts.'),
                        ('Grow at your pace', 'Start with one module. Add more later without starting again.'),
                        ('Your choice of setup', 'Run at the edge, on your servers, in your private cloud, or a mix.'),
                        ('Works with what you have', 'Ken360 connects to the cameras, sensors and systems you already run.'),
                        ('One API', 'Connect your own systems once, whichever modules you use.')]), 'why')
    return '\n\n  '.join([hero, what, mods, how, why, faq(FAQ[:4]), cta()])


def page_platform():
    parts = [('Shared data model', 'Every camera, sensor, robot and voice stream is stored in the same format, so modules can read each other.'),
             ('AI engine', 'Reads each stream and flags what matters. Runs at the edge, on your servers or in the cloud.'),
             ('Correlation across modules', 'Compares what different modules see and joins the overlap into one incident.'),
             ('Alerts and routing', 'Sends one clear alert, with context, to the right person.'),
             ('Dashboard and API', 'One place to see everything, and one API to connect your own systems.')]
    inside = block(head_block('Inside Ken360', 'Five parts, <span class="hl">shared by every module</span>.', 'Add a module and it joins the same engine.')
                   + '<ul class="k3-rows plain">' + ''.join(f'<li><span class="mn"><b>{t}</b></span><span class="mj">{p}</span></li>' for t, p in parts) + '</ul>')
    flow = block(head_block('How data flows', 'From a stream to <span class="hl">a decision</span>.')
                 + steps([('Connect', 'Ken360 connects to the cameras, sensors, drones, robots and building systems you already run and turns each stream into one shared format.'),
                          ('Understand', 'The AI engine reads every stream. Then it compares them, so related events from different modules are seen together.'),
                          ('Act', 'The right person gets one alert with the context attached, on the dashboard or through the API.')]))
    srcs = ''.join(f'<span class="chip">{s}</span>' for s in ('Cameras', 'Sensors', 'Drones', 'Robots', 'Voice', 'Building systems'))
    protos = ''.join(f'<span class="chip">{s}</span>' for s in ('RTSP', 'ONVIF', 'MQTT', 'Modbus', 'OPC-UA', 'ROS2'))
    conn = block(head_block('Connects to', 'What you already run.', 'No replacement phase before you see results.')
                 + f'<h3 style="margin-bottom:14px">Sources</h3><div class="chips">{srcs}</div><h3 style="margin:32px 0 14px">Protocols</h3><div class="chips">{protos}</div>')
    return '\n\n  '.join([page_hero('Platform', 'One engine for <span class="hl">every site</span>.', 'Ken360 is the layer that turns separate cameras, sensors and robots into one picture of what is happening on site.'), inside, flow, conn, cta()])


def page_modules():
    return '\n\n  '.join([page_hero('Modules', 'Seven modules. <span class="hl">One engine.</span>', DEFINITION),
                          block(head_block('The Ken modules', 'What each module adds.', 'Each module sends its own events into Ken360. Ken360 compares them across modules.') + mod_rows(True)),
                          cta('Not sure which module to start with? <span class="hl">Talk to us.</span>')])


def page_combinations():
    items = ''
    for pair, t, p, ok in COMBOS:
        tags = ' <em>+</em> '.join(f'<span class="mn">{dot(MOD[k][4])}{MOD[k][1]}</span>' for k in pair)
        items += f'<li><div class="pair">{tags}</div><h3>{t}</h3><p>{p}</p>{"" if ok else "<span class=draft>Draft example</span>"}</li>'
    return '\n\n  '.join([page_hero('Combinations', 'What one module can not see, <span class="hl">two can</span>.', 'Each Ken module is useful alone. Ken360 compares what they see and turns the overlap into one incident, one alert and one next step.', False),
                          block(f'<ul class="k3-combos">{items}</ul><p class="k3-note">Examples show how modules can work together. Results depend on your site and setup.</p>'), cta()])


def page_deployment():
    opts = steps([('At the edge', 'Analysis runs next to the cameras and sensors, so alerts are quick and video stays where it is captured.'),
                  ('On your servers', 'Everything runs inside your own data centre. Only the events and derived data you choose leave the site.'),
                  ('In the cloud, or both', 'Use your private cloud for scale and reporting, and keep sensitive streams on site. One platform, mixed setup.')])
    return '\n\n  '.join([page_hero('Deployment', 'Your data stays where <span class="hl">you decide</span>.', 'Run Ken360 at the edge, on your servers, in your private cloud, or a mix. In an on-premise setup the video stays on site.', False),
                          block(head_block('Setup options', 'Three ways to run Ken360.') + opts), faq(FAQ, 'Deployment, data and support'), cta()])


def page_about():
    body = block(head_block('About', 'Ken360 is an <span class="hl">Intelense technology</span>.', 'Intelense is an applied AI company working in industrial and operational environments.')
                 + cols([('One team', 'The same team builds Ken360 and every Ken module that runs on it.'),
                         ('One family', 'KenVision, KenSafety, KenHome, KenAgri, KenIoT, KenRobotics and KenVoice all share the same core.'),
                         ('More at intelense.com', 'Read about the company, the team and the offices on the Intelense site.')])
                 + f'<p style="margin-top:32px"><a class="btn btn-ghost" href="{INTELENSE}/about" rel="noopener">About Intelense</a></p>')
    return '\n\n  '.join([page_hero('About', 'Built by <span class="hl">Intelense</span>.', DEFINITION, False), body, cta()])


def page_contact():
    body = block(head_block('Contact', 'Talk to the team behind Ken360.', 'Tell us what you run today and which module you would start with.')
                 + f'''<div class="k3-cols c3"><div><h3>Email</h3><p class="email">enquiries@intelense.ca</p><p class="email">dinesh@intelense.com</p></div>
        <div><h3>Phone</h3><p><a href="tel:+12895523165">+1 (289) 552-3165</a> Canada</p><p><a href="tel:+919342810422">+91 93428 10422</a> India</p></div>
        <div><h3>Book a demo</h3><p>Use the form on the Intelense site.</p><p><a class="btn btn-blue" href="{DEMO}" target="_blank" rel="noopener">Book a demo</a></p></div></div>''')
    return '\n\n  '.join([page_hero('Contact', 'Let us <span class="hl">talk</span>.', 'We reply to every enquiry.', False), body])


PAGES = {
    'index': ('Ken360 by Intelense | The Core AI Technology Behind All Seven Ken Modules',
              'Ken360 is the core AI technology from Intelense that powers KenVision, KenSafety, KenHome, KenAgri, KenIoT, KenRobotics and KenVoice. One engine, one picture of every site.', page_index),
    'platform': ('Ken360 Platform | One AI Engine for Cameras, Sensors and Robots', 'How Ken360 connects cameras, sensors, drones, robots and voice into one engine and sends one clear alert to the right person.', page_platform),
    'modules': ('Ken Modules | KenVision, KenSafety, KenHome, KenAgri, KenIoT, KenRobotics, KenVoice', 'The seven Ken modules by Intelense, all running on Ken360. See what each one does and what it feeds into the shared engine.', page_modules),
    'combinations': ('Module Combinations | What Ken360 Sees Across Ken Modules', 'Examples of how Ken modules work together on Ken360: one incident, one alert and one next step instead of separate alerts.', page_combinations),
    'deployment': ('Ken360 Deployment | Edge, On-Premise, Cloud and FAQ', 'Run Ken360 at the edge, on your servers, in your private cloud, or a mix. Answers on data, video, rollout and support.', page_deployment),
    'about': ('About Ken360 | An Intelense Technology', 'Ken360 is built by Intelense, an applied AI company working in industrial and operational environments.', page_about),
    'contact': ('Contact Ken360 | Book a Demo with Intelense', 'Talk to the Intelense team about Ken360 and the Ken modules. Email, phone or book a demo.', page_contact),
}


def jsonld(name):
    org = {'@type': 'Organization', 'name': 'Intelense', 'url': INTELENSE + '/', 'sameAs': [LINKEDIN]}
    out = []
    if name == 'index':
        out.append({'@context': 'https://schema.org', '@type': 'SoftwareApplication', 'name': 'Ken360', 'alternateName': 'Ken360 by Intelense', 'applicationCategory': 'BusinessApplication',
                    'url': SITE_URL + '/', 'description': PAGES['index'][1], 'publisher': org, 'provider': org, 'sameAs': [INTELENSE + '/ken360'],
                    'isBasedOn': [{'@type': 'SoftwareApplication', 'name': m[1], 'url': m[5]} for m in MODS]})
    if name == 'deployment':
        out.append({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]})
    return out


ICON_LINKS = ('<link rel="icon" href="@a/icons/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="@a/icons/favicon-32.png">'
              '<link rel="icon" type="image/png" sizes="96x96" href="@a/icons/favicon-96.png"><link rel="apple-touch-icon" href="@a/icons/apple-touch-icon.png">')


def render(name):
    title, desc, fn = PAGES[name]
    url = SITE_URL + ('/' if name == 'index' else f'/{name}')
    ld = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace('</', '<\\/') + '</script>' for x in jsonld(name))
    head = (f'<title>{e(title)}</title>\n<meta name="description" content="{ea(desc)}">\n<meta name="author" content="Intelense Inc.">\n<meta name="theme-color" content="#0A34ED">\n{ICON_LINKS}\n'
            f'<meta name="robots" content="index, follow"><link rel="canonical" href="{url}">\n<meta property="og:type" content="website"><meta property="og:site_name" content="Ken360 by Intelense">'
            f'<meta property="og:url" content="{url}"><meta property="og:title" content="{ea(title)}"><meta property="og:description" content="{ea(desc)}">\n'
            f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{ea(title)}"><meta name="twitter:description" content="{ea(desc)}">\n{ld}\n{IB.FONTS}\n'
            '<script>document.documentElement.classList.add("js")</script><link rel="stylesheet" href="@a/site.css">')
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n'
            f'{header(name)}\n<main id="top">\n  {fn()}\n</main>\n\n{footer()}\n<script src="@a/site.js" defer></script>\n<script src="@a/k3.js" defer></script>\n</body>\n</html>\n')


def resolve(html, version):
    if PREVIEW:
        html = html.replace('href="@index"', 'href="home.html"')
        html = re.sub(r'href="@p/([a-z]+)"', r'href="\1.html"', html)
        html = html.replace('@a/', 'assets/')
    else:
        html = html.replace('href="@index"', 'href="/"')
        html = re.sub(r'href="@p/([a-z]+)"', r'href="/\1"', html)
        html = html.replace('@a/', '/assets/')
    if version:
        html = re.sub(r'((?:href|src)="[^"]*assets/[a-z0-9-]+\.(?:css|js))"', lambda m: m.group(1) + '?v=' + version + '"', html)
    return html


def deploy(out):
    out.mkdir(parents=True, exist_ok=True)
    css = (SITE_DIR / 'assets' / 'site.css').read_text() + '\n' + (HERE / 'assets-src' / 'k3.css').read_text()
    version = hashlib.md5((css + (SITE_DIR / 'assets' / 'site.js').read_text() + (HERE / 'assets-src' / 'k3.js').read_text()).encode()).hexdigest()[:8]
    a = out / 'assets'
    a.mkdir(exist_ok=True)
    (a / 'site.css').write_text(css)
    shutil.copy(SITE_DIR / 'assets' / 'site.js', a / 'site.js')
    shutil.copy(HERE / 'assets-src' / 'k3.js', a / 'k3.js')
    shutil.copytree(SITE_DIR / 'assets' / 'icons', a / 'icons', dirs_exist_ok=True)
    shutil.copytree(HERE / 'assets-src' / 'logos', a / 'logos', dirs_exist_ok=True)
    for name in PAGES:
        html = resolve(render(name), None if PREVIEW else version)
        if PREVIEW:
            (out / ('home.html' if name == 'index' else f'{name}.html')).write_text(html)
        elif name == 'index':
            (out / 'index.html').write_text(html)
        else:
            (out / name).mkdir(exist_ok=True)
            (out / name / 'index.html').write_text(html)
    if not PREVIEW:
        urls = ''.join(f'  <url><loc>{SITE_URL}{"/" if n == "index" else "/" + n}</loc></url>\n' for n in PAGES)
        (out / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n')
        (out / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
        shutil.copy(a / 'icons' / 'favicon.ico', out / 'favicon.ico')
    print('wrote the Ken360 site (%d pages) to %s' % (len(PAGES), out))


if __name__ == '__main__':
    if '--deploy' not in sys.argv:
        raise SystemExit(__doc__)
    deploy(Path(sys.argv[sys.argv.index('--deploy') + 1]))
