import logging
from abc import ABC
from typing import Sequence, Callable, List, Type, TypeVar, Coroutine, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.types import RetryPolicy
from pydantic import BaseModel

from exceptions.node_exception import (
    InvalidReasoningException,
    ToolNodeException,
    EmptyOutputException,
)

AgentStateLike = TypeVar("AgentStateLike", bound=AgentState)
OutputLike = TypeVar("OutputLike", bound=BaseModel)


class BaseAgentBuilder(ABC):
    def build(self, **kwargs) -> CompiledGraph:
        pass

    @classmethod
    def create_agentic_graph(
        cls,
        state_schema: Type[AgentStateLike],
        llm_node: Callable[[AgentStateLike], Coroutine[Any, Any, AgentStateLike]],
        output_node: Callable[[AgentStateLike], Coroutine[Any, Any, AgentStateLike]],
        tools: List[BaseTool],
    ) -> StateGraph:
        workflow = StateGraph(state_schema)

        retry_policy = RetryPolicy(
            retry_on=lambda e: isinstance(e, InvalidReasoningException)
            or isinstance(e, EmptyOutputException),
            max_attempts=3,
            initial_interval=2.0,
            backoff_factor=4.0,
        )

        workflow.add_node("llm_node", llm_node, retry=retry_policy)
        workflow.add_node("tool_node", ToolNode(tools))
        workflow.add_node("output_node", output_node, retry=retry_policy)

        workflow.set_entry_point("llm_node")
        workflow.add_edge("llm_node", "tool_node")
        workflow.add_edge("tool_node", "output_node")
        workflow.set_finish_point("output_node")

        return workflow

    @classmethod
    def create_llm_node(
        cls,
        model: BaseChatModel,
        tools: List[BaseTool],
        message_builder: Callable[
            [AgentStateLike], Sequence[BaseMessage]
        ] = lambda state: state["messages"],
    ) -> Callable[[AgentStateLike], Coroutine[Any, Any, AgentStateLike]]:
        async def llm_node(state: AgentStateLike) -> AgentStateLike:
            logging.info("에이전트 추론 중...")
            model_with_tools = model.bind_tools(tools)
            inputs = message_builder(state)
            output: BaseMessage = await model_with_tools.ainvoke(inputs)
            if _is_invalid_reasoning(output, state):
                logging.error("Invalid reasoning exception")
                raise InvalidReasoningException()
            logging.info("도구 선택: %s", output.tool_calls)
            state["messages"] += [output]
            return state

        return llm_node

    @classmethod
    def create_output_node(
        cls,
        model: BaseChatModel,
        output_schema: Type[BaseModel],
        output_processor: Callable[
            [AgentStateLike, OutputLike], None
        ] = lambda state, output: ...,
    ) -> Callable[[AgentStateLike], Coroutine[Any, Any, AgentStateLike]]:
        async def output_node(state: AgentStateLike) -> AgentStateLike:
            if (
                len(state["messages"]) > 0
                and "ToolException" in state["messages"][-1].content
            ):
                raise ToolNodeException()
            model_with_output = model.with_structured_output(output_schema)
            inputs = [
                state["messages"][-1].content,
                "DO NOT GENERATE THE FIELD VALUES, just parse",
            ]
            logging.info("도구 호출 결과: %s", state["messages"][-1].content)
            response: OutputLike = await model_with_output.ainvoke(inputs)
            if response is None:
                raise EmptyOutputException()
            state["structured_response"] = response
            output_processor(state, response)
            logging.info("매핑 결과: %s", response)
            return state

        return output_node


def _is_invalid_reasoning(current_message: BaseMessage, state: AgentStateLike) -> bool:
    if not isinstance(current_message, AIMessage):
        return False
    return _is_empty_tool_calls(current_message) and _no_tool_calls_in_messages(state)


def _is_empty_tool_calls(message: AIMessage) -> bool:
    curr_tool_calls = len(message.tool_calls)
    return curr_tool_calls == 0


def _no_tool_calls_in_messages(state: AgentStateLike) -> bool:
    prev_tool_message_count = len(
        list(filter(lambda msg: isinstance(msg, ToolMessage), state["messages"]))
    )
    return prev_tool_message_count == 0
