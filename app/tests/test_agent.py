import os
import textwrap
from typing import override, Optional
from dotenv import load_dotenv
from pydantic import BaseModel
import pytest

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import Tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt.chat_agent_executor import (
    AgentStateWithStructuredResponsePydantic,
)
from langgraph.graph.graph import CompiledGraph

from app.llm.agent.base import BaseAgentBuilder


class WeatherResponse(BaseModel):
    weather: str
    location: str


class WeatherState(AgentStateWithStructuredResponsePydantic):
    structured_response: Optional[WeatherResponse] = None


@pytest.mark.asyncio
async def test_agent():
    load_dotenv()
    agent = WeatherAgent().build()
    response = await agent.ainvoke(
        WeatherState(
            messages=[
                HumanMessage(
                    textwrap.dedent(
                        """
                        You are a weather agent. Follow the instructions below to get the weather in a specific location.
                        The postal code is 102-711.
                        
                        Instructions:
                        1. Get the current location at the postal code using the location_tool
                        2. Get the weather in the current location using the weather_tool
                        3. Return the weather in the current location
                        """
                    )
                )
            ]
        ).model_dump()
    )
    print(response)


class WeatherAgent(BaseAgentBuilder):
    def __init__(self):
        super().__init__(
            model=ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                api_key=os.getenv("GEMINI_API_KEY"),
            ),
            tools=[
                Tool(
                    name="weather_tool",
                    description="this tool is used to get the weather in a specific location. The location is required.",
                    func=lambda location: "sunny",
                ),
                Tool(
                    name="location_tool",
                    description="This tool is used to get the current location at the postal code. The postal code is required.",
                    func=lambda postal_code: "seoul",
                ),
            ],
            tool_call_mode="multi_turn",
        )

    @override
    def build(self) -> CompiledGraph:
        return self.create_agentic_graph(
            state_schema=WeatherState,
            llm_node=self.create_llm_node(),
            output_node=self.create_output_node(WeatherResponse),
        ).compile()
