---
description: Block YouTube Kids channel networks from the parent's own lists on the child's profile, e.g. "/block-channel all" or "/block-channel only <name>". Use when the parent asks to block a network, a publisher or a brand they have made a list for, says "block it" after investigating a channel, or asks to start over for another child.
argument-hint: all | <network names> | only <network>
---
Start a blocking job on my child's YouTube Kids profile for: **$ARGUMENTS**

Folders: the repository is `${CLAUDE_PLUGIN_ROOT}` and my folder is `${CLAUDE_PLUGIN_DATA}`. If these still read as `${…}` placeholders, you're in a clone of the repository: both are the current folder. The progress folder is `results/` in my folder, and my lists are the `networks/*.md` files in my folder (not `README.md`). Run the repository's scripts with `YKB_HOME="<my folder>"` set (see the "Folders" note in `block-channels-prompt.md`).

Follow `block-channels-prompt.md` in the repository (everything below its line). This is a new or changed plan, so do its step 2: match my words to my list files ("all" = every list, "only X" = just that network; "block it" right after investigating = the list just made or found), ask the plan questions once, write `plan.txt` in the progress folder (replace an old plan; the logs keep what is already blocked), then block.

If I didn't name any network, show me my lists as a short table (from each file's title and its Publisher and What it is lines, one line each) and ask which ones.

If I have no lists yet, say so in one line and explain how to start: copy the link of an unwanted video from my child's Recommended page and ask *"Who is behind this video? <link>"* (the investigate skill).
