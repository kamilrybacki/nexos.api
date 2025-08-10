import pytest
from mypy.metastore import random_string

from nexosapi.common.exceptions import InvalidControllerEndpointError
from nexosapi.config.setup import wire_sdk_dependencies
from tests.mocks import (
    MOCK_ENDPOINT_PATH,
    EndpointControllerWithCustomOperations,
    MockAIAPIService,
    MockEndpointController,
    MockResponseModel,
)
from tests.services import MOCK_API_KEY, mock_api_injected_into_services_wiring


def test_endpoint_with_invalid_format_raises_value_error():
    with pytest.raises(InvalidControllerEndpointError):

        class InvalidEndpointController(MockEndpointController):
            endpoint = "invalid_format"


def test_endpoint_with_valid_format_initializes_correctly():
    class ValidEndpointController(MockEndpointController): ...

    controller = ValidEndpointController()
    assert controller.endpoint == MOCK_ENDPOINT_PATH


@pytest.mark.asyncio
async def test_send_with_valid_request_returns_successful_response(service_environment, caplog):
    with (
        mock_api_injected_into_services_wiring(MockAIAPIService),
        service_environment(
            {"NEXOSAI__BASE_URL": "http://localhost:5000", "NEXOSAI__VERSION": "v1", "NEXOSAI__API_KEY": MOCK_API_KEY}
        ),
    ):
        wire_sdk_dependencies()
        controller = MockEndpointController()
        controller.request.prepare(
            {
                "key": "test_key",
                "value": "test_value",
            }
        )
        response = (await controller.request.send()).model_dump()
        assert "Mock POST request data" in caplog.text
        assert response["key"] == "test_key"
        assert response["value"] == "test_value"


@pytest.mark.asyncio
async def test_send_with_invalid_request_returns_null_response(service_environment, caplog):
    with (
        mock_api_injected_into_services_wiring(MockAIAPIService),
        service_environment(
            {"NEXOSAI__BASE_URL": "http://localhost:5000", "NEXOSAI__VERSION": "v1", "NEXOSAI__API_KEY": MOCK_API_KEY}
        ),
    ):
        wire_sdk_dependencies()
        controller = MockEndpointController()
        response = (await controller.request.send()).model_dump()
        assert response == MockResponseModel.null().model_dump()
        assert "No pending request" in caplog.text


def test_controller_with_custom_operations() -> None:
    random_key = random_string()
    random_value = random_string()

    controller = EndpointControllerWithCustomOperations()
    assert controller.endpoint == MOCK_ENDPOINT_PATH

    mock_response_data = {"key": random_key, "value": random_value}
    controller.request.prepare(mock_response_data)

    assert controller.request.pending.model_dump() == mock_response_data

    controller.request.with_uppercase_value()
    assert controller.request.pending.value == mock_response_data["value"].upper()

    latest_request_data = controller.request.pending
    controller.request.with_switched_field_values()
    assert controller.request.pending.model_dump() == {
        "key": latest_request_data["value"],
        "value": latest_request_data["key"],
    }

    hardcoded_value = MockResponseModel.__doc__.lower()
    controller.request.with_hardcoded_value(hardcoded_value)
    assert controller.request.pending.value == hardcoded_value

    hardcoded_value = MockResponseModel.__doc__.upper()
    controller.request.with_hardcoded_value(value=hardcoded_value)
    assert controller.request.pending.value == hardcoded_value


def test_chaining_operations_in_controller() -> None:
    controller = EndpointControllerWithCustomOperations()
    random_key = random_string()
    random_value = random_string()
    hardcoded_value = MockResponseModel.__doc__.lower()

    initial_data: dict[str, str] = {"key": random_key, "value": random_value}
    (
        controller.request.prepare(initial_data)
        .with_uppercase_value()
        .with_switched_field_values()
        .with_hardcoded_value(hardcoded_value)
        .with_uppercase_value()
        .with_switched_field_values()
    )
    assert controller.request.pending.key == hardcoded_value.upper()
    assert controller.request.pending.value == initial_data["value"].upper()


@pytest.mark.asyncio
async def test_using_controller_to_send_request(
    service_environment,
) -> None:
    with service_environment(
        {"NEXOSAI__BASE_URL": "http://localhost:5000", "NEXOSAI__VERSION": "v1", "NEXOSAI__API_KEY": MOCK_API_KEY}
    ):
        random_key = random_string()
        random_value = random_string()
        initial_data = {"key": random_key, "value": random_value}
        with mock_api_injected_into_services_wiring(MockAIAPIService):
            wire_sdk_dependencies()
            controller = EndpointControllerWithCustomOperations()

            controller.request.prepare(initial_data)
            controller.request.with_uppercase_value()

            response: MockResponseModel = await controller.request.send()

            # Check the contents of the response
            assert response.key == initial_data["key"]
            assert response.value == initial_data["value"].upper()

            # Check the request state after sending
            assert controller.request.pending is None
            assert controller.request._last_response == response
