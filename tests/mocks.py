import json
import logging
import typing

import httpx

from nexosapi.config.settings.services import NexosAIAPIConfiguration
from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse
from nexosapi.endpoints.controller import NexosAIEndpointController
from nexosapi.services.http import NexosAIAPIService


class MockRequestModel(NexosAPIRequest):
    """For testing purposes."""

    key: str
    value: str


class MockResponseModel(NexosAPIResponse):
    """For testing purposes."""

    key: str
    value: str


class MockAIAPIService(NexosAIAPIService):
    """Mock service for testing purposes."""

    def initialize(self, config: NexosAIAPIConfiguration) -> None:  # noqa: ARG002
        self.base_url = "http://mockapi.test"

    async def request(self, verb: str, url: str, override_base: bool = False, **kwargs: typing.Any) -> httpx.Response:  # noqa: ARG002
        if verb == "POST":
            # Simulate a successful response for the mock endpoint
            if post_data := kwargs.get("json", kwargs.get("data")):
                logging.info("[API] Mock POST request data: %s", post_data)
                if isinstance(post_data, str):
                    try:
                        post_data = json.loads(post_data)
                    except json.JSONDecodeError:
                        logging.exception("[API] Failed to decode JSON from POST data: %s", post_data)
                        return httpx.Response(status_code=400, json={"error": "Invalid JSON format"})

                return httpx.Response(
                    status_code=200, json={"key": post_data.get("key", ""), "value": post_data.get("value", "")}
                )
            return httpx.Response(status_code=400, json={"error": "Invalid request data"})
        if verb == "GET":
            # Simulate a successful GET request
            return httpx.Response(status_code=200, json={"message": "GET request successful"})
        return httpx.Response(status_code=404, json={"error": "Not Found"})


MOCK_ENDPOINT_PATH = "post:/mock_path"


class MockEndpointController[MockRequestModel, MockResponseModel](NexosAIEndpointController):
    endpoint: typing.ClassVar[str] = MOCK_ENDPOINT_PATH


class EndpointControllerWithCustomOperations(MockEndpointController):
    class Operations:
        @staticmethod
        def with_uppercase_value(request: MockRequestModel) -> MockRequestModel:
            """
            Converts the value field of the request to uppercase.

            :param request: The request model to modify.
            :return: The modified request model with the value field in uppercase.
            """
            request.value = request.value.upper()
            return request

        @staticmethod
        def with_switched_field_values(request: MockRequestModel) -> MockRequestModel:
            """
            Switches the values of the key and value fields in the request model.

            :param request: The request model to modify.
            :return: The modified request model with key and value fields switched.
            """
            key = request.key
            value = request.value
            return MockRequestModel(key=value, value=key)

        @staticmethod
        def with_hardcoded_value(request: MockRequestModel, value: str) -> MockRequestModel:
            """
            Sets the value field of the request to a hardcoded value.

            :param request: The request model to modify.
            :param value: The hardcoded value to set in the request model.
            :return: The modified request model with the value field set to the hardcoded value.
            """
            request.value = value
            return request
