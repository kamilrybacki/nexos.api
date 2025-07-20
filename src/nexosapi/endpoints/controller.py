import abc
import dataclasses
import logging
import re
import typing
from typing import Any, ClassVar, TypeVar

import httpx
import pydantic
from dependency_injector.wiring import Provide, inject
from mypy.metastore import random_string

from nexosapi.common.exceptions import InvalidControllerEndpointError
from nexosapi.common.imports import (
    get_available_request_models,
    get_available_response_models,
    get_data_model_if_available,
)
from nexosapi.domain.base import NullableBaseModel
from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse
from nexosapi.services.http import NexosAPIService

EndpointRequestType = TypeVar("EndpointRequestType", bound=NexosAPIRequest)
EndpointResponseType = TypeVar("EndpointResponseType", bound=NexosAPIResponse)


@dataclasses.dataclass
class RequestManager:
    _controller: "NexosAIEndpointController" = dataclasses.field()
    _pending: EndpointRequestType | None = dataclasses.field(init=False, default=None)
    __salt: str = dataclasses.field(init=False, default=random_string())

    @staticmethod
    def _get_verb_from_endpoint(endpoint: str) -> str:
        """
        Extract the HTTP verb from the endpoint string.

        :param endpoint: The endpoint string in the format "verb: /path".
        :return: The HTTP verb (e.g., "GET", "POST").
        """
        return endpoint.split(":", 1)[0].strip().upper()

    @staticmethod
    def _get_path_from_endpoint(endpoint: str) -> str:
        """
        Extract the path from the endpoint string.

        :param endpoint: The endpoint string in the format "verb: /path".
        :return: The path (e.g., "/path").
        """
        return endpoint.split(":", 1)[1].strip()

    def prepare(self, data: dict[str, Any]) -> "RequestManager":
        """
        Prepare the request data by initializing the pending request.

        :param data: The data to be included in the request.
        """
        try:
            if not self._pending:
                self._pending = self._controller._request_model(**data)  # noqa: SLF001
        except pydantic.ValidationError as incorrect_data:
            logging.info(f"[API] Validation error in {self._controller.__class__.__name__}: {incorrect_data}")
            self._pending = None
        else:
            return self

    @inject
    async def send(
        self, endpoint: str, api_service: NexosAPIService = Provide["NexosAPIService"]
    ) -> EndpointRequestType | NullableBaseModel:
        """
        Call the endpoint with the provided request data.

        :param endpoint: The endpoint string in the format "verb:/path".
        :param api_service: The HTTP service used to make the request.
        :return: The response data from the endpoint.
        """
        if not self._pending:
            logging.info(f"[API] No pending request in {self._controller.__class__.__name__}")
            return self._controller._response_model.null()  # noqa: SLF001

        response: httpx.Response = await api_service.request(
            verb=self._get_verb_from_endpoint(endpoint),
            url=self._get_path_from_endpoint(endpoint),
            json=self._pending.model_dump(),
        )
        if response.is_error:
            self._controller.on_error(response)
            return self._controller._response_model.null()  # noqa: SLF001
        structured_response = self._controller._response_model(**response.json())  # noqa: SLF001
        structured_response._response = response  # noqa: SLF001
        return self._controller.on_response(structured_response)

    def __getattr__(self, target: str) -> Any:
        """
        Redirect any getattr calls to the operations defined
        in the controller class, EXCEPT for the `prepare` and `send` methods.
        """
        if target in ("prepare", "send"):
            if retrieved_method := getattr(self._controller, f"_{self.__salt}_{target}"):
                return retrieved_method
            raise AttributeError(f"[API] Method {target} not found.")

        if operation := getattr(self._controller.operations, target):

            def _wrapped_operation(*args: Any, **kwargs: Any) -> "RequestManager":
                operation_result = operation(self._pending, *args, **kwargs)
                self._pending = operation_result
                return self

            return _wrapped_operation
        raise AttributeError(f"[API] {self._controller.__class__.__name__} has no operation '{target}' defined.")


@dataclasses.dataclass
class NexosAIEndpointController(typing.Generic[EndpointRequestType, EndpointResponseType]):  # noqa: UP046
    """
    Abstract base class for NexosAI endpoint controllers.
    This class defines the structure for endpoint controllers in the Nexos AI API.
    """

    VALID_ENDPOINT_REGEX: ClassVar[str] = r"^(post|get|delete|patch):(\/[a-zA-Z0-9\/_-]+)$"

    endpoint: ClassVar[str | None] = dataclasses.field(init=False, default=None)
    _request_model: EndpointRequestType = dataclasses.field(init=False)
    _response_model: EndpointResponseType = dataclasses.field(init=False)

    class Operations:
        """
        Enum to define operations for the NexosAIEndpointController.
        This enum can be extended to include specific operations for different controllers.
        """

    operations: Operations = dataclasses.field(init=False)
    request: RequestManager = dataclasses.field(init=False)

    @classmethod
    def _validate_endpoint(cls, endpoint: str) -> None:
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
        cls._validate_endpoint(cls.endpoint)

    def __post_init__(self) -> None:
        """
        Post-initialization method to validate the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.
        """
        self.request = RequestManager(self)
        self.operations = self.Operations()
        nested_endpoint_base_class = self.__class__

        # Here, we dig down to the underlying endpoint base class with generic
        # for data models defined, to properly instantiate them for the controller
        while nested_endpoint_base_class.__base__ != NexosAIEndpointController:
            if nested_endpoint_base_class is None:
                nested_endpoint_base_class = self.__class__.__bases__[0]
            if len(nested_endpoint_base_class.__bases__) > 1:
                nested_endpoint_base_class = nested_endpoint_base_class.__bases__[0]
            else:
                nested_endpoint_base_class = nested_endpoint_base_class.__base__

        # Getting the data model types from generic
        data_models_generics = nested_endpoint_base_class.__type_params__

        request_model_name = data_models_generics[0].__name__
        response_model_name = data_models_generics[1].__name__

        self._request_model = get_data_model_if_available(request_model_name, get_available_request_models())
        self._response_model = get_data_model_if_available(response_model_name, get_available_response_models())

        logging.info(
            f"[API] Instantiated {self.__class__.__name__} with following data models: {request_model_name} => {response_model_name}"
        )

    def on_response(self, response: EndpointRequestType) -> EndpointResponseType:
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

        :param response: The HTTP response object containing the error.
        :return: A null response object or a custom error response.
        """
        logging.info(f"[API] Encountered an error during the request: {response.content}")
        return self._response_model.__class__.null()
