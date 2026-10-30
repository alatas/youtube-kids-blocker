# YouTube Kids channel-network blocker: instructions for Claude

A parent has opened this folder to find out who is behind the videos on their child's YouTube Kids profile, make their own lists of channel networks, and block them. The project ships tools only, never lists: every parent's lists stay in their own git-ignored `networks/` folder.

- **Blocking** (`/block-channel …`, `/continue-to-block`, "block X", "continue"): use the matching skill in `.claude/skills/`; both follow **`block-channels-prompt.md`**, which also holds the lessons from real use. If `results/plan.txt` exists, a job is in progress: continue it without questions unless the parent names different networks.
- **Investigating** (`/investigate-channel <link>`, "who is behind this channel?", making or updating a list, "help me set up the research tools"): use the investigate skill; it follows `CONTRIBUTING.md` and the scripts in `tools/` (run them as `python -I tools/<script>.py`).
- You need browser access (Claude in Chrome) for blocking. If you don't have it, tell the parent how to set it up (README.md → "Get started" → "What you need") and stop.
- Blocking runs fine on Sonnet. If you are Opus, say once at the start of a new job: "Sonnet is enough for this and costs about half: type `/model sonnet` and run the command again, or tell me to continue." Don't repeat it on `/continue-to-block`.

## Helping a parent with the research tools

The investigate skill (`.claude/skills/investigate-channel/SKILL.md`) has the steps for setting up the research tools and making or updating a list. Follow it here too; the parent is usually not technical.

## Keep the repository free of family data

The repository is public. The child's data and the parent's lists stay in `research/`, `results/` and `networks/` (git ignores all three, except `networks/README.md`): never put lists, channel names or IDs of a network, watch history, view counts, account names, which channels a particular child has blocked, or screenshots of a child's profile into commits, issues or pull requests. If a parent asks to share a list, say in one sentence that the project doesn't accept lists. Never print or commit the API key (`.yt_api_key`).

Every list follows the template in `CONTRIBUTING.md` → "List format": only public facts about the publisher, no research notes, no names of children or personal emails. Don't copy headers from `research/*-draft.md` files; older drafts there still have the old shape. Run `python -I tools/check_networks.py` after changing any list; it must say "All … files OK". Before every commit, check that nothing in `networks/` except its README is staged.

## Notes for changing the blocker

- The skills in `.claude/skills/` are also the plugin's skills (`.claude-plugin/plugin.json`), so they must work both in a clone and from the plugin's read-only cache. That's why they name the repository folder and the parent's folder (the plugin's data folder), and why the tools read `YKB_HOME`: `results/`, `research/`, the parent's own `networks/` and `.yt_api_key` live there.
- `tools/ytk-blocker.js` sends the site's own `kids/update_blacklist` request and only ever the BLOCK action. YouTube Kids already uses `window.ytk`, so the script's object is `window.ytkBlocker`.
- Keep `version` in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` the same, and raise it when the skills or tools change, so plugin users get the update. Check with `claude plugin validate .`.
