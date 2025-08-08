from __future__ import annotations

import abc
import dataclasses
import json
import logging
import re
import typing

import httpx  # noqa: TC002
import pydantic
from dependency_injector.wiring import Provide
from mypy.metastore import random_string

from nexosapi.common.exceptions import InvalidControllerEndpointError
from nexosapi.config.setup import ServiceName
from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse
from nexosapi.services.http import NexosAIAPIService

EndpointRequestType = typing.TypeVar("EndpointRequestType", bound=NexosAPIRequest)
EndpointResponseType = typing.TypeVar("EndpointResponseType", bound=NexosAPIResponse)


@dataclasses.dataclass
class NexosAIAPIEndpointController[EndpointRequestType, EndpointResponseType]:
    """
    Abstract base class for NexosAI endpoint controllers.
    This class defines the structure for endpoint controllers in the Nexos AI API.
    """

    endpoint: typing.ClassVar[str | None] = dataclasses.field(init=False, default=None)
    request_model: EndpointRequestType = dataclasses.field(init=False)
    response_model: EndpointResponseType = dataclasses.field(init=False)

    VALID_ENDPOINT_REGEX: typing.ClassVar[str] = r"^(post|get|delete|patch):(\/[a-zA-Z0-9\/_-]+)$"
    api_service: NexosAIAPIService = Provide[ServiceName.NEXOSAI_API_HTTP_CLIENT]

    class Operations:
        """
        Enum to define operations for the NexosAIEndpointController.
        This enum can be extended to include specific operations for different controllers.
        """

    operations: Operations = dataclasses.field(init=False)

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

        controller: NexosAIAPIEndpointController = dataclasses.field()
        pending: dict[str, typing.Any] | None = dataclasses.field(init=False, default=None)
        _last_response: EndpointResponseType | None = dataclasses.field(init=False, default=None)
        _last_request: dict[str, typing.Any] | None = dataclasses.field(init=False, default=None)
        __salt: str = dataclasses.field(init=False, default=random_string())

        def __post_init__(self) -> None:
            """
            Post-initialization method to set the endpoint for the request manager.
            This method is called after the instance is created to ensure that the endpoint
            is set correctly based on the controller's endpoint.
            """
            self._endpoint = self.controller.__class__.endpoint
            setattr(self.controller, f"_{self.__salt}_prepare", self.prepare)
            setattr(self.controller, f"_{self.__salt}_send", self.send)

        @staticmethod
        def get_verb_from_endpoint(endpoint: str) -> str:
            """
            Extract the HTTP verb from the endpoint string.

            :param endpoint: The endpoint string in the format "verb: /path".
            :return: The HTTP verb (e.g., "GET", "POST").
            """
            return endpoint.split(":", 1)[0].strip().upper()

        @staticmethod
        def get_path_from_endpoint(endpoint: str) -> str:
            """
            Extract the path from the endpoint string.

            :param endpoint: The endpoint string in the format "verb: /path".
            :return: The path (e.g., "/path").
            """
            return endpoint.split(":", 1)[1].strip()

        def prepare(
            self, data: typing.Annotated[dict[str, typing.Any], "model:EndpointRequestType"]
        ) -> NexosAIAPIEndpointController._RequestManager:  # type: ignore
            """
            Prepare the request data by initializing the pending request.

            :param data: The data to be included in the request.
            :return: The current instance of the RequestManager for method chaining.
            """
            try:
                if not self.pending:
                    validated_data = self.controller.request_model(**data)
                    self.pending = validated_data.model_dump(exclude_none=True)
            except pydantic.ValidationError as incorrect_data:
                logging.info(f"[SDK] Validation error in {self.controller.__class__.__name__}: {incorrect_data}")
                self._last_request = self.pending
                self.pending = None
            else:
                return self

        def dump(self) -> typing.Annotated[dict[str, typing.Any], "model:EndpointRequestType"]:
            """
            Show the current pending request data.

            :return: The pending request data or None if not set.
            """
            return (
                json.loads(
                    json.dumps(self.pending), parse_int=lambda x: x, parse_constant=lambda x: x, parse_float=lambda x: x
                )
                if self.pending
                else {}
            )

        async def send(self) -> typing.Annotated[dict[str, typing.Any], "model:EndpointResponseType"]:
            """
            Call the endpoint with the provided request data.

            :return: The response data from the endpoint.
            """
            logging.debug(f"[SDK] Sending request to {self.endpoint} with data: {self.pending}")
            verb = self.get_verb_from_endpoint(self.endpoint)
            if verb not in ("POST", "PUT", "PATCH"):
                logging.error(f"[SDK] Invalid verb requested: {verb}")
                return self.controller.response_model.null()  # type: ignore

            response: httpx.Response = await self.controller.api_service.request(
                verb=verb,
                url=self.get_path_from_endpoint(self.endpoint),
                **{"json": json.loads(json.dumps(self.pending))} if verb in ("POST", "PUT", "PATCH") else {},
            )
            if response.is_error:
                logging.error(f"[SDK] Error: {response.content.decode(encoding='utf-8')}")
                await self.controller.on_error(response)
                return self.controller.response_model.null().model_dump(exclude_none=True)

            self._last_response = response.json()
            structured_response = self.controller.response_model(**self._last_response)
            structured_response._response = response
            self._last_request = self.pending
            self.pending = None
            return (await self.controller.on_response(structured_response)).model_dump(exclude_none=True)

        def reload_last(self) -> NexosAIAPIEndpointController._RequestManager:
            """
            Reload the last request to reuse it for the next operation.

            :return: The current instance of the RequestManager for method chaining.
            """
            if self._last_request is not None:
                self.pending = self._last_request
            return self

        def __getattr__(self, target: str) -> typing.Any:
            """
            Redirect any getattr calls to the operations defined
            in the controller class, EXCEPT for the `prepare` and `send` methods.
            """
            if target in ("prepare", "send"):
                # If the target is one of the methods, return it from the salted controller attribute
                if retrieved_method := getattr(self.controller, f"_{self.__salt}_{target}"):
                    return retrieved_method
                raise AttributeError(f"[SDK] Method {target} not found.")
            if target in ("endpoint",):
                # If the target is one of the properties, return it directly
                return getattr(self.controller, target)
            if target == "controller":
                # If the target is 'controller', return the controller instance
                return self.controller
            if target == ("pending", "_last_response", "_last_request", "reload_last"):
                # If the target is 'pending' or '_last_response', return the respective attribute
                return getattr(self, target)

            if operation := getattr(self.controller.operations, target):

                def _wrapped_operation(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
                    pending_data = (
                        self.controller.request_model(**self.pending)
                        if self.pending
                        else self.controller.request_model.null()
                    )
                    operation_result = operation(pending_data, *args, **kwargs)
                    self.pending = operation_result.model_dump(exclude_none=True)
                    return self

                return _wrapped_operation
            raise AttributeError(f"[SDK] {self.controller.__name__} has no operation '{target}' defined.")

    REQUEST_MANAGER_CLASS: type = dataclasses.field(init=False, default=_RequestManager)
    request: REQUEST_MANAGER_CLASS = dataclasses.field(init=False)  # type: ignore

    @classmethod
    def validate_endpoint(cls, endpoint: str) -> None:
        """
        Validates the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.

        :param endpoint: The API endpoint to validate.
        """
        verbs = ("get:", "post:", "put:", "delete:", "patch:")
        if not isinstance(cls.endpoint, str) or not endpoint.startswith(verbs):
            raise InvalidControllerEndpointError(
                f"Invalid endpoint format: {endpoint}. Must start with one of {verbs}."
            )
        if not cls.endpoint or not isinstance(cls.endpoint, str):
            raise InvalidControllerEndpointError(f"Endpoint must be a non-empty string for {cls.__class__.__name__}.")
        if not re.match(cls.VALID_ENDPOINT_REGEX, cls.endpoint):
            raise InvalidControllerEndpointError(
                f"Invalid endpoint format for {cls.__class__.__name__}: {cls.endpoint}. Expected format: 'verb:/path'."
            )

    @classmethod
    def __init_subclass__(cls, **kwargs: typing.Any) -> None:
        if abc.ABC in cls.__bases__:
            # If the class is defined as an abstract base class
            # then omit the validation of the endpoint on a subclassing
            # level because the class is not yet finally defined
            return
        if cls.request_model is None or cls.response_model is None:
            raise ValueError(
                f"Request and response models must be defined for {cls.__name__}. Please set 'request_model' and 'response_model' class variables."
            )
        if cls.endpoint is None:
            raise ValueError(f"Endpoint must be defined for {cls.__name__}. Please set the 'endpoint' class variable.")
        cls.validate_endpoint(cls.endpoint)

    def __post_init__(self) -> None:
        """
        Post-initialization method to validate the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.
        """
        self.request = self.REQUEST_MANAGER_CLASS(self)
        self.operations = self.Operations()

        logging.debug(
            f"[SDK] Instantiated {self.__class__.__name__} with following data models: {self.request_model.__name__} => {self.response_model.__name__}"
        )

    # noinspection PyMethodMayBeStatic
    async def on_response(self, response: EndpointResponseType) -> EndpointResponseType:
        """
        Hook for processing the response before returning it.
        Can be overridden in subclasses to add custom response handling.

        :param response: The response object to process.
        :return: The processed response object.
        """
        return response

    async def on_error(self, response: httpx.Response) -> EndpointResponseType:
        """
        Hook for handling errors that occur during the request.
        Can be overridden in subclasses to add custom error handling.

        :param response: The HTTP response object which contains the error.
        :return: A null response object or a custom error response.
        """
        logging.error(f"[SDK] Encountered an error during the request: {response.status_code} - {response.text}")
        logging.warning("[SDK] Returning null response due to error.")
        return self.response_model.null()
