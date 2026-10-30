# Privacy

The YouTube Kids channel-network blocker runs on your own computer. The project has no server and the author receives no data.

## What stays on your computer

- Your network lists, the blocking progress, and your YouTube API key.
- Only if you ask for the watch-history spreadsheet: your child's Google Takeout watch history and the files made from it.

They are kept in your folder (the plugin's data folder, or the git-ignored `networks/`, `results/` and `research/` folders in a clone). Delete that folder to remove them.

## What is sent, and where

| Service | What is sent | Why |
|---|---|---|
| `www.googleapis.com` (YouTube Data API v3) | your own API key, and channel or video IDs | to look up public channel information |
| `i.ytimg.com` | video IDs | to download public video thumbnails (watch-history spreadsheet only) |
| `www.youtubekids.com` | channel IDs, from your child's signed-in tab | to block channels and check the blocks |

These services are run by Google and covered by [Google's privacy policy](https://policies.google.com/privacy). Nothing else is sent anywhere.

## Claude

The plugin runs inside Claude Code. What you and the tools show Claude is handled under Anthropic's privacy policy: https://www.anthropic.com/legal/privacy

## Contact

Questions: open an issue at https://github.com/alatas/youtube-kids-blocker/issues (don't include any personal or family details).
