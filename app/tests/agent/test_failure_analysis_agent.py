import textwrap
from typing import Annotated
import pytest
from pydantic import BaseModel, Field

from app.llm.agent.failure_analysis_agent import TestFailureAnalysisAgent
from app.llm.model_factory import ModelFactory
from app.schemas.model_factory import GeminiParams
from app.core.setting import gemini_settings
from langchain_core.tools import StructuredTool


class CodebaseToolInput(BaseModel):
    query: str = Field(description="The natural language query to get the codebase")


@pytest.mark.asyncio
async def test_validate_vitest():
    agent = TestFailureAnalysisAgent(
        model=await ModelFactory().load_llm(
            GeminiParams(api_key=gemini_settings.GEMINI_API_KEY)
        ),
        tools=[
            StructuredTool(
                name="codebase_tool",
                description="Tool to get codebase for a source file and its test file",
                func=get_codebase,
                args_schema=CodebaseToolInput,
            )
        ],
    )
    response = await agent.analyze_vitest_failure(
        test_file_name="button.test.tsx",
        test_file_content=get_test_file(),
        source_file_name="button.tsx",
        source_file_content=get_source_file(),
        stdout=get_stdout(),
        stderr=get_stderr(),
    )
    print(response)


def get_stdout():
    return textwrap.dedent(
        """
        FAIL  src/components/Button.test.tsx > <Button/> Test > Should update button text with server response on click
        FAIL  Tests: 1 failed, 1 passed (2 total)
        """
    ).strip()


def get_stderr():
    return textwrap.dedent(
        """
        Error: expect(received).toBeInTheDocument()

        Received element is not present in the document.  
        """
    ).strip()


def get_codebase(
    query: Annotated[str, "The natural language query of the codebase"],
):
    return {
        "file_path": "src/utils/mock_server.ts",
        "content": textwrap.dedent(
            """
            mockServer.get = (url: string) => Promise.resolve('Hello, world!');

            export const mockServer;
            """
        ),
    }


def get_test_file():
    return textwrap.dedent(
        """
        import { render, renderWithSetup, screen, waitFor } from 'shared-utils-test';
        import { vi } from 'vitest';

        import Button from '../Button';

        describe('<Button/> Test', () => {
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

          test('Should update button text with server response on click', async () => {
            const { user } = renderWithSetup(
              <Button>Click me</Button>
            );

            const button = screen.getByRole('button', { name: 'Click me' });
            await user.click(button);

            await waitFor(() => {
              expect(screen.getByRole('button', { name: 'Hi, world!' })).toBeInTheDocument();
            });
          });
        });
        """
    ).strip()


def get_source_file():
    return textwrap.dedent(
        """
        import React, { useState } from 'react';
        import { mockServer } from '../utils/mock_server';

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
          const [buttonText, setButtonText] = useState(children);

          const handleClick = async (event: React.MouseEvent<HTMLButtonElement>) => {
            try {
              const response = await mockServer.get('http://localhost:3000');
              setButtonText(response);
              
              if (onClick) {
                onClick(event);
              }
            } catch (error) {
              console.error('Failed to fetch from mock server:', error);
            }
          };

          return (
            <button
              disabled={disabled}
              onClick={handleClick}
            >
              {buttonText}
            </button>
          );
        };

        export default Button;
        """
    ).strip()
