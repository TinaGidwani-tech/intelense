"""Extract the old kenvision.ai pages into content/pages.json (text kept word for word).
usage: extract_old.py OLD_SITE_DIR"""
import sys, re, json, pathlib
from bs4 import BeautifulSoup

root = pathlib.Path(sys.argv[1])
out = pathlib.Path(__file__).resolve().parent.parent / 'content' / 'pages.json'

def T(el):
    return re.sub(r'\s+', ' ', el.get_text(' ', strip=True)).replace(' ,', ',').replace(' .', '.') if el else ''

def meta(s):
    g = lambda sel, attr='content': (s.select_one(sel) or {}).get(attr) if s.select_one(sel) else None
    return {
        'title': T(s.title),
        'description': re.sub(r'\s+', ' ', g('meta[name=description]') or ''),
        'og_description': re.sub(r'\s+', ' ', g('meta[property="og:description"]') or ''),
        'og_image': g('meta[property="og:image"]'),
        'keywords': g('meta[name=keywords]'),
        'jsonld': [json.loads(x.string) for x in s.select('script[type="application/ld+json"]')],
    }

def img(el):
    i = el.find('img') if el else None
    return {'src': i['src'].replace('../', ''), 'alt': i.get('alt', '')} if i else None

def cards(sec, head='h3'):
    res = []
    for h in sec.find_all(head):
        box = h.parent
        for _ in range(3):
            if box.find('img') or box.find('p'): break
            box = box.parent
        p = box.find('p')
        res.append({'t': T(h), 'p': T(p), 'img': img(box)})
    return res

def faq(s):
    return [{'q': T(d.find('summary')), 'a': T(d.find('p'))} for d in s.find_all('details')]

pages = {}
def solution(name):
    s = BeautifulSoup((root / 'solutions' / f'{name}.html').read_text(encoding='utf-8'), 'html.parser')
    m = s.main
    secs = m.find_all('section', recursive=False) or m.find_all('section')
    d = {'meta': meta(s), 'h1': T(m.find('h1')), 'lede': T(m.find('h1').find_next('p')),
         'hero_img': img(secs[0]), 'faq': faq(s)}
    # sections by heading
    def sec_with(h2text, tag='h2'):
        for x in m.find_all(tag):
            if T(x).startswith(h2text): return x
    for sec in secs:
        h2 = sec.find('h2')
        if not h2: continue
        t = T(h2)
        if sec.find('details'): d['faq_h'] = {'h': t, 'p': T(h2.find_next('p'))}
        elif sec.find_all('h4') and not sec.find('details') and 'pain' not in d and sec.find('h4') and not sec.find('h3'):
            d['pain'] = {'h': t, 'items': [{'t': T(h), 'p': T(h.find_next('p'))} for h in sec.find_all('h4')]}
        elif t.startswith(('How KenVision', 'From Cameras')):
            d['how_h'] = t
        elif sec.find_all('img') and len(sec.find_all('h3')) >= 6:
            d['core'] = {'h': t, 'h2b': [T(x) for x in sec.find_all('h2')][1:], 'items': cards(sec)}
        elif t in ('Business Impact', 'Operational Impact', 'Impact for Cities'):
            d['impact'] = {'h': t, 'items': [{'t': T(h), 'p': T(h.find_next('p'))} for h in sec.find_all('h3')]}
        elif t.startswith(('Built for', 'Designed for')):
            d['scale'] = {'h': t, 'li': [T(x).lstrip('✓ ').strip() for x in sec.find_all('li')], 'img': img(sec)}
        elif sec.find_all('li') and ('Why it matters' in T(sec) or 'In the field' in T(sec) or 'Beyond the panic' in T(sec)):
            ps = [T(p) for p in sec.find_all('p')]
            d['field'] = {'eyebrow': ps[0], 'h': t, 'lede': T(h2.find_next('p')), 'li': [T(x) for x in sec.find_all('li')],
                          'caption': next((p for p in ps if p in ('Shopper funnel', 'Occupancy-driven energy', 'From signal to standard response', 'Crowd density over time')), '')}
        elif len(sec.find_all('h3')) == 4 and 'why' not in d:
            d['why'] = {'h': t, 'items': [{'t': T(h), 'p': T(h.find_next('p'))} for h in sec.find_all('h3')]}
        elif len(secs) and sec is secs[-2]:
            pass
    # strip words
    for sec in secs:
        if sec.find('h2') is None and sec.find(class_=re.compile('ticker|marquee|strip'), recursive=True):
            words = [T(x) for x in sec.select('span,div') if T(x) and not x.find(['span', 'div'])]
            d['strip'] = list(dict.fromkeys(words))
    # cta
    h = m.find_all('h2')[-1]
    d['cta'] = {'h': T(h), 'p': T(h.find_next('p'))}
    # steps
    st = [x for x in m.find_all('h3') if re.match(r'\d\. ', T(x))]
    d['steps'] = [{'t': T(x), 'p': T(x.find_next('p')), 'img': img(x.parent)} for x in st]
    pages[name] = d

for n in ('retail-analytics', 'commercial-buildings', 'smart-cities', 'video-surveillance'):
    solution(n)

# solutions index
s = BeautifulSoup((root / 'solutions' / 'index.html').read_text(encoding='utf-8'), 'html.parser')
m = s.main or s.body
pages['solutions-index'] = {'meta': meta(s), 'h1': T(m.find('h1')), 'lede': T(m.find('h1').find_next('p')),
    'hero_img': {'src': 'assets/images/solutions-hero-collage.webp', 'alt': 'AI Video Intelligence Across Industries'}}
for name, f in (('home', 'index.html'), ('company', 'company.html'), ('contact', 'contact.html'), ('404', '404.html')):
    s = BeautifulSoup((root / f).read_text(encoding='utf-8'), 'html.parser')
    pages[name] = {'meta': meta(s)}
    if name == 'home':
        pages[name]['faq'] = faq(s)
        h = [x for x in s.find_all('h2') if T(x).startswith('Frequently')][0]
        pages[name]['faq_h'] = {'h': T(h), 'p': T(h.find_next('p'))}
json.dump(pages, out.open('w', encoding='utf-8'), ensure_ascii=False, indent=1)
print({k: sorted(v) for k, v in pages.items()})
