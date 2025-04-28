from enum import Enum
from typing import ClassVar

from pydantic import BaseModel, SecretStr, Field


class LlmName(Enum):
    GEMINI_2_FLASH = "gemini-2.0-flash"
    CLAUDE_3_7_SONNET = "claude-3-7-sonnet-20250219"


class GeminiParams(BaseModel):
    MODEL_TYPE: ClassVar = "gemini"
    llm_name: str = LlmName.GEMINI_2_FLASH.value
    api_key: SecretStr
    temperature: float = Field(ge=0.0, le=1.0, default=0.2)
    max_tokens: int = Field(gt=0, default=1024)


class AnthropicParams(BaseModel):
    MODEL_TYPE: ClassVar = "claude"
    llm_name: str = LlmName.CLAUDE_3_7_SONNET.value
    api_key: SecretStr
    temperature: float = Field(ge=0.0, le=1.0, default=0.2)
    max_tokens: int = Field(gt=0, default=1024)


class LocalParams(BaseModel):
    MODEL_TYPE: ClassVar = "local"
    llm_name: str
    device: str
    pipeline_args: dict = {}


ModelParams = GeminiParams | LocalParams
