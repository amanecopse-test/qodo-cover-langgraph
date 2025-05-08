import logging
from abc import ABC, abstractmethod
from typing import (
    Literal,
    Optional,
    Sequence,
    Callable,
    List,
    Type,
    TypeVar,
    Coroutine,
    Any,
)

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph
from langgraph.prebuilt.chat_agent_executor import (
    AgentStateWithStructuredResponsePydantic,
)
from langgraph.graph.graph import CompiledGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import RetryPolicy
from pydantic import BaseModel

from app.exceptions.node_exception import (
    InvalidReasoningException,
    EmptyOutputException,
)

AgentStateLike = TypeVar(
    "AgentStateLike", bound=AgentStateWithStructuredResponsePydantic
)
OutputLike = TypeVar("OutputLike", bound=BaseModel)

LLM_NODE = "llm_node"
TOOL_NODE = "tool_node"
OUTPUT_NODE = "output_node"

retry_policy = RetryPolicy(
    retry_on=lambda e: isinstance(e, InvalidReasoningException)
    or isinstance(e, EmptyOutputException),
    max_attempts=3,
    initial_interval=2.0,
    backoff_factor=4.0,
)


class BaseAgentBuilder(ABC):
    def __init__(
        self,
        model: BaseChatModel,
        tools: List[BaseTool] = [],
        tool_call_mode: Literal["multi_turn", "single_turn", "none"] = "single_turn",
    ):
        self.model = model
        self.tools = tools
        self.tool_call_mode = tool_call_mode

    @abstractmethod
    def build(self, *args, **kwargs) -> CompiledGraph:
        pass

    def create_agentic_graph(
        self,
        state_schema: Type[AgentStateLike],
        llm_node: Callable[[AgentStateLike], Coroutine[Any, Any, AgentStateLike]],
        output_node: Callable[[AgentStateLike], Coroutine[Any, Any, AgentStateLike]],
        tools: Optional[List[BaseTool]] = None,
    ) -> StateGraph:
        if tools is None:
            tools = self.tools

        workflow = StateGraph(state_schema)

        workflow.add_node(LLM_NODE, llm_node, retry=retry_policy)
        workflow.add_node(TOOL_NODE, ToolNode(tools))
        workflow.add_node(OUTPUT_NODE, output_node, retry=retry_policy)

        def route_from_tool_node(
            state: AgentStateLike,
        ) -> Literal["llm_node", "output_node"]:
            if len(state.messages) == 0:
                raise Exception("No messages in state")

            if (
                "ToolException" in state.messages[-1].content
                or state.messages[-1].status == "error"
            ):
                return LLM_NODE

            if self.tool_call_mode == "none":
                return OUTPUT_NODE
            elif self.tool_call_mode == "single_turn":
                return OUTPUT_NODE
            elif self.tool_call_mode == "multi_turn":
                if isinstance(state.messages[-1], ToolMessage):
                    return LLM_NODE
                else:
                    return OUTPUT_NODE

        workflow.set_entry_point(LLM_NODE)
        workflow.add_edge(LLM_NODE, TOOL_NODE)
        workflow.add_conditional_edges(
            TOOL_NODE,
            route_from_tool_node,
            {
                LLM_NODE: LLM_NODE,
                OUTPUT_NODE: OUTPUT_NODE,
            },
        )
        workflow.set_finish_point(OUTPUT_NODE)

        return workflow

    def create_llm_node(
        self,
        model: Optional[BaseChatModel] = None,
        tools: Optional[List[BaseTool]] = None,
        message_builder: Callable[
            [AgentStateLike], Sequence[BaseMessage]
        ] = lambda state: state.messages,
    ) -> Callable[[AgentStateLike], Coroutine[Any, Any, AgentStateLike]]:
        if model is None:
            model = self.model
        if tools is None:
            tools = self.tools

        async def llm_node(state: AgentStateLike) -> AgentStateLike:
            logging.info("에이전트 추론 중...")
            model_with_tools = model.bind_tools(tools)
            inputs = message_builder(state)
            new_message: BaseMessage = await model_with_tools.ainvoke(inputs)
            if not self._is_valid_reasoning(new_message, state):
                logging.error("Invalid reasoning exception")
                raise InvalidReasoningException()
            logging.info("도구 선택: %s", new_message.tool_calls)
            return {
                "messages": [new_message],
            }

        return llm_node

    def create_output_node(
        self,
        output_schema: Type[BaseModel],
        model: Optional[BaseChatModel] = None,
        output_processor: Callable[
            [AgentStateLike, OutputLike], None
        ] = lambda state, output: ...,
    ) -> Callable[[AgentStateLike], Coroutine[Any, Any, AgentStateLike]]:
        if model is None:
            model = self.model

        async def output_node(state: AgentStateLike) -> AgentStateLike:
            model_with_output = model.with_structured_output(output_schema)
            inputs = [
                state.messages[-1].content,
                "DO NOT GENERATE THE FIELD VALUES, just parse",
            ]
            logging.info("도구 호출 결과: %s", state.messages[-1].content)
            response: OutputLike = await model_with_output.ainvoke(inputs)
            if response is None:
                raise EmptyOutputException()
            output_processor(state, response)
            logging.info("매핑 결과: %s", response)
            return {
                "structured_response": response,
            }

        return output_node

    def _is_valid_reasoning(
        self,
        current_message: BaseMessage,
        state: AgentStateLike,
    ) -> bool:
        if not isinstance(current_message, AIMessage):
            return False

        if self.tool_call_mode == "none":
            return _is_empty_tool_calls(current_message)
        elif self.tool_call_mode == "single_turn":
            return not _is_empty_tool_calls(current_message)
        elif self.tool_call_mode == "multi_turn":
            return not (
                _is_empty_tool_calls(current_message)
                and _no_tool_calls_in_messages(state)
            )


def _is_empty_tool_calls(message: AIMessage) -> bool:
    curr_tool_calls = len(message.tool_calls)
    return curr_tool_calls == 0


def _no_tool_calls_in_messages(state: AgentStateLike) -> bool:
    prev_tool_message_count = len(
        list(
            filter(
                lambda msg: isinstance(msg, ToolMessage) and msg.status != "error",
                state.messages,
            )
        )
    )
    return prev_tool_message_count == 0
