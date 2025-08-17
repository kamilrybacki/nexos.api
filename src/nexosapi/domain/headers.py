from enum import StrEnum


class CompletionHeaders(StrEnum):
    """
    Headers for chat completions.

    :ivar COMPLETION_TIME: The time taken to complete the chat request.
    :ivar MODEL_ID: The ID of the model used for the chat request.
    """

    COMPLETION_TIME = "X-Nexos-Completion-Time-Ms"
    MODEL_ID = "X-Nexos-Model-Id"
