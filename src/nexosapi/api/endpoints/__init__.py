import dataclasses
import logging
import os
from typing import ClassVar

from nexosapi.api.endpoints.chat.completions import ChatCompletionsEndpointController
from nexosapi.config.setup import wire_sdk_dependencies

if os.environ.get("NEXOSAI_INIT__LOAD_DOTENV", "false").lower() == "true":
    # Load environment variables from a .env file if NEXOSAPI_LOAD_DOTENV is set to true
    # This is useful for local development or testing environments
    import dotenv

    dotenv.load_dotenv(
        os.environ.get("NEXOSAI_INIT__DOTENV_PATH", ".env"),
        override=True,
        verbose=True,
    )


if os.environ.get("NEXOSAI_INIT__DISABLE_AUTOWIRING", "false").lower() == "false":
    # Automatically wire dependencies for the SDK
    # This is useful for ensuring that all necessary parts are initialized
    # when the SDK is imported, without requiring manual setup in each module.
    wire_sdk_dependencies()
    logging.info("[SDK] Dependencies automatically wired.")


@dataclasses.dataclass(frozen=True)
class ChatEndpoints:
    """
    Main interface for accessing specific endpoint controllers e.g. chat completions or image generation.

    :ivar completions: Controller for handling chat completions.
    """

    completions: ClassVar[ChatCompletionsEndpointController] = ChatCompletionsEndpointController()


chat: ChatEndpoints = ChatEndpoints()
