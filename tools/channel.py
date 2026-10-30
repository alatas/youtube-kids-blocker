"""Look up one channel: who runs it, what it uploads, which channels it features, and whether it is already in
one of the networks/*.md lists. If your Takeout export is in research/, it also shows how often your child
watched it. Use this on a channel you spotted in your child's history before you start a crawl.

usage:   python -I tools/channel.py <channel ID | v:videoId | @handle | YouTube link>
example: python -I tools/channel.py v:jNQXAC9IVRw
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ytapi

if len(sys.argv) < 2: sys.exit(__doc__)
cid = ytapi.resolve(sys.argv[1])
c = ytapi.channels([cid], 'snippet,statistics,status,brandingSettings').get(cid) or sys.exit(f'Channel not found: {cid}')
s, st = c['snippet'], c['statistics']
print(f"{s['title']} | {cid} | {s.get('customUrl', '')} | {s.get('country', '')} | since {s.get('publishedAt', '')[:10]}")
print(f"{ytapi.subs(c):,} subscribers, {ytapi.videos(c):,} videos, {int(st.get('viewCount') or 0):,} views, made for kids: {c['status'].get('madeForKids')}")
print(f"https://www.youtubekids.com/channel/{cid}\n")
print(s.get('description', '')[:1200] or '(no description)')
print('\nKeywords:', c.get('brandingSettings', {}).get('channel', {}).get('keywords', '')[:250])

known = ytapi.known_networks()
print('\nAlready listed:', f'networks/{known[cid][0]}.md ({known[cid][2]} list)' if cid in known else 'no')
fams = ytapi.work('families.json')
if os.path.exists(fams):
    for g in ytapi.load(fams)['groups']:
        if cid in g['members']: print('Family (research/families.json):', json.dumps(g['evidence'], ensure_ascii=False)[:900])

h = ytapi.history()
if h is not None:
    seen = [e for e in h if ytapi.watched_channel(e) == cid]
    print(f'Watched {len(seen)} times in your Takeout history')
    for e in seen[:6]: print('  ', e['time'][:10], e.get('title', '').removeprefix('Watched ')[:80])

up = ytapi.uploads(cid, 15, 'snippet')
print('\nLatest uploads:')
for i in up: print('  ', i['snippet']['title'][:95])
if up: print('Newest video description:', up[0]['snippet']['description'][:500])

feat = ytapi.featured(cid)
if feat:
    print('\nFeatured channels:')
    for f, x in sorted(ytapi.channels(list(feat)[:50]).items(), key=lambda kv: -ytapi.subs(kv[1])):
        tag = f'  [{known[f][0]}]' if f in known else ''
        print(f"   {f} {x['snippet']['title']} | {ytapi.subs(x):,} subs | kids {x['status'].get('madeForKids')} | {x['snippet'].get('country', '')}{tag}")
print('\n' + ytapi.quota())
