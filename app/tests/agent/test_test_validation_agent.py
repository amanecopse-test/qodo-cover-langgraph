import textwrap
from typing import Annotated
import pytest
from pydantic import BaseModel, Field

from app.llm.agent.test_validation_agent import TestValidationAgent
from app.llm.model_factory import ModelFactory
from app.schemas.model_factory import GeminiParams
from app.core.setting import gemini_settings
from app.schemas.structured_output import TestCoverage
from langchain_core.tools import StructuredTool


class CoverageToolInput(BaseModel):
    source_file_name: str = Field(description="The name of the source file")
    source_file_path: str = Field(description="The path to the source file")
    test_file_name: str = Field(description="The name of the test file")
    test_file_content: str = Field(description="The content of the test file")


@pytest.mark.asyncio
async def test_test_validation_agent():
    agent = TestValidationAgent(
        model=await ModelFactory().load_llm(
            GeminiParams(api_key=gemini_settings.GEMINI_API_KEY)
        ),
        tools=[
            StructuredTool(
                name="coverage_tool",
                description="Tool to get test coverage report for a source file and its test file",
                func=get_coverage_report,
                args_schema=CoverageToolInput,
            )
        ],
    )
    response = await agent.validate_vitest(
        source_file_name="button.tsx",
        source_file_path="src/components/button.tsx",
        test_file_name="button.test.tsx",
        test_file_content=get_test_file(),
    )
    print(response)
    assert response.coverage_percent == 100
    assert response.uncovered_lines == []
    assert response.stdout == ""
    assert response.stderr == ""


def get_coverage_report(
    source_file_name: Annotated[str, "The name of the source file"],
    source_file_path: Annotated[str, "The path to the source file"],
    test_file_name: Annotated[str, "The name of the test file"],
    test_file_content: Annotated[str, "The content of the test file"],
):
    return TestCoverage(
        coverage_percent=100,
        uncovered_lines=[],
        stdout="",
        stderr="",
    )


def get_test_file():
    return textwrap.dedent(
        """
        import { render, renderWithSetup, screen } from 'shared-utils-test';

        import Button from '../Button';

        describe('<Button/> Test', () => {
          test('Should render in DOM', () => {
            render(<Button>button</Button>);
            const button = screen.getByRole('button', {
              name: 'button',
            });
            expect(button).toBeInTheDocument();
            expect(button.textContent).toBe('button');
          });

          test('Should be disabled', () => {
            render(<Button disabled>button</Button>);
            const button = screen.getByRole('button', {
              name: 'button',
            });
            expect(button).toBeDisabled();
          });

          test('Should call the callback function on click', async () => {
            const handleClick = vitest.fn((event) => event);
            const { user } = renderWithSetup(
              <Button onClick={handleClick}>button</Button>,
            );

            const button = screen.getByRole('button', {
              name: 'button',
            });
            await user.click(button);

            expect(handleClick).toHaveBeenCalledOnce();
          });
        });
        """
    ).strip()


def get_source_file():
    return textwrap.dedent(
        """
        import React from 'react';

        interface ButtonProps {
          children: React.ReactNode;
          disabled?: boolean;
          onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
        }

        const Button: React.FC<ButtonProps> = ({
          children,
          disabled = false,
          onClick,
        }) => {
          return (
            <button
              disabled={disabled}
              onClick={onClick}
            >
              {children}
            </button>
          );
        };

        export default Button;
        """
    ).strip()
