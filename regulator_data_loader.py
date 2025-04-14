# regulator_data_loader.py

from data_collectors import run_whitehouse_scraper, run_cfpb_scraper, run_rss_parser
from datetime import datetime

# ✅ Hardcoded source type mapping
REGULATOR_METHODS = {
    "White House": "Scraper",
    "CFPB": "Scraper",
    "Federal Reserve": "RSS",
    "BIS": "RSS",
    "OCC": "RSS",
    "FDIC": "RSS"
}

# ✅ Base URLs for scraping (informational)
SCRAPER_URLS = {
    "White House": "https://www.whitehouse.gov/news/",
    "CFPB": "https://www.consumerfinance.gov/about-us/newsroom/"
}

# ✅ RSS feed URLs
RSS_FEEDS = {
    "Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "FDIC": "https://public.govdelivery.com/topics/USFDIC_26/feed.rss",
    "OCC": "https://www.occ.gov/news-issuances/news-releases/index.xml",
    "BIS": "https://www.bis.org/doclist/rss_all_categories.rss"
}


# ✅ Main dispatcher
def run_all_sources(selected_regulators, start_date: str, end_date: str):
    all_outputs = []

    for regulator in selected_regulators:
        method = REGULATOR_METHODS.get(regulator)
        if not method:
            continue

        try:
            if method == "Scraper":
                if regulator == "White House":
                    entries = run_whitehouse_scraper(start_date, end_date)
                elif regulator == "CFPB":
                    entries = run_cfpb_scraper(start_date, end_date)
                else:
                    entries = []
            elif method == "RSS":
                rss_url = RSS_FEEDS.get(regulator)
                entries = run_rss_parser(regulator, rss_url, start_date, end_date)
            else:
                entries = []

            all_outputs.append({
                "Regulator": regulator,
                "Method": method,
                "Count": len(entries),
                "Entries": entries,
                "SourceURL": RSS_FEEDS.get(regulator) if method == "RSS" else SCRAPER_URLS.get(regulator)
            })

        except Exception as e:
            all_outputs.append({
                "Regulator": regulator,
                "Method": method,
                "Count": 0,
                "Entries": [],
                "Error": str(e),
                "SourceURL": RSS_FEEDS.get(regulator) if method == "RSS" else SCRAPER_URLS.get(regulator)
            })

    return all_outputs

# ✅ Expose to UI
AVAILABLE_REGULATORS = list(REGULATOR_METHODS.keys())
