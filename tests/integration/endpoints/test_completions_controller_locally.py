import json

import pytest

from nexosapi.api.endpoints.chat.completions import ChatCompletionsEndpointController
from nexosapi.domain.metadata import ToolType, ToolChoiceAsDictionary
from nexosapi.domain.responses import ChatCompletionsResponse

TEST_MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
]
TEST_COMPLETIONS_REQUEST = {"model": "gpt-3.5-turbo", "messages": TEST_MESSAGES}


@pytest.mark.asyncio
@pytest.mark.order("first")
async def test_sending_request(initialized_controller, caplog) -> None:
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
        assert "HTTP/1.1 200 OK" in caplog.text, "The response should indicate a successful request."

        expected_fields = controller.response_model.null().model_dump()
        assert all(field in response for field in expected_fields), (
            f"The response should contain all expected fields: {expected_fields}."
        )


@pytest.mark.asyncio
async def test_setting_model(initialized_controller, caplog) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert current_request_dump["model"] == "gpt-3.5-turbo", "The initial model should be set to 'gpt-3.5-turbo'."

        controller.request.with_model("gemini-1.5-flash")
        updated_request_dump = controller.request.dump()
        assert updated_request_dump["model"] == "gemini-1.5-flash", "The model should be updated to 'gemini-1.5-flash'."

        response = await controller.request.send()
        assert "HTTP/1.1 200 OK" in caplog.text, "The response should indicate a successful request."


@pytest.mark.asyncio
async def test_using_web_search_engine(initialized_controller, caplog) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert "tools" not in current_request_dump, "The initial request should not contain any tools."

        controller.request.with_search_engine_tool(
            options={
                "search_context_size": "low",
            },
        )
        updated_request_dump = controller.request.dump()

        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 1, "There should be one tool in the request."
        assert updated_request_dump["tools"][0]["type"] == str(ToolType.WEB_SEARCH), (
            "The tool type should be 'web_search'."
        )

        response = await controller.request.send()
        assert "HTTP/1.1 200 OK" in caplog.text, "The response should indicate a successful request."

        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        controller.request.with_search_engine_tool(
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
        assert updated_request_dump["tools"][0][str(ToolType.WEB_SEARCH)]["search_context_size"] == "medium", (
            "The search context size should be set to 'medium'."
        )
        assert updated_request_dump["tools"][0][str(ToolType.WEB_SEARCH)]["user_location"] == {
            "country": "France",
            "city": "Paris",
            "region": "Île-de-France",
            "timezone": "Europe/Paris",
            "type": "approximate",  # Added by default
        }, "The user location should match the provided location details."

        response = await controller.request.send()
        assert "HTTP/1.1 200 OK" in caplog.text, "The response should indicate a successful request."


@pytest.mark.asyncio
async def test_using_rag_tool(initialized_controller, caplog) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert "tools" not in current_request_dump, "The initial request should not contain any tools."

        controller.request.with_rag_tool(
            options={
                "query": "What are the latest advancements in AI?",
                "collection_uuid": "example-collection-uuid",
            },
        )
        updated_request_dump = controller.request.dump()

        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 1, "There should be one tool in the request."

        assert updated_request_dump["tools"][0]["type"] == str(ToolType.RAG), "The tool type should be 'rag'."
        assert (
            updated_request_dump["tools"][0][str(ToolType.RAG)]["mcp"]["collection_uuid"] == "example-collection-uuid"
        ), "Collection UUID should be set"
        assert (
            updated_request_dump["tools"][0][str(ToolType.RAG)]["mcp"]["query"]
            == "What are the latest advancements in AI?"
        ), "The query in the RAG tool should match the provided query."

        response = await controller.request.send()
        assert "HTTP/1.1 200 OK" in caplog.text, "The response should indicate a successful request."


@pytest.mark.asyncio
async def test_using_ocr_tool(initialized_controller, caplog) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert "tools" not in current_request_dump, "The initial request should not contain any tools."

        controller.request.with_ocr_tool(
            options={
                "file_id": "example-file-id",
            },
        )
        updated_request_dump = controller.request.dump()

        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 1, "There should be one tool in the request."

        assert updated_request_dump["tools"][0]["type"] == str(ToolType.OCR), "The tool type should be 'ocr'."
        assert updated_request_dump["tools"][0][str(ToolType.OCR)]["file_id"] == "example-file-id", (
            "The file ID in the OCR tool should match the provided file ID."
        )

        response = await controller.request.send()
        assert "HTTP/1.1 200 OK" in caplog.text, "The response should indicate a successful request."


@pytest.mark.asyncio
async def test_using_multiple_tools(initialized_controller, caplog) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert "tools" not in current_request_dump, "The initial request should not contain any tools."

        controller.request.with_search_engine_tool(
            options={
                "search_context_size": "low",
            },
        )

        controller.request.with_rag_tool(
            options={
                "collection_uuid": "example-collection-uuid",
            },
        )

        updated_request_dump = controller.request.dump()

        assert "tools" in updated_request_dump, "The request should now contain tools."
        assert len(updated_request_dump["tools"]) == 2, (
            "There should be two tools in the request: one for web search and one for RAG."
        )
        assert updated_request_dump["tools"][0]["type"] == str(ToolType.WEB_SEARCH), (
            "The first tool should be a web search tool."
        )
        assert updated_request_dump["tools"][1]["type"] == str(ToolType.RAG), "The second tool should be a RAG tool."

        response = await controller.request.send()
        assert "HTTP/1.1 200 OK" in caplog.text, "The response should indicate a successful request."


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

        input_options = {
            "type": "enabled",
            "budget_tokens": 500,
        }
        controller.request.with_thinking(input_options)
        updated_request_dump = controller.request.dump()
        assert "thinking" in updated_request_dump, "The request should now have thinking mode enabled."
        assert "budget_tokens" in updated_request_dump["thinking"], (
            "The request should have budget_tokens set in the thinking mode."
        )
        assert updated_request_dump["thinking"]["type"] == "enabled", "The type of thinking mode should be 'enabled'."

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
        assert updated_request_dump["tool_choice"] == "auto", (
            "The tool_choice should remain 'auto' after adding an OCR tool."
        )

        controller.request.with_tool_choice("none")
        updated_request_dump = controller.request.dump()
        assert updated_request_dump["tool_choice"] == "none", (
            "The request should now have tool_choice set to 'required'."
        )

        controller.request.with_tool_choice("name:example_tool")
        updated_request_dump = controller.request.dump()
        assert (
            updated_request_dump["tool_choice"]
            == ToolChoiceAsDictionary(type="function", function={"name": "example_tool"}).model_dump()
        )
