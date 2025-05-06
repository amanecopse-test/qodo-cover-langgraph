from typing import List, Type

from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from app.prompts.base import PromptABC
from app.schemas.structured_output import TestHeadersIndentation


class AnalyzeSuiteTestHeadersIndentation(PromptABC):
    """Prompt builder for analyzing suite test headers indentation."""

    def __init__(
        self,
        language: str,
        test_file_name: str,
        test_file: str,
    ):
        """Initialize the analyze suite test headers indentation prompt.

        Args:
            language (str): Programming language of the source code
            test_file_name (str): Name of the test file
            test_file (str): Content of the test file
        """
        self.language = language
        self.test_file_name = test_file_name
        self.test_file = test_file

    def get_output_model(self) -> Type[BaseModel]:
        """Get the output model type for this prompt.

        Returns:
            Type[BaseModel]: The Pydantic model class that represents the output structure.
        """
        return TestHeadersIndentation

    def build(self) -> List[BaseMessage]:
        """Build the analyze suite test headers indentation prompt.

        Returns:
            List[BaseMessage]: List of system and user messages
        """
        messages: List[BaseMessage] = []

        # Build user message
        user_content = self._dedent(
            f"""
            ## Overview
            You are a code assistant that accepts a {self.language} test file.
            Your goal is to analyze the indentation of test headers in the test file.

            ## Test File
            Here is the test file that you will be analyzing, called `{self.test_file_name}`:
            =========
            {self.test_file.strip()}
            =========
        """
        )

        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
