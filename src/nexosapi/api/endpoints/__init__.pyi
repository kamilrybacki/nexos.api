from __future__ import annotations
import typing
import dataclasses
from nexosapi.api.endpoints.chat.completions import (
    ChatCompletionsEndpointController as ChatCompletionsEndpointController,
)
from nexosapi.config.setup import wire_sdk_dependencies as wire_sdk_dependencies
from typing import ClassVar

@dataclasses.dataclass(frozen=True)
class ChatEndpoints:
    """
    Main interface for accessing specific endpoint controllers e.g. chat completions or image generation.

    :ivar completions: Controller for handling chat completions.
    """

    completions: ClassVar[ChatCompletionsEndpointController] = ...

chat: ChatEndpoints
