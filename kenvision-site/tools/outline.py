"""Print a compact outline (headings, text, images, links) of an old KenVision page."""
import sys, re, html
from html.parser import HTMLParser

class P(HTMLParser):
    def __init__(s):
        super().__init__(convert_charrefs=True); s.out=[]; s.buf=''; s.skip=0; s.tag=None
    def flush(s):
        t=re.sub(r'\s+',' ',s.buf).strip()
        if t: s.out.append((s.tag or 'txt', t))
        s.buf=''
    def handle_starttag(s,t,a):
        a=dict(a)
        if t in('script','style','svg'): s.skip+=1; return
        if s.skip: return
        if t in('h1','h2','h3','h4','h5','p','li','section','summary','a','button','span','div','small','em','strong','label'):
            if t in('h1','h2','h3','h4','h5','p','li','summary','section','label'): s.flush(); s.tag=t
            if t=='section': s.out.append(('SECTION',(a.get('class') or '')+' '+(a.get('id') or '')))
        if t=='img': s.out.append(('IMG',a.get('src')+' | '+(a.get('alt') or '')))
        if t=='a' and a.get('href'): s.buf+=f' [{a["href"]}] '
    def handle_endtag(s,t):
        if t in('script','style','svg'): s.skip=max(0,s.skip-1); return
        if t in('h1','h2','h3','h4','h5','p','li','summary','label'): s.flush(); s.tag=None
    def handle_data(s,d):
        if not s.skip: s.buf+=d
src=open(sys.argv[1],encoding='utf-8').read()
src=src[src.find('<body'):]
p=P(); p.feed(src); p.flush()
for k,v in p.out: print(f'{k}: {v}')
