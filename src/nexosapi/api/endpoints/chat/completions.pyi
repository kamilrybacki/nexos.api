from __future__ import annotations
import typing
import typing
from nexosapi.api.controller import NexosAIAPIEndpointController as NexosAIAPIEndpointController
from nexosapi.config.settings.defaults import (
    COMPLETIONS_DEFAULT_SEARCH_ENGINE as COMPLETIONS_DEFAULT_SEARCH_ENGINE,
    FALLBACK_WEB_SEARCH_TOOL_DESCRIPTION as FALLBACK_WEB_SEARCH_TOOL_DESCRIPTION,
)
from nexosapi.domain.metadata import (
    OCRToolOptions as OCRToolOptions,
    RAGToolOptions as RAGToolOptions,
    ToolDefinition as ToolDefinition,
    ToolModule as ToolModule,
    WebSearchToolMCP as WebSearchToolMCP,
    WebSearchToolOptions as WebSearchToolOptions,
    WebSearchUserLocation as WebSearchUserLocation,
)
from nexosapi.domain.requests import ChatCompletionsRequest as ChatCompletionsRequest
from nexosapi.domain.responses import ChatCompletionsResponse as ChatCompletionsResponse

def create_web_search_tool(
    definition: ToolDefinition, options: dict[str, typing.Any] | None = None
) -> dict[str, typing.Any]:
    """
    Creates a definition for a web search tool.

    :param definition: The definition of the web search tool, which should include "name", "query", "description".
    :param options: Additional options for the web search tool, if any.
    :return: A dictionary representing the web search tool definition.
    """

def create_ocr_tool(definition: ToolDefinition, options: dict[str, typing.Any] | None = None) -> dict[str, typing.Any]:
    """
    Creates a definition for an OCR tool.

    :param definition: The definition of the OCR tool, which should include "name", "description".
    :param options: Additional options for the OCR tool, if any.
    :return: A dictionary representing the OCR tool definition.
    """

def create_rag_tool(definition: ToolDefinition, options: dict[str, typing.Any] | None = None) -> dict[str, typing.Any]:
    """
    Creates a definition for a RAG tool.
    :param definition: The definition of the RAG tool, which should include "name", "description", and "query".
    :param options: Additional options for the RAG tool, if any.
    :return: A dictionary representing the RAG tool definition.
    """

class ChatCompletionsEndpointController(NexosAIAPIEndpointController):
    endpoint: str
    response_model = ChatCompletionsResponse
    request_model = ChatCompletionsRequest

    class RequestManager(ChatCompletionsEndpointController._RequestManager):
        @staticmethod
        def with_model(model: str) -> ChatCompletionsRequest:
            """Sets the model to be used for the chat completion.

            :param model: The model to be used for the chat completion.
            :return: The updated request object with the model set."""

        @staticmethod
        def with_search_engine_tool(
            definition: ToolDefinition, options: dict[str, typing.Any] | None = None
        ) -> ChatCompletionsRequest:
            """Sets the search engine to be used for the chat completion.

            :param definition: The definition of the web search tool to be used.
            :param options: Optional search options to be used with the search engine.
            :return: The updated request object with the search engine set."""

        @staticmethod
        def with_rag_tool(
            definition: ToolDefinition, options: dict[str, typing.Any] | None = None
        ) -> ChatCompletionsRequest:
            """Sets the RAG tool to be used for the chat completion.

            :param definition: The definition of the RAG tool to be used, which should include "name", "description".
            :param options: Additional options for the RAG tool, if any.
            :return: The updated request object with the RAG tool set."""

        @staticmethod
        def with_ocr_tool(
            definition: ToolDefinition, options: dict[str, typing.Any] | None = None
        ) -> ChatCompletionsRequest:
            """Sets the OCR tool to be used for the chat completion.

            :param definition: The definition of the OCR tool to be used, which should include "name", "description".
            :param options: Additional options for the OCR tool, if any.
            :return: The updated request object with the OCR tool set."""

        @staticmethod
        def with_combined_tool(definition: ToolDefinition, modules: list[ToolModule]) -> ChatCompletionsRequest:
            """Sets multiple tools to be used for the chat completion.

            :param definition: The definition of the combined tool, which should include "name", "description".
            :param modules: A list of ToolModule instances, each containing a definition and optional options.
            :return: The updated request object with the tools set."""

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

        def prepare(self, data: dict) -> "RequestManager":
            """
            Prepare the request data by initializing the pending request.

            :param data: The data to be included in the request.
            :return: The current instance of the RequestManager for method chaining."""

        def dump(self) -> dict[str, typing.Any]:
            """
            Show the current pending request data.

            :return: The pending request data or None if not set."""

        def send(self) -> typing.Any:
            """
            Call the endpoint with the provided request data.

            :return: The response data from the endpoint."""

    _RequestManager = RequestManager
    request = RequestManager()
