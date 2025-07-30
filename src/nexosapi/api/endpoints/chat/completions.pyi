from __future__ import annotations
import typing
from nexosapi.api.controller import NexosAIAPIEndpointController as NexosAIAPIEndpointController
from nexosapi.domain.requests import ChatCompletionsRequest as ChatCompletionsRequest
from nexosapi.domain.responses import ChatCompletionsResponse as ChatCompletionsResponse

class ChatCompletionsEndpointController(NexosAIAPIEndpointController):
    endpoint: str
    response_model = ChatCompletionsResponse
    request_model = ChatCompletionsRequest

    class RequestManager(ChatCompletionsEndpointController._RequestManager):
        @staticmethod
        def with_model(model: str) -> ChatCompletionsRequest:
            """
            Sets the model to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param model: The model to be used for the chat completion.
            :return: The updated request object with the model set.
            """

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
