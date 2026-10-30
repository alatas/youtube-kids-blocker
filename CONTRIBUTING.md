# Contributing

Fixes and improvements to the tools, skills and docs are welcome.

## No lists

This project ships tools, not lists. We don't accept:

- network lists, or any file in `networks/` other than its README;
- names, IDs or links of channels or publishers to block, in files, issues or pull requests;
- anything about a family or child (watch history, account names, screenshots, files from `research/` or `results/`);
- API keys.

To show a bug, describe the channel in general terms ("a channel with an empty description").

## Pull requests

1. `git status` shows nothing from `networks/`, `research/` or `results/`.
2. Changed a skill or tool? Raise `version` in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, then run `claude plugin validate .`.
3. Say what you changed and how you tested it.

---

# Reference: your lists and the research tools

The rest is for Claude and for parents who like to run the tools themselves. The skills already do all of this for you.

## Where your lists live

Your lists are in `networks/` in **your folder**: the plugin's data folder (with the plugin), or the repository folder (in a clone, where git ignores everything in `networks/` except its README). The research files are in `research/` and the blocking progress in `results/`, also in your folder.

## List format

One file per publisher network, `networks/<name>.md`. Keep only facts about the publisher and its channels in it: no research notes, and nothing about your family. The blocking scripts read this shape, so keep it exactly.

```
# Network: <Publisher or brand>

- **Publisher:** who runs it, country, website or contact as given on the channels
- **What it is:** what the channels upload, in a sentence or two
- **Brands:** or **Shows:** (optional) the names you recognise
- **Why block it:** (optional) why you want the whole network gone
- **Trade-off:** (optional) shows in it you may want to keep
- **Optional list:** (optional) what the optional list contains

## Main list: <short description> (<count>)

1. Channel name | Channel ID | YouTube Kids link | Country | Subscribers | Test video ID

## Optional list: <short description> (<count>)

<one sentence: when to block these>

*List made <date> from public YouTube data (YouTube Data API v3).*
```

- `## Main list` is blocked by default; `## Optional list` only on request (e.g. general-audience channels).
- Each channel line: `number. Channel name | Channel ID | YouTube Kids link | Country | Subscribers | Test video ID`. Channel names can contain `|`, so the Channel ID (starts with `UC`) is the reliable key. The link is `https://www.youtubekids.com/channel/<Channel ID>`. The test video is the channel's newest upload, for checking on the child's own device; `none` if it has no public videos.
- Channel numbers are unique in the whole file: the optional list continues after the main list. When you add channels, give them new numbers after the highest one and never renumber: the progress logs refer to the numbers. Add "updated <date>" to the last line.
- Check your lists with `python -I tools/check_networks.py` (no API key needed). It reports extra header fields, research notes, wrong headings and malformed channel lines.

## Research tools (`tools/`)

They use only public channel data from the YouTube Data API v3, plus, if you want, your own child's watch history.

### Setup

1. Python 3.9 or newer. `pip install -r tools/requirements.txt` (Pillow and openpyxl; only `families.py`, `vidpairs.py` and `scorecard.py` need them).
2. A free API key: in https://console.cloud.google.com create a project, enable **YouTube Data API v3**, then **Credentials → Create credentials → API key**. Save it in a file named `.yt_api_key` in your folder (in a clone, the repository folder; git ignores it. With the plugin, the plugin's data folder: Claude creates the file and opens it for you), or in your home folder, or set the `YT_API_KEY` environment variable. **Never print, paste or commit the key.**
3. Run every script from anywhere as `python -I tools/<script>.py` (`python3` on Mac/Linux). Run one without arguments to see its usage. With the plugin, set `YKB_HOME` to the plugin's data folder so research files, your lists and the key are kept there.

The free quota is 10,000 units a day. A channel search costs 100 units; almost everything else costs 1 unit per call. Each script prints the units it used.

### Investigate one channel or network

```
python -I tools/channel.py v:VIDEO_ID          # or a channel ID, @handle or link
python -I tools/crawl.py research/foo.json "foo studio|foostudio\.com" SEED_CHANNEL_ID "Foo Studio"
python -I tools/make_list.py research/foo.json "Foo Studio"
```

1. **`channel.py`** shows a channel's description, subscriber count, "made for kids" status, latest uploads and featured channels, and whether it is already in one of your lists. From the description, pick the publisher's **signature**: company name, website or contact email.
2. **`crawl.py`** starts from seed channels (and optional channel searches separated by `|`), follows featured channels breadth-first, and keeps channels whose own description matches the signature (a regular expression, case-insensitive). It prints every channel found, marks those already in your lists, and lists name-only matches it left out. Add `--loose` for publishers with empty descriptions; it also takes channels that feature each other with a member or are featured by 3+ members, marked unconfirmed.
3. **`make_list.py`** writes `research/foo-draft.md` in the format above, with a test video per channel. Fill in the TODOs in the header, check the channels, and copy it to `networks/` in your folder.

### Start from your child's watch history

1. At https://takeout.google.com, signed in as the child's account: **Deselect all**, tick **YouTube and YouTube Music**, under *Multiple formats* set **history** to **JSON**, and under *All YouTube data included* keep only **history** (and **subscriptions** if you want). Unzip the export into `research/`.
2. Run, in this order:
   - `fetch_channels.py`: public data for every channel in the history → `research/channels.json`
   - `fetch_related.py`: featured channels, latest 50 uploads and their thumbnails → `research/related/`
   - `families.py`: groups channels into families by shared websites/emails, identical videos (same length and thumbnail) and featuring each other → `research/families.json`
   - `scorecard.py`: a spreadsheet `research/scorecard.xlsx` with every channel, its family, whether it is already in your lists, sister channels your child hasn't watched yet, and columns for your own ratings and a Keep/Block decision
3. A family that isn't in your lists yet is a candidate for a new list: run `channel.py` on one of its channels and continue with `crawl.py` as above. `vidpairs.py` is a diagnostic that lists look-alike video pairs, to check the identical-video matching by eye.

## How to find a network (method notes)

- `channels.list` (snippet, statistics, status for `madeForKids`, brandingSettings) and `channelSections` (featured channels) do most of the work; `videos.list` turns a video into its channel.
- Grow the network breadth-first through featured channels. Keep only channels whose description matches the publisher's signature (company name, website, contact email). Add channel searches for the brand name. Don't use channel keywords as evidence; they often name other brands to attract searches.
- Drop copycats with under 1,000 subscribers, channels with no videos, and automatic "- Topic" channels.
- To find re-uploads across publishers, search for the show's name as videos and group the results by channel: a channel of another publisher can carry the same show.
- To find sister channels that hide their link, match identical videos: same duration and a thumbnail dHash distance of 0 (or ≤3 for videos of 90 seconds or longer), with at least 2 matches.
- Name-only matches are unreliable: short, generic channel names belong to many unrelated accounts. Always confirm with the description signature.
