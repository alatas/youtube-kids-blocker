---
description: Find out who is behind a YouTube Kids channel or video and collect its network into the parent's own list. Use when the parent shares a youtubekids.com or youtube.com link, a channel ID or an @handle and asks who made it, whether it is in their lists, or how to block it; when they ask to make or update a list for a network; or when they ask to set up the research tools.
argument-hint: <youtubekids.com or youtube.com link | channel ID | @handle>
---
Investigate this for me (a parent): **$ARGUMENTS**

I'm not technical: one step at a time, plain words, and do the steps yourself where you can.

Folders: the repository is `${CLAUDE_PLUGIN_ROOT}` and my folder is `${CLAUDE_PLUGIN_DATA}`. If these still read as `${…}` placeholders, you're in a clone of the repository: both are the current folder. Run every script as `YKB_HOME="<my folder>" python -I "<repository>/tools/<script>.py" …`. My research files go in `research/` in my folder, and my lists go in `networks/` in my folder. The repository's own folder may be read-only: never write into it from the plugin.

## Setup (first time, or "help me set up the research tools")

1. Check that Python 3.9+ works (`python --version`; on Mac/Linux `python3`). If not, help me install it.
2. Only for the watch-history spreadsheet: `pip install -r "<repository>/tools/requirements.txt"`.
3. The free YouTube key: walk me through `CONTRIBUTING.md` → "Setup" in the repository, one screen at a time. Then create an empty file named `.yt_api_key` in my folder and open it in a text editor for me (Windows: `notepad "<file>"`; Mac: `open -e "<file>"`); I paste the key, save and close it. Never ask me to paste the key into the chat, and never print it.
4. Test: `YKB_HOME="<my folder>" python -I "<repository>/tools/channel.py" v:jNQXAC9IVRw`.

If a script says the key is missing while investigating, do this setup first.

## Investigate a link

1. Run `channel.py "<the link>"`. It accepts video links (`watch?v=`), channel links, channel IDs and @handles.
2. Tell me in plain words, briefly:
   - the channel's name, who runs it (a company, a family or a creator; company website or contact from its description), country, subscribers, "made for kids" or not;
   - what it uploads (from its latest videos);
   - whether it is already in one of my lists (which one, and whether my plan and logs in `results/` show it as blocked);
   - its sister channels (featured channels and the same publisher signature), and whether it looks like part of a network.
3. Suggest one next step:
   - **already in my lists:** block that network (the block-channel skill), or say it's already blocked;
   - **a network that isn't in my lists yet:** offer to make a list (below);
   - **a single channel:** offer to block just this one with `tools/ytk-blocker.js` in the child's youtubekids.com tab, as described in `block-channels-prompt.md` step 3 (use the item `manual/1:<channel ID>`; its log is `results/manual.txt` in my folder).

## Make a list ("make a list for this network")

1. Collect the network with `crawl.py` and write a draft with `make_list.py` (`CONTRIBUTING.md` → "Investigate one channel or network").
2. Show me the channel names and wait for my OK; remove what I say doesn't belong. If some channels carry gentle shows I might want to keep, point them out.
3. Save it as `networks/<name>.md` in my folder (in a clone, the repository's `networks/`, which git ignores). Write the header from the template in `CONTRIBUTING.md` → "List format", using only its fields. Describe what the videos show; no names of children, no personal emails, nothing about me or my child, and no notes on how you found the channels.
4. Run `check_networks.py "<the new file>"` and fix everything it reports.
5. Offer to block it now.

## Update a list ("update the list for X")

Run `crawl.py` again with the same signature and seeds, show me only the channels that aren't in the list yet, and after my OK add them with new numbers after the highest one (never renumber) and "updated <date>" on the last line. Run `check_networks.py` on it, then offer *continue blocking*.

## Sharing lists

The project doesn't accept lists. If I ask to share one, say so in one sentence: my lists stay on my computer, and other parents make their own the same way. Never open a pull request or issue that contains a list, channel names or IDs of a network, or anything about my family.

Keep my child's data and my lists in my folder (`networks/`, `research/`, `results/`).
