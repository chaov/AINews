import pytest
from app.services.llm_service import MockLLMService, LLMServiceFactory, BaseLLMService


@pytest.mark.asyncio
async def test_mock_generate_summary_short():
    service = MockLLMService()
    result = await service.generate_summary("Short content", max_length=200)
    assert result == "Short content"


@pytest.mark.asyncio
async def test_mock_generate_summary_long():
    service = MockLLMService()
    long_content = "A" * 300
    result = await service.generate_summary(long_content, max_length=200)
    assert len(result) == 203
    assert result.endswith("...")


@pytest.mark.asyncio
async def test_mock_generate_evaluation():
    service = MockLLMService()
    result = await service.generate_evaluation("Some content", "Test Title")
    assert "Test Title" in result
    assert "值得关注" in result


@pytest.mark.asyncio
async def test_mock_extract_tags_enough_words():
    service = MockLLMService()
    result = await service.extract_tags("content", "AI Technology Future")
    assert len(result) == 3
    assert "AI" in result
    assert "Technology" in result
    assert "Future" in result


@pytest.mark.asyncio
async def test_mock_extract_tags_few_words():
    service = MockLLMService()
    result = await service.extract_tags("content", "AI")
    assert result == ["AI"]


@pytest.mark.asyncio
async def test_mock_classify_category_with_list():
    service = MockLLMService()
    result = await service.classify_category("content", "title", ["tech", "finance"])
    assert result == "tech"


@pytest.mark.asyncio
async def test_mock_classify_category_empty_list():
    service = MockLLMService()
    result = await service.classify_category("content", "title", [])
    assert result == "general"


def test_llm_service_factory_get_default():
    service = LLMServiceFactory.get("mock")
    assert isinstance(service, MockLLMService)


def test_llm_service_factory_get_unknown():
    service = LLMServiceFactory.get("unknown_provider")
    assert isinstance(service, MockLLMService)


def test_llm_service_factory_register():
    custom_service = MockLLMService()
    LLMServiceFactory.register("custom", custom_service)
    result = LLMServiceFactory.get("custom")
    assert result is custom_service


@pytest.mark.asyncio
async def test_base_llm_service_is_abstract():
    with pytest.raises(TypeError):
        BaseLLMService()
