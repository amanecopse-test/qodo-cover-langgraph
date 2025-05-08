from langchain_core.language_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph

from app.llm.agent.base import BaseAgentBuilder
from app.prompts.analysis_prompt import TestAnalysisPrompt
from app.schemas.state import TestAnalysisState
from app.schemas.structured_output import TestFileAnalysis


class TestAnalysisAgent(BaseAgentBuilder):
    """
    테스트 코드의 분석을 수행하는 에이전트
    """

    def __init__(
        self,
        model: BaseChatModel,
    ):
        super().__init__(
            model=model,
            tools=[],
            tool_call_mode="none",
        )

    def build(self) -> CompiledGraph:
        return self.create_agentic_graph(
            state_schema=TestAnalysisState,
            llm_node=self.create_llm_node(),
            output_node=self.create_output_node(TestFileAnalysis),
        ).compile()

    async def validate_vitest(
        self,
        test_file_content: str,
    ) -> TestFileAnalysis:
        agent = self.build()
        response = await agent.ainvoke(
            TestAnalysisState(
                messages=TestAnalysisPrompt(
                    test_file_content=test_file_content,
                ).build()
            )
        )
        return response["structured_response"]
