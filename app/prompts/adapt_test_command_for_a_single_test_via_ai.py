from typing import List, Type

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

from app.schemas.structured_output import AdaptedTestCommand
from app.prompts.base import PromptABC


class AdaptTestCommandForASingleTestViaAI(PromptABC):
    """Prompt builder for adapting test command for a single test."""

    def __init__(
        self,
        language: str,
        test_file_name: str,
        test_file: str,
        test_name: str,
        test_command: str,
        test_output: str,
    ):
        """Initialize the adapt test command prompt.

        Args:
            language (str): Programming language of the source code
            test_file_name (str): Name of the test file
            test_file (str): Content of the test file
            test_name (str): Name of the test to adapt
            test_command (str): Command that was used to run the test
            test_output (str): Output of the test command
        """
        self.language = language
        self.test_file_name = test_file_name
        self.test_file = test_file
        self.test_name = test_name
        self.test_command = test_command
        self.test_output = test_output

    def get_output_model(self) -> Type[BaseModel]:
        """Get the output model type for this prompt.

        Returns:
            Type[BaseModel]: The Pydantic model class that represents the output structure.
        """
        return AdaptedTestCommand

    def build(self) -> List[BaseMessage]:
        """Build the adapt test command prompt.

        Returns:
            List[BaseMessage]: List of system and user messages
        """
        messages: List[BaseMessage] = []

        # Build system message
        system_content = "You are a code assistant that helps developers to adapt a command line to run only a single test file."
        system_message = self._create_system_message(system_content)
        if system_message:
            messages.append(system_message)

        # Build user message
        user_content = self._dedent(
            f"""
            ## Overview
            You are a code assistant that accepts a {self.language} test file, a test name, a test command, and a test output.
            Your goal is to adapt the test command to run a single test.

            ## Test File
            Here is the test file that you will be adapting the command for, called `{self.test_file_name}`:
            =========
            {self.test_file.strip()}
            =========

            ## Test Name
            The test name to adapt the command for is: `{self.test_name}`

            ## Test Command
            The command that was used to run the test is:
            ```
            {self.test_command.strip()}
            ```

            ## Test Output
            The output of the test command is:
            ```
            {self.test_output.strip()}
            ```
        """
        )

        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
