from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse
from nexosapi.endpoints.controller import NexosAIEndpointController


class MockRequestModel(NexosAPIRequest):
    """For testing purposes."""

    key: str
    value: str


class MockResponseModel(NexosAPIResponse):
    """For testing purposes."""

    @classmethod
    def null(cls) -> NexosAPIResponse:
        return cls()


class MockEndpointController[MockRequestModel, MockResponseModel](NexosAIEndpointController):
    endpoint = "post:/mock_path"


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
