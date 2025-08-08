import contextlib
import os
from collections.abc import Generator

import environ

from nexosapi.config.settings.defaults import NEXOSAI_API_VERSION, NEXOSAI_BASE_URL, NEXOSAI_CONFIGURATION_PREFIX


@environ.config(prefix=NEXOSAI_CONFIGURATION_PREFIX)
class NexosAIAPIConfiguration:
    """
    Configuration class for the NEXOSAI API service.
    This class holds the necessary configuration values for the NEXOSAI API service.
    """

    @classmethod
    @contextlib.contextmanager
    def use(cls) -> Generator["NexosAIAPIConfiguration"]:
        """Context manager to use the configuration."""
        yield cls.from_environ(environ=os.environ)  # type: ignore

    base_url: str = environ.var(help="Base URL for the API service.", converter=str, default=NEXOSAI_BASE_URL)
    api_key: str = environ.var(help="API key", converter=str)
    version: str = environ.var(
        default=NEXOSAI_API_VERSION,
        help="Version of the NEXOSAI API to use, e.g., 'v1'.",
    )

    timeout: int = environ.var(default=30, help="Timeout for API requests in seconds.", converter=int)
    retries: int = environ.var(
        default=3,
        help="Number of retries for failed API requests.",
        converter=int,
    )
    exponential_backoff: bool = environ.var(
        default=True,
        help="Use exponential backoff for retries.",
        converter=bool,
    )
    minimum_wait: int = environ.var(
        default=1,
        help="Minimum wait time between retries in seconds.",
        converter=int,
    )
    maximum_wait: int = environ.var(
        default=10,
        help="Maximum wait time between retries in seconds.",
        converter=int,
    )
    reraise_exceptions: bool = environ.var(
        default=True,
        help="Whether to reraise exceptions after retries.",
        converter=bool,
    )
    rate_limit: int = environ.var(
        default=0,
        help="Rate limit for API requests per second. 0 means no rate limit.",
        converter=int,
    )
    follow_redirects: bool = environ.var(
        default=True,
        help="Whether to follow redirects in API requests.",
        converter=bool,
    )
