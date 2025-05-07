import textwrap
from typing import List
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.graph.graph import CompiledGraph

from app.llm.agent.base import BaseAgentBuilder
from app.prompts.test_finder_prompt import TestFinderPrompt
from app.schemas.state import TestFinderState
from app.schemas.structured_output import TestFile


class TestFinderAgent(BaseAgentBuilder):
    """
    타겟 소스를 테스트하는 기존 테스트 코드를 찾거나 생성하고 이에 대한 에디터 객체를 반환하는 에이전트
    """

    def __init__(
        self,
        model: BaseChatModel,
        tools: List[BaseTool] = [],
    ):
        super().__init__(
            model=model,
            tools=tools,
            tool_call_mode="multi_turn",
        )

    def build(self) -> CompiledGraph:
        return self.create_agentic_graph(
            state_schema=TestFinderState,
            llm_node=self.create_llm_node(),
            output_node=self.create_output_node(TestFile),
        ).compile()

    async def find_or_generate_vitest_file(
        self,
        source_file_name: str,
        source_file_content: str,
        source_file_path: str,
    ) -> TestFile:
        agent = self.build()
        response = await agent.ainvoke(
            TestFinderState(
                messages=TestFinderPrompt(
                    language="typescript",
                    source_file_name=source_file_name,
                    source_file_content=source_file_content,
                    source_file_path=source_file_path,
                    testing_framework="vitest",
                    additional_instructions_text=_get_additional_instructions(),
                ).build()
            )
        )
        return response["structured_response"]


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
