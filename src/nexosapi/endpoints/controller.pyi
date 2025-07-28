import dataclasses
import httpx
from nexosapi.common.exceptions import InvalidControllerEndpointError as InvalidControllerEndpointError
from nexosapi.common.imports import (
    get_available_request_models as get_available_request_models,
    get_available_response_models as get_available_response_models,
    get_data_model_if_available as get_data_model_if_available,
)
from nexosapi.config.setup import ServiceName as ServiceName
from nexosapi.domain.base import NullableBaseModel as NullableBaseModel
from nexosapi.domain.requests import NexosAPIRequest as NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse as NexosAPIResponse
from nexosapi.services.http import NexosAIAPIService as NexosAIAPIService
from typing import Any, ClassVar, TypeVar

EndpointRequestType = TypeVar("EndpointRequestType", bound=NexosAPIRequest)
EndpointResponseType = TypeVar("EndpointResponseType", bound=NexosAPIResponse)

@dataclasses.dataclass
class NexosAIEndpointController[EndpointRequestType, EndpointResponseType]:
    """
    Abstract base class for NexosAI endpoint controllers.
    This class defines the structure for endpoint controllers in the Nexos AI API.
    """

    VALID_ENDPOINT_REGEX: ClassVar[str] = ...
    endpoint: ClassVar[str | None] = dataclasses.field(init=False, default=None)
    request_model: EndpointRequestType = dataclasses.field(init=False)
    response_model: EndpointResponseType = dataclasses.field(init=False)
    class Operations:
        """
        Enum to define operations for the NexosAIEndpointController.
        This enum can be extended to include specific operations for different controllers.
        """

    operations: Operations
    @dataclasses.dataclass
    class _RequestManager:
        """
        RequestManager is responsible for preparing and sending requests to the API endpoints.
        It handles the request data preparation and manages the lifecycle of the request.
        It also provides a way to perform operations on the request data before sending it.
        This class is initialized with a controller instance and uses dependency injection
        to access the NexosAPIService for making HTTP requests.

        IT HAS TO BE NESTED INSIDE THE CONTROLLER CLASS SINCE THE COMPILED TYPE STUBS
        HAVE TO STATICALLY OVERWRITE THE METHODS OF THE REQUEST MANAGER FOR EACH CONTROLLER IMPLEMENTATION.
        """

        pending: EndpointRequestType | None = dataclasses.field(init=False, default=None)
        def __post_init__(self) -> None:
            """
            Post-initialization method to set the endpoint for the request manager.
            This method is called after the instance is created to ensure that the endpoint
            is set correctly based on the controller's endpoint.
            """
        @staticmethod
        def get_verb_from_endpoint(endpoint: str) -> str:
            """
            Extract the HTTP verb from the endpoint string.

            :param endpoint: The endpoint string in the format "verb: /path".
            :return: The HTTP verb (e.g., "GET", "POST").
            """
        @staticmethod
        def get_path_from_endpoint(endpoint: str) -> str:
            """
            Extract the path from the endpoint string.

            :param endpoint: The endpoint string in the format "verb: /path".
            :return: The path (e.g., "/path").
            """
        def prepare(self, data: dict[str, Any]) -> NexosAIEndpointController._RequestManager:
            """
            Prepare the request data by initializing the pending request.

            :param data: The data to be included in the request.
            :return: The current instance of the RequestManager for method chaining.
            """
        def dump(self) -> dict[str, Any]:
            """
            Show the current pending request data.

            :return: The pending request data or None if not set.
            """
        async def send(self) -> EndpointResponseType | NullableBaseModel:
            """
            Call the endpoint with the provided request data.

            :return: The response data from the endpoint.
            """
        def __getattr__(self, target: str) -> Any:
            """
            Redirect any getattr calls to the operations defined
            in the controller class, EXCEPT for the `prepare` and `send` methods.
            """

    REQUEST_MANAGER_CLASS: type
    request: REQUEST_MANAGER_CLASS
    @classmethod
    def validate_endpoint(cls, endpoint: str) -> None:
        """
        Validates the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.

        :param endpoint: The API endpoint to validate.
        """
    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None: ...
    def __post_init__(self) -> None:
        """
        Post-initialization method to validate the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.
        """
    def on_response(self, response: EndpointResponseType) -> EndpointResponseType:
        """
        Hook for processing the response before returning it.
        Can be overridden in subclasses to add custom response handling.

        :param response: The response object to process.
        :return: The processed response object.
        """
    def on_error(self, response: httpx.Response) -> EndpointResponseType:
        """
        Hook for handling errors that occur during the request.
        Can be overridden in subclasses to add custom error handling.

        :param response: The HTTP response object which contains the error.
        :return: A null response object or a custom error response.
        """
    def __init__(self, _api_service=...) -> None: ...
    def __replace__(self, *, _api_service=...) -> None: ...
