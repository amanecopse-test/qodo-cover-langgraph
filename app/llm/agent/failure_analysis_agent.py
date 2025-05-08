from typing import List
from langchain_core.language_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph
from langchain_core.tools import BaseTool
from app.llm.agent.base import BaseAgentBuilder
from app.prompts.failure_analysis_prompt import TestFailureAnalysisPrompt
from app.schemas.state import TestFailureAnalysisState
from app.schemas.structured_output import TestFailureAnalysis


class TestFailureAnalysisAgent(BaseAgentBuilder):
    """
    테스트 코드의 실패 이유를 분석하고 해결 방법을 제안하는 에이전트
    """

    def __init__(
        self,
        model: BaseChatModel,
        tools: List[BaseTool],
    ):
        super().__init__(
            model=model,
            tools=tools,
            tool_call_mode="multi_turn",
        )

    def build(self) -> CompiledGraph:
        return self.create_agentic_graph(
            state_schema=TestFailureAnalysisState,
            llm_node=self.create_llm_node(),
            output_node=self.create_output_node(TestFailureAnalysis),
        ).compile()

    async def analyze_vitest_failure(
        self,
        test_file_name: str,
        test_file_content: str,
        source_file_name: str,
        source_file_content: str,
        stdout: str,
        stderr: str,
    ) -> TestFailureAnalysis:
        agent = self.build()
        response = await agent.ainvoke(
            TestFailureAnalysisState(
                messages=TestFailureAnalysisPrompt(
                    test_file_name=test_file_name,
                    test_file_content=test_file_content,
                    source_file_name=source_file_name,
                    source_file_content=source_file_content,
                    stdout=stdout,
                    stderr=stderr,
                ).build()
            )
        )
        return response["structured_response"]
