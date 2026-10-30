// YouTube Kids channel blocker. Claude pastes this whole file into a youtubekids.com tab (javascript tool).
// It reuses the site's own requests: "kids/update_blacklist" blocks a channel (what ⋮ → "Block this channel"
// sends) and "browse" checks it. It only ever sends the BLOCK action: never unblock, never clear_blacklist.
// Running the file sets it up and returns "CHILD" or "PARENT" (which account the tab is signed in with). Then:
//   ytkBlocker.start("network/number:UCxxxx,...")   starts blocking in the background (list from blocklog.sh todo)
//   ytkBlocker.take()                               progress line, then each finished "network number channelId STATUS"
// Channels are blocked 20 at a time, 0.5 s apart; then the same 20 are checked. A block takes 10-15 s to show.
await (async () => {
  const sleep = ms => new Promise(r => setTimeout(r, ms));
  if (!/(^|\.)youtubekids\.com$/.test(location.hostname)) return 'ERROR: this tab is not on youtubekids.com';

  if (!window.ytkBlocker) {
    let H = null, C = null;   // headers and context of the site's last browse request (the signed-in child profile)
    const X = XMLHttpRequest.prototype, open = X.open, send = X.send, setHeader = X.setRequestHeader;
    X.open = function (m, u) { this.ytkUrl = String(u); this.ytkHeaders = {}; return open.apply(this, arguments); };
    X.setRequestHeader = function (k, v) { if (this.ytkHeaders) this.ytkHeaders[k] = v; return setHeader.apply(this, arguments); };
    X.send = function (body) {
      if (/\/youtubei\/v1\/browse/.test(this.ytkUrl)) {
        try {
          const j = JSON.parse(body);
          if (j.context && j.context.client && j.context.client.kidsAppInfo) { H = { ...this.ytkHeaders }; C = j.context; }
        } catch (e) {}
      }
      return send.apply(this, arguments);
    };
    const api = async (path, body) => {
      const r = await fetch(`/youtubei/v1/${path}?alt=json&prettyPrint=false`,
        { method: 'POST', credentials: 'include', headers: H, body: JSON.stringify({ context: C, ...body }) });
      return { status: r.status, retryAfter: r.headers.get('retry-after'), j: await r.json().catch(() => null) };
    };
    // seconds to wait after a 429: the Retry-After header (seconds or a date), else 60 s; at most 15 minutes
    const retryDelay = h => {
      const s = /^\d+$/.test(h || '') ? +h : h ? (Date.parse(h) - Date.now()) / 1000 : NaN;
      return Math.min(900, Math.max(5, Number.isFinite(s) ? Math.ceil(s) : 60));
    };

    const ytk = window.ytkBlocker = {
      ready: () => !!(H && C),
      // a parent account sends a "kidsParent" token for the profile it manages; the child's own account doesn't
      parentAccount: () => !!(C && C.user && C.user.kidsParent),
      // VISIBLE: the child can open the channel. HIDDEN: blocked, or not available to this profile.
      async status(id) {
        const { status, j } = await api('browse', { browseId: id });
        if (status !== 200 || !j) return 'ERROR';
        if (j.alerts) return 'HIDDEN';
        const h = j.header && j.header.c4TabbedHeaderRenderer;
        return h && h.channelId === id ? 'VISIBLE' : 'ERROR';
      },
      async block(id) {
        const { status, retryAfter, j } = await api('kids/update_blacklist',
          { items: [{ externalChannelId: id, action: 'BLOCKLIST_ACTION_BLOCK' }] });
        if (j && j.responseRenderer && j.responseRenderer.kidsBlacklistResponseToastRenderer) return 'OK';
        if (status === 429) ytk.lastRetryAfter = retryAfter;
        return `HTTP ${status}`;
      },
      job: null,
      start(list) {
        if (!ytk.ready()) return 'ERROR: not set up; run ytk-blocker.js again';
        if (ytk.parentAccount()) return 'ERROR: this tab is signed in with a parent account, not the child';
        if (ytk.job && !ytk.job.finished) return `ERROR: a job is still running (${ytk.job.done}/${ytk.job.total})`;
        const items = String(list).split(',').map(s => s.trim()).filter(Boolean).map(s => {
          const i = s.lastIndexOf(':');
          return { key: s.slice(0, i).replace('/', ' '), id: s.slice(i + 1) };
        });
        if (!items.length || items.some(it => !/^UC[\w-]{22}$/.test(it.id) || !/^[a-z0-9-]+ \d+$/.test(it.key)))
          return 'ERROR: expected "network/number:UCxxxx,..." (the output of blocklog.sh todo)';
        ytk.job = { total: items.length, done: 0, lines: [], taken: 0, finished: false, stopped: null };
        run(ytk.job, items);
        return `started ${items.length} channels`;
      },
      take() {
        const job = ytk.job;
        if (!job) return 'NO JOB';
        const lines = job.lines.slice(job.taken);
        job.taken = job.lines.length;
        const head = job.stopped ? `STOPPED ${job.done}/${job.total}: ${job.stopped}`
          : `${job.finished ? 'FINISHED' : 'RUNNING'} ${job.done}/${job.total}${job.waiting ? ` (${job.waiting})` : ''}`;
        return [head, ...lines].join('\n');
      },
    };

    const run = async (job, items) => {
      let refused = 0;
      for (let i = 0; i < items.length; i += 20) {
        const chunk = items.slice(i, i + 20);
        for (const it of chunk) {
          let r = await ytk.block(it.id).catch(() => 'network error');
          // "too many requests": wait as long as YouTube asks (up to 3 times per channel), then try the same channel again
          for (let waits = 0; r === 'HTTP 429' && waits < 3; waits++) {
            const s = retryDelay(ytk.lastRetryAfter);
            job.waiting = `waiting ${s} s: YouTube asked to slow down (Retry-After: ${ytk.lastRetryAfter || 'none'})`;
            await sleep(s * 1000);
            job.waiting = null;
            r = await ytk.block(it.id).catch(() => 'network error');
          }
          if (r !== 'OK' && r !== 'HTTP 429') { await sleep(5000); r = await ytk.block(it.id).catch(() => 'network error'); }
          it.sent = r === 'OK';
          if (it.sent) refused = 0;
          else {
            it.result = `FAILED (${r})`;
            if (++refused >= 5) job.stopped = 'YouTube refused 5 blocks in a row';
          }
          if (job.stopped) break;
          await sleep(500);
        }
        if (!job.stopped) {
          await sleep(15000);
          for (let round = 0; round < 2; round++) {
            for (const it of chunk) {
              if (it.sent && !it.result && await ytk.status(it.id).catch(() => 'ERROR') === 'HIDDEN') it.result = 'BLOCKED';
            }
            if (chunk.every(it => it.result) || round) break;
            await sleep(20000);
          }
        }
        for (const it of chunk) {
          if (it.sent === undefined) continue;   // not reached before a stop: stays to do
          job.lines.push(`${it.key} ${it.id} ${it.result || 'NOT-CONFIRMED (YouTube said blocked, still visible)'}`);
          job.done++;
        }
        if (job.stopped) break;
      }
      job.finished = true;
    };
  }

  const ytk = window.ytkBlocker;
  if (!ytk.ready()) {   // make the site send one request, so its headers and profile context can be reused
    for (const tab of document.querySelectorAll('ytk-kids-category-tab-renderer')) {
      tab.click();
      for (let t = 0; t < 8 && !ytk.ready(); t++) await sleep(500);
      if (ytk.ready()) break;
    }
  }
  if (!ytk.ready()) return 'ERROR: could not read the site\'s requests. Open https://www.youtubekids.com (home page) and run this again';
  return ytk.parentAccount() ? 'PARENT' : 'CHILD';
})();
