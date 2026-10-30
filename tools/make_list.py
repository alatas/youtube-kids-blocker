"""Turn a crawl result into a draft networks/<name>.md file in the repository's format (see CONTRIBUTING.md).

Main list: channels made for kids, or unknown. Optional list: channels not marked "made for kids".
Each line gets the channel's newest upload as its test video. Unconfirmed channels (from --loose) are left
out unless you add --include-unconfirmed; check those by hand with channel.py first.
The draft is written to research/; review it, fill in the header (CONTRIBUTING.md -> "List format"),
then copy it to networks/ in your folder.

usage:   python -I tools/make_list.py <crawl.json> "<Publisher name>" [--include-unconfirmed]
example: python -I tools/make_list.py research/foo.json "Foo Studio"
"""
import datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ytapi

args = [a for a in sys.argv[1:] if not a.startswith('--')]
if len(args) < 2: sys.exit(__doc__)
src, publisher = args
rows = [r for r in ytapi.load(src) if r['confirmed'] or '--include-unconfirmed' in sys.argv]
skipped = [r for r in ytapi.load(src) if r not in rows]

def short(n):
    if n >= 1_000_000: return f'{n / 1e6:.1f}'.rstrip('0').rstrip('.') + 'M'
    return f'{round(n / 1000)}K' if n >= 1000 else str(n)
def newest(cid):
    items = ytapi.uploads(cid, 1)
    return items[0]['contentDetails']['videoId'] if items else ''

main = sorted((r for r in rows if r['mfk'] is not False), key=lambda r: -r['subs'])
optional = sorted((r for r in rows if r['mfk'] is False), key=lambda r: -r['subs'])
today = datetime.date.today().isoformat()
lines = [f'# Network: {publisher}', '',
         f'- **Publisher:** {publisher} (TODO: company, or "a family channel" / "a creator"; country as YouTube lists it; company website or company-domain email only)',
         '- **What it is:** TODO (what the videos show; quote real titles; no names of children, no verdicts like "clickbait")',
         '- **Why block it:** TODO (the practical reason to block the whole network, e.g. many sister channels or the same videos in many languages)', '',
         f'## Main list: channels for kids ({len(main)})', '']
n = 0
for title, part in (('', main), (f'## Optional list: channels not marked "made for kids" ({len(optional)})', optional)):
    if not part: continue
    if title: lines += ['', title, '']
    for r in part:
        n += 1
        lines.append(f"{n}. {r['name']} | {r['id']} | https://www.youtubekids.com/channel/{r['id']} | {r['country']} | {short(r['subs'])} subscribers | {newest(r['id'])}")
lines += ['', f'*List made {today} from public YouTube data (YouTube Data API v3). It\'s not affiliated with or endorsed by YouTube or {publisher}.*', '']

out = os.path.splitext(src)[0] + '-draft.md'
open(out, 'w', encoding='utf-8').write('\n'.join(lines))
print(f'{len(main)} main + {len(optional)} optional channels -> {out}')
print('Next: fill in the TODOs (only the fields already in the draft; no notes on how the list was made), copy it to networks/ in your folder,'
      ' then run: python -I tools/check_networks.py <that file>')
print('Keep it factual: no names of children or private adults, no personal emails, no guesses about people.'
      ' The list stays on your computer.')
if skipped:
    print(f'Left out {len(skipped)} unconfirmed channels (check with channel.py, then rerun with --include-unconfirmed or add them by hand):')
    for r in skipped: print(f"   {r['id']} {r['name']}  ({'; '.join(r['why'])})")
print(ytapi.quota())
