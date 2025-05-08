from typing import List, Optional, Type, override
from langchain_core.messages import HumanMessage, BaseMessage
from pydantic import BaseModel

from app.prompts.base import PromptABC
from app.schemas.structured_output import TestCoverage


class TestValidationPrompt(PromptABC):
    def __init__(
        self,
        language: str,
        testing_framework: str,
        source_file_name: str,
        source_file_path: str,
        test_file_name: str,
        test_file_content: str,
        additional_instructions_text: Optional[str] = None,
    ):
        self.language = language
        self.testing_framework = testing_framework
        self.source_file_name = source_file_name
        self.source_file_path = source_file_path
        self.test_file_name = test_file_name
        self.test_file_content = test_file_content
        self.additional_instructions_text = additional_instructions_text

    @override
    def get_output_model(self) -> Type[BaseModel]:
        return TestCoverage

    @override
    def build(self) -> list[HumanMessage]:
        messages: List[BaseMessage] = []

        # Build user message
        user_content = self._dedent(
            """
            ## Overview
            You are a test validation assistant that accepts a {language} source file, and a {language} test file.
            Your goal is to validate the test file using the `coverage_tool`.

            ## Steps
            1. Use the `coverage_tool` to validate the test file.
            2. Parse the output of the `coverage_tool` to generate a `TestCoverage` object.

            ## Source File
            The source file is called `{source_file_name}`.
            The source file is located at `{source_file_path}`.

            ## Test File
            Here is the test file that you will be validating, called `{test_file_name}`.
            =========
            {test_file_content}
            =========

            ### Test Framework
            The test framework used for running tests is `{testing_framework}`.
            """
        ).format(
            language=self.language,
            testing_framework=self.testing_framework,
            source_file_name=self.source_file_name,
            source_file_path=self.source_file_path,
            test_file_name=self.test_file_name,
            test_file_content=self.test_file_content,
        )

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
            ## Output Example
            Here is an example of the output you should parse from the `coverage_tool`:
            =========
            TestCoverage(
                stdout="",
                stderr="",
                coverage_percent=60,
                uncovered_lines=[11, 14, 15],
            )
            =========
            """
        )

        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
