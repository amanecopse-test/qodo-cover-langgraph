from collections import deque
from typing import List, Optional
from langgraph.prebuilt.chat_agent_executor import (
    AgentStateWithStructuredResponsePydantic,
)
from pydantic import Field

from app.core.snapshot_editor import SnapshotEditor
from app.schemas.structured_output import (
    FailedTestReport,
    ImprovedResult,
    NewTests,
    SingleTest,
    SourceFile,
    TestFailureAnalysis,
    TestFile,
    TestCoverage,
    TestFileAnalysis,
)


class TestImproverState(AgentStateWithStructuredResponsePydantic):
    structured_response: Optional[NewTests] = None


class TestFinderState(AgentStateWithStructuredResponsePydantic):
    structured_response: Optional[TestFile] = None


class TestValidationState(AgentStateWithStructuredResponsePydantic):
    structured_response: Optional[TestCoverage] = None


class TestAnalysisState(AgentStateWithStructuredResponsePydantic):
    structured_response: Optional[TestFileAnalysis] = None


class TestFailureAnalysisState(AgentStateWithStructuredResponsePydantic):
    structured_response: Optional[TestFailureAnalysis] = None


class TestSupervisorState(AgentStateWithStructuredResponsePydantic):
    source_file: SourceFile = Field(description="The source file to be tested")
    base_test_file: Optional[TestFile] = Field(
        description="The base test file to be improved"
    )
    snapshot_editor: Optional[SnapshotEditor] = Field(
        description="The snapshot editor to be used"
    )
    test_coverage: Optional[TestCoverage] = Field(
        description="The test coverage report"
    )
    test_failure_analysis: Optional[TestFailureAnalysis] = Field(
        description="The test failure analysis"
    )
    single_test_queue: deque[SingleTest] = Field(
        default_factory=lambda: deque([]),
        description="The queue of single tests to be improved",
    )
    failed_test_reports: List[FailedTestReport] = Field(
        default_factory=lambda: [], description="The failed test reports"
    )
    structured_response: Optional[ImprovedResult] = None
