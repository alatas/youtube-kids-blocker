# YouTube Kids channel-network blocker

A tool for parents. Start from a video you don't want on your child's YouTube Kids **Recommended** page; Claude (Anthropic's AI assistant) finds out who is behind it, collects that publisher's whole **network of sister channels** into a list on your computer, and blocks every channel in it on your child's profile.

## Why

Look at what YouTube Kids recommends to a preschooler. Little of it is made to be good for a small child; most of it is made to keep them watching:

- **Overstimulating:** saturated colours, nonstop motion, fast cuts and loud effects. Small children find it hard to look away, and calmer shows feel boring afterwards.
- **Endless:** compilations of one, two, even ten hours, so a video never really ends.
- **Not really children's programmes:** recorded mobile-game play, such as truck, tractor and bus "simulators".
- **Poor role models:** stories built on pranks, tantrums, breaking things or ignoring rules, played for laughs.

A few are calm, story-driven shows with kind characters that model good behaviour. Those are the ones worth keeping.

YouTube Kids doesn't let you fix this properly. In many countries and apps you can't choose which channels are allowed; you can only **block** channels one at a time. And many kids' publishers run dozens of sister channels that re-upload the same videos, so when you block one, the same videos come back through another. This tool blocks the **whole network** at once.

**No lists are included.** You make your own, and they stay on your computer.

## How it works

1. **Spot it.** On your child's YouTube Kids profile, open the **Recommended** page, find a video you don't want and copy its link (browser address bar; on a tablet: **Share → Copy link**).
2. **Ask who is behind it.** Tell Claude: *"Who is behind this video? &lt;link&gt;"*. Claude tells you in plain words who runs the channel, what it uploads, and which sister channels it has.
3. **Make a list.** Say *"make a list for this network"*. Claude collects the sister channels and shows you their names to check; you say what doesn't belong. The list is saved on your computer.
4. **Block it.** Say *"block it"*. Claude blocks every channel in the list on your child's profile, then checks that each one is really gone.

Repeat with the next unwanted video. After a few networks the Recommended page looks very different.

---

## Get started (once)

### What you need

1. **A computer** (Windows, Mac or Linux) with **Google Chrome**. A tablet or phone won't work for this.
2. **Claude Code**, Anthropic's assistant that runs on your computer, and the **Claude in Chrome** extension, both signed in to the same Claude account. Install them from https://claude.com/claude-code and https://claude.com/chrome. In the Chrome extension, allow Claude on **youtubekids.com** without asking each time.
3. **Python 3.9 or newer** and a **free YouTube key** from Google, to look up public channel information. Claude checks Python and walks you through getting the key, one screen at a time; just say *"help me set up the research tools"*. The key goes into a file on your computer, never into the chat.
4. In Chrome, a window where **your child's Google account** is signed in to **https://www.youtubekids.com**, with **your child's profile** picked. A private (incognito) window is fine; then turn on **"Allow in Incognito"** for the Claude extension (`chrome://extensions` → Claude → Details). **Keep that window in front** while Claude blocks. If your own account's window is in front, Claude notices it's the wrong account and stops.
5. Your **parent passcode or Google password**, in case YouTube asks. You type it yourself; Claude never types it.

### Install

Open Claude Code and type these two lines, one after the other:

```
/plugin marketplace add alatas/youtube-kids-blocker
/plugin install youtube-kids-blocker@youtube-kids-blocker
```

Then type `/model sonnet`. Sonnet is enough for everything here and costs about half as much as the bigger model.

Finally, say *"help me set up the research tools"* for the YouTube key.

---

## Investigate: who is behind this video?

Tell Claude *"Who is behind this video? &lt;link&gt;"* (or `/youtube-kids-blocker:investigate-channel <link>`). It accepts youtubekids.com and youtube.com video or channel links, channel IDs and @handles.

Claude tells you:

- who runs the channel (a company, a family, a creator), its country, and whether it's marked "made for kids";
- what it uploads, from its latest videos;
- its sister channels, and whether it looks like part of a network;
- whether it's already in one of your lists, and whether you've blocked it.

Then it suggests one next step: make a list for the network, block the network you already have a list for, or block just this one channel.

| Say | What happens |
|---|---|
| *"Make a list for this network"* | Claude collects all the sister channels, shows you their names to check, and saves the list on your computer |
| *"Block just this channel"* | blocks only that one channel, for a channel with no sister channels |
| *"Go through my child's watch history"* | from a Google Takeout export, Claude makes a spreadsheet of every channel your child watched, grouped by publisher, for you to mark Keep or Block |

## Block

| Say | What happens |
|---|---|
| *"Block it"*, *"Block &lt;name&gt;"* | blocks that network from your lists (brand names work too) |
| *"Block all my lists"* | blocks every network you've made a list for |
| *"Block &lt;name&gt; but keep &lt;show&gt;"* | skips that show's channels. Say it **before** blocking starts: unblocking later removes every block |
| *"Continue blocking"* | carries on after a break, an error, or after you've added channels to a list |
| *"Start over for my other child"* | starts fresh for another child's profile, so channels blocked for the first child aren't skipped |
| *"Show me the report"* | what's blocked, and what was tried but not confirmed |

1. Claude asks its questions once at the start. If you're not sure, say *"ok"* for the safe defaults.
2. It blocks the first 2 channels and shows you. Say *"ok"*; after that it works on its own, about 2 minutes per 50 channels. It doesn't click through pages: it sends the same request as YouTube Kids' own "Block this channel" button, then checks that each channel is really gone.
3. If anything stops it (the browser, your laptop going to sleep), say **"Continue blocking"**. It picks up exactly where it left off.
4. At the end you get a short report per network.

The blocks are saved to **your child's account**, so they also apply on the tablet or phone, as long as the YouTube Kids app there uses your child's account and the same profile.

Prefer commands? Type `/youtube-kids-blocker:block-channel <name>`, `/youtube-kids-blocker:block-channel all` or `/youtube-kids-blocker:continue-to-block`.

### After blocking: give the recommendations a fresh start

If your child's watch history is full of the kind of videos you just blocked, YouTube keeps recommending **look-alike videos** from channels that aren't blocked yet, because it learned from that history. When you've blocked the networks you found, three steps help a lot:

1. **Delete your child's watch history.** Signed in as your child's Google account, open https://myactivity.google.com/product/youtube, choose **Delete → All time**, and confirm. This resets the recommendations. The channels you blocked stay blocked.
2. **Unsubscribe from the channels you don't want.** On YouTube Kids (or YouTube, for a supervised account), open the subscribed channels and unsubscribe from each one you blocked or don't like.
3. **Subscribe to a few good channels**: calm, story-driven shows you're happy with. The new recommendations start from those.

Deleting the history can't be undone. If you want to use it first, for example for *"go through my child's watch history"*, export it before you delete it: https://takeout.google.com → YouTube and YouTube Music → history.

---

## Good to know

- **Your lists and your child's data stay on your computer.** The lists, the blocking progress and anything from the watch history are kept in your folder (with the plugin, its data folder; in a clone, the git-ignored `networks/`, `results/` and `research/` folders). See "Data and privacy" below.
- **Blocking is per child profile.** For several children, do it once per profile (*"start over for my other child"*).
- **Some networks also carry gentle shows.** When Claude makes a list, check the channel names; to keep a show, say so before blocking.
- **Unblocking removes everything.** In the YouTube Kids parent settings, **Unblock videos** removes *all* the blocks you've made, not just one, so use it carefully.
- **YouTube Kids has no list of blocked channels.** To check later, ask Claude for the report.
- **Networks grow.** Publishers open new channels all the time. Every few weeks, look at what your child is recommended, and investigate anything new. To refresh a list, say *"update the list for &lt;name&gt;"*, then *"continue blocking"*.
- **"Approve content yourself" mode** (where you choose the allowed channels) is better, if your country and app offer it. Check your child's profile settings first. This tool is for parents who only get the age-level options.
- **When YouTube asks to slow down.** After many block requests in a short time, YouTube can answer "too many requests". The blocker already goes at a calm pace (one channel every half second, 20 at a time); when asked, it waits as long as YouTube says (usually a minute, never more than 15) and carries on by itself. If YouTube refuses 5 channels in a row, Claude stops; come back in an hour or the next day and say *"continue blocking"*.
- **The free YouTube key has a daily allowance** of 10,000 "units". Looking up one channel costs about 5; collecting a big network costs up to a few thousand. When it runs out, the tools say so; it resets every day at midnight US Pacific time. **Blocking doesn't use the key**, so you can always block.
- **Use it at your own risk.** The blocker does in your child's own account what you could do by hand with the **Block this channel** button, one channel at a time. YouTube can change its site at any time, and this project can't promise it keeps working.

---

## Data and privacy

**What it reads and stores (on your computer only):** your network lists, the blocking progress, and, only if you ask for the watch-history spreadsheet, your child's Google Takeout watch history and the files made from it. They stay in your folder; the project author receives nothing.

**Which services it talks to:**

| Service | What is sent | Why |
|---|---|---|
| `www.googleapis.com` (YouTube Data API v3) | your own API key, and channel or video IDs | to look up public channel information |
| `i.ytimg.com` | video IDs | to download public video thumbnails (watch-history spreadsheet only) |
| `www.youtubekids.com` | channel IDs, from your child's signed-in tab | to block channels and check the blocks |

Nothing else is sent anywhere. There is no server of this project. Full details: [Privacy](PRIVACY.md).

---

## For developers

To work on the project itself, clone it (`git clone https://github.com/alatas/youtube-kids-blocker`) and open Claude Code in that folder; the same skills then run as `/block-channel`, `/continue-to-block` and `/investigate-channel`, and your lists, progress and research stay in the git-ignored `networks/`, `results/` and `research/` folders.

Files: `block-channels-prompt.md` (the blocking instructions Claude follows), `.claude/skills/` (the skills behind the commands), `.claude-plugin/` (the plugin and marketplace), `.claude/CLAUDE.md` (read by Claude Code automatically in a clone), `tools/ytk-blocker.js` and `tools/blocklog.sh` (the blocking script and its bookkeeping), the research scripts in `tools/*.py`, `tools/check_networks.py` (checks the shape of your own lists), and `CONTRIBUTING.md` (what contributions are welcome, the list format and how the research tools work).

Contributions: see [`CONTRIBUTING.md`](CONTRIBUTING.md). No lists.

## License

[MIT](LICENSE). [Privacy](PRIVACY.md).

*This project is not affiliated with or endorsed by YouTube, Google, Anthropic or any channel publisher. It uses only public channel information from the YouTube Data API v3, looked up with each parent's own key.*
