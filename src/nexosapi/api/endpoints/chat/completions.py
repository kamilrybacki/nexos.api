from nexosapi.api.controller import NexosAIAPIEndpointController
from nexosapi.domain.requests import ChatCompletionsRequest
from nexosapi.domain.responses import ChatCompletionsResponse


class ChatCompletionsEndpointController(NexosAIAPIEndpointController):
    endpoint = "post:/chat/completions"
    response_model = ChatCompletionsResponse
    request_model = ChatCompletionsRequest

    class Operations:
        @staticmethod
        def with_model(request: ChatCompletionsRequest, model: str) -> ChatCompletionsRequest:
            """
            Sets the model to be used for the chat completion.

            :param request: The request object containing the chat completion parameters.
            :param model: The model to be used for the chat completion.
            :return: The updated request object with the model set.
            """
            request.model = model
            return request
