import asyncio
import feedparser
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from app.core.database import get_database
from app.services.llm_service import get_llm_service


class CrawlerAgent:
    def __init__(self):
        self.db = None
        self.llm_service = None

    async def initialize(self):
        self.db = get_database()
        self.llm_service = await get_llm_service()

    async def fetch_rss_feed(self, url: str) -> List[Dict[str, Any]]:
        try:
            feed = feedparser.parse(url)
            items = []
            for entry in feed.entries:
                items.append({
                    "title": entry.get("title", ""),
                    "content": entry.get("summary", entry.get("description", "")),
                    "url": entry.get("link", ""),
                    "published_at": entry.get("published_parsed") or entry.get("updated_parsed"),
                    "source": feed.feed.get("title", url),
                })
            return items
        except Exception as e:
            print(f"Error fetching RSS feed {url}: {e}")
            return []

    async def fetch_html_page(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "lxml")

                title = soup.find("title")
                title = title.get_text(strip=True) if title else ""

                meta_desc = soup.find("meta", attrs={"name": "description"})
                content = meta_desc.get("content", "") if meta_desc else ""

                return {
                    "title": title,
                    "content": content,
                    "url": url,
                    "published_at": datetime.now(timezone.utc),
                    "source": url,
                }
        except Exception as e:
            print(f"Error fetching HTML page {url}: {e}")
            return None

    async def is_duplicate(self, title: str, source_url: str) -> bool:
        if not self.db:
            await self.initialize()

        existing = await self.db.news.find_one({
            "source_url": source_url,
            "title": title,
        })
        return existing is not None

    async def process_news_item(self, item: Dict[str, Any], category: str = "general") -> Optional[Dict[str, Any]]:
        if await self.is_duplicate(item["title"], item.get("url", "")):
            return None

        content = item.get("content", "")
        title = item.get("title", "")

        summary = await self.llm_service.generate_summary(content)
        evaluation = await self.llm_service.generate_evaluation(content, title)
        tags = await self.llm_service.extract_tags(content, title)
        predicted_category = await self.llm_service.classify_category(content, title, [])

        news_data = {
            "title": title,
            "summary": summary,
            "evaluation": evaluation,
            "content": content,
            "source_name": item.get("source", "Unknown"),
            "source_url": item.get("url", ""),
            "category": category or predicted_category,
            "tags": tags,
            "published_at": item.get("published_at", datetime.now(timezone.utc)),
            "is_active": True,
            "view_count": 0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

        return news_data

    async def crawl_all_sources(self):
        if not self.db:
            await self.initialize()

        sources = await self.db.news_sources.find({"is_active": True}).to_list(length=100)
        total_crawled = 0

        for source in sources:
            try:
                if source["type"] == "rss":
                    items = await self.fetch_rss_feed(source["url"])
                elif source["type"] == "html":
                    items = [await self.fetch_html_page(source["url"])]
                    items = [i for i in items if i]
                else:
                    continue

                for item in items:
                    processed = await self.process_news_item(item)
                    if processed:
                        await self.db.news.insert_one(processed)
                        total_crawled += 1

                await self.db.news_sources.update_one(
                    {"_id": source["_id"]},
                    {"$set": {"last_fetch_at": datetime.now(timezone.utc)}}
                )
            except Exception as e:
                print(f"Error processing source {source['name']}: {e}")
                continue

        return {"crawled": total_crawled, "sources": len(sources)}


async def run_crawler():
    agent = CrawlerAgent()
    await agent.initialize()
    return await agent.crawl_all_sources()


if __name__ == "__main__":
    from app.core.database import connect_to_mongodb, close_mongodb_connection

    async def main():
        await connect_to_mongodb()
        try:
            result = await run_crawler()
            print(f"Crawl result: {result}")
        finally:
            await close_mongodb_connection()

    asyncio.run(main())
