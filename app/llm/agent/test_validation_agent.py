from typing import List
from langchain_core.language_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph
from mcp import Tool

from app.llm.agent.base import BaseAgentBuilder
from app.prompts.test_validation_prompt import TestValidationPrompt
from app.schemas.state import TestValidationState
from app.schemas.structured_output import TestCoverage


class TestValidationAgent(BaseAgentBuilder):
    """
    테스트 코드의 유효성을 검증하고 개선 사항을 제안하는 에이전트
    """

    def __init__(
        self,
        model: BaseChatModel,
        tools: List[Tool],
    ):
        super().__init__(
            model=model,
            tools=tools,
            tool_call_mode="single_turn",
        )

    def build(self) -> CompiledGraph:
        return self.create_agentic_graph(
            state_schema=TestValidationState,
            llm_node=self.create_llm_node(),
            output_node=self.create_output_node(TestCoverage),
        ).compile()

    async def validate_vitest(
        self,
        source_file_name: str,
        source_file_path: str,
        test_file_name: str,
        test_file_content: str,
    ) -> TestCoverage:
        agent = self.build()
        response = await agent.ainvoke(
            TestValidationState(
                messages=TestValidationPrompt(
                    language="typescript",
                    source_file_name=source_file_name,
                    source_file_path=source_file_path,
                    test_file_name=test_file_name,
                    test_file_content=test_file_content,
                    testing_framework="vitest",
                ).build()
            )
        )
        return response["structured_response"]
