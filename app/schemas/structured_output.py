from typing import List

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
        )
        ```
    """

    language: str = Field(description="The programming language of the test file")
    name: str = Field(description="The name of the test file")
    content: str = Field(description="The content of the test file")


class AdaptedTestCommand(BaseModel):
    """Model for adapted test command.

    Example:
        ```python
        command = AdaptedTestCommand(
            adapted_command="pytest test_file.py::test_name",
            explanation="Modified the command to run only the specific test using pytest's test selection syntax"
        )
        ```
    """

    adapted_command: str = Field(description="The adapted command to run a single test")
    explanation: str = Field(
        description="An explanation of how the command was adapted"
    )


class TestHeadersIndentation(BaseModel):
    """Model for test headers indentation analysis.

    Example:
        ```python
        analysis = TestHeadersIndentation(
            test_headers=["test_header_1", "test_header_2"],
            indentation_levels=[0, 1],
            explanation="The test headers follow a consistent indentation pattern where main headers are at level 0 and sub-headers are at level 1"
        )
        ```
    """

    test_headers: List[str] = Field(
        description="A list of test headers found in the test file"
    )
    indentation_levels: List[int] = Field(
        description="A list of indentation levels for each test header"
    )
    explanation: str = Field(
        description="An explanation of the indentation pattern found in the test file"
    )


class TestsAnalysis(BaseModel):
    """Model for test suite analysis.

    Example:
        ```python
        analysis = TestsAnalysis(
            language="python",
            testing_framework="pytest",
            number_of_tests=5,
            relevant_line_number_to_insert_tests_after=42,
            relevant_line_number_to_insert_imports_after=10
        )
        ```
    """

    language: str = Field(description="The programming language used by the test file")
    testing_framework: str = Field(
        description="The testing framework needed to run the tests in the test file"
    )
    number_of_tests: int = Field(description="The number of tests in the test file")
    relevant_line_number_to_insert_tests_after: int = Field(
        description="The line number in the test file, after which the new tests should be inserted"
    )
    relevant_line_number_to_insert_imports_after: int = Field(
        description="The line number in the test file, after which new imports should be inserted"
    )


class TestAnalysis(BaseModel):
    """Model for test analysis against context.

    Example:
        ```python
        analysis = TestAnalysis(
            is_valid=True,
            explanation="The test code is valid against the context as it properly uses all required imports and follows the expected patterns",
            suggestions=["Consider adding more edge cases", "Add error handling for invalid inputs"]
        )
        ```
    """

    is_valid: bool = Field(
        description="Whether the test code is valid against the context"
    )
    explanation: str = Field(
        description="An explanation of why the test code is valid or invalid against the context"
    )
    suggestions: List[str] = Field(
        description="A list of suggestions to improve the test code"
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
