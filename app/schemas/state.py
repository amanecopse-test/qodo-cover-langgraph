from typing import Optional
from langgraph.prebuilt.chat_agent_executor import (
    AgentStateWithStructuredResponsePydantic,
)

from app.schemas.structured_output import NewTests


class TestGenState(AgentStateWithStructuredResponsePydantic):
    structured_response: Optional[NewTests] = None
