from typing import List, Type

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from app.prompts.base import PromptABC
from app.schemas.structured_output import TestAnalysis


class AnalyzeTestRunFailure(PromptABC):
    """Prompt builder for analyzing test run failure."""

    def __init__(
        self,
        language: str,
        test_file_name: str,
        test_file: str,
        test_name: str,
        test_code: str,
        test_output: str,
    ):
        """Initialize the analyze test run failure prompt.

        Args:
            language (str): Programming language of the source code
            test_file_name (str): Name of the test file
            test_file (str): Content of the test file
            test_name (str): Name of the test that failed
            test_code (str): Code of the test that failed
            test_output (str): Output of the test that failed
        """
        self.language = language
        self.test_file_name = test_file_name
        self.test_file = test_file
        self.test_name = test_name
        self.test_code = test_code
        self.test_output = test_output

    def get_output_model(self) -> Type[BaseModel]:
        """Get the output model type for this prompt.

        Returns:
            Type[BaseModel]: The Pydantic model class that represents the output structure.
        """
        return TestAnalysis

    def build(self) -> List[BaseMessage]:
        """Build the analyze test run failure prompt.

        Returns:
            List[BaseMessage]: List of system and user messages
        """
        messages: List[BaseMessage] = []

        # Build user message
        user_content = self._dedent(
            f"""
            ## Overview
            You are a code assistant that accepts a {self.language} test file, a test name, a test code, and a test output.
            Your goal is to analyze why the test failed.

            ## Test File
            Here is the test file that you will be analyzing, called `{self.test_file_name}`:
            =========
            {self.test_file.strip()}
            =========

            ## Test Name
            The test name that failed is: `{self.test_name}`

            ## Test Code
            The test code that failed is:
            ```
            {self.test_code.strip()}
            ```

            ## Test Output
            The output of the test that failed is:
            ```
            {self.test_output.strip()}
            ```
        """
        )

        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
