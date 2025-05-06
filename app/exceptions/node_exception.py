class InvalidReasoningException(Exception):
    def __init__(self, message: str = "Empty tool_calls") -> None:
        super().__init__(message)


class ToolNodeException(Exception):
    def __init__(self, message: str = "Error during tool processing") -> None:
        super().__init__(message)


class EmptyOutputException(Exception):
    def __init__(self, message: str = "Empty structured output") -> None:
        super().__init__(message)
