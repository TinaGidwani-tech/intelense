"""Build the Intelense static site.

Every page shares one header, footer and navigation, so all pages link to each other.
Run:  python3 site/build.py            -> writes site/*.html (uses assets/*.css and *.js)
      python3 site/build.py --inline DIR -> also writes a self-contained copy (CSS/JS inlined) to DIR
"""
import math
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / 'assets'
HOME_SOURCE = ROOT.parent / 'design' / 'mockups' / 'homepage-monad-style.html'

# ---------------------------------------------------------------- data

ICONS = {
    'eye': '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    'users': '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16 14.2c2.9.4 5 2.8 5 5.8"/>',
    'car': '<path d="M3 16v-4l2-5h14l2 5v4H3z"/><circle cx="7.5" cy="16.5" r="1.8"/><circle cx="16.5" cy="16.5" r="1.8"/><path d="M5 12h14"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    'box': '<path d="M3 7l9-4 9 4v10l-9 4-9-4V7z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    'hardhat': '<path d="M4 15a8 8 0 0116 0M2.5 15h19v2.5h-19zM12 7v4"/>',
    'zone': '<path d="M3 3h18v18H3z"/><path d="M3 9l6-6M3 15L15 3M3 21L21 3M9 21l12-12M15 21l6-6"/>',
    'fall': '<circle cx="14" cy="5" r="2"/><path d="M12 9l-4 4 4 3-2 5M12 9l5 2 2 4M4 21h16"/>',
    'forklift': '<path d="M3 18V9h6l3 5v4H3z"/><path d="M15 4v14h6"/><circle cx="6" cy="19" r="1.6"/><circle cx="11" cy="19" r="1.6"/>',
    'exit': '<path d="M14 3h6v18h-6M10 8l-4 4 4 4M6 12h10"/>',
    'chart': '<path d="M3 20h18"/><path d="M6 16v-5M11 16V7M16 16v-8M21 16v-3"/>',
    'home': '<path d="M3 11l9-7 9 7M5.5 9.5V20h13V9.5M10 20v-5h4v5"/>',
    'bell': '<path d="M12 3a6 6 0 016 6v4l2 3H4l2-3V9a6 6 0 016-6zM10 19a2 2 0 004 0"/>',
    'moon': '<path d="M20 14.5A8.5 8.5 0 019.5 4 8.5 8.5 0 1020 14.5z"/>',
    'filter': '<path d="M3 5h18l-7 8v6l-4 2v-8L3 5z"/>',
    'plug': '<path d="M9 3v5M15 3v5M6 8h12v3a6 6 0 01-12 0V8zM12 17v4"/>',
    'leaf': '<path d="M12 21V11M12 11c0-4 3-7 8-7 0 5-3 7-8 7zM12 14c0-3-2.5-5.5-7-5.5 0 4 2.5 5.5 7 5.5z"/>',
    'paw': '<circle cx="7" cy="9" r="1.8"/><circle cx="11" cy="6" r="1.8"/><circle cx="15" cy="6" r="1.8"/><circle cx="18" cy="9.5" r="1.8"/><path d="M8 17c0-3 2-5 4.5-5S17 14 17 17c0 2-1.5 3-4.5 3S8 19 8 17z"/>',
    'fence': '<path d="M4 21V6l2-2 2 2v15M11 21V6l2-2 2 2v15M18 21V6l2-2"/><path d="M2 10h20M2 16h20"/>',
    'tractor': '<circle cx="7" cy="16" r="4"/><circle cx="18" cy="17" r="2.5"/><path d="M7 12V6h6l2 6h4v3M13 6v6"/>',
    'thermo': '<path d="M10 14V5a2 2 0 014 0v9a4 4 0 11-4 0z"/><path d="M12 9v7"/>',
    'pulse': '<path d="M3 12h4l2-5 4 10 2-5h6"/>',
    'gauge': '<path d="M4 18a8 8 0 1116 0"/><path d="M12 18l4-6"/>',
    'air': '<path d="M3 9h11a3 3 0 10-3-3M3 15h15a3 3 0 11-3 3M3 12h8"/>',
    'bolt': '<path d="M13 2L4 14h7l-1 8 9-12h-7l1-8z"/>',
    'wrench': '<path d="M14 6a4 4 0 015 5l-8.5 8.5a2 2 0 01-3-3L16 8"/><path d="M14 6l4 4"/>',
    'route': '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h7a3 3 0 000-6H9a3 3 0 010-6h7"/>',
    'robot': '<rect x="5" y="8" width="14" height="10" rx="3"/><path d="M12 4v4M9 13h.01M15 13h.01M9 21h6"/>',
    'drone': '<circle cx="5" cy="5" r="2.5"/><circle cx="19" cy="5" r="2.5"/><circle cx="5" cy="19" r="2.5"/><circle cx="19" cy="19" r="2.5"/><path d="M7 7l3 3M17 7l-3 3M7 17l3-3M17 17l-3-3"/><rect x="10" y="10" width="4" height="4" rx="1"/>',
    'patrol': '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z"/><path d="M9 12l2 2 4-4"/>',
    'layers': '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    'mic': '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3"/>',
    'speaker': '<path d="M4 9h4l5-4v14l-5-4H4V9z"/><path d="M16.5 8.5a5 5 0 010 7M19 6a8.5 8.5 0 010 12"/>',
    'text': '<path d="M4 6h16M4 12h10M4 18h13"/>',
    'tag': '<path d="M3 12V4h8l10 10-8 8L3 12z"/><circle cx="7.5" cy="8.5" r="1.3"/>',
    'timeline': '<path d="M6 3v18"/><circle cx="6" cy="7" r="2"/><circle cx="6" cy="17" r="2"/><path d="M10 7h10M10 17h7"/>',
    'radio': '<rect x="5" y="8" width="14" height="13" rx="2"/><path d="M8 8l8-5M9 14h.01M15 13v3"/>',
}


def icon(name):
    return '<svg viewBox="0 0 24 24" aria-hidden="true">' + ICONS[name] + '</svg>'


MODULES = [
    dict(key='kenvision', name='KenVision', kind='Video analytics', color='#0A34ED', logo='kenvision.png', size=(783, 287),
         card='Turns existing CCTV into a real-time detection system. Find people, vehicles, intrusions and crowding as they happen, and search hours of footage in seconds.',
         h1='Turn every camera into a sensor that understands.',
         lede='KenVision runs computer vision on the CCTV you already have. It detects people, vehicles and unusual activity in real time, and makes hours of footage searchable in seconds.',
         caps=[('eye', 'Intrusion detection', 'Draw a zone on any camera and get an alert the moment someone enters it out of hours.'),
               ('users', 'Crowd density', 'Count people per zone and flag crowding before it becomes unsafe.'),
               ('car', 'Vehicle tracking', 'Follow vehicles across cameras and flag stops in fire lanes, loading bays or no-go areas.'),
               ('clock', 'Loitering and dwell time', 'Spot people or vehicles that stay too long in sensitive places.'),
               ('box', 'Objects left behind', 'Flag bags, boxes and equipment left unattended in public spaces.'),
               ('search', 'Video search', 'Search recorded footage by person, vehicle, colour or time instead of scrubbing through hours.')],
         steps=[('Connect', 'Point KenVision at the IP cameras you already run. No new cameras needed for most sites.'),
                ('Configure', 'Draw zones, choose what to detect and set who gets each alert.'),
                ('Act', 'Operators get a clip, a location and a confidence score, then acknowledge, escalate or dismiss.')],
         uses=[('public-safety', 'City and campus cameras', 'Faster detection and dispatch across hundreds of feeds.'),
               ('smart-cities', 'Streets and transit', 'Crowd, traffic and incident monitoring in real time.'),
               ('retail', 'Stores and malls', 'Loss prevention, queue length and after-hours intrusion.'),
               ('healthcare', 'Hospitals', 'Restricted areas, wandering patients and entrances.')],
         visual='console', related=['kensafety', 'keniot', 'kenvoice']),
    dict(key='kensafety', name='KenSafety', kind='Workplace safety', color='#FF7953', logo='kensafety.png', size=(793, 300),
         card='Spots missing PPE, unsafe zones, slips and falls, and alerts supervisors before a near miss becomes an injury.',
         h1='Catch the near miss before it becomes an injury.',
         lede='KenSafety watches your floors, docks and yards for the moments that lead to accidents, and tells supervisors while there is still time to step in.',
         caps=[('hardhat', 'PPE compliance', 'Checks for hard hats and hi-vis vests where your rules require them.'),
               ('zone', 'Restricted and hazard zones', 'Alerts when people enter areas around machinery, docks or chemicals.'),
               ('fall', 'Slips, trips and falls', 'Detects a person on the ground and raises an alert straight away.'),
               ('forklift', 'Forklift and pedestrian proximity', 'Flags close calls between vehicles and people on shared floors.'),
               ('exit', 'Blocked exits and walkways', 'Spots pallets and equipment left in emergency routes.'),
               ('chart', 'Safety trends', 'Weekly reports show where and when risks cluster, so you can fix the cause.')],
         steps=[('Map your rules', 'Mark PPE zones, hazard areas and walkways on your existing camera views.'),
                ('Watch every shift', 'KenSafety checks every frame against those rules, around the clock.'),
                ('Coach, not just catch', 'Supervisors get the clip and context, and trends show where training helps most.')],
         uses=[('industrial', 'Warehouses and logistics', 'Docks, aisles and shared forklift floors.'),
               ('industrial', 'Manufacturing plants', 'Machine guarding zones and PPE areas.'),
               ('industrial', 'Construction sites', 'Hard hats, exclusion zones and site perimeters.'),
               ('healthcare', 'Healthcare facilities', 'Staff and patient falls in corridors and wards.')],
         visual='safety', related=['kenvision', 'keniot', 'kenrobotics']),
    dict(key='kenhome', name='KenHome', kind='Smart home security', color='#78AFCF', logo='kenhome.png', size=(793, 300),
         card='Knows a family member from a stranger at the door and cuts the false alarms that make people ignore alerts.',
         h1="Know who's at the door, not just that someone is.",
         lede='KenHome adds real understanding to home cameras and doorbells. It tells household members from visitors, spots packages, and stays quiet when a car or a cat goes by.',
         caps=[('users', 'Household and visitors', 'Recognises the household members you enrol and flags unknown visitors.'),
               ('box', 'Package detection', 'Tells you when a parcel arrives, and when it leaves.'),
               ('filter', 'Fewer false alarms', 'Ignores passing cars, pets, shadows and swaying trees.'),
               ('moon', 'Night-time analytics', 'Works on infrared footage, when most break-ins happen.'),
               ('bell', 'Smart notifications', 'One clear alert with a snapshot, not a stream of motion pings.'),
               ('plug', 'Works with your cameras', 'Built to run on common doorbells and IP cameras.')],
         steps=[('Connect', 'Link your doorbell or home cameras to KenHome.'),
                ('Enrol your household', 'Add the people who live with you, so they never trigger an alert.'),
                ('Get alerts that matter', 'Unknown visitors, packages and late-night activity, with a snapshot.')],
         uses=[('residential', 'Homeowners', 'Front doors, driveways and back yards.'),
               ('residential', 'Property managers', 'Entrances and lobbies across multi-residential buildings.'),
               ('residential', 'Security installers', 'A smarter layer on top of the cameras you already fit.'),
               ('residential', 'Short-term rentals', 'Know when guests arrive and leave, without watching footage.')],
         visual='home', related=['kenvision', 'kenvoice', 'keniot']),
    dict(key='kenagri', name='KenAgri', kind='Precision agriculture', color='#368736', logo='kenagri.png', size=(673, 300),
         card='Watches crops, livestock and field perimeters to flag stress, disease and intrusions early.',
         h1='Eyes on every field, pen and fence line.',
         lede='KenAgri turns farm cameras and drones into an early-warning system for crops, livestock and property, day and night.',
         caps=[('leaf', 'Crop stress and disease', 'Flags patches that look different from the rest of the field so you can check them early.'),
               ('paw', 'Livestock monitoring', 'Counts animals and spots unusual behaviour in pens and pastures.'),
               ('fence', 'Perimeter and wildlife', 'Alerts when people or wildlife cross a fence line at night.'),
               ('tractor', 'Equipment and yard security', 'Watches machinery, fuel tanks and storage outside working hours.'),
               ('drone', 'Drone footage analysis', 'Runs the same analytics on drone flights over large fields.'),
               ('moon', 'Thermal and low light', 'Works on thermal and infrared cameras after dark.')],
         steps=[('Cover the farm', 'Use existing yard cameras, add field cameras, or upload drone flights.'),
                ('Set what matters', 'Choose fields, pens and fence lines to watch, and what counts as unusual.'),
                ('Act early', 'Get alerts with location and a snapshot, and track issues across the season.')],
         uses=[('agriculture', 'Row crops', 'Stress and disease patches, irrigation issues.'),
               ('agriculture', 'Greenhouses', 'Plant health and climate-related issues across rows.'),
               ('agriculture', 'Livestock farms', 'Counts, behaviour and predator alerts.'),
               ('agriculture', 'Orchards and vineyards', 'Perimeter security and canopy checks.')],
         visual='agri', related=['keniot', 'kenrobotics', 'kenvision']),
    dict(key='keniot', name='KenIoT', kind='Predictive monitoring', color='#7C28E9', logo='keniot.png', size=(643, 287),
         card='Reads equipment and environmental sensors to predict failures and send maintenance teams before anything breaks.',
         h1='Hear the machine before it fails.',
         lede='KenIoT reads vibration, temperature, power and environmental sensors, learns what normal looks like, and warns you when something starts to drift.',
         caps=[('pulse', 'Vibration and temperature', 'Continuous readings from motors, pumps, compressors and conveyors.'),
               ('gauge', 'Anomaly detection', 'Learns each machine\'s normal pattern and flags drift early.'),
               ('wrench', 'Failure prediction', 'Estimates how long until a part needs attention, so you can plan the fix.'),
               ('air', 'Environmental sensing', 'Air quality, humidity and temperature across rooms and cold chain.'),
               ('bolt', 'Energy monitoring', 'Spots machines drawing more power than they should.'),
               ('bell', 'Alerts to the right team', 'Maintenance gets the reading, the trend and the asset location.')],
         steps=[('Connect sensors', 'Bring in the sensors you have, or add new ones where you need them.'),
                ('Learn normal', 'KenIoT builds a baseline for each asset over its first weeks of data.'),
                ('Fix before failure', 'Drift becomes an alert and a work order, not a breakdown.')],
         uses=[('industrial', 'Manufacturing lines', 'Motors, pumps and conveyors.'),
               ('industrial', 'Cold chain', 'Freezers, trucks and storage temperatures.'),
               ('smart-cities', 'Buildings and HVAC', 'Air handling, chillers and indoor air quality.'),
               ('smart-cities', 'Utilities', 'Pumping stations and remote equipment.')],
         visual='iot', related=['kensafety', 'kenvision', 'kenrobotics']),
    dict(key='kenrobotics', name='KenRobotics', kind='Autonomous systems', color='#6C6E82', logo='kenrobotics.png', size=(919, 300),
         card='Gives robots and drones the vision to navigate, inspect and patrol on their own.',
         h1='Vision that lets machines find their own way.',
         lede='KenRobotics gives robots and drones the perception they need to move safely, patrol and inspect, and reports what they see to the same dashboard as your cameras.',
         caps=[('robot', 'Obstacle detection', 'Sees pallets, people and vehicles in the path and reacts in time.'),
               ('route', 'Navigation support', 'Feeds path and free-space information to the robot\'s planner.'),
               ('patrol', 'Autonomous patrol', 'Runs security rounds and reports anything unusual along the route.'),
               ('search', 'Inspection', 'Checks gauges, leaks, damage and blocked access on each pass.'),
               ('drone', 'Drone analytics', 'Detection and tracking from the air, on the same engine.'),
               ('layers', 'One fleet view', 'Robot and drone events sit next to your fixed cameras.')],
         steps=[('Connect the robot', 'Stream the robot or drone camera to KenRobotics.'),
                ('Define the mission', 'Set routes, inspection points and what should trigger an alert.'),
                ('Review the run', 'Each patrol produces a timeline of what was seen, with clips.')],
         uses=[('industrial', 'Warehouses', 'Autonomous carts and inventory robots.'),
               ('public-safety', 'Security patrol', 'Robot and drone rounds of large sites.'),
               ('smart-cities', 'Infrastructure inspection', 'Bridges, tunnels, substations and pipelines.'),
               ('agriculture', 'Field robotics', 'Drones and ground robots across large farms.')],
         visual='robotics', related=['kenvision', 'kenagri', 'keniot']),
    dict(key='kenvoice', name='KenVoice', kind='Voice AI', color='#5466DD', logo='kenvoice.png', size=(792, 300), new=True,
         card='Brings voice into the platform: spoken alerts, hands-free commands and call transcription that feed the same incident timeline.',
         h1='Let your sites speak, and listen.',
         lede='KenVoice, our newest module, adds voice to the Ken platform. It speaks alerts, takes hands-free commands, and turns calls and radio traffic into searchable text on the same incident timeline.',
         caps=[('speaker', 'Spoken alerts', 'Plays clear voice alerts on site speakers and radios when an event fires.'),
               ('mic', 'Hands-free commands', 'Workers and operators can query and acknowledge alerts by voice.'),
               ('text', 'Call and radio transcription', 'Turns calls and radio traffic into searchable text.'),
               ('tag', 'Keyword detection', 'Listens for words like "help" or "fire" and raises an alert.'),
               ('timeline', 'One incident timeline', 'Voice, video and sensor events land in the same place.'),
               ('radio', 'Works with your devices', 'Built to connect to speakers, radios and phone lines.')],
         steps=[('Connect audio', 'Link speakers, radios, phone lines or microphones.'),
                ('Choose the words', 'Set the keywords, commands and alerts that matter on each site.'),
                ('Close the loop', 'Every spoken alert and response is logged with the incident.')],
         uses=[('public-safety', 'Dispatch and response', 'Transcribed calls and radio linked to camera events.'),
               ('industrial', 'Industrial sites', 'Hands-free alerts and commands for workers.'),
               ('healthcare', 'Healthcare', 'Staff calls and distress keywords on wards.'),
               ('residential', 'Smart homes', 'Spoken alerts and voice control with KenHome.')],
         visual='voice', related=['kenvision', 'kenhome', 'kensafety']),
]
MOD = {m['key']: m for m in MODULES}

INDUSTRIES = [
    dict(id='public-safety', name='Public safety', title='Public safety and emergency response',
         text='Police, fire, campus and municipal teams watch hundreds of feeds with small teams. Intelense surfaces the moments that matter and links them to calls and radio traffic, so responders arrive informed.',
         uses=[('Intrusion and after-hours alerts', 'Parks, schools and municipal buildings.'), ('Crowd and incident detection', 'Events, transit hubs and public squares.'), ('Calls linked to cameras', 'Transcribed calls next to the matching video.')],
         mods=['kenvision', 'kenvoice', 'kenrobotics']),
    dict(id='smart-cities', name='Smart cities', title='Smart cities and infrastructure',
         text='Streets, transit and utilities generate more data than any team can watch. Intelense turns cameras and sensors into live signals for traffic, crowds and asset health.',
         uses=[('Traffic and crowd flow', 'Intersections, stations and busy streets.'), ('Infrastructure health', 'Pumps, HVAC and remote equipment.'), ('Inspection at scale', 'Drones and robots on bridges, tunnels and substations.')],
         mods=['kenvision', 'keniot', 'kenrobotics']),
    dict(id='retail', name='Retail', title='Retail and commercial spaces',
         text='Stores and malls already have cameras. Intelense uses them to cut losses, shorten queues and keep staff and shoppers safe.',
         uses=[('Loss prevention', 'Suspicious behaviour and after-hours intrusion.'), ('Queues and footfall', 'Queue length and busy-hour staffing.'), ('Safety on the floor', 'Slips, blocked exits and stockroom hazards.')],
         mods=['kenvision', 'kensafety']),
    dict(id='healthcare', name='Healthcare', title='Hospitals and care facilities',
         text='Care teams cannot watch every corridor. Intelense flags falls, restricted-area access and calls for help so staff can respond quickly.',
         uses=[('Falls and wandering', 'Corridors, wards and exits.'), ('Restricted areas', 'Pharmacies, labs and staff-only zones.'), ('Calls for help', 'Distress keywords and staff calls.')],
         mods=['kenvision', 'kensafety', 'kenvoice']),
    dict(id='industrial', name='Industrial', title='Industrial sites and workplaces',
         text='Warehouses, plants and construction sites combine people, vehicles and heavy machines. Intelense watches all three and warns before accidents and breakdowns.',
         uses=[('PPE and hazard zones', 'Hard hats, vests and machinery exclusion zones.'), ('Forklift safety', 'Close calls between vehicles and pedestrians.'), ('Predictive maintenance', 'Motors, conveyors and compressors.')],
         mods=['kensafety', 'keniot', 'kenrobotics', 'kenvision']),
    dict(id='agriculture', name='Agriculture', title='Farms and agriculture',
         text='Large properties are hard to watch, especially at night. Intelense covers fields, pens and fence lines with cameras, drones and sensors.',
         uses=[('Crop health', 'Stress and disease patches, spotted early.'), ('Livestock', 'Counts, behaviour and predators.'), ('Property and equipment', 'Fence lines, yards and fuel storage.')],
         mods=['kenagri', 'keniot', 'kenrobotics']),
    dict(id='residential', name='Residential', title='Homes and residential buildings',
         text='Homeowners and property managers want alerts they can trust. Intelense tells residents from visitors and ignores the motion that does not matter.',
         uses=[('Front door and packages', 'Visitors, deliveries and porch activity.'), ('Building entrances', 'Lobbies, garages and shared spaces.'), ('Voice alerts', 'Spoken alerts and hands-free control.')],
         mods=['kenhome', 'kenvoice', 'kenvision']),
]
IND = {i['id']: i for i in INDUSTRIES}

NAV = [('platform.html', 'Platform'), ('modules.html', 'Modules'), ('industries.html', 'Industries'), ('about.html', 'Company')]

# ---------------------------------------------------------------- shared fragments


def logo_img(m, scale=0.22, cls='mod-logo'):
    w, h = m['size']
    return f'<img class="{cls}" src="assets/logos/{m["logo"]}" alt="{m["name"]} by Intelense" width="{round(w * scale)}" height="{round(h * scale)}">'


def header(active):
    links = []
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active or (href == 'modules.html' and active in MOD) else ''
        if href == 'modules.html':
            items = ''.join(f'<li><a href="{m["key"]}.html" style="--mod:{m["color"]}"><i></i>{m["name"]}<small>{m["kind"]}</small></a></li>' for m in MODULES)
            items += '<li><a href="modules.html#compare">Compare all modules</a></li>'
            links.append(f'<li class="has-menu"><a href="modules.html"{cur}>Modules</a><div class="dropdown"><ul>{items}</ul></div></li>')
        else:
            links.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    mobile = ''.join(f'<a href="{h}">{l}</a>' + (''.join(f'<a class="sub" href="{m["key"]}.html">{m["name"]}</a>' for m in MODULES) if h == 'modules.html' else '') for h, l in NAV)
    return f'''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="brand-g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0A34ED"/><stop offset=".3" stop-color="#7C28E9"/><stop offset=".6" stop-color="#FF7953"/><stop offset=".82" stop-color="#78AFCF"/><stop offset="1" stop-color="#73C4C5"/>
    </linearGradient>
  </defs>
</svg>

<div class="announce">
  <div class="wrap">
    <span><span class="tag-new">New</span>&nbsp; KenVoice joins the Ken platform as our seventh module</span>
    <a class="pill" href="kenvoice.html">See KenVoice</a>
  </div>
</div>

<header class="nav">
  <div class="wrap">
    <a class="logo" href="index.html"><img src="assets/logos/intelense.png" alt="Intelense home" width="169" height="26"></a>
    <ul class="nav-links">
      {''.join(links)}
    </ul>
    <div class="nav-cta">
      <a class="btn btn-ghost" href="contact.html">Contact</a>
      <a class="btn btn-blue" href="contact.html">Book a demo</a>
      <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Menu"><span></span></button>
    </div>
  </div>
  <nav class="mobile-menu" id="mobile-menu" hidden aria-label="Mobile">
    <div class="wrap">
      <a href="index.html">Home</a>{mobile}<a href="contact.html">Contact</a>
      <a class="btn btn-blue" href="contact.html">Book a demo</a>
    </div>
  </nav>
</header>
'''


def footer():
    mods = ''.join(f'<li><a href="{m["key"]}.html">{m["name"]}</a></li>' for m in MODULES)
    return f'''<footer>
  <div class="wrap">
    <div class="foot">
      <div>
        <a class="logo" href="index.html"><img src="assets/logos/intelense-light.png" alt="Intelense home" width="169" height="26"></a>
        <p style="margin-top:16px;max-width:34ch">AI video analytics and intelligence at the edge, for a safer world.</p>
      </div>
      <div>
        <h4>Platform</h4>
        <ul><li><a href="platform.html">How it works</a></li><li><a href="platform.html#console">Live console</a></li><li><a href="platform.html#integrations">Integrations</a></li><li><a href="modules.html">All modules</a></li><li><a href="modules.html#compare">Compare modules</a></li></ul>
      </div>
      <div>
        <h4>Modules</h4>
        <ul>{mods}</ul>
      </div>
      <div>
        <h4>Company</h4>
        <ul><li><a href="about.html">About Intelense</a></li><li><a href="industries.html">Industries</a></li><li><a href="index.html#faq">FAQ</a></li><li><a href="contact.html">Contact</a></li><li><a href="contact.html">Book a demo</a></li></ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul><li class="email">enquiries@intelense.ca</li><li>Markham, Ontario, Canada</li></ul>
      </div>
    </div>
    <div class="legal"><span>© 2026 Intelense Inc.</span><span>Sample site concept</span></div>
  </div>
</footer>
'''


def crumbs(*items):
    out = ['<li><a href="index.html">Home</a></li>']
    for href, label in items:
        out.append(f'<li><a href="{href}">{label}</a></li>' if href else f'<li aria-current="page">{label}</li>')
    return f'<ol class="crumbs" aria-label="Breadcrumb">{"".join(out)}</ol>'


def page_hero(crumb, eyebrow, h1, lede, ctas, extra=''):
    return f'''<section class="page-hero">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap">
      {crumb}
      <span class="eyebrow">{eyebrow}</span>
      {extra}
      <h1>{h1}</h1>
      <p class="lede">{lede}</p>
      <div class="hero-ctas">{ctas}</div>
    </div>
  </section>'''


def head_block(eyebrow, h2, lede):
    return f'''<div class="head">
        <div>
          <span class="eyebrow">{eyebrow}</span>
          <h2>{h2}</h2>
        </div>
        <p class="lede">{lede}</p>
      </div>'''


def cta_band(h2='See Intelense on your own footage.', second=('modules.html', 'Compare modules')):
    return f'''<section class="cta">
    <div class="wash wash-b" aria-hidden="true" style="top:10%;right:20%"></div>
    <div class="wash wash-a" aria-hidden="true" style="top:30%;left:20%"></div>
    <div class="wrap">
      <span class="eyebrow">Get started</span>
      <h2 style="margin-top:20px">{h2}</h2>
      <div class="hero-ctas">
        <a class="btn btn-blue" href="contact.html">Book a demo</a>
        <a class="btn btn-black" href="{second[0]}">{second[1]}</a>
      </div>
    </div>
  </section>'''


def card(m):
    tag = '<span class="tag-new">New</span>' if m.get('new') else ''
    return f'''<article style="--mod:{m["color"]}" class="card">
          <div class="card-top"><span class="kind">{m["kind"]}</span>{tag}</div>
          <h3><a href="{m["key"]}.html">{logo_img(m)}</a></h3>
          <p>{m["card"]}</p>
          <a class="link-arrow" href="{m["key"]}.html">Learn more</a>
        </article>'''


def module_grid():
    v = MOD['kenvision']
    feature = f'''<article style="--mod:{v["color"]}" class="card feature">
          <div class="feat-copy">
            <div class="card-top" style="margin-bottom:6px"><span class="kind">{v["kind"]}</span></div>
            <h3><a href="kenvision.html">{logo_img(v, 0.36)}</a></h3>
            <p>{v["card"]}</p>
            <div class="chips"><span class="chip">Intrusion</span><span class="chip">Crowd density</span><span class="chip">Vehicle tracking</span><span class="chip">Video search</span></div>
            <a class="link-arrow" href="kenvision.html">Explore KenVision</a>
          </div>
          <div class="snap" role="img" aria-label="Simulated plaza camera with a crowd-density heatmap and a live people count for zone A">
            <canvas class="cctv" data-scene="plaza" width="800" height="600"></canvas>
            <div class="snap-ui"><span class="lvl">High density</span><span>Zone A · <b id="crowd-count">26</b> people</span><span class="snap-legend">Density <i></i></span></div>
          </div>
        </article>'''
    return '<div class="modules">\n        ' + feature + '\n        ' + '\n        '.join(card(m) for m in MODULES[1:]) + '\n      </div>'


def mod_chips(keys):
    return '<div class="mod-chips">' + ''.join(f'<a href="{k}.html" style="--mod:{MOD[k]["color"]}">{MOD[k]["name"]}</a>' for k in keys) + '</div>'


def sector_links():
    return '<div class="sectors">' + ''.join(f'<a href="industries.html#{i["id"]}">{i["name"]}</a>' for i in INDUSTRIES) + '</div>'


def sparkline(vals, color, w=200, h=44):
    lo, hi = min(vals), max(vals)
    pts = ' '.join(f'{i * w / (len(vals) - 1):.1f},{h - 4 - (v - lo) / ((hi - lo) or 1) * (h - 8):.1f}' for i, v in enumerate(vals))
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" aria-hidden="true"><polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>'


def checklist(title, rows):
    lis = ''.join(f'<li><span class="dot{" bad" if bad else ""}"></span><span>{text}</span><span class="st{" bad" if bad else ""}">{st}</span></li>' for text, st, bad in rows)
    return f'<div class="panel"><h3>{title}</h3><ul class="checklist">{lis}</ul><p class="demo-note">Example data</p></div>'


def tile(scene, osd=None, w=960, h=540):
    o = f' data-osd="{osd}"' if osd else ''
    return f'<div class="tile-solo"><canvas class="cctv" data-scene="{scene}"{o} width="{w}" height="{h}"></canvas></div>'


# ---------------------------------------------------------------- home page sections (reused from the approved homepage)

_home = HOME_SOURCE.read_text()
_main = _home[_home.index('<main id="top">') + len('<main id="top">'):_home.index('</main>')].replace('src="logos/', 'src="assets/logos/')


def home_section(sid=None, cls=None):
    pat = r'\s*<section class="%s"[^>]*>.*?</section>' % re.escape(cls) if cls else r'\s*<section class="[^"]*" id="%s">.*?</section>' % re.escape(sid)
    return re.search(pat, _main, re.S).group(0).strip()


HERO = home_section(cls='hero').replace('href="#demo-cta"', 'href="contact.html"').replace('href="#modules"', 'href="modules.html"')
FLOW_SECTION = home_section('platform')
FLOW = FLOW_SECTION[FLOW_SECTION.index('<div class="flow"'):FLOW_SECTION.rindex('\n    </div>\n  </section>')]
CONSOLE_SECTION = home_section('live')
CONSOLE = CONSOLE_SECTION[CONSOLE_SECTION.index('<div class="console"'):CONSOLE_SECTION.index('<p class="demo-note">')].rstrip()
FAQ = home_section('faq')

# ---------------------------------------------------------------- pages


def page_index():
    platform = FLOW_SECTION.replace('</div>\n    </div>\n  </section>', '</div>\n      <p style="margin-top:32px"><a class="link-arrow" href="platform.html">See how the platform works</a></p>\n    </div>\n  </section>', 1)
    live = CONSOLE_SECTION.replace('<p class="demo-note">Simulated camera feeds and example data. Not a real site or customer.</p>',
                                   '<p class="demo-note">Simulated camera feeds and example data. Not a real site or customer.</p>\n      <p style="margin-top:20px"><a class="link-arrow" href="kenvision.html">Explore KenVision</a></p>')
    modules = f'''<section class="block" id="modules">
    <div class="wrap">
      {head_block('The Ken platform', 'Seven modules. One platform.', "Start with the module that solves today's problem. Add others as you grow, on the same engine and the same dashboard.")}
      {module_grid()}
      <p style="margin-top:32px"><a class="link-arrow" href="modules.html#compare">Compare all seven modules</a></p>
    </div>
  </section>'''
    sectors = f'''<section class="block" id="sectors">
    <div class="wrap">
      {head_block('Industries', "Built for places where safety can't wait.", 'Our mission is a safer world, starting with public safety. The same platform serves teams across these sectors.')}
      {sector_links()}
      <div class="proof">
        <span class="lbl">Supported by</span>
        <span class="mark">CENGN</span>
        <span class="mark">VentureLab</span>
        <a class="link-arrow" href="about.html" style="margin-left:auto">About Intelense</a>
      </div>
    </div>
  </section>'''
    faq = FAQ.replace('<p>Book a demo. We', '<p><a href="contact.html">Book a demo</a>. We').replace('<summary>What is KenVoice?</summary>\n          <p>KenVoice is our newest module.', '<summary>What is KenVoice?</summary>\n          <p><a href="kenvoice.html">KenVoice</a> is our newest module.')
    body = '\n\n  '.join([HERO, platform, live, modules, sectors, faq, cta_band()])
    return dict(file='index.html', title='Intelense | AI Video Analytics & Intelligence at the Edge',
                desc='Intelense turns live video, sensor and voice data into real-time alerts. Seven Ken modules on one AI platform.',
                active='index.html', body=body, cctv=True)


def page_platform():
    hero = page_hero(crumbs((None, 'Platform')), 'The Intelense platform', 'One engine for every camera, sensor and voice on site.',
                     'Intelense connects to the devices you already run, understands what they see and hear at the edge, and sends each event to the people who need it.',
                     '<a class="btn btn-blue" href="contact.html">Book a demo</a><a class="btn btn-ghost" href="modules.html">Explore the modules</a>')
    flow = f'''<section class="block" id="how">
    <div class="wrap">
      {head_block('How it works', 'From every sensor to the right response.', 'Connect the cameras and devices you already run. Intelense watches, listens and understands them, then sends each event where it needs to go.')}
      {FLOW}
    </div>
  </section>'''
    edge = f'''<section class="block" id="edge">
    <div class="wrap">
      {head_block('Built for the edge', 'Analytics close to the camera.', 'Processing near the source keeps alerts fast and keeps bandwidth low. The same engine powers every Ken module.')}
      <div class="caps">
        <div class="cap">{icon('plug')}<h3>At the edge</h3><p>Video and sensor data is analysed on site, close to your cameras, so alerts arrive in seconds and raw footage does not have to leave the building.</p></div>
        <div class="cap">{icon('layers')}<h3>In the Intelense engine</h3><p>Detection, tracking, voice and sensor models share one engine, so adding a module adds capability, not another system.</p></div>
        <div class="cap">{icon('bell')}<h3>With your teams</h3><p>Alerts, dashboards and reports reach operators, supervisors and responders on the devices they already use.</p></div>
      </div>
    </div>
  </section>'''
    console = f'''<section class="block" id="console">
    <div class="wrap">
      {head_block('The operator console', 'One screen for every site.', 'Live feeds, alerts and trends sit together, so operators review events instead of watching screens.')}
      {CONSOLE}
      <p class="demo-note">Simulated camera feeds and example data. Not a real site or customer.</p>
    </div>
  </section>'''
    chips = ['IP cameras (RTSP / ONVIF)', 'Video management systems', 'Drones and body cams', 'IoT and industrial sensors', 'Radios, speakers and phone lines', 'Access control', 'Email, SMS and push alerts', 'Webhooks and APIs']
    integ = f'''<section class="block" id="integrations">
    <div class="wrap">
      {head_block('Integrations', 'Works with what you already run.', 'No rip-and-replace. Intelense is built to connect to common cameras, sensors and alerting tools.')}
      <div class="chips" style="gap:10px">{''.join(f'<span class="chip" style="padding:12px 18px;font-size:13px">{c}</span>' for c in chips)}</div>
      <ul class="uses" style="margin-top:48px">
        <li><b>On-site edge</b><span>Analytics run on hardware at your site, next to your cameras.</span></li>
        <li><b>Cloud</b><span>Central dashboards and reporting across many sites.</span></li>
        <li><b>Hybrid</b><span>Edge processing for speed, cloud for oversight and search.</span></li>
        <li><b>Pilot first</b><span>Start on a few cameras and prove results before rolling out.</span></li>
      </ul>
    </div>
  </section>'''
    mods = f'''<section class="block" id="modules">
    <div class="wrap">
      {head_block('Modules', 'Seven ways to use the same engine.', 'Each module is built on the platform above. Pick one to see what it does.')}
      {mod_chips([m['key'] for m in MODULES])}
    </div>
  </section>'''
    body = '\n\n  '.join([hero, flow, edge, console, integ, mods, cta_band()])
    return dict(file='platform.html', title='Platform | Intelense', desc='How the Intelense AI platform connects cameras, sensors and voice at the edge and turns them into real-time alerts.',
                active='platform.html', body=body, cctv=True)


def page_modules():
    hero = page_hero(crumbs((None, 'Modules')), 'The Ken platform', 'Seven modules. One engine.',
                     "Start with the module that solves today's problem. Every module runs on the same engine and dashboard, so adding the next one is simple.",
                     '<a class="btn btn-blue" href="contact.html">Book a demo</a><a class="btn btn-ghost" href="#compare">Compare modules</a>')
    grid = f'''<section class="block" id="all">
    <div class="wrap">
      {module_grid()}
    </div>
  </section>'''
    rows = []
    watch = {'kenvision': 'CCTV and IP cameras', 'kensafety': 'Cameras on floors, docks and sites', 'kenhome': 'Doorbells and home cameras',
             'kenagri': 'Farm cameras, thermal and drones', 'keniot': 'Vibration, temperature, power and air sensors',
             'kenrobotics': 'Robot and drone cameras', 'kenvoice': 'Speakers, radios, phones and microphones'}
    alerts = {'kenvision': 'Intrusion, crowding, loitering, vehicles', 'kensafety': 'Missing PPE, hazard zones, falls, close calls',
              'kenhome': 'Unknown visitors, packages, night activity', 'kenagri': 'Crop stress, livestock, wildlife, intruders',
              'keniot': 'Drift, overheating, predicted failures', 'kenrobotics': 'Obstacles, patrol findings, inspection issues',
              'kenvoice': 'Keywords, calls for help, spoken alerts'}
    best = {m['key']: sorted({u[0] for u in m['uses']}, key=[i['id'] for i in INDUSTRIES].index) for m in MODULES}
    for m in MODULES:
        inds = ', '.join(f'<a href="industries.html#{i}">{IND[i]["name"]}</a>' for i in best[m['key']])
        rows.append(f'<tr><td><a href="{m["key"]}.html" style="--mod:{m["color"]}">{m["name"]}</a></td><td>{watch[m["key"]]}</td><td>{alerts[m["key"]]}</td><td>{inds}</td></tr>')
    table = f'''<section class="block" id="compare">
    <div class="wrap">
      {head_block('Compare', 'Which module fits your site?', 'A quick view of what each module watches, what it alerts on and where it is used most.')}
      <div class="table-wrap"><table>
        <thead><tr><th>Module</th><th>Watches</th><th>Typical alerts</th><th>Best for</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table></div>
    </div>
  </section>'''
    body = '\n\n  '.join([hero, grid, table, cta_band('Not sure where to start?', ('platform.html', 'See the platform'))])
    return dict(file='modules.html', title='Ken modules | Intelense', desc='The seven Ken modules: KenVision, KenSafety, KenHome, KenAgri, KenIoT, KenRobotics and KenVoice.',
                active='modules.html', body=body, cctv=True)


def module_visual(m):
    v = m['visual']
    if v == 'console':
        return CONSOLE + '\n      <p class="demo-note">Simulated camera feeds and example data. Not a real site or customer.</p>'
    if v == 'safety':
        return '<div class="split">' + tile('dock') + checklist('PPE check · CAM-04', [
            ('Worker A: hard hat and vest', 'OK', False), ('Worker B: no hard hat in restricted zone', 'Alert', True),
            ('Forklift: inside speed limit', 'OK', False), ('Walkway 2: clear', 'OK', False)]) + '</div>'
    if v == 'home':
        return '<div class="split">' + tile('porch') + checklist('Front door · today', [
            ('Unknown visitor at the door, 14:31', 'Alert', True), ('Package delivered, 14:32', 'Info', False),
            ('Household member arrived, 17:05', 'Quiet', False), ('Passing car ignored, 17:40', 'Quiet', False)]) + '</div>'
    if v == 'agri':
        return '<div class="split">' + tile('field') + checklist('Field 3 · tonight', [
            ('Deer near north fence, 21:14', 'Alert', True), ('Crop stress patch, row 14', 'Review', True),
            ('Equipment yard: no activity', 'OK', False), ('Gate 2: closed', 'OK', False)]) + '</div>'
    if v == 'robotics':
        return '<div class="split">' + tile('robot', 'ROBOT-03  FRONT CAMERA') + checklist('ROBOT-03 · Aisle 7 patrol', [
            ('Pallet blocking path, rerouting', 'Alert', True), ('Person ahead, slowing down', 'Info', False),
            ('Patrol progress: 4 of 6 aisles', 'OK', False), ('Battery 76%', 'OK', False)]) + '</div>'
    if v == 'iot':
        s1 = sparkline([2.1, 2.2, 2.1, 2.3, 2.2, 2.4, 2.6, 2.8, 3.1, 3.4, 3.9, 4.2], '#FF7953')
        s2 = sparkline([61, 62, 61, 63, 62, 64, 63, 65, 64, 66, 67, 68], '#A98BF5')
        s3 = sparkline([3.9, 4.0, 3.8, 3.9, 4.1, 4.0, 3.9, 4.0, 4.1, 4.0, 3.9, 4.0], '#73C4C5')
        s4 = sparkline([44, 43, 45, 44, 42, 43, 44, 45, 43, 44, 44, 43], '#73C4C5')
        dash = f'''<div class="iot" role="img" aria-label="KenIoT dashboard with four sensor readings and a predicted failure alert">
        <div class="iot-top"><b style="color:#e9e9ec;font-size:14px">Line 2 · Compressor C-3</b><span>Updated 14:32</span></div>
        <div class="iot-grid">
          <div class="sensor warn"><div class="lbl"><span>Vibration</span><span class="tag">Rising</span></div><div class="val">4.2 <small>mm/s</small></div>{s1}</div>
          <div class="sensor"><div class="lbl"><span>Bearing temp</span><span class="tag">Watch</span></div><div class="val">68 <small>°C</small></div>{s2}</div>
          <div class="sensor"><div class="lbl"><span>Power draw</span><span class="tag">Normal</span></div><div class="val">4.0 <small>kW</small></div>{s3}</div>
          <div class="sensor"><div class="lbl"><span>Humidity</span><span class="tag">Normal</span></div><div class="val">44 <small>%</small></div>{s4}</div>
        </div>
        <div class="iot-alert"><b>Bearing wear likely on C-3</b><span>Vibration has risen steadily for 9 days. Suggested: inspect before next weekend shift.</span></div>
      </div>'''
        return '<div class="split">' + dash + checklist('Flagged this week', [
            ('Compressor C-3: vibration drift', 'Alert', True), ('Freezer F-1: door left open twice', 'Review', True),
            ('Conveyor B: normal', 'OK', False), ('Air quality, packing room: normal', 'OK', False)]) + '</div>'
    if v == 'voice':
        bars = ''.join(f'<i style="--h:{round(14 + 40 * abs(math.sin(i * 0.7) * math.cos(i * 0.23)))}px;--d:-{(i % 9) * 0.13:.2f}s"></i>' for i in range(56))
        panel = f'''<div class="voice" role="img" aria-label="KenVoice panel with a live audio waveform, a transcript and the actions taken">
        <div class="iot-top"><b style="color:#e9e9ec;font-size:14px">Radio channel 2 · Site 2</b><span class="c-live">Live</span></div>
        <div class="wave">{bars}</div>
        <ul class="transcript">
          <li><time>14:31:58</time><div><b>Supervisor</b>Can someone check dock B, the camera flagged a worker without a hard hat.</div></li>
          <li><time>14:32:06</time><div><b>Worker</b>On it. Also need <mark>help</mark> moving a pallet blocking walkway two.</div></li>
          <li><time>14:32:07</time><div><b>KenVoice</b>Alert raised: keyword "help", dock B. Spoken notice sent to zone B speakers.</div></li>
        </ul>
        <div class="voice-acts"><span class="hot">Keyword: help</span><span>Linked to CAM-04 alert</span><span>Added to incident timeline</span></div>
      </div>'''
        return '<div class="split">' + panel + checklist('What KenVoice did', [
            ('Transcribed radio channel 2', 'Done', False), ('Detected keyword "help"', 'Alert', True),
            ('Spoke a notice on zone B speakers', 'Done', False), ('Linked audio to the CAM-04 clip', 'Done', False)]) + '</div>'
    raise ValueError(v)


def page_module(m):
    i = MODULES.index(m)
    prev_m, next_m = MODULES[i - 1], MODULES[(i + 1) % len(MODULES)]
    tag = ' <span class="tag-new" style="margin-left:6px">New</span>' if m.get('new') else ''
    hero = page_hero(crumbs(('modules.html', 'Modules'), (None, m['name'])), m['kind'] + tag, m['h1'], m['lede'],
                     '<a class="btn btn-blue" href="contact.html">Book a demo</a><a class="btn btn-ghost" href="modules.html">All modules</a>',
                     extra=logo_img(m, 0.42, 'hero-logo'))
    hero = hero.replace('<section class="page-hero">', f'<section class="page-hero" style="--mod:{m["color"]}">')
    visual = f'''<section class="block" id="in-action">
    <div class="wrap">
      {head_block(m['name'] + ' in action', 'See what it sees.', 'A live example of the alerts and context your team would get.')}
      {module_visual(m)}
    </div>
  </section>'''
    caps = f'''<section class="block" id="capabilities">
    <div class="wrap">
      {head_block('Capabilities', 'What ' + m['name'] + ' does.', 'Six things your team can switch on from day one.')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in m['caps'])}</div>
    </div>
  </section>'''
    steps = f'''<section class="block" id="how">
    <div class="wrap">
      {head_block('How it works', 'Up and running in three steps.', 'Most teams start with a pilot on a few cameras or sensors.')}
      <div class="steps">{''.join(f'<div><b>{t}</b><p>{d}</p></div>' for t, d in m['steps'])}</div>
      <p style="margin-top:32px"><a class="link-arrow" href="platform.html">How the Intelense platform works</a></p>
    </div>
  </section>'''
    uses = f'''<section class="block" id="use-cases">
    <div class="wrap">
      {head_block('Where it is used', 'Built for real sites.', 'Typical places teams run ' + m['name'] + '.')}
      <ul class="uses">{''.join(f'<li><b>{t}</b><span>{d}</span><a href="industries.html#{ind}">{IND[ind]["name"]} →</a></li>' for ind, t, d in m['uses'])}</ul>
    </div>
  </section>'''
    related = f'''<section class="block" id="related">
    <div class="wrap">
      {head_block('Related modules', 'Works well with.', 'Modules share one engine and dashboard, so they combine easily.')}
      <div class="related">{''.join(card(MOD[k]) for k in m['related'])}</div>
      <div class="proof" style="margin-top:48px">
        <a class="link-prev" href="{prev_m['key']}.html">← {prev_m['name']}</a>
        <a class="link-arrow" href="modules.html" style="margin-inline:auto">All modules</a>
        <a class="link-arrow" href="{next_m['key']}.html">{next_m['name']}</a>
      </div>
    </div>
  </section>'''
    body = '\n\n  '.join([hero, visual, caps, steps, uses, related, cta_band('See ' + m['name'] + ' on your own site.')])
    return dict(file=m['key'] + '.html', title=f'{m["name"]}: {m["kind"]} | Intelense', desc=m['lede'], active=m['key'],
                body=body, cctv=m['visual'] in ('console', 'safety', 'home', 'agri', 'robotics'))


def page_industries():
    hero = page_hero(crumbs((None, 'Industries')), 'Industries', "Built for places where safety can't wait.",
                     'Our mission is a safer world, starting with public safety. The same platform serves teams across seven sectors.',
                     '<a class="btn btn-blue" href="contact.html">Book a demo</a><a class="btn btn-ghost" href="modules.html">Explore the modules</a>')
    jump = f'''<section class="block" id="sectors" style="padding-block:40px">
    <div class="wrap">{sector_links()}</div>
  </section>'''
    blocks = []
    for ind in INDUSTRIES:
        uses = ''.join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in ind['uses'])
        blocks.append(f'''<article class="sector" id="{ind['id']}">
          <div>
            <span class="eyebrow">{ind['name']}</span>
            <h2>{ind['title']}</h2>
            <p>{ind['text']}</p>
            {mod_chips(ind['mods'])}
          </div>
          <ul class="uses">{uses}</ul>
        </article>''')
    lst = f'''<section class="block" style="border-top:0;padding-top:0">
    <div class="wrap"><div class="sector-list">
        {''.join(blocks)}
    </div></div>
  </section>'''
    body = '\n\n  '.join([hero, jump, lst, cta_band('Tell us about your site.', ('platform.html', 'See the platform'))])
    return dict(file='industries.html', title='Industries | Intelense', desc='How Intelense serves public safety, smart cities, retail, healthcare, industrial, agriculture and residential teams.',
                active='industries.html', body=body)


def page_about():
    hero = page_hero(crumbs((None, 'Company')), 'About Intelense', 'A safer world, starting with public safety.',
                     'Intelense is an artificial intelligence and data analytics company based in Markham, Ontario. We turn the video, sensor and voice data organisations already have into alerts people can act on.',
                     '<a class="btn btn-blue" href="contact.html">Talk to us</a><a class="btn btn-ghost" href="platform.html">See the platform</a>')
    story = f'''<section class="block" id="story">
    <div class="wrap">
      {head_block('Our story', 'From one idea to seven modules.', 'We started with a simple question: why do cameras record everything but tell nobody anything?')}
      <ol class="timeline">
        <li><b>2018</b><div><h3>Founded in Markham, Ontario</h3><p>Intelense starts with a mission to make public spaces safer using AI and data analytics.</p></div></li>
        <li><b>Growth</b><div><h3>Supported by CENGN and VentureLab</h3><p>Canadian innovation programmes help us test and scale the platform.</p></div></li>
        <li><b>Today</b><div><h3>Seven Ken modules on one platform</h3><p>From <a href="kenvision.html">video analytics</a> to <a href="kenagri.html">agriculture</a> and <a href="keniot.html">predictive maintenance</a>, all on the same engine.</p></div></li>
        <li><b>New</b><div><h3>KenVoice joins the platform</h3><p><a href="kenvoice.html">KenVoice</a> brings spoken alerts, hands-free commands and transcription to the Ken platform.</p></div></li>
      </ol>
    </div>
  </section>'''
    values = f'''<section class="block" id="values">
    <div class="wrap">
      {head_block('What we believe', 'How we build.', 'Three principles shape every module we ship.')}
      <div class="values">
        <div class="cap">{icon('plug')}<h3>Start from what is already there</h3><p>Most sites already have cameras and sensors. We make them useful instead of asking you to replace them.</p></div>
        <div class="cap">{icon('filter')}<h3>Alerts people can trust</h3><p>An alert nobody believes is noise. We focus on fewer, clearer alerts with the context to act.</p></div>
        <div class="cap">{icon('layers')}<h3>Intelligence at the edge</h3><p>Analysing data close to where it is captured keeps alerts fast and keeps footage on site.</p></div>
      </div>
    </div>
  </section>'''
    proof = f'''<section class="block" id="partners">
    <div class="wrap">
      {head_block('Ecosystem', 'Supported by Canadian innovation.', 'We are grateful to the programmes that have helped us grow.')}
      <div class="proof" style="margin-top:0;border-top:0;padding-top:0">
        <span class="lbl">Supported by</span><span class="mark">CENGN</span><span class="mark">VentureLab</span>
        <a class="link-arrow" href="industries.html" style="margin-left:auto">Who we work with</a>
      </div>
    </div>
  </section>'''
    body = '\n\n  '.join([hero, story, values, proof, cta_band('Want to work with us?', ('industries.html', 'See industries'))])
    return dict(file='about.html', title='About | Intelense', desc='Intelense is an AI and data analytics company in Markham, Ontario, with a mission to create a safer world.',
                active='about.html', body=body)


def page_contact():
    hero = page_hero(crumbs((None, 'Contact')), 'Contact', 'Book a demo.',
                     'Tell us about your sites and what you want to catch. We will show you Intelense on footage like yours.',
                     '<a class="btn btn-ghost" href="index.html#faq">Read the FAQ</a><a class="btn btn-ghost" href="modules.html">Explore the modules</a>')
    checks = ''.join(f'<label><input type="checkbox" name="modules" value="{m["key"]}"> {m["name"]}</label>' for m in MODULES)
    form = f'''<section class="block" id="form">
    <div class="wrap contact-grid">
      <div class="panel">
        <form class="form" id="demo-form" novalidate>
          <div class="field"><label for="f-name">Full name</label><input id="f-name" name="name" autocomplete="name" required></div>
          <div class="field"><label for="f-email">Work email</label><input id="f-email" name="email" type="email" autocomplete="email" required></div>
          <div class="field"><label for="f-company">Company</label><input id="f-company" name="company" autocomplete="organization" required></div>
          <div class="field"><label for="f-role">Role</label><input id="f-role" name="role" autocomplete="organization-title"></div>
          <div class="field"><label for="f-industry">Industry</label><select id="f-industry" name="industry"><option value="">Choose one</option>{''.join(f'<option>{i["name"]}</option>' for i in INDUSTRIES)}<option>Other</option></select></div>
          <div class="field"><label for="f-size">Number of cameras or sensors</label><select id="f-size" name="size"><option value="">Choose one</option><option>Under 25</option><option>25 to 100</option><option>100 to 500</option><option>More than 500</option></select></div>
          <div class="field full"><label>Modules you are interested in</label><div class="checks">{checks}</div></div>
          <div class="field full"><label for="f-msg">What would you like to catch?</label><textarea id="f-msg" name="message" placeholder="For example: PPE compliance on two loading docks, after-hours intrusion at three sites."></textarea></div>
          <div class="full" style="display:flex;gap:16px;align-items:center;flex-wrap:wrap"><button class="btn btn-blue" type="submit">Request a demo</button><span class="form-note">Sample form: not connected to email yet.</span></div>
        </form>
        <div class="form-done" id="form-done" hidden tabindex="-1">
          <h3>Thanks, we have your request.</h3>
          <p>This sample form is not connected yet. On the live site it will send your details to enquiries@intelense.ca and our team will be in touch.</p>
          <p style="margin-top:18px"><a class="link-arrow" href="modules.html">Explore the modules while you wait</a></p>
        </div>
      </div>
      <aside class="panel">
        <ul class="info-list">
          <li><span>Email</span><b class="email">enquiries@intelense.ca</b></li>
          <li><span>Head office</span><b>Markham, Ontario, Canada</b></li>
        </ul>
        <h3 style="margin-top:28px">What happens next</h3>
        <ol class="next-steps">
          <li><div><b>Discovery call</b>We learn about your sites, cameras and goals.</div></li>
          <li><div><b>Tailored demo</b>We show the modules that fit, on footage like yours.</div></li>
          <li><div><b>Pilot</b>We run Intelense on a few of your cameras so you can judge the results.</div></li>
        </ol>
      </aside>
    </div>
  </section>'''
    body = '\n\n  '.join([hero, form])
    return dict(file='contact.html', title='Contact and book a demo | Intelense', desc='Book a demo of the Intelense AI platform and the Ken modules.',
                active='contact.html', body=body)


PAGES = [page_index, page_platform, page_modules, *[(lambda m: (lambda: page_module(m)))(m) for m in MODULES], page_industries, page_about, page_contact]

# ---------------------------------------------------------------- output

GRID_OPTS = "{ cellSize: 60, color: '#0a0a0a', radius: 160, falloff: 'smooth', holdTime: 300, fadeDuration: 700, lineWidth: 1, maxOpacity: 0.3, fillOpacity: 0, gridOpacity: 0, cellRadius: 4, clickPulse: true, pulseSpeed: 700 }"
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap">'


def render(p, inline=False, bare=False):
    css = (ASSETS / 'site.css').read_text()
    style = f'<style>\n{css}</style>' if inline else '<link rel="stylesheet" href="assets/site.css">'
    head = f'<title>{p["title"]}</title>\n<meta name="description" content="{p["desc"]}">\n{FONTS}\n{style}'
    scripts = []
    for name, need in (('site.js', True), ('cctv.js', p.get('cctv'))):
        if need:
            scripts.append(f'<script>\n{(ASSETS / name).read_text()}</script>' if inline else f'<script src="assets/{name}" defer></script>')
    if inline:
        grid = (ASSETS / 'cursor-grid.js').read_text().replace('export function', 'function')
        scripts.append(f"<script>\n{{\n{grid}\ninitCursorGrid(document.querySelector('.cursor-grid'), {GRID_OPTS});\n}}\n</script>")
    else:
        scripts.append(f"<script type=\"module\">\nimport {{ initCursorGrid }} from './assets/cursor-grid.js';\ninitCursorGrid(document.querySelector('.cursor-grid'), {GRID_OPTS});\n</script>")
    content = f'{header(p["active"])}\n<main id="top">\n  {p["body"]}\n</main>\n\n{footer()}\n' + '\n'.join(scripts) + '\n'
    if bare:
        return head + '\n\n' + content
    return f'<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{head}\n</head>\n<body>\n{content}</body>\n</html>\n'


def main():
    pages = [f() for f in PAGES]
    for p in pages:
        (ROOT / p['file']).write_text(render(p))
    print('wrote', len(pages), 'pages to', ROOT)
    if '--inline' in sys.argv:
        out = Path(sys.argv[sys.argv.index('--inline') + 1])
        out.mkdir(parents=True, exist_ok=True)
        for p in pages:
            (out / p['file']).write_text(render(p, inline=True, bare=p['file'] == 'index.html'))
        shutil.copytree(ASSETS / 'logos', out / 'assets' / 'logos', dirs_exist_ok=True)
        print('wrote inline copy to', out)


if __name__ == '__main__':
    main()
