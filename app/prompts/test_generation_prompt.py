from typing import List, Optional, Type, override

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from app.prompts.base import PromptABC
from app.schemas.structured_output import NewTests


class TestGenerationPrompt(PromptABC):
    """Prompt builder for generating test cases."""

    def __init__(
        self,
        language: str,
        source_file_name: str,
        source_file_numbered: str,
        test_file_name: str,
        test_file: str,
        testing_framework: str,
        code_coverage_report: str,
        max_tests: int,
        additional_includes_section: Optional[str] = None,
        failed_tests_section: Optional[str] = None,
        additional_instructions_text: Optional[str] = None,
    ):
        """Initialize the test generation prompt.

        Args:
            language (str): Programming language of the source code
            source_file_name (str): Name of the source file
            source_file_numbered (str): Source file content with line numbers
            test_file_name (str): Name of the test file
            test_file (str): Content of the test file
            testing_framework (str): Testing framework being used
            code_coverage_report (str): Code coverage report
            max_tests (int): Maximum number of tests to generate
            additional_includes_section (Optional[str]): Additional includes section
            failed_tests_section (Optional[str]): Previously failed tests section
            additional_instructions_text (Optional[str]): Additional instructions
        """
        self.language = language
        self.source_file_name = source_file_name
        self.source_file_numbered = source_file_numbered
        self.test_file_name = test_file_name
        self.test_file = test_file
        self.testing_framework = testing_framework
        self.code_coverage_report = code_coverage_report
        self.max_tests = max_tests
        self.additional_includes_section = additional_includes_section
        self.failed_tests_section = failed_tests_section
        self.additional_instructions_text = additional_instructions_text

    @override
    def get_output_model(self) -> Type[BaseModel]:
        """Get the output model type for this prompt.

        Returns:
            Type[BaseModel]: The Pydantic model class that represents the output structure.
        """
        return NewTests

    @override
    def build(self) -> List[BaseMessage]:
        """Build the test generation prompt.

        Returns:
            List[BaseMessage]: List of system and user messages
        """
        messages: List[BaseMessage] = []

        # System message is empty in this case
        system_message = self._create_system_message("")
        if system_message:
            messages.append(system_message)

        # Build user message
        user_content = self._dedent(
            """
            ## Overview
            You are a code assistant that accepts a {language} source file, and a {language} test file.
            Your goal is to generate additional comprehensive unit tests to complement the existing test suite, in order to increase the code coverage against the source file.

            Additional guidelines:
            - Carefully analyze the provided code. Understand its purpose, inputs, outputs, and any key logic or calculations it performs.
            - Brainstorm a list of diverse and meaningful test cases you think will be necessary to fully validate the correctness and functionality of the code, and achieve 100% code coverage.
            - After each individual test has been added, review all tests to ensure they cover the full range of scenarios, including how to handle exceptions or errors.
            - If the original test file contains a test suite, assume that each generated test will be a part of the same suite. Ensure that the new tests are consistent with the existing test suite in terms of style, naming conventions, and structure.

            ## Source File
            Here is the source file that you will be writing tests against, called `{source_file_name}`.
            Note that we have manually added line numbers for each line of code, to help you understand the code coverage report.
            Those numbers are not a part of the original code.
            =========
            {source_file_numbered}
            =========

            ## Test File
            Here is the file that contains the existing tests, called `{test_file_name}`:
            =========
            {test_file}
            =========

            ### Test Framework
            The test framework used for running tests is `{testing_framework}`.
            """
        ).format(
            language=self.language,
            source_file_name=self.source_file_name,
            source_file_numbered=self.source_file_numbered,
            test_file_name=self.test_file_name,
            test_file=self.test_file,
            testing_framework=self.testing_framework,
        )

        if self.language == "python" and self.testing_framework == "pytest":
            user_content += self._dedent(
                """
                If the current tests are part of a class and contain a 'self' input, then the generated tests should also include the `self` parameter in the test function signature.
                """
            )

        if self.additional_includes_section:
            user_content += self._dedent(
                """
                ## Additional Includes
                Here are the additional files needed to provide context for the source code:
                ======
                {additional_includes_section}
                ======
                """
            ).format(additional_includes_section=self.additional_includes_section)

        if self.failed_tests_section:
            user_content += self._dedent(
                """
                ## Previous Iterations Failed Tests
                Below is a list of failed tests that were generated in previous iterations. Do not generate the same tests again, and take these failed tests into account when generating new tests.
                ======
                {failed_tests_section}
                ======
                """
            ).format(failed_tests_section=self.failed_tests_section)

        if self.additional_instructions_text:
            user_content += self._dedent(
                """
                ## Additional Instructions
                ======
                {additional_instructions_text}
                ======
                """
            ).format(additional_instructions_text=self.additional_instructions_text)

        user_content += self._dedent(
            """
            ## Code Coverage
            Based on the code coverage report below, your goal is to suggest new test cases for the test file `{test_file_name}` against the source file `{source_file_name}` that would increase the coverage, meaning cover missing lines of code.
            =========
            {code_coverage_report}
            =========
            """
        ).format(
            test_file_name=self.test_file_name,
            source_file_name=self.source_file_name,
            code_coverage_report=self.code_coverage_report,
        )

        user_content += self._dedent(
            """
            ## Output Example
            Here is an example of the output you should generate:
            =========
            NewTests(
                language="python",
                existing_test_function_signature="def test_example(self):",
                new_tests=[
                    SingleTest(
                        test_behavior="Test single element list",
                        lines_to_cover="[1,2,5]",
                        test_name="test_single_element_list",
                        test_code="def test_single_element_list(self):\\n    result = function([1])\\n    assert result == expected",
                        new_imports_code="",
                        test_tags="happy path"
                    )
                ]
            )
            =========
            """
        )
        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
