import textwrap
from typing import Annotated
import pytest
from langchain_core.tools import Tool

from app.llm.agent.finder_agent import TestFinderAgent
from app.llm.model_factory import ModelFactory
from app.schemas.model_factory import GeminiParams
from app.core.setting import gemini_settings
from app.schemas.structured_output import TestFile


@pytest.mark.asyncio
async def test_find_or_generate_vitest_file():
    agent = TestFinderAgent(
        model=await ModelFactory().load_llm(
            GeminiParams(api_key=gemini_settings.GEMINI_API_KEY)
        ),
        tools=[
            Tool(
                name="test_finder",
                description="Find the test file for the given source file",
                func=find_test_file,
            )
        ],
    )
    response = await agent.find_or_generate_vitest_file(
        source_file_name="button.tsx",
        source_file_content=get_source_content(),
        source_file_path="src/components/Button.tsx",
    )
    print(response)
    assert (
        response.content
        == find_test_file(source_file_path="src/components/Button.tsx").content
    )


def find_test_file(source_file_path: Annotated[str, "The path to the source file"]):
    content = textwrap.dedent(
        """
        import { render, renderWithSetup, screen } from 'shared-utils-test';

        import Button from '../Button';

        describe('<Button/> Test', () => {
          test('Button test1', () => {
            expect(true).toBe(true);
          });
          test('Button test2', () => {
            expect(true).toBe(true);
          });
        });
        """
    ).strip()

    return TestFile(
        language="typescript",
        name="Button.test.tsx",
        content=content,
        path="src/components/Button.test.tsx",
    )


def get_source_content():
    return textwrap.dedent(
        """
        import { forwardRef } from 'react';
        import { cn } from 'shared-utils-styles';

        export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
          variant?: 'solid' | 'outline' | 'ghost';
        };
        
        const STYLES = {
          base: 'box-border min-w-auto cursor-pointer whitespace-nowrap rounded border p-1 font-bold text-button-base',
          solid: {
            DEFAULT:
              'active:bg-button-solid-content-active bg-button-solid-content hover:bg-button-solid-content-hover text-button-solid-text border-button-solid-border',
            disabled:
              'disabled:bg-button-disabled disabled:hover:bg-button-disabled disabled:active:bg-button-disabled disabled:border-button-disabled-border disabled:cursor-not-allowed',
          },
          outline: {
            DEFAULT:
              'text-button-outline-text bg-button-outline-content hover:bg-button-outline-content-hover active:bg-button-outline-content-active',
            disabled:
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:border-button-disabled-border',
          },
          ghost: {
            DEFAULT:
              'border-none text-button-ghost-text hover:bg-button-ghost-content-hover active:bg-button-ghost-content-active',
            disabled:
              'disabled:bg-button-disabled disabled:hover:bg-button-disabled disabled:active:bg-button-disabled disabled:border-button-disabled-border disabled:cursor-not-allowed',
          },
        };
        
        /**
         * A customizable button component.
         *
         * @component
         * @example
         * // Example usage of the Button component
         * <Button onClick={handleClick} disabled={isDisabled}>
         *   Click me
         * </Button>
         *
         * @param {ButtonProps} props - The props for the Button component.
         * @param {React.Ref<HTMLButtonElement>} ref - The ref for the button element.
         * @returns {JSX.Element} The rendered Button component.
         */
        const Button = forwardRef<HTMLButtonElement, ButtonProps>(
          ({ className, variant = 'solid', ...props }, ref) => {
            let resolvedClassName = STYLES.base;
            if (variant === 'solid') {
              resolvedClassName += ` ${STYLES.solid.DEFAULT} ${STYLES.solid.disabled}`;
            } else if (variant === 'outline') {
              resolvedClassName += ` ${STYLES.outline.DEFAULT} ${STYLES.outline.disabled}`;
            } else if (variant === 'ghost') {
              resolvedClassName += ` ${STYLES.ghost.DEFAULT} ${STYLES.ghost.disabled}`;
            }
        
            return (
              <button
                ref={ref}
                className={cn(resolvedClassName, className)}
                type="button"
                {...props}
              />
            );
          },
        );
        Button.displayName = 'Button';
        
        export default Button;
        """
    ).strip()
