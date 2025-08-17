from __future__ import annotations
import dataclasses
import httpx
import typing
from mypy.metastore import random_string
from nexosapi.common.exceptions import InvalidControllerEndpointError as InvalidControllerEndpointError
from nexosapi.config.setup import ServiceName as ServiceName
from nexosapi.domain.requests import NexosAPIRequest as NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse as NexosAPIResponse
from nexosapi.services.http import NexosAIAPIService as NexosAIAPIService

EndpointRequestType = typing.TypeVar("EndpointRequestType", bound=NexosAPIRequest)
EndpointResponseType = typing.TypeVar("EndpointResponseType", bound=NexosAPIResponse)
_EndpointRequestType = typing.TypeVar("_EndpointRequestType", bound=NexosAPIRequest)
_EndpointResponseType = typing.TypeVar("_EndpointResponseType", bound=NexosAPIResponse)
CONTROLLERS_REGISTRY: dict[str, NexosAIAPIEndpointController]

@dataclasses.dataclass
class NexosAIAPIEndpointController(typing.Generic[EndpointRequestType, EndpointResponseType]):
    """
    Abstract base class for NexosAI endpoint controllers.
    This class defines the structure for endpoint controllers in the Nexos AI API.
    """

    endpoint: typing.ClassVar[str | None] = dataclasses.field(init=False, default=None)
    request_model: EndpointRequestType = dataclasses.field(init=False)
    response_model: EndpointResponseType = dataclasses.field(init=False)
    VALID_ENDPOINT_REGEX: typing.ClassVar[str] = ...
    api_service: NexosAIAPIService = ...

    class Operations:
        """
        Enum to define operations for the NexosAIEndpointController.
        This enum can be extended to include specific operations for different controllers.
        """

    operations: Operations

    @dataclasses.dataclass
    class _RequestManager(typing.Generic[_EndpointRequestType, _EndpointResponseType]):
        """
        RequestManager is responsible for preparing and sending requests to the API endpoints.
        It handles the request data preparation and manages the lifecycle of the request.
        It also provides a way to perform operations on the request data before sending it.
        This class is initialized with a controller instance and uses dependency injection
        to access the NexosAPIService for making HTTP requests.

        IT HAS TO BE NESTED INSIDE THE CONTROLLER CLASS SINCE THE COMPILED TYPE STUBS
        HAVE TO STATICALLY OVERWRITE THE METHODS OF THE REQUEST MANAGER FOR EACH CONTROLLER IMPLEMENTATION.
        """

        controller: NexosAIAPIEndpointController = dataclasses.field(init=False)
        pending: _EndpointRequestType | None = dataclasses.field(init=False, default=None)
        _last_response: _EndpointResponseType | None = dataclasses.field(init=False, default=None)
        _last_request: _EndpointRequestType | None = dataclasses.field(init=False, default=None)
        __salt: str = dataclasses.field(init=False, default=random_string())
        _endpoint = ...

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

        def prepare(
            self, data: _EndpointRequestType | dict[str, typing.Any]
        ) -> NexosAIAPIEndpointController._RequestManager:
            """
            Prepare the request data by initializing the pending request.

            :param data: The data to be included in the request.
            :return: The current instance of the RequestManager for method chaining.
            """

        def dump(self) -> dict[str, typing.Any]:
            """
            Show the current pending request data.

            :return: The pending request data or None if not set.
            """

        async def send(self) -> _EndpointResponseType:
            """
            Call the endpoint with the provided request data.

            :return: The response data from the endpoint.
            """

        def reload_last(self) -> NexosAIAPIEndpointController._RequestManager:
            """
            Reload the last request to reuse it for the next operation.

            :return: The current instance of the RequestManager for method chaining.
            """

        def __getattr__(self, target: str) -> typing.Any:
            """
            Redirect any getattr calls to the operations defined
            in the controller class, EXCEPT for the `prepare` and `send` methods.
            """

    request: _RequestManager

    @classmethod
    def validate_endpoint(cls, endpoint: str) -> None:
        """
        Validates the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.

        :param endpoint: The API endpoint to validate.
        """

    @classmethod
    def __init_subclass__(cls, **kwargs: typing.Any) -> None: ...
    def __post_init__(self) -> None:
        """
        Post-initialization method to validate the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.
        """

    async def on_response(self, response: EndpointResponseType) -> EndpointResponseType:
        """
        Hook for processing the response before returning it.
        Can be overridden in subclasses to add custom response handling.

        :param response: The response object to process.
        :return: The processed response object.
        """

    async def on_error(self, response: httpx.Response) -> EndpointResponseType:
        """
        Hook for handling errors that occur during the request.
        Can be overridden in subclasses to add custom error handling.

        :param response: The HTTP response object which contains the error.
        :return: A null response object or a custom error response.
        """

    def __init__(self, api_service=...) -> None: ...
    def __replace__(self, *, api_service=...) -> None: ...
