import asyncio
import logging
import uuid
from datetime import datetime

import feedparser
import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

IMPACT_MAP = {
    "High": "High",
    "Medium": "Medium",
    "Low": "Low",
    "Holiday": "Low",
}


async def fetch_forex_factory() -> list:
    """Fetch economic calendar from Forex Factory public JSON."""
    url = "https://nfs.forexfactory.net/ff_calendar_thisweek.json"
    results = []
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        for item in data:
            results.append(
                {
                    "id": str(uuid.uuid4()),
                    "source": "Forex Factory",
                    "timestamp": item.get("date", datetime.utcnow().isoformat()),
                    "currency": item.get("country", ""),
                    "importance": IMPACT_MAP.get(item.get("impact", "Low"), "Low"),
                    "event": item.get("title", ""),
                    "actual": item.get("actual") or None,
                    "forecast": item.get("forecast") or None,
                    "previous": item.get("previous") or None,
                    "sentiment": "Pending",
                }
            )
    except Exception as exc:
        logger.error("fetch_forex_factory error: %s", exc)
    return results


async def fetch_investing_rss() -> list:
    """Fetch news from Investing.com RSS feed."""
    url = "https://www.investing.com/rss/news.rss"
    results = []
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            response = await client.get(url)
            response.raise_for_status()
            content = response.text
        feed = feedparser.parse(content)
        for entry in feed.entries[:20]:
            results.append(
                {
                    "id": str(uuid.uuid4()),
                    "source": "Investing.com",
                    "timestamp": entry.get("published", datetime.utcnow().isoformat()),
                    "currency": "USD",
                    "importance": "Medium",
                    "event": entry.get("title", ""),
                    "actual": None,
                    "forecast": None,
                    "previous": None,
                    "sentiment": "Pending",
                }
            )
    except Exception as exc:
        logger.error("fetch_investing_rss error: %s", exc)
    return results


async def fetch_dailyfx() -> list:
    """Scrape news headlines from DailyFX."""
    url = "https://www.dailyfx.com/forex/fundamental/daily_briefing/daily_pieces/"
    results = []
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")
        articles = soup.select("article") or soup.select(".article-list-item")
        for article in articles[:20]:
            title_tag = article.find(["h2", "h3", "h4", "a"])
            title = title_tag.get_text(strip=True) if title_tag else ""
            if not title:
                continue
            results.append(
                {
                    "id": str(uuid.uuid4()),
                    "source": "DailyFX",
                    "timestamp": datetime.utcnow().isoformat(),
                    "currency": "USD",
                    "importance": "Medium",
                    "event": title,
                    "actual": None,
                    "forecast": None,
                    "previous": None,
                    "sentiment": "Pending",
                }
            )
    except Exception as exc:
        logger.error("fetch_dailyfx error: %s", exc)
    return results


async def collect_all_news() -> list:
    results = await asyncio.gather(
        fetch_forex_factory(),
        fetch_investing_rss(),
        fetch_dailyfx(),
    )
    flat_list = [item for sublist in results for item in sublist]
    return sorted(flat_list, key=lambda x: x["timestamp"], reverse=True)
