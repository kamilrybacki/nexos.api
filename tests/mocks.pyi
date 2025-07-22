from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse
from nexosapi.endpoints.controller import NexosAIEndpointController

class MockRequestModel(NexosAPIRequest):
    key: str
    value: str

class MockResponseModel(NexosAPIResponse):
    @classmethod
    def null(cls) -> NexosAPIResponse: ...

class MockEndpointController[MockRequestModel, MockResponseModel](NexosAIEndpointController):
    endpoint: str

class EndpointControllerWithCustomOperations(MockEndpointController):
    class RequestMaker(EndpointControllerWithCustomOperations._RequestMaker):
        @staticmethod
        def with_uppercase_value(request: MockRequestModel) -> MockRequestModel: ...
        @staticmethod
        def with_switched_field_values(request: MockRequestModel) -> MockRequestModel: ...
        @staticmethod
        def with_hardcoded_value(request: MockRequestModel, value: str) -> MockRequestModel: ...

    REQUEST_MAKER_CLASS = RequestMaker
