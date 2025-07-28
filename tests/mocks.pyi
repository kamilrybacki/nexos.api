from __future__ import annotations

import httpx
import typing
from nexosapi.config.settings.services import NexosAIAPIConfiguration as NexosAIAPIConfiguration
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

    base_url: str

    def initialize(self, config: NexosAIAPIConfiguration) -> None: ...
    async def request(
        self, verb: str, url: str, override_base: bool = False, **kwargs: typing.Any
    ) -> httpx.Response: ...

MOCK_ENDPOINT_PATH: str

class MockEndpointController[MockRequestModel, MockResponseModel](NexosAIEndpointController):
    endpoint: typing.ClassVar[str]

class EndpointControllerWithCustomOperations(MockEndpointController):
    class RequestManager(EndpointControllerWithCustomOperations._RequestManager):
        @staticmethod
        def with_uppercase_value(request: MockRequestModel) -> MockRequestModel:
            """
            Converts the value field of the request to uppercase.

            :param request: The request model to modify.
            :return: The modified request model with the value field in uppercase.
            """

        @staticmethod
        def with_switched_field_values(request: MockRequestModel) -> MockRequestModel:
            """
            Switches the values of the key and value fields in the request model.

            :param request: The request model to modify.
            :return: The modified request model with key and value fields switched.
            """

        @staticmethod
        def with_hardcoded_value(request: MockRequestModel, value: str) -> MockRequestModel:
            """
            Sets the value field of the request to a hardcoded value.

            :param request: The request model to modify.
            :param value: The hardcoded value to set in the request model.
            :return: The modified request model with the value field set to the hardcoded value.
            """

        def get_verb_from_endpoint(self, endpoint: str) -> str:
            """
            Extract the HTTP verb from the endpoint string.

            :param endpoint: The endpoint string in the format "verb: /path".
            :return: The HTTP verb (e.g., "GET", "POST")."""

        def get_path_from_endpoint(self, endpoint: str) -> str:
            """
            Extract the path from the endpoint string.

            :param endpoint: The endpoint string in the format "verb: /path".
            :return: The path (e.g., "/path")."""

        def prepare(self, data: dict) -> "RequestManager":
            """
            Prepare the request data by initializing the pending request.

            :param data: The data to be included in the request.
            :return: The current instance of the RequestManager for method chaining."""

        def dump(self) -> dict[str, typing.Any]:
            """
            Show the current pending request data.

            :return: The pending request data or None if not set."""

        def send(self) -> MockResponseModel:
            """
            Call the endpoint with the provided request data.

            :return: The response data from the endpoint."""

    _RequestManager = RequestManager
    request = RequestManager()
