from typing import List, Optional, Type, override
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage
from pydantic import BaseModel

from app.prompts.base import PromptABC
from app.schemas.structured_output import TestFailureAnalysis


class TestFailureAnalysisPrompt(PromptABC):
    def __init__(
        self,
        test_file_name: str,
        test_file_content: str,
        source_file_name: str,
        source_file_content: str,
        stdout: str,
        stderr: str,
        additional_instructions_text: Optional[str] = None,
    ):
        self.test_file_name = test_file_name
        self.test_file_content = test_file_content
        self.source_file_name = source_file_name
        self.source_file_content = source_file_content
        self.stdout = stdout
        self.stderr = stderr
        self.additional_instructions_text = additional_instructions_text

    @override
    def get_output_model(self) -> Type[BaseModel]:
        return TestFailureAnalysis

    @override
    def build(self) -> list[HumanMessage]:
        messages: List[BaseMessage] = []

        system_content = self._dedent(
            """
            Use the following format to analyze the test failure.

            ## ReAct Example
            Thought:
            Failure reason is related to the codebase. I need to find the code that is related to the test failure.
            Action:
            I will use the `codebase_tool` to find the code that is related to the test failure.
            Action Input:
            query: {{The natural language query of the codebase}}
            Observation:
            I found the code that is related to the test failure.
            Thought:
            Now, I know the test failure reason.
            Final Answer:
            {{
                explanation: {{The explanation of the failure reason}}
                failure_reason: {{The test failure reason}}
                suggestions: {{The recommended fixes}}
            }}
            """
        )
        messages.append(SystemMessage(content=system_content))

        # Build user message
        user_content = self._dedent(
            """
            ## Overview
            You are a specialized test analysis assistant focused on unit test regression results.
            Your role is to examine both standard output (stdout) and error output (stderr) from test executions, identify failures, and provide clear, actionable summaries to help understand and resolve test regressions effectively.
            You must use the `codebase_tool` when you need to find the code that is related to the test failure.
            Until you find the final answer, you must call the `codebase_tool` at least once.
            
            
            ## Steps
            1. Determine the code that is related to the test failure.
            2-1. If the test failure reason is related to the codebase(Out of given source code and test code), use the `codebase_tool` to find the code that is related to the test failure.
            2-2. If the test failure reason is related to the test code, you can directly analyze the failure reason.
            3. Analyze the code that is related to the test failure and provide the test failure reason and the recommended fixes.

            ## Test File
            Here is the file that contains the existing tests, called `{test_file_name}`:
            =========
            {test_file_content}
            =========

            ## Source File
            Here is the source file that we are writing tests against, called `{source_file_name}`.
            =========
            {source_file_content}
            =========

            ## Test Run Output
            `stdout` output when running the tests:
            =========
            {stdout}
            =========

            ## Test Run Error
            `stderr` output when running the tests:
            ========= 
            {stderr}
            =========


            Short and concise analysis of why the test run failed, and recommended Fixes (dont add any other information):
            """
        ).format(
            test_file_name=self.test_file_name,
            test_file_content=self.test_file_content,
            source_file_name=self.source_file_name,
            source_file_content=self.source_file_content,
            stdout=self.stdout,
            stderr=self.stderr,
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

        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
