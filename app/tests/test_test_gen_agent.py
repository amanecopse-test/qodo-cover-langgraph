import textwrap
import pytest

from app.llm.agent.test_gen_agent import TestGenAgent
from app.llm.model_factory import ModelFactory
from app.schemas.model_factory import GeminiParams
from app.core.setting import gemini_settings


@pytest.mark.asyncio
async def test_test_gen_agent():
    agent = TestGenAgent(
        model=await ModelFactory().load_llm(
            GeminiParams(api_key=gemini_settings.GEMINI_API_KEY)
        )
    )
    response = await agent.generate_vitest_test(
        source_file_name="button.tsx",
        source_file=get_source_file(),
        test_file_name="button.test.tsx",
        test_file=get_test_file(),
    )
    print(response)


def get_test_file():
    return textwrap.dedent(
        """
        import { render, renderWithSetup, screen } from 'shared-utils-test';

        import Button from '../Button';

        describe('<Button/> Test', () => {
          test('Empty test', () => {
            expect(true).toBe(true);
          });
        });
        """
    ).strip()


def get_source_file():
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
