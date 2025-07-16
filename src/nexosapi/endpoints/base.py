import dataclasses
import logging
import re
from typing import Any, ClassVar

import httpx
from dependency_injector.wiring import Provide, inject

from nexosapi.domain.requests import NexosAPIRequest
from nexosapi.domain.responses import NexosAPIResponse
from nexosapi.services.http import NexosAPIService


@dataclasses.dataclass
class NexosAIEndpointController:
    """
    Abstract base class for Nexos AI endpoint controllers.
    This class defines the structure for endpoint controllers in the Nexos AI API.
    """

    VALID_ENDPOINT_REGEX: ClassVar[str] = r"^(post|get|delete|patch):(\/[a-zA-Z0-9\/_-]+)$"
    endpoint: ClassVar[str | None] = dataclasses.field(init=False, default=None)
    response_model: ClassVar[type[NexosAPIResponse]] = dataclasses.field(init=False, default=None)
    request_model: ClassVar[type[NexosAPIRequest]] = dataclasses.field(init=False, default=None)

    @classmethod
    def _validate_endpoint(cls, endpoint: str) -> None:
        """
        Validates the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.

        :param endpoint: The API endpoint to validate.
        """
        verbs = ("get:", "post:", "put:", "delete:", "patch:")
        if not isinstance(endpoint, str) or not endpoint.startswith(verbs):
            raise ValueError(f"Invalid endpoint format: {endpoint}. Must start with one of {verbs}.")

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

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        if cls.endpoint is None:
            raise ValueError(f"Endpoint must be defined for {cls.__name__}. Please set the 'endpoint' class variable.")
        cls._validate_endpoint(cls.endpoint)
        if not issubclass(cls.response_model, NexosAPIResponse):
            raise TypeError(f"Response model must be a subclass of {NexosAPIResponse.__name__}.")

    def __post_init__(self) -> None:
        """
        Post-initialization method to validate the endpoint format.
        Raises ValueError if the endpoint does not match the expected format.
        """
        if not self.endpoint or not isinstance(self.endpoint, str):
            raise ValueError(f"Endpoint must be a non-empty string for {self.__class__.__name__}.")
        if not re.match(self.VALID_ENDPOINT_REGEX, self.endpoint):
            raise ValueError(
                f"Invalid endpoint format for {self.__class__.__name__}: {self.endpoint}. "
                "Expected format: 'verb:/path'."
            )

    def on_response(self, response: httpx.Response) -> NexosAPIResponse:
        """
        Handle an incoming request and return a response.

        :param response: The response data to be processed.
        :return: The response data.
        """
        return self.response_model(**response.json())

    def on_error(self, response: NexosAPIResponse) -> None:
        """
        Handle an error that occurs during request processing.

        :param response: The exception that occurred.
        :return: A response indicating the error.
        """
        logging.info(f"Error occurred while processing request for endpoint {self.endpoint}: {response}")

    @inject
    def call(
        self, request: NexosAPIRequest, api_service: NexosAPIService = Provide["NexosAPIService"]
    ) -> NexosAPIResponse:
        """
        Call the endpoint with the provided request data.

        :param request: The request data to be sent to the endpoint.
        :param api_service: The HTTP service used to make the request.
        :return: The response data from the endpoint.
        """
        response: httpx.Response = api_service.request(
            method=self._get_verb_from_endpoint(self.endpoint), url=self.endpoint, json=request
        )
        if response.is_error:
            self.on_error(response)
            return self.response_model.null()
        structured_response = self.on_response(response)
        structured_response._response = response  # noqa: SLF001
        return structured_response
