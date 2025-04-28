from typing import List

from pydantic import BaseModel


class SseClientSchema(BaseModel):
    mcp_sse_url: str


class StdioClientSchema(BaseModel):
    mcp_stdio_command: str
    mcp_stdio_args: List[str]
