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

import appui as ap

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


ap.icon = icon


def mmss(sec):
    return f'{sec // 60}m {sec % 60:02d}s'


MODULES = [
    dict(key='kenvision', name='KenVision', kind='Video analytics', color='#0A34ED', logo='kenvision.png', size=(783, 287),
         card='Turns your existing CCTV cameras into business intelligence. Track footfall, customer movement, dwell time and queues without manually reviewing footage.',
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
         uses=[('retail', 'Retail stores and malls', 'Footfall, heatmaps, dwell time and billing queues.'),
               ('smart-cities', 'Transit hubs and offices', 'Passenger movement, occupancy and space utilisation.'),
               ('healthcare', 'Hospitals and clinics', 'Occupancy in waiting areas and entrances.')],
         visual='console', related=['kensafety', 'keniot', 'kenvoice']),
    dict(key='kensafety', name='KenSafety', kind='Workplace safety', color='#FF7953', logo='kensafety.png', size=(793, 300),
         card='Uses AI video analytics on your existing CCTV to flag missing PPE, restricted-zone entry, human-vehicle risks, fire, smoke and falls.',
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
         card='Turns your existing home cameras into AI-powered monitoring for home security, elderly falls, children, pets and your driveway.',
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
         card='Uses AI with satellite, drone, sensor and weather data to monitor crop health, flag pests and disease, predict yields and guide irrigation.',
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
         card='Turns data from connected sensors and equipment into real-time monitoring, anomaly detection and predictive maintenance insights.',
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
    dict(key='kenrobotics', name='KenRobotics', kind='Autonomous robotics', color='#6C6E82', logo='kenrobotics.png', size=(919, 300),
         card='AI perception, dynamic path planning and fleet coordination that help autonomous robots work safely alongside people.',
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
         visual='robotics', related=['keniot', 'kensafety', 'kenagri']),
    dict(key='kenvoice', name='KenVoice', kind='Conversation intelligence', color='#5466DD', logo='kenvoice.png', size=(792, 300), new=True,
         card='Uses on-device AI audio analytics to turn customer and staff conversations at the counter into service, coaching and sales insights.',
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
         uses=[('retail', 'Retail counters', 'Greetings, upsells, sentiment and staff coaching.')],
         visual='voice', related=['kenvision', 'kensafety', 'keniot']),
]
MOD = {m['key']: m for m in MODULES}

INDUSTRIES = [
    dict(id='public-safety', name='Public safety', title='Public safety and emergency response',
         text='Police, fire, campus and municipal teams watch hundreds of feeds with small teams. Intelense surfaces the moments that matter and links them to calls and radio traffic, so responders arrive informed.',
         uses=[('Intrusion and after-hours alerts', 'Parks, schools and municipal buildings.'), ('Crowd and incident detection', 'Events, transit hubs and public squares.'), ('Faster video review', 'Search footage instead of scrubbing through hours.')],
         mods=['kenvision', 'kensafety', 'kenrobotics']),
    dict(id='smart-cities', name='Smart cities', title='Smart cities and infrastructure',
         text='Streets, transit and utilities generate more data than any team can watch. Intelense turns cameras and sensors into live signals for traffic, crowds and asset health.',
         uses=[('Traffic and crowd flow', 'Intersections, stations and busy streets.'), ('Infrastructure health', 'Pumps, HVAC and remote equipment.'), ('Inspection at scale', 'Drones and robots on bridges, tunnels and substations.')],
         mods=['kenvision', 'keniot', 'kenrobotics']),
    dict(id='retail', name='Retail', title='Retail and commercial spaces',
         text='Stores and malls already have cameras. Intelense uses them to cut losses, shorten queues and keep staff and shoppers safe.',
         uses=[('Footfall and queues', 'Visitor traffic, dwell time and billing queues.'), ('Counter conversations', 'Greetings, upsells and staff coaching.'), ('Safety on the floor', 'Slips, blocked exits and stockroom hazards.')],
         mods=['kenvision', 'kenvoice', 'kensafety']),
    dict(id='healthcare', name='Healthcare', title='Hospitals and care facilities',
         text='Care teams cannot watch every corridor. Intelense flags falls, restricted-area access and calls for help so staff can respond quickly.',
         uses=[('Falls and wandering', 'Corridors, wards and exits.'), ('Restricted areas', 'Pharmacies, labs and staff-only zones.'), ('Facility systems', 'Environmental and equipment sensors.')],
         mods=['kenvision', 'kensafety', 'keniot']),
    dict(id='industrial', name='Industrial', title='Industrial sites and workplaces',
         text='Warehouses, plants and construction sites combine people, vehicles and heavy machines. Intelense watches all three and warns before accidents and breakdowns.',
         uses=[('PPE and hazard zones', 'Hard hats, vests and machinery exclusion zones.'), ('Forklift safety', 'Close calls between vehicles and pedestrians.'), ('Predictive maintenance', 'Motors, conveyors and compressors.')],
         mods=['kensafety', 'keniot', 'kenrobotics', 'kenvision']),
    dict(id='agriculture', name='Agriculture', title='Farms and agriculture',
         text='Large properties are hard to watch, especially at night. Intelense covers fields, pens and fence lines with cameras, drones and sensors.',
         uses=[('Crop health', 'Stress and disease patches, spotted early.'), ('Livestock', 'Counts, behaviour and predators.'), ('Property and equipment', 'Fence lines, yards and fuel storage.')],
         mods=['kenagri', 'keniot', 'kenrobotics']),
    dict(id='residential', name='Residential', title='Homes and residential buildings',
         text='Families and property managers want alerts they can trust. Intelense watches entrances, living spaces and driveways and flags the events that matter.',
         uses=[('Front door and packages', 'Visitors, deliveries and porch activity.'), ('Building entrances', 'Lobbies, garages and shared spaces.'), ('Driveways and vehicles', 'Activity around parked cars at night.')],
         mods=['kenhome', 'kenvision']),
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
            <div class="chips"><span class="chip">Footfall</span><span class="chip">Heatmaps</span><span class="chip">Dwell time</span><span class="chip">Queues</span></div>
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
_main = _home[_home.index('<main id="top">') + len('<main id="top">'):_home.index('</main>')].replace('src="logos/', 'src="assets/logos/').replace('<img class="c-logo" src="assets/logos/kenvision-light.png" alt="" width="82" height="30">', '<img class="c-logo" src="assets/logos/intelense-light.png" alt="Intelense" width="143" height="22" style="height:22px">').replace('<span class="eyebrow">KenVision in action</span>', '<span class="eyebrow">Intelense in action</span>')


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
                                   '<p class="demo-note">Simulated camera feeds and example data. Not a real site or customer.</p>\n      <p style="margin-top:20px"><a class="link-arrow" href="platform.html#console">See the platform</a></p>')
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
    faq = FAQ.replace('<p>Book a demo. We', '<p><a href="contact.html">Book a demo</a>. We').replace('<summary>What is KenVoice?</summary>\n          <p>KenVoice is our newest module. It adds voice to the Ken platform, so spoken alerts, hands-free commands and call audio sit in the same timeline as your video and sensor events.</p>', '<summary>What is KenVoice?</summary>\n          <p><a href="kenvoice.html">KenVoice</a> is our newest module. It uses AI audio analytics to turn customer and staff conversations at retail counters into service, coaching and sales insights, with audio processed on-device.</p>')
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
    chips = ['IP cameras (RTSP / ONVIF)', 'Video management systems', 'Drones and body cams', 'IoT and industrial sensors', 'Counter tablets for in-store audio', 'Access control', 'Email, SMS and push alerts', 'Webhooks and APIs']
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
    watch = {'kenvision': 'Existing CCTV and IP cameras', 'kensafety': 'Cameras on floors, docks and sites', 'kenhome': 'Indoor, outdoor, doorbell and driveway cameras',
             'kenagri': 'Satellite and drone imagery, soil sensors, weather data', 'keniot': 'Temperature, vibration, pressure, humidity and power sensors',
             'kenrobotics': 'Robot sensor inputs and fleet status', 'kenvoice': 'Counter tablet audio, processed on-device'}
    alerts = {'kenvision': 'Footfall, heatmaps, dwell time, queue build-up', 'kensafety': 'Missing PPE, restricted zones, human-vehicle proximity, fire and smoke, falls',
              'kenhome': 'Intrusion, falls and inactivity, restricted zones, pets, vehicles', 'kenagri': 'Crop stress, pest and disease risk, irrigation needs, yield estimates',
              'keniot': 'Anomalies, threshold breaches, predicted failures, work orders', 'kenrobotics': 'Obstacles, route conflicts, safety-zone events, task status',
              'kenvoice': 'Missed greetings and upsells, walk-aways, sentiment, staff scores'}
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
        <li><b>New</b><div><h3>KenVoice joins the platform</h3><p><a href="kenvoice.html">KenVoice</a> brings AI conversation intelligence to retail counters, with audio processed on-device.</p></div></li>
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


# ---------------------------------------------------------------- KenVision page (business intelligence)

def _bar(x, y, w, h, r=3):
    """Bar with rounded data end (top), square at the baseline."""
    r = min(r, w / 2, h)
    return f'M{x:.1f},{y + h:.1f}V{y + r:.1f}Q{x:.1f},{y:.1f} {x + r:.1f},{y:.1f}H{x + w - r:.1f}Q{x + w:.1f},{y:.1f} {x + w:.1f},{y + r:.1f}V{y + h:.1f}Z'


def footfall_chart(dark=True):
    hours = list(range(8, 22))
    vals = [32, 58, 84, 96, 121, 148, 132, 118, 126, 152, 188, 201, 164, 96]
    W, H, ml, mb, mt = 560, 210, 34, 26, 16
    pw, ph = W - ml - 6, H - mb - mt
    bw = pw / len(vals)
    ink, mute, grid, fill = ('#e9e9ec', '#9b9daf', '#2a2c33', '#5b7cff') if dark else ('#242424', '#6C6E82', '#dcdce0', '#0A34ED')
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Footfall by hour, 08:00 to 21:00. Peak 201 visitors at 19:00.">']
    for gv in (0, 100, 200):
        y = mt + ph - gv / 220 * ph
        out.append(f'<line x1="{ml}" x2="{W - 6}" y1="{y:.1f}" y2="{y:.1f}" stroke="{grid}" stroke-width="1"/><text x="{ml - 8}" y="{y + 3:.1f}" text-anchor="end" fill="{mute}" font-size="10">{gv}</text>')
    for i, (hr, v) in enumerate(zip(hours, vals)):
        bh = v / 220 * ph
        x = ml + i * bw + 1
        out.append(f'<path d="{_bar(x, mt + ph - bh, bw - 2, bh)}" fill="{fill}" data-tip="{hr:02d}:00 · {v} visitors"/>')
        if i % 2 == 0:
            out.append(f'<text x="{x + (bw - 2) / 2:.1f}" y="{H - 8}" text-anchor="middle" fill="{mute}" font-size="10">{hr:02d}:00</text>')
    pk = vals.index(max(vals))
    px = ml + pk * bw + bw / 2
    out.append(f'<text x="{px:.1f}" y="{mt + ph - max(vals) / 220 * ph - 6:.1f}" text-anchor="middle" fill="{ink}" font-size="11" font-weight="600">Peak {max(vals)}</text>')
    out.append('</svg>')
    return ''.join(out)


def dwell_chart():
    zones = [('Promo display', 250), ('Electronics', 185), ('Checkout', 160), ('Apparel', 140), ('Grocery', 105)]
    W, rowh, lab = 360, 30, 104
    H = rowh * len(zones) + 6
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Average dwell time by zone">']
    for i, (z, s) in enumerate(zones):
        y = i * rowh + 6
        bw = s / 260 * (W - lab - 54)
        out.append(f'<text x="0" y="{y + 13}" fill="#c9cbd6" font-size="11">{z}</text>')
        out.append(f'<rect x="{lab}" y="{y + 3}" width="{W - lab - 54}" height="14" rx="3" fill="#24262d"/>')
        out.append(f'<path d="M{lab},{y + 3}H{lab + bw - 3:.1f}Q{lab + bw:.1f},{y + 3} {lab + bw:.1f},{y + 6}V{y + 14}Q{lab + bw:.1f},{y + 17} {lab + bw - 3:.1f},{y + 17}H{lab}Z" fill="#5b7cff" data-tip="{z} · {s // 60}m {s % 60:02d}s average"/>')
        out.append(f'<text x="{W}" y="{y + 14}" text-anchor="end" fill="#e9e9ec" font-size="11" font-weight="600">{s // 60}m {s % 60:02d}s</text>')
    out.append('</svg>')
    return ''.join(out)


def queue_chart():
    vals = [1, 1, 2, 1, 2, 3, 2, 2, 3, 4, 3, 2, 2, 3, 3, 4, 5, 6, 6, 5, 4, 3, 2, 2, 1]
    W, H, ml, mb, mt = 360, 170, 24, 24, 12
    pw, ph = W - ml - 6, H - mb - mt
    X = lambda i: ml + i * pw / (len(vals) - 1)
    Y = lambda v: mt + ph - v / 8 * ph
    pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals))
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Queue length at checkout through the day, crossing the alert threshold of 5 between 17:00 and 18:30.">']
    for gv in (0, 4, 8):
        out.append(f'<line x1="{ml}" x2="{W - 6}" y1="{Y(gv):.1f}" y2="{Y(gv):.1f}" stroke="#2a2c33"/><text x="{ml - 6}" y="{Y(gv) + 3:.1f}" text-anchor="end" fill="#9b9daf" font-size="10">{gv}</text>')
    out.append(f'<line x1="{ml}" x2="{W - 6}" y1="{Y(5):.1f}" y2="{Y(5):.1f}" stroke="#FF7953" stroke-dasharray="4 4" stroke-width="1.5"/><text x="{W - 6}" y="{Y(5) - 5:.1f}" text-anchor="end" fill="#ffb39b" font-size="10" font-weight="600">Alert at 5</text>')
    out.append(f'<polygon points="{ml},{Y(0):.1f} {pts} {X(len(vals) - 1):.1f},{Y(0):.1f}" fill="rgba(115,196,197,.14)"/>')
    out.append(f'<polyline points="{pts}" fill="none" stroke="#73C4C5" stroke-width="2" stroke-linejoin="round"/>')
    for i, v in enumerate(vals):
        hh, mm = 9 + i // 2, '30' if i % 2 else '00'
        col = '#FF7953' if v >= 5 else '#73C4C5'
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{4 if v >= 5 else 2.5}" fill="{col}" stroke="#16171b" stroke-width="2" data-tip="{hh:02d}:{mm} · {v} in queue"/>')
    for i, lab in ((0, '09:00'), (12, '15:00'), (24, '21:00')):
        out.append(f'<text x="{X(i):.1f}" y="{H - 6}" text-anchor="{"start" if i == 0 else "end" if i == 24 else "middle"}" fill="#9b9daf" font-size="10">{lab}</text>')
    out.append('</svg>')
    return ''.join(out)


def heat_plan(dark=False, uid='a'):
    """Top-down store plan with a single-hue activity heatmap (same layout as the store camera)."""
    W, H = 400, 260
    wall, floor, shelf, ink, mute = ('#3a3c44', '#1d1f24', '#2c2e35', '#e9e9ec', '#9b9daf') if dark else ('#9a978f', '#ffffff', '#e4e2dc', '#242424', '#6C6E82')
    hot = [(.66, .45, 70, 1.0), (.88, .4, 58, .95), (.5, .86, 60, .8), (.3, .415, 46, .55), (.3, .245, 40, .35), (.06, .6, 40, .3), (.3, .76, 44, .45), (.2, .585, 36, .3)]
    out = [f'<svg class="plan" viewBox="0 0 {W} {H + 34}" role="img" aria-label="Store heatmap: most activity at the promo display, checkout queue and entrance; least in the back aisles.">',
           f'<defs><radialGradient id="ht-{uid}"><stop offset="0" stop-color="#7C28E9" stop-opacity=".85"/><stop offset=".55" stop-color="#7C28E9" stop-opacity=".35"/><stop offset="1" stop-color="#7C28E9" stop-opacity="0"/></radialGradient>'
           f'<linearGradient id="hl-{uid}"><stop offset="0" stop-color="#7C28E9" stop-opacity=".08"/><stop offset="1" stop-color="#7C28E9" stop-opacity=".9"/></linearGradient></defs>',
           f'<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="10" fill="{floor}" stroke="{wall}" stroke-width="2"/>',
           f'<rect x="{W * .4}" y="{H - 3}" width="{W * .2}" height="5" fill="{floor}"/>']
    for gy in (.15, .32, .49, .66):
        out.append(f'<rect x="{W * .08}" y="{H * gy}" width="{W * .42}" height="{H * .075}" rx="3" fill="{shelf}"/>')
    out.append(f'<circle cx="{W * .66}" cy="{H * .45}" r="{W * .055}" fill="{shelf}"/>')
    for cy in (.16, .7):
        out.append(f'<rect x="{W * .84}" y="{H * cy}" width="{W * .12}" height="{H * .08}" rx="3" fill="{shelf}"/>')
    for x, y, r, a in hot:
        out.append(f'<circle cx="{x * W:.0f}" cy="{y * H:.0f}" r="{r}" fill="url(#ht-{uid})" opacity="{a}"/>')
    labels = [(.66, .25, 'Promo display', 'middle'), (.9, .1, 'Checkout', 'middle'), (.5, .975, 'Entrance', 'middle'), (.3, .1, 'Back aisles · low activity', 'middle')]
    for x, y, t, anc in labels:
        out.append(f'<text x="{x * W:.0f}" y="{y * H:.0f}" text-anchor="{anc}" fill="{ink}" font-size="11" font-weight="600">{t}</text>')
    out.append(f'<text x="0" y="{H + 24}" fill="{mute}" font-size="10">Less activity</text><rect x="78" y="{H + 15}" width="120" height="10" rx="5" fill="url(#hl-{uid})"/><text x="206" y="{H + 24}" fill="{mute}" font-size="10">More</text>')
    out.append('</svg>')
    return ''.join(out)


def mini(kind):
    """Small illustrative visual for each feature card (light surface)."""
    b, v, m, g = '#0A34ED', '#7C28E9', '#6C6E82', '#e4e2dc'
    if kind == 'footfall':
        vals = [20, 34, 46, 40, 58, 70, 52, 64, 78, 60]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<path d="{_bar(4 + i * 21.5, 70 - h * .85, 17, h * .85)}" fill="{b}" opacity="{.45 + i * .05:.2f}"/>' for i, h in enumerate(vals)) + '</svg>'
    if kind == 'heat':
        import random
        rnd = random.Random(4)
        cells = []
        for r in range(3):
            for c in range(10):
                o = max(.06, min(.95, (1 - abs(c - 6.5) / 7) * (1 - abs(r - 1) / 3) + rnd.uniform(-.15, .15)))
                cells.append(f'<rect x="{c * 22 + 1}" y="{r * 24 + 1}" width="20" height="22" rx="4" fill="{v}" opacity="{o:.2f}"/>')
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(cells) + '</svg>'
    if kind == 'dwell':
        rows = [('Display', 180), ('Counter', 130), ('Aisle', 80)]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<text x="0" y="{i * 24 + 15}" fill="{m}" font-size="10">{n}</text><rect x="54" y="{i * 24 + 5}" width="166" height="12" rx="3" fill="{g}"/><rect x="54" y="{i * 24 + 5}" width="{w * .9:.0f}" height="12" rx="3" fill="{b}"/>' for i, (n, w) in enumerate(rows)) + '</svg>'
    if kind == 'queue':
        dots = ''.join(f'<circle cx="{18 + i * 30}" cy="40" r="10" fill="{"#FF7953" if i >= 4 else b}" opacity="{1 if i < 4 else .9}"/>' for i in range(6))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="0" y="22" width="200" height="36" rx="18" fill="none" stroke="{g}" stroke-width="2"/>{dots}<line x1="129" x2="129" y1="10" y2="66" stroke="#FF7953" stroke-dasharray="3 3" stroke-width="1.5"/><text x="135" y="14" fill="{m}" font-size="10">Alert</text></svg>'
    if kind == 'funnel':
        rows = [('Visitors', 210), ('Engaged', 140), ('Purchased', 70)]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<rect x="{(220 - w) / 2:.0f}" y="{i * 24 + 2}" width="{w}" height="20" rx="4" fill="{b}" opacity="{1 - i * .25:.2f}"/><text x="110" y="{i * 24 + 16}" text-anchor="middle" fill="#fff" font-size="10" font-weight="600">{n}</text>' for i, (n, w) in enumerate(rows)) + '</svg>'
    if kind == 'util':
        rows = [('Floor', .82), ('Checkout', .64), ('Fitting', .38)]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<text x="0" y="{i * 24 + 15}" fill="{m}" font-size="10">{n}</text><rect x="58" y="{i * 24 + 5}" width="162" height="12" rx="6" fill="{g}"/><rect x="58" y="{i * 24 + 5}" width="{162 * p:.0f}" height="12" rx="6" fill="{v}"/>' for i, (n, p) in enumerate(rows)) + '</svg>'
    raise ValueError(kind)


KV_FAQ = [
    ('What is AI video analytics?', 'AI video analytics uses artificial intelligence and computer vision to analyse video footage and identify useful information, such as people counts, movement patterns, occupancy and activity within defined areas.'),
    ('What is KenVision?', "KenVision is Intelense's AI video analytics product. It turns video feeds from compatible cameras into business insights, including footfall analytics, heatmaps, dwell time, queue monitoring and other supported metrics."),
    ('How is AI video analytics different from CCTV?', 'Traditional CCTV primarily records video for live monitoring or later review. AI video analytics automatically analyses video feeds to generate metrics, identify patterns and provide operational insights.'),
    ('Can KenVision work with existing CCTV cameras?', 'KenVision is designed to integrate with compatible existing cameras and recording systems. The exact compatibility and setup depend on your current infrastructure.'),
    ('What is footfall analytics?', 'Footfall analytics measures visitor traffic across a location. Businesses use it to understand visitor numbers, entry and exit patterns, and peak hours.'),
    ('What is dwell time analytics?', 'Dwell time analytics measures how long people remain in a defined area. Retailers can use it to understand activity around displays, counters and other selected zones.'),
    ('Can KenVision help improve retail performance?', 'KenVision can help retailers understand footfall, customer movement, dwell time and queue patterns. These insights can support decisions about staffing, store layouts and customer experience. Actual sales impact depends on how the insights are used.'),
    ('Does KenVision require new hardware?', 'Not necessarily. KenVision can use compatible existing camera infrastructure. Hardware, processing and integration requirements depend on the deployment.'),
    ('Can KenVision be used outside retail?', 'Yes. Video analytics can also support applications in commercial buildings, offices, transport hubs, healthcare facilities and hospitality environments, depending on the features configured.'),
    ('How can I get a KenVision demo?', 'Contact Intelense to discuss your business requirements, camera infrastructure and analytics needs. The team can help you understand the appropriate configuration for your use case.'),
]


KV_HERO = dict(
    uid='kv', logo='kenvision', site='Store 014 · CAM-02 store floor',
    aria='Overhead store camera counting people at the entrance, tracking a checkout queue and measuring dwell time at a promo display',
    media='<div class="tile-solo"><canvas class="cctv" data-scene="store" width="960" height="540"></canvas></div>',
    kpis=[('users', 'Footfall today', '1,284', '↗ 8%', 'pos', 'vs last Tue', [40, 46, 44, 52, 58, 55, 63, 70, 68, 76, 84, 90]),
          ('clock', 'Avg dwell time', '6m 12s', '↗ 24s', 'pos', 'vs last week', [5.2, 5.5, 5.4, 5.6, 5.5, 5.8, 5.7, 5.9, 6.0, 6.1, 6.0, 6.2])],
    alert=('Queue alert', 'neg', 'timeline', '<b>4 waiting</b> at Checkout 2. Open another till.', '14:32'))


def kv_dash():
    hours = [f'{h:02d}:00' for h in range(8, 22)]
    vals = [32, 58, 84, 96, 121, 148, 132, 118, 126, 152, 188, 201, 164, 96]
    prev = [28, 50, 70, 92, 110, 130, 126, 112, 120, 140, 170, 182, 150, 90]
    main = ap.card('Footfall by hour', '<div class="ap-mhead"><b>1,284</b>' + ap.pill('↗ 8%', 'pos') + '<span class="ap-vs">visitors today</span>'
                   '<span class="ap-legend"><span><i></i>Today</span><span><i class="prev"></i>Last Tuesday</span></span></div>'
                   + ap.line_chart(hours, vals, 11, '19:00 · 201 visitors', 'kv', (0, 80, 160, 240), prev, every=2), cls='ap-mainc')
    side = ap.feed([('timeline', 'neg', '<b>Queue alert</b> at Checkout 2 · 4 waiting', '14:32'),
                    ('users', 'info', '<b>Busy period</b> started · 148 visitors in the last hour', '13:00'),
                    ('clock', 'violet', '<b>Promo display</b> dwell time up 18% on yesterday', '12:40'),
                    ('eye', 'pos', '<b>CAM-04</b> back online at the side entrance', '11:05'),
                    ('chart', 'mute', '<b>Weekly report</b> is ready to download', '09:00')])
    evs = ap.events([('Footfall', 'info', 'users', 'Entrance A · peak hour', '201', 'Visitors between 19:00 and 20:00'),
                     ('Queue', 'neg', 'timeline', 'Checkout 2', '4 waiting', 'Over the 3 minute wait target'),
                     ('Dwell', 'violet', 'clock', 'Promo display', '4m 10s', 'Average time spent today'),
                     ('Conversion', 'pos', 'cart', 'Store-wide', '24%', 'With POS data · up 2 pts')])
    zones = [('Promo', 250), ('Electr.', 185), ('Checkout', 160), ('Apparel', 140), ('Grocery', 105)]
    bottom = [ap.media('CAM-02 · Store floor', '<div class="tile-solo"><canvas class="cctv" data-scene="store" width="480" height="270"></canvas></div>', foot=(('Entry · IN 415', 'pos'), ('Queue · 4', 'neg'), ('Promo · 1m 42s', 'violet'))),
              ap.card('Dwell time by zone', ap.bar_chart([z for z, _ in zones], [v for _, v in zones], 0, mmss, 'kv'), sub='Average per visitor, today'),
              ap.card('Store right now', '<div class="ap-rings">' + ap.ring(62, '62%', 'Occupancy', 'kv1') + ap.ring(24, '24%', 'Conversion', 'kv2') + '</div>'
                      '<div class="ap-split" style="margin-top:14px"><div class="ap-stat"><span>In store</span><b>37</b></div><div class="ap-stat"><span>Queue wait</span><b>2m 40s</b></div></div>')]
    return dict(uid='kv', logo='kenvision', alt='KenVision', me='DT', nav=['eye', 'chart', 'users', 'clock', 'bell', 'cog'],
                hello='Good afternoon, Downtown team', sub='Store 014 · Tuesday 14 October · 6 cameras online', range='Today',
                aria='KenVision dashboard for Store 014 with footfall, dwell time, queue and conversion analytics',
                kpis=[('users', 'Footfall today', '1,284', '↗ 8%', 'pos', 'vs last Tuesday', [40, 46, 44, 52, 58, 55, 63, 70, 68, 76, 84, 90]),
                      ('eye', 'In store now', '37', 'Live', 'info', 'Updated every minute', [22, 26, 31, 28, 34, 30, 36, 33, 39, 35, 38, 37]),
                      ('clock', 'Avg dwell time', '6m 12s', '↗ 7%', 'pos', 'vs last week', [5.2, 5.5, 5.4, 5.6, 5.5, 5.8, 5.7, 5.9, 6.0, 6.1, 6.0, 6.2]),
                      ('timeline', 'Avg queue wait', '2m 40s', '↘ 12%', 'pos', 'shorter than last week', [3.4, 3.2, 3.3, 3.0, 3.1, 2.9, 3.0, 2.8, 2.9, 2.7, 2.8, 2.7])],
                main=main, side=side, events=evs, bottom=bottom)


def page_kenvision():
    import json
    m = MOD['kenvision']
    hero = f'''<section class="page-hero kv-hero" style="--mod:{m["color"]}">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap kv-hero-grid">
      <div class="kv-hero-copy">
        {crumbs(('modules.html', 'Modules'), (None, 'KenVision'))}
        <span class="eyebrow">AI video analytics by Intelense</span>
        {logo_img(m, 0.36, 'hero-logo')}
        <h1>Turn Your Existing CCTV Cameras into Business Intelligence.</h1>
        <p class="lede">KenVision is AI-powered video analytics software that helps you understand what's happening across your business. Track footfall, customer movement, dwell time and queues using your existing camera infrastructure.</p>
        <p class="lede kv-sub">Get useful insights from your video feeds without spending hours manually reviewing footage.</p>
        <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">Book a Demo</a><a class="btn btn-ghost" href="modules.html">All Modules</a></div>
        <p class="kv-tagline">AI video analytics for retail, commercial spaces and business operations.</p>
      </div>
      <div class="kv-hero-visual">
        {ap.hero(KV_HERO)}
        <p class="demo-note">Simulated camera feed and example data</p>
      </div>
    </div>
  </section>'''

    problem = f'''<section class="block" id="problem">
    <div class="wrap">
      {head_block('The problem', 'Your CCTV Cameras Record Everything. But What Can They Tell You?', 'Traditional CCTV helps you see what happened. AI video analytics helps you understand patterns in what is happening.')}
      <div class="kv-problem">
        <div class="kv-questions">
          <p class="kv-q">How many people visited your store today?</p>
          <p class="kv-q">Which areas attracted the most attention?</p>
          <p class="kv-q">When did queues start building up?</p>
          <p class="kv-q">Where could your operations improve?</p>
          <p class="kv-answer">Finding these answers manually takes time. KenVision analyses video feeds to help you turn everyday activity into useful business data.</p>
        </div>
        <ul class="kv-points">
          <li>{icon('users')}<div><b>Understand visitor traffic</b><span>Track footfall and identify peak visiting hours.</span></div></li>
          <li>{icon('clock')}<div><b>See where people spend time</b><span>Measure dwell time and understand activity across different areas.</span></div></li>
          <li>{icon('timeline')}<div><b>Monitor queues</b><span>Identify queue build-up and help your team respond sooner.</span></div></li>
          <li>{icon('chart')}<div><b>Make better operational decisions</b><span>Use video analytics reports and trends to understand what needs attention.</span></div></li>
        </ul>
      </div>
    </div>
  </section>'''

    feats = [
        ('footfall', 'Footfall Analytics &amp; People Counting', 'Know how many people walk through your doors.', 'Count visitors, understand entry and exit patterns, and identify peak hours. Footfall analytics helps you understand traffic across stores, buildings and other business locations.'),
        ('heat', 'Heatmap Analytics', 'See which areas attract attention.', 'Visualise movement patterns and activity across defined zones. Identify busy and less-visited areas to help inform store layouts, product placement and space planning.'),
        ('dwell', 'Dwell Time Analytics', 'Understand where people spend their time.', 'Measure how long people stay in selected areas, around displays or at counters. Use dwell time insights to understand activity and engagement across your space.'),
        ('queue', 'Queue Monitoring &amp; Detection', 'Know when waiting lines start building up.', 'Monitor queues and activity around billing counters or service areas. Help your team identify congestion and respond during busy periods.'),
        ('funnel', 'Conversion Analytics', 'Understand the gap between visitors and purchases.', 'Combine visitor and zone activity data with compatible sales or POS data to understand how store traffic relates to purchasing activity and identify opportunities for improvement.'),
        ('util', 'Staff &amp; Space Utilisation', 'Make better use of your people and space.', 'Understand activity across designated areas and compare it with busy periods. Use these insights to support staffing plans, space utilisation and operational decisions.'),
    ]
    features = f'''<section class="block" id="features">
    <div class="wrap">
      {head_block('Features', 'Everything You Need to Understand Your Space Better', 'KenVision combines AI video analytics, people counting and movement analysis to help you see beyond the camera feed.')}
      <div class="kv-feats">{''.join(f'<article class="kv-feat"><div class="kv-mini">{mini(k)}</div><span class="kv-num">{i + 1:02d}</span><h3>{t}</h3><p class="kv-strap">{s}</p><p>{d}</p></article>' for i, (k, t, s, d) in enumerate(feats))}</div>
    </div>
  </section>'''

    how = f'''<section class="block" id="how">
    <div class="wrap">
      {head_block('How it works', 'How Does AI Video Analytics Work?', 'KenVision turns camera footage into structured insights in three steps.')}
      <ol class="kv-steps">
        <li><span>Step 1</span><h3>Connect Your Existing Cameras</h3><p>Integrate compatible CCTV cameras and video recording systems with KenVision. Use your existing infrastructure where supported instead of replacing your entire camera setup.</p></li>
        <li><span>Step 2</span><h3>AI Analyses Video Feeds</h3><p>AI-powered video analytics processes camera feeds to count people, measure activity across defined zones and identify configured events or patterns.</p></li>
        <li><span>Step 3</span><h3>View Insights on Your Dashboard</h3><p>Access available metrics, trends and alerts through dashboards and reports. Use the information to understand activity and make informed operational decisions.</p></li>
      </ol>
      <p style="margin-top:36px"><a class="btn btn-black" href="#dashboard">See KenVision in Action</a></p>
    </div>
  </section>'''

    inds = [('box', 'Retail Stores &amp; Shopping Malls', 'Use retail video analytics to track footfall, analyse customer movement, understand dwell time around product displays and monitor billing queues.', 'retail'),
            ('users', 'Supermarkets &amp; Food Courts', 'Understand visitor patterns, monitor queues at checkout counters and identify busy periods across service areas.', 'retail'),
            ('route', 'Airports &amp; Transit Hubs', 'Analyse passenger movement, monitor occupancy and understand queue patterns across designated areas.', 'smart-cities'),
            ('layers', 'Offices &amp; Commercial Buildings', 'Understand visitor footfall, activity across floors and utilisation patterns in shared spaces.', 'smart-cities'),
            ('plug', 'Hospitals &amp; Clinics', 'Monitor occupancy and activity in designated waiting areas, entrances and other operational spaces.', 'healthcare'),
            ('home', 'Hotels &amp; Hospitality', 'Understand guest movement and activity across lobbies, restaurants and other shared spaces.', 'retail')]
    industries = f'''<section class="block" id="industries">
    <div class="wrap">
      {head_block('Industry applications', 'AI Video Analytics for Different Industries', 'KenVision helps businesses understand movement, occupancy and activity across their physical spaces.')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p><a class="kv-link" href="industries.html#{a}">More on {IND[a]["name"].lower()} →</a></div>' for ic, t, d, a in inds)}</div>
    </div>
  </section>'''

    retail = f'''<section class="block" id="retail">
    <div class="wrap kv-split">
      <div>
        <span class="eyebrow">Retail use case</span>
        <h2 style="margin-top:18px">A Busy Store Doesn't Always Mean More Sales.</h2>
        <p class="lede" style="margin-top:20px">Your store may be full of visitors, but that doesn't automatically mean customers are finding what they need or completing purchases.</p>
        <p class="kv-body">Retail video analytics can help you investigate what's happening.</p>
        <ul class="kv-defs">
          <li><b>Footfall analytics</b><span>Understand how many visitors enter and when your store is busiest.</span></li>
          <li><b>Heatmap analytics</b><span>Identify which areas attract more activity and which are overlooked.</span></li>
          <li><b>Dwell time analytics</b><span>Understand how long visitors spend around selected counters and displays.</span></li>
          <li><b>Queue analytics</b><span>Identify waiting-time and congestion patterns around billing counters.</span></li>
        </ul>
        <p class="kv-body">By combining these insights with available sales data, retailers can make better-informed decisions about store layouts, staffing and the customer experience.</p>
      </div>
      <figure class="panel kv-plan">
        {heat_plan(False, 'light')}
        <figcaption class="demo-note">Example store heatmap</figcaption>
      </figure>
    </div>
  </section>'''

    bens = [('plug', 'Beyond Traditional CCTV', 'Go beyond recording footage and use AI video analytics to understand activity patterns across your business.'),
            ('clock', 'Less Manual Video Review', 'Automate supported analysis and reduce the need to manually review footage for routine operational insights.'),
            ('eye', 'Real-Time Operational Visibility', 'Access supported live analytics and alerts to understand activity as it unfolds.'),
            ('chart', 'Better-Informed Decisions', 'Use footfall, dwell time, heatmaps and queue data to identify patterns and opportunities for improvement.'),
            ('layers', 'Flexible Integration', 'Connect compatible cameras and recording systems, subject to your existing setup and deployment requirements.')]
    benefits = f'''<section class="block" id="benefits">
    <div class="wrap">
      {head_block('Key benefits', 'Get More from Your Existing Camera Infrastructure', '')}
      <div class="kv-bens">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in bens)}</div>
    </div>
  </section>'''

    dash = f'''<section class="block" id="dashboard">
    <div class="wrap">
      {head_block('Dashboard', 'See the Numbers Behind What You See.', 'Bring important video analytics into one view. Monitor footfall, review activity across zones, understand dwell time and track queue patterns through an analytics dashboard.')}
      {ap.dash(kv_dash())}
      <p class="demo-note">Example dashboard with simulated data. Not a real store.</p>
      <p class="kv-body" style="max-width:62ch">Move from watching camera footage to understanding what the activity means for your business.</p>
      <p style="margin-top:28px"><a class="btn btn-blue" href="contact.html">Request a KenVision Demo</a></p>
    </div>
  </section>'''

    faq = f'''<section class="block" id="faq">
    <div class="wrap faq-grid">
      <div>
        <span class="eyebrow">FAQ</span>
        <h2 style="margin-top:18px">Frequently asked questions</h2>
      </div>
      <div>{''.join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(KV_FAQ))}</div>
    </div>
  </section>'''

    related = f'''<section class="block" id="related">
    <div class="wrap">
      {head_block('Related modules', 'Works well with.', 'Modules share one engine and dashboard, so they combine easily.')}
      <div class="related">{''.join(card(MOD[k]) for k in m['related'])}</div>
      <div class="proof" style="margin-top:48px">
        <a class="link-prev" href="kenvoice.html">← KenVoice</a>
        <a class="link-arrow" href="modules.html" style="margin-inline:auto">All modules</a>
        <a class="link-arrow" href="kensafety.html">KenSafety</a>
      </div>
    </div>
  </section>'''

    final = '''<section class="cta">
    <div class="wash wash-b" aria-hidden="true" style="top:10%;right:20%"></div>
    <div class="wash wash-a" aria-hidden="true" style="top:30%;left:20%"></div>
    <div class="wrap">
      <span class="eyebrow">Get started</span>
      <h2 style="margin-top:20px">Your Cameras Can Do More Than Record.</h2>
      <p class="lede" style="margin:20px auto 0">Discover how KenVision AI video analytics can help you understand footfall, customer movement, dwell time and queues across your business.</p>
      <div class="hero-ctas">
        <a class="btn btn-blue" href="contact.html">Book a Free Demo</a>
      </div>
      <p class="kv-tagline" style="margin-top:18px">See what your existing camera infrastructure can tell you.</p>
      <p class="kv-sign">KenVision by Intelense | Intelligence at the Edge.</p>
    </div>
  </section>'''

    ld = {'@context': 'https://schema.org', '@type': 'FAQPage',
          'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in KV_FAQ]}
    schema = '<script type="application/ld+json">' + json.dumps(ld) + '</script>'

    body = '\n\n  '.join([hero, problem, features, how, industries, retail, benefits, dash, faq, related, final, schema])
    return dict(file='kenvision.html', title='KenVision: AI Video Analytics Software | Intelense',
                desc="KenVision is AI-powered video analytics software. Track footfall, customer movement, dwell time and queues using your existing CCTV cameras.",
                active='kenvision', body=body, cctv=True)


# ---------------------------------------------------------------- shared blocks for reworked module pages

def faq_block(items, title='Frequently asked questions'):
    return f'''<section class="block" id="faq">
    <div class="wrap faq-grid">
      <div>
        <span class="eyebrow">FAQ</span>
        <h2 style="margin-top:18px">{title}</h2>
      </div>
      <div>{''.join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(items))}</div>
    </div>
  </section>'''


def faq_schema(items):
    import json
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage',
          'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in items]}
    return '<script type="application/ld+json">' + json.dumps(ld) + '</script>'


def related_block(m):
    i = MODULES.index(m)
    prev_m, next_m = MODULES[i - 1], MODULES[(i + 1) % len(MODULES)]
    return f'''<section class="block" id="related">
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


def final_cta(h2, lede, btn, support, sign):
    return f'''<section class="cta">
    <div class="wash wash-b" aria-hidden="true" style="top:10%;right:20%"></div>
    <div class="wash wash-a" aria-hidden="true" style="top:30%;left:20%"></div>
    <div class="wrap">
      <span class="eyebrow">Get started</span>
      <h2 style="margin-top:20px">{h2}</h2>
      {''.join(f'<p class="lede" style="margin:18px auto 0">{p}</p>' for p in lede)}
      <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">{btn}</a></div>
      <p class="kv-tagline" style="margin:18px auto 0;max-width:60ch">{support}</p>
      <p class="kv-sign">{sign}</p>
    </div>
  </section>'''


# ---------------------------------------------------------------- KenSafety page

def ks_mini(kind):
    b, v, m, g, c = '#0A34ED', '#7C28E9', '#6C6E82', '#e4e2dc', '#FF7953'
    if kind == 'ppe':
        rows = [('Hard hat', True), ('Hi-vis vest', True), ('Gloves', False)]
        fig = f'<circle cx="26" cy="16" r="8" fill="{m}"/><path d="M17 13a9 8 0 0118 0z" fill="{b}"/><rect x="15" y="26" width="22" height="30" rx="6" fill="#d0a43a"/><rect x="15" y="36" width="22" height="3" fill="#fff"/><rect x="17" y="56" width="7" height="14" rx="2" fill="{m}"/><rect x="28" y="56" width="7" height="14" rx="2" fill="{m}"/>'
        lst = ''.join(f'<rect x="64" y="{i * 23 + 2}" width="156" height="19" rx="9.5" fill="{"#e6f4f4" if ok else "#ffe9e2"}"/><circle cx="76" cy="{i * 23 + 11.5}" r="4" fill="{"#73C4C5" if ok else c}"/><text x="86" y="{i * 23 + 15}" font-size="10" fill="#242424">{n}</text><text x="212" y="{i * 23 + 15}" font-size="10" text-anchor="end" font-weight="600" fill="{"#1e5f60" if ok else "#9a3412"}">{"Detected" if ok else "Missing"}</text>' for i, (n, ok) in enumerate(rows))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true">{fig}{lst}</svg>'
    if kind == 'zone':
        hatch = ''.join(f'<line x1="{x}" y1="70" x2="{x + 60}" y2="10" stroke="{c}" stroke-opacity=".35" stroke-width="3"/>' for x in range(40, 200, 12))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><defs><clipPath id="kz"><rect x="70" y="10" width="140" height="58" rx="6"/></clipPath></defs><g clip-path="url(#kz)">{hatch}</g><rect x="70" y="10" width="140" height="58" rx="6" fill="none" stroke="{c}" stroke-dasharray="5 4" stroke-width="2"/><text x="140" y="8" text-anchor="middle" font-size="9" fill="{m}">Restricted zone</text><circle cx="30" cy="40" r="8" fill="{b}"/><circle cx="104" cy="40" r="8" fill="{c}"/><circle cx="104" cy="40" r="14" fill="none" stroke="{c}" stroke-width="2"/><path d="M40 40h46" stroke="{m}" stroke-dasharray="3 3"/></svg>'
    if kind == 'proximity':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><circle cx="66" cy="38" r="32" fill="{c}" fill-opacity=".1" stroke="{c}" stroke-dasharray="4 4" stroke-width="1.5"/><rect x="44" y="26" width="34" height="22" rx="4" fill="{b}"/><rect x="78" y="18" width="4" height="30" fill="{m}"/><rect x="78" y="44" width="16" height="3" fill="{m}"/><circle cx="52" cy="50" r="4" fill="#242424"/><circle cx="70" cy="50" r="4" fill="#242424"/><circle cx="118" cy="36" r="8" fill="{c}"/><path d="M98 54h18" stroke="{c}" stroke-width="2"/><text x="142" y="40" font-size="11" font-weight="600" fill="#242424">1.2 m</text><text x="142" y="54" font-size="9" fill="{m}">Too close</text></svg>'
    if kind == 'fire':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><circle cx="70" cy="18" r="10" fill="{g}"/><circle cx="84" cy="12" r="8" fill="{g}"/><circle cx="96" cy="20" r="9" fill="{g}"/><path d="M84 66c-14 0-20-9-18-19 2-8 9-11 9-20 7 5 9 10 9 14 3-3 4-7 4-10 8 6 12 14 12 21 0 9-6 14-16 14z" fill="{c}"/><path d="M85 66c-6 0-9-4-8-9 1-4 4-6 5-10 4 4 9 8 9 12 0 4-2 7-6 7z" fill="#ffd27a"/><rect x="58" y="6" width="54" height="64" rx="3" fill="none" stroke="{c}" stroke-width="2"/><text x="124" y="34" font-size="11" font-weight="600" fill="#242424">Smoke</text><text x="124" y="50" font-size="11" font-weight="600" fill="#242424">Flame</text><text x="124" y="64" font-size="9" fill="{m}">Flagged for review</text></svg>'
    if kind == 'fall':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><line x1="10" y1="62" x2="210" y2="62" stroke="{g}" stroke-width="2"/><rect x="60" y="48" width="58" height="12" rx="6" fill="{b}"/><circle cx="128" cy="53" r="7" fill="{m}"/><rect x="40" y="52" width="22" height="6" rx="3" fill="{m}"/><rect x="34" y="36" width="104" height="30" rx="3" fill="none" stroke="{c}" stroke-width="2"/><rect x="34" y="24" width="56" height="12" fill="{c}"/><text x="38" y="33" font-size="9" font-weight="600" fill="#101114">Fall 93%</text><text x="150" y="40" font-size="10" fill="#242424">Alert</text><text x="150" y="54" font-size="9" fill="{m}">Site team</text></svg>'
    if kind == 'report':
        rows = [('14:32', 'No hard hat · Dock B', c), ('11:05', 'Zone entry · Yard', c), ('09:48', 'Proximity · Aisle 3', '#73C4C5')]
        return '<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="0" y="0" width="220" height="72" rx="8" fill="#fff"/>' + ''.join(f'<circle cx="12" cy="{i * 22 + 13}" r="4" fill="{col}"/><text x="22" y="{i * 22 + 16}" font-size="9" fill="{m}">{tm}</text><text x="52" y="{i * 22 + 16}" font-size="10" fill="#242424">{t}</text><rect x="178" y="{i * 22 + 6}" width="34" height="14" rx="3" fill="{g}"/><text x="195" y="{i * 22 + 16}" text-anchor="middle" font-size="8" fill="{m}">CLIP</text>' for i, (tm, t, col) in enumerate(rows)) + '</svg>'
    if kind == 'dash':
        vals = [40, 52, 46, 61, 58, 70, 64]
        bars = ''.join(f'<path d="{_bar(8 + i * 20, 66 - h * .8, 14, h * .8)}" fill="{b}" opacity="{.5 + i * .07:.2f}"/>' for i, h in enumerate(vals))
        rows = ''.join(f'<rect x="160" y="{6 + i * 22}" width="200" height="16" rx="8" fill="#fff"/><circle cx="172" cy="{14 + i * 22}" r="4" fill="{col}"/><text x="182" y="{17 + i * 22}" font-size="9" fill="#242424">{t}</text>' for i, (t, col) in enumerate([('Missing vest · Dock A', c), ('Zone entry · Yard', c), ('Resolved · Aisle 3', '#73C4C5')]))
        return f'<svg viewBox="0 0 370 72" aria-hidden="true">{bars}{rows}</svg>'
    raise ValueError(kind)


def ks_types_chart():
    rows = [('Missing hard hat', 12), ('Missing hi-vis vest', 9), ('Restricted zone entry', 7), ('Human-vehicle proximity', 5), ('Fall or incident', 1), ('Fire or smoke', 0)]
    W, rowh, lab = 360, 30, 150
    out = [f'<svg class="chart" viewBox="0 0 {W} {rowh * len(rows) + 6}" role="img" aria-label="Safety violations this week by type">']
    for i, (n, v) in enumerate(rows):
        y = i * rowh + 6
        bw = max(v / 12 * (W - lab - 34), 2)
        out.append(f'<text x="0" y="{y + 13}" fill="#c9cbd6" font-size="11">{n}</text><rect x="{lab}" y="{y + 3}" width="{W - lab - 34}" height="14" rx="3" fill="#24262d"/>')
        out.append(f'<rect x="{lab}" y="{y + 3}" width="{bw:.1f}" height="14" rx="3" fill="#5b7cff" data-tip="{n} · {v} this week"/><text x="{W}" y="{y + 14}" text-anchor="end" fill="#e9e9ec" font-size="11" font-weight="600">{v}</text>')
    out.append('</svg>')
    return ''.join(out)


def ks_trend_chart():
    vals = [89, 90, 88, 91, 92, 90, 93, 92, 94, 93, 95, 94, 96, 94]
    W, H, ml, mb, mt = 560, 200, 34, 26, 14
    pw, ph = W - ml - 6, H - mb - mt
    lo, hi = 85, 100
    X = lambda i: ml + i * pw / (len(vals) - 1)
    Y = lambda v: mt + ph - (v - lo) / (hi - lo) * ph
    pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals))
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="PPE compliance over the last 14 days, rising from 89% to 94% against a 95% target.">']
    for gv in (85, 90, 95, 100):
        out.append(f'<line x1="{ml}" x2="{W - 6}" y1="{Y(gv):.1f}" y2="{Y(gv):.1f}" stroke="#2a2c33"/><text x="{ml - 8}" y="{Y(gv) + 3:.1f}" text-anchor="end" fill="#9b9daf" font-size="10">{gv}%</text>')
    out.append(f'<line x1="{ml}" x2="{W - 6}" y1="{Y(95):.1f}" y2="{Y(95):.1f}" stroke="#73C4C5" stroke-dasharray="5 4" stroke-width="1.5"/><text x="{ml + 6}" y="{Y(95) - 6:.1f}" text-anchor="start" fill="#9fe0e1" font-size="10" font-weight="600">Target 95%</text>')
    out.append(f'<polygon points="{ml},{Y(lo):.1f} {pts} {X(len(vals) - 1):.1f},{Y(lo):.1f}" fill="rgba(91,124,255,.14)"/><polyline points="{pts}" fill="none" stroke="#5b7cff" stroke-width="2" stroke-linejoin="round"/>')
    for i, v in enumerate(vals):
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{4 if i == len(vals) - 1 else 2.5}" fill="#5b7cff" stroke="#16171b" stroke-width="2" data-tip="Day {i + 1} · {v}% compliant"/>')
    out.append(f'<text x="{X(len(vals) - 1) - 4:.1f}" y="{Y(vals[-1]) + 20:.1f}" text-anchor="end" fill="#e9e9ec" font-size="11" font-weight="600">Today {vals[-1]}%</text>')
    for i, lab in ((0, '14 days ago'), (13, 'Today')):
        out.append(f'<text x="{X(i):.1f}" y="{H - 8}" text-anchor="{"start" if i == 0 else "end"}" fill="#9b9daf" font-size="10">{lab}</text>')
    out.append('</svg>')
    return ''.join(out)


def ks_matrix():
    zones = ['Dock A', 'Dock B', 'Aisle 3', 'Yard', 'Production']
    hours = ['06', '08', '10', '12', '14', '16', '18', '20']
    data = [[0, 1, 2, 1, 3, 2, 1, 0], [1, 2, 4, 2, 5, 3, 2, 1], [0, 1, 1, 2, 2, 3, 1, 0], [0, 0, 1, 1, 2, 1, 0, 0], [1, 1, 2, 3, 2, 2, 1, 1]]
    W, lab, cw, ch = 560, 82, (560 - 82) / 8, 26
    out = [f'<svg class="chart" viewBox="0 0 {W} {ch * len(zones) + 30}" role="img" aria-label="Safety events by zone and hour. Dock B at 14:00 has the most.">']
    for r, z in enumerate(zones):
        out.append(f'<text x="0" y="{r * ch + 17}" fill="#c9cbd6" font-size="11">{z}</text>')
        for col, hv in enumerate(hours):
            v = data[r][col]
            op = .08 + v / 5 * .82
            out.append(f'<rect x="{lab + col * cw + 1:.1f}" y="{r * ch + 2}" width="{cw - 2:.1f}" height="{ch - 4}" rx="4" fill="#7C28E9" fill-opacity="{op:.2f}" data-tip="{z} · {hv}:00 · {v} events"/>')
    for col, hv in enumerate(hours):
        out.append(f'<text x="{lab + col * cw + cw / 2:.1f}" y="{ch * len(zones) + 16}" text-anchor="middle" fill="#9b9daf" font-size="10">{hv}:00</text>')
    out.append('</svg>')
    return ''.join(out)


KS_FAQ = [
    ('What is AI workplace safety monitoring?', 'AI workplace safety monitoring uses artificial intelligence and computer vision to analyse camera feeds for safety-related events, such as missing protective equipment, restricted-zone entry and selected hazards. It helps safety teams identify potential issues without relying entirely on manual camera monitoring.'),
    ('What is KenSafety?', "KenSafety is Intelense's AI-powered safety monitoring solution. It uses compatible camera feeds to help detect PPE violations, restricted-zone entry, human-vehicle safety risks, fire, smoke and supported incidents, with alerts and reporting capabilities."),
    ('What is AI PPE detection?', 'AI PPE detection uses computer vision to identify whether workers appear to be wearing required personal protective equipment, such as helmets, high-visibility vests, gloves and boots, within camera-visible areas.'),
    ('Can KenSafety work with existing CCTV cameras?', 'Yes, KenSafety is designed to integrate with compatible existing CCTV cameras and recording systems. The exact compatibility depends on the camera setup, video streams and deployment requirements.'),
    ('Can KenSafety detect restricted-area entry?', 'KenSafety can monitor configured restricted zones and flag unauthorised entry when the relevant capability is enabled. This helps teams identify potential access and safety violations.'),
    ('Can KenSafety detect fire, smoke and falls?', 'KenSafety supports configured fire, smoke and fall-related detection capabilities. Performance depends on camera positioning, visibility, environmental conditions and deployment configuration. Alerts should complement established emergency procedures and safety systems.'),
    ('Which industries can use KenSafety?', 'KenSafety is suited to use cases in construction, manufacturing, warehouses, logistics, ports, infrastructure and other environments where monitoring safety conditions through cameras is useful.'),
    ('Does KenSafety replace safety officers?', 'No. KenSafety is designed to support safety teams, not replace them. AI detection, alerts and reports help teams identify potential issues, but people remain responsible for assessment, intervention and safety decisions.'),
    ('Does KenSafety provide compliance reports?', 'KenSafety supports incident records and safety reporting to help teams review events and monitor compliance trends. The specific reports available depend on the deployment.'),
    ('How can I get started with KenSafety?', 'Book a demo with Intelense. Share your industry, main safety concerns and existing camera setup so the team can explain how KenSafety may fit your requirements.'),
]



KS_HERO = dict(
    uid='ks', logo='kensafety', site='Distribution Centre · CAM-04 loading dock',
    aria='Loading dock camera flagging a worker without a hard hat inside a restricted zone, next to a moving forklift',
    media='<div class="tile-solo"><canvas class="cctv" data-scene="dock" width="960" height="540"></canvas></div>',
    kpis=[('hardhat', 'PPE compliance', '94%', '↗ 2 pts', 'pos', 'vs last week', [88, 90, 89, 91, 90, 92, 91, 93, 90, 92, 93, 94]),
          ('zone', 'Zone violations', '7', '↘ 30%', 'pos', 'vs yesterday', [12, 11, 13, 10, 11, 9, 10, 8, 9, 8, 7, 7])],
    alert=('High priority', 'neg', 'hardhat', '<b>No hard hat</b> in the restricted zone at Dock B.', '14:31'))


def ks_dash():
    days = [f'{d} Oct' for d in range(1, 15)]
    vals = [88, 90, 89, 91, 90, 92, 91, 93, 90, 92, 93, 96, 94, 94]
    main = ap.main('PPE compliance · last 14 days', '94%', '↗ 2 pts', 'pos', 'today', [('Compliance', False)],
                   ap.line_chart(days, vals, 11, '12 Oct · 96%', 'ks', (80, 85, 90, 95, 100), every=2))
    side = ap.feed([('hardhat', 'neg', '<b>No hard hat</b> in restricted zone · Dock B', '14:31'),
                    ('forklift', 'neg', '<b>Person in vehicle lane</b> · Aisle 3', '14:32'),
                    ('eye', 'warn', '<b>No hi-vis vest</b> · CAM-09, sent for review', '14:32'),
                    ('fall', 'violet', '<b>Slip incident</b> reviewed and closed by a supervisor', '11:20'),
                    ('doc', 'mute', '<b>Daily safety report</b> sent to 3 managers', '08:00')], title='Recent alerts')
    evs = ap.events([('PPE', 'neg', 'hardhat', 'Dock B', '3 alerts', 'Missing hard hats today'),
                     ('Zone', 'warn', 'zone', 'Forklift lane', '4 entries', 'Restricted-zone violations'),
                     ('Incident', 'violet', 'fall', 'Aisle 3', '1 slip', 'Reviewed · no injury'),
                     ('Compliance', 'pos', 'check', 'Site-wide', '94%', 'Up 2 pts on last week')])
    types = [('Hard hat', 12), ('Hi-vis', 8), ('Zone', 7), ('Vehicle', 4), ('Fall', 1)]
    bottom = [ap.media('CAM-04 · Loading dock', '<div class="tile-solo"><canvas class="cctv" data-scene="dock" width="480" height="270"></canvas></div>', foot=(('No hard hat', 'neg'), ('Restricted zone', 'warn'), ('Forklift moving', 'info'))),
              ap.card('Violations by type', ap.bar_chart([t for t, _ in types], [v for _, v in types], 0, lambda v: f'{v} alerts', 'ks'), sub='This week'),
              ap.card('Safety score', '<div class="ap-rings">' + ap.ring(88, '88', 'Site score', 'ks1') + ap.ring(92, '92%', 'Alerts reviewed', 'ks2') + '</div>'
                      '<div class="ap-split" style="margin-top:14px"><div class="ap-stat"><span>Open alerts</span><b>3</b></div><div class="ap-stat"><span>Incidents</span><b>2</b></div></div>')]
    return dict(uid='ks', logo='kensafety', alt='KenSafety', me='ST', nav=['hardhat', 'chart', 'zone', 'bell', 'doc', 'cog'],
                hello='Good afternoon, Safety team', sub='Distribution Centre · Site 2 · 14 cameras online', range='Today',
                aria='KenSafety dashboard with PPE compliance, restricted-zone violations, incidents and recent alerts',
                kpis=[('hardhat', 'PPE compliance', '94%', '↗ 2 pts', 'pos', 'vs last week', [88, 90, 89, 91, 90, 92, 91, 93, 90, 92, 93, 94]),
                      ('bell', 'Open alerts', '3', '1 high', 'neg', 'priority to review', [5, 4, 6, 3, 4, 5, 2, 4, 3, 4, 2, 3]),
                      ('zone', 'Zone violations', '7', '↘ 30%', 'pos', 'vs yesterday', [12, 11, 13, 10, 11, 9, 10, 8, 9, 8, 7, 7]),
                      ('fall', 'Incidents this week', '2', 'Reviewed', 'info', 'both closed', [1, 0, 1, 2, 1, 0, 1, 1, 0, 2, 1, 2])],
                main=main, side=side, events=evs, bottom=bottom)


def page_kensafety():
    m = MOD['kensafety']
    hero = f'''<section class="page-hero kv-hero" style="--mod:{m["color"]}">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap kv-hero-grid">
      <div class="kv-hero-copy">
        {crumbs(('modules.html', 'Modules'), (None, 'KenSafety'))}
        <span class="eyebrow">AI safety intelligence by Intelense</span>
        {logo_img(m, 0.36, 'hero-logo')}
        <h1>Spot Safety Risks Before They Become Bigger Problems.</h1>
        <p class="lede">KenSafety uses AI-powered video analytics to monitor workplace safety through compatible existing CCTV cameras. Detect missing protective equipment, identify restricted-zone entry, flag potential hazards and alert your team when something needs attention.</p>
        <p class="lede kv-sub">Help your team move from manually checking footage to more proactive safety monitoring.</p>
        <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">Book a Free Demo</a><a class="btn btn-ghost" href="#features">Explore Features</a></div>
        <p class="kv-tagline">AI-powered workplace safety monitoring for construction, manufacturing, warehouses and industrial facilities.</p>
      </div>
      <div class="kv-hero-visual">
        {ap.hero(KS_HERO)}
        <p class="demo-note">Simulated camera feed and example data</p>
      </div>
    </div>
  </section>'''

    problem = f'''<section class="block" id="problem">
    <div class="wrap">
      {head_block('The problem', "Safety Shouldn't Depend on Someone Watching Every Screen.", 'On a busy construction site, factory floor or warehouse, things can change in seconds.')}
      <div class="kv-problem">
        <div class="kv-questions">
          <p class="kv-answer" style="font-size:17px;color:#e9e6e3">A worker may enter a restricted area, operate without the required protective equipment or move too close to heavy machinery.</p>
          <p class="kv-answer" style="font-size:17px;color:#e9e6e3">Traditional CCTV records what happens. But reviewing every camera feed continuously is difficult, especially across large sites.</p>
          <p class="kv-q" style="border:0;padding:0;margin-top:8px">KenSafety uses AI to help identify potential safety risks as they appear on camera.</p>
        </div>
        <ul class="kv-points">
          <li>{icon('hardhat')}<div><b>Missing protective equipment?</b><span>Identify potential PPE violations, such as missing helmets or high-visibility vests.</span></div></li>
          <li>{icon('zone')}<div><b>Workers entering dangerous areas?</b><span>Monitor restricted zones and flag unauthorised entry.</span></div></li>
          <li>{icon('forklift')}<div><b>People and machinery working too close?</b><span>Detect configured human-vehicle safety-zone violations.</span></div></li>
          <li>{icon('fall')}<div><b>Fire, smoke or a potential fall?</b><span>Flag supported visual events so the relevant team can respond.</span></div></li>
          <li>{icon('text')}<div><b>Too much paperwork after an incident?</b><span>Maintain incident records and reports to support safety reviews and compliance documentation.</span></div></li>
        </ul>
      </div>
    </div>
  </section>'''

    feats = [
        ('ppe', 'AI PPE Detection &amp; Compliance', 'Make protective equipment checks more consistent.', ['Use AI PPE detection to identify when workers may be missing required safety equipment, including hard hats, high-visibility vests, gloves, boots and other configured PPE.', 'Monitor compliance across camera-covered work areas and help safety teams identify recurring violations.']),
        ('zone', 'Hazard Zone &amp; Restricted Area Detection', "Know when someone enters an area they shouldn't.", ['Define restricted areas and hazardous zones within camera views. KenSafety can flag unauthorised entry and configured zone violations, helping teams respond before a situation escalates.']),
        ('proximity', 'Human-Vehicle Safety Monitoring', 'Help keep workers and moving vehicles apart.', ['Monitor designated areas where pedestrians and vehicles such as forklifts or other site machinery operate near one another. Detect configured proximity risks and alert the relevant team when safety boundaries are breached.']),
        ('fire', 'AI Fire &amp; Smoke Detection', 'Identify potential fire hazards through camera feeds.', ['Use AI-powered visual detection to flag signs of fire or smoke in camera-visible areas. Give designated teams an additional way to identify potential hazards and investigate them promptly.']),
        ('fall', 'Fall &amp; Incident Detection', 'Flag potential incidents that need attention.', ['Detect supported events such as falls and other configured safety incidents from video feeds. Help teams identify situations that may require immediate investigation or assistance.']),
        ('report', 'Automated Safety Reports', 'Spend less time putting incident records together.', ['Maintain timestamped incident records, event details and available visual evidence. Review recurring violations and safety patterns to support audits, internal reviews and corrective action.']),
    ]
    feat_cards = ''.join(f'<article class="kv-feat"><div class="kv-mini">{ks_mini(k)}</div><span class="kv-num">{i + 1:02d}</span><h3>{t}</h3><p class="kv-strap">{s}</p>{"".join(f"<p>{p}</p>" for p in ps)}</article>' for i, (k, t, s, ps) in enumerate(feats))
    feat_cards += f'''<article class="kv-feat kv-feat-wide"><div class="kv-mini">{ks_mini('dash')}</div><div><span class="kv-num">07</span><h3>Safety Dashboard &amp; Alerts</h3><p class="kv-strap">Know where attention is needed.</p><p>Bring safety events and compliance information into a central dashboard. Help supervisors review alerts, identify recurring issues and monitor activity across supported camera feeds and locations.</p></div></article>'''
    features = f'''<section class="block" id="features">
    <div class="wrap">
      {head_block('Features', 'Everything You Need for Smarter Workplace Safety Monitoring', 'KenSafety combines AI video analytics, hazard detection and safety reporting to help teams understand risks across their work environments.')}
      <div class="kv-feats">{feat_cards}</div>
    </div>
  </section>'''

    steps = [('Connect Your Existing Cameras', 'Integrate compatible CCTV cameras and recording systems with KenSafety. Reuse your current setup where supported instead of replacing your entire camera infrastructure.'),
             ('Let AI Monitor for Safety Risks', 'AI analyses video feeds for configured safety conditions, such as missing PPE, restricted-zone entry, unsafe proximity between people and vehicles, and supported incident events.'),
             ('Alert Teams &amp; Record Events', 'When a configured event is detected, KenSafety can notify the relevant team through supported alert channels and create incident records for review.'),
             ('Review &amp; Improve Safety Practices', 'Use dashboards and reports to understand recurring violations, review incidents and identify areas where safety procedures may need attention.')]
    how = f'''<section class="block" id="how">
    <div class="wrap">
      {head_block('How it works', 'From Camera Footage to Actionable Safety Insights', 'KenSafety adds an AI-powered safety monitoring layer to your existing camera infrastructure.')}
      <ol class="kv-steps four">{''.join(f'<li><span>{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(steps))}</ol>
      <p style="margin-top:36px"><a class="btn btn-black" href="#example">See KenSafety in Action</a></p>
    </div>
  </section>'''

    inds = [('hardhat', 'Construction Sites', 'Monitor hard hat and high-visibility vest compliance, restricted areas, scaffolding zones, heavy machinery activity and potential falls.', 'industrial'),
            ('wrench', 'Manufacturing &amp; Industrial Facilities', 'Monitor PPE compliance, machine-adjacent safety zones and configured hazard areas across production floors.', 'industrial'),
            ('forklift', 'Warehouses &amp; Logistics', 'Identify potential risks around forklifts, pedestrian walkways, loading bays and restricted storage areas.', 'industrial'),
            ('route', 'Ports &amp; Transportation Hubs', 'Monitor designated operational zones, vehicle movement areas, restricted access points and camera-visible safety events.', 'smart-cities'),
            ('bolt', 'Energy &amp; Infrastructure', 'Support safety monitoring around designated high-risk areas, equipment zones and restricted operational spaces.', 'smart-cities'),
            ('layers', 'Commercial &amp; Large Facilities', 'Monitor selected areas for restricted entry, crowd-density concerns and configured fire or smoke events.', 'retail')]
    industries = f'''<section class="block" id="industries">
    <div class="wrap">
      {head_block('Industry applications', 'AI Safety Monitoring for High-Risk Work Environments', 'Different workplaces face different risks. KenSafety helps teams monitor camera-visible safety conditions across a range of industrial and commercial environments.')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p><a class="kv-link" href="industries.html#{a}">More on {IND[a]["name"].lower()} →</a></div>' for ic, t, d, a in inds)}</div>
    </div>
  </section>'''

    example = f'''<section class="block" id="example">
    <div class="wrap kv-split" style="align-items:start">
      <div>
        <span class="eyebrow">Real-world example</span>
        <h2 style="margin-top:18px">A Small Safety Violation Can Become a Serious Incident.</h2>
        <p class="lede" style="margin-top:20px">Imagine a busy warehouse where forklifts move between storage racks while workers handle incoming shipments.</p>
        <p class="kv-body">A pedestrian enters a designated vehicle movement zone. At the same time, another worker is operating without the required high-visibility vest.</p>
        <p class="kv-body">If no one notices immediately, the risks can increase.</p>
        <p class="kv-body">With KenSafety, AI video analytics can help identify configured human-vehicle zone violations and potential PPE non-compliance from compatible camera feeds.</p>
        <p class="kv-body">The relevant team can receive alerts, review the event and take corrective action.</p>
        <p class="kv-body"><b style="color:var(--off-black);font-weight:600">Instead of relying only on manual inspections or reviewing footage after an incident, your team gains another layer of visibility into everyday workplace risks.</b></p>
      </div>
      <div>
        <div class="tile-solo" role="img" aria-label="Warehouse camera flagging a pedestrian inside the forklift lane and a worker without a high-visibility vest">
          <canvas class="cctv" data-scene="whse" width="960" height="540"></canvas>
        </div>
        <ol class="ks-timeline">
          <li><time>14:32:07</time><div><b>Person in vehicle zone</b><span>CAM-09 · Aisle 3. Alert sent to the floor supervisor.</span></div><em class="bad">Alert</em></li>
          <li><time>14:32:09</time><div><b>No hi-vis vest detected</b><span>CAM-09 · Aisle 3. Added to today's PPE log.</span></div><em class="bad">Alert</em></li>
          <li><time>14:32:41</time><div><b>Supervisor acknowledged</b><span>Clip reviewed, worker reminded, incident record created.</span></div><em>Resolved</em></li>
        </ol>
        <p class="demo-note">Simulated camera feed and example events</p>
      </div>
    </div>
  </section>'''

    why = [('plug', 'Use Your Existing Camera Infrastructure', 'Integrate compatible CCTV cameras and recording systems to extend safety monitoring without necessarily installing a completely new camera network.'),
           ('clock', 'Monitor Beyond Scheduled Inspections', 'Use AI to monitor configured safety conditions across supported camera feeds, including outside scheduled manual inspection rounds.'),
           ('chart', 'Identify Recurring Safety Issues', 'Review incident records and compliance trends to understand where violations occur and which areas may require attention.'),
           ('bell', 'Respond to Potential Risks Sooner', 'Receive alerts for supported safety events and help the appropriate teams investigate and respond promptly.'),
           ('text', 'Support Safety Audits &amp; Reporting', 'Maintain structured incident records and reports to support internal reviews, compliance processes and corrective action.'),
           ('layers', 'Monitor Multiple Areas', 'Use centralised dashboards to review safety events across supported cameras, zones and locations.')]
    benefits = f'''<section class="block" id="why">
    <div class="wrap">
      {head_block('Why KenSafety?', 'More Visibility. More Consistent Safety Monitoring.', '')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in why)}</div>
    </div>
  </section>'''

    dash = f'''<section class="block" id="dashboard">
    <div class="wrap">
      {head_block('Dashboard', 'A Clearer View of Workplace Safety.', 'Bring important safety information into one place. Review PPE compliance, restricted-zone violations, detected incidents and safety trends through a central dashboard.')}
      {ap.dash(ks_dash())}
      <p class="demo-note">Example dashboard with simulated data. Not a real site.</p>
      <p class="kv-body" style="max-width:62ch">Understand where events are occurring, identify recurring problems and give your team the information it needs to take action.</p>
      <p style="margin-top:28px"><a class="btn btn-blue" href="contact.html">Request a KenSafety Demo</a></p>
    </div>
  </section>'''

    final = final_cta('Safer Workplaces Start with Better Visibility.',
                      ['From PPE compliance to hazard-zone monitoring, KenSafety helps you identify potential safety risks through your existing camera infrastructure.',
                       "Give your safety team better visibility into what's happening across your workplace."],
                      'Book a Free Demo',
                      "Tell us about your site, your safety requirements and your camera setup. We'll help you explore the right AI safety monitoring solution.",
                      'KenSafety by Intelense | Intelligence at the Edge.')

    body = '\n\n  '.join([hero, problem, features, how, industries, example, benefits, dash, faq_block(KS_FAQ), related_block(m), final, faq_schema(KS_FAQ)])
    return dict(file='kensafety.html', title='KenSafety: AI Workplace Safety Monitoring | Intelense',
                desc='KenSafety uses AI video analytics on your existing CCTV to detect missing PPE, restricted-zone entry, human-vehicle risks, fire, smoke and falls, with alerts and safety reports.',
                active='kensafety', body=body, cctv=True)


# ---------------------------------------------------------------- KenAgri page (precision agriculture)

AG_FIELDS = [
    # name, crop, polygon (fractions), row angle, health base
    ('A', 'Wheat', [(.04, .06), (.36, .05), (.37, .44), (.05, .46)], 0, .82),
    ('B', 'Corn', [(.40, .05), (.70, .06), (.69, .40), (.41, .43)], 90, .78),
    ('C', 'Soybean', [(.05, .52), (.37, .50), (.38, .94), (.06, .95)], 0, .74),
    ('D', 'Wheat', [(.42, .48), (.69, .45), (.70, .94), (.43, .95)], 90, .80),
    ('E', 'Corn', [(.74, .06), (.96, .07), (.95, .54), (.74, .55)], 0, .69),
    ('F', 'Orchard', [(.74, .60), (.95, .60), (.95, .94), (.74, .95)], 45, .84),
]
AG_STRESS = (.11, .58, .17, .22)  # x, y, w, h in map fractions, inside field C


def _ag_health(x, y, base, seed):
    import math
    v = base + .08 * math.sin(x * 23 + seed) * math.cos(y * 19 - seed) + .05 * math.sin((x + y) * 41 + seed * 2)
    sx, sy, sw, sh = AG_STRESS
    if sx <= x <= sx + sw and sy <= y <= sy + sh:
        cx, cy = sx + sw / 2, sy + sh / 2
        d = math.hypot((x - cx) / (sw / 2), (y - cy) / (sh / 2))
        v -= .42 * max(0, 1 - d * .8)
    return max(.15, min(.98, v))


def farm_map(dark=False, uid='m', labels=True, scan=False):
    W, H = 600, 400
    base, road, tree, ink, chip, rowc = ('#1c211b', '#3b3f3a', '#1f3a22', '#e9e9ec', 'rgba(16,17,20,.82)', 'rgba(255,255,255,.06)') if dark else ('#b9b08f', '#9e9a8e', '#3f5a36', '#101114', 'rgba(255,255,255,.9)', 'rgba(0,0,0,.08)')
    hc = '#6fdc6f' if dark else '#2e7d32'
    out = [f'<svg class="plan agmap" viewBox="0 0 {W} {H}" role="img" aria-label="Aerial farm map with crop-health overlay. Most fields are healthy; a section of block C shows lower crop health and is flagged for inspection.">', '<defs>']
    for i, (n, crop, poly, ang, hb) in enumerate(AG_FIELDS):
        pts = ' '.join(f'{x * W:.1f},{y * H:.1f}' for x, y in poly)
        out.append(f'<clipPath id="cf-{uid}-{n}"><polygon points="{pts}"/></clipPath>')
        out.append(f'<pattern id="rw-{uid}-{n}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate({ang})"><rect width="7" height="3" fill="{rowc}"/></pattern>')
    out.append('</defs>')
    out.append(f'<rect width="{W}" height="{H}" fill="{base}"/>')
    out.append(f'<path d="M0 {H * .475} H{W}" stroke="{road}" stroke-width="9"/><path d="M{W * .72} 0 V{H}" stroke="{road}" stroke-width="8"/><path d="M{W * .395} 0 V{H}" stroke="{road}" stroke-width="5"/>')
    for i, (n, crop, poly, ang, hb) in enumerate(AG_FIELDS):
        pts = ' '.join(f'{x * W:.1f},{y * H:.1f}' for x, y in poly)
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        cells = []
        step = .022
        y = min(ys)
        while y < max(ys):
            x = min(xs)
            while x < max(xs):
                v = _ag_health(x + step / 2, y + step / 2, hb, i * 1.7)
                cells.append(f'<rect x="{x * W:.1f}" y="{y * H:.1f}" width="{step * W + .6:.1f}" height="{step * H + .6:.1f}" fill="{hc}" fill-opacity="{.12 + v * .78:.2f}"/>')
                x += step
            y += step
        out.append(f'<g clip-path="url(#cf-{uid}-{n})"><rect x="0" y="0" width="{W}" height="{H}" fill="{"#283126" if dark else "#d9d2b4"}"/>{"".join(cells)}<rect width="{W}" height="{H}" fill="url(#rw-{uid}-{n})"/></g>')
        out.append(f'<polygon points="{pts}" fill="none" stroke="{"#4a5048" if dark else "#f4f1e6"}" stroke-width="1.5"/>')
    import random
    rnd = random.Random(7)
    for _ in range(46):
        x, y = rnd.choice([(rnd.uniform(.0, 1), rnd.uniform(.465, .485)), (rnd.uniform(.715, .727), rnd.uniform(0, 1)), (rnd.uniform(0, .03), rnd.uniform(0, 1))])
        out.append(f'<circle cx="{x * W:.1f}" cy="{y * H:.1f}" r="{rnd.uniform(4, 8):.1f}" fill="{tree}" opacity=".9"/>')
    out.append(f'<rect x="{W * .78}" y="{H * .555}" width="26" height="16" rx="2" fill="{"#555a5c" if dark else "#e9e5da"}"/><rect x="{W * .83}" y="{H * .56}" width="16" height="12" rx="2" fill="{"#44494b" if dark else "#c9c3b4"}"/>')
    sx, sy, sw, sh = AG_STRESS
    out.append(f'<rect x="{sx * W:.1f}" y="{sy * H:.1f}" width="{sw * W:.1f}" height="{sh * H:.1f}" rx="6" fill="none" stroke="#FF7953" stroke-width="2.5" stroke-dasharray="7 5"/>')
    out.append(f'<rect x="{sx * W:.1f}" y="{(sy + sh) * H + 4:.1f}" width="160" height="18" rx="3" fill="#FF7953"/><text x="{sx * W + 7:.1f}" y="{(sy + sh) * H + 17:.1f}" font-size="11" font-weight="600" fill="#101114">Low moisture · Block C3</text>')
    for x, y, v in ((.17, .66, '18%'), (.28, .78, '29%'), (.55, .7, '33%'), (.2, .25, '34%'), (.85, .3, '27%')):
        out.append(f'<circle cx="{x * W:.0f}" cy="{y * H:.0f}" r="9" fill="none" stroke="#73C4C5" stroke-width="2"/><circle cx="{x * W:.0f}" cy="{y * H:.0f}" r="4" fill="#73C4C5" data-tip="Soil sensor · moisture {v}"/>')
    if labels:
        for n, crop, poly, ang, hb in AG_FIELDS:
            x, y = poly[0][0] * W + 8, poly[0][1] * H + 8
            out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{len(crop) * 6.6 + 54:.0f}" height="20" rx="10" fill="{chip}"/><text x="{x + 10:.0f}" y="{y + 14:.0f}" font-size="11" font-weight="600" fill="{ink}">{n} · {crop}</text>')
    if scan:
        out.append(f'<rect class="agscan" x="0" y="0" width="{W}" height="3" fill="#73C4C5" opacity=".7"/>')
    out.append('</svg>')
    return ''.join(out)


def ag_legend(dark=False):
    c = '#6fdc6f' if dark else '#2e7d32'
    return f'<p class="ag-legend"><span>Lower crop health</span><i style="background:linear-gradient(90deg,{c}22,{c})"></i><span>Higher</span><b></b><span class="ag-sen">Soil sensor</span><span class="ag-str">Flagged area</span></p>'


def ag_moisture(dark=True):
    avg = [34, 33, 32, 33, 31, 30, 32, 31, 30, 31, 32, 31, 30, 31]
    c3 = [33, 31, 29, 27, 25, 23, 22, 21, 20, 19, 19, 18, 18, 18]
    W, H, ml, mb, mt = 560, 210, 34, 26, 14
    pw, ph = W - ml - 100, H - mb - mt
    lo, hi = 10, 40
    ink, mute, grid, card = ('#e9e9ec', '#9b9daf', '#2a2c33', '#16171b') if dark else ('#242424', '#6C6E82', '#e4e2dc', '#ffffff')
    ca, cc = ('#5b7cff' if dark else '#0A34ED'), '#FF7953'
    X = lambda i: ml + i * pw / 13
    Y = lambda v: mt + ph - (v - lo) / (hi - lo) * ph
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Soil moisture over 14 days: block C3 falls from 33% to 18% while the field average stays near 31%.">']
    for gv in (10, 20, 30, 40):
        out.append(f'<line x1="{ml}" x2="{ml + pw}" y1="{Y(gv):.1f}" y2="{Y(gv):.1f}" stroke="{grid}"/><text x="{ml - 8}" y="{Y(gv) + 3:.1f}" text-anchor="end" fill="{mute}" font-size="10">{gv}%</text>')
    out.append(f'<line x1="{ml}" x2="{ml + pw}" y1="{Y(25):.1f}" y2="{Y(25):.1f}" stroke="{mute}" stroke-dasharray="4 4"/><text x="{ml + 6}" y="{Y(25) + 14:.1f}" fill="{mute}" font-size="10">Irrigation threshold 25%</text>')
    for vals, col, lab in ((avg, ca, 'Average'), (c3, cc, 'Block C3')):
        pts = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round"/>')
        for i, v in enumerate(vals):
            out.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="{3.5 if i == 13 else 2.2}" fill="{col}" stroke="{card}" stroke-width="2" data-tip="{lab} · day {i + 1} · {v}%"/>')
        out.append(f'<text x="{X(13) + 8:.1f}" y="{Y(vals[-1]) + 4:.1f}" fill="{ink}" font-size="11" font-weight="600">{lab} {vals[-1]}%</text>')
    out.append(f'<text x="{ml}" y="{H - 8}" fill="{mute}" font-size="10">14 days ago</text><text x="{ml + pw}" y="{H - 8}" text-anchor="end" fill="{mute}" font-size="10">Today</text>')
    out.append('</svg>')
    return ''.join(out)


def ag_yield():
    rows = [('A · Wheat', 4.9, .3), ('B · Corn', 9.8, .6), ('C · Soybean', 2.6, .4), ('D · Wheat', 5.1, .3), ('E · Corn', 8.7, .7)]
    W, rowh, lab, mx = 360, 30, 96, 11
    out = [f'<svg class="chart" viewBox="0 0 {W} {rowh * len(rows) + 22}" role="img" aria-label="Estimated yield by field in tonnes per hectare, with forecast ranges">']
    span = W - lab - 50
    for i, (n, v, e) in enumerate(rows):
        y = i * rowh + 6
        out.append(f'<text x="0" y="{y + 13}" fill="#c9cbd6" font-size="11">{n}</text><rect x="{lab}" y="{y + 3}" width="{span}" height="14" rx="3" fill="#24262d"/>')
        out.append(f'<rect x="{lab}" y="{y + 3}" width="{v / mx * span:.1f}" height="14" rx="3" fill="#5fbf5f" data-tip="{n} · {v} t/ha (±{e})"/>')
        x1, x2 = lab + (v - e) / mx * span, lab + (v + e) / mx * span
        out.append(f'<path d="M{x1:.1f} {y + 10}H{x2:.1f}M{x1:.1f} {y + 5}V{y + 15}M{x2:.1f} {y + 5}V{y + 15}" stroke="#e9e9ec" stroke-width="1.5"/>')
        out.append(f'<text x="{W}" y="{y + 14}" text-anchor="end" fill="#e9e9ec" font-size="11" font-weight="600">{v} t/ha</text>')
    out.append(f'<text x="{lab}" y="{rowh * len(rows) + 16}" fill="#9b9daf" font-size="10">Bar = estimate · whisker = forecast range</text></svg>')
    return ''.join(out)


def ag_weather():
    days = [('Fri', 22, 13, 10), ('Sat', 24, 14, 5), ('Sun', 21, 12, 60), ('Mon', 18, 10, 80), ('Tue', 19, 11, 30), ('Wed', 23, 13, 10), ('Thu', 25, 15, 0)]
    return '<div class="ag-weather">' + ''.join(f'<div data-tip="{d} · high {hi}° · low {lo}° · rain {r}%"><b>{d}</b><span class="t">{hi}°<small>{lo}°</small></span><span class="r"><i style="height:{max(r, 4) * .4:.0f}px"></i></span><small>{r}% rain</small></div>' for d, hi, lo, r in days) + '</div>'


def ag_mini(kind):
    g, m, c, b, ash = '#2e7d32', '#6C6E82', '#FF7953', '#0A34ED', '#e4e2dc'
    if kind == 'health':
        import math
        cells = ''.join(f'<rect x="{col * 22 + 1}" y="{r * 24 + 1}" width="20" height="22" rx="4" fill="{g}" opacity="{.25 + .7 * (.82 + .1 * math.sin(col * 1.3 + r) - (.55 if col in (6, 7) and r in (1, 2) else 0)):.2f}"/>' for r in range(3) for col in range(10))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true">{cells}<rect x="131" y="24" width="46" height="48" rx="6" fill="none" stroke="{c}" stroke-width="2" stroke-dasharray="4 3"/></svg>'
    if kind == 'pest':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><path d="M30 60C30 30 60 10 100 12C98 46 70 64 30 60Z" fill="{g}" opacity=".85"/><path d="M30 60L92 18" stroke="#fff" stroke-width="1.5" opacity=".7"/><circle cx="62" cy="34" r="4" fill="#7a5a2c"/><circle cx="72" cy="42" r="3" fill="#7a5a2c"/><circle cx="56" cy="46" r="2.5" fill="#7a5a2c"/><circle cx="64" cy="40" r="20" fill="none" stroke="{c}" stroke-width="2" stroke-dasharray="4 3"/><text x="118" y="34" font-size="11" font-weight="600" fill="#242424">Possible blight</text><text x="118" y="50" font-size="10" fill="{m}">Inspect block C</text></svg>'
    if kind == 'yield':
        past = [3.9, 4.3, 4.1, 4.4]
        bars = ''.join(f'<path d="{_bar(12 + i * 34, 66 - v * 11, 22, v * 11)}" fill="{ash}"/>' for i, v in enumerate(past))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true">{bars}<path d="{_bar(148, 66 - 4.6 * 11, 22, 4.6 * 11)}" fill="{g}"/><path d="M159 10V24M153 10H165M153 24H165" stroke="#242424" stroke-width="1.5"/><text x="176" y="30" font-size="10" font-weight="600" fill="#242424">4.6 t/ha</text><text x="176" y="44" font-size="9" fill="{m}">forecast</text></svg>'
    if kind == 'irrigation':
        pts = [(0, 30), (20, 36), (40, 42), (60, 48), (70, 22), (90, 28), (110, 34), (130, 40), (150, 46), (160, 20), (180, 26), (200, 32), (220, 38)]
        poly = ' '.join(f'{x},{y}' for x, y in pts)
        drops = ''.join(f'<path d="M{x} 6c-4 6-6 8-6 11a6 6 0 0012 0c0-3-2-5-6-11z" fill="{b}"/>' for x in (66, 156))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><line x1="0" x2="220" y1="46" y2="46" stroke="{m}" stroke-dasharray="3 3"/><text x="2" y="62" font-size="9" fill="{m}">Moisture threshold</text><polyline points="{poly}" fill="none" stroke="{g}" stroke-width="2"/>{drops}</svg>'
    if kind == 'soil':
        stats = [('Soil temp', '18°C', .55), ('Moisture', '31%', .62), ('Rain 24h', '4 mm', .2)]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<text x="0" y="{i * 24 + 14}" font-size="10" fill="{m}">{n}</text><rect x="66" y="{i * 24 + 5}" width="110" height="10" rx="5" fill="{ash}"/><rect x="66" y="{i * 24 + 5}" width="{110 * p:.0f}" height="10" rx="5" fill="{g}"/><text x="220" y="{i * 24 + 14}" text-anchor="end" font-size="10" font-weight="600" fill="#242424">{v}</text>' for i, (n, v, p) in enumerate(stats)) + '</svg>'
    if kind == 'aerial':
        grid = ''.join(f'<rect x="{60 + col * 16}" y="{40 + r * 10}" width="15" height="9" rx="2" fill="{g}" opacity="{.35 + ((col * 7 + r * 3) % 5) * .12:.2f}"/>' for r in range(3) for col in range(8))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><path d="M110 18L64 70H188Z" fill="#73C4C5" opacity=".18"/>{grid}<rect x="98" y="8" width="24" height="8" rx="3" fill="#242424"/><path d="M90 8h-8M138 8h-8M86 6v4M134 6v4" stroke="#242424" stroke-width="2"/><text x="0" y="16" font-size="9" fill="{m}">Drone</text><text x="0" y="28" font-size="9" fill="{m}">+ satellite</text></svg>'
    raise ValueError(kind)


KA_FAQ = [
    ('What is precision agriculture?', 'Precision agriculture uses data, technology and field-level analysis to help farmers manage crops and resources more effectively. It can include satellite imagery, drones, soil sensors, weather data and AI.'),
]



def ka_hero():
    return dict(
        uid='ka', logo='kenagri', site='North Farm · Crop health map',
        aria='Crop health map of six fields with one low-health block highlighted for inspection',
        media=f'<div class="ap-map">{farm_map(True, "hero", True, True)}{ag_legend(True)}</div>',
        kpis=[('leaf', 'Avg crop health', '0.78', '↗ 0.03', 'pos', 'vs last week', [0.70, 0.71, 0.72, 0.72, 0.73, 0.74, 0.75, 0.75, 0.76, 0.77, 0.77, 0.78]),
              ('drop', 'Soil moisture', '31%', '↘ 4 pts', 'neg', 'this week', [36, 35, 35, 34, 34, 33, 33, 32, 32, 31, 31, 31])],
        alert=('Inspect', 'neg', 'leaf', '<b>Block C3</b> health dropped to 0.64 with low soil moisture.', '2 days ago'))


def ka_dash():
    weeks = [f'W{i}' for i in range(1, 15)]
    vals = [0.42, 0.48, 0.55, 0.61, 0.66, 0.70, 0.73, 0.75, 0.77, 0.79, 0.81, 0.79, 0.77, 0.76]
    prev = [0.40, 0.45, 0.51, 0.57, 0.62, 0.66, 0.69, 0.71, 0.73, 0.75, 0.76, 0.75, 0.74, 0.73]
    main = ap.main('Average crop health · this season', '0.76', '↗ 0.03', 'pos', 'vs last season', [('This season', False), ('Last season', True)],
                   ap.line_chart(weeks, vals, 10, 'Week 11 · 0.81', 'ka', (0.4, 0.5, 0.6, 0.7, 0.8, 0.9), prev, every=2))
    side = ap.feed([('leaf', 'neg', '<b>Field C3</b> health down 0.06 this week', 'Mon'),
                    ('drop', 'warn', '<b>Soil moisture</b> below 20% in block C3', 'Mon'),
                    ('sun', 'info', '<b>Rain likely</b> Sunday to Monday · 18 mm', 'Mon'),
                    ('drone', 'violet', '<b>Drone survey</b> uploaded for fields A to D', 'Sun'),
                    ('chart', 'pos', '<b>Yield estimate</b> updated for the season', 'Sat')])
    evs = ap.events([('Crop health', 'neg', 'leaf', 'Field C · Soybean', '0.64', 'Inspect block C3'),
                     ('Moisture', 'warn', 'drop', 'Field E · Corn', '27%', 'Watch over the next 3 days'),
                     ('Weather', 'info', 'sun', 'Next 7 days', '18 mm', 'Rain likely Sunday to Monday'),
                     ('Irrigation', 'pos', 'tractor', 'Next window', 'Thu', 'Skip C3 rotation after rain')])
    yld = [('A', 4.1), ('B', 9.8), ('C', 2.6), ('D', 4.3), ('E', 8.9), ('F', 6.2)]
    rows = [('Field A', 'Wheat', 'Health 0.82', 'pos', 82, 'Healthy', 'pos'), ('Field C', 'Soybean · block C3', 'Health 0.64', 'neg', 64, 'Inspect', 'neg'),
            ('Field E', 'Corn', 'Health 0.69', 'warn', 69, 'Watch', 'warn'), ('Field F', 'Orchard', 'Health 0.84', 'pos', 84, 'Healthy', 'pos')]
    bottom = [ap.media('Crop health map', f'<div class="ap-map">{farm_map(True, "dash", True)}{ag_legend(True)}</div>', tag=('Imagery 2 days ago', 'mute'), cls='ap-wide'),
              ap.card('Estimated yield', ap.bar_chart([f'Field {f}' for f, _ in yld], [v for _, v in yld], 1, lambda v: f'{v:g} t/ha', 'ka'), sub='Tonnes per hectare, by field'),
              ap.tasks(rows, 'Field status', 'Six fields', cls='ap-full')]
    return dict(uid='ka', logo='kenagri', alt='KenAgri', me='NF', nav=['leaf', 'chart', 'drone', 'drop', 'bell', 'cog'],
                hello='Good morning, North Farm', sub='6 fields · 412 ha · Imagery updated 2 days ago', range='This week',
                aria='KenAgri dashboard with crop health, soil moisture, weather, yield estimates and field status',
                kpis=[('layers', 'Fields monitored', '6', '412 ha', 'info', 'in total', None),
                      ('leaf', 'Avg crop health', '0.76', '↗ 0.03', 'pos', 'vs last week', [0.70, 0.71, 0.72, 0.72, 0.73, 0.74, 0.75, 0.75, 0.74, 0.75, 0.76, 0.76]),
                      ('alert', 'Need attention', '2', 'C3 · E', 'neg', 'low moisture, watch', [0, 0, 1, 1, 1, 0, 1, 1, 2, 1, 2, 2]),
                      ('drop', 'Next irrigation', 'Thu', 'Rain Sun', 'info', '18 mm expected', None)],
                main=main, side=side, events=evs, bottom=bottom)


def page_kenagri():
    m = MOD['kenagri']
    hero = f'''<section class="page-hero kv-hero" style="--mod:{m["color"]}">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap kv-hero-grid">
      <div class="kv-hero-copy">
        {crumbs(('modules.html', 'Modules'), (None, 'KenAgri'))}
        <span class="eyebrow">AI-powered precision agriculture by Intelense</span>
        {logo_img(m, 0.36, 'hero-logo')}
        <h1>Smarter Farming Starts with Better Information.</h1>
        <p class="lede">KenAgri uses AI to help farmers and agricultural businesses understand crop health, identify potential pest and disease problems, predict yields and make smarter irrigation decisions.</p>
        <p class="lede kv-sub">By bringing together available satellite imagery, drone images, ground sensors and weather data, KenAgri turns field information into practical insights that help you manage your crops with greater confidence.</p>
        <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">Get a Free Crop Health Assessment</a><a class="btn btn-ghost" href="#features">Explore KenAgri</a></div>
        <p class="kv-tagline">AI agriculture solutions for crop monitoring, precision farming and smarter resource management.</p>
      </div>
      <div class="kv-hero-visual">
        {ap.hero(ka_hero())}
        <p class="demo-note">Illustrative field map and example data</p>
      </div>
    </div>
  </section>'''

    problem = f'''<section class="block" id="problem">
    <div class="wrap">
      {head_block('The problem', 'Your Crops Tell a Story. Are You Seeing the Early Signs?', "A healthy-looking field doesn't always tell the whole story.")}
      <div class="kv-problem">
        <div class="kv-questions">
          <p class="kv-answer" style="font-size:17px;color:#e9e6e3">Water stress, nutrient deficiencies, pests and diseases can develop across different parts of a farm, sometimes before the symptoms become obvious.</p>
          <p class="kv-answer" style="font-size:17px;color:#e9e6e3">Checking every field manually takes time, and decisions based on limited information can lead to unnecessary resource use or missed warning signs.</p>
          <p class="kv-q" style="border:0;padding:0;margin-top:8px">KenAgri helps you understand what's happening across your fields using AI-powered crop monitoring and agricultural data analytics.</p>
        </div>
        <ul class="kv-points">
          <li>{icon('leaf')}<div><b>Crop problems going unnoticed?</b><span>Monitor crop conditions and identify areas that may need closer inspection.</span></div></li>
          <li>{icon('air')}<div><b>Not sure when to irrigate?</b><span>Use available soil moisture, weather and crop information to support irrigation planning.</span></div></li>
          <li>{icon('chart')}<div><b>Uncertain about your upcoming harvest?</b><span>Use yield prediction to help estimate potential production and plan ahead.</span></div></li>
          <li>{icon('search')}<div><b>Pests or diseases spreading across fields?</b><span>Identify potential problem areas earlier and prioritise field inspections.</span></div></li>
          <li>{icon('layers')}<div><b>Managing multiple fields or large estates?</b><span>Bring available field data into one view to understand conditions across different areas.</span></div></li>
        </ul>
      </div>
    </div>
  </section>'''

    feats = [
        ('health', 'AI Crop Health Monitoring', 'Know which parts of your field need attention.', ['Analyse available satellite and drone imagery to monitor crop conditions across different field areas. Identify unusual patterns and potential signs of crop stress so you can prioritise inspections and take action where needed.']),
        ('pest', 'AI Pest &amp; Disease Detection', 'Spot potential crop problems earlier.', ['Use AI to analyse available crop imagery and sensor data for patterns associated with potential pests, diseases and crop stress. Identify areas that need closer inspection and help your team investigate problems before they spread further.']),
        ('yield', 'Crop Yield Prediction', 'Plan ahead with a clearer picture of your harvest.', ['Use available crop health information, historical yield records, weather conditions and other field data to estimate potential harvest output.', 'Yield predictions can help agricultural businesses plan harvesting, labour, storage, transport and market supply more effectively.']),
        ('irrigation', 'Smart Irrigation Management', 'Give your crops water based on what they need.', ['Use soil moisture readings, weather information and crop requirements to support irrigation planning. Where compatible sensors and irrigation equipment are integrated, KenAgri can support automated irrigation workflows.', 'For farms without connected irrigation hardware, available insights can help guide manual watering schedules.']),
        ('soil', 'Soil &amp; Weather Analytics', 'Understand the conditions shaping your crops.', ['Bring together available soil, temperature, moisture and weather data to understand how growing conditions change across your fields.', 'Use these insights to support irrigation planning, crop care and decisions about field management.']),
        ('aerial', 'Satellite &amp; Drone Crop Analysis', 'Monitor more land without checking every field on foot.', ['Use satellite imagery and drone-based crop analysis to assess large areas, identify unusual patterns and focus field visits where they are most useful.', 'Combine aerial observations with ground-level data for a more complete understanding of crop conditions.']),
    ]
    features = f'''<section class="block" id="features">
    <div class="wrap">
      {head_block('Features', 'Everything You Need to Understand Your Fields Better', 'KenAgri combines AI crop monitoring, predictive analytics and agricultural data to help you make informed decisions throughout the growing season.')}
      <div class="kv-feats">{''.join(f'<article class="kv-feat"><div class="kv-mini">{ag_mini(k)}</div><span class="kv-num">{i + 1:02d}</span><h3>{t}</h3><p class="kv-strap">{s}</p>{"".join(f"<p>{p}</p>" for p in ps)}</article>' for i, (k, t, s, ps) in enumerate(feats))}</div>
    </div>
  </section>'''

    steps = [('Connect Your Field Data', 'Bring in available satellite imagery, drone images, ground sensor readings, weather information and historical farm records. The data sources used depend on your farm and deployment setup.'),
             ('Let AI Analyse Your Crops', 'AI analyses the available information to identify crop stress patterns, potential pest and disease risks, changing field conditions and factors that may affect yield.'),
             ('Get Insights for Your Next Step', 'Review crop health information, yield estimates and irrigation recommendations through available dashboards, reports and alerts. Use these insights to prioritise inspections and plan field operations.'),
             ('Monitor and Adjust Throughout the Season', 'Continue reviewing field conditions as new imagery and data become available. Use updated insights to support decisions as your crops grow and conditions change.')]
    how = f'''<section class="block" id="how">
    <div class="wrap">
      {head_block('How it works', 'From Field Data to Better Farming Decisions', 'KenAgri brings available agricultural data together and turns it into insights you can use.')}
      <ol class="kv-steps four">{''.join(f'<li><span>{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(steps))}</ol>
      <p style="margin-top:36px"><a class="btn btn-black" href="#example">See KenAgri in Action</a></p>
    </div>
  </section>'''

    inds = [('leaf', 'Row Crops', 'Monitor crops such as wheat, corn, soybeans and other field crops. Identify areas showing signs of stress and support decisions about irrigation, crop care and input planning.'),
            ('tractor', 'Horticulture &amp; Orchards', 'Monitor crop conditions across orchards, fruit farms and horticultural operations. Identify areas that may require closer inspection and track changes throughout the growing season.'),
            ('layers', 'Plantation Agriculture', 'Support monitoring across large tea, rubber, palm oil, cocoa and other plantation estates. Compare conditions across field blocks and prioritise areas that need attention.'),
            ('air', 'Paddy &amp; Rice Farming', 'Use available water-level, soil moisture, weather and crop information to support water management and monitor changing field conditions throughout the growing cycle.'),
            ('home', 'Greenhouses &amp; Protected Cultivation', 'Monitor available environmental and crop data across greenhouse operations. Support decisions around irrigation, growing conditions and potential pest or disease concerns.')]
    industries = f'''<section class="block" id="industries">
    <div class="wrap">
      {head_block('Industry applications', 'Precision Agriculture for Different Crops and Growing Environments', 'Every crop has different needs. KenAgri helps agricultural businesses use available field data to monitor crop conditions and make better-informed decisions across different farming environments.')}
      <div class="caps ag-caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in inds)}<div class="cap ag-more"><h3>Farms and agriculture</h3><p>See how Intelense supports agricultural businesses across the platform.</p><a class="kv-link" href="industries.html#agriculture">More on agriculture →</a></div></div>
    </div>
  </section>'''

    example = f'''<section class="block" id="example">
    <div class="wrap kv-split" style="align-items:start">
      <div>
        <span class="eyebrow">Real-world example</span>
        <h2 style="margin-top:18px">A Field Can Look Fine from a Distance and Still Need Attention.</h2>
        <p class="lede" style="margin-top:20px">Imagine you manage a large farm. Most of your crops appear healthy, but a section of the field is receiving less water than expected.</p>
        <p class="kv-body">Without detailed field information, the issue may go unnoticed until the crops begin showing visible signs of stress.</p>
        <p class="kv-body">With KenAgri, available satellite or drone imagery and ground sensor data can help identify unusual patterns in that section.</p>
        <p class="kv-body">Your team can then inspect the affected area, investigate the cause and decide whether irrigation or another corrective action is needed.</p>
        <p class="kv-body">The same approach can help you monitor potential pest and disease concerns, compare crop conditions across fields and plan for the upcoming harvest.</p>
        <p class="kv-body"><b style="color:var(--off-black);font-weight:600">Instead of treating every part of the farm the same way, use field-level insights to focus attention where it matters most.</b></p>
      </div>
      <div>
        <div class="panel ag-panel">{farm_map(False, 'ex', True)}</div>
        <div class="panel" style="margin-top:12px"><h3 style="font-size:16px;margin-bottom:10px">Soil moisture · last 14 days</h3>{ag_moisture(False)}</div>
        <ol class="ks-timeline">
          <li><time>Day 9</time><div><b>Imagery flags block C3</b><span>Crop health in one section falls below the field average.</span></div><em class="bad">Flagged</em></li>
          <li><time>Day 10</time><div><b>Sensors confirm low moisture</b><span>Soil moisture in C3 drops below the irrigation threshold.</span></div><em class="bad">Alert</em></li>
          <li><time>Day 11</time><div><b>Team inspects and adjusts irrigation</b><span>Section C3 added to the next watering schedule.</span></div><em>Action</em></li>
        </ol>
        <p class="demo-note">Illustrative example and data</p>
      </div>
    </div>
  </section>'''

    why = [('leaf', 'A Clearer Picture of Crop Health', 'Understand field conditions through available imagery and sensor data instead of relying only on occasional visual inspections.'),
           ('search', 'Earlier Visibility into Potential Problems', 'Identify unusual crop patterns and potential stress indicators so your team can investigate areas that may need attention.'),
           ('air', 'Better Use of Water and Other Resources', 'Use available soil, crop and weather information to support irrigation planning and field management decisions.'),
           ('chart', 'Plan for the Harvest', 'Use yield estimates and crop monitoring insights to support harvesting schedules, labour planning and supply preparation.'),
           ('layers', 'Monitor Large Areas More Efficiently', 'Bring information from multiple fields or farm blocks into a central view and prioritise inspections where they are most useful.'),
           ('timeline', 'Adapt as Conditions Change', 'Review updated field information as new data becomes available and adjust farm management decisions throughout the growing season.')]
    benefits = f'''<section class="block" id="why">
    <div class="wrap">
      {head_block('Why KenAgri?', 'Less Guesswork. More Informed Farming Decisions.', '')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in why)}</div>
    </div>
  </section>'''

    table_rows = [('A', 'Wheat', '0.82', '34%', 'Healthy', ''), ('B', 'Corn', '0.78', '31%', 'Healthy', ''), ('C', 'Soybean', '0.64', '18%', 'Inspect C3', 'bad'), ('D', 'Wheat', '0.80', '33%', 'Healthy', ''), ('E', 'Corn', '0.69', '27%', 'Watch', 'warn'), ('F', 'Orchard', '0.84', '30%', 'Healthy', '')]
    dash = f'''<section class="block" id="dashboard">
    <div class="wrap">
      {head_block('Dashboard', "See What's Happening Across Your Fields.", 'Bring available crop health indicators, field conditions, yield estimates and irrigation insights into one place.')}
      {ap.dash(ka_dash())}
      <p class="demo-note">Example dashboard with illustrative data. Not a real farm.</p>
      <p class="kv-body" style="max-width:62ch">Compare different areas of your farm, identify potential problem zones and understand which fields may need closer attention.</p>
      <p class="kv-body" style="max-width:62ch">With a clearer view of your agricultural data, you can spend less time piecing together information and more time making informed decisions.</p>
      <p style="margin-top:28px"><a class="btn btn-blue" href="contact.html">Request a KenAgri Demo</a></p>
    </div>
  </section>'''

    final = final_cta('Smarter Farming Starts with Better Information.',
                      ['See how KenAgri can bring your satellite, drone, sensor and weather data together into practical field insights.'],
                      'Get a Free Crop Health Assessment',
                      'Tell us about your farm, your crops and the data you already have.',
                      'KenAgri by Intelense | Intelligence at the Edge.')

    body = '\n\n  '.join([hero, problem, features, how, industries, example, benefits, dash, faq_block(KA_FAQ), related_block(m), final, faq_schema(KA_FAQ)])
    return dict(file='kenagri.html', title='KenAgri: AI-Powered Precision Agriculture | Intelense',
                desc='KenAgri uses AI with satellite imagery, drone images, ground sensors and weather data to monitor crop health, flag pests and disease, predict yields and guide irrigation.',
                active='kenagri', body=body)


# ---------------------------------------------------------------- KenHome page

def kh_mini(kind):
    b, m, c, ash, t = '#0A34ED', '#6C6E82', '#FF7953', '#e4e2dc', '#73C4C5'
    if kind == 'intrusion':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><path d="M20 40L60 12L100 40V68H20Z" fill="none" stroke="{m}" stroke-width="2"/><rect x="50" y="46" width="20" height="22" fill="{ash}"/><rect x="112" y="18" width="96" height="50" rx="6" fill="none" stroke="{c}" stroke-width="2" stroke-dasharray="5 4"/><text x="118" y="14" font-size="9" fill="{m}">Garden boundary</text><circle cx="168" cy="40" r="7" fill="{c}"/><rect x="161" y="48" width="14" height="16" rx="4" fill="{c}"/><rect x="152" y="28" width="32" height="40" fill="none" stroke="{c}" stroke-width="1.5"/></svg>'
    if kind == 'fall':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><line x1="10" y1="62" x2="210" y2="62" stroke="{ash}" stroke-width="2"/><rect x="60" y="48" width="58" height="12" rx="6" fill="#7a6a8a"/><circle cx="128" cy="53" r="7" fill="#b9a99a"/><rect x="40" y="52" width="22" height="6" rx="3" fill="{m}"/><rect x="34" y="36" width="104" height="30" rx="3" fill="none" stroke="{c}" stroke-width="2"/><rect x="34" y="24" width="86" height="12" fill="{c}"/><text x="38" y="33" font-size="9" font-weight="600" fill="#101114">Inactive 2m 10s</text><text x="150" y="40" font-size="10" fill="#242424">Alert</text><text x="150" y="54" font-size="9" fill="{m}">Caregiver</text></svg>'
    if kind == 'child':
        hatch = ''.join(f'<line x1="{x}" y1="68" x2="{x + 50}" y2="8" stroke="{c}" stroke-opacity=".3" stroke-width="3"/>' for x in range(90, 230, 12))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><defs><clipPath id="khc"><rect x="120" y="8" width="96" height="60" rx="6"/></clipPath></defs><g clip-path="url(#khc)">{hatch}</g><rect x="120" y="8" width="96" height="60" rx="6" fill="none" stroke="{c}" stroke-dasharray="5 4" stroke-width="2"/><text x="168" y="44" text-anchor="middle" font-size="10" font-weight="600" fill="#242424">Pool gate</text><rect x="8" y="8" width="96" height="60" rx="6" fill="{t}" fill-opacity=".15" stroke="{t}" stroke-width="2"/><text x="56" y="62" text-anchor="middle" font-size="9" fill="{m}">Safe zone</text><circle cx="86" cy="30" r="6" fill="{b}"/><rect x="81" y="37" width="10" height="13" rx="4" fill="{b}"/><path d="M96 40h18" stroke="{c}" stroke-width="2" marker-end=""/></svg>'
    if kind == 'pet':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="100" y="10" width="112" height="22" rx="4" fill="{ash}"/><text x="156" y="25" text-anchor="middle" font-size="9" fill="{m}">Kitchen counter</text><rect x="96" y="6" width="120" height="30" rx="6" fill="none" stroke="{c}" stroke-dasharray="5 4" stroke-width="2"/><g fill="#7a5a3a"><ellipse cx="60" cy="50" rx="22" ry="12"/><circle cx="84" cy="40" r="9"/><path d="M80 32l2-8 5 7zM88 32l4-7 1 8z"/><rect x="42" y="56" width="5" height="12" rx="2"/><rect x="70" y="56" width="5" height="12" rx="2"/></g><text x="10" y="18" font-size="10" font-weight="600" fill="#242424">Pet · near zone</text></svg>'
    if kind == 'drive':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><path d="M60 0H160L190 72H30Z" fill="{ash}"/><rect x="88" y="16" width="44" height="46" rx="10" fill="{m}"/><rect x="94" y="22" width="32" height="10" rx="3" fill="#2b2d30"/><rect x="84" y="12" width="52" height="54" fill="none" stroke="{t}" stroke-width="1.5"/><circle cx="168" cy="40" r="6" fill="{c}"/><rect x="163" y="47" width="10" height="13" rx="4" fill="{c}"/><rect x="156" y="30" width="24" height="34" fill="none" stroke="{c}" stroke-width="1.5"/></svg>'
    if kind == 'alerts':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="46" y="2" width="128" height="68" rx="12" fill="#101114"/><rect x="54" y="12" width="112" height="24" rx="6" fill="#26282e"/><circle cx="64" cy="24" r="5" fill="{c}"/><text x="74" y="22" font-size="8" font-weight="600" fill="#fff">KenHome · Front door</text><text x="74" y="31" font-size="7" fill="#b9bbc8">Person at door · 14:31</text><rect x="54" y="40" width="54" height="22" rx="4" fill="#3a3c44"/><text x="81" y="54" text-anchor="middle" font-size="7" fill="#fff">View clip</text><rect x="112" y="40" width="54" height="22" rx="4" fill="#3a3c44"/><text x="139" y="54" text-anchor="middle" font-size="7" fill="#fff">Dismiss</text></svg>'
    if kind == 'grid':
        cells = ''.join(f'<rect x="{8 + (i % 4) * 44}" y="{6 + (i // 4) * 32}" width="40" height="28" rx="4" fill="#2b2d33"/>' for i in range(8))
        dots = f'<circle cx="44" cy="12" r="3" fill="{c}"/><circle cx="132" cy="44" r="3" fill="{c}"/>'
        rows = ''.join(f'<rect x="190" y="{6 + i * 20}" width="170" height="16" rx="8" fill="#fff"/><circle cx="202" cy="{14 + i * 20}" r="4" fill="{col}"/><text x="212" y="{17 + i * 20}" font-size="9" fill="#242424">{txt}</text>' for i, (txt, col) in enumerate([('Front door · person at door', c), ('Living room · all OK', t), ('Driveway · vehicle parked', t)]))
        return f'<svg viewBox="0 0 370 72" aria-hidden="true">{cells}{dots}{rows}</svg>'
    raise ValueError(kind)


def kh_types_chart():
    rows = [('Person at entrance', 9), ('Driveway activity', 6), ('Pet in restricted zone', 4), ('Child near restricted zone', 2), ('Unusual inactivity', 1), ('Possible fall', 1)]
    W, rowh, lab = 360, 30, 150
    out = [f'<svg class="chart" viewBox="0 0 {W} {rowh * len(rows) + 6}" role="img" aria-label="Home alerts this week by type">']
    for i, (n, v) in enumerate(rows):
        y = i * rowh + 6
        out.append(f'<text x="0" y="{y + 13}" fill="#c9cbd6" font-size="11">{n}</text><rect x="{lab}" y="{y + 3}" width="{W - lab - 34}" height="14" rx="3" fill="#24262d"/>')
        out.append(f'<rect x="{lab}" y="{y + 3}" width="{max(v / 9 * (W - lab - 34), 3):.1f}" height="14" rx="3" fill="#5b7cff" data-tip="{n} · {v} this week"/><text x="{W}" y="{y + 14}" text-anchor="end" fill="#e9e9ec" font-size="11" font-weight="600">{v}</text>')
    out.append('</svg>')
    return ''.join(out)


KH_FAQ = [
    ('What is KenHome?', "KenHome is Intelense's AI-powered home security and monitoring solution. It uses compatible camera feeds to help identify configured security and safety events involving property access, elderly monitoring, children, pets and vehicles."),
    ('How is KenHome different from a regular home security camera?', 'A traditional security camera primarily records footage and may provide basic motion notifications. KenHome adds AI-powered event analysis to help identify selected activities and provide more context about what may need attention.'),
    ('Can KenHome work with my existing security cameras?', 'KenHome is designed to work with compatible existing cameras, including supported indoor, outdoor and driveway setups. The exact compatibility depends on the camera model, video stream and deployment configuration.'),
    ('Can KenHome detect falls in elderly people?', 'KenHome supports camera-based fall monitoring in compatible setups. Detection depends on camera placement, visibility and configuration. Alerts should supplement regular care arrangements and must not be treated as a replacement for emergency response or medical monitoring.'),
    ('Can KenHome help keep children safe at home?', 'KenHome can monitor configured zones and flag supported events, such as entry into a designated restricted area. It provides an additional layer of awareness, not a guarantee that every unsafe situation will be detected.'),
    ('Can I use KenHome to monitor my pets?', 'Yes, supported pet-monitoring features can help you review activity in camera-covered areas and receive configured alerts for selected events or restricted-zone entry.'),
    ('Can KenHome monitor my driveway and parked car?', 'KenHome supports driveway and vehicle monitoring through compatible cameras and configured detection capabilities. Available alerts depend on the setup and events the system is configured to recognise.'),
    ('How quickly does KenHome send alerts?', 'Alert speed depends on the event type, deployment configuration, network connectivity and notification channel. Contact Intelense for the expected performance of your proposed setup.'),
    ('Does KenHome use facial recognition?', "KenHome's published configuration describes zone-based rules and behaviour patterns rather than facial recognition for distinguishing expected activity from potential threats. Confirm the exact configuration and privacy settings with Intelense before deployment."),
    ('Can multiple family members receive alerts?', 'KenHome supports configurable family access according to the published product information. Available permissions, notification channels and access controls depend on the deployed configuration.'),
    ('Does KenHome replace a professional security system or caregiver?', 'No. KenHome is intended to support home security and family awareness. It does not replace professional security arrangements, direct supervision, caregiving or emergency services.'),
    ('How much does KenHome cost?', "Pricing depends on factors such as the number of cameras, monitored zones, required features and deployment configuration. Contact Intelense for a quote based on your home's needs."),
    ('How can I get started with KenHome?', 'Book a demo with Intelense. Share your home layout, existing camera setup and monitoring priorities so the team can help you understand the suitable configuration.'),
]



KH_HERO = dict(
    uid='kh', logo='kenhome', site='Home · Front door camera',
    aria='Front door camera flagging a person at the door and a package on the step',
    media='<div class="tile-solo"><canvas class="cctv" data-scene="porch" width="960" height="540"></canvas></div>',
    kpis=[('cam', 'Cameras online', '4 / 4', 'All OK', 'pos', 'connected', None),
          ('bell', 'Alerts today', '3', '1 to review', 'neg', '', [1, 0, 2, 1, 0, 1, 3, 1, 2, 1, 2, 3])],
    alert=('Person at door', 'neg', 'users', '<b>Front door</b> · someone is at the door and a package is on the step.', '14:31'))


def kh_dash():
    cams = ('<div class="ap-cams"><figure><div class="tile-solo"><canvas class="cctv" data-scene="porch" width="640" height="360"></canvas></div><figcaption>Front door ' + ap.pill('Person', 'neg') + '</figcaption></figure>'
            '<figure><div class="tile-solo"><canvas class="cctv" data-scene="living" width="480" height="270"></canvas></div><figcaption>Living room ' + ap.pill('All OK', 'pos') + '</figcaption></figure>'
            '<figure><div class="tile-solo"><canvas class="cctv" data-scene="drive" width="480" height="270"></canvas></div><figcaption>Driveway ' + ap.pill('Vehicle', 'info') + '</figcaption></figure></div>')
    main = ap.card('Cameras', cams, action='4 online')
    side = ap.feed([('users', 'neg', '<b>Person at front door</b> · notified 3 people', '14:31'),
                    ('box', 'info', '<b>Package</b> left on the front step', '14:32'),
                    ('fall', 'pos', '<b>Living room</b> · no falls or inactivity today', '12:00'),
                    ('car', 'violet', '<b>Person near vehicle</b> at night · driveway', '02:14'),
                    ('fence', 'warn', '<b>Back garden</b> boundary zone paused', 'Mon')], title="Today's events")
    evs = ap.events([('Person', 'neg', 'users', 'Front door', '14:31', 'Person at the door, family notified'),
                     ('Package', 'info', 'box', 'Front door', '14:32', 'Package left on the step'),
                     ('Night', 'violet', 'moon', 'Driveway', '02:14', 'Person near the vehicle'),
                     ('Wellbeing', 'pos', 'fall', 'Living room', 'All OK', 'No falls or inactivity today')])
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    zones = [('Front door', 'Entrance', 'Alerts', 'neg', None, 'Alert', 'neg'), ('Pool gate', 'Child restricted zone', 'Children', 'violet', None, 'Active', 'pos'),
             ('Kitchen counter', 'Pet restricted zone', 'Pets', 'info', None, 'Active', 'pos'), ('Back garden', 'Boundary', 'Night', 'mute', None, 'Paused', 'warn')]
    bottom = [ap.tasks(zones, 'Monitored zones', '6 zones'),
              ap.card('Alerts this week', ap.bar_chart(days, [2, 1, 4, 2, 3, 6, 3], 5, lambda v: f'{v} alerts', 'kh'), sub='Saturday was busiest')]
    return dict(uid='kh', logo='kenhome', alt='KenHome', me='AC', nav=['home', 'cam', 'bell', 'zone', 'users', 'cog'],
                hello='Good afternoon, welcome home', sub='4 cameras · 6 zones · 3 family members notified', range='Today',
                aria='KenHome dashboard with live cameras, today\'s alerts, monitored zones and alerts by day',
                kpis=[('cam', 'Cameras online', '4 / 4', 'All OK', 'pos', 'connected', None),
                      ('bell', 'Alerts today', '3', '1 to review', 'neg', '', [1, 0, 2, 1, 0, 1, 3, 1, 2, 1, 2, 3]),
                      ('zone', 'Zones monitored', '6', '1 paused', 'warn', 'back garden', None),
                      ('users', 'Family notified', '3', 'Push · SMS', 'info', 'people', None)],
                main=main, side=side, events=evs, bottom=bottom)


def page_kenhome():
    m = MOD['kenhome']
    hero = f'''<section class="page-hero kv-hero" style="--mod:{m["color"]}">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap kv-hero-grid">
      <div class="kv-hero-copy">
        {crumbs(('modules.html', 'Modules'), (None, 'KenHome'))}
        <span class="eyebrow">AI-powered home monitoring by Intelense</span>
        {logo_img(m, 0.36, 'hero-logo')}
        <h1>Your Home, Always Protected. Even When You Can't Be There.</h1>
        <p class="lede">KenHome turns compatible existing home cameras into an intelligent monitoring system that helps you keep an eye on what matters most.</p>
        <p class="lede kv-sub">From unexpected visitors and suspicious activity to elderly fall detection, child safety and pet monitoring, KenHome helps you stay informed when something needs your attention.</p>
        <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">Book a Free Demo</a><a class="btn btn-ghost" href="#features">Explore Features</a></div>
        <p class="kv-tagline">AI home security and safety monitoring for families, homes and residential properties.</p>
      </div>
      <div class="kv-hero-visual">
        {ap.hero(KH_HERO)}
        <p class="demo-note">Simulated camera feed and example alerts</p>
      </div>
    </div>
  </section>'''

    problem = f'''<section class="block" id="problem">
    <div class="wrap">
      {head_block('The problem', "Your Cameras Record What Happens. But Who's Watching?", "You may already have cameras at your front door, in your living room or across your driveway. But when you're at work, travelling or asleep, reviewing every camera feed isn't practical.")}
      <div class="kv-problem">
        <div class="kv-questions">
          <p class="kv-q">A family member could fall.</p>
          <p class="kv-q">A child could enter an unsafe area.</p>
          <p class="kv-q">An unfamiliar person could linger near your property.</p>
          <p class="kv-q">Your pet could get into trouble.</p>
          <p class="kv-answer">KenHome uses AI-powered video monitoring to help identify selected events and notify you when something may need attention.</p>
        </div>
        <ul class="kv-points">
          <li>{icon('users')}<div><b>Worried about elderly parents at home?</b><span>Receive alerts for supported fall events or unusual inactivity.</span></div></li>
          <li>{icon('zone')}<div><b>Want to keep children safer?</b><span>Set up designated safe and restricted zones to help monitor activity.</span></div></li>
          <li>{icon('paw')}<div><b>Concerned about your pets?</b><span>Monitor their activity and receive alerts for configured events or restricted-area entry.</span></div></li>
          <li>{icon('patrol')}<div><b>Want better home security?</b><span>Get notified about suspicious activity, unauthorised entry or unexpected movement in monitored areas.</span></div></li>
          <li>{icon('car')}<div><b>Park your car outside?</b><span>Monitor your driveway and receive alerts for supported vehicle-access or suspicious-activity events.</span></div></li>
        </ul>
      </div>
    </div>
  </section>'''

    feats = [
        ('intrusion', 'AI Home Security &amp; Intrusion Detection', 'Know when something unusual happens around your home.', 'Monitor camera-covered entrances, outdoor areas and property boundaries. KenHome can identify configured intrusion events, restricted-area entry and suspicious activity, helping you investigate potential security concerns.'),
        ('fall', 'Elderly Monitoring &amp; Fall Detection', 'Extra peace of mind for the people you care about.', 'Use compatible cameras to monitor designated living areas and identify supported fall events or unusual inactivity. Alerts can help family members or designated caregivers check on a loved one when something may be wrong.'),
        ('child', 'Child Safety Monitoring', 'Keep an eye on the areas that matter most.', 'Define safe and restricted zones around your home. KenHome can alert you when configured activity, such as a child entering a restricted area, is detected by compatible cameras.'),
        ('pet', 'AI Pet Monitoring', 'Know what your pets are getting into.', "Monitor designated areas and receive alerts for supported activity, restricted-zone entry or potential hazards. Stay informed about your pet's activity even when you're not in the same room."),
        ('drive', 'Driveway &amp; Vehicle Security', "Keep an eye on your vehicle, even when you're indoors.", "Monitor your driveway and parking areas for unexpected vehicle access, suspicious activity and supported tampering-related events. Receive alerts so you can review what's happening around your vehicle."),
        ('alerts', 'Real-Time Alerts &amp; Video Evidence', 'Get the context you need when an alert arrives.', 'Receive notifications for configured events through supported alert channels. Review available timestamps, camera details and video clips to better understand what triggered the alert.'),
    ]
    cards = ''.join(f'<article class="kv-feat"><div class="kv-mini">{kh_mini(k)}</div><span class="kv-num">{i + 1:02d}</span><h3>{t}</h3><p class="kv-strap">{s}</p><p>{d}</p></article>' for i, (k, t, s, d) in enumerate(feats))
    cards += f'<article class="kv-feat kv-feat-wide"><div class="kv-mini" style="background:#16171b">{kh_mini("grid")}</div><div><span class="kv-num">07</span><h3>One View for Your Home</h3><p class="kv-strap">Keep your cameras and important alerts in one place.</p><p>Review activity across supported cameras and monitored zones through a central dashboard. Help family members and designated caregivers stay informed without manually checking every feed.</p></div></article>'
    features = f'''<section class="block" id="features">
    <div class="wrap">
      {head_block('Features', 'One Smarter Way to Monitor Your Home', 'KenHome brings AI home security and safety monitoring into one solution, helping families keep track of important activity across camera-covered areas.')}
      <div class="kv-feats">{cards}</div>
    </div>
  </section>'''

    steps = [('Connect Your Existing Cameras', 'Integrate compatible indoor, outdoor, doorbell or driveway cameras with KenHome. Reuse your current setup where supported, subject to camera compatibility and deployment requirements.'),
             ('Set Up Your Monitoring Zones', 'Choose the areas you want to monitor, such as entrances, living spaces, driveways or designated restricted zones. Configure the events and alerts relevant to your household.'),
             ('Let AI Monitor for Selected Events', 'KenHome analyses supported camera feeds to identify configured events, such as potential falls, unusual inactivity, restricted-zone entry and suspicious activity.'),
             ('Receive Alerts When Something Needs Attention', 'When a configured event is detected, KenHome can notify designated family members or caregivers through supported channels. Review the available event information and decide what action is needed.')]
    how = f'''<section class="block" id="how">
    <div class="wrap">
      {head_block('How it works', 'From Your Existing Cameras to Smarter Home Monitoring', 'KenHome adds AI-powered monitoring to compatible cameras, helping you identify selected events without having to watch every screen yourself.')}
      <ol class="kv-steps four">{''.join(f'<li><span>{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(steps))}</ol>
      <p style="margin-top:36px"><a class="btn btn-black" href="#example">See KenHome in Action</a></p>
    </div>
  </section>'''

    who = [('users', 'Families with Children', 'Monitor selected areas, establish restricted zones and receive alerts when configured safety events occur.'),
           ('home', 'Families Caring for Elderly Parents', 'Get additional visibility into selected living spaces and receive alerts for supported fall events or unusual inactivity, helping you check in when needed.'),
           ('paw', 'Pet Owners', 'Monitor pet activity in camera-covered areas and receive notifications for supported events or entry into designated restricted zones.'),
           ('patrol', 'Homeowners', 'Monitor entrances, property boundaries and outdoor areas to identify unexpected activity and potential security concerns.'),
           ('car', 'Vehicle Owners', 'Keep track of activity around driveways and parking areas through compatible cameras and configured alerts.'),
           ('route', 'Families Who Travel Frequently', "Stay informed about selected activity around your property while you're away, subject to your camera setup, connectivity and monitoring configuration.")]
    whos = f'''<section class="block" id="who">
    <div class="wrap">
      {head_block("Who it's for", 'Smart Home Monitoring for the People and Places You Care About', '')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in who)}</div>
      <p style="margin-top:28px"><a class="link-arrow" href="industries.html#residential">More on residential</a></p>
    </div>
  </section>'''

    example = f'''<section class="block" id="example">
    <div class="wrap kv-split" style="align-items:start">
      <div>
        <span class="eyebrow">Real-world example</span>
        <h2 style="margin-top:18px">You Can't Be Everywhere at Once. Your Home Monitoring Can Be Smarter.</h2>
        <p class="lede" style="margin-top:20px">Imagine you're at work while an elderly parent is home alone.</p>
        <p class="kv-body">You can't keep checking a live camera feed throughout the day. But you still want to know if something happens that requires your attention.</p>
        <p class="kv-body">With KenHome, compatible cameras can monitor designated living areas for supported events, such as a potential fall or unusual inactivity.</p>
        <p class="kv-body">If a configured event is detected, the system can notify a designated family member or caregiver, who can check the available video context and decide what to do next.</p>
        <p class="kv-body">The same approach can help you monitor restricted areas for children, activity around pets or unexpected movement near your driveway.</p>
        <p class="kv-body"><b style="color:var(--off-black);font-weight:600">Instead of constantly checking cameras, receive relevant alerts when configured events need your attention.</b></p>
      </div>
      <div class="kh-example">
        <div class="tile-solo" role="img" aria-label="Living room camera: a person walks across the room, then a possible fall and inactivity alert appears">
          <canvas class="cctv" data-scene="living" width="960" height="540"></canvas>
        </div>
        <div class="kh-row">
        <div class="kh-phone" aria-label="Example phone notification">
          <div class="kh-notch"></div>
          <p class="kh-time">10:42</p>
          <div class="kh-note">
            <div class="kh-note-top"><img src="assets/logos/kenhome-light.png" alt="" width="58" height="22"><span>now</span></div>
            <b>Possible fall · Living room</b>
            <p>No movement for 2 minutes after a possible fall. Tap to view the clip.</p>
            <div class="kh-acts"><span class="pri">View clip</span><span>Call Mum</span></div>
          </div>
          <div class="kh-note dim"><b>Driveway · vehicle parked</b><p>No activity since 08:15.</p></div>
        </div>
        <ol class="ks-timeline" style="margin:0">
          <li><time>10:40:12</time><div><b>Possible fall detected</b><span>Living room camera</span></div><em class="bad">Alert</em></li>
          <li><time>10:42:12</time><div><b>No movement for 2 minutes</b><span>Caregiver and family notified</span></div><em class="bad">Alert</em></li>
          <li><time>10:43:05</time><div><b>Family member reviews clip</b><span>Calls to check in</span></div><em>Action</em></li>
        </ol>
        </div>
        <p class="demo-note">Simulated camera feed and example notification</p>
      </div>
    </div>
  </section>'''

    why = [('plug', 'Make More of Your Existing Cameras', 'Use compatible cameras you already have instead of necessarily replacing your entire home monitoring setup.'),
           ('bell', 'Get Alerts Instead of Watching Every Feed', 'Automate supported event detection and reduce the need to continuously check live camera footage.'),
           ('layers', 'Monitor More Than Intruders', 'Go beyond traditional home security with supported monitoring for elderly family members, children, pets and vehicles.'),
           ('users', 'Keep Family Members Informed', 'Configure supported notifications for designated family members or caregivers so the right people can respond when needed.'),
           ('clock', 'Review Events with Context', 'Use available timestamps and video evidence to understand what triggered an alert and decide on the appropriate response.'),
           ('zone', 'Configure Monitoring Around Your Home', "Set up supported cameras, zones and event rules according to your household's needs and deployment capabilities.")]
    benefits = f'''<section class="block" id="why">
    <div class="wrap">
      {head_block('Why KenHome?', 'More Than Home Security. More Awareness of Everyday Life.', '')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in why)}</div>
    </div>
  </section>'''

    zones = [('Front door', 'Entrance', 'Alert', 'bad'), ('Living room', 'Fall and inactivity', 'Active', ''), ('Pool gate', 'Child restricted zone', 'Active', ''), ('Kitchen counter', 'Pet restricted zone', 'Active', ''), ('Driveway', 'Vehicle and night activity', 'Active', ''), ('Back garden', 'Boundary', 'Paused', 'warn')]
    dash = f'''<section class="block" id="dashboard">
    <div class="wrap">
      {head_block('Dashboard', 'Your Home at a Glance. Important Alerts in One Place.', 'Bring your supported camera feeds, monitored zones and safety events into one view.')}
      {ap.dash(kh_dash())}
      <p class="demo-note">Example dashboard with simulated feeds and data. Not a real home.</p>
      <p class="kv-body" style="max-width:62ch">Review notifications, understand where an event occurred and access available video context without having to search through hours of recordings.</p>
      <p class="kv-body" style="max-width:62ch">KenHome helps make home monitoring more useful, more organised and easier to manage.</p>
      <p style="margin-top:28px"><a class="btn btn-blue" href="contact.html">Request a KenHome Demo</a></p>
    </div>
  </section>'''

    final = final_cta('More Peace of Mind for the People Who Matter Most.',
                      ['From home security and driveway monitoring to elderly, child and pet safety, KenHome helps you stay informed about important events at home.',
                       'Make your existing cameras more useful with AI-powered monitoring and alerts.'],
                      'Book a Free Demo',
                      "Tell us about your home, your existing cameras and what you want to monitor. We'll help you explore the right KenHome setup.",
                      'KenHome by Intelense | Intelligence at the Edge.')

    body = '\n\n  '.join([hero, problem, features, how, whos, example, benefits, dash, faq_block(KH_FAQ), related_block(m), final, faq_schema(KH_FAQ)])
    return dict(file='kenhome.html', title='KenHome: AI Home Security & Smart Monitoring | Intelense',
                desc='KenHome turns compatible home cameras into AI-powered monitoring for home security, elderly fall detection, child safety, pets and driveways, with real-time alerts.',
                active='kenhome', body=body, cctv=True)


# ---------------------------------------------------------------- KenIoT page

def ki_mini(kind):
    b, m, c, ash, t, v = '#0A34ED', '#6C6E82', '#FF7953', '#e4e2dc', '#73C4C5', '#7C28E9'
    if kind == 'realtime':
        vals = [('Temp', '71°C'), ('Vibration', '4.2'), ('Pressure', '6.1 bar'), ('Power', '18 kW')]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<rect x="{(i % 2) * 112}" y="{(i // 2) * 37}" width="106" height="32" rx="8" fill="#fff"/><circle cx="{(i % 2) * 112 + 12}" cy="{(i // 2) * 37 + 16}" r="4" fill="{c if i == 1 else t}"/><text x="{(i % 2) * 112 + 22}" y="{(i // 2) * 37 + 14}" font-size="8" fill="{m}">{n}</text><text x="{(i % 2) * 112 + 22}" y="{(i // 2) * 37 + 26}" font-size="11" font-weight="600" fill="#242424">{val}</text>' for i, (n, val) in enumerate(vals)) + '</svg>'
    if kind == 'anomaly':
        import math
        pts = ' '.join(f'{x},{36 - 6 * math.sin(x / 9) - (22 if 140 < x < 170 else 0) * math.sin((x - 140) / 30 * math.pi)}' for x in range(0, 221, 5))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="0" y="24" width="220" height="24" fill="{t}" fill-opacity=".18"/><polyline points="{pts}" fill="none" stroke="{b}" stroke-width="2"/><circle cx="155" cy="16" r="12" fill="none" stroke="{c}" stroke-width="2"/><text x="172" y="66" font-size="9" fill="{m}">Anomaly</text></svg>'
    if kind == 'predict':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><line x1="0" y1="56" x2="220" y2="56" stroke="{c}" stroke-dasharray="4 3"/><text x="2" y="68" font-size="8" fill="{m}">Failure threshold</text><path d="M0 14 C60 16 100 20 130 28" fill="none" stroke="{b}" stroke-width="2"/><path d="M130 28 C160 36 180 46 200 56" fill="none" stroke="{b}" stroke-width="2" stroke-dasharray="4 3"/><circle cx="130" cy="28" r="4" fill="{b}"/><text x="140" y="20" font-size="10" font-weight="600" fill="#242424">~9 days</text><text x="140" y="32" font-size="8" fill="{m}">to threshold</text></svg>'
    if kind == 'health':
        rows = [('Motor M-14', .62, c), ('Pump P-03', .86, t), ('Compressor C-3', .91, t)]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<text x="0" y="{i * 24 + 14}" font-size="10" fill="{m}">{n}</text><rect x="92" y="{i * 24 + 5}" width="100" height="10" rx="5" fill="{ash}"/><rect x="92" y="{i * 24 + 5}" width="{100 * p:.0f}" height="10" rx="5" fill="{col}"/><text x="220" y="{i * 24 + 14}" text-anchor="end" font-size="10" font-weight="600" fill="#242424">{int(p * 100)}</text>' for i, (n, p, col) in enumerate(rows)) + '</svg>'
    if kind == 'alerts':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="10" y="6" width="200" height="40" rx="10" fill="#101114"/><circle cx="28" cy="26" r="6" fill="{c}"/><text x="42" y="22" font-size="9" font-weight="600" fill="#fff">Vibration above range</text><text x="42" y="35" font-size="8" fill="#b9bbc8">Motor M-14 · Line 2 · 09:42</text><rect x="30" y="52" width="160" height="16" rx="8" fill="#fff"/><text x="110" y="63" text-anchor="middle" font-size="8" fill="{m}">Threshold 4.0 mm/s · rule active</text></svg>'
    if kind == 'integrate':
        nodes = ''.join(f'<rect x="0" y="{4 + i * 23}" width="60" height="18" rx="9" fill="#fff" stroke="{ash}"/><text x="30" y="{16 + i * 23}" text-anchor="middle" font-size="8" fill="#242424">{n}</text><path d="M60 {13 + i * 23} C80 {13 + i * 23} 80 36 98 36" fill="none" stroke="{t}" stroke-width="1.5"/>' for i, n in enumerate(['Sensors', 'PLCs', 'Meters']))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true">{nodes}<rect x="98" y="24" width="50" height="24" rx="6" fill="{m}"/><text x="123" y="40" text-anchor="middle" font-size="8" fill="#fff">Gateway</text><path d="M148 36H168" stroke="{t}" stroke-width="1.5"/><rect x="168" y="22" width="52" height="28" rx="8" fill="{v}"/><text x="194" y="40" text-anchor="middle" font-size="9" font-weight="600" fill="#fff">KenIoT</text></svg>'
    if kind == 'workflow':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="0" y="22" width="62" height="28" rx="8" fill="#ffe9e2"/><text x="31" y="40" text-anchor="middle" font-size="9" font-weight="600" fill="#9a3412">Anomaly</text><path d="M62 36H84" stroke="{m}" stroke-width="1.5"/><path d="M80 32l5 4-5 4" fill="none" stroke="{m}" stroke-width="1.5"/><rect x="86" y="6" width="134" height="60" rx="8" fill="#fff" stroke="{ash}"/><text x="96" y="22" font-size="9" font-weight="600" fill="#242424">Work order WO-1042</text><text x="96" y="36" font-size="8" fill="{m}">Inspect bearing, motor M-14</text><rect x="96" y="44" width="52" height="14" rx="7" fill="#e6f4f4"/><text x="122" y="54" text-anchor="middle" font-size="8" fill="#1e5f60">Assigned</text></svg>'
    if kind == 'trends':
        import math
        pts = ' '.join(f'{x},{50 - x * .12 - 5 * math.sin(x / 11)}' for x in range(0, 221, 5))
        marks = ''.join(f'<circle cx="{x}" cy="{50 - x * .12 - 5 * math.sin(x / 11):.1f}" r="4" fill="{c}"/>' for x in (60, 150, 205))
        gl = ''.join(f'<line x1="{x}" y1="4" x2="{x}" y2="66" stroke="{ash}"/>' for x in (55, 110, 165))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true">{gl}<polyline points="{pts}" fill="none" stroke="{b}" stroke-width="2"/>{marks}<text x="2" y="70" font-size="8" fill="{m}">12 weeks · 3 recurring anomalies</text></svg>'
    raise ValueError(kind)


def ki_example_chart():
    import math
    weeks = 10
    n = weeks * 7
    vals = []
    for d in range(n):
        base = 2.3 + .15 * math.sin(d * .9) + .08 * math.sin(d * 2.3)
        if d > 38:
            base += (d - 38) * .045
        vals.append(round(base, 2))
    W, H, ml, mb, mt = 640, 240, 40, 30, 16
    pw, ph = W - ml - 10, H - mb - mt
    lo, hi = 1.5, 4.5
    X = lambda i: ml + i * pw / (n - 1)
    Y = lambda v: mt + ph - (v - lo) / (hi - lo) * ph
    alert_i = next(i for i, v in enumerate(vals) if v > 3.0)
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Motor vibration over ten weeks: steady inside the normal range until week six, then rising until an alert at {vals[alert_i]} mm/s triggers an inspection.">']
    for gv in (2, 3, 4):
        out.append(f'<line x1="{ml}" x2="{W - 10}" y1="{Y(gv):.1f}" y2="{Y(gv):.1f}" stroke="#e4e2dc"/><text x="{ml - 8}" y="{Y(gv) + 3:.1f}" text-anchor="end" fill="#6C6E82" font-size="10">{gv}</text>')
    out.append(f'<rect x="{ml}" y="{Y(2.8):.1f}" width="{pw}" height="{Y(1.9) - Y(2.8):.1f}" fill="#73C4C5" fill-opacity=".16"/><text x="{ml + 8}" y="{Y(2.8) + 14:.1f}" fill="#1e5f60" font-size="10" font-weight="600">Normal operating range</text>')
    out.append(f'<line x1="{ml}" x2="{W - 10}" y1="{Y(3.0):.1f}" y2="{Y(3.0):.1f}" stroke="#FF7953" stroke-dasharray="5 4"/><text x="{ml + 8}" y="{Y(3.0) - 6:.1f}" fill="#9a3412" font-size="10" font-weight="600">Alert threshold 3.0 mm/s</text>')
    pts_ok = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals[:alert_i + 1]))
    pts_bad = ' '.join(f'{X(i):.1f},{Y(v):.1f}' for i, v in enumerate(vals) if i >= alert_i)
    out.append(f'<polyline points="{pts_ok}" fill="none" stroke="#0A34ED" stroke-width="2" stroke-linejoin="round"/><polyline points="{pts_bad}" fill="none" stroke="#FF7953" stroke-width="2" stroke-linejoin="round"/>')
    for i in range(0, n, 7):
        out.append(f'<circle cx="{X(i):.1f}" cy="{Y(vals[i]):.1f}" r="7" fill="transparent" data-tip="Week {i // 7 + 1} · {vals[i]} mm/s"/>')
    drift_i = 39
    for i, lab, col in ((drift_i, 'Drift begins', '#6C6E82'), (alert_i, 'Alert sent', '#FF7953')):
        out.append(f'<line x1="{X(i):.1f}" x2="{X(i):.1f}" y1="{mt}" y2="{mt + ph}" stroke="{col}" stroke-opacity=".6"/><circle cx="{X(i):.1f}" cy="{Y(vals[i]):.1f}" r="5" fill="{col}" stroke="#fff" stroke-width="2"/><text x="{X(i) - 6:.1f}" y="{mt + 10}" text-anchor="end" fill="{col}" font-size="10" font-weight="600">{lab}</text>')
    for w in range(weeks):
        out.append(f'<text x="{X(w * 7 + 3):.1f}" y="{H - 10}" text-anchor="middle" fill="#6C6E82" font-size="10">Wk {w + 1}</text>')
    out.append(f'<text x="{ml}" y="{mt - 4}" fill="#6C6E82" font-size="10">mm/s</text></svg>')
    return ''.join(out)


KI_FAQ = [
    ('What is an IoT monitoring platform?', 'An IoT monitoring platform connects to compatible devices and sensors to collect, display and analyse data. It helps businesses monitor operating conditions, identify unusual readings and understand how connected equipment is performing.'),
    ('What is KenIoT?', "KenIoT is Intelense's IoT and sensor intelligence solution. It brings together data from compatible sensors and industrial systems to support real-time monitoring, anomaly detection and predictive maintenance."),
    ('What is predictive maintenance?', 'Predictive maintenance uses equipment data and condition indicators to identify signs of potential failure. It helps maintenance teams investigate problems and plan servicing based on equipment condition rather than relying only on fixed schedules or waiting for a breakdown.'),
    ('How does AI anomaly detection work?', 'AI anomaly detection learns or uses expected operating patterns and compares them with incoming sensor data. When readings deviate from those patterns, the system can flag the change for investigation. Not every anomaly indicates a fault, so alerts may require human review.'),
    ('What types of sensors can KenIoT monitor?', 'Depending on supported integrations, KenIoT can work with sensors that measure variables such as temperature, vibration, pressure, humidity, soil moisture and electrical current. The exact range depends on the devices and communication protocols supported by the deployment.'),
    ('Can KenIoT work with existing industrial equipment?', 'KenIoT is designed to integrate with compatible existing sensors and industrial systems. For older equipment without digital outputs, additional retrofit sensors or gateways may be required.'),
    ('How does KenIoT help reduce equipment downtime?', 'KenIoT can identify unusual sensor patterns that may indicate developing equipment issues. This gives teams an opportunity to investigate and plan maintenance earlier. Actual downtime reduction depends on the equipment, data quality, detection performance and maintenance response.'),
    ('Does KenIoT automatically create maintenance tickets?', 'Maintenance tickets or work orders can be created through supported integrations and configured workflows. Availability depends on the maintenance management system and deployment setup.'),
    ('Can KenIoT monitor multiple sites?', 'KenIoT is designed to support connected asset monitoring across different operational environments. Multi-site visibility, user permissions and reporting capabilities depend on the deployed configuration.'),
    ('How long does KenIoT take to identify potential equipment failures?', 'The time required to identify an anomaly or predict a potential failure varies by equipment type, failure mode, sensor availability and historical data quality. Some abnormal readings may be identified quickly, while reliable failure prediction may require a longer learning period and sufficient operating data.'),
    ('How can I get started with KenIoT?', 'Book a demo with Intelense. Share your equipment types, existing sensors, communication protocols and maintenance challenges so the team can help you explore a suitable IoT monitoring setup.'),
]



KI_HERO = dict(
    uid='ki', logo='keniot', site='Plant 1 · Line 2 · Motor M-14',
    aria='Live sensor monitor for motor M-14 on line 2: vibration streams against its expected range and is flagged when it drifts outside it',
    media='<div class="ap-ch" style="margin:4px 6px 8px"><h4>Vibration · mm/s</h4><span class="ap-act">Expected range shaded</span></div><div class="ki-stream"><canvas data-iotstream="dark" width="720" height="250"></canvas><span class="ki-status" data-iotstatus>Within expected range</span></div>',
    kpis=[('pulse', 'Vibration', '4.2', '↗ 18%', 'neg', 'mm/s since 06:00', [2.2, 2.3, 2.2, 2.4, 2.6, 2.8, 3.1, 3.4, 3.7, 3.9, 4.1, 4.2]),
          ('gauge', 'Asset health', '93%', '119 / 128', 'pos', 'healthy', [90, 91, 91, 92, 92, 91, 92, 93, 92, 93, 93, 93])],
    alert=('Anomaly', 'neg', 'wrench', '<b>Motor M-14</b> bearing vibration is rising. Work order WO-1042 created.', '14:30'))


def ki_dash():
    hours = [f'{h:02d}:00' for h in range(0, 24, 2)] + ['Now']
    vals = [2.2, 2.3, 2.2, 2.4, 2.3, 2.6, 2.9, 3.2, 3.5, 3.8, 4.0, 4.1, 4.2]
    exp = [2.4] * 13
    main = ap.main('Motor M-14 · vibration, last 24 hours', '4.2 mm/s', '↗ 18%', 'neg', 'above the expected 2.4', [('Vibration', False), ('Expected', True)],
                   ap.line_chart(hours, vals, 12, 'Now · 4.2 mm/s', 'ki', (0, 1.5, 3, 4.5, 6), exp, every=2))
    side = ap.feed([('pulse', 'neg', '<b>Motor M-14</b> vibration above expected range', '14:30'),
                    ('wrench', 'violet', '<b>WO-1042</b> created · inspect bearing', '14:31'),
                    ('thermo', 'warn', '<b>Freezer F-1</b> temperature drifting up', '13:05'),
                    ('check', 'pos', '<b>HVAC unit 4</b> filter replaced · back to normal', '10:20'),
                    ('doc', 'mute', '<b>Weekly asset report</b> sent', '08:00')], title='Anomalies')
    evs = ap.events([('Vibration', 'neg', 'pulse', 'Motor M-14', '4.2 mm/s', 'Above expected 2.4'),
                     ('Temperature', 'warn', 'thermo', 'Freezer F-1', '-14 °C', 'Check the door seal'),
                     ('Power', 'violet', 'bolt', 'Line 2 drive', '18.4 kW', 'Up 9% on last week'),
                     ('Healthy', 'pos', 'check', 'Line 1', '42 / 42', 'All assets normal')])
    wos = [('WO-1042', 'Inspect bearing · Motor M-14', 'High', 'neg', 30, 'Assigned', 'info'), ('WO-1039', 'Check door seal · Freezer F-1', 'Medium', 'warn', 10, 'Scheduled', 'warn'),
           ('WO-1031', 'Replace filter · HVAC unit 4', 'Low', 'mute', 100, 'Done', 'pos')]
    bottom = [ap.tasks(wos, 'Maintenance queue', '3 open this week'),
              ap.card('Fleet health', '<div class="ap-rings">' + ap.ring(93, '93%', 'Healthy assets', 'ki1') + ap.ring(99, '99.2%', 'Sensor uptime', 'ki2') + '</div>'
                      '<div class="ap-split" style="margin-top:14px"><div class="ap-stat"><span>Assets</span><b>128</b></div><div class="ap-stat"><span>Sensors</span><b>412</b></div></div>')]
    return dict(uid='ki', logo='keniot', alt='KenIoT', me='MT', nav=['pulse', 'gauge', 'wrench', 'bell', 'doc', 'cog'],
                hello='Good afternoon, Maintenance team', sub='Plant 1 · Markham · 128 assets · 412 sensors', range='Last 24 hours',
                aria='KenIoT dashboard with asset health, a vibration anomaly on motor M-14, recent anomalies and the maintenance queue',
                kpis=[('layers', 'Assets monitored', '128', '412 sensors', 'info', '', [120, 121, 121, 122, 124, 124, 125, 126, 126, 127, 128, 128]),
                      ('check', 'Healthy', '119', '93%', 'pos', 'of assets', [116, 117, 118, 117, 118, 119, 118, 119, 120, 119, 119, 119]),
                      ('alert', 'Open anomalies', '4', '1 rising', 'neg', 'fast', [2, 2, 3, 2, 3, 3, 2, 3, 4, 3, 4, 4]),
                      ('wrench', 'Work orders', '3', 'This week', 'info', 'created from alerts', None)],
                main=main, side=side, events=evs, bottom=bottom)


def page_keniot():
    m = MOD['keniot']
    gauges = [('Temperature', '71', '°C', 'Normal', '', [66, 67, 66, 68, 67, 69, 68, 70, 69, 71, 70, 71]),
              ('Vibration', '4.2', 'mm/s', 'Rising', 'warn', [2.2, 2.3, 2.2, 2.4, 2.6, 2.8, 3.1, 3.4, 3.7, 3.9, 4.1, 4.2]),
              ('Pressure', '6.1', 'bar', 'Normal', '', [6.0, 6.1, 6.0, 6.2, 6.1, 6.0, 6.1, 6.2, 6.1, 6.0, 6.1, 6.1]),
              ('Power', '18.4', 'kW', 'Watch', 'warn', [16.8, 17.0, 16.9, 17.2, 17.4, 17.3, 17.7, 17.9, 18.0, 18.2, 18.3, 18.4])]
    gauge_html = ''.join(f'<div class="sensor{" warn" if cls else ""}"><div class="lbl"><span>{n}</span></div><div class="val">{v} <small>{u}</small></div>{sparkline(series, "#FF7953" if cls else "#73C4C5")}</div>' for n, v, u, st, cls, series in gauges)
    hero = f'''<section class="page-hero kv-hero" style="--mod:{m["color"]}">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap kv-hero-grid">
      <div class="kv-hero-copy">
        {crumbs(('modules.html', 'Modules'), (None, 'KenIoT'))}
        <span class="eyebrow">Intelligent sensor analytics by Intelense</span>
        {logo_img(m, 0.36, 'hero-logo')}
        <h1>Know When Something Is Wrong Before It Becomes a Bigger Problem.</h1>
        <p class="lede">KenIoT turns data from connected sensors and equipment into useful operational insights. Monitor equipment health, detect unusual behaviour and identify potential failures before they lead to unexpected downtime.</p>
        <p class="lede kv-sub">Whether you manage a factory, railway system, fleet or agricultural operation, KenIoT helps you understand what's happening across your connected assets and make better-informed maintenance decisions.</p>
        <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">Book a Free Demo</a><a class="btn btn-ghost" href="#features">Explore Features</a></div>
        <p class="kv-tagline">AI-powered IoT monitoring, sensor analytics and predictive maintenance for industrial operations.</p>
      </div>
      <div class="kv-hero-visual">
        {ap.hero(KI_HERO)}
        <p class="demo-note">Simulated sensor data</p>
      </div>
    </div>
  </section>'''

    problem = f'''<section class="block" id="problem">
    <div class="wrap">
      {head_block('The problem', 'Your Equipment Gives You Signals. Are You Catching Them?', "Machines rarely go from working perfectly to failing without any warning signs. Changes in temperature, vibration, pressure or power consumption can indicate that something isn't operating as expected.")}
      <div class="kv-problem">
        <div class="kv-questions">
          <p class="kv-answer" style="font-size:17px;color:#e9e6e3">But when sensor data is spread across different systems, identifying these changes and understanding what they mean can be difficult.</p>
          <p class="kv-q" style="border:0;padding:0;margin-top:8px">KenIoT brings sensor intelligence together to help your team spot unusual patterns and investigate potential problems earlier.</p>
        </div>
        <ul class="kv-points">
          <li>{icon('wrench')}<div><b>Unexpected equipment breakdowns?</b><span>Monitor equipment behaviour and identify patterns that may indicate a developing fault.</span></div></li>
          <li>{icon('layers')}<div><b>Too much data, not enough clarity?</b><span>Bring sensor readings together to understand how connected assets are performing.</span></div></li>
          <li>{icon('clock')}<div><b>Maintenance always happening after something goes wrong?</b><span>Use predictive maintenance insights to help plan inspections and servicing before a potential failure.</span></div></li>
          <li>{icon('route')}<div><b>Problems difficult to spot across multiple sites?</b><span>Monitor connected assets through a centralised view of available sensor data.</span></div></li>
          <li>{icon('bolt')}<div><b>Unnecessary maintenance and operating costs?</b><span>Use equipment health information to help prioritise maintenance based on actual operating conditions.</span></div></li>
        </ul>
      </div>
    </div>
  </section>'''

    feats = [
        ('realtime', 'Real-Time IoT Monitoring', "Know what's happening across your connected assets.", 'Collect and monitor data from compatible sensors and industrial systems. Track available readings such as temperature, vibration, pressure, humidity and power consumption to understand operating conditions as they change.'),
        ('anomaly', 'AI-Powered Anomaly Detection', 'Spot unusual behaviour before it becomes a bigger concern.', 'KenIoT analyses sensor readings to identify patterns that differ from expected equipment behaviour. Detect unusual changes, investigate potential issues and help your team respond before a small problem develops into a major disruption.'),
        ('predict', 'Predictive Maintenance', 'Move from fixing breakdowns to planning ahead.', 'Use equipment data, historical patterns and anomaly detection to identify signs of potential equipment failure. Help maintenance teams prioritise inspections, plan servicing and reduce dependence on reactive repairs.'),
        ('health', 'Equipment Health Monitoring', 'Understand how your assets are performing.', 'Monitor equipment conditions through available sensor data and asset-specific indicators. Compare current readings with expected operating patterns to help identify equipment that may need inspection or maintenance.'),
        ('alerts', 'Smart Alerts &amp; Notifications', 'Know when a reading needs your attention.', 'Configure alerts for supported anomalies, operating thresholds and equipment conditions. Help the relevant team investigate unusual readings without continuously checking every sensor dashboard.'),
        ('integrate', 'Sensor Data Integration', 'Bring different data sources into one view.', 'Connect compatible sensors, industrial equipment and monitoring systems through supported communication protocols and integrations. Build a more complete picture of your operations without necessarily replacing existing equipment.'),
        ('workflow', 'Automated Maintenance Workflows', 'Turn potential problems into planned action.', 'Use detected anomalies and configured rules to support maintenance workflows, including work-order or maintenance-ticket creation where integrated. Help teams document issues, assign follow-ups and track corrective action.'),
        ('trends', 'Historical Trends &amp; Reporting', "Understand what's changing over time.", 'Review historical sensor readings, equipment behaviour and detected anomalies. Use trends and reports to investigate recurring issues, understand operating patterns and support maintenance planning.'),
    ]
    features = f'''<section class="block" id="features">
    <div class="wrap">
      {head_block('Features', 'Turn Sensor Data into Decisions That Keep Operations Moving.', 'KenIoT combines IoT connectivity, AI-powered sensor analytics and predictive maintenance capabilities to help you understand the condition of your equipment and infrastructure.')}
      <div class="kv-feats four">{''.join(f'<article class="kv-feat"><div class="kv-mini">{ki_mini(k)}</div><span class="kv-num">{i + 1:02d}</span><h3>{t}</h3><p class="kv-strap">{s}</p><p>{d}</p></article>' for i, (k, t, s, d) in enumerate(feats))}</div>
    </div>
  </section>'''

    steps = [('Connect Your Sensors &amp; Systems', 'Integrate compatible sensors, industrial equipment and existing monitoring systems. Support for specific devices and communication protocols depends on your infrastructure and deployment requirements.'),
             ('Learn Normal Operating Behaviour', 'KenIoT analyses available sensor readings and operating history to establish expected behaviour for monitored assets. The initial learning period and baseline quality depend on the available data and equipment conditions.'),
             ('Detect Anomalies &amp; Potential Risks', 'AI models compare incoming readings with expected patterns and configured conditions. When unusual behaviour is identified, the system can flag the issue for investigation.'),
             ('Take Action Before Downtime Escalates', 'Review alerts, investigate potential faults and use supported maintenance integrations to plan the next steps. Your team can make informed decisions about inspections, repairs and equipment servicing.')]
    how = f'''<section class="block" id="how">
    <div class="wrap">
      {head_block('How it works', 'From Connected Sensors to Predictive Insights', 'KenIoT turns incoming equipment data into information your team can use.')}
      <ol class="kv-steps four">{''.join(f'<li><span>{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(steps))}</ol>
      <p style="margin-top:36px"><a class="btn btn-black" href="#example">See KenIoT in Action</a></p>
    </div>
  </section>'''

    inds = [('wrench', 'Manufacturing &amp; Industrial Facilities', 'Monitor machine temperature, vibration, pressure and other available readings. Identify unusual operating patterns and support predictive maintenance across production equipment.', 'industrial'),
            ('route', 'Railways &amp; Transportation Infrastructure', 'Monitor compatible railway equipment, signalling systems and infrastructure sensors. Identify unusual readings that may require inspection and help maintenance teams prioritise potential issues.', 'smart-cities'),
            ('leaf', 'Agriculture &amp; Smart Irrigation', 'Connect compatible soil moisture, weather and irrigation sensors to understand field conditions. Use sensor insights to support irrigation planning and identify abnormal equipment or system behaviour.', 'agriculture'),
            ('car', 'Fleet &amp; Transportation', 'Monitor available vehicle health data, including engine-related readings and other connected sensor information. Identify unusual operating patterns and support proactive vehicle maintenance.', 'smart-cities'),
            ('plug', 'Healthcare Facilities', 'Monitor connected facility systems and compatible equipment sensors. Track available environmental or operational readings and alert relevant teams when configured conditions require attention.', 'healthcare'),
            ('bolt', 'Energy &amp; Critical Infrastructure', 'Monitor compatible equipment and environmental sensors across connected infrastructure. Identify unusual readings and support maintenance planning for critical assets.', 'smart-cities')]
    industries = f'''<section class="block" id="industries">
    <div class="wrap">
      {head_block('Industry applications', 'One IoT Intelligence Platform. Multiple Industrial Applications.', 'Different industries rely on different types of equipment, sensors and operating conditions. KenIoT helps teams monitor connected assets and understand changes that may affect performance.')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p><a class="kv-link" href="industries.html#{a}">More on {IND[a]["name"].lower()} →</a></div>' for ic, t, d, a in inds)}</div>
    </div>
  </section>'''

    example = f'''<section class="block" id="example">
    <div class="wrap">
      <div class="kv-split" style="align-items:start">
        <div>
          <span class="eyebrow">Real-world example</span>
          <h2 style="margin-top:18px">A Machine Doesn't Have to Break Down Before You Notice a Problem.</h2>
          <p class="lede" style="margin-top:20px">Imagine a motor running continuously on a factory production line.</p>
          <p class="kv-body">For weeks, it operates within its normal temperature and vibration ranges. Then its vibration readings begin changing, even though the machine is still running.</p>
          <p class="kv-body">Without continuous monitoring, the change may go unnoticed until the motor overheats, production slows or the equipment fails.</p>
        </div>
        <div>
          <p class="kv-body" style="margin-top:0">With KenIoT, sensor data can be analysed against the motor's expected operating behaviour. An unusual pattern can trigger an alert, giving the maintenance team a reason to inspect the equipment.</p>
          <p class="kv-body">The team can investigate the cause and decide whether maintenance is needed before the problem escalates.</p>
          <p class="kv-body"><b style="color:var(--off-black);font-weight:600">The goal isn't to predict every breakdown perfectly. It's to identify meaningful warning signs earlier and give your team more time to act.</b></p>
        </div>
      </div>
      <div class="panel" style="margin-top:32px"><h3 style="font-size:16px;margin-bottom:12px">Motor M-14 · vibration over 10 weeks</h3>{ki_example_chart()}</div>
      <ol class="ks-timeline ki-steps">
        <li><time>Weeks 1 to 5</time><div><b>Normal operation</b><span>Vibration stays inside the learned operating range.</span></div><em>Normal</em></li>
        <li><time>Week 6</time><div><b>Readings start to drift</b><span>KenIoT notes a sustained change from expected behaviour.</span></div><em class="bad">Watch</em></li>
        <li><time>Week 8</time><div><b>Alert sent to maintenance</b><span>Vibration crosses the configured threshold; a work order is raised.</span></div><em class="bad">Alert</em></li>
        <li><time>Week 8</time><div><b>Inspection planned</b><span>The team checks the motor during the next scheduled stop.</span></div><em>Action</em></li>
      </ol>
      <p class="demo-note">Illustrative example and data</p>
    </div>
  </section>'''

    why = [('plug', 'Make Better Use of Existing Equipment', 'Integrate compatible sensors and industrial systems instead of necessarily replacing your entire infrastructure.'),
           ('search', 'Identify Problems Earlier', 'Use AI-powered anomaly detection to highlight unusual equipment behaviour that may otherwise go unnoticed.'),
           ('clock', 'Reduce Unplanned Downtime', 'Use early warning signals to help plan inspections and maintenance before potential faults disrupt operations.'),
           ('chart', 'Prioritise Maintenance Efforts', 'Use equipment health indicators and detected anomalies to help teams decide which assets need attention first.'),
           ('layers', 'Monitor Assets from One Place', 'Bring available sensor data, alerts and equipment information into a central monitoring view.'),
           ('timeline', 'Make Decisions with Historical Context', 'Review trends and past anomalies to understand recurring issues and support longer-term maintenance planning.')]
    benefits = f'''<section class="block" id="why">
    <div class="wrap">
      {head_block('Why KenIoT?', 'Less Reactive Maintenance. More Control Over Your Operations.', '')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in why)}</div>
    </div>
  </section>'''

    assets = [('Motor M-14', 'Line 2', 62, 'Anomaly', 'bad'), ('Freezer F-1', 'Cold store', 74, 'Watch', 'warn'), ('Pump P-03', 'Line 1', 86, 'Healthy', ''), ('Compressor C-3', 'Utilities', 91, 'Healthy', ''), ('Conveyor B', 'Packing', 88, 'Healthy', ''), ('HVAC unit 4', 'Building A', 93, 'Healthy', '')]
    asset_rows = ''.join(f'<tr><td><b>{a}</b><br><small>{site}</small></td><td><span class="ki-bar"><i style="width:{h}%;background:{"#FF7953" if cls == "bad" else "#f2d28a" if cls == "warn" else "#73C4C5"}"></i></span> {h}</td><td><span class="st {cls}">{st}</span></td></tr>' for a, site, h, st, cls in assets)
    sens = [('Bearing temp', '68', '°C', [61, 62, 61, 63, 62, 64, 63, 65, 64, 66, 67, 68], True), ('Humidity', '44', '%', [44, 43, 45, 44, 42, 43, 44, 45, 43, 44, 44, 43], False), ('Current', '31', 'A', [30, 31, 30, 31, 32, 31, 30, 31, 31, 32, 31, 31], False), ('Line pressure', '6.1', 'bar', [6.0, 6.1, 6.0, 6.2, 6.1, 6.0, 6.1, 6.2, 6.1, 6.0, 6.1, 6.1], False)]
    sens_html = ''.join(f'<div class="sensor{" warn" if w else ""}"><div class="lbl"><span>{n}</span><span class="tag">{"Watch" if w else "Normal"}</span></div><div class="val">{v} <small>{u}</small></div>{sparkline(s, "#FF7953" if w else "#73C4C5")}</div>' for n, v, u, s, w in sens)
    wos = [('WO-1042', 'Inspect bearing · Motor M-14', 'Assigned', 'bad'), ('WO-1039', 'Check door seal · Freezer F-1', 'Scheduled', 'warn'), ('WO-1031', 'Replace filter · HVAC unit 4', 'Done', '')]
    dash = f'''<section class="block" id="dashboard">
    <div class="wrap">
      {head_block('Dashboard', 'Every Sensor Has a Signal. See What It Means.', 'Bring your connected equipment and sensor information into one view.')}
      {ap.dash(ki_dash())}
      <p class="demo-note">Example dashboard with simulated data. Not a real site.</p>
      <p class="kv-body" style="max-width:62ch">Monitor available readings, review unusual patterns, track equipment health indicators and investigate alerts across your connected assets.</p>
      <p class="kv-body" style="max-width:62ch">KenIoT helps your team move beyond isolated sensor readings to a clearer understanding of what's happening across your operations.</p>
      <p style="margin-top:28px"><a class="btn btn-blue" href="contact.html">Request a KenIoT Demo</a></p>
    </div>
  </section>'''

    final = final_cta('Connect Your Sensors. Understand Your Operations. Plan Ahead.',
                      ['From real-time sensor monitoring to AI-powered anomaly detection and predictive maintenance, KenIoT helps you turn equipment data into actionable operational insights.',
                       'Give your team a clearer view of asset health and more opportunities to address potential problems before they lead to unexpected downtime.'],
                      'Book a Free Demo',
                      "Tell us about your equipment, existing sensors and operational challenges. We'll help you explore how KenIoT can fit your infrastructure.",
                      'KenIoT by Intelense | Intelligence at the Edge.')

    body = '\n\n  '.join([hero, problem, features, how, industries, example, benefits, dash, faq_block(KI_FAQ), related_block(m), final, faq_schema(KI_FAQ)])
    return dict(file='keniot.html', title='KenIoT: AI-Powered IoT Monitoring & Predictive Maintenance | Intelense',
                desc='KenIoT turns data from connected sensors and equipment into real-time monitoring, AI anomaly detection and predictive maintenance insights.',
                active='keniot', body=body)


# ---------------------------------------------------------------- KenVoice page (retail conversation intelligence)

def kc_mini(kind):
    b, m, c, ash, t, v = '#0A34ED', '#6C6E82', '#FF7953', '#e4e2dc', '#73C4C5', '#5466DD'
    if kind == 'greeting':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="0" y="10" width="140" height="22" rx="11" fill="{t}" fill-opacity=".2"/><text x="10" y="25" font-size="10" fill="#242424">Staff: "Hi, welcome in!"</text><circle cx="180" cy="34" r="26" fill="none" stroke="{ash}" stroke-width="5"/><circle cx="180" cy="34" r="26" fill="none" stroke="{t}" stroke-width="5" stroke-dasharray="40 164" transform="rotate(-90 180 34)"/><text x="180" y="38" text-anchor="middle" font-size="12" font-weight="600" fill="#242424">4s</text><text x="0" y="56" font-size="10" font-weight="600" fill="#1e5f60">Greeted</text><text x="0" y="68" font-size="9" fill="{m}">time to first greeting</text></svg>'
    if kind == 'upsell':
        rows = [('Screen protector', True), ('Charging cable', True), ('Extended warranty', False)]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<rect x="0" y="{i * 24 + 2}" width="220" height="20" rx="10" fill="{"#e6f4f4" if ok else "#ffe9e2"}"/><text x="12" y="{i * 24 + 16}" font-size="10" fill="#242424">{n}</text><text x="210" y="{i * 24 + 16}" text-anchor="end" font-size="9" font-weight="600" fill="{"#1e5f60" if ok else "#9a3412"}">{"Offered" if ok else "Missed"}</text>' for i, (n, ok) in enumerate(rows)) + '</svg>'
    if kind == 'walkaway':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="10" y="8" width="44" height="60" rx="3" fill="none" stroke="{m}" stroke-width="2"/><circle cx="46" cy="40" r="2.5" fill="{m}"/><circle cx="92" cy="22" r="7" fill="{c}"/><path d="M92 30v18M92 36l-10 8M92 36l10 4M92 48l-8 16M92 48l8 16" stroke="{c}" stroke-width="3" stroke-linecap="round"/><path d="M70 40H58" stroke="{c}" stroke-width="2"/><path d="M62 36l-5 4 5 4" fill="none" stroke="{c}" stroke-width="2"/><text x="118" y="34" font-size="10" font-weight="600" fill="#242424">Walk-away</text><text x="118" y="48" font-size="9" fill="{m}">No purchase · 14:12</text></svg>'
    if kind == 'sentiment':
        segs = [('Positive', .62, t), ('Neutral', .26, '#b8b8c0'), ('Negative', .12, c)]
        x, out = 0, []
        for n, p_, col in segs:
            out.append(f'<rect x="{x:.0f}" y="12" width="{220 * p_ - 2:.0f}" height="18" rx="4" fill="{col}"/>')
            x += 220 * p_
        lab = ''.join(f'<circle cx="{4 + i * 70}" cy="52" r="4" fill="{col}"/><text x="{11 + i * 70}" y="56" font-size="8.5" fill="#242424">{n} {int(p_ * 100)}%</text>' for i, (n, p_, col) in enumerate(segs))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true">{"".join(out)}{lab}</svg>'
    if kind == 'score':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><circle cx="34" cy="36" r="28" fill="none" stroke="{ash}" stroke-width="6"/><circle cx="34" cy="36" r="28" fill="none" stroke="{b}" stroke-width="6" stroke-dasharray="{176 * .86:.0f} 176" transform="rotate(-90 34 36)"/><text x="34" y="41" text-anchor="middle" font-size="15" font-weight="600" fill="#242424">86</text><rect x="74" y="8" width="146" height="56" rx="8" fill="#fff"/><text x="84" y="24" font-size="9" fill="{m}">Evidence</text><text x="84" y="38" font-size="9" fill="#242424">"Would you like a screen</text><text x="84" y="50" font-size="9" fill="#242424">protector as well?"</text></svg>'
    if kind == 'scorecard':
        rows = [('Chloe M.', 91), ('Aisha K.', 88), ('Daniel R.', 68)]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<text x="0" y="{i * 24 + 14}" font-size="10" fill="#242424">{n}</text><rect x="64" y="{i * 24 + 5}" width="126" height="10" rx="5" fill="{ash}"/><rect x="64" y="{i * 24 + 5}" width="{126 * s / 100:.0f}" height="10" rx="5" fill="{c if s < 75 else v}"/><text x="220" y="{i * 24 + 14}" text-anchor="end" font-size="10" font-weight="600" fill="#242424">{s}</text>' for i, (n, s) in enumerate(rows)) + '</svg>'
    raise ValueError(kind)


def kc_privacy_diagram():
    return '''<svg class="plan" viewBox="0 0 640 250" role="img" aria-label="Audio is processed on the counter tablet and discarded. Only text transcripts and structured insights sync to the cloud dashboard, which uses role-based access, audit logs and configurable retention.">
  <rect x="10" y="20" width="270" height="200" rx="18" fill="#101114"/>
  <text x="30" y="50" font-size="12" font-weight="600" fill="#e9e9ec">Counter tablet</text>
  <text x="30" y="68" font-size="10" fill="#9b9daf">On-device processing</text>
  <g font-size="10" fill="#e9e9ec">
    <rect x="30" y="86" width="230" height="30" rx="8" fill="#1d1f24"/><text x="44" y="105">Audio in</text>
    <rect x="30" y="124" width="230" height="30" rx="8" fill="#1d1f24"/><text x="44" y="143">Speech to text · voices separated</text>
    <rect x="30" y="162" width="230" height="30" rx="8" fill="#3d2620"/><text x="44" y="181" fill="#ffb39b">Audio discarded after processing</text>
  </g>
  <path d="M280 120 H360" stroke="#5466DD" stroke-width="2.5"/><path d="M352 113l10 7-10 7" fill="none" stroke="#5466DD" stroke-width="2.5"/>
  <text x="320" y="106" text-anchor="middle" font-size="10" font-weight="600" fill="#242424">Text and</text>
  <text x="320" y="144" text-anchor="middle" font-size="10" font-weight="600" fill="#242424">insights only</text>
  <rect x="360" y="20" width="270" height="200" rx="18" fill="#ffffff" stroke="#d8d8dc"/>
  <text x="380" y="50" font-size="12" font-weight="600" fill="#242424">Cloud dashboard</text>
  <text x="380" y="68" font-size="10" fill="#6C6E82">Transcripts and structured insights</text>
  <g font-size="10" fill="#242424">
    <rect x="380" y="86" width="230" height="30" rx="8" fill="#f5f5f5"/><text x="394" y="105">Role-based permissions</text>
    <rect x="380" y="124" width="230" height="30" rx="8" fill="#f5f5f5"/><text x="394" y="143">Audit logs</text>
    <rect x="380" y="162" width="230" height="30" rx="8" fill="#f5f5f5"/><text x="394" y="181">Configurable transcript retention</text>
  </g>
</svg>'''


def kc_sentiment_chart():
    days = [('Mon', 64, 26, 10), ('Tue', 68, 24, 8), ('Wed', 61, 27, 12), ('Thu', 70, 22, 8), ('Fri', 66, 23, 11), ('Sat', 58, 26, 16), ('Sun', 72, 20, 8)]
    cols = (('Positive', '#73C4C5'), ('Neutral', '#6b6e7a'), ('Negative', '#FF7953'))
    W, H, ml, mb = 560, 190, 40, 44
    ph = H - mb - 8
    bw = (W - ml) / len(days)
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="Customer sentiment share by day, mostly positive, with the most negative conversations on Saturday">']
    for gv in (0, 50, 100):
        y = 8 + ph - gv / 100 * ph
        out.append(f'<text x="{ml - 6}" y="{y + 3:.1f}" text-anchor="end" fill="#9b9daf" font-size="10">{gv}%</text>')
    for i, (d, *vals) in enumerate(days):
        x, y = ml + i * bw + 6, 8 + ph
        for (name, col), v in zip(cols, vals):
            h = v / 100 * ph
            y -= h
            out.append(f'<rect x="{x:.1f}" y="{y + 1:.1f}" width="{bw - 12:.1f}" height="{max(h - 2, 1):.1f}" rx="3" fill="{col}" data-tip="{d} · {name} {v}%"/>')
        out.append(f'<text x="{x + (bw - 12) / 2:.1f}" y="{8 + ph + 16}" text-anchor="middle" fill="#9b9daf" font-size="10">{d}</text>')
    out.append(''.join(f'<circle cx="{ml + i * 100 + 6}" cy="{H - 8}" r="5" fill="{col}"/><text x="{ml + i * 100 + 16}" y="{H - 4}" fill="#c9cbd6" font-size="11">{n}</text>' for i, (n, col) in enumerate(cols)))
    out.append('</svg>')
    return ''.join(out)


KC_FAQ = [
    ('What is KenVoice?', 'KenVoice is an AI audio analytics platform for physical retail stores. It analyses customer and staff conversations to identify service patterns, sales opportunities, and coaching insights.'),
    ('How is KenVoice different from call-centre analytics?', 'Call-centre tools typically analyse phone calls or digital meetings. KenVoice is designed for face-to-face conversations at retail counters, using a tablet-based setup and retail-specific analytics.'),
    ('Does KenVoice record and store customer audio?', 'KenVoice processes audio on the device and discards it after processing. Text transcripts and insights may be synced to the cloud according to the configured system and retention settings.'),
    ('Do we need to change our POS or phone system?', 'KenVoice is designed to operate from a tablet placed at the counter, without requiring phone-system integration. Confirm any deployment-specific requirements with the Intelense team.'),
    ('How does KenVoice identify staff and customer speech?', 'Its speech-processing workflow separates staff and customer voices to help structure conversations and generate interaction insights. Identification and configuration depend on the deployment.'),
    ('Can KenVoice help improve staff performance?', 'KenVoice provides conversation tags, scores, transcripts, and staff scorecards that managers can use to identify coaching opportunities and review service patterns.'),
    ('Can KenVoice be used across multiple stores?', 'The platform describes dashboards for retail teams and management. Ask the Intelense team about the multi-store setup, permissions, and reporting options for your requirements.'),
]



def kc_hero(lines, ins, bars):
    media = f'''<div class="kc-tablet" data-convo role="img" aria-label="Counter tablet showing a live staff and customer conversation with insights: greeting detected in 4 seconds, upsell offered, positive sentiment, conversation score 86">
          <div class="wave kc-wave">{bars}</div>
          <div class="kc-body">
            <ul class="kc-lines">{lines}</ul>
            <ul class="kc-ins"><li class="kc-ins-h">Live insights</li>{ins}</ul>
          </div>
        </div>'''
    return dict(uid='kc', logo='kenvoice', site='Store 014 · Counter 2 · on-device', media=media,
                kpis=[('users', 'Customers greeted', '91%', '↗ 3 pts', 'pos', 'vs last week', [84, 85, 87, 86, 88, 87, 89, 88, 90, 89, 90, 91]),
                      ('cart', 'Upsell offered', '38%', '14 missed', 'neg', 'today', [34, 36, 35, 37, 36, 38, 37, 39, 37, 38, 37, 38])],
                alert=('Score 86', 'pos', 'mic', '<b>Counter 2</b> · greeted in 4s, upsell offered, sale with add-on.', '14:32'))


def kc_dash():
    hours = [f'{h:02d}:00' for h in range(9, 21)]
    vals = [6, 12, 18, 22, 27, 24, 16, 14, 20, 24, 18, 13]
    prev = [5, 10, 15, 20, 23, 22, 15, 13, 18, 21, 16, 12]
    main = ap.main('Conversations by hour', '214', '↗ 9%', 'pos', 'conversations today', [('Today', False), ('Last week', True)],
                   ap.line_chart(hours, vals, 4, '13:00 · 27 conversations', 'kc', (0, 10, 20, 30, 40), prev, every=2))
    side = ap.feed([('mic', 'pos', '<b>Counter 2</b> · upsell offered, sale with add-on · 86', '14:32'),
                    ('mic', 'neg', '<b>Counter 1</b> · walk-away, not greeted · 52', '14:20'),
                    ('mic', 'info', '<b>Counter 3</b> · return handled, positive · 81', '14:11'),
                    ('star', 'violet', '<b>Coaching note</b> added for Daniel R.', '13:40'),
                    ('doc', 'mute', '<b>Weekly scorecards</b> ready to review', '09:00')], title='Recent conversations')
    evs = ap.events([('Greeting', 'pos', 'users', 'Greeted within 10s', '91%', 'Up 3 pts on last week'),
                     ('Missed upsell', 'neg', 'cart', 'Screen protector', '14', 'With a new phone today'),
                     ('Sentiment', 'info', 'star', 'Positive', '66%', '11% negative'),
                     ('Coaching', 'violet', 'doc', 'Staff to review', '2', 'Scores under 75 this week')])
    staff = [('Chloe M.', '41 conversations', 'Greeted 98%', 'pos', 91, 'On track', 'pos'), ('Aisha K.', '48 conversations', 'Greeted 96%', 'pos', 88, 'On track', 'pos'),
             ('Ben T.', '52 conversations', 'Upsell 31%', 'warn', 79, 'On track', 'pos'), ('Daniel R.', '37 conversations', 'Upsell 22%', 'neg', 68, 'Coach', 'neg')]
    bottom = [ap.tasks(staff, 'Staff scorecards', 'This week'),
              ap.card('Positive sentiment', ap.bar_chart(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], [61, 64, 62, 66, 68, 72, 66], 5, lambda v: f'{v}%', 'kc'), sub='Share of conversations, by day')]
    return dict(uid='kc', logo='kenvoice', alt='KenVoice', me='SM', nav=['mic', 'chart', 'users', 'star', 'doc', 'cog'],
                hello='Good afternoon, Store 014', sub='Downtown · 3 counters · audio processed on-device', range='Today',
                aria='KenVoice dashboard with conversations by hour, greeting and upsell rates, sentiment and staff scorecards',
                kpis=[('mic', 'Conversations', '214', '3 counters', 'info', 'today', [150, 162, 170, 168, 180, 176, 190, 186, 198, 204, 210, 214]),
                      ('users', 'Customers greeted', '91%', '↗ 3 pts', 'pos', 'vs last week', [84, 85, 87, 86, 88, 87, 89, 88, 90, 89, 90, 91]),
                      ('cart', 'Upsell offered', '38%', '14 missed', 'neg', 'accessory offers', [34, 36, 35, 37, 36, 38, 37, 39, 37, 38, 37, 38]),
                      ('star', 'Positive sentiment', '66%', '11% neg.', 'info', '', [60, 62, 61, 63, 64, 62, 65, 64, 66, 65, 67, 66])],
                main=main, side=side, events=evs, bottom=bottom)


def page_kenvoice():
    m = MOD['kenvoice']
    convo = [(1, 'staff', 'Hi there, welcome in! Anything I can help you find today?'),
             (2, 'cust', "I'm looking for a case for this phone."),
             (3, 'staff', 'These ones fit your model. Would you like a screen protector as well? It comes with a discount when you buy a case.'),
             (4, 'cust', 'Maybe. How much is it?'),
             (5, 'staff', 'It is a small add-on, and we can fit it for you right now.'),
             (6, 'cust', "Great, I'll take both.")]
    lines = ''.join(f'<li data-step="{n}" class="{who}"><b>{"Staff" if who == "staff" else "Customer"}</b><span>{txt}</span></li>' for n, who, txt in convo)
    insights = [(1, 'ok', 'Greeting', 'Detected · 4s'), (2, '', 'Customer need', 'Phone case'), (3, 'ok', 'Upsell offered', 'Screen protector'), (6, 'ok', 'Sentiment', 'Positive'), (6, 'ok', 'Outcome', 'Sale with add-on'), (7, 'score', 'Conversation score', '86 / 100')]
    ins = ''.join(f'<li data-step="{n}" class="{cls}"><span>{k}</span><b>{v}</b></li>' for n, cls, k, v in insights)
    bars = ''.join(f'<i style="--h:{round(10 + 26 * abs(math.sin(i * 0.7) * math.cos(i * 0.23)))}px;--d:-{(i % 9) * 0.13:.2f}s"></i>' for i in range(40))
    hero = f'''<section class="page-hero kv-hero" style="--mod:{m["color"]}">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap kv-hero-grid">
      <div class="kv-hero-copy">
        {crumbs(('modules.html', 'Modules'), (None, 'KenVoice'))}
        <span class="eyebrow">Retail conversation intelligence by Intelense <span class="tag-new" style="margin-left:6px">New</span></span>
        {logo_img(m, 0.36, 'hero-logo')}
        <h1>Know What Happens at the Counter.</h1>
        <p class="lede">KenVoice uses AI audio analytics to turn customer and staff conversations into insights that help retailers improve service, coach teams, and identify missed sales opportunities.</p>
        <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">Book a Free Demo</a><a class="btn btn-ghost" href="#how">See How It Works</a></div>
        <p class="kv-tagline">AI-powered conversation insights. Audio processed on-device.</p>
      </div>
      <div class="kv-hero-visual">
        {ap.hero(kc_hero(lines, ins, bars))}
        <p class="demo-note">Example conversation and insights</p>
      </div>
    </div>
  </section>'''

    caps = [('greeting', 'Greeting Detection', 'Understand whether customers are greeted and how quickly.'),
            ('upsell', 'Upsell and Cross-sell Tracking', 'Identify product recommendations, additional offers, and missed opportunities.'),
            ('walkaway', 'Walk-away Detection', 'Flag conversations where a customer leaves without completing a purchase, based on supported signals.'),
            ('sentiment', 'Customer Sentiment', 'Classify conversations as positive, neutral, or negative.'),
            ('score', 'Conversation Scoring', 'Review interaction quality through scores linked to conversation evidence.'),
            ('scorecard', 'Staff Scorecards', 'Compare performance patterns and identify coaching opportunities.')]
    what = f'''<section class="block" id="what">
    <div class="wrap">
      {head_block('What KenVoice does', 'Understand More Than What Your Customers Buy', "Sales reports show what customers purchased. They don't always show what happened during the conversation before a sale — or why a customer walked away.")}
      <div class="kv-split" style="margin-bottom:40px;align-items:start">
        <p class="kv-body" style="margin:0;font-size:17px">KenVoice analyses in-store conversations to help retailers understand how staff greet customers, recommend products, handle questions, and identify opportunities to upsell or cross-sell.</p>
        <p class="kv-body" style="margin:0;font-size:17px">With conversation insights and staff scorecards, managers can make coaching more specific and identify areas for improvement.</p>
      </div>
      <h3 class="kc-sub">Key capabilities</h3>
      <div class="kv-feats">{''.join(f'<article class="kv-feat"><div class="kv-mini">{kc_mini(k)}</div><span class="kv-num">{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></article>' for i, (k, t, d) in enumerate(caps))}</div>
    </div>
  </section>'''

    steps = [('Set Up at the Counter', 'Place a compatible tablet at the point of sale. KenVoice is designed for in-person retail conversations, without requiring headsets or phone-system integration.'),
             ('AI Analyses the Conversation', 'On-device AI processes speech, separates staff and customer voices, and converts the conversation into text and structured insights.'),
             ('Review Insights on Your Dashboard', 'Managers can review conversation tags, scores, staff performance, and potential missed sales opportunities through dashboards and reports.'),
             ('Coach with Context', 'Use conversation transcripts and interaction scores to give staff specific feedback, recognise effective selling behaviours, and improve customer service.')]
    how = f'''<section class="block" id="how">
    <div class="wrap">
      {head_block('How it works', 'From Conversation to Actionable Insights', '')}
      <ol class="kv-steps four">{''.join(f'<li><span>{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(steps))}</ol>
    </div>
  </section>'''

    bens = [('users', 'Improve Customer Service', 'Understand greeting quality, response patterns, and how consistently customers are being assisted.'),
            ('search', 'Identify Missed Sales Opportunities', 'Spot conversations where relevant product recommendations, upsells, or cross-sells may have been missed.'),
            ('text', 'Give Better Staff Feedback', 'Use conversation evidence to support more focused coaching instead of relying only on general observations.'),
            ('chart', 'See Patterns Across Your Store', 'Review conversation trends over time to understand recurring service issues and opportunities for improvement.'),
            ('layers', 'Support Consistent Retail Standards', 'Give store managers and regional teams a clearer view of how customer interactions are handled across their teams.')]
    benefits = f'''<section class="block" id="benefits">
    <div class="wrap">
      {head_block('Benefits', 'Make Every Customer Interaction More Informative', '')}
      <div class="kv-bens">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in bens)}</div>
    </div>
  </section>'''

    retail = [('tag', 'Fashion Retail', 'Review greetings, product recommendations, outfit pairing, and cross-selling opportunities.'),
              ('plug', 'Electronics Stores', 'Understand how staff explain product features, respond to budget concerns, and recommend suitable alternatives or accessories.'),
              ('eye', 'Jewellery Retail', 'Review customer engagement, product explanations, complementary recommendations, and service quality.'),
              ('patrol', 'Pharmacies', "Support consistent customer assistance and review how product-related questions are handled, subject to your store's privacy and compliance requirements."),
              ('box', 'Supermarkets and Department Stores', 'Understand service patterns at counters and identify opportunities to improve customer interactions.')]
    built = f'''<section class="block" id="retail">
    <div class="wrap">
      {head_block('Built for retail', 'Conversation Intelligence for In-Store Teams', '')}
      <div class="caps ag-caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in retail)}<div class="cap ag-more"><h3>Retail and commercial spaces</h3><p>Pair KenVoice with KenVision footfall, dwell time and queue analytics for a fuller view of the store.</p><a class="kv-link" href="kenvision.html">Explore KenVision →</a><a class="kv-link" href="industries.html#retail" style="padding-top:0">More on retail →</a></div></div>
    </div>
  </section>'''

    COACH = ' <span class="st warn">Coach</span>'
    staff = [('Chloe M.', 41, 98, 52, 91), ('Aisha K.', 48, 96, 44, 88), ('Emma S.', 36, 90, 40, 84), ('Ben T.', 52, 92, 31, 79), ('Daniel R.', 37, 81, 22, 68)]
    staff_rows = ''.join(f'<tr><td><b>{n}</b></td><td>{c}</td><td>{g}%</td><td>{u}%</td><td><span class="ki-bar"><i style="width:{s}%;background:{"#FF7953" if s < 75 else "#5466DD"}"></i></span> {s}{COACH if s < 75 else ""}</td></tr>' for n, c, g, u, s in staff)
    feed = [('14:31', 'Counter 2', 86, ['Greeted 4s', 'Upsell offered', 'Positive'], ''),
            ('14:12', 'Counter 1', 54, ['Not greeted', 'Walk-away', 'Negative'], 'bad'),
            ('13:58', 'Counter 2', 77, ['Greeted 9s', 'Accessory missed', 'Neutral'], 'warn'),
            ('13:40', 'Counter 3', 92, ['Greeted 3s', 'Cross-sell', 'Positive'], '')]
    feed_html = ''.join(f'<li class="{cls}"><div><b>{t} · {ctr}</b><div class="kc-tags">{"".join(f"<span>{x}</span>" for x in tags)}</div></div><em>{sc}</em></li>' for t, ctr, sc, tags, cls in feed)
    missed = [('Screen protector with a new phone', 14), ('Charging cable with headphones', 9), ('Extended warranty on laptops', 6), ('Case with a tablet', 4)]
    dash = f'''<section class="block" id="dashboard">
    <div class="wrap">
      <div class="kv-split" style="align-items:start;margin-bottom:40px">
        <div>
          <span class="eyebrow">Dashboards and scorecards</span>
          <h2 style="margin-top:18px">Turn Conversations into Clearer Coaching Decisions</h2>
          <p class="lede" style="margin-top:20px">KenVoice organises conversation insights so managers can review patterns without manually listening to every interaction.</p>
        </div>
        <div>
          <ul class="kc-list">
            <li>Conversation-level scores and tags</li><li>Staff performance scorecards</li><li>Greeting and response indicators</li>
            <li>Upsell and cross-sell opportunities</li><li>Customer sentiment classifications</li><li>Trends across selected time periods</li>
          </ul>
          <p class="kv-body">The result is a more structured way to review service quality, identify coaching needs, and understand what is happening during customer interactions.</p>
        </div>
      </div>
      {ap.dash(kc_dash())}
      <p class="demo-note">Example dashboard with illustrative data. Names are fictional.</p>
    </div>
  </section>'''

    privacy = f'''<section class="block" id="privacy">
    <div class="wrap">
      {head_block('Privacy', 'Conversation Intelligence with Privacy in Mind', 'KenVoice is designed to process audio on the device rather than upload raw recordings to the cloud.')}
      <div class="kv-split" style="align-items:center">
        <div>
          <ul class="kc-list kc-checks">
            <li>Audio is processed on the tablet and discarded after processing.</li>
            <li>Text transcripts and structured insights can be synced to the cloud.</li>
            <li>Staff voiceprints are encrypted and treated as biometric data.</li>
            <li>Access is controlled through role-based permissions and audit logs.</li>
            <li>Transcript retention can be configured.</li>
          </ul>
          <p class="kv-body kc-note">Retailers should establish appropriate staff and customer notices, consent processes, access policies, and retention settings for their deployment and applicable local requirements.</p>
        </div>
        <figure class="panel" style="margin:0">{kc_privacy_diagram()}</figure>
      </div>
    </div>
  </section>'''

    final = f'''<section class="cta">
    <div class="wash wash-b" aria-hidden="true" style="top:10%;right:20%"></div>
    <div class="wash wash-a" aria-hidden="true" style="top:30%;left:20%"></div>
    <div class="wrap">
      <span class="eyebrow">Get started</span>
      <h2 style="margin-top:20px">Hear What Your Store Has Been Missing</h2>
      <p class="lede" style="margin:18px auto 0">Understand the conversations behind customer experiences and sales outcomes.</p>
      <p class="lede" style="margin:12px auto 0">See how KenVoice can help your retail team identify missed opportunities, improve service quality, and coach with clearer evidence.</p>
      <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">Book a Free Demo</a></div>
      <p class="kv-sign">KenVoice by Intelense — AI-powered conversation intelligence for retail.</p>
    </div>
  </section>'''

    body = '\n\n  '.join([hero, what, how, benefits, built, dash, privacy, faq_block(KC_FAQ), related_block(m), final, faq_schema(KC_FAQ)])
    return dict(file='kenvoice.html', title='KenVoice: Retail Conversation Intelligence | Intelense',
                desc='KenVoice uses on-device AI audio analytics to turn customer and staff conversations at the counter into service, coaching and sales insights for retailers.',
                active='kenvoice', body=body)


# ---------------------------------------------------------------- KenRobotics page

def kr_mini(kind):
    b, m, c, ash, t, v = '#0A34ED', '#6C6E82', '#FF7953', '#e4e2dc', '#73C4C5', '#7C28E9'
    robot = lambda x, y, col=b: f'<circle cx="{x}" cy="{y}" r="9" fill="{col}"/><path d="M{x} {y}h9" stroke="#fff" stroke-width="2"/>'
    if kind == 'perception':
        import math, random
        rnd = random.Random(3)
        pts = ''.join(f'<circle cx="{110 + math.cos(a) * r:.1f}" cy="{36 + math.sin(a) * r * .55:.1f}" r="1.6" fill="{t}"/>' for a, r in ((i * .21, 30 + rnd.uniform(-3, 3) if i % 9 else 18) for i in range(30)))
        return f'<svg viewBox="0 0 220 72" aria-hidden="true">{pts}<rect x="126" y="24" width="14" height="12" rx="2" fill="none" stroke="{c}" stroke-width="2"/>{robot(110, 36)}<text x="0" y="14" font-size="9" fill="{m}">Sensor sweep</text><text x="150" y="20" font-size="9" fill="#9a3412">Obstacle</text></svg>'
    if kind == 'path':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><path d="M20 50H200" stroke="{ash}" stroke-width="3" stroke-dasharray="6 5"/><rect x="100" y="40" width="22" height="20" rx="3" fill="#7a5f45"/><path d="M20 50H80Q90 50 92 36H130Q134 36 140 50H200" fill="none" stroke="{b}" stroke-width="2.5"/>{robot(20, 50)}<circle cx="200" cy="50" r="5" fill="{t}"/><text x="140" y="24" font-size="9" fill="{m}">Route updated</text></svg>'
    if kind == 'avoid':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><rect x="0" y="6" width="220" height="10" fill="{ash}"/><rect x="0" y="58" width="220" height="10" fill="{ash}"/><rect x="120" y="22" width="24" height="24" rx="3" fill="#7a5f45"/><circle cx="132" cy="34" r="22" fill="none" stroke="{c}" stroke-dasharray="4 3"/><path d="M30 36C70 36 90 52 132 52S190 36 210 36" fill="none" stroke="{b}" stroke-width="2" stroke-dasharray="5 4"/>{robot(30, 36)}</svg>'
    if kind == 'fleet':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><path d="M10 36H210M110 4V68" stroke="{ash}" stroke-width="10"/>{robot(70, 36)}{robot(110, 16, v)}{robot(160, 36, t)}<rect x="94" y="44" width="34" height="14" rx="7" fill="#fff" stroke="{ash}"/><text x="111" y="54" text-anchor="middle" font-size="8" fill="{m}">Yield</text></svg>'
    if kind == 'tasks':
        rows = [('Pick · Aisle 4', 'R-01', b), ('Move · Dock B', 'R-03', t), ('Charge', 'R-02', v)]
        return '<svg viewBox="0 0 220 72" aria-hidden="true">' + ''.join(f'<rect x="0" y="{i * 24 + 2}" width="220" height="20" rx="10" fill="#fff"/><text x="12" y="{i * 24 + 16}" font-size="10" fill="#242424">{n}</text><circle cx="168" cy="{i * 24 + 12}" r="5" fill="{col}"/><text x="210" y="{i * 24 + 16}" text-anchor="end" font-size="10" font-weight="600" fill="#242424">{r}</text>' for i, (n, r, col) in enumerate(rows)) + '</svg>'
    if kind == 'safety':
        return f'<svg viewBox="0 0 220 72" aria-hidden="true"><circle cx="70" cy="36" r="32" fill="{t}" fill-opacity=".14" stroke="{t}" stroke-dasharray="4 3"/><circle cx="70" cy="36" r="16" fill="{c}" fill-opacity=".14" stroke="{c}" stroke-dasharray="4 3"/>{robot(70, 36)}<circle cx="114" cy="30" r="6" fill="#242424"/><text x="128" y="26" font-size="10" font-weight="600" fill="#242424">Slow zone</text><text x="128" y="40" font-size="9" fill="{m}">Stop zone inside</text><text x="128" y="54" font-size="9" fill="{m}">Configurable</text></svg>'
    raise ValueError(kind)


def kr_safety_diagram():
    return '''<svg class="plan" viewBox="0 0 520 300" role="img" aria-label="A robot with a configurable slow zone and stop zone. A person entering the slow zone makes the robot reduce speed; entering the stop zone makes it stop.">
  <rect width="520" height="300" rx="16" fill="#ffffff"/>
  <path d="M20 150 H500" stroke="#e4e2dc" stroke-width="44"/>
  <circle cx="210" cy="150" r="118" fill="#73C4C5" fill-opacity=".12" stroke="#73C4C5" stroke-width="2" stroke-dasharray="7 6"/>
  <circle cx="210" cy="150" r="58" fill="#FF7953" fill-opacity=".12" stroke="#FF7953" stroke-width="2" stroke-dasharray="7 6"/>
  <circle cx="210" cy="150" r="20" fill="#0A34ED"/><path d="M210 150h22" stroke="#fff" stroke-width="3"/>
  <path d="M232 150 H340" stroke="#0A34ED" stroke-width="2" stroke-dasharray="6 5"/>
  <circle cx="318" cy="96" r="9" fill="#242424"/><rect x="311" y="107" width="14" height="22" rx="5" fill="#242424"/>
  <text x="210" y="24" text-anchor="middle" font-size="13" font-weight="600" fill="#1e5f60">Slow zone</text>
  <text x="210" y="84" text-anchor="middle" font-size="12" font-weight="600" fill="#9a3412">Stop zone</text>
  <rect x="340" y="196" width="164" height="78" rx="12" fill="#101114"/>
  <text x="356" y="220" font-size="12" font-weight="600" fill="#e9e9ec">R-03 · Aisle 4</text>
  <text x="356" y="240" font-size="11" fill="#ffb39b">Person in slow zone</text>
  <text x="356" y="258" font-size="11" fill="#9b9daf">Speed reduced to 30%</text>
</svg>'''


def kr_stack_diagram():
    layers = [('Robot platforms', 'Mobile robots, robotic arms, drones and inspection robots', '#f5f5f5', '#242424'),
              ('Integration interfaces', 'Available SDKs and integration methods, including ROS 2 where supported', '#e8ecfd', '#0A34ED'),
              ('KenRobotics', 'Perception · path planning · fleet coordination · safety zones', '#101114', '#e9e9ec'),
              ('Ken ecosystem', 'Insights from other Ken modules where relevant', '#f1eafd', '#5a1fb0')]
    out = ['<svg class="plan" viewBox="0 0 520 330" role="img" aria-label="Integration stack: robot platforms connect through interfaces such as ROS 2 where supported to KenRobotics, which can connect with other Ken modules.">']
    for i, (t, d, bg, ink) in enumerate(layers):
        y = i * 80
        out.append(f'<rect x="{i * 10}" y="{y + 4}" width="{520 - i * 20}" height="66" rx="14" fill="{bg}" stroke="#d8d8dc"/>')
        out.append(f'<text x="{i * 10 + 20}" y="{y + 30}" font-size="13" font-weight="600" fill="{ink}">{t}</text>')
        out.append(f'<text x="{i * 10 + 20}" y="{y + 52}" font-size="10.5" fill="{"#9b9daf" if bg == "#101114" else "#4e4d4d"}">{d}</text>')
        if i < 3:
            out.append(f'<path d="M260 {y + 70} V{y + 84}" stroke="#7C28E9" stroke-width="2"/>')
    out.append('</svg>')
    return ''.join(out)


KR_FAQ = [
    ('What is KenRobotics?', 'KenRobotics is an AI robotics platform designed to support robot perception, autonomous path planning, obstacle avoidance, and coordination across connected robot fleets.'),
    ('What is robot fleet coordination?', 'Robot fleet coordination involves managing multiple robots operating in the same environment. It can include assigning tasks, managing routes, and reducing conflicts between robots.'),
    ('Can KenRobotics work with existing robots?', 'KenRobotics is designed to integrate with compatible robot platforms. Support depends on the robot hardware, available interfaces, and integration requirements.'),
    ('What is ROS 2, and why does it matter?', 'ROS 2 is a software framework commonly used to build robotics applications. Where supported, ROS 2 integration can help connect robotic systems with navigation, perception, and coordination software.'),
    ('How does KenRobotics help robots avoid obstacles?', "The system uses sensor inputs and AI-based environment understanding to support obstacle detection and route planning. Actual performance depends on the robot's sensors, environment, and safety configuration."),
    ('Can KenRobotics coordinate robots from different manufacturers?', 'Multi-platform integration depends on the available interfaces, supported robot models, and compatibility of their control systems. Contact the Intelense team to confirm support for your fleet.'),
    ('Can KenRobotics be used around people?', 'KenRobotics supports configurable human-robot safety zones and navigation logic. Deployments must also use appropriate hardware-level safety mechanisms, risk assessments, and applicable safety standards.'),
    ('Which industries can use KenRobotics?', 'Potential applications include warehousing, logistics, manufacturing, construction, agriculture, healthcare, and security. The available functions depend on the robot platform and deployment.'),
]



def kr_hero(fleet):
    media = f'''<div class="kr-console" role="img" aria-label="Live fleet map of a warehouse: four robots follow planned routes, one detours around an obstacle, and robots slow down near a person">
          <div class="kr-body">
            <canvas data-fleet width="900" height="540"></canvas>
            <ul class="kr-fleet"><li class="kr-h">Fleet · 4 robots</li>{fleet}</ul>
          </div>
        </div>'''
    return dict(uid='kr', logo='kenrobotics', site='Warehouse A · Fleet map', media=media,
                kpis=[('robot', 'Robots active', '4 / 4', 'On route', 'pos', '', None),
                      ('check', 'Tasks done today', '128', '↗ 12%', 'pos', 'vs yesterday', [60, 68, 72, 80, 86, 92, 98, 104, 110, 116, 122, 128])],
                alert=('Safety zone', 'warn', 'users', '<b>R-02</b> slowed down near a person in aisle 4.', 'Live'))


def page_kenrobotics():
    m = MOD['kenrobotics']
    fleet = ''.join(f'<li><i style="background:{col}"></i><b>{rid}</b><span data-fleet-status="{rid}">On route</span></li>' for rid, col in (('R-01', '#5b7cff'), ('R-02', '#a98bf5'), ('R-03', '#73C4C5'), ('R-04', '#78AFCF')))
    hero = f'''<section class="page-hero kv-hero" style="--mod:{m["color"]}">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap kv-hero-grid">
      <div class="kv-hero-copy">
        {crumbs(('modules.html', 'Modules'), (None, 'KenRobotics'))}
        <span class="eyebrow">AI for autonomous robotics by Intelense</span>
        {logo_img(m, 0.36, 'hero-logo')}
        <h1>Smarter Robots. Better Coordination.</h1>
        <p class="lede">KenRobotics helps autonomous robots understand their surroundings, navigate changing environments, avoid obstacles, and coordinate tasks across robot fleets.</p>
        <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">Book a Demo</a><a class="btn btn-ghost" href="#capabilities">Explore Capabilities</a></div>
        <p class="kv-tagline">AI-powered perception, path planning, and fleet coordination.</p>
      </div>
      <div class="kv-hero-visual">
        {ap.hero(kr_hero(fleet))}
        <p class="demo-note">Simulated fleet and example data</p>
      </div>
    </div>
  </section>'''

    caps = [('perception', 'AI Perception', 'Process sensor inputs to understand surroundings and detect obstacles.'),
            ('path', 'Dynamic Path Planning', 'Calculate routes and adapt when conditions or obstacles change.'),
            ('avoid', 'Obstacle Avoidance', 'Help robots navigate around objects and respond to changing environments.'),
            ('fleet', 'Fleet Coordination', 'Coordinate tasks and movements across multiple robots.'),
            ('tasks', 'Task Scheduling', 'Allocate work based on operational priorities and fleet availability.'),
            ('safety', 'Human-Robot Safety', 'Support configurable safety zones for environments shared by people and robots.')]
    what = f'''<section class="block" id="what">
    <div class="wrap">
      {head_block('What KenRobotics does', 'Give Your Robots the Intelligence to Work Together', 'Autonomous robots need more than the ability to move. They need to understand their surroundings, respond to changing conditions, and work efficiently alongside people and other machines.')}
      <div class="kv-split" style="margin-bottom:40px;align-items:start">
        <p class="kv-body" style="margin:0;font-size:17px">KenRobotics brings AI perception, dynamic path planning, and fleet coordination together to help robots navigate real-world environments and manage operational tasks.</p>
        <p class="kv-body" style="margin:0;font-size:17px">From warehouse robots moving goods to inspection robots operating in complex environments, KenRobotics helps teams coordinate autonomous operations more effectively.</p>
      </div>
      <h3 class="kc-sub" id="capabilities">Key capabilities</h3>
      <div class="kv-feats">{''.join(f'<article class="kv-feat"><div class="kv-mini">{kr_mini(k)}</div><span class="kv-num">{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></article>' for i, (k, t, d) in enumerate(caps))}</div>
    </div>
  </section>'''

    steps = [('Integrate Your Robots', 'Connect compatible robot platforms through supported integrations and interfaces. Configure the environment, operating zones, and workflow requirements for your deployment.'),
             ('Perceive, Plan, and Navigate', 'AI processes sensor data to build an understanding of the surroundings. Robots use this information to plan routes, identify obstacles, and adapt their movements.'),
             ('Coordinate Your Fleet', 'Coordinate tasks across connected robots, manage route conflicts, and allocate work based on operational priorities.'),
             ('Monitor and Scale', 'Monitor fleet activity and add compatible robots as operational needs grow, subject to platform and integration requirements.')]
    how = f'''<section class="block" id="how">
    <div class="wrap">
      {head_block('How it works', 'From Robot Integration to Coordinated Operations', '')}
      <ol class="kv-steps four">{''.join(f'<li><span>{i + 1:02d}</span><h3>{t}</h3><p>{d}</p></li>' for i, (t, d) in enumerate(steps))}</ol>
    </div>
  </section>'''

    core = [('eye', 'Real-Time Environment Understanding', 'Use sensor inputs to help robots interpret their surroundings and respond to changes in their operating environment.'),
            ('route', 'Adaptive Navigation', 'Plan and adjust routes around obstacles, restricted areas, and changing conditions.'),
            ('robot', 'Multi-Robot Coordination', 'Help multiple robots work within the same environment while managing task allocation and movement conflicts.'),
            ('zone', 'Human-Robot Safety Zones', 'Configure operating boundaries and safety rules for environments where people and robots work near one another.'),
            ('timeline', 'Intelligent Task Allocation', 'Prioritise and distribute tasks across a connected fleet according to operational requirements.'),
            ('plug', 'Flexible Robot Integration', 'Connect supported robot platforms through available SDKs and integration methods, including ROS 2 where supported.')]
    corecaps = f'''<section class="block" id="core">
    <div class="wrap">
      {head_block('Core capabilities', 'Intelligence for Real-World Robotics', '')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p></div>' for ic, t, d in core)}</div>
    </div>
  </section>'''

    uses = [('forklift', 'Warehousing and Logistics', 'Coordinate autonomous mobile robots for material movement, picking support, sorting, and internal logistics.', 'industrial.html#industrial', 'industrial'),
            ('wrench', 'Manufacturing', 'Support automated material handling, repetitive movement tasks, and coordination between robotic systems on production floors.', '', 'industrial'),
            ('patrol', 'Defence and Security', 'Support autonomous patrol, inspection, and other robotic operations in environments that require carefully configured safety and access controls.', '', 'public-safety'),
            ('hardhat', 'Construction', 'Enable robotic and drone-based site inspection, surveying, and progress monitoring, depending on the platform and integration.', '', 'industrial'),
            ('leaf', 'Agriculture', 'Support field robots for crop scouting, spraying, and other precision operations, with opportunities to integrate insights from KenAgri.', 'kenagri', 'agriculture'),
            ('plug', 'Healthcare', 'Support compatible autonomous systems used for internal delivery and transport tasks in healthcare facilities.', '', 'healthcare')]
    where = f'''<section class="block" id="industries">
    <div class="wrap">
      {head_block('Where KenRobotics can be used', 'Autonomous Intelligence Across Industries', '')}
      <div class="caps">{''.join(f'<div class="cap">{icon(ic)}<h3>{t}</h3><p>{d}</p>' + (f'<a class="kv-link" href="kenagri.html">Explore KenAgri →</a>' if extra == 'kenagri' else '') + f'<a class="kv-link" href="industries.html#{a}"{" style=padding-top:0" if extra == "kenagri" else ""}>More on {IND[a]["name"].lower()} →</a></div>' for ic, t, d, extra, a in uses)}</div>
    </div>
  </section>'''

    collab = f'''<section class="block" id="collaboration">
    <div class="wrap kv-split" style="align-items:start">
      <div>
        <span class="eyebrow">Human-robot collaboration</span>
        <h2 style="margin-top:18px">Designed for Dynamic Work Environments</h2>
        <p class="lede" style="margin-top:20px">Robots often operate in spaces where people, vehicles, and other machines are moving at the same time.</p>
        <p class="kv-body">KenRobotics supports configurable safety zones and dynamic navigation to help robots respond to obstacles and changing conditions.</p>
        <p class="kv-body">Teams can define operating areas, restricted zones, and workflow rules according to their environment and deployment requirements.</p>
        <p class="kv-body">The goal is to make autonomous operations more coordinated and predictable while keeping safety requirements central to deployment planning.</p>
        <p class="kv-body kc-note"><b style="color:var(--off-black)">Note:</b> AI-based detection and navigation should complement, not replace, certified robot safety systems and site-specific safety procedures.</p>
      </div>
      <div class="kr-collab">
        <div class="tile-solo" role="img" aria-label="Robot front camera in a warehouse aisle: a pallet blocks the path, a person is detected ahead, and the planned route bends around the obstacle">
          <canvas class="cctv" data-scene="robot" data-osd="R-03  FRONT CAMERA" width="960" height="540"></canvas>
        </div>
        <figure class="panel" style="margin:12px 0 0;padding:12px">{kr_safety_diagram()}</figure>
        <p class="demo-note">Simulated camera feed and example safety zones</p>
      </div>
    </div>
  </section>'''

    integ = f'''<section class="block" id="integration">
    <div class="wrap">
      {head_block('Integration and scalability', 'Start with Your Robots. Build from There.', 'Integrating autonomous robotics into existing operations can involve different hardware platforms, sensors, layouts, and workflows.')}
      <div class="kv-split" style="align-items:center">
        <div>
          <p class="kv-body" style="margin-top:0">KenRobotics is designed to support compatible robot platforms and integration methods, helping teams build toward coordinated fleet operations.</p>
          <ul class="kv-defs">
            <li><b>Robot Integration</b><span>Connect supported robot platforms through available interfaces.</span></li>
            <li><b>Environment Mapping</b><span>Configure floor plans, operating areas, and restricted zones.</span></li>
            <li><b>Fleet Management</b><span>Coordinate tasks and movements across connected robots.</span></li>
            <li><b>Expandable Operations</b><span>Extend deployments as robot fleets and workflows grow.</span></li>
            <li><b>Platform Integration</b><span>Explore connections with other Intelense AI modules where relevant.</span></li>
          </ul>
          <p class="kv-body kc-note">Integration timelines and supported capabilities depend on the robot model, hardware, and deployment requirements.</p>
        </div>
        <figure class="panel" style="margin:0">{kr_stack_diagram()}</figure>
      </div>
    </div>
  </section>'''

    eco_txt = [('kenvision', 'AI video analytics for footfall, movement, queues, and operational visibility.'),
               ('kensafety', 'AI-powered workplace safety monitoring and hazard detection.'),
               ('keniot', 'Sensor analytics, anomaly detection, and predictive maintenance.'),
               ('kenagri', 'AI-powered precision agriculture and crop intelligence.'),
               ('kenhome', 'AI-powered monitoring for homes and connected spaces.'),
               ('kenvoice', 'AI audio analytics for retail conversations.')]
    eco = f'''<section class="block" id="ecosystem">
    <div class="wrap">
      {head_block('The Ken ecosystem', 'One AI Platform. Connected Intelligence.', 'KenRobotics is part of the Intelense Ken ecosystem, designed to bring AI capabilities across different operational environments.')}
      <div class="kr-eco">{''.join(f'<a class="kr-eco-card" href="{k}.html" style="--mod:{MOD[k]["color"]}">{logo_img(MOD[k], 0.2)}<span><b>{MOD[k]["name"]}:</b> {d}</span></a>' for k, d in eco_txt)}</div>
      <p class="kv-body" style="max-width:62ch">Together, these modules can help businesses connect insights from their physical environments, equipment, and operations.</p>
    </div>
  </section>'''

    final = f'''<section class="cta">
    <div class="wash wash-b" aria-hidden="true" style="top:10%;right:20%"></div>
    <div class="wash wash-a" aria-hidden="true" style="top:30%;left:20%"></div>
    <div class="wrap">
      <span class="eyebrow">Get started</span>
      <h2 style="margin-top:20px">Ready to Make Your Robot Fleet Smarter?</h2>
      <p class="lede" style="margin:18px auto 0">Explore how KenRobotics can support autonomous navigation, fleet coordination, and intelligent operations for your environment.</p>
      <div class="hero-ctas"><a class="btn btn-blue" href="contact.html">Book a Demo</a></div>
      <p class="kv-sign">KenRobotics by Intelense — Intelligence for autonomous systems.</p>
    </div>
  </section>'''

    body = '\n\n  '.join([hero, what, how, corecaps, where, collab, integ, eco, faq_block(KR_FAQ), final, faq_schema(KR_FAQ)])
    return dict(file='kenrobotics.html', title='KenRobotics: AI for Autonomous Robotics | Intelense',
                desc='KenRobotics helps autonomous robots understand their surroundings, navigate changing environments, avoid obstacles and coordinate tasks across robot fleets.',
                active='kenrobotics', body=body, cctv=True)


PAGES = [page_index, page_platform, page_modules, page_kenvision, page_kensafety, page_kenagri, page_kenhome, page_keniot, page_kenvoice, page_kenrobotics, page_industries, page_about, page_contact]

# ---------------------------------------------------------------- output

GRID_OPTS = "{ cellSize: 60, color: '#0a0a0a', radius: 160, falloff: 'smooth', holdTime: 300, fadeDuration: 700, lineWidth: 1, maxOpacity: 0.3, fillOpacity: 0, gridOpacity: 0, cellRadius: 4, clickPulse: true, pulseSpeed: 700 }"
FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&display=swap">'


# ---------------------------------------------------------------- real camera footage
# Drop a still (.jpg/.png/.webp) or clip (.mp4/.webm) into assets/footage and describe it in feeds.json.
# Every simulated canvas for that scene is then swapped for the real frame with light analytics overlays.

FOOTAGE = ASSETS / 'footage'
TONE_RGB = {'pos': '115,196,197', 'neg': '255,121,83', 'info': '120,150,255', 'violet': '170,120,245', 'warn': '242,210,138', 'mute': '255,255,255'}


def load_feeds():
    import json
    f = FOOTAGE / 'feeds.json'
    feeds = json.loads(f.read_text()) if f.exists() else {}
    return {k: v for k, v in feeds.items() if not k.startswith('_') and (FOOTAGE / v['src']).exists()}


FEEDS = load_feeds()


def feed_html(scene):
    f = FEEDS[scene]
    src = f'assets/footage/{f["src"]}'
    if src.endswith(('.mp4', '.webm')):
        media = f'<video src="{src}" autoplay muted loop playsinline preload="metadata"></video>'
    else:
        media = f'<img src="{src}" alt="" loading="lazy" decoding="async">'
    svg, tags = [], []
    for z in f.get('zones', []):
        rgb = TONE_RGB[z.get('tone', 'mute')]
        pts = ' '.join(f'{x * 1000:.0f},{y * 1000:.0f}' for x, y in z['points'])
        svg.append(f'<polygon points="{pts}" fill="rgba({rgb},.10)" stroke="rgba({rgb},.75)" stroke-dasharray="6 5"/>')
        x0, y0 = min(x for x, _ in z['points']), min(y for _, y in z['points'])
        tags.append((x0, y0, z['label'], z.get('tone', 'mute'), 'zone'))
    for ln in f.get('lines', []):
        rgb = TONE_RGB[ln.get('tone', 'info')]
        (x1, y1), (x2, y2) = ln['from'], ln['to']
        svg.append(f'<line x1="{x1 * 1000:.0f}" y1="{y1 * 1000:.0f}" x2="{x2 * 1000:.0f}" y2="{y2 * 1000:.0f}" stroke="rgba({rgb},.9)"/>')
        tags.append((min(x1, x2), min(y1, y2), ln['label'], ln.get('tone', 'info'), 'line'))
    for b in f.get('boxes', []):
        x, y, w, h = (b[k] * 1000 for k in ('x', 'y', 'w', 'h'))
        c = min(w, h) * 0.22
        d = (f'M{x},{y + c}V{y}H{x + c} M{x + w - c},{y}H{x + w}V{y + c} M{x + w},{y + h - c}V{y + h}H{x + w - c} M{x + c},{y + h}H{x}V{y + h - c}')
        rgb = TONE_RGB[b.get('tone', 'mute')]
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="rgba({rgb},.28)"/><path d="{d}" fill="none" stroke="rgba({rgb},.95)" stroke-width="2"/>')
        tags.append((b['x'], b['y'], b['label'], b.get('tone', 'mute'), 'box'))
    labels = ''.join(f'<span class="feed-tag {kind}" style="left:{x * 100:.2f}%;top:{y * 100:.2f}%"><i class="{tone}"></i>{lab}</span>' for x, y, lab, tone, kind in tags)
    return (f'<figure class="feed">{media}'
            f'<svg class="feed-ov" viewBox="0 0 1000 1000" preserveAspectRatio="none" aria-hidden="true">{"".join(svg)}</svg>{labels}'
            f'<figcaption class="feed-osd"><span><b class="rec"></b>{f.get("camera", "")}</span><span data-feed-clock>14:32:09</span></figcaption></figure>')


def swap_feeds(html):
    if not FEEDS:
        return html
    return re.sub(r'<canvas class="cctv" data-scene="(\w+)"[^>]*></canvas>',
                  lambda m: feed_html(m.group(1)) if m.group(1) in FEEDS else m.group(0), html)


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
    content = f'{header(p["active"])}\n<main id="top">\n  {swap_feeds(p["body"])}\n</main>\n\n{footer()}\n' + '\n'.join(scripts) + '\n'
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
        shutil.copytree(FOOTAGE, out / 'assets' / 'footage', dirs_exist_ok=True)
        print('wrote inline copy to', out)


if __name__ == '__main__':
    main()
