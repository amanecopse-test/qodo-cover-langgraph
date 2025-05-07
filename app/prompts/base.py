from abc import ABC, abstractmethod
from textwrap import dedent
from typing import List, Type

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from pydantic import BaseModel


class PromptABC(ABC):
    """Base class for all prompt builders."""

    @abstractmethod
    def build(self) -> List[BaseMessage]:
        """Build and return a list of messages for the prompt.

        Returns:
            List[BaseMessage]: A list of messages containing system and user messages.
        """
        pass

    @abstractmethod
    def get_output_model(self) -> Type[BaseModel]:
        """Get the output model type for this prompt.

        Returns:
            Type[BaseModel]: The Pydantic model class that represents the output structure.
        """
        pass

    def _create_system_message(self, content: str) -> SystemMessage:
        """Create a system message if content is not empty.

        Args:
            content (str): The content of the system message.

        Returns:
            SystemMessage: A system message if content is not empty, None otherwise.
        """
        return SystemMessage(content=content) if content else None

    def _create_user_message(self, content: str) -> HumanMessage:
        """Create a user message if content is not empty.

        Args:
            content (str): The content of the user message.

        Returns:
            HumanMessage: A user message if content is not empty, None otherwise.
        """
        return HumanMessage(content=content) if content else None

    def _dedent(self, text: str) -> str:
        """Remove common leading whitespace from every line in text.

        Args:
            text (str): The text to dedent.

        Returns:
            str: The dedented text.
        """
        return dedent(text)
