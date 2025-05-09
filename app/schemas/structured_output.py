from typing import List, Optional

from pydantic import BaseModel, Field


class SingleTest(BaseModel):
    """Model for a single test case.

    Example:
        ```python
        test = SingleTest(
            test_behavior="Test that the function returns the correct output for a single element list",
            lines_to_cover="[1,2,5, ...]",
            test_name="test_single_element_list",
            test_code="def test_single_element_list(self):\n    result = function([1])\n    assert result == expected",
            new_imports_code="",
            test_tags="happy path"
        )
        ```
    """

    test_behavior: str = Field(
        description="Short description of the behavior the test covers"
    )
    lines_to_cover: str = Field(
        description="A list of line numbers, currently uncovered, that this specific new test aims to cover"
    )
    test_name: str = Field(
        description="A short test name, in snake case, that reflects the behaviour to test"
    )
    test_code: str = Field(
        description="A new test function that extends the existing test suite, and tests the behavior described in 'test_behavior'"
    )
    new_imports_code: str = Field(
        description="New imports that are required to run the new test function"
    )
    test_tags: str = Field(
        description="A single label that best describes the test, out of: ['happy path', 'edge case','other']"
    )


class NewTests(BaseModel):
    """Model for new test cases.

    Example:
        ```python
        tests = NewTests(
            language="python",
            existing_test_function_signature="def test_example(self):",
            new_tests=[
                SingleTest(
                    test_behavior="Test single element list",
                    lines_to_cover="[1,2,5]",
                    test_name="test_single_element_list",
                    test_code="def test_single_element_list(self):\n    result = function([1])\n    assert result == expected",
                    new_imports_code="",
                    test_tags="happy path"
                )
            ]
        )
        ```
    """

    language: str = Field(description="The programming language of the source code")
    existing_test_function_signature: str = Field(
        description="A single line repeating a signature header of one of the existing test functions"
    )
    new_tests: List[SingleTest] = Field(
        min_items=1,
        description="A list of new test functions to append to the existing test suite",
    )


class TestFile(BaseModel):
    """Model for a test file.

    Example:
        ```python
        test_file = TestFile(
            language="python",
            name="test_file.py",
            content="\\n".join([
                "def test_example(self):",
                "    assert True",
            ]),
            path="src/test_file.py",
        )
        ```
    """

    language: str = Field(description="The programming language of the test file")
    name: str = Field(description="The name of the test file")
    content: str = Field(description="The content of the test file")
    path: str = Field(description="The path of the test file")


class SourceFile(BaseModel):
    """Model for a source file.

    Example:
        ```python
        source_file = SourceFile(
            language="python",
            name="source_file.py",
            content="\\n".join([
                "def function(self):",
                "    return 1",
            ]),
            path="src/source_file.py",
        )
        ```
    """

    language: str = Field(description="The programming language of the source file")
    name: str = Field(description="The name of the source file")
    content: str = Field(description="The content of the source file")
    path: str = Field(description="The path of the source file")


class TestCoverage(BaseModel):
    """Model for a test file.

    Example:
        ```python
        test_coverage = TestCoverage(
            stdout="",
            stderr="",
            coverage_percent=60,
            uncovered_lines=[11, 14, 15],
        )
        ```
    """

    stdout: Optional[str] = Field(description="The stdout of the test file")
    stderr: Optional[str] = Field(description="The stderr of the test file")
    coverage_percent: Optional[int] = Field(
        description="The coverage percent of the test file"
    )
    uncovered_lines: Optional[List[int]] = Field(
        description="The uncovered lines of the test file"
    )


class TestFileAnalysis(BaseModel):
    """Model for test file analysis.

    Example:
        ```python
        analysis = TestFileAnalysis(
            test_headers_indentation=0,
            last_single_test_line_number=42,
            last_import_line_number=10
        )
        ```
    """

    test_headers_indentation: int = Field(
        description="The indentation of the test headers in the test file. For example, 'def test_...' has an indentation of 0, '  def test_...' has an indentation of 2, '    def test_...' has an indentation of 4, and so on."
    )
    last_single_test_line_number: int = Field(
        description="The last line number of the single test"
    )
    last_import_line_number: int = Field(
        description="The last line number of the imports"
    )


class TestFailureAnalysis(BaseModel):
    """Model for test failure analysis.

    Example:
        ```python
        analysis = TestFailureAnalysis(
            failure_reason="AssertionError: expected 2 but got 1",
            explanation="The test failed because the function returned 1 instead of the expected value 2",
            suggestions=["Check if the input parameters are correct", "Verify the function's logic"]
        )
        ```
    """

    failure_reason: str = Field(description="The reason why the test failed")
    explanation: str = Field(description="An explanation of the failure reason")
    suggestions: List[str] = Field(description="A list of suggestions to fix the test")


class FailedTestReport(BaseModel):
    analysis: TestFailureAnalysis = Field(description="The analysis of the failed test")
    failed_single_test: SingleTest = Field(description="The single test that failed")


class ImprovedResult(BaseModel):
    """Model for ImprovedResult result.

    Example:
        ```python
        improved_result = ImprovedResult(
            coverage_percent=100,
            source_file=SourceFile(
                language="python",
                name="source_file.py",
                content="\\n".join([
                    "def function(self):",
                    "    return 1",
                ]),
            ),
            test_file=TestFile(
                language="python",
                name="test_file.py",
                content="\\n".join([
                    "def test_function(self):",
                    "    assert function(1) == 1",
                ]),
            ),
        )
        ```
    """

    coverage_percent: Optional[int] = Field(
        description="The coverage percent of the improved result"
    )
    source_file: SourceFile = Field(description="The source file that is tested")
    test_file: TestFile = Field(description="The test file that is improved")
