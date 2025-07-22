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
