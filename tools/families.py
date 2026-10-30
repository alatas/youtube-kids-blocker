"""Step 3 of the history workflow: group the channels your child watches into families (same publisher).

Two channels are linked when they share a website, contact email or social-media page in their descriptions,
upload the same videos (same duration and a near-identical thumbnail, at least twice), or feature each other.
Similar names are listed as hints only. Needs Pillow (pip install -r tools/requirements.txt).
Reads research/channels.json and research/related/; writes research/families.json.
usage: python -I tools/families.py
"""
import collections, itertools, os, re, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ytapi

reldir = ytapi.work('related')
ch = ytapi.load(ytapi.work('channels.json'))
rel = ytapi.load(os.path.join(reldir, 'related.json'))
name = {c: v['snippet']['title'] for c, v in ch.items()}
parent = {c: c for c in ch}
def find(x):
    while parent[x] != x: parent[x] = parent[parent[x]]; x = parent[x]
    return x
ev = collections.defaultdict(set)   # (a,b) -> evidence strings
def link(a, b, why):
    if a == b or a not in ch or b not in ch: return
    ev[tuple(sorted((a, b)))].add(why); parent[find(a)] = find(b)

# A. featured channels
feat = set()
outside = collections.defaultdict(set)  # watched channel -> featured channels not in the history
for c, secs in rel['sections'].items():
    for lst in secs:
        for o in lst:
            if o in ch: feat.add((c, o))
            elif o != c: outside[c].add(o)

# B. shared websites / emails in descriptions
SKIP = {'gmail.com', 'hotmail.com', 'outlook.com', 'yahoo.com', 'icloud.com', 'mail.ru', 'yandex.ru', 'yandex.com', 'qq.com', '163.com', 'naver.com', 'onelink.me', 'youtube.com', 'youtu.be', 'www.youtube.com', 'bit.ly', 'goo.gl', 'linktr.ee'}
def tokens(d):
    t = set(m.lower() for m in re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', d))
    d = re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+', ' ', d)
    for host, path in re.findall(r'(?:https?://)?((?:[\w-]+\.)+(?:com|net|org|tv|io|co|ru|de|tr|uk|in|id|fr|es|it|jp|kr|cn|me|app|kids)(?:\.\w\w)?)(/[\w.-]*)?', d, re.I):
        host = host.lower().removeprefix('www.')
        if host in SKIP: continue
        social = any(s in host for s in ('instagram', 'facebook', 'tiktok', 'twitter', 'x.com', 'pinterest'))
        if social:
            if path and len(path) > 2: t.add(host + path.lower().rstrip('/'))
        else: t.add(host)
    return t
tok = {c: tokens(v['snippet'].get('description', '') + ' ' + rel['branding'].get(c, {}).get('brandingSettings', {}).get('channel', {}).get('description', '')) for c, v in ch.items()}
bytok = collections.defaultdict(set)
for c, ts in tok.items():
    for t in ts: bytok[t].add(c)
for t, cs in bytok.items():
    if 2 <= len(cs) <= 25:
        for a, b in itertools.combinations(sorted(cs), 2): link(a, b, 'same link: ' + t)

# C. same video re-uploaded / dubbed: same duration (>=60s) + near-identical thumbnail
def secs(d):
    m = re.fullmatch(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', d or '')
    return None if not m else sum(int(x or 0) * k for x, k in zip(m.groups(), (86400, 3600, 60, 1)))
def dhash(p):
    try: im = Image.open(p).convert('L')
    except Exception: return None
    w, h = im.size; im = im.crop((0, int(h * .14), w, int(h * .86))).resize((9, 8))   # crop the letterbox bars
    px = list(im.get_flattened_data()) if hasattr(im, 'get_flattened_data') else list(im.getdata())
    return sum(1 << i for i in range(64) if px[(i // 8) * 9 + i % 8] > px[(i // 8) * 9 + i % 8 + 1])
bydur = collections.defaultdict(list)
for v, info in rel['videos'].items():
    s = secs(info['dur'])
    if s and s >= 60:
        h = dhash(os.path.join(reldir, 'thumbs', v + '.jpg'))
        if h is not None: bydur[s].append((info['ch'], h, v))
pairs = collections.Counter()
for s, items in bydur.items():
    near = items + bydur.get(s + 1, [])
    for (c1, h1, _), (c2, h2, _) in itertools.combinations(near, 2):
        d = bin(h1 ^ h2).count('1')
        if c1 != c2 and (d == 0 or (d <= 3 and s >= 90)): pairs[tuple(sorted((c1, c2)))] += 1
for (a, b), n in pairs.items():
    if n >= 2: link(a, b, f'{n} identical videos')

strong = set(ev)
for a, b in feat:
    k = tuple(sorted((a, b)))
    if (b, a) in feat or k in strong: link(a, b, 'feature each other' if (b, a) in feat else 'featured channel')

# D. similar names (shown as a hint only, not used to merge)
LANG = set('türkçe turkce english español espanol italiano indonesian indonesia deutsch français francais português portugues русский 中文 日本語 한국어 arabic العربية hindi tv kids official resmi kanal channel for the - – & and jr.'.split())
def core(n): return frozenset(w for w in re.findall(r'\w+', n.lower()) if w not in LANG and len(w) > 2)
hints = []
for a, b in itertools.combinations(sorted(ch), 2):
    ca, cb = core(name[a]), core(name[b])
    if ca and cb and (ca <= cb or cb <= ca) and find(a) != find(b): hints.append((name[a], name[b]))

fam = collections.defaultdict(list)
for c in ch: fam[find(c)].append(c)
groups = [sorted(m, key=lambda c: name[c].lower()) for m in fam.values() if len(m) > 1]
res = {'groups': [{'members': g, 'evidence': sorted({f'{name[a]} ↔ {name[b]}: ' + '; '.join(sorted(w)) for (a, b), w in ev.items() if a in g and b in g})} for g in groups],
       'outside': {c: sorted(s) for c, s in outside.items()}, 'name_hints': hints}
ytapi.save(res, ytapi.work('families.json'), indent=1)
print('families', len(groups), 'channels in families', sum(map(len, groups)), 'name hints', len(hints),
      'featured but not watched', len({o for s in outside.values() for o in s}))
for g in sorted(groups, key=len, reverse=True)[:25]: print(len(g), ' | '.join(name[c] for c in g)[:230])
print('--hints'); [print(' ', a, '~', b) for a, b in hints[:30]]
