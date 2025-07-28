from __future__ import annotations

import abc
import dataclasses
import json
import logging
import re
from typing import Any, ClassVar, TypeVar

import httpx  # noqa: TC002
import pydantic
from dependency_injector.wiring import Provide
from mypy.metastore import random_string

from nexosapi.common.exceptions import InvalidControllerEndpointError
from nexosapi.common.imports import (
    get_available_request_models,
    get_available_response_models,
    get_data_model_if_available,
)
from nexosapi.config.setup import ServiceName
from nexosapi.domain.base import NullableBaseModel
from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse
from nexosapi.services.http import NexosAIAPIService

EndpointRequestType = TypeVar("EndpointRequestType", bound=NexosAPIRequest)
EndpointResponseType = TypeVar("EndpointResponseType", bound=NexosAPIResponse)


@dataclasses.dataclass
class NexosAIEndpointController[EndpointRequestType, EndpointResponseType]:
    """
    Abstract base class for NexosAI endpoint controllers.
    This class defines the structure for endpoint controllers in the Nexos AI API.
    """

    VALID_ENDPOINT_REGEX: ClassVar[str] = r"^(post|get|delete|patch):(\/[a-zA-Z0-9\/_-]+)$"

    _api_service: NexosAIAPIService = Provide[ServiceName.NEXOSAI_API_HTTP_CLIENT]
    endpoint: ClassVar[str | None] = dataclasses.field(init=False, default=None)
    request_model: EndpointRequestType = dataclasses.field(init=False)
    response_model: EndpointResponseType = dataclasses.field(init=False)

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

        _controller: NexosAIEndpointController = dataclasses.field()
        pending: EndpointRequestType | None = dataclasses.field(init=False, default=None)
        _last_response: EndpointResponseType | None = dataclasses.field(init=False, default=None)
        __salt: str = dataclasses.field(init=False, default=random_string())

        def __post_init__(self) -> None:
            """
            Post-initialization method to set the endpoint for the request manager.
            This method is called after the instance is created to ensure that the endpoint
            is set correctly based on the controller's endpoint.
            """
            self._endpoint = self._controller.__class__.endpoint
            setattr(self._controller, f"_{self.__salt}_prepare", self.prepare)
            setattr(self._controller, f"_{self.__salt}_send", self.send)

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

        def prepare(self, data: dict[str, Any]) -> NexosAIEndpointController._RequestManager:  # type: ignore
            """
            Prepare the request data by initializing the pending request.

            :param data: The data to be included in the request.
            :return: The current instance of the RequestManager for method chaining.
            """
            try:
                if not self.pending:
                    self.pending = self._controller.request_model(**data)
            except pydantic.ValidationError as incorrect_data:
                logging.info(f"[API] Validation error in {self._controller.__class__.__name__}: {incorrect_data}")
                self.pending = None
            else:
                return self

        def dump(self) -> dict[str, Any]:
            """
            Show the current pending request data.

            :return: The pending request data or None if not set.
            """
            return self.pending.model_dump() if self.pending else {}

        async def send(self) -> EndpointResponseType | NullableBaseModel:
            """
            Call the endpoint with the provided request data.

            :return: The response data from the endpoint.
            """
            verb = self.get_verb_from_endpoint(self.endpoint)
            if verb in ("POST", "PUT", "PATCH") and not isinstance(self.pending, self._controller.request_model):
                logging.info(
                    f"[API] Pending request is not of type {self._controller.request_model.__name__} in {self._controller.__class__.__name__}"
                )
                return self._controller.response_model.null()  # type: ignore

            response: httpx.Response = await self._controller._api_service.request(
                verb=verb,
                url=self.get_path_from_endpoint(self.endpoint),
                **{
                    "json": json.dumps(self.pending.model_dump())  # type: ignore
                }
                if verb in ("POST", "PUT", "PATCH")
                else {},
            )
            if response.is_error:
                self._controller.on_error(response)
                return self._controller.response_model.null()
            structured_response = self._controller.response_model(**response.json())
            structured_response._response = response
            self._last_response = structured_response
            self.pending = None
            return self._controller.on_response(structured_response)

        def __getattr__(self, target: str) -> Any:
            """
            Redirect any getattr calls to the operations defined
            in the controller class, EXCEPT for the `prepare` and `send` methods.
            """
            if target in ("prepare", "send"):
                # If the target is one of the methods, return it from the salted controller attribute
                if retrieved_method := getattr(self._controller, f"_{self.__salt}_{target}"):
                    return retrieved_method
                raise AttributeError(f"[API] Method {target} not found.")
            if target in ("endpoint",):
                # If the target is one of the properties, return it directly
                return getattr(self._controller, target)
            if target == "_controller":
                # If the target is 'controller', return the controller instance
                return self._controller
            if target == ("pending", "_last_response"):
                # If the target is 'pending' or '_last_response', return the respective attribute
                return getattr(self, target)

            if operation := getattr(self._controller.operations, target):

                def _wrapped_operation(*args: Any, **kwargs: Any) -> Any:
                    operation_result = operation(self.pending, *args, **kwargs)
                    self.pending = operation_result
                    return self

                return _wrapped_operation
            raise AttributeError(f"[API] {self._controller.__name__} has no operation '{target}' defined.")

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
    def __init_subclass__(cls, **kwargs: Any) -> None:
        if abc.ABC in cls.__bases__:
            # If the class is defined as an abstract base class
            # then omit the validation of the endpoint on a subclassing
            # level because the class is not yet finally defined
            return
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
        nested_endpoint_base_class = self.__class__

        # Here, we dig down to the underlying endpoint base class with generic
        # for data models defined, to properly instantiate them for the controller
        while nested_endpoint_base_class.__base__ != NexosAIEndpointController:
            if nested_endpoint_base_class is None:
                nested_endpoint_base_class = self.__class__.__bases__[0]  # type: ignore
            if len(nested_endpoint_base_class.__bases__) > 1:
                nested_endpoint_base_class = nested_endpoint_base_class.__bases__[0]
            else:
                nested_endpoint_base_class = nested_endpoint_base_class.__base__  # type: ignore

        # Getting the data model types from generic
        data_models_generics = nested_endpoint_base_class.__type_params__

        request_model_name = data_models_generics[0].__name__
        response_model_name = data_models_generics[1].__name__

        self.request_model = get_data_model_if_available(request_model_name, get_available_request_models())  # type: ignore
        self.response_model = get_data_model_if_available(response_model_name, get_available_response_models())  # type: ignore

        logging.info(
            f"[API] Instantiated {self.__class__.__name__} with following data models: {request_model_name} => {response_model_name}"
        )

    # noinspection PyMethodMayBeStatic
    def on_response(self, response: EndpointResponseType) -> EndpointResponseType:
        """
        Hook for processing the response before returning it.
        Can be overridden in subclasses to add custom response handling.

        :param response: The response object to process.
        :return: The processed response object.
        """
        return response

    def on_error(self, response: httpx.Response) -> EndpointResponseType:
        """
        Hook for handling errors that occur during the request.
        Can be overridden in subclasses to add custom error handling.

        :param response: The HTTP response object which contains the error.
        :return: A null response object or a custom error response.
        """
        logging.error(f"[API] Encountered an error during the request: {response.status_code} - {response.text}")
        logging.warning("[API] Returning null response due to error.")
        return self.response_model.null()
