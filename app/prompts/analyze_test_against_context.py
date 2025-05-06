from typing import List, Type

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from app.prompts.base import PromptABC
from app.schemas.structured_output import TestAnalysis


class AnalyzeTestAgainstContext(PromptABC):
    """Prompt builder for analyzing test against context."""

    def __init__(
        self,
        language: str,
        test_file_name: str,
        test_file: str,
        test_name: str,
        test_code: str,
        context: str,
    ):
        """Initialize the analyze test against context prompt.

        Args:
            language (str): Programming language of the source code
            test_file_name (str): Name of the test file
            test_file (str): Content of the test file
            test_name (str): Name of the test to analyze
            test_code (str): Code of the test to analyze
            context (str): Context to analyze the test against
        """
        self.language = language
        self.test_file_name = test_file_name
        self.test_file = test_file
        self.test_name = test_name
        self.test_code = test_code
        self.context = context

    def get_output_model(self) -> Type[BaseModel]:
        """Get the output model type for this prompt.

        Returns:
            Type[BaseModel]: The Pydantic model class that represents the output structure.
        """
        return TestAnalysis

    def build(self) -> List[BaseMessage]:
        """Build the analyze test against context prompt.

        Returns:
            List[BaseMessage]: List of system and user messages
        """
        messages: List[BaseMessage] = []

        # Build system message
        system_content = f"You are a {self.language} code assistant that accepts a test file and a list of context files."
        system_message = self._create_system_message(system_content)
        if system_message:
            messages.append(system_message)

        # Build user message
        user_content = self._dedent(
            f"""
            ## Overview
            You are a code assistant that accepts a {self.language} test file, a test name, a test code, and a context.
            Your goal is to analyze the test code against the context.

            ## Test File
            Here is the test file that you will be analyzing, called `{self.test_file_name}`:
            =========
            {self.test_file.strip()}
            =========

            ## Test Name
            The test name to analyze is: `{self.test_name}`

            ## Test Code
            The test code to analyze is:
            ```
            {self.test_code.strip()}
            ```

            ## Context
            The context to analyze the test against is:
            ```
            {self.context.strip()}
            ```
        """
        )

        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
