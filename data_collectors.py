# data_collectors.py

import feedparser
from bs4 import BeautifulSoup
from datetime import datetime
import asyncio
from playwright.async_api import async_playwright
import openai
import json
import time

from dotenv import load_dotenv
import os

# Load variables from .env into environment
load_dotenv()


# 🔐 OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ LLM-based structured field extractor
def extract_structured_fields_with_llm(raw_title, raw_summary, raw_date, raw_link, regulator):
    prompt = f"""
You are a document parsing assistant. Extract structured metadata from the following regulatory update.
Do not summarize or rephrase. Preserve the original phrasing and meaning.

Respond strictly in this JSON format:
{{
  "Date": "...",
  "Topic": "...",
  "Summary": "...",
  "Link": "...",
  "Regulator": "..."
}}

Input:
Title: {raw_title}
Summary: {raw_summary}
Date: {raw_date}
Link: {raw_link}
Regulator: {regulator}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            top_p=0.1,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        return json.loads(content)
    except Exception as e:
        return {
            "Date": raw_date,
            "Topic": raw_title,
            "Summary": raw_summary,
            "Link": raw_link,
            "Regulator": regulator,
            "Error": str(e)
        }

# ---------------------------
# ✅ RSS Parser
def run_rss_parser(regulator_name, feed_url, start_date, end_date):
    parsed = feedparser.parse(feed_url)
    entries = []
    start_dt = datetime.fromisoformat(start_date)
    end_dt = datetime.fromisoformat(end_date)

    for entry in parsed.entries:
        published = entry.get("published", "") or entry.get("updated", "")
        try:
            pub_date = datetime.strptime(published[:10], "%Y-%m-%d")
        except:
            continue

        print(f"[{regulator_name}] RSS Entry: {entry.get('title')} | Date: {published[:10]}")

        if not (start_dt <= pub_date <= end_dt):
            continue

        raw = {
            "title": entry.get("title", ""),
            "summary": entry.get("summary", ""),
            "date": pub_date.strftime("%Y-%m-%d"),
            "link": entry.get("link", "")
        }

        structured = extract_structured_fields_with_llm(
            raw["title"], raw["summary"], raw["date"], raw["link"], regulator_name
        )
        entries.append(structured)
        time.sleep(1)

    return entries

# ---------------------------
# ✅ White House Scraper (async)
async def fetch_whitehouse_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.whitehouse.gov/news/")
        await page.wait_for_load_state('networkidle')
        html = await page.content()
        await browser.close()
        return html

def run_whitehouse_scraper(start_date, end_date):
    html = asyncio.run(fetch_whitehouse_html())
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.select('li.wp-block-post')
    output = []

    for article in articles:
        title_tag = article.find('h2', class_='wp-block-post-title')
        if not title_tag or not title_tag.find('a'):
            continue
        title = title_tag.find('a').get_text(strip=True)
        link = title_tag.find('a')['href']
        if not link.startswith("http"):
            link = "https://www.whitehouse.gov" + link

        date_tag = article.find('time')
        pub_date = date_tag.get('datetime', '')[:10] if date_tag else ''
        if not pub_date:
            continue

        print(f"[WH] Found article: {title} | Date: {pub_date}")

        pub_dt = datetime.strptime(pub_date, "%Y-%m-%d")
        if not (datetime.fromisoformat(start_date) <= pub_dt <= datetime.fromisoformat(end_date)):
            continue

        summary_tag = article.find('p')
        summary = summary_tag.get_text(strip=True) if summary_tag else ""

        record = extract_structured_fields_with_llm(title, summary, pub_date, link, "White House")
        output.append(record)
        time.sleep(1)

    return output

# ---------------------------
# ✅ CFPB Scraper (async)
async def fetch_cfpb_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.consumerfinance.gov/about-us/newsroom/")
        await page.wait_for_load_state('networkidle')
        html = await page.content()
        await browser.close()
        return html

def run_cfpb_scraper(start_date, end_date):
    html = asyncio.run(fetch_cfpb_html())
    soup = BeautifulSoup(html, 'html.parser')
    articles = soup.find_all("article")
    output = []

    for article in articles:
        title_tag = article.find("h2")
        if not title_tag or not title_tag.find("a"):
            continue
        title = title_tag.get_text(strip=True)
        link = title_tag.find("a")["href"]
        if not link.startswith("http"):
            link = "https://www.consumerfinance.gov" + link

        date_tag = article.find("time")
        pub_date = date_tag.get("datetime", "")[:10] if date_tag else ""
        if not pub_date:
            continue

        print(f"[CFPB] Found article: {title} | Date: {pub_date}")

        pub_dt = datetime.strptime(pub_date, "%Y-%m-%d")
        if not (datetime.fromisoformat(start_date) <= pub_dt <= datetime.fromisoformat(end_date)):
            continue

        summary_tag = article.find("p")
        summary = summary_tag.get_text(strip=True) if summary_tag else ""

        record = extract_structured_fields_with_llm(title, summary, pub_date, link, "CFPB")
        output.append(record)
        time.sleep(1)

    return output
