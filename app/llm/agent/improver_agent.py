import textwrap
from typing import List, Optional
from langchain_core.language_models import BaseChatModel
from langgraph.graph.graph import CompiledGraph

from app.llm.agent.base import BaseAgentBuilder
from app.prompts.improver_prompt import TestGenerationPrompt
from app.schemas.state import TestImproverState
from app.schemas.structured_output import FailedTestReport, NewTests


class TestImproverAgent(BaseAgentBuilder):
    """
    커버리지 향상을 위해 추가 테스트를 생성하는 에이전트
    """

    def __init__(self, model: BaseChatModel):
        super().__init__(
            model=model,
            tools=[],
            tool_call_mode="none",
        )

    def build(self) -> CompiledGraph:
        return self.create_agentic_graph(
            state_schema=TestImproverState,
            llm_node=self.create_llm_node(),
            output_node=self.create_output_node(NewTests),
        ).compile()

    async def generate_vitest_test(
        self,
        source_file_name: str,
        source_file_content: str,
        test_file_name: str,
        test_file_content: str,
        code_coverage_report: Optional[str] = None,
        failed_test_reports: List[FailedTestReport] = [],
    ) -> NewTests:
        agent = self.build()
        failed_tests_section = _parse_failed_test_reports(failed_test_reports)

        response = await agent.ainvoke(
            TestImproverState(
                messages=TestGenerationPrompt(
                    language="typescript",
                    source_file_name=source_file_name,
                    source_file_numbered="\n".join(
                        [
                            f"{i+1}: {line}"
                            for i, line in enumerate(source_file_content.splitlines())
                        ]
                    ),
                    test_file_name=test_file_name,
                    test_file=test_file_content,
                    testing_framework="vitest",
                    code_coverage_report=str(code_coverage_report),
                    max_tests=10,
                    additional_instructions_text=_get_additional_instructions(),
                    failed_tests_section=failed_tests_section,
                ).build()
            )
        )
        return response["structured_response"].new_tests


def _parse_failed_test_reports(
    failed_test_reports: List[FailedTestReport],
) -> Optional[str]:
    if not failed_test_reports and len(failed_test_reports) == 0:
        return None

    return "-----------\n".join(
        [report.model_dump_json() for report in failed_test_reports]
    )


def _get_additional_instructions():
    return textwrap.dedent(
        """
// It's our testing library
/**
 * This file is used to configure the testing library for the project.
 */
import '@testing-library/jest-dom';
import '@testing-library/jest-dom/vitest';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';

import { configure, render, RenderOptions } from '@testing-library/react';
import { ReactNode } from 'react';

configure({ testIdAttribute: 'data-sp-id' });

/**
 * Creates a mock of the event bus store.
 * @returns A mock of the event bus store.
 */
const createEventBusStore = () => ({
  getState: () => ({
    subscribe: vi.fn(),
    subscribeOne: vi.fn(),
    unsubscribe: vi.fn(),
    unsubscribeAll: vi.fn(),
    publish: vi.fn(),
    getLastEvent: vi.fn(),
  }),
});

/**
 * Renders a React component and sets up user events for testing.
 * Combines React Testing Library's render with user event setup for convenience.
 *
 * @param jsx - The React component or JSX element to render
 * @returns An object containing both user event setup and render results
 * @example
 * ```tsx
 * const { user, container } = renderWithSetup(<MyComponent />);
 * await user.click(container.querySelector('button'));
 * ```
 */
const renderWithSetup = (jsx: ReactNode, options?: RenderOptions) => {
  return {
    user: userEvent.setup(),
    ...render(jsx, options),
  };
};

export * from '@testing-library/react';
export { createEventBusStore, renderWithSetup };


// It's Vitest, not Jest

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
