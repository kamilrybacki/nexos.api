from __future__ import annotations
import typing
import httpx
import typing
from nexosapi.api.controller import NexosAIAPIEndpointController
from nexosapi.config.settings.services import NexosAIAPIConfiguration as NexosAIAPIConfiguration
from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse
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

class MockEndpointController(NexosAIAPIEndpointController):
    endpoint: typing.ClassVar[str]
    request_model = MockRequestModel
    response_model = MockResponseModel

class EndpointControllerWithCustomOperations(MockEndpointController):
    class RequestManager(EndpointControllerWithCustomOperations._RequestManager):
        @staticmethod
        def with_uppercase_value() -> MockRequestModel:
            """Converts the value field of the request to uppercase.

            :return: The modified request model with the value field in uppercase."""

        @staticmethod
        def with_switched_field_values() -> MockRequestModel:
            """Switches the values of the key and value fields in the request model.

            :return: The modified request model with key and value fields switched."""

        @staticmethod
        def with_hardcoded_value(value: str) -> MockRequestModel:
            """Sets the value field of the request to a hardcoded value.

            :param value: The hardcoded value to set in the request model.
            :return: The modified request model with the value field set to the hardcoded value."""

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

        def send(self) -> typing.Any:
            """
            Call the endpoint with the provided request data.

            :return: The response data from the endpoint."""

    _RequestManager = RequestManager
    request = RequestManager()
