#!/usr/bin/env python3
"""Static generator for ken360.ai (first draft: the home page), in the same design language as www.intelense.com.

Reuses the Intelense stylesheet, script and components (site/) and adds ken360-site/assets-src/k3.css and k3.js.

    python3 ken360-site/build.py --deploy DIR [--preview]

--preview writes relative links so the folder opens from disk or a preview host.
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

icon = IB.icon
PREVIEW = '--preview' in sys.argv
SITE_URL = 'https://ken360.ai'
INTELENSE = 'https://www.intelense.com'
LINKEDIN = 'https://www.linkedin.com/company/intelense/'

# key, name, short job, colour (the Ken module colours), where it lives
MODS = [
    ('kenvision', 'KenVision', 'Video analytics', '#0A34ED', 'https://kenvision.ai/'),
    ('kensafety', 'KenSafety', 'Workplace safety', '#FF7953', INTELENSE + '/kensafety'),
    ('kenhome', 'KenHome', 'Smart home security', '#78AFCF', INTELENSE + '/kenhome'),
    ('kenagri', 'KenAgri', 'Precision agriculture', '#368736', INTELENSE + '/kenagri'),
    ('keniot', 'KenIoT', 'Predictive monitoring', '#7C28E9', INTELENSE + '/keniot'),
    ('kenrobotics', 'KenRobotics', 'Autonomous robotics', '#6C6E82', INTELENSE + '/kenrobotics'),
    ('kenvoice', 'KenVoice', 'Conversation intelligence', '#5466DD', INTELENSE + '/kenvoice'),
]
MOD = {m[0]: m for m in MODS}

DEFINITION = ('Ken360 is the core AI technology from Intelense. It powers all seven Ken modules: '
              'KenVision, KenSafety, KenHome, KenAgri, KenIoT, KenRobotics and KenVoice.')

# Combination scenarios. The first three are from the current ken360.ai page; the rest are DRAFT, to be approved.
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


def e(s):
    return H.escape(s or '', quote=False)


def ea(s):
    return H.escape(s or '', quote=True)


def rv(i=0):
    return f' data-r style="--d:{i * 70}ms"'


def dot(c):
    return f'<i class="md" style="--c:{c}"></i>'


# ---------------------------------------------------------------- shared fragments

def lockup(cls=''):
    return (f'<a class="logo k3-logo {cls}" href="@index" aria-label="Ken360 by Intelense, home">'
            '<img src="@a/logos/ken360.png" alt="Ken360 by Intelense" width="168" height="64"></a>')


def header():
    mod_items = ''.join(f'<li><a href="#stack" style="--mod:{c}"><i></i>{n}<small>{job}</small></a></li>' for k, n, job, c, url in MODS)
    links = ('<li><a href="#how">Platform</a></li><li><a href="#combos">Combinations</a></li><li><a href="#runs">Deployment</a></li>'
             f'<li class="has-menu"><a href="#stack">Modules</a><div class="dropdown"><ul>{mod_items}</ul></div></li><li><a href="#faq">FAQ</a></li>')
    mobile = '<a href="#how">Platform</a><a href="#combos">Combinations</a><a href="#runs">Deployment</a><a href="#stack">Modules</a><a href="#faq">FAQ</a>'
    return f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs><linearGradient id="brand-g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A34ED"/><stop offset=".3" stop-color="#7C28E9"/><stop offset=".6" stop-color="#FF7953"/><stop offset=".82" stop-color="#78AFCF"/><stop offset="1" stop-color="#73C4C5"/></linearGradient></defs></svg>
<div class="announce"><div class="wrap"><span><span class="tag-new">Intelense</span>&nbsp; Ken360 is the core technology behind all seven Ken modules</span><a class="pill" href="{INTELENSE}/">Visit Intelense</a></div></div>
<header class="nav"><div class="wrap">{lockup()}
    <ul class="nav-links">{links}</ul>
    <div class="nav-cta"><a class="btn btn-blue" href="{INTELENSE}/contact" target="_blank" rel="noopener">Book a demo</a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Menu"><span></span></button></div></div>
  <nav class="mobile-menu" id="mobile-menu" hidden aria-label="Mobile"><div class="wrap">{mobile}<a class="btn btn-blue" href="{INTELENSE}/contact" target="_blank" rel="noopener">Book a demo</a></div></nav>
</header>
'''


def footer():
    mods = ''.join(f'<li><a href="{u}" rel="noopener">{n}</a></li>' for k, n, j, c, u in MODS)
    return f'''<footer><div class="wrap"><div class="foot k3-foot">
      <div><a class="logo k3-logo" href="@index" aria-label="Ken360 by Intelense, home"><img src="@a/logos/ken360-light.png" alt="Ken360 by Intelense" width="168" height="64"></a>
        <p style="margin-top:16px;max-width:36ch">Ken360 is the core AI technology from Intelense, behind all seven Ken modules.</p></div>
      <div><h4>Platform</h4><ul><li><a href="#how">How it works</a></li><li><a href="#combos">Combinations</a></li><li><a href="#runs">Deployment</a></li><li><a href="#faq">FAQ</a></li></ul></div>
      <div><h4>Ken modules</h4><ul>{mods}</ul></div>
      <div><h4>Intelense</h4><ul><li><a href="{INTELENSE}/">intelense.com</a></li><li><a href="{INTELENSE}/ken360">Ken360 on intelense.com</a></li><li><a href="{INTELENSE}/about">About Intelense</a></li><li><a href="{INTELENSE}/contact">Contact</a></li></ul></div>
      <div><h4>Contact</h4><ul><li class="email">enquiries@intelense.ca</li><li class="email">dinesh@intelense.com</li><li><a href="tel:+12895523165">+1 (289) 552-3165</a> Canada</li><li><a href="tel:+919342810422">+91 93428 10422</a> India</li><li><a href="{LINKEDIN}" target="_blank" rel="noopener noreferrer">LinkedIn</a></li></ul></div>
    </div><div class="legal"><span>© 2026 Intelense Inc. · <a href="{INTELENSE}/privacy">Privacy</a> · <a href="{INTELENSE}/terms">Terms</a></span><span>Ken360 is an Intelense technology</span></div></div></footer>
'''


def head_block(eyebrow, h2, lede=''):
    lede_html = f'<p class="lede">{lede}</p>' if lede else ''
    return f'<div class="head"><div><span class="eyebrow">{eyebrow}</span><h2>{h2}</h2></div>{lede_html}</div>'


def block(inner, sid='', cls=''):
    return f'<section class="block{" " + cls if cls else ""}"{f" id={chr(34)}{sid}{chr(34)}" if sid else ""}><div class="wrap">{inner}</div></section>'


# ---------------------------------------------------------------- sections

def site_map():
    """An example site as one floor plan. Each Ken module adds its own layer to the same map (toggled by k3.js). All content is illustrative."""
    C = {k: c for k, n, j, c, u in MODS}
    zone = lambda x, y, w, h, t: f'<rect class="zn" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/><text class="zt" x="{x + 16}" y="{y + 26}">{t}</text>'
    base = (
        '<rect class="bg" x="20" y="20" width="960" height="520" rx="34"/>'
        '<rect class="yard" x="48" y="396" width="660" height="116" rx="18"/><text class="zt" x="64" y="426">Yard and gate</text>'
        '<line class="lane" x1="64" y1="470" x2="690" y2="470"/>'
        + zone(60, 50, 200, 200, 'Loading dock') + zone(260, 50, 260, 200, 'Storage') + zone(520, 50, 180, 330, 'Production line')
        + zone(60, 250, 200, 130, 'Office and counter') + zone(260, 250, 260, 130, 'Packing aisle')
        + '<rect class="field" x="740" y="50" width="220" height="250" rx="18"/><text class="zt" x="756" y="80">Field 3</text>'
        + ''.join(f'<line class="row" x1="{756 + i * 22}" y1="96" x2="{756 + i * 22}" y2="284"/>' for i in range(9))
        + '<rect class="zn" x="740" y="330" width="220" height="110" rx="14"/><text class="zt" x="756" y="358">Caretaker\'s home</text>'
        + '<path class="home" d="M790 416 V386 L830 364 L870 386 V416 Z"/>'
    )
    vision = (
        f'<g data-l="kenvision" style="--c:{C["kenvision"]}">'
        '<polygon class="fov" points="236,72 90,170 200,238"/><polygon class="fov" points="470,72 330,236 508,236"/>'
        '<circle class="heat" cx="150" cy="170" r="70"/>'
        + ''.join(f'<circle class="pp" cx="{x}" cy="{y}" r="6" style="--dx:{dx}px;--dy:{dy}px;animation-delay:{-i * .7}s"/>' for i, (x, y, dx, dy) in enumerate([(120, 150, 16, 10), (150, 180, -14, 12), (178, 150, 10, -14), (140, 214, 18, -8), (200, 200, -12, 8), (110, 190, 12, 14)]))
        + '<g class="cam"><circle cx="236" cy="72" r="9"/><circle cx="470" cy="72" r="9"/></g>'
        '<g class="tag"><rect x="74" y="212" width="106" height="26" rx="13"/><text x="88" y="230">Crowd · 12</text></g></g>')
    safety = (
        f'<g data-l="kensafety" style="--c:{C["kensafety"]}">'
        '<rect class="hatch" x="176" y="150" width="76" height="92" rx="8"/>'
        '<g class="pin"><circle cx="214" cy="196" r="13"/><text x="214" y="201" text-anchor="middle">!</text></g>'
        '<g class="tag"><rect x="156" y="118" width="100" height="26" rx="13"/><text x="170" y="136">PPE alert</text></g></g>')
    ring = '<rect class="ring" data-ring x="52" y="42" width="216" height="216" rx="26"/><g class="tag incl" data-ring><rect x="92" y="28" width="124" height="28" rx="14"/><text x="108" y="47">One incident</text></g>'
    iot = (
        f'<g data-l="keniot" style="--c:{C["keniot"]}">'
        + ''.join(f'<g class="sn{" bad" if bad else ""}"><circle cx="{x}" cy="{y}" r="8"/><circle class="pl" cx="{x}" cy="{y}" r="8"/></g><g class="tag"><rect x="{x + 14}" y="{y - 13}" width="{w}" height="26" rx="13"/><text x="{x + 26}" y="{y + 5}">{t}</text></g>'
                  for x, y, w, t, bad in [(560, 110, 92, 'Vibration', False), (600, 190, 96, 'Temp high', True), (580, 310, 80, 'Motor', False)])
        + '</g>')
    robots = (
        f'<g data-l="kenrobotics" style="--c:{C["kenrobotics"]}">'
        '<path class="route" d="M290 296 H494 V350 H290 Z"/>'
        '<rect class="bot" width="26" height="18" rx="6" style="animation-delay:0s"/><rect class="bot" width="26" height="18" rx="6" style="animation-delay:-4s"/>'
        '<g class="tag"><rect x="392" y="258" width="108" height="26" rx="13"/><text x="406" y="276">Robot fleet</text></g></g>')
    voice = (
        f'<g data-l="kenvoice" style="--c:{C["kenvoice"]}">'
        '<g class="mic"><circle cx="140" cy="326" r="15"/><path d="M140 318v10M134 326a6 6 0 0012 0"/></g>'
        '<path class="wave w1" d="M164 316a14 14 0 010 20"/><path class="wave w2" d="M174 310a24 24 0 010 32"/>'
        '<g class="tag"><rect x="78" y="350" width="110" height="26" rx="13"/><text x="92" y="368">Counter 2</text></g></g>')
    home = (
        f'<g data-l="kenhome" style="--c:{C["kenhome"]}">'
        '<circle class="cam2" cx="850" cy="372" r="8"/><polygon class="fov" points="850,372 790,430 910,430"/>'
        '<g class="tag"><rect x="866" y="396" width="86" height="26" rx="13"/><text x="880" y="414">Driveway</text></g></g>')
    agri = (
        f'<g data-l="kenagri" style="--c:{C["kenagri"]}">'
        '<path class="dry" d="M780 150 L900 130 L920 220 L800 240 Z"/>'
        '<g class="tag"><rect x="772" y="256" width="132" height="26" rx="13"/><text x="786" y="274">Dry patch</text></g></g>')
    defs = '<defs><radialGradient id="hg"><stop offset="0" stop-color="#FF7953" stop-opacity=".55"/><stop offset="1" stop-color="#FF7953" stop-opacity="0"/></radialGradient><pattern id="ht" width="10" height="10" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="10" stroke="#FF7953" stroke-width="3" opacity=".55"/></pattern></defs>'
    return (f'<svg class="map" viewBox="0 0 1000 560" role="img" aria-label="One site floor plan. Each Ken module adds its own layer to the same map." focusable="false">{defs}{base}{agri}{home}{iot}{robots}{voice}{vision}{safety}{ring}</svg>')


def hero():
    chips = ''.join(f'<button type="button" class="lt" aria-pressed="true" data-k="{k}" style="--c:{c}">{dot(c)}{n}</button>' for k, n, j, c, u in MODS)
    return f'''<section class="page-hero k3-hero">
    <div class="wash wash-a" aria-hidden="true"></div><div class="wash wash-b" aria-hidden="true"></div><div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap">
      <div class="k3-hero-copy">
        <span class="eyebrow">The core technology behind the Ken modules</span>
        <h1>One picture of everything happening on <em>site</em>.</h1>
        <p class="lede">Ken360 is the core AI technology from Intelense. It brings your cameras, sensors, drones, robots and conversations into one engine, and it powers all seven Ken modules.</p>
        <div class="hero-ctas"><a class="btn btn-blue" href="{INTELENSE}/contact" target="_blank" rel="noopener">Book a demo</a><a class="btn btn-ghost" href="#how">See how it works</a></div>
      </div>
      <div class="k3-mapwrap" data-map>
        <div class="mbar"><span class="lbl">One site. Tap a module to add or remove its layer.</span><div class="lts" role="group" aria-label="Module layers on the site map">{chips}</div></div>
        <div class="mstage">{site_map()}
          <div class="mcard" data-card aria-live="polite"><span class="tag">One incident</span><b>Crowd building where PPE has dropped</b><small>KenVision + KenSafety · Loading dock</small><div class="act"><span>Notify</span> Shift supervisor</div></div>
        </div>
        <p class="k3-note"><span data-count>7 of 7</span> layers on. Example site and data, for illustration.</p>
      </div>
    </div></section>'''


def what_is():
    top = ''.join(f'<a class="mchip" href="{u}" rel="noopener" style="--c:{c}">{dot(c)}{n}</a>' for k, n, j, c, u in MODS)
    sources = ''.join(f'<span class="schip">{s}</span>' for s in ('Cameras', 'Sensors', 'Drones', 'Robots', 'Voice', 'Building systems'))
    return block(head_block('What Ken360 is', 'Seven modules. <em>One technology</em> underneath.',
                            'The Ken modules are the products you use on site. Ken360 is what runs inside every one of them: the shared data model, the AI engine, the alerts and the dashboard. Add a module and it joins the same engine, so what each one learns is available to the rest.')
                 + f'''<div class="k3-stack" id="stack"{rv()}>
        <div class="row top"><span class="lbl">The Ken modules</span><div class="mods">{top}</div></div>
        <div class="links" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
        <div class="row core"><div class="coreb"><div class="ctitle"><b>Ken360</b><span>core technology by Intelense</span></div>
          <ul><li>Shared data model</li><li>AI engine</li><li>Correlation across modules</li><li>Alerts and routing</li><li>One dashboard and API</li></ul></div></div>
        <div class="links" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
        <div class="row src"><span class="lbl">What it connects to</span><div class="srcs">{sources}</div></div>
      </div>
      <p class="k3-def"{rv(1)}>{DEFINITION}</p>''', 'what')


def problem():
    old = [('kenvision', 'Crowd density rising · Zone B'), ('kensafety', 'PPE compliance dropped · Zone B'), ('keniot', 'Compressor temperature high'), ('kenvoice', 'Queue at counter 3')]
    olds = ''.join(f'<div class="n" style="--c:{MOD[k][3]}"{rv(i)}>{dot(MOD[k][3])}<span>{e(t)}</span><small>{MOD[k][1]}</small></div>' for i, (k, t) in enumerate(old))
    return block(head_block('The problem', 'Most sites run on <em>separate tools</em>.',
                            'One system watches the cameras. Another reads the sensors. A third listens at the counter. Each sends its own alerts, and no one sees how they connect. Ken360 is the layer that does.')
                 + f'''<div class="k3-before-after"><div class="ba before"><span class="cap-t">Today: separate alerts</span>{olds}</div>
      <div class="ba arrowc" aria-hidden="true"><i></i></div>
      <div class="ba after"{rv(2)}><span class="cap-t">With Ken360: one picture</span>
        <div class="one"><span class="tag">One incident</span><b>Crowd building where PPE has dropped, Zone B</b><p>Two modules, one alert, one next step. The temperature reading and the queue stay as separate items, each in its own place.</p></div></div></div>''', 'problem')


def how():
    steps = [('Connect', 'Plug in cameras, sensors, drones, robots and building systems. Ken360 turns every stream into one shared format. No rip-and-replace.',
              '<div class="protos"><span>RTSP</span><span>ONVIF</span><span>MQTT</span><span>Modbus</span><span>OPC-UA</span><span>ROS2</span></div>'),
             ('Understand', 'AI reads each stream, then compares them. It can run at the edge, on your servers or in the cloud.',
              '<div class="mini-u"><span class="a"></span><span class="b"></span><span class="c"></span><em>compare</em></div>'),
             ('Act', 'The right person gets one clear alert with the context attached. The team spends its time deciding, not watching.',
              '<div class="mini-a"><b>Zone B · one incident</b><small>Sent to the shift supervisor</small></div>')]
    li = ''.join(f'<li{rv(i)}><span class="dot"></span><span class="num">0{i + 1}</span><h3>{t}</h3><p>{p}</p>{v}</li>' for i, (t, p, v) in enumerate(steps))
    return block(head_block('How it works', 'Connect. Understand. <em>Act.</em>', 'Everything on a site flows through the same three steps.')
                 + f'<div class="k3-how" data-how><div class="track" aria-hidden="true"><i class="fill"></i></div><ol class="stp">{li}</ol></div>', 'how')


def combos():
    chips = ''.join(f'<button type="button" class="mt" aria-pressed="{"true" if k in ("kenvision", "kensafety") else "false"}" data-k="{k}" style="--c:{c}">{dot(c)}{n}</button>' for k, n, j, c, u in MODS)
    data = [{'a': a, 'b': b, 't': t, 'p': p, 'ok': ok} for (a, b), t, p, ok in COMBOS]
    names = {k: n for k, n, j, c, u in MODS}
    jobs = {k: j for k, n, j, c, u in MODS}
    cols = {k: c for k, n, j, c, u in MODS}
    return block(head_block('Combinations', 'What one module can\'t see, <em>two can</em>.',
                            'Each Ken module is useful alone. Ken360 compares what they see and turns the overlap into one incident, one alert and one next step.')
                 + f'''<div class="k3-pick" data-combos data-set='{json.dumps(data)}' data-names='{json.dumps(names)}' data-cols='{json.dumps(cols)}'{rv()}>
        <div class="bar"><span class="lbl">Switch on what your site runs</span><div class="mts" role="group" aria-label="Modules on this site">{chips}</div></div>
        <div class="out"><div class="sum" aria-live="polite"></div><div class="list"></div></div>
        <p class="k3-note">Examples show how modules can work together. Results depend on your site and setup.</p></div>''', 'combos')


def runs():
    items = [('At the edge', 'Analysis runs next to the cameras and sensors, so alerts are quick and video stays where it is captured.', ['Cameras', 'Edge', 'Alerts']),
             ('On your servers', 'Everything runs inside your own data centre. Only the events and derived data you choose leave the site.', ['Sources', 'Your servers', 'Dashboard']),
             ('In the cloud, or both', 'Use your private cloud for scale and reporting, and keep sensitive streams on site. One platform, mixed setup.', ['Sources', 'Edge + cloud', 'Dashboard'])]
    cards = ''.join(f'<div class="rn"{rv(i)}><h3>{t}</h3><p>{p}</p><div class="path">{"<i></i>".join(f"<span>{x}</span>" for x in n)}</div></div>' for i, (t, p, n) in enumerate(items))
    return block(head_block('Deployment', 'Your data stays where <em>you decide</em>.', 'Run Ken360 at the edge, on your servers, in your private cloud, or a mix. In an on-premise setup the video stays on site.')
                 + f'<div class="k3-runs">{cards}</div>', 'runs')


def faq():
    det = ''.join(f'<details{" open" if i == 0 else ""}><summary>{e(q)}</summary><p>{e(a)}</p></details>' for i, (q, a) in enumerate(FAQ))
    return f'<section class="block" id="faq"><div class="wrap faq-grid"><div><span class="eyebrow">FAQ</span><h2 style="margin-top:18px">Questions buyers ask</h2></div><div>{det}</div></div></section>'


def by_intelense():
    return f'''<section class="block" id="intelense"><div class="wrap"><div class="k3-by-card"{rv()}>
      <div><span class="eyebrow">Ken360 is an Intelense technology</span><h2>The core technology behind the Ken product family.</h2>
        <p>{DEFINITION} Intelense is an applied AI company working in industrial and operational environments. The same team builds every module on Ken360.</p>
        <p style="margin-top:22px"><a class="btn btn-ghost on-card" href="{INTELENSE}/">Visit intelense.com</a></p></div>
      <ul class="links"><li><a href="{INTELENSE}/ken360">Ken360 on intelense.com<small>The platform page on the company site</small></a></li>
        <li><a href="https://kenvision.ai/">kenvision.ai<small>The KenVision product site</small></a></li>
        <li><a href="{INTELENSE}/modules">All Ken modules<small>Compare what each module does</small></a></li>
        <li><a href="{INTELENSE}/about">About Intelense<small>The team, offices and story</small></a></li></ul>
    </div></div></section>'''


def cta():
    return f'''<section class="cta"><div class="wash wash-b" aria-hidden="true" style="top:10%;right:20%"></div><div class="wash wash-a" aria-hidden="true" style="top:30%;left:20%"></div>
    <div class="wrap"><span class="eyebrow">Get started</span><h2 style="margin-top:20px">Start with one module. Add the rest when you're ready.</h2>
    <p class="lede" style="margin:22px auto 0">Ken360 is useful from the first deployment, not only at full scale.</p>
    <div class="hero-ctas"><a class="btn btn-blue" href="{INTELENSE}/contact" target="_blank" rel="noopener">Book a demo</a><a class="btn btn-black" href="mailto:enquiries@intelense.ca">Email us</a></div></div></section>'''


# ---------------------------------------------------------------- page assembly

TITLE = 'Ken360 by Intelense | The Core AI Technology Behind All Seven Ken Modules'
DESC = ('Ken360 is the core AI technology from Intelense that powers KenVision, KenSafety, KenHome, KenAgri, KenIoT, KenRobotics and KenVoice. '
        'One engine, one picture of every site.')


def jsonld():
    org = {'@type': 'Organization', 'name': 'Intelense', 'url': INTELENSE + '/', 'sameAs': [LINKEDIN]}
    return [
        {'@context': 'https://schema.org', '@type': 'SoftwareApplication', 'name': 'Ken360', 'alternateName': 'Ken360 by Intelense',
         'applicationCategory': 'BusinessApplication', 'url': SITE_URL + '/', 'description': DESC, 'publisher': org, 'provider': org,
         'sameAs': [INTELENSE + '/ken360'], 'isBasedOn': [{'@type': 'SoftwareApplication', 'name': n, 'url': u} for k, n, j, c, u in MODS]},
        {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in FAQ]},
    ]


def page_index():
    body = '\n\n  '.join([hero(), what_is(), problem(), how(), combos(), runs(), faq(), by_intelense(), cta()])
    return body


FONTS = IB.FONTS
ICON_LINKS = ('<link rel="icon" href="@a/icons/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="@a/icons/favicon-32.png">'
              '<link rel="icon" type="image/png" sizes="96x96" href="@a/icons/favicon-96.png"><link rel="apple-touch-icon" href="@a/icons/apple-touch-icon.png">')


def render(body):
    scripts = ('<script src="@a/site.js" defer></script>\n<script src="@a/k3.js" defer></script>\n<script type="module">\nimport { initCursorGrid } from \'@a/cursor-grid.js\';\n'
               + IB.GRID_START % IB.GRID_OPTS + '\n</script>')
    ld = ''.join('<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False).replace('</', '<\\/') + '</script>' for x in jsonld())
    head = (f'<title>{e(TITLE)}</title>\n<meta name="description" content="{ea(DESC)}">\n<meta name="author" content="Intelense Inc.">\n<meta name="theme-color" content="#0A34ED">\n{ICON_LINKS}\n'
            f'<meta name="robots" content="index, follow"><link rel="canonical" href="{SITE_URL}/">\n<meta property="og:type" content="website"><meta property="og:site_name" content="Ken360 by Intelense">'
            f'<meta property="og:url" content="{SITE_URL}/"><meta property="og:title" content="{ea(TITLE)}"><meta property="og:description" content="{ea(DESC)}">\n'
            f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{ea(TITLE)}"><meta name="twitter:description" content="{ea(DESC)}">\n{ld}\n{FONTS}\n'
            '<script>document.documentElement.classList.add("js")</script><link rel="stylesheet" href="@a/site.css">')
    return (f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n'
            f'{header()}\n<main id="top">\n  {body}\n</main>\n\n{footer()}\n{scripts}\n</body>\n</html>\n')


def resolve(html, version):
    html = html.replace('href="@index"', 'href="index.html"' if PREVIEW else 'href="/"')
    html = html.replace('@a/', 'assets/' if PREVIEW else '/assets/')
    if version:
        html = re.sub(r'((?:href|src)="[^"]*assets/[a-z0-9-]+\.(?:css|js))"', lambda m: m.group(1) + '?v=' + version + '"', html)
        html = re.sub(r"(from '[^']*assets/cursor-grid\.js)'", lambda m: m.group(1) + '?v=' + version + "'", html)
    return html


def deploy(out):
    out.mkdir(parents=True, exist_ok=True)
    css = (SITE_DIR / 'assets' / 'site.css').read_text() + '\n' + (HERE / 'assets-src' / 'k3.css').read_text() + '\n' + (HERE / 'assets-src' / 'k3-map.css').read_text()
    js = (HERE / 'assets-src' / 'k3.js').read_text() + '\n' + (HERE / 'assets-src' / 'k3-map.js').read_text()
    version = hashlib.md5((css + (SITE_DIR / 'assets' / 'site.js').read_text() + js).encode()).hexdigest()[:8]
    a = out / 'assets'
    a.mkdir(exist_ok=True)
    (a / 'site.css').write_text(css)
    (a / 'k3.js').write_text(js)
    for f in ('site.js', 'cursor-grid.js'):
        shutil.copy(SITE_DIR / 'assets' / f, a / f)
    shutil.copytree(SITE_DIR / 'assets' / 'icons', a / 'icons', dirs_exist_ok=True)
    shutil.copytree(HERE / 'assets-src' / 'logos', a / 'logos', dirs_exist_ok=True)
    (out / 'index.html').write_text(resolve(render(page_index()), None if PREVIEW else version))
    if not PREVIEW:
        (out / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n')
        (out / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>{SITE_URL}/</loc></url>\n</urlset>\n')
        shutil.copy(a / 'icons' / 'favicon.ico', out / 'favicon.ico')
    print('wrote the Ken360 home page to', out)


if __name__ == '__main__':
    if '--deploy' not in sys.argv:
        raise SystemExit(__doc__)
    deploy(Path(sys.argv[sys.argv.index('--deploy') + 1]))
