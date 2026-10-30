# Shared helpers for the research tools: API key, YouTube Data API v3 calls, your Takeout watch history,
# and the channels already in your own lists (networks/*.md in your folder). The other scripts import this file.
import collections, concurrent.futures as cf, glob, json, os, re, sys, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Your folder: research/ (your Takeout export and every output), networks/ (lists you add) and .yt_api_key.
# In a clone it is the repository itself (git ignores research/ and the key); the plugin sets YKB_HOME to its data folder.
HOME = os.environ.get('YKB_HOME') or ROOT
WORK = os.path.join(HOME, 'research')
NETWORK_DIRS = list(dict.fromkeys([os.path.join(ROOT, 'networks'), os.path.join(HOME, 'networks')]))
os.makedirs(WORK, exist_ok=True)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
CHANNEL_ID = re.compile(r'\bUC[\w-]{22}\b')

def work(*p): return os.path.join(WORK, *p)
def load(path): return json.load(open(path, encoding='utf-8'))
def save(obj, path, indent=None): json.dump(obj, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=indent)

_key = None
def key():
    global _key
    if not _key:
        files = [os.path.join(d, '.yt_api_key') for d in (HOME, ROOT, os.path.expanduser('~'))]
        _key = os.environ.get('YT_API_KEY') or next((open(p).read().strip() for p in files if os.path.exists(p)), '')
        if not _key: sys.exit(f'No API key. Put it in a file named .yt_api_key in {HOME} (or your home folder), or set YT_API_KEY.')
    return _key

units = collections.Counter()   # quota used, per endpoint: 10,000 units a day; search costs 100, most calls 1
def api(ep, cost=1, **p):
    units[ep] += cost
    url = f'https://www.googleapis.com/youtube/v3/{ep}?' + urllib.parse.urlencode({**p, 'key': key()})
    try: return json.load(urllib.request.urlopen(url, timeout=30))
    except urllib.error.HTTPError as e:
        try: msg = json.load(e).get('error', {}).get('message', '')
        except Exception: msg = ''
        if e.code == 403 and 'quota' in msg.lower(): sys.exit('Daily API quota used up. Try again tomorrow.')
        return {'_error': f'{e.code} {msg}'}

def channels(ids, part='snippet,statistics,status'):
    ids, res = sorted(set(ids)), {}
    for i in range(0, len(ids), 50):
        for it in api('channels', part=part, id=','.join(ids[i:i + 50]), maxResults=50).get('items', []): res[it['id']] = it
    return res

def featured(cid):
    return {o for s in api('channelSections', part='contentDetails', channelId=cid).get('items', [])
            for o in s.get('contentDetails', {}).get('channels', []) if o != cid}

def featured_many(ids):
    with cf.ThreadPoolExecutor(8) as ex: return dict(zip(ids, ex.map(featured, ids)))

def uploads(cid, n=50, part='contentDetails'):
    return api('playlistItems', part=part, playlistId='UU' + cid[2:], maxResults=n).get('items', [])

def resolve(x):
    """Channel ID from 'UC…', 'v:<videoId>', '@handle' or a youtube.com / youtubekids.com link."""
    x = x.strip()
    if m := CHANNEL_ID.search(x): return m.group()
    if m := re.search(r'(?:v=|youtu\.be/|/watch/)([\w-]{11})', x): x = 'v:' + m.group(1)
    if x.startswith('v:'):
        items = api('videos', part='snippet', id=x[2:]).get('items', [])
        return items[0]['snippet']['channelId'] if items else sys.exit(f'Video not found: {x[2:]}')
    if m := re.search(r'@[\w.-]+', x):
        items = api('channels', part='id', forHandle=m.group()).get('items', [])
        return items[0]['id'] if items else sys.exit(f'Handle not found: {m.group()}')
    sys.exit(f'Not a channel ID, v:<videoId>, @handle or link: {x}')

def subs(c): return int(c.get('statistics', {}).get('subscriberCount') or 0)
def videos(c): return int(c.get('statistics', {}).get('videoCount') or 0)
def text(c):
    """What a channel says about itself. Keywords are left out: they often name other brands for search traffic."""
    return c.get('snippet', {}).get('description', '') + ' ' + c.get('brandingSettings', {}).get('channel', {}).get('description', '')

def history(required=False):
    """Your child's watch history from a Google Takeout export (JSON format) anywhere under research/."""
    found = glob.glob(work('**', 'watch-history.json'), recursive=True)
    if found: return load(found[0])
    if required: sys.exit('No watch-history.json under research/. Export it from takeout.google.com (YouTube, history, JSON format) and unzip it there.')
    return None

def watched_channel(entry):
    s = (entry.get('subtitles') or [{}])[0]
    return s.get('url', '').rsplit('/', 1)[-1] if '/channel/' in s.get('url', '') else ''

def view_counts(h): return collections.Counter(watched_channel(e) for e in h or [] if watched_channel(e))

def known_networks():
    """{channel ID: (network file, network title, 'main' or 'optional')} for every channel in networks/*.md."""
    res = {}
    for f in sorted(f for d in NETWORK_DIRS for f in glob.glob(os.path.join(d, '*.md')) if os.path.basename(f).lower() != 'readme.md'):
        stem, title, part = os.path.basename(f)[:-3], '', 'main'
        for line in open(f, encoding='utf-8'):
            if line.startswith('# Network:'): title = line[10:].strip()
            elif line.startswith('## '): part = 'optional' if line.lower().startswith('## optional') else 'main'
            elif m := re.match(r'\d+\.\s.*?\|\s*(UC[\w-]{22})\s*\|', line): res.setdefault(m.group(1), (stem, title or stem, part))
    return res

def quota(): return f"API units used: {sum(units.values())} ({', '.join(f'{k} {v}' for k, v in sorted(units.items()))})"
