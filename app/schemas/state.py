from typing import Optional
from langgraph.prebuilt.chat_agent_executor import (
    AgentStateWithStructuredResponsePydantic,
)

from app.schemas.structured_output import NewTests, TestFile


class TestGenState(AgentStateWithStructuredResponsePydantic):
    structured_response: Optional[NewTests] = None


class TestFinderState(AgentStateWithStructuredResponsePydantic):
    structured_response: Optional[TestFile] = None
