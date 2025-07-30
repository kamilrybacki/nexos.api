import asyncio
import dataclasses
import httpx
import typing
from collections.abc import Callable as Callable
from nexosapi.config.settings.defaults import (
    NEXOSAI_AUTH_HEADER_NAME as NEXOSAI_AUTH_HEADER_NAME,
    NEXOSAI_AUTH_HEADER_PREFIX as NEXOSAI_AUTH_HEADER_PREFIX,
)
from nexosapi.config.settings.services import NexosAIAPIConfiguration as NexosAIAPIConfiguration

@dataclasses.dataclass
class NexosAIAPIService:
    """
    Abstract class for asynchronous services.
    """

    base_url: str = dataclasses.field(init=False)
    loop: asyncio.AbstractEventLoop | None = dataclasses.field(default=None, init=False)
    client: Callable[[], httpx.AsyncClient] = dataclasses.field(init=False, repr=False)
    follow_redirects: bool = dataclasses.field(init=False, default=True)
    def __post_init__(self) -> None: ...
    async def request(self, verb: str, url: str, override_base: bool = False, **kwargs: typing.Any) -> httpx.Response:
        """
        Send an HTTP request using the configured client.

        :param verb: The HTTP method to use (e.g., 'GET', 'POST').
        :param url: The URL to which the request is sent. If `override_base` is True, it will not prepend the base URL.
        :param override_base: If True, the base URL will not be prepended to the provided URL.
        :return: The HTTP response.
        """
    def initialize(self, config: NexosAIAPIConfiguration) -> None: ...
    def construct_headers(self, config: NexosAIAPIConfiguration) -> dict[str, str]:
        """
        Construct headers for the HTTP request.

        :param config: The configuration for the API service.
        :return: A dictionary of headers.
        """
    def construct_auth(self, config: NexosAIAPIConfiguration) -> httpx.Auth | None:
        """
        Construct authentication for the HTTP request.

        :param config: The configuration for the API service.
        :return: A httpx.Auth object or None if no authentication is needed.
        """
    async def disconnect(self) -> None:
        """
        Disconnect the HTTP client.
        """
