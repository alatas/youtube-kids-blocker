---
description: Carry on with the saved YouTube Kids blocking job (after a break, an error or /clear). Use when the parent says "continue" or asks to finish blocking.
---
Continue blocking YouTube Kids channels for my child.

Folders: the repository is `${CLAUDE_PLUGIN_ROOT}` and my folder is `${CLAUDE_PLUGIN_DATA}`. If these still read as `${…}` placeholders, you're in a clone of the repository: both are the current folder. The progress folder is `results/` in my folder, and my lists are the `networks/*.md` files in my folder (not `README.md`). Run the repository's scripts with `YKB_HOME="<my folder>"` set (see the "Folders" note in `block-channels-prompt.md`).

Follow `block-channels-prompt.md` in the repository (everything below its line), starting at its step 3 with the `plan.txt` in the progress folder. Don't ask me anything you don't need to.

If there is no `plan.txt`, tell me to start with `/block-channel <network>` or `/block-channel all`, and show me my lists as a short table (from each file's title and its Publisher and What it is lines). If I have no lists yet, explain how to start from a video link (*"Who is behind this video? <link>"*).
