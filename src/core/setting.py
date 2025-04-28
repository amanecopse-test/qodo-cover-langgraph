from pathlib import Path
from typing import Literal, List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

from schemas.mcp import SseClientSchema, StdioClientSchema


class CommonSettings(BaseSettings):
    ENV_STATE: Literal["", "dev", "prod"] = Field(default="", frozen=True)


class GeminiSettings(BaseSettings):
    GEMINI_API_KEY: str = Field(default="", frozen=True)


class McpSettings(BaseSettings):
    SSE_CLIENTS: List[SseClientSchema] = Field(default=[], frozen=True)
    STDIO_CLIENTS: List[StdioClientSchema] = Field(default=[], frozen=True)

    class _Schema(BaseModel):
        sse_clients: List[SseClientSchema]
        stdio_clients: List[StdioClientSchema]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        json_file_name = f"mcp-setting.{CommonSettings().ENV_STATE}.json".replace(
            "..", "."
        )
        json_setting = Path(json_file_name).read_text(encoding="utf-8")
        setting = self._Schema.model_validate_json(json_setting)
        self.SSE_CLIENTS.extend(setting.sse_clients)
        self.STDIO_CLIENTS.extend(setting.stdio_clients)


gemini_settings = GeminiSettings()
mcp_settings = McpSettings()
