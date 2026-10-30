"""Diagnostic for families.py: list every pair of videos from different channels that look like the same video
(same duration and a thumbnail dHash distance of 8 or less), so you can tune the matching by eye.
Columns: distance, seconds, thumbnail contrast, channel A, title A, channel B, title B. Low contrast (plain or
dark thumbnails) gives false matches. Writes research/related/vidpairs.json. Needs Pillow.
usage: python -I tools/vidpairs.py
"""
import collections, itertools, os, re, sys, warnings
warnings.filterwarnings('ignore')
from PIL import Image, ImageStat
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ytapi

reldir = ytapi.work('related')
rel = ytapi.load(os.path.join(reldir, 'related.json'))
name = {c: v['snippet']['title'] for c, v in ytapi.load(ytapi.work('channels.json')).items()}
def secs(d):
    m = re.fullmatch(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d or '')
    return None if not m else sum(int(x or 0) * k for x, k in zip(m.groups(), (86400, 3600, 60, 1)))
def feat(p):
    im = Image.open(p).convert('L'); w, h = im.size; im = im.crop((0, int(h * .14), w, int(h * .86)))
    sd = ImageStat.Stat(im).stddev[0]
    px = list(im.resize((9, 8)).getdata())
    return sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1]), sd
bydur = collections.defaultdict(list)
for v, info in rel['videos'].items():
    s = secs(info['dur'])
    if s and s >= 60:
        try: h, sd = feat(os.path.join(reldir, 'thumbs', v + '.jpg'))
        except Exception: continue
        bydur[s].append((info['ch'], h, sd, v, info['title']))
out = []
for s, items in bydur.items():
    for a, b in itertools.combinations(items + bydur.get(s + 1, []), 2):
        if a[0] != b[0]:
            d = bin(a[1] ^ b[1]).count('1')
            if d <= 8: out.append((d, s, round(min(a[2], b[2])), name.get(a[0], a[0]), a[4][:50], name.get(b[0], b[0]), b[4][:50]))
out.sort()
ytapi.save(out, os.path.join(reldir, 'vidpairs.json'))
for row in out[:40]: print(*row, sep=' | ')
print(len(out), 'pairs -> research/related/vidpairs.json')
