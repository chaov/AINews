import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.crawler_agent import CrawlerAgent


@pytest.fixture
def crawler():
    return CrawlerAgent()


@pytest.mark.asyncio
async def test_is_duplicate_found(crawler):
    mock_db = MagicMock()
    mock_db.news.find_one = AsyncMock(return_value={"_id": "existing"})
    crawler.db = mock_db

    result = await crawler.is_duplicate("Test Title", "https://example.com")
    assert result is True


@pytest.mark.asyncio
async def test_is_duplicate_not_found(crawler):
    mock_db = MagicMock()
    mock_db.news.find_one = AsyncMock(return_value=None)
    crawler.db = mock_db

    result = await crawler.is_duplicate("New Title", "https://example.com/new")
    assert result is False


@pytest.mark.asyncio
async def test_process_news_item_duplicate(crawler):
    mock_db = MagicMock()
    mock_db.news.find_one = AsyncMock(return_value={"_id": "existing"})
    crawler.db = mock_db

    result = await crawler.process_news_item({
        "title": "Duplicate",
        "url": "https://example.com",
    })
    assert result is None


@pytest.mark.asyncio
async def test_process_news_item_new(crawler):
    mock_db = MagicMock()
    mock_db.news.find_one = AsyncMock(return_value=None)
    crawler.db = mock_db

    mock_llm = MagicMock()
    mock_llm.generate_summary = AsyncMock(return_value="AI Summary")
    mock_llm.generate_evaluation = AsyncMock(return_value="AI Evaluation")
    mock_llm.extract_tags = AsyncMock(return_value=["AI", "Tech"])
    mock_llm.classify_category = AsyncMock(return_value="tech")
    crawler.llm_service = mock_llm

    result = await crawler.process_news_item({
        "title": "New AI Breakthrough",
        "content": "Content about AI",
        "url": "https://example.com/new",
        "source": "TechNews",
    }, category="tech")

    assert result is not None
    assert result["title"] == "New AI Breakthrough"
    assert result["summary"] == "AI Summary"
    assert result["evaluation"] == "AI Evaluation"
    assert result["tags"] == ["AI", "Tech"]
    assert result["category"] == "tech"
    assert result["source_name"] == "TechNews"
    assert result["is_active"] is True
    assert result["view_count"] == 0


@pytest.mark.asyncio
async def test_crawl_all_sources_no_sources(crawler):
    mock_db = MagicMock()
    mock_db.news_sources.find.return_value = MagicMock(
        to_list=AsyncMock(return_value=[])
    )
    crawler.db = mock_db

    result = await crawler.crawl_all_sources()
    assert result["crawled"] == 0
    assert result["sources"] == 0


@pytest.mark.asyncio
async def test_fetch_rss_feed_error(crawler):
    result = await crawler.fetch_rss_feed("not-a-valid-url")
    assert result == []


@pytest.mark.asyncio
async def test_fetch_html_page_error(crawler):
    result = await crawler.fetch_html_page("http://nonexistent-domain-12345.com")
    assert result is None
