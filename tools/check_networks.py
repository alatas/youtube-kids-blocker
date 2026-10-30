"""Check that every networks/*.md file has the generic shape from CONTRIBUTING.md ("File format"):
only the allowed header fields, no research notes ("How this list was made"), no line-format notes, nothing
about a particular family or child, the exact list headings, and well-formed channel lines.
Keeps your lists readable for the blocking scripts and free of personal details. No API key needed.
usage:   python -I tools/check_networks.py [networks/foo.md ...]      (default: every list in your folder)
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ('Publisher', 'What it is', 'Brands', 'Shows', 'Why block it', 'Trade-off', 'Optional list')
# research notes and personal wording belong in the pull request description, never in the file
BANNED = [r'how this list', r'format of each line', r'\bseed(ed|s)?\b', r'checked by hand', r'added later',
          r'left out', r'\ba parent\b', r"\ba child's\b", r'\bmy (child|son|daughter|kid)', r'\bour (child|son|daughter|kid)',
          r'watch history', r'\bwatched\b', r'\bturned up\b']
LINE = re.compile(r'^(\d+)\. .+ \| (UC[\w-]{22}) \| https://www\.youtubekids\.com/channel/\2 \| [^|]* \| [^|]+( \| [\w-]*)?$')

def check(path):
    errors = []
    lines = open(path, encoding='utf-8').read().splitlines()
    if not lines or not lines[0].startswith('# Network: '): errors.append('line 1 must be "# Network: <name>"')
    numbers, sections = [], []
    for i, line in enumerate(lines, 1):
        low = line.lower()
        if not re.match(r'^\d+\. ', line):   # channel names are public data; check only the text around them
            for pat in BANNED:
                if re.search(pat, low): errors.append(f'line {i}: remove "{re.search(pat, low).group()}" (keep research notes and personal details out of the list)')
        if m := re.match(r'^- \*\*([^*:]+):\*\*', line):
            if m.group(1) not in FIELDS: errors.append(f'line {i}: field "{m.group(1)}" isn\'t allowed; use {", ".join(FIELDS)}')
        elif line.startswith('- '): errors.append(f'line {i}: header bullets must be "- **<Field>:** …"')
        if line.startswith('## '):
            if not re.match(r'^## (Main list|Optional list)\b', line): errors.append(f'line {i}: only "## Main list…" and "## Optional list…" headings')
            sections.append(line.split(':')[0].split(' (')[0])
        if re.match(r'^\d+\. ', line):
            if not LINE.match(line): errors.append(f'line {i}: expected "number. Channel name | UC… | https://www.youtubekids.com/channel/UC… | Country | Subscribers | Test video ID"')
            numbers.append(int(line.split('.')[0]))
    if not sections or sections[0] != '## Main list': errors.append('the first list must be "## Main list"')
    if len(set(numbers)) != len(numbers): errors.append('channel numbers must be unique in the whole file (the optional list continues after the main list; new channels get new numbers)')
    if not any(l.startswith('*List made ') for l in lines): errors.append('end with the "*List made <date> from public YouTube data…*" line')
    return errors

dirs = dict.fromkeys([os.path.join(ROOT, 'networks'), os.path.join(os.environ.get('YKB_HOME') or ROOT, 'networks')])
files = sys.argv[1:] or sorted(f for d in dirs for f in glob.glob(os.path.join(d, '*.md')) if os.path.basename(f).lower() != 'readme.md')
bad = 0
for f in files:
    errs = check(f)
    if errs:
        bad += 1
        print(f'{os.path.relpath(f, ROOT)}:')
        for e in errs: print(f'   {e}')
if not files: print('No lists yet: make one with the investigate skill (README.md -> "How it works").')
print(f'{len(files) - bad} of {len(files)} files OK' if bad else f'All {len(files)} files OK')
sys.exit(1 if bad else 0)
