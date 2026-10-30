#!/bin/sh
# Bookkeeping for block-channels-prompt.md. Reads results/plan.txt, networks/*.md and the logs results/<network>.txt.
#   sh tools/blocklog.sh todo [N]   the channels still to block, as one line for ytkBlocker.start() (at most N)
#   sh tools/blocklog.sh save       add the lines from ytkBlocker.take() ("network number channelId STATUS", on stdin) to the logs
#   sh tools/blocklog.sh report     one line per network, then the channels that still need attention
# A channel is done when the last log line for its number is BLOCKED… or SKIPPED (parent). Anything else
# (NOT-CONFIRMED, FAILED, and the old click flow's NOT-BLOCKABLE-HERE / UNCERTAIN) is blocked again next time.
# The plan and logs live in results/ of your folder: the repository in a clone, or the folder named by YKB_HOME
# (the plugin's data folder). Your network lists live in networks/ of your folder.
set -e
home=${YKB_HOME:-}
cd "$(dirname "$0")/.."
[ -n "$home" ] || home=.
data=$home/results
mkdir -p "$data"
plan=$data/plan.txt

field() { sed -n "s/\r\$//; s/^$1:[[:space:]]*//p" "$plan" | tr ',\n' '  '; }
skips() { sed -n "s/\r\$//; s/^skip:[[:space:]]*$1[[:space:]]\{1,\}//p" "$plan" | tr ',\n' '  '; }
optional() { case " $(field optional) " in *" $1 "*) echo 1 ;; *) echo 0 ;; esac; }

# the list file of a network: networks/ here (a clone), or networks/ in your folder
netfile() { if [ -f "networks/$1.md" ]; then echo "networks/$1.md"; elif [ -f "$home/networks/$1.md" ]; then echo "$home/networks/$1.md"; fi; }

# one tab-separated line per channel of a network's chosen lists: number, id, state (done/skip/todo), last log status, name
channels() {
  log=$data/$1.txt; [ -f "$log" ] || log=/dev/null
  awk -v OFS='\t' -v logf="$log" -v opt="$(optional "$1")" -v skip=" $(skips "$1") " '
    { sub(/\r$/, "") }
    FILENAME == logf { split($0, f, / \| /); n = f[1]; gsub(/ /, "", n); st[n] = f[3]; next }
    /^## / { sec = ($0 ~ /^## Main list/) || (opt && $0 ~ /^## Optional/); next }
    sec && /^[0-9]+\. / {
      n = $0; sub(/\..*/, "", n)
      if (!match($0, /youtubekids\.com\/channel\/UC[A-Za-z0-9_-]+/)) next
      id = substr($0, RSTART + 24, RLENGTH - 24)   # from the link: names can contain "|", and test videos can be missing
      name = substr($0, length(n) + 3); name = substr(name, 1, index(name, " | " id) - 1)
      state = index(skip, " " n " ") || st[n] ~ /^SKIPPED \(parent\)/ ? "skip" : st[n] ~ /^BLOCKED/ ? "done" : "todo"
      print n, id, state, st[n], name
    }' "$log" "$(netfile "$1")"
}

[ -f "$plan" ] || { echo "No plan.txt in $data yet: start with /block-channel" >&2; exit 1; }
for net in $(field networks); do
  [ -n "$(netfile "$net")" ] || { echo "plan.txt names a network that doesn't exist: $net" >&2; exit 1; }
done

case "$1" in
todo)
  limit=${2:-100000}
  for net in $(field networks); do
    channels "$net" | awk -F'\t' -v net="$net" '$3 == "todo" { print net "/" $1 ":" $2 }'
  done | head -n "$limit" | paste -sd, -
  for net in $(field networks); do
    channels "$net" | awk -F'\t' -v net="$net" '$3 == "todo" { t++ } END { if (t) printf "%s: %d to do\n", net, t }'
  done >&2 ;;
save)
  n=0
  while read -r net num id status; do
    case "$net" in RUNNING|FINISHED|STOPPED|NO|'') continue ;; esac
    case "$net$num" in *[!a-z0-9-]*) echo "skipped a line I can't read: $net $num $id $status" >&2; continue ;; esac
    [ -n "$(netfile "$net")" ] || [ "$net" = manual ] || { echo "skipped a line for an unknown network: $net" >&2; continue; }
    echo "$num | $id | $status" >> "$data/$net.txt"
    n=$((n + 1))
  done
  echo "saved $n lines" ;;
report)
  left=0
  for net in $(field networks); do
    channels "$net" | awk -F'\t' -v net="$net" '
      { total++; if ($3 == "done") d++; else if ($3 == "skip") s++; else t++ }
      END { printf "%s: %d of %d blocked, %d skipped by you, %d to do\n", net, d, total, s, t }'
    left=$((left + $(channels "$net" | awk -F'\t' '$3 == "todo"' | wc -l)))
  done
  [ "$left" -gt 0 ] || echo "ALL DONE"
  for net in $(field networks); do
    channels "$net" | awk -F'\t' -v net="$net" '$3 == "todo" && $4 ~ /^(NOT-CONFIRMED|FAILED)/ { printf "  %s %s: %s (%s)\n", net, $1, $5, $4 }'
  done | awk 'NR == 1 { print "Tried but not confirmed (they are tried again next time):" } 1' ;;
*)
  sed -n '2,6s/^# \{0,1\}//p' "$0"; exit 1 ;;
esac
