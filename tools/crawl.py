"""Find a publisher's network of sister channels.

Starts from seed channels (and optional channel searches), then follows each channel's "featured channels"
breadth-first. A channel joins when its own description names the publisher (the signature regex), or when it
is a seed whose title matches. Copycats under 1,000 subscribers, empty channels and "- Topic" channels are dropped.
With --loose, channels that feature each other with a member, or are featured by 3+ members, also join, marked
unconfirmed: use it for publishers whose descriptions are empty (e.g. Emma And Joey), and check them by hand.

usage:   python -I tools/crawl.py <out.json> "<signature regex>" <seeds> ["search 1|search 2"] [--loose]
seeds:   comma-separated channel IDs, v:<videoId>, @handles or links
example: python -I tools/crawl.py research/foo.json "foo studio|foostudio.com" UCxxxxxxxxxxxxxxxxxxxxxx "Foo Studio"
Search costs 100 quota units per query (daily quota 10,000); everything else ~1 unit per call.
"""
import collections, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ytapi

loose = '--loose' in sys.argv
args = [a for a in sys.argv[1:] if a != '--loose']
if len(args) < 3: sys.exit(__doc__)
out, sig = args[0], re.compile(args[1], re.I)
seeds = {ytapi.resolve(s) for s in args[2].split(',') if s.strip()}
queries = [q for q in (args[3] if len(args) > 3 else '').split('|') if q.strip()]

info, feats, why, name_only = {}, {}, collections.defaultdict(set), {}
def fetch(ids): info.update(ytapi.channels([i for i in ids if i not in info], 'snippet,statistics,status,brandingSettings'))
def fetch_feats(ids): feats.update(ytapi.featured_many([i for i in ids if i not in feats]))
def ok(c): return ytapi.subs(c) >= 1000 and ytapi.videos(c) > 0 and not c['snippet']['title'].endswith(' - Topic')
def title(cid): return info.get(cid, {}).get('snippet', {}).get('title', cid)

queue = set(seeds)
for q in queries:
    queue |= {i['snippet']['channelId'] for i in ytapi.api('search', cost=100, part='snippet', q=q, type='channel', maxResults=50).get('items', [])}
net, seen = set(), set()
for rnd in range(8):
    new = queue - seen
    if not new: break
    seen |= new; fetch(new); queue = set(); added = set()
    for cid in new:
        c = info.get(cid)
        if not c: continue
        if sig.search(ytapi.text(c)): why[cid].add('description names the publisher')
        elif cid in seeds and sig.search(c['snippet']['title']): why[cid].add('seed, name matches')
        elif sig.search(c['snippet']['title']) and ytapi.subs(c) >= 1000: name_only[cid] = c
        if why[cid] and ok(c): added.add(cid)
    if loose:
        fetch_feats(net | added)
        cands = {o for c in net | added for o in feats[c]} - net - added
        fetch(cands); fetch_feats(cands)
        for o in cands:
            by = {c for c in net | added if o in feats[c]}
            why[o] = {w for w in why[o] if not w.startswith(('features each other', 'featured by'))}
            if back := by & feats[o]: why[o].add('features each other with ' + ', '.join(sorted(map(title, back)))[:200])
            if len(by) >= 3: why[o].add(f'featured by {len(by)} network channels')
            if why[o] and o in info and ok(info[o]): added.add(o)
    fetch_feats(added)
    net |= added
    queue = {o for c in added for o in feats[c]}
    print(f'round {rnd}: {len(net)} channels', file=sys.stderr)
    if len(net) > 1500: print('Stopped at 1,500 channels: the signature is probably too broad.', file=sys.stderr); break

known, views = ytapi.known_networks(), ytapi.view_counts(ytapi.history())
rows = []
for cid in net:
    c = info[cid]; s = c['snippet']
    rows.append(dict(id=cid, name=s['title'].strip(), country=s.get('country', ''), subs=ytapi.subs(c), videos=ytapi.videos(c),
                     mfk=c.get('status', {}).get('madeForKids'), confirmed=bool(sig.search(ytapi.text(c))), why=sorted(why[cid]),
                     known=known.get(cid, ('',))[0], views=views.get(cid, 0)))
rows.sort(key=lambda r: (r['mfk'] is False, not r['confirmed'], -r['subs']))
ytapi.save(rows, out, indent=1)
print(f"{'views':>5} {'subs':>9} {'kids':5} {'cc':3} {'videos':>6} {'ok':3} channel   [already in networks/]")
for r in rows:
    print(f"{r['views']:>5} {r['subs']:>9} {str(r['mfk']):5} {r['country']:3} {r['videos']:>6} {'yes' if r['confirmed'] else 'no':3} {r['id']} {r['name']}"
          + (f"  [{r['known']}]" if r['known'] else ''))
print(f'{len(rows)} channels, {sum(r["confirmed"] for r in rows)} confirmed by description -> {out}')
print('Name-only matches, not included (check by hand):')
for c in sorted(name_only.values(), key=ytapi.subs, reverse=True)[:25]:
    if c['id'] not in net: print(f"   {ytapi.subs(c):>9} {c['id']} {c['snippet']['title']}")
print(ytapi.quota())
