from mailbox import BabylMessage
from typing import List, Optional, Type, override
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from app.prompts.base import PromptABC
from app.schemas.structured_output import TestFileAnalysis


class TestAnalysisPrompt(PromptABC):
    def __init__(
        self,
        test_file_content: str,
        additional_instructions_text: Optional[str] = None,
    ):
        self.test_file_content = test_file_content
        self.additional_instructions_text = additional_instructions_text

    @override
    def get_output_model(self) -> Type[BaseModel]:
        return TestFileAnalysis

    @override
    def build(self) -> list[HumanMessage]:
        messages: List[BabylMessage] = []

        line_numbered_test_file_content = "\n".join(
            [
                f"{line} // Line number: {i + 1}."
                for i, line in enumerate(self.test_file_content.splitlines())
            ]
        )

        # Build user message
        user_content = self._dedent(
            """
            ## Overview
            You are a code assistant that accepts a test file as input.
            Your goal is to analyze this file, and provide several feedbacks: the indentation of the test headers in the test file, the last line number of the single test, and the last line number of the imports.

            ## Test File
            Here is the target `test_file` that contains the existing tests:
            =========
            {test_file_content}
            =========

            ## Example
            When you analyze below example test, you should return the following object:
            ```typescript
            import {{ describe, test, expect }} from 'vitest'; // Line number: 1. The last line number of the import.
            // Line number: 2
            describe('Test Suite', () => {{ // Line number: 3.
              test('single test1', () => {{ // Line number: 4. This is the line number of the test header. The indentation of the test header is 2.
                expect(true).toBe(true); // Line number: 5.
              }}); // Line number: 6.
              test('single test2', () => {{ // Line number: 7. This is the line number of the test header. The indentation of the test header is 2.
                expect(true).toBe(true); // Line number: 8.
              }}); // Line number: 9. The last line number of the single test.
            }}); // Line number: 10. The last line number of the test suite.
            ```
            Return the following object:
            ```python
            analysis = TestFileAnalysis(
                test_headers_indentation=2,
                last_single_test_line_number=9,
                last_import_line_number=1
            )
            ```

            Now, you need to analyze the `test_file` and provide a object equivalent to type $TestFileAnalysis, according to the following Pydantic definitions:
            =========
            ```python
            class TestFileAnalysis(BaseModel):
                test_headers_indentation: int = Field(
                    description="The indentation of the test headers in the test file. For example, 'def test_...' has an indentation of 0, '  def test_...' has an indentation of 2, '    def test_...' has an indentation of 4, and so on."
                )
                last_single_test_line_number: int = Field(
                    description="The last line number of the single test"
                )
                last_import_line_number: int = Field(
                    description="The last line number of the imports"
                )
            ```
            =========
            """
        ).format(
            test_file_content=line_numbered_test_file_content,
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
            Example:
            ```python
            analysis = TestFileAnalysis(
                test_headers_indentation=0,
                last_single_test_line_number=42,
                last_import_line_number=10
            )
            ```
            =========
            """
        )

        user_message = self._create_user_message(user_content)
        if user_message:
            messages.append(user_message)

        return messages
