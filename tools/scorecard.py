"""Step 4 of the history workflow: a spreadsheet to decide, channel by channel, what to keep and what to block.

Sheets: Summary, Scorecard (every channel your child watched, with yellow cells for your ratings and a
Keep/Block/Maybe decision), Families, Known networks (watched channels that are already in networks/*.md),
Not watched yet (sister channels promoted by channels your child watches) and All views.
Times are shown in this computer's time zone. Needs openpyxl (pip install -r tools/requirements.txt).
Reads research/: the Takeout watch history (and subscriptions.csv if present), channels.json, families.json.
Writes research/scorecard.xlsx. It stays on your computer; never commit it.
usage: python -I tools/scorecard.py
"""
import collections, csv, glob, os, re, sys
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.utils import get_column_letter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ytapi

hist = ytapi.history(required=True)
info = ytapi.load(ytapi.work('channels.json'))
fams = ytapi.load(ytapi.work('families.json')) if os.path.exists(ytapi.work('families.json')) else {'groups': [], 'outside': {}}
subfile = glob.glob(ytapi.work('**', 'subscriptions.csv'), recursive=True)
subscribed = {r['Channel Title'] for r in csv.DictReader(open(subfile[0], encoding='utf-8')) if r.get('Channel Title')} if subfile else set()
known = ytapi.known_networks()
def num(v): return int(v) if v not in (None, '') else None
def cid(url): return url.rsplit('/', 1)[-1] if '/channel/' in url else ''
def local(ts):   # Takeout time (UTC) -> this computer's time zone, without fractional seconds
    return datetime.fromisoformat(re.sub(r'\.\d+', '', ts).replace('Z', '+00:00')).astimezone().replace(tzinfo=None)

rows = []
for x in hist:
    s = (x.get('subtitles') or [{}])[0]
    title = x.get('title', '')
    if title.startswith('Watched '): title = title[8:]
    rows.append((s.get('name', '(unknown / removed video)'), s.get('url', ''), title, local(x['time']), x.get('titleUrl', '')))

ch = collections.defaultdict(lambda: {'n': 0, 'first': None, 'last': None, 'url': '', 'titles': collections.Counter()})
for name, url, title, t, _ in rows:
    c = ch[name]; c['n'] += 1; c['url'] = c['url'] or url; c['titles'][title] += 1
    c['first'] = min(c['first'] or t, t); c['last'] = max(c['last'] or t, t)
order = sorted(ch.items(), key=lambda kv: (-kv[1]['n'], kv[0].lower()))
views_by_id = {cid(c['url']): c['n'] for _, c in order}
name_by_id = {cid(c['url']): n for n, c in order}

# family label = the known network it belongs to, else its most-watched member
families = []
for g in fams['groups']:
    members = sorted(g['members'], key=lambda i: -views_by_id.get(i, 0))
    nets = sorted({known[m][1] for m in members if m in known})
    families.append([nets[0] if len(nets) == 1 else name_by_id.get(members[0], members[0]), members, g['evidence']])
# watched channels that are in a known network but in no family join that network's family
in_family = {m for f in families for m in f[1]}
for m in views_by_id:
    if m in known and m not in in_family:
        f = next((f for f in families if f[0] == known[m][1]), None)
        if f: f[1].append(m)
        else: families.append([known[m][1], [m], [f'listed in networks/{known[m][0]}.md']])
families.sort(key=lambda f: -sum(views_by_id.get(m, 0) for m in f[1]))
family_of = {m: label for label, members, _ in families for m in members}

F = 'Arial'
norm = Font(name=F); bold = Font(name=F, bold=True); hdr_font = Font(name=F, bold=True, color='FFFFFF')
hdr_fill = PatternFill('solid', fgColor='305496'); inp_fill = PatternFill('solid', fgColor='FFF2CC')
inp_font = Font(name=F, color='0000FF'); link_font = Font(name=F, color='0563C1', underline='single')
block_fill = PatternFill('solid', fgColor='F8CBAD'); keep_fill = PatternFill('solid', fgColor='C6EFCE')

def header(ws, heads, widths):
    ws.append(heads)
    for cell in ws[1]:
        cell.font = hdr_font; cell.fill = hdr_fill; cell.alignment = Alignment(wrap_text=True, vertical='center')
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[1].height = 32
def hyperlink(cell, url):
    if url: cell.value = 'open'; cell.hyperlink = url; cell.font = link_font
def listed(i): return f'{known[i][0]} ({known[i][2]})' if i in known else ''

wb = Workbook()

# --- Scorecard ---
ws = wb.active; ws.title = 'Scorecard'
cols = ['Rank', 'Channel', 'Family', 'In networks/ list', 'Views', 'Family views', 'Share of views', 'First watched', 'Last watched',
        'Days between', 'Subscribed', 'Most watched video', 'Channel link', 'Country', 'Subscribers',
        'Videos on channel', 'Made for kids', 'Topics', 'Channel since', 'Description',
        'Educational (1-5)', 'Calm pace (1-5)', 'Language OK (1-5)', 'Score', 'Decision']
L = {h: get_column_letter(i) for i, h in enumerate(cols, 1)}
header(ws, cols, [6, 38, 26, 18, 8, 9, 9, 17, 17, 9, 10, 50, 8, 8, 12, 10, 9, 28, 12, 60, 12, 12, 12, 8, 11])
last = len(order) + 1
V, FAM, SC, LST = L['Views'], L['Family'], L['Score'], L['In networks/ list']
E1, E3, DEC = L['Educational (1-5)'], L['Language OK (1-5)'], L['Decision']
for r, (name, c) in enumerate(order, start=2):
    i = cid(c['url'])
    it = info.get(i, {}); sn = it.get('snippet', {}); st = it.get('statistics', {})
    mfk = it.get('status', {}).get('madeForKids')
    topics = ', '.join(t.rsplit('/', 1)[-1].replace('_', ' ') for t in it.get('topicDetails', {}).get('topicCategories', []))
    vals = {
        'Rank': r - 1, 'Channel': name, 'Family': family_of.get(i, ''), 'In networks/ list': listed(i), 'Views': c['n'],
        'Family views': f'=IF({FAM}{r}="",{V}{r},SUMIFS(${V}$2:${V}${last},${FAM}$2:${FAM}${last},{FAM}{r}))',
        'Share of views': f'={V}{r}/SUM(${V}$2:${V}${last})',
        'First watched': c['first'], 'Last watched': c['last'],
        'Days between': f'=INT({L["Last watched"]}{r})-INT({L["First watched"]}{r})+1',
        'Subscribed': 'Yes' if name in subscribed else '', 'Most watched video': c['titles'].most_common(1)[0][0],
        'Country': sn.get('country', ''),
        'Subscribers': None if st.get('hiddenSubscriberCount') else num(st.get('subscriberCount')),
        'Videos on channel': num(st.get('videoCount')), 'Made for kids': {True: 'Yes', False: 'No'}.get(mfk, ''),
        'Topics': topics, 'Channel since': sn.get('publishedAt', '')[:10],
        'Description': ' '.join(sn.get('description', '').split())[:300],
        'Score': f'=IF(COUNT({E1}{r}:{E3}{r})=0,"",AVERAGE({E1}{r}:{E3}{r}))',
    }
    ws.append([vals.get(h) for h in cols])
    for cell in ws[r]: cell.font = norm
    hyperlink(ws[f'{L["Channel link"]}{r}'], c['url'])
    ws[f'{L["Share of views"]}{r}'].number_format = '0.0%'
    ws[f'{L["First watched"]}{r}'].number_format = ws[f'{L["Last watched"]}{r}'].number_format = 'yyyy-mm-dd hh:mm'
    ws[f'{L["Days between"]}{r}'].number_format = '0'
    ws[f'{L["Subscribers"]}{r}'].number_format = ws[f'{L["Videos on channel"]}{r}'].number_format = '#,##0'
    ws[f'{SC}{r}'].number_format = '0.0'
    for h in ('Educational (1-5)', 'Calm pace (1-5)', 'Language OK (1-5)', 'Decision'):
        ws[f'{L[h]}{r}'].fill = inp_fill; ws[f'{L[h]}{r}'].font = inp_font
score_dv = DataValidation(type='whole', operator='between', formula1='1', formula2='5', allow_blank=True)
dec_dv = DataValidation(type='list', formula1='"Keep,Block,Maybe"', allow_blank=True)
ws.add_data_validation(score_dv); ws.add_data_validation(dec_dv)
score_dv.add(f'{E1}2:{E3}{last}'); dec_dv.add(f'{DEC}2:{DEC}{last}')
ws.conditional_formatting.add(f'{DEC}2:{DEC}{last}', CellIsRule(operator='equal', formula=['"Block"'], fill=block_fill))
ws.conditional_formatting.add(f'{DEC}2:{DEC}{last}', CellIsRule(operator='equal', formula=['"Keep"'], fill=keep_fill))
ws.freeze_panes = 'C2'; ws.auto_filter.ref = f'A1:{DEC}{last}'
DECISION = lambda col, r: f'=IFERROR(INDEX(Scorecard!${DEC}$2:${DEC}${last},MATCH({col}{r},Scorecard!$B$2:$B${last},0))&"","")'

# --- Families ---
fw = wb.create_sheet('Families')
header(fw, ['Family', 'Channel', 'Views', 'Decision (from Scorecard)', 'Channel link', 'Why linked'], [30, 40, 8, 14, 8, 110])
r = 2
for label, members, evidence in families:
    for m in members:
        mname = name_by_id.get(m, m)
        why = '; '.join(e for e in evidence if mname in e or e.startswith('listed in'))
        fw.append([label, mname, views_by_id.get(m, 0), DECISION('B', r), None, why[:1000]])
        for cell in fw[r]: cell.font = norm
        hyperlink(fw[f'E{r}'], f'https://www.youtube.com/channel/{m}')
        r += 1
fw.conditional_formatting.add(f'D2:D{r - 1}', CellIsRule(operator='equal', formula=['"Block"'], fill=block_fill))
fw.conditional_formatting.add(f'D2:D{r - 1}', CellIsRule(operator='equal', formula=['"Keep"'], fill=keep_fill))
fw.freeze_panes = 'A2'; fw.auto_filter.ref = f'A1:F{max(r - 1, 1)}'

# --- Watched channels already in this repository's network lists ---
kw = wb.create_sheet('Known networks')
header(kw, ['Network', 'Channel', 'Views', 'List', 'Decision (from Scorecard)', 'Network file', 'Channel link'], [40, 40, 8, 10, 14, 26, 8])
krows = sorted((known[i][1], name_by_id[i], views_by_id[i], known[i][2], f'networks/{known[i][0]}.md', i) for i in views_by_id if i in known)
krows.sort(key=lambda x: (x[0], -x[2]))
for r, (net, cname, n, part, f, i) in enumerate(krows, start=2):
    kw.append([net, cname, n, part, DECISION('B', r), f, None])
    for cell in kw[r]: cell.font = norm
    hyperlink(kw[f'G{r}'], f'https://www.youtube.com/channel/{i}')
kw.freeze_panes = 'C2'; kw.auto_filter.ref = f'A1:G{len(krows) + 1}'

# --- Sister channels not watched yet (featured by channels your child watches) ---
promoted = collections.defaultdict(set)
for watched, others in fams['outside'].items():
    for o in others: promoted[o].add(watched)
outside = ytapi.channels(promoted) if promoted else {}
sw = wb.create_sheet('Not watched yet')
header(sw, ['Sister channel', 'Promoted by (channels your child watches)', 'Family', 'Promoted by # channels', 'Country', 'Subscribers', 'In networks/ list', 'Channel link'],
       [40, 70, 28, 10, 8, 12, 18, 8])
srows = []
for o, by in promoted.items():
    if o not in outside: continue
    by_names = sorted((name_by_id.get(b, b) for b in by), key=lambda n: -ch[n]['n'] if n in ch else 0)
    fam_labels = sorted({family_of[b] for b in by if b in family_of})
    srows.append((outside[o]['snippet']['title'], ', '.join(by_names), ', '.join(fam_labels), len(by),
                  outside[o]['snippet'].get('country', ''), ytapi.subs(outside[o]), listed(o), o))
srows.sort(key=lambda x: (-x[3], x[0].lower()))
for r, row in enumerate(srows, start=2):
    sw.append(list(row[:7]) + [None])
    for cell in sw[r]: cell.font = norm
    sw[f'F{r}'].number_format = '#,##0'
    hyperlink(sw[f'H{r}'], f'https://www.youtube.com/channel/{row[7]}')
sw.freeze_panes = 'B2'; sw.auto_filter.ref = f'A1:H{len(srows) + 1}'

# --- Summary / legend ---
sm = wb.create_sheet('Summary', 0)
S = f'Scorecard!${V}$2:${V}${last}'; D = f'Scorecard!${DEC}$2:${DEC}${last}'; K = f'Scorecard!${LST}$2:${LST}${last}'
lines = [
    ('YouTube Kids viewing scorecard', None),
    (None, None),
    ('Total videos watched', f'=SUM({S})'),
    ('Distinct channels', f'=COUNTA(Scorecard!$B$2:$B${last})'),
    ('First entry', f'=MIN(Scorecard!${L["First watched"]}$2:${L["First watched"]}${last})'),
    ('Last entry', f'=MAX(Scorecard!${L["Last watched"]}$2:${L["Last watched"]}${last})'),
    ('Channel families found', len(families)),
    ('Channels that belong to a family', f'=COUNTIF(Scorecard!${FAM}$2:${FAM}${last},"?*")'),
    ('Channels marked Keep', f'=COUNTIF({D},"Keep")'),
    ('Channels marked Block', f'=COUNTIF({D},"Block")'),
    ('Channels not decided yet', f'=B4-B9-B10-COUNTIF({D},"Maybe")'),
    ('Share of viewing that would be blocked', f'=IFERROR(SUMIFS({S},{D},"Block")/B3,0)'),
    ('Channels in this repository\'s network lists', f'=COUNTIF({K},"?*")'),
    ('Share of viewing from those channels', f'=IFERROR(SUMIFS({S},{K},"?*")/B3,0)'),
    (None, None),
    ('How to use', None),
    ('1. Scorecard tab: fill in the yellow cells (blue text) only: three 1-5 ratings and a Decision (Keep / Block / Maybe).', None),
    ('2. Score is the average of your ratings. Sort by "Family views" to handle a whole family at once.', None),
    ('3. Example: a calm, educational show in your language → Educational 4, Calm pace 5, Language OK 5 → Score 4.7 → Keep.', None),
    ('4. Families tab: channels that are the same brand/publisher. If you block one, block all of them, or the same videos come back.', None),
    ('5. Known networks tab: watched channels already in networks/*.md. Ask Claude to block that whole network.', None),
    ('6. Not watched yet tab: sister channels promoted by channels your child watches. Block these too before your child finds them.', None),
    ('7. In YouTube Kids, on any video from a Block channel tap ⋮ → Block this channel.', None),
    ('8. "Views" counts every watch, so re-watches count. Times are in this computer\'s time zone.', None),
    ('9. Families are linked by: channels featuring each other, the same publisher website/email, or the same videos (same length + thumbnail).', None),
    (f'Source: YouTube Data API v3 (public channel data) + your Google Takeout export. Made {datetime.now():%Y-%m-%d}.', None),
]
for i, (a, b) in enumerate(lines, start=1):
    sm.cell(i, 1, a).font = norm
    if b is not None: sm.cell(i, 2, b).font = norm
sm['A1'].font = Font(name=F, bold=True, size=14); sm['A16'].font = bold
sm['B5'].number_format = sm['B6'].number_format = 'yyyy-mm-dd'; sm['B12'].number_format = sm['B14'].number_format = '0.0%'
sm.column_dimensions['A'].width = 42; sm.column_dimensions['B'].width = 14

# --- All views ---
av = wb.create_sheet('All views')
header(av, ['Time', 'Channel', 'Video', 'Video link'], [17, 40, 70, 45])
for name, url, title, t, vurl in sorted(rows, key=lambda r: r[3], reverse=True):
    av.append([t, name, title, vurl])
for r in range(2, av.max_row + 1):
    for cell in av[r]: cell.font = norm
    av.cell(r, 1).number_format = 'yyyy-mm-dd hh:mm'
av.freeze_panes = 'A2'; av.auto_filter.ref = f'A1:D{av.max_row}'

wb.calculation.fullCalcOnLoad = True
wb.save(ytapi.work('scorecard.xlsx'))
print(len(order), 'channels,', len(families), 'families,', len(krows), 'in known networks,', len(srows), 'sister channels not watched yet -> research/scorecard.xlsx')
print(ytapi.quota())
