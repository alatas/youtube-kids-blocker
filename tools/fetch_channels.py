"""Step 1 of the history workflow: look up every channel in your child's Takeout watch history.

Reads research/**/watch-history.json and writes research/channels.json (public channel data from the API).
usage: python -I tools/fetch_channels.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ytapi

ids = set(ytapi.view_counts(ytapi.history(required=True)))
res = ytapi.channels(ids, 'snippet,statistics,status,topicDetails')
ytapi.save(res, ytapi.work('channels.json'))
print(f'{len(ids)} channels in the history, {len(res)} found -> research/channels.json')
print(ytapi.quota())
