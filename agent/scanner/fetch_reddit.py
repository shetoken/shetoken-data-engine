"""
SHEtoken Agent — Reddit Scanner (RSS version)
===============================================
Uses Reddit's public RSS feeds — NO API key, NO approval needed.
Reddit serves public subreddit content as RSS at:
  https://www.reddit.com/r/{subreddit}/.rss

This replaces the PRAW version which requires API approval.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
# Reddit RSS feeds are handled directly by fetch_rss.py
# This file exists as a no-op placeholder.
# Reddit sources are defined in config.py NEWS_SOURCES
# and fetched automatically by fetch_all_sources()

def fetch_all_reddit(days_back=7):
    """Reddit handled via RSS in config.py — no separate fetch needed."""
    return []
