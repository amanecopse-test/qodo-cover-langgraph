from typing import List, Tuple, Self

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
from pydantic import BaseModel

from core.setting import mcp_settings
from schemas.mcp import SseClientSchema, StdioClientSchema


class McpClient:
    def __init__(self):
        self._streams_ctx = None
        self._streams: Tuple | None = None
        self._session_ctx = None
        self._session: ClientSession | None = None

    async def initialize(self, setting: SseClientSchema | StdioClientSchema) -> None:
        self._streams_ctx = self._get_streams_ctx(setting)
        self._streams = await self._streams_ctx.__aenter__()
        self._session_ctx = ClientSession(*self._streams)
        self._session = await self._session_ctx.__aenter__()

        await self._session.initialize()

    async def list_tools(self) -> List[BaseTool]:
        return await load_mcp_tools(self._session)

    async def close(self) -> None:
        if self._session_ctx is not None:
            await self._session_ctx.__aexit__(None, None, None)
        if self._streams_ctx is not None:
            await self._streams_ctx.__aexit__(None, None, None)

    @classmethod
    async def from_setting(cls, setting: SseClientSchema | StdioClientSchema) -> Self:
        client = McpClient()
        await client.initialize(setting)
        return client

    @classmethod
    def _get_streams_ctx(cls, setting: BaseModel):
        if isinstance(setting, SseClientSchema):
            return sse_client(url=setting.mcp_sse_url)
        elif isinstance(setting, StdioClientSchema):
            return stdio_client(
                StdioServerParameters(
                    command=setting.mcp_stdio_command,
                    args=setting.mcp_stdio_args,
                )
            )
        raise Exception("Not valid setting")


class McpManager:
    def __init__(self) -> None:
        self.clients: List[McpClient] = []
        self.tools: List[BaseTool] = []

    async def init_mcp_settings(self):
        for setting in mcp_settings.SSE_CLIENTS + mcp_settings.STDIO_CLIENTS:
            client = await McpClient.from_setting(setting)
            self.clients.append(client)
            self.tools.extend(await client.list_tools())

    async def close(self):
        for client in self.clients:
            await client.close()

    async def __aenter__(self) -> Self:
        await self.init_mcp_settings()
        return self

    async def __aexit__(self, *exc_info):
        await self.close()
