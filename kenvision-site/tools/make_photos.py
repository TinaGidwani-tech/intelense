"""Download the Pexels photos used for the solution visuals, crop them and write assets/photos/*.webp.
All photos are free to use under the Pexels licence (pexels.com/license). Run: python3 kenvision-site/tools/make_photos.py
name: (Pexels photo id, aspect, vertical bias 0..1, horizontal bias 0..1)"""
import io
import sys
import urllib.request
from pathlib import Path
from PIL import Image

OUT = Path(__file__).resolve().parent.parent / 'assets' / 'photos'
W = 1600
PHOTOS = {
    # one visual per solution (16:9, overlays are drawn on a 1280x720 canvas over these crops)
    'retail-aisle': (38079866, 16 / 9, .5, .5), 'building-atrium': (36064155, 16 / 9, .5, .5),
    'city-station': (32819765, 16 / 9, .5, .5), 'surveillance-yard': (4483556, 16 / 9, .5, .5),
    # scale picture per solution (4:3)
    'scale-retail': (17574590, 4 / 3, .5, .5), 'scale-building': (37320179, 4 / 3, .4, .5),
    'scale-city': (5231181, 4 / 3, .5, .5), 'scale-yard': (35501718, 4 / 3, .5, .5),
    # before/after slider
    'slider-mall': (4254891, 16 / 9, .5, .5), 'slider-street': (10661529, 16 / 9, .5, .5),
    # how it works: capture, processing, outputs
    'how-feed': (39609039, 16 / 9, .5, .5), 'how-read': (8311880, 16 / 9, .5, .5), 'how-dash': (577210, 16 / 9, .5, .5),
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (pid, ar, vb, hb) in PHOTOS.items():
        url = f'https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg?auto=compress&cs=tinysrgb&w=2000'
        im = Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read())).convert('RGB')
        w, h = im.size
        tw, th = (w, round(w / ar)) if w / h < ar else (round(h * ar), h)
        x, y = round((w - tw) * hb), round((h - th) * vb)
        im = im.crop((x, y, x + tw, y + th)).resize((W, round(W / ar)), Image.LANCZOS)
        im.save(OUT / f'{name}.webp', quality=80, method=6)
        print(name, pid, im.size, (OUT / f'{name}.webp').stat().st_size // 1024, 'KB')
    (OUT / 'CREDITS.md').write_text('# Photo credits\n\nPhotos from Pexels (https://www.pexels.com), used under the Pexels licence.\n\n'
                                    + ''.join(f'- {n}: https://www.pexels.com/photo/{p}/\n' for n, (p, *_r) in PHOTOS.items()))


if __name__ == '__main__':
    sys.exit(main())
