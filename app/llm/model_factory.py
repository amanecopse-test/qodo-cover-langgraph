import asyncio
from abc import ABC, abstractmethod

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.model_factory import ModelParams, GeminiParams


class BaseModelLoader(ABC):
    @abstractmethod
    async def load_llm(self, parameters: ModelParams):
        pass


class GeminiLoader(BaseModelLoader):
    async def load_llm(self, parameters: GeminiParams) -> ChatGoogleGenerativeAI:
        return await asyncio.to_thread(
            lambda: ChatGoogleGenerativeAI(
                model=parameters.llm_name,
                api_key=parameters.api_key,
                temperature=parameters.temperature,
                max_tokens=parameters.max_tokens,
            )
        )


class ModelFactory:
    _registry = {
        GeminiParams.MODEL_TYPE: GeminiLoader(),
    }

    async def load_llm(self, params: ModelParams) -> BaseChatModel:
        model_type = params.MODEL_TYPE
        if model_type not in self._registry:
            raise ValueError(f"Unsupported model type: {model_type}")
        return await self._registry[model_type].load_llm(params)
