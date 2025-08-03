import logging
import typing

from nexosapi.api.controller import NexosAIAPIEndpointController
from nexosapi.config.settings.defaults import COMPLETIONS_DEFAULT_SEARCH_ENGINE, FALLBACK_WEB_SEARCH_TOOL_DESCRIPTION
from nexosapi.domain.metadata import (
    ChatThinkingModeConfiguration,
    OCRToolOptions,
    RAGToolOptions,
    ToolChoiceAsDictionary,
    ToolChoiceFunction,
    ToolDefinition,
    ToolModule,
    ToolType,
    WebSearchToolMCP,
    WebSearchToolOptions,
    WebSearchUserLocation,
)
from nexosapi.domain.requests import ChatCompletionsRequest
from nexosapi.domain.responses import ChatCompletionsResponse


def adjust_tool_choice(
    request: ChatCompletionsRequest,
) -> ChatCompletionsRequest:
    """
    Adjusts the tool choice in the chat completions request to ensure it is a list.

    :param request: The chat completions request object.
    :return: The updated request object with tools as a list.
    """
    if (request.tools and len(request.tools) > 0) and request.tool_choice == "none":
        request.tool_choice = "auto"
    if request.tool_choice == "auto" and not request.tools:
        logging.warning("[SDK] No tools provided in the request. Defaulting to 'none' tool choice.")
        request.tool_choice = "none"
    return request


def create_web_search_tool(
    definition: ToolDefinition,
    options: dict[str, typing.Any] | None = None,
) -> dict[str, typing.Any]:
    """
    Creates a definition for a web search tool.

    :param definition: The definition of the web search tool, which should include "name", "query", "description".
    :param options: Additional options for the web search tool, if any.
    :return: A dictionary representing the web search tool definition.
    """
    query = definition["query"]
    is_strict = definition.get("strict", None)
    if options is None:
        validated_search_options = WebSearchToolOptions(
            mcp=WebSearchToolMCP(
                type="query",
                tool=COMPLETIONS_DEFAULT_SEARCH_ENGINE,  # type: ignore
                query=query,
            ),
        )
    else:
        logging.debug(f"[SDK] Using custom search options: {options}")
        context_size = options.get("search_context_size", None)
        user_location = options.get("user_location", None)
        blank_mcp_options = WebSearchToolMCP.null().model_dump()
        provided_mcp_options = {
            option_name: option
            for option_name, option in options.items()
            if option not in ["name", "description", "strict"]
        }
        mcp_options = {
            "query": query,
            **blank_mcp_options,
            **provided_mcp_options,
        }
        validated_search_options = WebSearchToolOptions(
            search_context_size=context_size,
            user_location=WebSearchUserLocation(**user_location) if user_location else None,
            mcp=WebSearchToolMCP(**mcp_options),
        )
        if validated_search_options.mcp.query:
            validated_search_options.mcp.query = query
        if validated_search_options.mcp.url:
            validated_search_options.mcp.url = query

    return {
        "type": "function",
        "function": {
            "name": definition["name"],
            "description": definition["description"] or FALLBACK_WEB_SEARCH_TOOL_DESCRIPTION,
            **({"parameters": definition["parameters"]} if "parameters" in definition else {}),
            **({"strict": is_strict} if is_strict is not None else {}),
        },
        str(ToolType.WEB_SEARCH): validated_search_options.model_dump(),
    }


def create_ocr_tool(
    definition: ToolDefinition,
    options: dict[str, typing.Any] | None = None,
) -> dict[str, typing.Any]:
    """
    Creates a definition for an OCR tool.

    :param definition: The definition of the OCR tool, which should include "name", "description".
    :param options: Additional options for the OCR tool, if any.
    :return: A dictionary representing the OCR tool definition.
    """
    validated_ocr_options = OCRToolOptions(**options) if options else OCRToolOptions.null()
    return {
        "type": "function",
        "function": {
            "name": definition.get("name", "OCR Tool"),
            "description": definition.get("description", "A tool for performing OCR on images"),
            **({"strict": definition.get("strict", False)} if "strict" in definition else {}),
            **({"parameters": definition.get("parameters", {})} if "parameters" in definition else {}),
        },
        str(ToolType.OCR): validated_ocr_options.model_dump(exclude_none=True),
    }


def create_rag_tool(definition: ToolDefinition, options: dict[str, typing.Any] | None = None) -> dict[str, typing.Any]:
    """
    Creates a definition for a RAG tool.
    :param definition: The definition of the RAG tool, which should include "name", "description", and "query".
    :param options: Additional options for the RAG tool, if any.
    :return: A dictionary representing the RAG tool definition.
    """
    tool_name = definition.get("name", "RAG Tool")
    tool_description = definition.get("description", "A tool for retrieving and generating content")

    validated_rag_options = RAGToolOptions(**options) if options else RAGToolOptions.null()
    return {
        "type": "function",
        "function": {
            "name": tool_name,
            "description": tool_description,
            **({"strict": definition.get("strict", False)} if "strict" in definition else {}),
            **({"parameters": definition.get("parameters", {})} if "parameters" in definition else {}),
        },
        str(ToolType.RAG): {
            "mcp": validated_rag_options.model_dump(exclude_none=True) | {"query": definition["query"]}
        },
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
            definition: ToolDefinition,
            options: dict[str, typing.Any] | None = None,
        ) -> ChatCompletionsRequest:
            """
            Sets the search engine to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param definition: The definition of the web search tool to be used.
            :param options: Optional search options to be used with the search engine.
            :return: The updated request object with the search engine set.
            """
            if not request.tools:
                request.tools = []

            request.tools.append(create_web_search_tool(definition, options))
            return adjust_tool_choice(request)

        @staticmethod
        def with_rag_tool(
            request: ChatCompletionsRequest, definition: ToolDefinition, options: dict[str, typing.Any] | None = None
        ) -> ChatCompletionsRequest:
            """
            Sets the RAG tool to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param definition: The definition of the RAG tool to be used, which should include "name", "description".
            :param options: Additional options for the RAG tool, if any.
            :return: The updated request object with the RAG tool set.
            """
            if request.tools is None:
                request.tools = []

            request.tools.append(create_rag_tool(definition, options))
            return adjust_tool_choice(request)

        @staticmethod
        def with_ocr_tool(
            request: ChatCompletionsRequest, definition: ToolDefinition, options: dict[str, typing.Any] | None = None
        ) -> ChatCompletionsRequest:
            """
            Sets the OCR tool to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param definition: The definition of the OCR tool to be used, which should include "name", "description".
            :param options: Additional options for the OCR tool, if any.
            :return: The updated request object with the OCR tool set.
            """
            if request.tools is None:
                request.tools = []

            request.tools.append(create_ocr_tool(definition, options))
            return adjust_tool_choice(request)

        @staticmethod
        def with_combined_tool(
            request: ChatCompletionsRequest, definition: ToolDefinition, modules: list[ToolModule]
        ) -> ChatCompletionsRequest:
            """
            Sets multiple tools to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param definition: The definition of the combined tool, which should include "name", "description".
            :param modules: A list of ToolModule instances, each containing a definition and optional options.
            :return: The updated request object with the tools set.
            """
            if request.tools is None:
                request.tools = []

            combined_tool = {}
            for module in modules:
                module_options = module.get("options")

                match module_type := module["type"]:
                    case ToolType.WEB_SEARCH:
                        combined_tool.update(create_web_search_tool(definition, module_options))
                    case ToolType.RAG:
                        combined_tool.update(create_rag_tool(definition, module_options))
                    case ToolType.OCR:
                        combined_tool.update(create_ocr_tool(definition, module_options))
                    case _:
                        logging.error("[SDK] Unsupported tool type: %s. Skipping...", module_type)

            request.tools.append(combined_tool)
            return adjust_tool_choice(request)

        @staticmethod
        def with_parallel_tool_calls(request: ChatCompletionsRequest, enabled: bool = True) -> ChatCompletionsRequest:
            """
            Enables or disables parallel tool calls for the chat completion request.

            :param request: The request object containing the chat completion parameters.
            :param enabled: A boolean indicating whether to enable parallel tool calls.
            :return: The updated request object with the parallel tool calls set.
            """
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
            if not tool_choice:
                logging.warning("[SDK] No tool choice settings provided. Using default 'auto' tool choice.")
                return adjust_tool_choice(request)

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
