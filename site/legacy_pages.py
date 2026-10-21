"""Rebuilds the old www.intelense.com pages that have no equivalent in the new design.

The text comes verbatim from content/old-pages.json (extracted from the live old site). Nothing is rewritten:
this module only decides which existing site.css pattern each block of text goes into.
"""
import json
import re
from pathlib import Path

CONTENT = json.loads((Path(__file__).resolve().parent / 'content' / 'old-pages.json').read_text())

SLUGS = ['retail-analytics', 'casestudies', 'kensafety-construction', 'kenvision-retail', 'kenhome-safety', 'blog',
         'blogs/generative-ai-rewriting-business', 'blogs/ai-video-surveillance', 'blogs/ai-changing-how-we-work',
         'blogs/ai-across-every-sector', 'blogs/ai-digital-billboards', 'blogs/ai-construction-safety', 'blogs/ai-smart-buildings',
         'faq', 'privacy', 'terms']
# old stub pages that only redirected to /retail-analytics
REDIRECTS = {'/video-analytics-retail': '/retail-analytics', '/footfall-analytics': '/retail-analytics', '/queue-analytics': '/retail-analytics',
             '/heatmap-analytics': '/retail-analytics', '/cctv-analytics-retail': '/retail-analytics', '/index': '/'}
OLD_HOSTS = ('https://www.intelense.com', 'https://intelense.com')


def file_for(slug):
    return slug.replace('/', '-') + '.html'


def public_for(slug):
    return '/' + slug


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def attr(t):
    return esc(t).replace('"', '&quot;')


def link(href, public):
    """Old absolute URL -> the .html name build.py rewrites to the clean URL (so the same markup works in site/ and in dist/)."""
    for h in OLD_HOSTS:
        if href.startswith(h):
            href = href[len(h):] or '/'
    if href.startswith(('mailto:', 'tel:', 'http')):
        return href
    path, _, frag = href.partition('#')
    path = path.rstrip('/') or '/'
    path = REDIRECTS.get(path, path)
    if path == '/contact':
        return 'contact.html' + ('#form' if frag == 'demo' else ('#' + frag if frag else ''))
    if path == '/':
        return 'index.html' + ('#' + frag if frag else '')
    if path == '/ken360':
        return 'platform.html' + ('#' + frag if frag else '')
    return path.strip('/').replace('/', '-') + '.html' + ('#' + frag if frag else '') if path else '#' + frag


def fix_html(html, public):
    return re.sub(r'href="([^"]*)"', lambda m: f'href="{link(m.group(1), public)}"' if m.group(1).startswith(('http', '/')) else m.group(0), html)


def plain(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html.replace('<br>', ' '))).strip()


def unesc(t):
    return t.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&amp;', '&')


# ------------------------------------------------------------------ block grouping

def classify(b):
    t, cls = b['t'], b.get('cls', '')
    if cls.startswith('cam-') or cls in ('breadcrumb', 'post-breadcrumb'):
        return 'drop'
    if t == 'img' or t == 'video':
        return 'drop'
    if t == 'line' and b['html'] == 'Answer Block':
        return 'drop'
    return t if t != 'line' else 'line:' + cls


def sections(blocks):
    """Split into [(eyebrow, h2 block, content blocks)] at each eyebrow line / h2."""
    secs, cur = [], None
    for b in blocks:
        if classify(b) == 'drop':
            continue
        if b['t'] == 'line' and b['cls'] == 'eyebrow':
            cur = {'eyebrow': b['html'], 'h2': None, 'content': []}
            secs.append(cur)
        elif b['t'] == 'h2':
            if cur and cur['h2'] is None and not cur['content']:
                cur['h2'] = b
            else:
                cur = {'eyebrow': None, 'h2': b, 'content': []}
                secs.append(cur)
        else:
            if cur is None:
                cur = {'eyebrow': None, 'h2': None, 'content': []}
                secs.append(cur)
            cur['content'].append(b)
    return secs


def render_content(items, public, sid=''):
    out, i, n = [], 0, len(items)

    def grp(pred):
        nonlocal i
        res = []
        while i < n and pred(items[i]):
            res.append(items[i])
            i += 1
        return res

    while i < n:
        b = items[i]
        t, cls = b['t'], b.get('cls', '')
        if t == 'line' and cls == 'challenge-num':
            cards = []
            while i + 2 < n + 0 and items[i]['t'] == 'line' and items[i]['cls'] == 'challenge-num':
                cards.append((items[i]['html'], items[i + 1]['html'], items[i + 2]['html']))
                i += 3
            out.append('<div class="caps legacy-caps">' + ''.join(f'<div class="cap"><span class="num">{a}</span><h3>{b_}</h3><p>{c}</p></div>' for a, b_, c in cards) + '</div>')
        elif t == 'line' and cls == 'seo-card-label':
            cards = []
            while i + 2 < n and items[i]['t'] == 'line' and items[i]['cls'] == 'seo-card-label':
                cards.append((items[i]['html'], items[i + 1]['html'], items[i + 2]['html']))
                i += 3
            out.append('<div class="caps legacy-caps">' + ''.join(f'<div class="cap"><span class="num">{a}</span><h3>{b_}</h3><p>{c}</p></div>' for a, b_, c in cards) + '</div>')
        elif t == 'line' and cls == 'seo-step-num':
            steps = []
            while i + 2 < n and items[i]['t'] == 'line' and items[i]['cls'] == 'seo-step-num':
                steps.append((items[i]['html'], items[i + 1]['html'], items[i + 2]['html']))
                i += 3
            out.append('<div class="steps four">' + ''.join(f'<div><b>Step {a}</b><h3>{b_}</h3><p>{c}</p></div>' for a, b_, c in steps) + '</div>')
        elif t == 'h4':
            cards = []
            while i + 1 < n and items[i]['t'] == 'h4':
                cards.append((items[i]['html'], items[i + 1]['html']))
                i += 2
            out.append('<div class="caps legacy-caps">' + ''.join(f'<div class="cap"><h3>{a}</h3><p>{b_}</p></div>' for a, b_ in cards) + '</div>')
        elif t == 'line' and cls in ('impact-item', 'seo-metric', 'post-stat', 'cs-stat'):
            stats = grp(lambda x: x['t'] == 'line' and x['cls'] in ('impact-item', 'seo-metric', 'post-stat', 'cs-stat'))
            cells = []
            for st in stats:
                pr = [esc(unesc(x)) for x in st['parts']]
                cells.append(f'<div><b>{pr[0]}</b>' + (f'<span>{pr[1]}</span>' if len(pr) > 1 else '') + (f'<small>{pr[2]}</small>' if len(pr) > 2 else '') + '</div>')
            out.append('<div class="stats">' + ''.join(cells) + '</div>')
        elif t == 'line' and cls == 'case-block-label':
            cards = []
            while i + 1 < n and items[i]['t'] == 'line' and items[i]['cls'] == 'case-block-label':
                cards.append((items[i]['html'], items[i + 1]['items'] if items[i + 1]['t'] == 'ul' else []))
                i += 2
            out.append('<div class="caps legacy-caps two">' + ''.join(f'<div class="cap"><h3>{a}</h3><ul class="bul">' + ''.join(f'<li>{x}</li>' for x in lis) + '</ul></div>' for a, lis in cards) + '</div>')
        elif t == 'line' and cls == 'result-tag':
            out.append(f'<p class="callout">{b["html"]}</p>'); i += 1
        elif t == 'p' and b.get('ctx') == 'answer-block':
            out.append(f'<p class="callout">{b["html"]}</p>'); i += 1
        elif t == 'p' and b.get('ctx') == 'why-item':
            ps = grp(lambda x: x['t'] == 'p' and x.get('ctx') == 'why-item')
            out.append('<ul class="why">' + ''.join(f'<li>{x["html"]}</li>' for x in ps) + '</ul>')
        elif t == 'p' and b.get('ctx') == 'post-pullquote':
            out.append(f'<blockquote class="pullquote">{b["html"]}</blockquote>'); i += 1
        elif t == 'p':
            out.append(f'<p>{b["html"]}</p>'); i += 1
        elif t in ('ul', 'ol'):
            out.append(f'<{t} class="bul">' + ''.join(f'<li>{x}</li>' for x in b['items']) + f'</{t}>'); i += 1
        elif t == 'h2':
            out.append(f'<h2>{b["html"]}</h2>'); i += 1
        elif t == 'h3' and i + 1 < n and items[i + 1].get('ctx') == 'post-cta':
            cta = [b, items[i + 1]]
            i += 2
            if i < n and items[i]['t'] == 'link':
                cta.append(items[i]); i += 1
            out.append(f'<div class="post-cta"><h3>{cta[0]["html"]}</h3><p>{cta[1]["html"]}</p>' + (f'<a class="btn btn-blue" href="{link(cta[2]["href"], public)}">{cta[2]["html"]}</a>' if len(cta) > 2 else '') + '</div>')
        elif t == 'h3':
            # sub-heading, optionally followed by paragraphs/lists (privacy, terms, retail "what retailers can measure")
            out.append(f'<h3>{b["html"]}</h3>'); i += 1
        elif t == 'faq':
            fq = grp(lambda x: x['t'] == 'faq')
            out.append('<div class="faq-list">' + ''.join(f'<details{" open" if k == 0 else ""}><summary>{f["q"]}</summary>{"".join(f"<p>{a["html"]}</p>" for a in f["a"])}</details>' for k, f in enumerate(fq)) + '</div>')
        elif t == 'line' and cls == 'btn-row':
            out.append(f'<div class="hero-ctas legacy-ctas">{btns(b, public)}</div>'); i += 1
        elif t == 'link':
            out.append(f'<p><a class="btn btn-blue" href="{link(b["href"], public)}">{b["html"]}</a></p>'); i += 1
        elif t == 'line' and cls == 'related-link':
            out.append(f'<p>{b["html"]}</p>'); i += 1
        elif t == 'line':
            out.append(f'<p>{b["html"]}</p>'); i += 1
        else:
            i += 1
    return '\n'.join(out)


def btns(b, public):
    """btn-row line: html holds the anchors with absolute URLs."""
    anchors = re.findall(r'<a href="([^"]*)">(.*?)</a>', b['html'])
    return ''.join(f'<a class="btn {"btn-blue" if k == 0 else "btn-ghost"}" href="{link(h, public)}">{t}</a>' for k, (h, t) in enumerate(anchors))


# ------------------------------------------------------------------ pages

FAQ_LINKS = ['/retail-analytics', '/retail-analytics', '/casestudies', '/contact#demo']  # old seo-link-card targets (the 2nd was /video-analytics-retail, now a 301)
CASE_CARDS = ['/kensafety-construction', '/kenvision-retail', '/kenhome-safety']
BLOG_CARDS = [s for s in SLUGS if s.startswith('blogs/')]
RETAIL_IDS = {'Definition': 'definition', 'How It Works': 'how-it-works', 'Key Features': 'features', 'FAQ': 'faqs', 'Retail Analytics': 'modules'}
CTA_EYEBROWS = ('Get Started', 'Book Demo')


def hero_split(blocks):
    """Hero = everything up to the first section marker after the h1; returns (hero blocks, rest)."""
    h1_at = next(i for i, b in enumerate(blocks) if b['t'] == 'h1')
    for i in range(h1_at + 1, len(blocks)):
        b = blocks[i]
        if (b['t'] == 'line' and b['cls'] in ('eyebrow', 'pp-sidebar-label', 'blog-tag')) or b['t'] in ('h2', 'img') or (b['t'] == 'p' and b.get('ctx') == 'post-body') \
                or (b['t'] == 'line' and b['cls'] == '' and not blocks[i]['html'].startswith('Case Study')):
            # first image (case-study visual) or section start ends the hero; casestudies/blog index handle their own cards
            return blocks[:i], blocks[i:]
    return blocks, []


def hero_shell(crumb, eyebrow, h1, lede='', below='', ctas=''):
    """Same markup as build.page_hero (no media), with a slot for pills / meta / anchors below the lede."""
    return f'''<section class="page-hero legacy-hero">
    <div class="wash wash-a" aria-hidden="true"></div>
    <div class="wash wash-b" aria-hidden="true"></div>
    <div class="cursor-grid" aria-hidden="true"></div>
    <div class="wrap">
      {crumb}
      <span class="eyebrow">{eyebrow}</span>
      <h1>{h1}</h1>
      {f'<p class="lede">{lede}</p>' if lede else ''}
      {below}
      {f'<div class="hero-ctas">{ctas}</div>' if ctas else ''}
    </div>
  </section>'''


def make_pages(h):
    """h: the build.py helpers (page_hero, crumbs, cta_band, faq_schema)."""
    pages = []

    def hero_html(slug, hero, public):
        kicker = next((b for b in hero if b['t'] == 'line' and b['cls'] in ('seo-kicker', 'post-tag', 'pp-hero-eyebrow', 'eyebrow', '')), None)
        h1 = next(b for b in hero if b['t'] == 'h1')
        lede = next((b for b in hero if b['t'] == 'p'), None)
        extra = ''
        pills = next((b for b in hero if b['t'] == 'line' and b['cls'] == 'stat-pills'), None)
        meta = next((b for b in hero if b['t'] == 'line' and b['cls'] in ('post-meta', 'pp-hero-meta')), None)
        anchors = next((b for b in hero if b['t'] == 'line' and b['cls'] == 'seo-anchor-row'), None)
        ctas = next((b for b in hero if b['t'] == 'line' and b['cls'] == 'btn-row'), None)
        eyebrow = kicker['html'] if kicker else ''
        chips = ''
        if kicker and kicker['cls'] == '' and kicker['parts']:
            eyebrow = kicker['parts'][0]
            chips = ''.join(f'<span class="chip">{esc(x)}</span>' for x in kicker['parts'][1:])
        if meta and meta['cls'] == 'post-meta':
            extra = '<p class="post-meta">' + ''.join(f'<span>{esc(x)}</span>' for x in meta['parts']) + '</p>'
        elif meta:
            extra = f'<p class="post-meta"><span>{meta["html"]}</span></p>'
        if pills:
            extra += '<div class="chips legacy-pills">' + ''.join(f'<span class="chip">{esc(x)}</span>' for x in pills['parts']) + '</div>'
        if anchors:
            extra += '<nav class="anchor-row" aria-label="Page sections">' + ''.join(f'<a href="{a}">{t}</a>' for a, t in re.findall(r'<a href="([^"]*)">(.*?)</a>', anchors['html'])) + '</nav>'
        parent = {'blogs': ('blog.html', 'Blog')}.get(slug.split('/')[0]) if '/' in slug else None
        if slug in ('kensafety-construction', 'kenvision-retail', 'kenhome-safety'):
            parent = ('casestudies.html', 'Case studies')
        crumb = h.crumbs(*(([parent] if parent else []) + [(None, plain(h1['html']) if len(plain(h1['html'])) < 40 else CONTENT[slug]['title'].split(' | ')[0])]))
        return hero_shell(crumb, esc(unesc(eyebrow)) if False else eyebrow, h1['html'], lede['html'] if lede else '', (f'<div class="chips legacy-pills">{chips}</div>' if chips else '') + extra,
                          btns(ctas, public) if ctas else '')

    def head(sec, sid=''):
        ey = f'<span class="eyebrow">{sec["eyebrow"]}</span>' if sec['eyebrow'] else ''
        h2 = f'<h2>{sec["h2"]["html"]}</h2>' if sec['h2'] else ''
        return ey, h2

    def sec_html(sec, public, ids=None):
        content = sec['content']
        ey, h2 = head(sec)
        eb = plain(sec['eyebrow'] or '')
        sid = f' id="{ids[eb]}"' if ids and eb in ids else ''
        if eb in CTA_EYEBROWS and sec['h2']:
            ps = [b for b in content if b['t'] == 'p']
            ct = next((b for b in content if b['t'] == 'line' and b['cls'] == 'btn-row'), None)
            return (f'<section class="cta"{sid}><div class="wash wash-b" aria-hidden="true" style="top:10%;right:20%"></div><div class="wash wash-a" aria-hidden="true" style="top:30%;left:20%"></div>'
                    f'<div class="wrap">{ey}<h2 style="margin-top:20px">{sec["h2"]["html"]}</h2>' + (f'<p class="lede" style="margin:20px auto 0">{ps[0]["html"]}</p>' if ps else '')
                    + (f'<div class="hero-ctas">{btns(ct, public)}</div>' if ct else '') + '</div></section>')
        if content and all(b['t'] == 'faq' for b in content):
            return f'<section class="block"{sid}><div class="wrap faq-grid"><div>{ey}<h2 style="margin-top:18px">{sec["h2"]["html"] if sec["h2"] else ""}</h2></div>' + render_content(content, public) + '</div></section>'
        lede = ''
        if content and content[0]['t'] == 'p' and content[0].get('ctx') in ('section-header', 'seo-copy') and sec['h2']:
            lede = f'<p class="lede">{content[0]["html"]}</p>'
            content = content[1:]
        top = f'<div class="head">\n<div>{ey}{h2}</div>{lede}</div>' if sec['h2'] else ''
        return f'<section class="block"{sid}><div class="wrap">{top}{fix_html(render_content(content, public), public)}</div></section>'

    def generic(slug, ids=None):
        d = CONTENT[slug]
        public = public_for(slug)
        hero, rest = hero_split(d['blocks'])
        body = [hero_html(slug, hero, public)]
        for sec in sections(rest):
            if sec['h2'] is None and sec['eyebrow'] is None and not sec['content']:
                continue
            body.append(sec_html(sec, public, ids))
        return d, public, body

    def finish(slug, d, body, extra_ld=()):
        ld = [j for j in d['jsonld'] if j.get('@type') != 'Organization']
        return dict(file=file_for(slug), title=d['title'], desc=d['desc'], keywords=d['keywords'], active=file_for(slug),
                    body='\n\n  '.join(body), jsonld=ld, reveal=False)

    def page_factory(slug):
        def build():
            if slug == 'casestudies':
                return page_casestudies()
            if slug == 'blog':
                return page_blog()
            if slug in ('privacy', 'terms'):
                return page_legal(slug)
            ids = RETAIL_IDS if slug == 'retail-analytics' else None
            d, public, body = generic(slug, ids)
            if slug.startswith('blogs/'):
                return page_post(slug)
            if slug == 'faq':
                body = [fix_faq_links(x) for x in body]
            return finish(slug, d, body)
        build.__name__ = 'page_' + slug.replace('/', '_').replace('-', '_')
        return build

    def fix_faq_links(html):
        # the four "Explore" cards were whole-card links in the old markup
        if 'Retail analytics resources' not in html:
            return html
        parts = re.split(r'(?=<h3>)', html)
        out = [parts[0]]
        for k, ptxt in enumerate(parts[1:]):
            tgt = link(FAQ_LINKS[k], '') if k < len(FAQ_LINKS) else '#'
            m = re.match(r'<h3>(.*?)</h3>(.*)', ptxt, re.S)
            out.append(f'<h3><a href="{tgt}">{m.group(1)}</a></h3>' + m.group(2)) if m else out.append(ptxt)
        return ''.join(out)

    def cards_of(blocks):
        """Group index cards: each starts at an img block."""
        groups, cur = [], None
        for b in blocks:
            if b['t'] == 'img':
                cur = []
                groups.append(cur)
            elif cur is not None and b['t'] != 'h2' and not (b['t'] == 'line' and b['cls'] in ('eyebrow',)) and not (b['t'] == 'p' and b.get('ctx') == 'container' and cur and any(x.get('cls') == 'cs-stat' or x.get('cls') == 'blog-card-meta' for x in cur) and False):
                cur.append(b)
            if cur is not None and b['t'] == 'line' and b['cls'] in ('eyebrow',):
                cur = None
        return groups

    def page_casestudies():
        slug = 'casestudies'
        d = CONTENT[slug]
        public = public_for(slug)
        bl = [b for b in d['blocks'] if classify(b) != 'drop' or b['t'] == 'img']
        i1 = next(i for i, b in enumerate(bl) if b['t'] == 'h1')
        eyebrow = bl[i1 - 1]['html'] if bl[i1 - 1]['t'] == 'line' else ''
        lede = bl[i1 + 1]['html']
        hero = hero_shell(h.crumbs((None, 'Case studies')), eyebrow, bl[i1]['html'], lede)
        cards_blocks, k = [], i1 + 2
        cur = None
        tail = []
        for b in bl[k:]:
            if b['t'] == 'img':
                cur = []; cards_blocks.append(cur)
            elif b['t'] == 'line' and b['cls'] == 'eyebrow':
                cur = None; tail.append(b)
            elif cur is not None:
                cur.append(b)
            else:
                tail.append(b)
        cards = []
        for n, grp in enumerate(cards_blocks):
            tag = next(b for b in grp if b['t'] == 'line' and b.get('cls') == '')
            title = next(b for b in grp if b.get('cls') == 'blog-card-title')
            exc = next(b for b in grp if b['t'] == 'p')
            meta = next(b for b in grp if b.get('cls') == 'blog-card-meta')
            stats = [b for b in grp if b.get('cls') == 'cs-stat']
            cards.append(f'<a class="card post-card" href="{file_for(CASE_CARDS[n].strip("/"))}"><span class="kind">{" ".join(esc(x) for x in tag["parts"])}</span><h3>{title["html"]}</h3><p>{exc["html"]}</p>'
                         f'<p class="post-meta">{"".join(f"<span>{esc(x)}</span>" for x in meta["parts"])}</p>'
                         + '<div class="stats small">' + ''.join(f'<div><b>{esc(s["parts"][0])}</b><span>{esc(s["parts"][1])}</span></div>' for s in stats) + '</div></a>')
        body = [hero, f'<section class="block"><div class="wrap"><div class="post-grid">{"".join(cards)}</div></div></section>']
        for sec in sections(tail):
            if sec['h2'] or sec['eyebrow']:
                body.append(sec_html(sec, public))
        return finish(slug, d, body)

    def page_blog():
        slug = 'blog'
        d = CONTENT[slug]
        public = public_for(slug)
        bl = [b for b in d['blocks'] if classify(b) != 'drop' or b['t'] == 'img']
        i1 = next(i for i, b in enumerate(bl) if b['t'] == 'h1')
        eyebrow = bl[i1 - 1]['html']
        hero = hero_shell(h.crumbs((None, 'Blog')), eyebrow, bl[i1]['html'], bl[i1 + 1]['html'])
        groups, cur = [], None
        for b in bl[i1 + 2:]:
            if b['t'] == 'img':
                cur = []; groups.append(cur)
            elif cur is not None:
                cur.append(b)
        cards = []
        for n, grp in enumerate(groups):
            tag = next(b for b in grp if b.get('cls') == 'blog-tag'); title = next(b for b in grp if b.get('cls') == 'blog-card-title')
            exc = next(b for b in grp if b['t'] == 'p'); meta = next(b for b in grp if b.get('cls') == 'blog-card-meta')
            cards.append(f'<a class="card post-card" href="{file_for(BLOG_CARDS[n])}"><span class="kind">{tag["html"]}</span><h3>{title["html"]}</h3><p>{exc["html"]}</p>'
                         f'<p class="post-meta">{"".join(f"<span>{esc(x)}</span>" for x in meta["parts"])}</p></a>')
        body = [hero, f'<section class="block"><div class="wrap"><div class="post-grid">{"".join(cards)}</div></div></section>', h.cta_band('See Intelense on your own footage.')]
        return finish(slug, d, body)

    def page_post(slug):
        d = CONTENT[slug]
        public = public_for(slug)
        hero, rest = hero_split(d['blocks'])
        art = f'<section class="block"><div class="wrap prose">{fix_html(render_content([b for b in rest if classify(b) != "drop"], public), public)}</div></section>'
        return finish(slug, d, [hero_html(slug, hero, public), art])

    def page_legal(slug):
        d = CONTENT[slug]
        public = public_for(slug)
        bl = [b for b in d['blocks'] if classify(b) != 'drop']
        hero = [b for b in bl if b['t'] in ('h1',) or b.get('cls') in ('pp-hero-eyebrow', 'pp-hero-meta', 'pp-hero-desc')]
        toc = next(b for b in bl if b['t'] == 'ul')
        start = next(i for i, b in enumerate(bl) if b.get('cls') == 'pp-card-num')
        secs, cur = [], None
        for b in bl[start:]:
            if b['t'] == 'line' and b['cls'] == 'pp-card-num':
                cur = {'num': b['html'], 'h2': None, 'content': []}; secs.append(cur)
            elif b['t'] == 'h2' and cur and cur['h2'] is None:
                cur['h2'] = b['html']
            else:
                cur['content'].append(b)
        pre = 'section-' if slug == 'privacy' else 't'
        hero_blocks = hero
        pm = next(b for b in hero if b.get('cls') == 'pp-hero-meta')
        hh = hero_shell(h.crumbs((None, 'Privacy policy' if slug == 'privacy' else 'Terms of service')), next(b for b in hero if b.get('cls') == 'pp-hero-eyebrow')['html'],
                        next(b for b in hero if b['t'] == 'h1')['html'], next(b for b in hero if b.get('cls') == 'pp-hero-desc')['html'], f'<p class="post-meta"><span>{pm["html"]}</span></p>')
        toc_html = '<nav class="toc" aria-label="Contents"><b>Contents</b><ul>' + ''.join(f'<li>{fix_html(x, public)}</li>' for x in toc['items']) + '</ul></nav>'
        secs_html = ''.join(f'<section class="doc-sec" id="{pre}{n}"><span class="eyebrow">{s["num"]}</span><h2>{s["h2"]}</h2>{fix_html(render_content(s["content"], public), public)}</section>' for n, s in enumerate(secs, 1))
        body = [hh, f'<section class="block"><div class="wrap doc">{toc_html}<div class="doc-body">{secs_html}</div></div></section>']
        return finish(slug, d, body)

    return [page_factory(s) for s in SLUGS]
