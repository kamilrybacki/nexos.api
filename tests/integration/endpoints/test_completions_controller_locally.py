import pytest

from nexosapi.api.endpoints.chat.completions import ChatCompletionsEndpointController
from nexosapi.domain.metadata import ToolType, ToolChoiceAsDictionary
from nexosapi.domain.requests import ChatCompletionsRequest
from nexosapi.domain.responses import ChatCompletionsResponse

TEST_MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
]
TEST_COMPLETIONS_REQUEST = {"model": "gpt-3.5-turbo", "messages": TEST_MESSAGES}


@pytest.mark.asyncio
@pytest.mark.order("first")
async def test_sending_request(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        prepared_request = controller.request.dump()
        assert prepared_request["model"] == "gpt-3.5-turbo", (
            "The model in the request should be set to 'gpt-3.5-turbo'."
        )
        assert [message["role"] for message in prepared_request["messages"]] == [
            message["role"] for message in TEST_MESSAGES
        ], (
            f"The roles in the messages should match the test messages: "
            f"{[message['role'] for message in TEST_MESSAGES]}."
        )
        assert [message["content"] for message in prepared_request["messages"]] == [
            message["content"] for message in TEST_MESSAGES
        ], (
            f"The contents in the messages should match the test messages: "
            f"{[message['content'] for message in TEST_MESSAGES]}."
        )

        response: ChatCompletionsResponse = await controller.request.send()
        assert response._response.status_code == 200
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )

        response_data = response.model_dump()
        expected_fields = controller.response_model.null().model_dump()
        assert all(field in response_data for field in expected_fields), (
            f"The response should contain all expected fields: {expected_fields}."
        )


@pytest.mark.asyncio
async def test_setting_model(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert current_request_dump["model"] == "gpt-3.5-turbo", "The initial model should be set to 'gpt-3.5-turbo'."

        controller.request.with_model("gemini-1.5-flash")
        updated_request_dump = controller.request.dump()
        assert updated_request_dump["model"] == "gemini-1.5-flash", "The model should be updated to 'gemini-1.5-flash'."

        response = await controller.request.send()
        assert response._response.status_code == 200
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )


@pytest.mark.asyncio
async def test_using_web_search_engine(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert "tools" not in current_request_dump, "The initial request should not contain any tools."

        search_query = "What is the capital of France?"
        controller.request.with_search_engine_tool(
            definition={
                "name": "Web Search",
                "description": "A tool to search the web for information.",
                "query": search_query,
            },
            options={
                "search_context_size": "low",
            },
        )
        updated_request_dump = controller.request.dump()

        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 1, "There should be one tool in the request."
        assert updated_request_dump["tools"][0]["function"]["name"] == "Web Search"
        assert (
            updated_request_dump["tools"][0]["function"]["description"] == "A tool to search the web for information."
        )
        assert updated_request_dump["tools"][0]["web_search"]["mcp"]["options"]["query"] == search_query, (
            f"The search query in the tool should match '{search_query}'."
        )

        response = await controller.request.send()
        assert response._response.status_code == 200
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )

        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        controller.request.with_search_engine_tool(
            definition={
                "name": "Custom Search Engine",
                "description": "A custom search engine for testing purposes",
                "query": search_query,
            },
            options={
                "search_context_size": "medium",
                "user_location": {
                    "country": "France",
                    "city": "Paris",
                    "region": "Île-de-France",
                    "timezone": "Europe/Paris",
                },
                "parse": True,
            },
        )

        updated_request_dump = controller.request.dump()
        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 1, "There should be one tool in the request."
        assert updated_request_dump["tools"][0]["web_search"]["mcp"]["options"]["query"] == search_query, (
            f"The search query in the tool should match '{search_query}'."
        )
        assert updated_request_dump["tools"][0]["web_search"]["search_context_size"] == "medium", (
            "The search context size should be set to 'medium'."
        )
        assert updated_request_dump["tools"][0]["web_search"]["user_location"] == {
            "country": "France",
            "city": "Paris",
            "region": "Île-de-France",
            "timezone": "Europe/Paris",
            "type": "approximate",  # Added by default
        }, "The user location should match the provided location details."

        response = await controller.request.send()
        assert response._response.status_code == 200
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )


@pytest.mark.asyncio
async def test_using_rag_tool(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert "tools" not in current_request_dump, "The initial request should not contain any tools."

        controller.request.with_rag_tool(
            definition={
                "name": "RAG Tool",
                "description": "A tool to retrieve information from a collection.",
                "query": "What are the latest advancements in AI?",
            },
            options={
                "collection_uuid": "example-collection-uuid",
            },
        )
        updated_request_dump = controller.request.dump()

        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 1, "There should be one tool in the request."

        assert updated_request_dump["tools"][0]["function"]["name"] == "RAG Tool", (
            "The name of the RAG tool should be set correctly."
        )
        assert (
            updated_request_dump["tools"][0]["function"]["description"]
            == "A tool to retrieve information from a collection."
        ), "The description of the RAG tool should be set correctly."
        assert updated_request_dump["tools"][0]["rag"]["mcp"]["collection_uuid"] == "example-collection-uuid", (
            "Collection UUID should be set"
        )
        assert updated_request_dump["tools"][0]["rag"]["mcp"]["query"] == "What are the latest advancements in AI?", (
            "The query in the RAG tool should match the provided query."
        )

        response = await controller.request.send()
        assert response._response.status_code == 200
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )


@pytest.mark.asyncio
async def test_using_ocr_tool(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert "tools" not in current_request_dump, "The initial request should not contain any tools."

        controller.request.with_ocr_tool(
            definition={
                "name": "OCR Tool",
                "description": "A tool to perform OCR on images.",
            },
            options={
                "file_id": "example-file-id",
            },
        )
        updated_request_dump = controller.request.dump()

        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 1, "There should be one tool in the request."

        assert updated_request_dump["tools"][0]["function"]["name"] == "OCR Tool", (
            "The name of the OCR tool should be set correctly."
        )
        assert updated_request_dump["tools"][0]["function"]["description"] == "A tool to perform OCR on images.", (
            "The description of the OCR tool should be set correctly."
        )
        assert updated_request_dump["tools"][0]["tika_ocr"]["file_id"] == "example-file-id", (
            "The file ID in the OCR tool should match the provided file ID."
        )

        response = await controller.request.send()
        assert response._response.status_code == 200
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )


@pytest.mark.asyncio
async def test_using_multiple_tools(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert "tools" not in current_request_dump, "The initial request should not contain any tools."

        search_query = "What is the capital of France?"
        controller.request.with_search_engine_tool(
            definition={
                "name": "Web Search",
                "description": "A tool to search the web for information.",
                "query": search_query,
            },
            options={
                "search_context_size": "low",
            },
        )

        controller.request.with_rag_tool(
            definition={
                "name": "RAG Tool",
                "description": "A tool to retrieve information from a collection.",
                "query": "What are the latest advancements in AI?",
            },
            options={
                "collection_uuid": "example-collection-uuid",
            },
        )

        updated_request_dump = controller.request.dump()

        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 2, (
            "There should be two tools in the request: one for web search and one for RAG."
        )
        assert updated_request_dump["tools"][0]["function"]["name"] == "Web Search", (
            "The first tool should be the Web Search tool."
        )
        assert updated_request_dump["tools"][1]["function"]["name"] == "RAG Tool", (
            "The second tool should be the RAG Tool."
        )

        response = await controller.request.send()
        assert response._response.status_code == 200
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )


@pytest.mark.asyncio
async def test_using_combined_tools(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert "tools" not in current_request_dump, "The initial request should not contain any tools."

        combined_tool_definition = {
            "name": "Combined Tool",
            "description": "A tool that combines web search and RAG functionalities.",
            "query": "What is the latest news in AI?",
        }
        web_search_tool_options = {
            "search_context_size": "medium",
            "user_location": {
                "country": "USA",
                "city": "San Francisco",
                "region": "California",
                "timezone": "America/Los_Angeles",
            },
        }
        rag_tool_options = {
            "collection_uuid": "example-collection-uuid",
        }
        ocr_tool_options = {
            "file_id": "example-file-id",
        }

        controller.request.with_combined_tool(
            definition=combined_tool_definition,
            modules=[
                {
                    "type": ToolType.WEB_SEARCH,
                    "options": web_search_tool_options,
                },
                {
                    "type": ToolType.RAG,
                    "options": rag_tool_options,
                },
                {
                    "type": ToolType.OCR,
                    "options": ocr_tool_options,
                },
            ],
        )

        updated_request_dump = controller.request.dump()
        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 1, "There should be one combined tool in the request."
        assert updated_request_dump["tools"][0]["function"]["name"] == "Combined Tool", (
            "The name of the combined tool should be set correctly."
        )
        assert (
            updated_request_dump["tools"][0]["function"]["description"]
            == "A tool that combines web search and RAG functionalities."
        ), "The description of the combined tool should be set correctly."
        assert updated_request_dump["tools"][0][ToolType.WEB_SEARCH]["search_context_size"] == "medium", (
            "The search context size in the combined tool should be set to 'medium'."
        )
        assert updated_request_dump["tools"][0][ToolType.WEB_SEARCH]["user_location"] == {
            "country": "USA",
            "city": "San Francisco",
            "region": "California",
            "timezone": "America/Los_Angeles",
            "type": "approximate",  # Added by default
        }, "The user location in the combined tool should match the provided location details."
        assert updated_request_dump["tools"][0][ToolType.RAG]["mcp"]["collection_uuid"] == "example-collection-uuid", (
            "The collection UUID in the combined tool should match the provided collection UUID."
        )
        assert updated_request_dump["tools"][0][ToolType.OCR]["file_id"] == "example-file-id", (
            "The file ID in the combined tool should match the provided file ID."
        )
        response = await controller.request.send()
        assert response._response.status_code == 200
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )


def test_toggling_parallel_tool_calls(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        controller.request.with_parallel_tool_calls()
        updated_request_dump = controller.request.dump()
        assert updated_request_dump["parallel_tool_calls"] is True, (
            "The request should now have parallel_tool_calls set to True."
        )

        controller.request.with_parallel_tool_calls(enabled=False)
        updated_request_dump = controller.request.dump()
        assert updated_request_dump["parallel_tool_calls"] is False, (
            "The request should now have parallel_tool_calls set to False."
        )


def test_enabling_thinking_mode(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        controller.request.with_thinking(
            {
                "type": "enabled",
                "budget_tokens": 1000,
            }
        )
        updated_request_dump = controller.request.dump()
        assert updated_request_dump["thinking"] == {
            "type": "enabled",
            "budget_tokens": 1000,
        }, "The request should now have thinking mode enabled with a budget of 1000 tokens."
        controller.request.with_thinking(disabled=True)
        updated_request_dump = controller.request.dump()
        assert "thinking" not in updated_request_dump, "The request should now have thinking mode disabled."

        controller.request.with_thinking({})
        updated_request_dump = controller.request.dump()
        assert "thinking" not in updated_request_dump, (
            "The request should now have thinking mode disabled when an empty dictionary is passed."
        )


def test_adjustment_of_tool_choice_setting(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        controller.request.with_tool_choice("auto")
        updated_request_dump = controller.request.dump()
        assert updated_request_dump["tool_choice"] == "auto", "The request should now have tool_choice set to 'auto'."

        # Add some example OCR tool
        controller.request.with_ocr_tool(
            definition={
                "name": "OCR Tool",
                "description": "A tool to perform OCR on images.",
            },
            options={
                "file_id": "example-file-id",
            },
        )
        updated_request_dump = controller.request.dump()
        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 1, "There should be one tool in the request."
        assert updated_request_dump["tool_choice"] == "auto", (
            "The tool_choice should remain 'auto' after adding an OCR tool."
        )

        controller.request.with_tool_choice("required")
        updated_request_dump = controller.request.dump()
        assert updated_request_dump["tool_choice"] == "required", (
            "The request should now have tool_choice set to 'required'."
        )

        controller.request.with_tool_choice("name:example_tool")
        updated_request_dump = controller.request.dump()
        assert (
            updated_request_dump["tool_choice"]
            == ToolChoiceAsDictionary(type="function", function={"name": "example_tool"}).model_dump()
        )


@pytest.mark.asyncio
@pytest.mark.order("last")
async def test_with_chained_operations(
    initialized_controller,
) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        # Prepare the request
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        initial_request_dump = controller.request.dump()

        # Chain operations
        controller.request.with_model("gpt-4")
        controller.request.with_search_engine_tool(
            definition={
                "name": "Web Search",
                "description": "A tool to search the web for information.",
                "query": "What is the capital of France?",
            },
            options={
                "search_context_size": "low",
            },
        )
        controller.request.with_parallel_tool_calls(enabled=True)
        controller.request.with_tool_choice("required")
        controller.request.with_combined_tool(
            definition={
                "name": "Combined Tool",
                "description": "A tool that combines web search and RAG functionalities.",
                "query": "What is the latest news in AI?",
            },
            modules=[
                {
                    "type": ToolType.WEB_SEARCH,
                    "options": {
                        "search_context_size": "medium",
                        "user_location": {
                            "country": "USA",
                            "city": "San Francisco",
                            "region": "California",
                            "timezone": "America/Los_Angeles",
                        },
                    },
                },
                {
                    "type": ToolType.RAG,
                    "options": {
                        "collection_uuid": "example-collection-uuid",
                    },
                },
            ],
        )
        controller.request.with_thinking(
            {
                "type": "enabled",
                "budget_tokens": 500,
            }
        )
        prepared_request = controller.request.dump()
        initial_request_dump.update(
            {
                "model": "gpt-4",
                "messages": TEST_MESSAGES,
                "tools": [
                    {
                        "function": {
                            "name": "Web Search",
                            "description": "A tool to search the web for information.",
                        },
                        "type": "function",
                        str(ToolType.WEB_SEARCH): {
                            "mcp": {
                                "options": {
                                    "parse": False,
                                    "query": "What is the capital of France?",
                                    "tool": "google_search",
                                },
                                "type": "query",
                            },
                            "search_context_size": "low",
                        },
                    },
                    {
                        "function": {
                            "name": "Combined Tool",
                            "description": "A tool that combines web search and RAG functionalities.",
                        },
                        "type": "function",
                        str(ToolType.WEB_SEARCH): {
                            "mcp": {
                                "options": {
                                    "query": "What is the latest news in AI?",
                                    "parse": False,
                                    "tool": "google_search",
                                },
                                "type": "query",
                            },
                            "search_context_size": "medium",
                            "user_location": {
                                "country": "USA",
                                "city": "San Francisco",
                                "region": "California",
                                "timezone": "America/Los_Angeles",
                                "type": "approximate",  # Added by default
                            },
                        },
                        str(ToolType.RAG): {
                            "mcp": {
                                "collection_uuid": "example-collection-uuid",
                                "query": "What is the latest news in AI?",
                            }
                        },
                    },
                ],
                "parallel_tool_calls": True,
                "tool_choice": "required",
                "thinking": {"type": "enabled", "budget_tokens": 500},
            }
        )
        assert prepared_request == initial_request_dump, (
            "The prepared request should match the expected request after chaining operations."
        )

        # Send the request
        response = await controller.request.send()
        assert response._response.status_code == 200
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )
