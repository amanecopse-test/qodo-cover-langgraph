from typing import List, Optional, Type

from langchain_core.messages import BaseMessage
from pydantic import BaseModel
from .base import PromptABC
from ..schemas.structured_output import TestsAnalysis


class AnalyzeSuiteTestInsertLine(PromptABC):
    """Prompt builder for analyzing suite test insert line."""

    def __init__(
        self,
        language: str,
        test_file_name: str,
        test_file_numbered: str,
        additional_instructions_text: Optional[str] = None,
    ):
        """Initialize the analyze suite test insert line prompt.

        Args:
            language (str): Programming language of the source code
            test_file_name (str): Name of the test file
            test_file_numbered (str): Content of the test file with line numbers
            additional_instructions_text (Optional[str]): Additional instructions
        """
        self.language = language
        self.test_file_name = test_file_name
        self.test_file_numbered = test_file_numbered
        self.additional_instructions_text = additional_instructions_text

    def get_output_model(self) -> Type[BaseModel]:
        """Get the output model type for this prompt.

        Returns:
            Type[BaseModel]: The Pydantic model class that represents the output structure.
        """
        return TestsAnalysis

    def build(self) -> List[BaseMessage]:
        """Build the analyze suite test insert line prompt.

        Returns:
            List[BaseMessage]: List of system and user messages
        """
        messages: List[BaseMessage] = []

        # Build user message
        user_content = self._dedent(
            f"""
            ## Overview
            You are a code assistant that accepts a {self.language} test file as input.
            Your goal is to analyze this file and provide the following: 
            * The programming language of the test file
            * The testing framework needed to run the tests in the test file
            * The number of tests in the test file
            * The line number in the test file where the new test should be inserted. 

            IMPORTANT: Ensure that you account for block delimiters (e.g., curly braces in Java, `end` in Ruby) to correctly place the new test before the end of the relevant block, such as a class or method definition. If a test should live within a class then the insertion happens BEFORE the last delimiter (if relevant).

            Here is the file that contains the existing tests, called `{self.test_file_name}`. Note that we have manually added line numbers for each line of code, to help you understand the structure of the file. Those numbers are not a part of the original code.
            =========
            {self.test_file_numbered.strip()}
            =========
        """
        )

        if self.additional_instructions_text:
            user_content += self._dedent(
                f"""
                {self.additional_instructions_text.strip()}
            """
            )

        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
