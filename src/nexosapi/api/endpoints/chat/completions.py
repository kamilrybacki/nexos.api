import logging
import typing

from nexosapi.api.controller import NexosAIAPIEndpointController
from nexosapi.domain.metadata import (
    ChatThinkingModeConfiguration,
    OCRToolOptions,
    RAGToolOptions,
    ToolChoiceAsDictionary,
    ToolChoiceFunction,
    ToolType,
    WebSearchToolMCP,
    WebSearchToolOptions,
    WebSearchUserLocation,
)
from nexosapi.domain.requests import ChatCompletionsRequest
from nexosapi.domain.responses import ChatCompletionsResponse


def create_web_search_tool(
    options: dict[str, typing.Any] | None = None,
) -> dict[str, typing.Any]:
    """
    Creates a definition for a web search tool.

    :param options: Additional options for the web search tool, if any.
    :return: A dictionary representing the web search tool definition.
    """
    validated_search_options = None
    if options:
        context_size = options.get("search_context_size", None)
        user_location = options.get("user_location", None)
        validated_search_options = WebSearchToolOptions(
            search_context_size=context_size,
            user_location=WebSearchUserLocation(**user_location) if user_location else None,
            mcp=WebSearchToolMCP(**options.get("mcp", {})) if options.get("mcp") else None,
        )

    return {
        "type": str(ToolType.WEB_SEARCH),
        **({str(ToolType.WEB_SEARCH): validated_search_options.model_dump()} if validated_search_options else {}),
    }


def create_ocr_tool(
    options: dict[str, typing.Any],
) -> dict[str, typing.Any]:
    """
    Creates a definition for an OCR tool.

    :param options: Additional options for the OCR tool, if any.
    :return: A dictionary representing the OCR tool definition.
    """
    validated_ocr_options = OCRToolOptions(**options)
    return {
        "type": str(ToolType.OCR),
        str(ToolType.OCR): validated_ocr_options.model_dump(),
    }


def create_rag_tool(options: dict[str, typing.Any]) -> dict[str, typing.Any]:
    """
    Creates a definition for a RAG tool.
    :param options: Additional options for the RAG tool, if any.
    :return: A dictionary representing the RAG tool definition.
    """
    validated_rag_options = RAGToolOptions(**options)
    return {
        "type": str(ToolType.RAG),
        str(ToolType.RAG): {"mcp": validated_rag_options.model_dump()},
    }


class ChatCompletionsEndpointController(NexosAIAPIEndpointController):
    endpoint = "post:/chat/completions"
    response_model = ChatCompletionsResponse
    request_model = ChatCompletionsRequest

    class Operations:
        @staticmethod
        def with_model(request: ChatCompletionsRequest, model: str) -> ChatCompletionsRequest:
            """
            Sets the model to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param model: The model to be used for the chat completion.
            :return: The updated request object with the model set.
            """
            request.model = model
            return request

        @staticmethod
        def with_search_engine_tool(
            request: ChatCompletionsRequest,
            options: typing.Annotated[dict[str, typing.Any], "model:WebSearchToolOptions"],
        ) -> ChatCompletionsRequest:
            """
            Sets the search engine to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param options: Optional search options to be used with the search engine.
            :type options: WebSearchToolOptions
            :return: The updated request object with the search engine set.
            """
            if not request.tools:
                request.tools = []

            request.tools.append(create_web_search_tool(options))
            return request

        @staticmethod
        def with_rag_tool(
            request: ChatCompletionsRequest, options: typing.Annotated[dict[str, typing.Any], "model:RAGToolOptions"]
        ) -> ChatCompletionsRequest:
            """
            Sets the RAG tool to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param options: Additional options for the RAG tool, if any.
            :return: The updated request object with the RAG tool set.
            """
            if request.tools is None:
                request.tools = []

            request.tools.append(create_rag_tool(options))
            return request

        @staticmethod
        def with_ocr_tool(
            request: ChatCompletionsRequest, options: typing.Annotated[dict[str, typing.Any], "model:OCRToolOptions"]
        ) -> ChatCompletionsRequest:
            """
            Sets the OCR tool to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param options: Additional options for the OCR tool, if any.
            :return: The updated request object with the OCR tool set.
            """
            if request.tools is None:
                request.tools = []

            request.tools.append(create_ocr_tool(options))
            return request

        @staticmethod
        def with_parallel_tool_calls(request: ChatCompletionsRequest, enabled: bool = True) -> ChatCompletionsRequest:
            """
            Enables or disables parallel tool calls for the chat completion request.

            :param request: The request object containing the chat completion parameters.
            :param enabled: A boolean indicating whether to enable parallel tool calls.
            :return: The updated request object with the parallel tool calls set.
            """
            if request.tools is None:
                logging.warning("[SDK] No tools provided, parallel tool calls SHOULD NOT be set.")
            request.parallel_tool_calls = enabled
            return request

        @staticmethod
        def with_thinking(
            request: ChatCompletionsRequest, config: ChatThinkingModeConfiguration | None = None, disabled: bool = False
        ) -> ChatCompletionsRequest:
            """
            Enables or disables thinking for the chat completion request.

            :param request: The request object containing the chat completion parameters.
            :param config: The configuration for the thinking mode, which includes parameters like "enabled", "max_steps", etc.
            :param disabled: A boolean indicating whether to disable thinking mode.
            :return: The updated request object with the thinking set.
            """
            if config is None or len(config.keys()) == 0:
                logging.warning("[SDK] No thinking mode configuration provided. Disabling thinking mode.")
                request.thinking = None
                return request
            if disabled:
                request.thinking = None
                logging.info("[SDK] Disabled thinking mode.")
                return request

            request.thinking = config
            return request

        @staticmethod
        def with_tool_choice(
            request: ChatCompletionsRequest,
            tool_choice: str,
        ) -> ChatCompletionsRequest:
            # Check if passed tool_choice is a string in format 'name:<function_name>'
            if tool_choice.startswith("name:"):
                validated_tool_choice_settings = ToolChoiceAsDictionary(
                    type="function",
                    function=ToolChoiceFunction(name=tool_choice[5:]),  # Extract the function name after 'name:'
                )
                request.tool_choice = validated_tool_choice_settings.model_dump()
            else:
                request.tool_choice = tool_choice
            return request
