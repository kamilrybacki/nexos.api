import pytest

from nexosapi.api.endpoints.chat.completions import ChatCompletionsEndpointController
from nexosapi.domain.responses import ChatCompletionsResponse

TEST_MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"},
]
TEST_COMPLETIONS_REQUEST = {"model": "gpt-3.5-turbo", "messages": TEST_MESSAGES}


def test_setting_model_and_messages(initialized_controller) -> None:
    controller: ChatCompletionsEndpointController
    with initialized_controller(ChatCompletionsEndpointController) as controller:
        controller.request.prepare(TEST_COMPLETIONS_REQUEST)
        current_request_dump = controller.request.dump()
        assert current_request_dump["model"] == "gpt-3.5-turbo", "The initial model should be set to 'gpt-3.5-turbo'."

        controller.request.with_model("gemini-1.5-flash")
        updated_request_dump = controller.request.dump()
        assert updated_request_dump["model"] == "gemini-1.5-flash", "The model should be updated to 'gemini-1.5-flash'."


@pytest.mark.asyncio
@pytest.mark.order("last")
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
        assert isinstance(response, ChatCompletionsResponse), (
            "The response should be an instance of ChatCompletionsResponse."
        )

        response_data = response.model_dump()
        expected_fields = controller.response_model.null().model_dump()
        assert all(field in response_data for field in expected_fields), (
            f"The response should contain all expected fields: {expected_fields}."
        )
