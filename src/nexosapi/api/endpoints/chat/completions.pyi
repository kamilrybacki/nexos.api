from __future__ import annotations
import typing
from nexosapi.api.controller import NexosAIAPIEndpointController as NexosAIAPIEndpointController
from nexosapi.domain.data import ChatMessage as ChatMessage
from nexosapi.domain.metadata import (
    ChatThinkingModeConfiguration as ChatThinkingModeConfiguration,
    OCRToolOptions as OCRToolOptions,
    RAGToolOptions as RAGToolOptions,
    ToolChoiceAsDictionary as ToolChoiceAsDictionary,
    ToolChoiceFunction as ToolChoiceFunction,
    ToolType as ToolType,
    WebSearchToolOptions as WebSearchToolOptions,
)
from nexosapi.domain.requests import ChatCompletionsRequest as ChatCompletionsRequest
from nexosapi.domain.responses import ChatCompletionsResponse as ChatCompletionsResponse
from pydantic import BaseModel as BaseModel

def create_web_search_tool(options: WebSearchToolOptions | None = None) -> dict[str, typing.Any]:
    """
    Creates a definition for a web search tool.

    :param options: Additional options for the web search tool, if any.
    :return: A dictionary representing the web search tool definition.
    """

def create_ocr_tool(options: OCRToolOptions) -> dict[str, typing.Any]:
    """
    Creates a definition for an OCR tool.

    :param options: Additional options for the OCR tool, if any.
    :return: A dictionary representing the OCR tool definition.
    """

class ChatCompletionsEndpointController(NexosAIAPIEndpointController):
    """
    Controller for handling chat completions endpoint of NexosAI.
    """

    endpoint: str
    response_model = ChatCompletionsResponse
    request_model = ChatCompletionsRequest

    class RequestManager(ChatCompletionsEndpointController._RequestManager):
        @staticmethod
        def with_model(model: str) -> ChatCompletionsEndpointController.RequestManager:
            """Sets the model to be used for the chat completion.

            :param model: The model to be used for the chat completion.
            :return: The updated request object with the model set."""

        @staticmethod
        def with_search_engine_tool(
            options: WebSearchToolOptions | dict[str, typing.Any],
        ) -> ChatCompletionsEndpointController.RequestManager:
            """Sets the search engine to be used for the chat completion.

            :param options: Optional search options to be used with the search engine.
            :return: The updated request object with the search engine set."""

        @staticmethod
        def with_rag_tool(
            options: RAGToolOptions | dict[str, typing.Any],
        ) -> ChatCompletionsEndpointController.RequestManager:
            """Sets the RAG tool to be used for the chat completion.

            :param options: Additional options for the RAG tool, if any.
            :return: The updated request object with the RAG tool set."""

        @staticmethod
        def with_ocr_tool(
            options: OCRToolOptions | dict[str, typing.Any],
        ) -> ChatCompletionsEndpointController.RequestManager:
            """Sets the OCR tool to be used for the chat completion.

            :param options: Additional options for the OCR tool, if any.
            :return: The updated request object with the OCR tool set."""

        @staticmethod
        def with_parallel_tool_calls(enabled: bool = True) -> ChatCompletionsEndpointController.RequestManager:
            """Enables or disables parallel tool calls for the chat completion request.

            :param enabled: A boolean indicating whether to enable parallel tool calls.
            :return: The updated request object with the parallel tool calls set."""

        @staticmethod
        def with_thinking(
            config: ChatThinkingModeConfiguration | None = None, disabled: bool = False
        ) -> ChatCompletionsEndpointController.RequestManager:
            """Enables or disables thinking for the chat completion request.

            :param config: The configuration for the thinking mode, which includes parameters like "enabled", "max_steps", etc.
            :param disabled: A boolean indicating whether to disable thinking mode.
            :return: The updated request object with the thinking set."""

        @staticmethod
        def with_tool_choice(tool_choice: str) -> ChatCompletionsEndpointController.RequestManager:
            """Sets the tool choice for the chat completion request e.g. "auto" or to specific function name using "name:<function_name>" selector.

            :param tool_choice: The tool choice to be set for the request.
            :return: The updated request object with the tool choice set."""

        @staticmethod
        def add_image_to_last_message(
            image_url: str | None = None, image: bytes | None = None
        ) -> ChatCompletionsEndpointController.RequestManager:
            """Adds an image to the last message in the chat completion request.

            :param image_url: The URL of the image to be included in the request.
            :param image: The image data to be included in the request.
            :return: The updated request object with the image included."""

        @staticmethod
        def add_text_message(text: str, role: str = "user") -> ChatCompletionsEndpointController.RequestManager:
            """Adds a text message to the chat completion request.

            :param text: The content of the message, which can include text, images, etc.
            :param role: The role of the message sender (e.g., "user", "assistant"). Defaults to "user".
            :return: The updated request object with the new message added."""

        @staticmethod
        def set_response_structure(
            schema: dict[str, typing.Any] | type[BaseModel],
        ) -> ChatCompletionsEndpointController.RequestManager:
            """Sets the response structure for the chat completion request.

            :param schema: The desired response schema (e.g., a Pydantic model).
            :return: The updated request object with the response structure set."""

        def get_verb_from_endpoint(self, endpoint: str) -> str:
            """
            Extract the HTTP verb from the endpoint string.

            :param endpoint: The endpoint string in the format "verb: /path".
            :return: The HTTP verb (e.g., "GET", "POST")."""

        def get_path_from_endpoint(self, endpoint: str) -> str:
            """
            Extract the path from the endpoint string.

            :param endpoint: The endpoint string in the format "verb: /path".
            :return: The path (e.g., "/path")."""

        def prepare(
            self, data: ChatCompletionsRequest | dict[str, typing.Any]
        ) -> ChatCompletionsEndpointController.RequestManager:
            """
            Prepare the request data by initializing the pending request.

            :param data: The data to be included in the request.
            :return: The current instance of the RequestManager for method chaining."""

        def dump(self) -> dict[str, typing.Any]:
            """
            Show the current pending request data.

            :return: The pending request data or None if not set."""

        async def send(self) -> ChatCompletionsResponse:
            """
            Call the endpoint with the provided request data.

            :return: The response data from the endpoint."""

        def reload_last(self) -> ChatCompletionsEndpointController.RequestManager:
            """
            Reload the last request to reuse it for the next operation.

            :return: The current instance of the RequestManager for method chaining."""

    request: ChatCompletionsEndpointController.RequestManager
