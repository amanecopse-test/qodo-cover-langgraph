from typing import List, Optional, Type, override

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from app.prompts.base import PromptABC
from app.schemas.structured_output import TestFile


class TestFinderPrompt(PromptABC):
    """Prompt builder for finding a test file."""

    def __init__(
        self,
        language: str,
        source_file_name: str,
        source_file_content: str,
        source_file_path: str,
        testing_framework: str,
        additional_instructions_text: Optional[str] = None,
    ):
        self.language = language
        self.source_file_name = source_file_name
        self.source_file_content = source_file_content
        self.source_file_path = source_file_path
        self.testing_framework = testing_framework
        self.additional_instructions_text = additional_instructions_text

    @override
    def get_output_model(self) -> Type[BaseModel]:
        return TestFile

    @override
    def build(self) -> List[BaseMessage]:
        messages: List[BaseMessage] = []

        # Build user message
        user_content = self._dedent(
            """
            ## Overview
            You are a code assistant that accepts a {language} source file, and a {language} test file.
            Your goal is to find the test file that contains the tests for the source file, or generate a new test file if one does not exist.

            ## Steps
            1. Using the `test_finder` tool, find the test file that contains the tests for the source file.
            2-1. If the test file exists, return the test file.
            2-2. If the test file does not exist, generate a new test file.

            ## Source File
            Here is the source file that you will be writing tests against, called `{source_file_name}`.
            The source file is located at `{source_file_path}`.
            =========
            {source_file_content}
            =========

            ### Test Framework
            The test framework used for running tests is `{testing_framework}`.
            """
        ).format(
            language=self.language,
            source_file_name=self.source_file_name,
            source_file_content=self.source_file_content,
            source_file_path=self.source_file_path,
            testing_framework=self.testing_framework,
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
            Here is an example of the output you should generate when the test file does not exist:
            =========
            TestFile(
                language="python",
                name="test_file.py",
                content="\\n".join([
                    "import { render, renderWithSetup, screen } from 'shared-utils-test';",
                    "",
                    "import Button from '../Button';",
                    "",
                    "describe('<Button/> Test', () => {",
                    "  test('Sample test', () => {",
                    "    expect(true).toBe(true);",
                    "  });",
                    "});",
                ]),
                path="src/test_file.py",
            )
            =========
            """
        )

        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
