"""Step 2 of the history workflow: collect what links channels to each other.

For every channel in research/channels.json: featured channels, about-page branding, the latest 50 uploads with
their durations, and each upload's thumbnail. Writes research/related/related.json and research/related/thumbs/.
Costs roughly 3 units per channel plus 1 per 50 videos.
usage: python -I tools/fetch_related.py
"""
import concurrent.futures as cf, os, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ytapi

outdir = ytapi.work('related')
os.makedirs(os.path.join(outdir, 'thumbs'), exist_ok=True)
ids = sorted(ytapi.load(ytapi.work('channels.json')))
out = {'branding': ytapi.channels(ids, 'brandingSettings,contentDetails'), 'sections': {}, 'uploads': {}, 'videos': {}}
def per_channel(cid):
    sec = ytapi.api('channelSections', part='snippet,contentDetails', channelId=cid)
    return cid, sec, [x['contentDetails']['videoId'] for x in ytapi.uploads(cid)]
with cf.ThreadPoolExecutor(8) as ex:
    for cid, sec, vids in ex.map(per_channel, ids):
        out['sections'][cid] = [s.get('contentDetails', {}).get('channels', []) for s in sec.get('items', [])]
        out['uploads'][cid] = vids
allv = sorted({v for vs in out['uploads'].values() for v in vs})
def vbatch(chunk):
    return ytapi.api('videos', part='snippet,contentDetails', id=','.join(chunk), maxResults=50).get('items', [])
with cf.ThreadPoolExecutor(8) as ex:
    for items in ex.map(vbatch, [allv[i:i + 50] for i in range(0, len(allv), 50)]):
        for it in items:
            out['videos'][it['id']] = {'ch': it['snippet']['channelId'], 'title': it['snippet']['title'], 'dur': it['contentDetails'].get('duration', '')}
def thumb(v):
    p = os.path.join(outdir, 'thumbs', v + '.jpg')
    if not os.path.exists(p):
        try: open(p, 'wb').write(urllib.request.urlopen(f'https://i.ytimg.com/vi/{v}/default.jpg', timeout=20).read())
        except Exception: pass
with cf.ThreadPoolExecutor(16) as ex: list(ex.map(thumb, out['videos']))
ytapi.save(out, os.path.join(outdir, 'related.json'))
print('channels', len(ids), 'videos', len(out['videos']), 'thumbs', len(os.listdir(os.path.join(outdir, 'thumbs'))))
print(ytapi.quota())
