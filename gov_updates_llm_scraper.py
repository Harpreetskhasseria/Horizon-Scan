# gov_updates_llm_scraper.py

import sys
import asyncio
import feedparser
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from openai import OpenAI

from dotenv import load_dotenv
import os

# Load variables from .env into environment
load_dotenv()


# 🔐 OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

print("✅ Running NEW v1 OpenAI SDK version")

# ✅ SET YOUR OPENAI KEY HERE
client = OpenAI(api_key=openai.api_key)

# ----------------------------------------
# ✅ GPT-based structured field extractor
def extract_structured_fields(title, summary, date, link, regulator):
    prompt = f"""
You are a metadata extraction assistant. Given the following update, extract the structured fields.

Respond in this JSON format:
{{
  "Date": "...",
  "Topic": "...",
  "Summary": "...",
  "Link": "...",
  "Regulator": "..."
}}

Title: {title}
Summary: {summary}
Date: {date}
Link: {link}
Regulator: {regulator}
"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        return {
            "Date": date,
            "Topic": title,
            "Summary": summary,
            "Link": link,
            "Regulator": regulator,
            "Error": str(e)
        }

# ----------------------------------------
# ✅ White House Scraper
async def scrape_whitehouse():
    url = "https://www.whitehouse.gov/news/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        html = await page.content()
        await browser.close()
        return html

def run_whitehouse(start, end):
    html = asyncio.run(scrape_whitehouse())
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.select('li.wp-block-post')
    results = []

    for article in articles:
        title_tag = article.find('h2', class_='wp-block-post-title')
        if not title_tag or not title_tag.find('a'):
            continue
        title = title_tag.find('a').get_text(strip=True)
        link = title_tag.find('a')['href']
        if not link.startswith("http"):
            link = "https://www.whitehouse.gov" + link

        date_tag = article.find('time')
        pub_date = date_tag.get('datetime', '')[:10]
        if not pub_date:
            continue

        pub_dt = datetime.strptime(pub_date, "%Y-%m-%d")
        if not (start <= pub_dt <= end):
            continue

        summary_tag = article.find('p')
        summary = summary_tag.get_text(strip=True) if summary_tag else ""

        structured = extract_structured_fields(title, summary, pub_date, link, "White House")
        results.append(structured)
        time.sleep(1)

    return results

# ----------------------------------------
# ✅ CFPB Scraper
async def scrape_cfpb():
    url = "https://www.consumerfinance.gov/about-us/newsroom/"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        await page.wait_for_load_state('networkidle')
        html = await page.content()
        await browser.close()
        return html

def run_cfpb(start, end):
    html = asyncio.run(scrape_cfpb())
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all("article")
    results = []

    for article in articles:
        title_tag = article.find("h2")
        if not title_tag or not title_tag.find("a"):
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag.find("a")["href"]
        if not link.startswith("http"):
            link = "https://www.consumerfinance.gov" + link

        date_tag = article.find("time")
        pub_date = date_tag.get("datetime", "")[:10]
        if not pub_date:
            continue

        pub_dt = datetime.strptime(pub_date, "%Y-%m-%d")
        if not (start <= pub_dt <= end):
            continue

        summary_tag = article.find("p")
        summary = summary_tag.get_text(strip=True) if summary_tag else ""

        structured = extract_structured_fields(title, summary, pub_date, link, "CFPB")
        results.append(structured)
        time.sleep(1)

    return results

# ----------------------------------------
# ✅ RSS Parser
RSS_FEEDS = {
    "Federal Reserve": "https://www.federalreserve.gov/feeds/press_all.xml",
    "FDIC": "https://public.govdelivery.com/topics/USFDIC_26/feed.rss",
    "OCC": "https://www.occ.gov/news-issuances/news-releases/index.xml",
    "BIS": "https://www.bis.org/doclist/rss_all_categories.rss"
}

def run_rss(regulator, feed_url, start, end):
    import requests
    from dateutil import parser as date_parser

    print(f"🌐 Fetching feed for {regulator}...")
    resp = requests.get(feed_url, headers={"User-Agent": "Mozilla/5.0"})
    parsed = feedparser.parse(resp.content)

    print(f"📡 Parsed {len(parsed.entries)} entries for {regulator}")
    results = []

    for entry in parsed.entries:
        title = entry.get("title", "")
        summary = entry.get("summary", "")
        link = entry.get("link", "")
        date_raw = entry.get("published", "") or entry.get("updated", "")

        try:
            pub_dt = date_parser.parse(date_raw).date()
        except Exception as e:
            print(f"❌ Failed to parse date: {e} | Raw: {date_raw}")
            continue

        if not (start.date() <= pub_dt <= end.date()):
            print(f"⏩ Skipping outside range: {pub_dt}")
            continue

        structured = extract_structured_fields(title, summary, pub_dt.strftime("%Y-%m-%d"), link, regulator)
        results.append(structured)
        time.sleep(1)

    print(f"✅ {len(results)} entries kept after filtering for {regulator}")
    return results

# ----------------------------------------
# ✅ Main Runner
def main():
    args = sys.argv[1:]
    if len(args) < 3:
        print("Usage: python gov_updates_llm_scraper.py START_DATE END_DATE [REGULATORS...]")
        sys.exit(1)

    start_date = datetime.strptime(args[0], "%Y-%m-%d")
    end_date = datetime.strptime(args[1], "%Y-%m-%d")
    selected = args[2:]

    final = []

    for regulator in selected:
        print(f"🔍 Fetching: {regulator}")
        if regulator == "White House":
            entries = run_whitehouse(start_date, end_date)
            method = "Scraper"
            url = "https://www.whitehouse.gov/news/"
        elif regulator == "CFPB":
            entries = run_cfpb(start_date, end_date)
            method = "Scraper"
            url = "https://www.consumerfinance.gov/about-us/newsroom/"
        elif regulator in RSS_FEEDS:
            entries = run_rss(regulator, RSS_FEEDS[regulator], start_date, end_date)
            method = "RSS"
            url = RSS_FEEDS[regulator]
        else:
            entries = []
            method = "Unknown"
            url = ""

        final.append({
            "Regulator": regulator,
            "Method": method,
            "Count": len(entries),
            "SourceURL": url,
            "Entries": entries
        })

    with open("scraper_output.json", "w", encoding="utf-8") as f:
        json.dump(final, f, indent=2)

    print("✅ Done! Results saved to scraper_output.json")

# ----------------------------------------
if __name__ == "__main__":
    main()
