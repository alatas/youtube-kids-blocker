# Prompt: block channel networks in YouTube Kids

> **Parents:** you don't need to read or paste this file; Claude reads it by itself. Just tell Claude what you want, for example *"who is behind this video? <link>"*, *"block it"*, *"block all my lists"* or *"continue blocking"*. See README.md → "How it works".
>
> Claude asks its questions once at the start, blocks the first 2 channels for you to check, then does the rest on its own: about 2 minutes per 50 channels.

---

You are helping me, a parent, block YouTube Kids channels on my child's profile. I'm not technical: keep messages short and plain, and don't ask me anything you don't need to.

**How blocking works here:** a small script, `tools/ytk-blocker.js`, runs inside the youtubekids.com tab and sends the same request as the site's own "Block this channel" button, so there is nothing to click. It blocks 20 channels, 0.5 s apart, then checks the same 20 (a block takes 10–15 seconds to show), and so on. `tools/blocklog.sh` works out from the plan and the logs what is left, and saves the results. You need the browser (Claude in Chrome) and the shell.

**Folders:** the command that started you names the repository folder and my folder. The network lists are mine: the `networks/*.md` files in my folder (not `README.md`); the project ships none. In a clone, both are the current folder, and the commands below work as written. From the plugin, file paths like `tools/…` are in the repository folder, and `results/` and `networks/` mean those folders in my folder, and every `sh tools/blocklog.sh …` runs as `YKB_HOME="<my folder>" sh "<repository folder>/tools/blocklog.sh" …`.

## 1. Plan or continue?

- `/block-channel …`, or I name networks: a **new or changed plan**, go to step 2. Replace an old `results/plan.txt`; the logs keep what's already blocked, so nothing is done twice.
- `/continue-to-block`, "continue", or anything else while `results/plan.txt` exists: **continue**, go to step 3 without questions.
- "Start over", "another child", "my other child": the old progress belongs to another profile. Confirm in one line ("I'll put the progress for the first child aside and start fresh for this one, OK?"), then move everything in `results/` into a new folder `results/old-<today's date>/` and go to step 2. Also make sure the youtubekids.com tab now shows the other child's profile.

## 2. Make the plan (ask everything now, once)

1. Match my words to my list files in `networks/` (a brand name → the file whose title or Publisher, Brands or Shows line names it; "block it" right after investigating → the list just made or found). **"all" = every list file**, in alphabetical order. Ask only if you really can't tell which file I mean.
2. Read the notes at the top of each chosen file. Ask me **all** the choices they offer (**Trade-off** notes, **Optional lists**) **in one message**, with the default for each: Main list only, no optional lists, no skips. "ok" means the defaults. If I want to keep a show ("keep <show>"), find its channel numbers in that file.
3. Write `results/plan.txt` in exactly this form (network file names without `.md`; one `skip:` line per network; `optional: none` if none):

   ```
   networks: foo-studio bar-kids-tv
   optional: none
   skip: bar-kids-tv 41 42 43
   first check done: no
   ```

## 3. Open the child's tab and set up

1. Get the browser tabs. Use a youtubekids.com tab in the window where **the child's account** is signed in (often an incognito window), or open one there. If browser tools time out or the wrong window answers, the child's window is probably behind another one: ask me to click on it to bring it to the front, then try again.
2. Read `tools/ytk-blocker.js` and run its whole text in that tab with the javascript tool. It answers:
   - `CHILD`: good, go on.
   - `PARENT`: stop. Say: "This Chrome window is signed in with your own account, not your child's. Please click on the window with your child's account (for example the incognito window), then type /continue-to-block." Blocks made here would go to the wrong account.
   - `ERROR: …`: open https://www.youtubekids.com (the home page) in that tab and run it once more. If it fails again, tell me in one line and stop.

## 4. Block

1. Run `sh tools/blocklog.sh todo` (if the plan says `first check done: no`, run `sh tools/blocklog.sh todo 2`). It prints one line of channels, and a count per network. Empty line: nothing left, go to step 5.
2. In the tab, run `ytkBlocker.start("<that line>")`. Tell me in one line how many channels it's doing.
3. About every 45 seconds, use one browser_batch: 4 × wait 10 s, then `ytkBlocker.take()`. It returns a status line (`RUNNING 20/120`, `FINISHED …` or `STOPPED …`) and the finished channels. `RUNNING … (waiting 60 s: YouTube asked to slow down …)` means YouTube answered "too many requests" (HTTP 429): the script waits as long as its `Retry-After` header says (60 s if it doesn't say, at most 15 minutes) and then retries the same channel by itself, so just keep checking. Tell me once in plain words ("YouTube asked me to slow down, so I'm waiting a minute; nothing to do"), not on every check. Save them right away:

   ```
   sh tools/blocklog.sh save <<'EOF'
   <everything take() returned>
   EOF
   ```

   Don't repeat the lines in chat. Repeat until `FINISHED` or `STOPPED`.
4. **First check:** after the 2-channel job of a new plan, show me the two results (channel names, from the network file) and wait for my OK. Then change the plan line to `first check done: yes` and do step 4 again for the rest, without asking again.
5. **`STOPPED`** (YouTube refused several blocks in a row): wait 5 minutes, run steps 3 and 4 once more; if it stops again, tell me and give the report.
6. **Page reloaded or extension disconnected** (`ytkBlocker` is undefined, or tools fail): reconnect, run step 3 again, then step 4. Channels whose results weren't saved are simply done again; that's harmless.

## 5. Report

Run `sh tools/blocklog.sh report` and show its output, then add in plain words:

- Channels "tried but not confirmed" are tried again with `/continue-to-block`.
- Blocks reach the tablet or phone if the YouTube Kids app there uses the child's account and the same profile. Channels that are blank on the website get blocked too.
- If it says ALL DONE: "To do the same for another child, tell me *start over for my other child*."
- If it says ALL DONE, also suggest, in plain words, the fresh start from README.md → "Block" → "After blocking": delete the child's YouTube watch history at https://myactivity.google.com/product/youtube (signed in as the child; export it first at takeout.google.com if they want to keep it), unsubscribe from unwanted channels, and subscribe to a few good ones. This stops YouTube recommending look-alikes of the blocked videos. The parent does these steps themselves; don't do them for them.

## Good to know (lessons from real use)

- A block counts only when it's confirmed: YouTube answers "Channel blocked", and a check 10–15 seconds later shows the channel as hidden. Right after the block it still shows as visible. The script does both.
- Blocking works for channels whose page is blank on the website too, and those blocks reach the tablet or phone, as long as the YouTube Kids app there is signed in with the child's account and the same profile.
- The parent's own Chrome window can show YouTube Kids too; that's why the script checks for `PARENT`. When the child's window is behind another one, browser tools time out or act on the wrong window.
- What is left is decided only by `blocklog.sh todo` (lists vs. logs), never from memory or chat. Without the plan file, an earlier session after `/clear` silently skipped every network that hadn't been started.
- In the YouTube Kids settings, "Unblock videos" removes *all* blocks. To keep a show that is in a list, skip its channels in the plan instead.
- Direct `watch?v=` links don't play on the website, so the test videos in the network files are only for checking on the child's device.
- YouTube Kids has no list of blocked channels. To check later, use `blocklog.sh report`, or the child's watch history (myactivity.google.com, or Google Takeout → YouTube → history).

## Rules

- Only use `ytkBlocker.start`, `ytkBlocker.take` and `ytkBlocker.status` from the script. Never write your own requests to YouTube, and never unblock (no `BLOCKLIST_ACTION_UNBLOCK`, no `clear_blacklist`, no "Unblock videos" in settings).
- Block only channels from `blocklog.sh todo` (or a single channel I asked for with `/investigate-channel`).
- Change nothing else: no content levels, profiles or account settings. Don't sign in, sign out or switch accounts.
- Never type a passcode or password; if YouTube asks for one, ask me.
- No screenshots unless something is unclear.

## Fallback: if the script stops working

YouTube can change its site. If `ytk-blocker.js` keeps returning errors in the child's tab, tell me, and offer the slow way: for each channel from `blocklog.sh todo`, open `https://www.youtubekids.com/channel/<Channel ID>`, use the channel's **⋮** menu → **Block this channel** → confirm, and log `BLOCKED (clicked)` when YouTube says "Channel blocked". A blank channel page can't be blocked this way; log `NOT-BLOCKABLE-HERE`.
