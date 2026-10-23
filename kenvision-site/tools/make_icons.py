"""Favicons for kenvision.ai: the white K (with the blue tick) of the KenVision wordmark on a blue rounded square."""
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent.parent
src = Image.open(HERE.parent / 'site' / 'assets' / 'logos' / 'kenvision-light.png').convert('RGBA')
a = src.split()[3]
w, h = src.size
cols = [any(a.getpixel((x, y)) > 40 for y in range(h)) for x in range(w)]
x0 = cols.index(True)
x1 = x0
while x1 < w and cols[x1]:
    x1 += 1                      # first gap = end of the K
rows = [any(a.getpixel((x, y)) > 40 for x in range(x0, x1)) for y in range(h)]
y0, y1 = rows.index(True), len(rows) - rows[::-1].index(True)
k = src.crop((x0, y0, x1, y1))
# make the K white (the tick keeps its blue, so tint only the near-white pixels is not needed: use white everywhere on blue)
white = Image.new('RGBA', k.size, (255, 255, 255, 255))
white.putalpha(k.split()[3])


def tile(size, radius_ratio=0.22, pad=0.14):
    im = Image.new('RGBA', (size * 4, size * 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size * 4 - 1, size * 4 - 1), radius=int(size * 4 * radius_ratio), fill=(10, 52, 237, 255))
    box = int(size * 4 * (1 - 2 * pad))
    g = white.copy()
    g.thumbnail((box, box), Image.LANCZOS)
    im.alpha_composite(g, ((size * 4 - g.width) // 2, (size * 4 - g.height) // 2))
    return im.resize((size, size), Image.LANCZOS)


out = HERE / 'assets-src' / 'icons'
out.mkdir(parents=True, exist_ok=True)
for n, s in (('favicon-32.png', 32), ('favicon-48.png', 48), ('favicon-96.png', 96), ('icon-192.png', 192), ('icon-512.png', 512)):
    tile(s).save(out / n)
ap = Image.new('RGB', (180, 180), (10, 52, 237))
t = tile(180, 0, 0.14)
ap.paste(t, (0, 0), t)
ap.save(out / 'apple-touch-icon.png')
tile(256).save(out / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
print('icons written', k.size)
