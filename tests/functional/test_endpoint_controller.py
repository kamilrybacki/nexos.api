from unittest.mock import Mock

import pytest
from httpx import Response

from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse
from nexosapi.endpoints.base import NexosAIEndpointController
from nexosapi.services.http import NexosAPIService


class MockResponseModel(NexosAPIResponse):
    key: str


class MockEndpointController(NexosAIEndpointController):
    endpoint = "post:/mock_path"
    response_model = MockResponseModel
    request_model = NexosAPIRequest


@pytest.mark.chosen
def test_endpoint_with_invalid_format_raises_error():
    with pytest.raises(ValueError, match="Invalid endpoint format"):

        class InvalidEndpointController(NexosAIEndpointController):
            endpoint = "invalid_format"


@pytest.mark.chosen
def test_endpoint_with_valid_format_initializes_correctly():
    class ValidEndpointController(NexosAIEndpointController):
        endpoint = "post:/valid_path"
        response_model = MockResponseModel
        request_model = NexosAPIRequest

    controller = ValidEndpointController()
    assert controller.endpoint == "post:/valid_path"


@pytest.mark.chosen
def test_call_with_successful_response_returns_processed_data():
    mock_service = Mock(spec=NexosAPIService)
    mock_service.request = Mock(return_value=Response(status_code=200, json={"key": "value"}))

    controller = MockEndpointController()
    response = controller.call(request={"key": "value"}, api_service=mock_service)

    assert response.model_dump() == MockResponseModel(key="value").model_dump()
