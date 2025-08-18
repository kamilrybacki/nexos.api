import asyncio
import dataclasses
import logging
import typing
from collections.abc import Callable
from urllib.parse import urljoin

import httpx
import tenacity

from nexosapi.config.settings.defaults import NEXOSAI_AUTH_HEADER_NAME, NEXOSAI_AUTH_HEADER_PREFIX
from nexosapi.config.settings.services import NexosAIAPIConfiguration


@dataclasses.dataclass
class NexosAIAPIService:
    """
    Abstract class for asynchronous services.
    """

    base_url: str = dataclasses.field(init=False)
    loop: asyncio.AbstractEventLoop | None = dataclasses.field(default=None, init=False)
    client: Callable[[], httpx.AsyncClient] = dataclasses.field(init=False, repr=False)
    follow_redirects: bool = dataclasses.field(init=False, default=True)

    def __post_init__(self) -> None:
        with NexosAIAPIConfiguration.use() as initialized_config:
            self.initialize(initialized_config)

    async def request(self, verb: str, url: str, override_base: bool = False, **kwargs: typing.Any) -> httpx.Response:
        """
        Send an HTTP request using the configured client.

        :param verb: The HTTP method to use (e.g., 'GET', 'POST').
        :param url: The URL to which the request is sent. If `override_base` is True, it will not prepend the base URL.
        :param override_base: If True, the base URL will not be prepended to the provided URL.
        :return: The HTTP response.
        """
        full_url = url if override_base else f"{self.base_url}/{url.lstrip('/')}"
        logging.debug(f"[API] Requesting {verb} {full_url} with params: {kwargs.get('json', {})}")
        async with self.client() as spawned_client:
            return await spawned_client.request(
                method=verb, url=full_url, follow_redirects=self.follow_redirects, **kwargs
            )

    def initialize(self, config: NexosAIAPIConfiguration) -> None:
        self.follow_redirects = config.follow_redirects
        retry_strategy = tenacity.retry(
            stop=tenacity.stop_after_attempt(config.retries),
            wait=tenacity.wait_exponential(
                multiplier=config.exponential_backoff,
                min=config.minimum_wait,
                max=config.maximum_wait,
            ),
            reraise=config.reraise_exceptions,
            retry=tenacity.retry_if_exception_type(httpx.HTTPError),
        )
        self.base_url = urljoin(config.base_url, config.version)

        def __spawn_client() -> httpx.AsyncClient:
            """
            Create an instance of httpx.AsyncClient with the provided configuration.
            """
            return httpx.AsyncClient(
                base_url=self.base_url,
                timeout=httpx.Timeout(config.timeout),
                headers=self.construct_headers(config),
                auth=self.construct_auth(config),
            )

        self.client = __spawn_client
        setattr(self, "request", retry_strategy(self.request))  # noqa: B010

    def construct_headers(self, config: NexosAIAPIConfiguration) -> dict[str, str]:
        """
        Construct headers for the HTTP request.

        :param config: The configuration for the API service.
        :return: A dictionary of headers.
        """
        return {
            NEXOSAI_AUTH_HEADER_NAME: f"{NEXOSAI_AUTH_HEADER_PREFIX} {config.api_key}",
        }

    def construct_auth(self, config: NexosAIAPIConfiguration) -> httpx.Auth | None:  # noqa: ARG002
        """
        Construct authentication for the HTTP request.

        :param config: The configuration for the API service.
        :return: A httpx.Auth object or None if no authentication is needed.
        """
        return None

    async def disconnect(self) -> None:
        """
        Disconnect the HTTP client.
        """
        self.loop = None
