import json
import logging
import typing

from pydantic import BaseModel

from nexosapi.api.controller import NexosAIAPIEndpointController
from nexosapi.domain.data import ChatMessage
from nexosapi.domain.metadata import (
    ChatThinkingModeConfiguration,
    OCRToolOptions,
    RAGToolOptions,
    ToolChoiceAsDictionary,
    ToolChoiceFunction,
    ToolType,
    WebSearchToolOptions,
)
from nexosapi.domain.requests import ChatCompletionsRequest
from nexosapi.domain.responses import ChatCompletionsResponse


def create_web_search_tool(
    options: WebSearchToolOptions | None = None,
) -> dict[str, typing.Any]:
    """
    Creates a definition for a web search tool.

    :param options: Additional options for the web search tool, if any.
    :return: A dictionary representing the web search tool definition.
    """
    if options:
        return {"type": str(ToolType.WEB_SEARCH), str(ToolType.WEB_SEARCH): options.model_dump()}
    return {"type": str(ToolType.WEB_SEARCH)}


def create_ocr_tool(
    options: OCRToolOptions,
) -> dict[str, typing.Any]:
    """
    Creates a definition for an OCR tool.

    :param options: Additional options for the OCR tool, if any.
    :return: A dictionary representing the OCR tool definition.
    """
    return {
        "type": str(ToolType.OCR),
        str(ToolType.OCR): options.model_dump(),
    }


class ChatCompletionsEndpointController(NexosAIAPIEndpointController):
    """
    Controller for handling chat completions endpoint of NexosAI.
    """

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
            request: ChatCompletionsRequest, options: WebSearchToolOptions | dict[str, typing.Any]
        ) -> ChatCompletionsRequest:
            """
            Sets the search engine to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param options: Optional search options to be used with the search engine.
            :return: The updated request object with the search engine set.
            """
            if not request.tools:
                request.tools = []

            if isinstance(options, dict):
                # If options is a dictionary, convert it to WebSearchToolOptions
                options = WebSearchToolOptions(**options)

            if options:
                request.tools.append({"type": str(ToolType.WEB_SEARCH), str(ToolType.WEB_SEARCH): options.model_dump()})
            else:
                request.tools.append({"type": str(ToolType.WEB_SEARCH)})
            return request

        @staticmethod
        def with_rag_tool(
            request: ChatCompletionsRequest, options: RAGToolOptions | dict[str, typing.Any]
        ) -> ChatCompletionsRequest:
            """
            Sets the RAG tool to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param options: Additional options for the RAG tool, if any.
            :return: The updated request object with the RAG tool set.
            """
            if request.tools is None:
                request.tools = []

            if isinstance(options, dict):
                # If options is a dictionary, convert it to RAGToolOptions
                options = RAGToolOptions(**options)

            request.tools.append(
                {
                    "type": str(ToolType.RAG),
                    str(ToolType.RAG): {"mcp": options.model_dump()},
                }
            )
            return request

        @staticmethod
        def with_ocr_tool(
            request: ChatCompletionsRequest, options: OCRToolOptions | dict[str, typing.Any]
        ) -> ChatCompletionsRequest:
            """
            Sets the OCR tool to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param options: Additional options for the OCR tool, if any.
            :return: The updated request object with the OCR tool set.
            """
            if request.tools is None:
                request.tools = []

            if isinstance(options, dict):
                # If options is a dictionary, convert it to OCRToolOptions
                options = OCRToolOptions(**options)

            request.tools.append(
                {
                    "type": str(ToolType.OCR),
                    str(ToolType.OCR): options.model_dump(),
                }
            )
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
            """
            Sets the tool choice for the chat completion request e.g. "auto" or to specific function name using "name:<function_name>" selector.

            :param request: The request object containing the chat completion parameters.
            :param tool_choice: The tool choice to be set for the request.
            :return: The updated request object with the tool choice set.
            """
            if tool_choice.startswith("name:"):
                validated_tool_choice_settings = ToolChoiceAsDictionary(
                    type="function",
                    function=ToolChoiceFunction(name=tool_choice[5:]),  # Extract the function name after 'name:'
                )
                request.tool_choice = validated_tool_choice_settings.model_dump()
            else:
                request.tool_choice = tool_choice
            return request

        @staticmethod
        def add_image_to_last_message(
            request: ChatCompletionsRequest, image_url: str | None = None, image: bytes | None = None
        ) -> ChatCompletionsRequest:
            """
            Adds an image to the last message in the chat completion request.

            :param request: The request object containing the chat completion parameters.
            :param image_url: The URL of the image to be included in the request.
            :param image: The image data to be included in the request.
            :return: The updated request object with the image included.
            """
            if not image_url and not image:
                logging.warning("[SDK] No image provided. Skipping adding image to the request.")
                return request

            if len(request.messages) > 0 and request.messages[-1].role == "user":
                # If the last message is from the user, append the image to it
                if isinstance(request.messages[-1].content, list):
                    request.messages[-1].content.append({"type": "image_url", "image_url": {"url": image_url or image}})
                if isinstance(request.messages[-1].content, str):
                    request.messages[-1].content = [
                        {"type": "text", "text": request.messages[-1].content},
                        {"type": "image_url", "image_url": {"url": image_url or image}},
                    ]
            if (len(request.messages) > 0 and request.messages[-1].role != "user") or len(request.messages) == 0:
                request.messages.append(
                    ChatMessage(role="user", content=[{"type": "image_url", "image_url": {"url": image_url or image}}])
                )

            return request

        @staticmethod
        def add_text_message(
            request: ChatCompletionsRequest,
            text: str,
            role: str = "user",
        ) -> ChatCompletionsRequest:
            """
            Adds a text message to the chat completion request.

            :param request: The request object containing the chat completion parameters.
            :param text: The content of the message, which can include text, images, etc.
            :param role: The role of the message sender (e.g., "user", "assistant"). Defaults to "user".
            :return: The updated request object with the new message added.
            """
            request.messages.append(ChatMessage(role=role, content=text))
            return request

        @staticmethod
        def set_response_structure(
            request: ChatCompletionsRequest, schema: dict[str, typing.Any] | type[BaseModel]
        ) -> ChatCompletionsRequest:
            """
            Sets the response structure for the chat completion request.

            :param request: The request object containing the chat completion parameters.
            :param schema: The desired response schema (e.g., a Pydantic model).
            :return: The updated request object with the response structure set.
            """
            schema_system_message = ChatMessage(
                role="system",
                content=f"""
                Please provide a response in the following JSON format:
                {json.dumps(schema if isinstance(schema, dict) else schema.model_json_schema())}
                """,
            )
            request.messages.append(schema_system_message)
            request.response_format = {
                "type": "json_object"  # Specify that we want a JSON object response!
            }
            return request
