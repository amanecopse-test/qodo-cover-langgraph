from typing import List, Literal
from langchain_core.language_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph
from langgraph.graph import StateGraph
from app.core.snapshot_editor import SnapshotEditor
from app.llm.agent.analysis_agent import TestAnalysisAgent
from app.llm.agent.base import BaseAgentBuilder
from app.llm.agent.failure_analysis_agent import TestFailureAnalysisAgent
from app.llm.agent.finder_agent import TestFinderAgent
from app.llm.agent.improver_agent import TestImproverAgent
from app.llm.agent.validation_agent import TestValidationAgent
from app.schemas.state import TestSupervisorState
from app.schemas.structured_output import (
    ImprovedResult,
    SourceFile,
    TestFile,
)


class TestSupervisorAgent(BaseAgentBuilder):
    """
    테스트 커버리지 개선 작업을 총괄하는 에이전트
    """

    def __init__(
        self,
        model: BaseChatModel,
        finder_agent: TestFinderAgent,
        analysis_agent: TestAnalysisAgent,
        validation_agent: TestValidationAgent,
        failure_analysis_agent: TestFailureAnalysisAgent,
        improver_agent: TestImproverAgent,
    ):
        super().__init__(
            model=model,
            tools=[],
            tool_call_mode="none",
        )
        self.finder_agent = finder_agent
        self.analysis_agent = analysis_agent
        self.validation_agent = validation_agent
        self.failure_analysis_agent = failure_analysis_agent
        self.improver_agent = improver_agent

    def build(self) -> CompiledGraph:
        workflow = StateGraph(TestSupervisorState)

        async def finder_node(state: TestSupervisorState) -> TestSupervisorState:
            source_file = state.source_file

            test_file = await self.finder_agent.find_or_generate_vitest_file(
                source_file_name=source_file.name,
                source_file_content=source_file.content,
                source_file_path=source_file.path,
            )

            state.base_test_file = test_file
            return state

        async def analysis_node(state: TestSupervisorState) -> TestSupervisorState:
            test_file = state.base_test_file

            analysis = await self.analysis_agent.analyze_vitest(
                test_file_content=test_file.content,
            )
            snapshot_editor = SnapshotEditor(
                test_file_content=test_file.content,
                test_file_name=test_file.name,
                test_file_path=test_file.path,
                line_number_to_insert_imports_after=analysis.last_import_line_number,
                line_number_to_insert_tests_after=analysis.last_single_test_line_number,
            )

            state.snapshot_editor = snapshot_editor
            return state

        async def validation_node(state: TestSupervisorState) -> TestSupervisorState:
            source_file = state.source_file
            snapshot = state.snapshot_editor

            coverage = await self.validation_agent.validate_vitest(
                source_file_name=source_file.name,
                source_file_path=source_file.path,
                test_file_name=snapshot.test_file_name,
                test_file_content=snapshot.test_file_content,
            )
            state.test_coverage = coverage

            return state

        def validation_route(
            state: TestSupervisorState,
        ) -> Literal[
            "validation_node", "failure_analysis_node", "improver_node", "output_node"
        ]:
            coverage = state.test_coverage
            previous_coverage_percent = state.snapshot_editor.coverage_percent

            if coverage.improved(previous_coverage_percent):
                return True
            else:
                return False

        async def failure_analysis_node(
            state: TestSupervisorState,
        ) -> TestSupervisorState:
            coverage = state.test_coverage
            snapshot = state.snapshot_editor

            analysis = await self.failure_analysis_agent.analyze_vitest_failure(
                test_file_name=snapshot.test_file_name,
                test_file_content=snapshot.test_file_content,
                source_file_name=state.source_file.name,
                source_file_content=state.source_file.content,
                stdout=coverage.stdout,
                stderr=coverage.stderr,
            )

            snapshot.rollback()
            state.test_failure_analysis = analysis
            return state

        async def improver_node(state: TestSupervisorState) -> TestSupervisorState:
            source_file = state.source_file
            snapshot = state.snapshot_editor

            improver_result = await self.improver_agent.generate_vitest_test(
                source_file_name=source_file.name,
                source_file_content=source_file.content,
                test_file_name=snapshot.test_file_name,
                test_file_content=snapshot.test_file_content,
                code_coverage_report=state.test_coverage.uncovered_lines,
                failed_test_reports=state.failed_test_reports,
            )

            state.single_test_queue.extend(improver_result.new_tests)
            return state

        async def output_node(state: TestSupervisorState) -> TestSupervisorState:
            pass

        workflow.add_node("finder", finder_node)
        workflow.add_node("analysis", analysis_node)
        workflow.add_node("validation", validation_node)
        workflow.add_node("failure_analysis", failure_analysis_node)
        workflow.add_node("improver", improver_node)
        workflow.add_node("output", output_node)

        workflow.add_edge("finder", "analysis")
        workflow.add_edge("analysis", "validation")
        workflow.add_edge("validation", "failure_analysis")
        workflow.add_edge("failure_analysis", "improver")
        workflow.add_edge("improver", "output")

        return workflow.compile()

    async def cover_test(
        self,
        source_file_name: str,
        source_file_path: str,
        source_file_content: str,
    ) -> ImprovedResult:
        agent = self.build()
        response = await agent.ainvoke(
            TestSupervisorState(
                messages=[],
                source_file=SourceFile(
                    language="python",
                    name=source_file_name,
                    content=source_file_content,
                    path=source_file_path,
                ),
            )
        )
        return response["structured_response"]
        # return ImprovedResult(
        #     coverage_percent=100,
        #     source_file=SourceFile(
        #         language="python",
        #         name=source_file_name,
        #         content=source_file_content,
        #         path=source_file_path,
        #     ),
        #     test_file=TestFile(
        #         language="python",
        #         name="",
        #         content="",
        #         path="",
        #     ),
        # )
