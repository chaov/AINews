from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import os


class BaseLLMService(ABC):
    @abstractmethod
    async def generate_summary(self, content: str, max_length: int = 200) -> str:
        pass

    @abstractmethod
    async def generate_evaluation(self, content: str, title: str) -> str:
        pass

    @abstractmethod
    async def extract_tags(self, content: str, title: str) -> list[str]:
        pass

    @abstractmethod
    async def classify_category(self, content: str, title: str, categories: list[str]) -> str:
        pass


class MockLLMService(BaseLLMService):
    async def generate_summary(self, content: str, max_length: int = 200) -> str:
        if len(content) <= max_length:
            return content
        return content[:max_length] + "..."

    async def generate_evaluation(self, content: str, title: str) -> str:
        return f"这篇关于「{title}」的资讯内容值得关注，建议进一步了解详情。"

    async def extract_tags(self, content: str, title: str) -> list[str]:
        words = title.split()
        return words[:3] if len(words) >= 3 else words

    async def classify_category(self, content: str, title: str, categories: list[str]) -> str:
        if not categories:
            return "general"
        return categories[0]


class LangChainLLMService(BaseLLMService):
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            try:
                from langchain_openai import ChatOpenAI
                kwargs = {
                    "model": self._model,
                    "api_key": self._api_key,
                    "temperature": 0.3,
                    "max_tokens": 500,
                }
                if self._base_url:
                    kwargs["base_url"] = self._base_url
                self._llm = ChatOpenAI(**kwargs)
            except ImportError:
                raise ImportError("langchain-openai is required for LangChainLLMService")
        return self._llm

    async def generate_summary(self, content: str, max_length: int = 200) -> str:
        llm = self._get_llm()
        from langchain_core.messages import HumanMessage
        response = await llm.ainvoke([
            HumanMessage(content=f"请将以下内容总结为{max_length}字以内的中文摘要，只返回摘要内容：\n\n{content}")
        ])
        return response.content.strip()

    async def generate_evaluation(self, content: str, title: str) -> str:
        llm = self._get_llm()
        from langchain_core.messages import HumanMessage
        response = await llm.ainvoke([
            HumanMessage(content=f"请对以下资讯进行简短评价（50-100字），分析其价值和影响，只返回评价内容：\n标题：{title}\n内容：{content}")
        ])
        return response.content.strip()

    async def extract_tags(self, content: str, title: str) -> list[str]:
        llm = self._get_llm()
        from langchain_core.messages import HumanMessage
        response = await llm.ainvoke([
            HumanMessage(content=f"请从以下资讯中提取3-5个关键词标签，只返回标签，用逗号分隔：\n标题：{title}\n内容：{content[:500]}")
        ])
        tags = [t.strip() for t in response.content.strip().split(",") if t.strip()]
        return tags[:5]

    async def classify_category(self, content: str, title: str, categories: list[str]) -> str:
        if not categories:
            categories = ["tech", "finance", "education", "health", "entertainment", "sports", "world"]
        llm = self._get_llm()
        from langchain_core.messages import HumanMessage
        response = await llm.ainvoke([
            HumanMessage(content=f"请判断以下资讯属于哪个分类，只返回分类代码：\n可选分类：{', '.join(categories)}\n标题：{title}\n内容：{content[:300]}")
        ])
        result = response.content.strip().lower()
        for cat in categories:
            if cat.lower() in result:
                return cat
        return categories[0] if categories else "general"


class LLMServiceFactory:
    _services: Dict[str, BaseLLMService] = {}

    @classmethod
    def register(cls, name: str, service: BaseLLMService):
        cls._services[name] = service

    @classmethod
    def get(cls, name: str = "mock") -> BaseLLMService:
        return cls._services.get(name, MockLLMService())


LLMServiceFactory.register("mock", MockLLMService())


async def get_llm_service() -> BaseLLMService:
    from app.core.config import settings

    if settings.LLM_PROVIDER and settings.LLM_API_KEY:
        if settings.LLM_PROVIDER == "langchain":
            service = LangChainLLMService(
                api_key=settings.LLM_API_KEY,
                model=settings.LLM_MODEL or "gpt-3.5-turbo",
            )
            LLMServiceFactory.register("langchain", service)
            return service
        return LLMServiceFactory.get(settings.LLM_PROVIDER)
    return LLMServiceFactory.get("mock")
