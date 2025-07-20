from unittest.mock import AsyncMock

import pytest
from httpx import Response
from mypy.metastore import random_string

from nexosapi.common.exceptions import InvalidControllerEndpointError
from nexosapi.domain.requests import MockRequestModel
from nexosapi.domain.responses import MockResponseModel
from nexosapi.endpoints.controller import NexosAIEndpointController
from nexosapi.services.http import NexosAPIService


class MockEndpointController[MockRequestModel, MockResponseModel](NexosAIEndpointController):
    endpoint = "post:/mock_path"


def test_endpoint_with_invalid_format_raises_value_error():
    with pytest.raises(InvalidControllerEndpointError):

        class InvalidEndpointController(MockEndpointController):
            endpoint = "invalid_format"


def test_endpoint_with_valid_format_initializes_correctly():
    class ValidEndpointController(MockEndpointController): ...

    controller = ValidEndpointController()
    assert controller.endpoint == "post:/mock_path"


@pytest.mark.asyncio
async def test_send_with_valid_request_returns_successful_response():
    mock_service = AsyncMock(spec=NexosAPIService)
    mock_service.request.return_value = Response(status_code=200, json={"key": "value"})

    controller = MockEndpointController()
    controller.request.prepare({"key": "value"})
    response = await controller.request.send(controller.endpoint, api_service=mock_service)

    assert isinstance(response, MockResponseModel)


@pytest.mark.asyncio
async def test_send_with_invalid_request_returns_null_response():
    mock_service = AsyncMock(spec=NexosAPIService)
    mock_service.request.return_value = Response(status_code=500)

    controller = MockEndpointController()
    response = await controller.request.send(controller.endpoint, api_service=mock_service)

    assert isinstance(response, MockResponseModel)


class EndpointControllerWithCustomOperation(MockEndpointController):
    class Operations:
        @staticmethod
        def with_uppercase_value(request: MockRequestModel) -> MockRequestModel:
            request.value = request.value.upper()
            return request

        @staticmethod
        def with_switched_field_values(request: MockRequestModel) -> MockRequestModel:
            key = request.key
            value = request.value
            return MockRequestModel(key=value, value=key)

        @staticmethod
        def with_hardcoded_value(request: MockRequestModel, value: str) -> MockRequestModel:
            request.value = value
            return request


def test_controller_with_custom_operations() -> None:
    random_key = random_string()
    random_value = random_string()

    controller = EndpointControllerWithCustomOperation()
    assert controller.endpoint == "post:/mock_path"

    mock_response_data = {"key": random_key, "value": random_value}
    controller.request.prepare(mock_response_data)

    assert controller.request._pending == MockRequestModel(**mock_response_data)  # noqa: SLF001

    controller.request.with_uppercase_value()
    assert controller.request._pending.value == mock_response_data["value"].upper()  # noqa: SLF001

    latest_request_data = controller.request._pending.model_dump()  # noqa: SLF001
    controller.request.with_switched_field_values()
    assert controller.request._pending == MockRequestModel(  # noqa: SLF001
        key=latest_request_data["value"],
        value=latest_request_data["key"],
    )

    hardcoded_value = MockResponseModel.__doc__.lower()
    controller.request.with_hardcoded_value(hardcoded_value)
    assert controller.request._pending.value == hardcoded_value  # noqa: SLF001

    hardcoded_value = MockResponseModel.__doc__.upper()
    controller.request.with_hardcoded_value(value=hardcoded_value)
    assert controller.request._pending.value == hardcoded_value  # noqa: SLF001


def test_chaining_operations_in_controller() -> None:
    controller = EndpointControllerWithCustomOperation()
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
    assert controller.request._pending.key == hardcoded_value.upper()  # noqa: SLF001
    assert controller.request._pending.value == initial_data["value"].upper()  # noqa: SLF001
