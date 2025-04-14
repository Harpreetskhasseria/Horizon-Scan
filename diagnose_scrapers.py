# diagnose_scrapers.py

from data_collectors import (
    run_whitehouse_scraper,
    run_cfpb_scraper,
    run_rss_parser
)

from regulator_data_loader import RSS_FEEDS
from datetime import datetime
from pprint import pprint

START_DATE = "2025-03-16"
END_DATE = "2025-04-14"

print("\n🔍 Diagnosing White House Scraper")
try:
    entries_wh = run_whitehouse_scraper(START_DATE, END_DATE)
    print(f"✅ White House entries: {len(entries_wh)}")
    pprint(entries_wh[:2])
except Exception as e:
    print("❌ Error in White House scraper:", e)

print("\n🔍 Diagnosing CFPB Scraper")
try:
    entries_cfpb = run_cfpb_scraper(START_DATE, END_DATE)
    print(f"✅ CFPB entries: {len(entries_cfpb)}")
    pprint(entries_cfpb[:2])
except Exception as e:
    print("❌ Error in CFPB scraper:", e)

print("\n🔍 Diagnosing RSS Feeds")
for regulator, feed_url in RSS_FEEDS.items():
    try:
        print(f"\n🔄 Fetching from: {regulator} ({feed_url})")
        entries = run_rss_parser(regulator, feed_url, START_DATE, END_DATE)
        print(f"✅ {regulator} entries: {len(entries)}")
        pprint(entries[:2])
    except Exception as e:
        print(f"❌ Error in {regulator} RSS feed:", e)
