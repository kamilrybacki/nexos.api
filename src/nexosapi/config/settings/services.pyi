import contextlib
from collections.abc import Generator
from nexosapi.config.settings.defaults import NEXOSAI_CONFIGURATION_PREFIX as NEXOSAI_CONFIGURATION_PREFIX

class NexosAIAPIConfiguration:
    """
    Configuration class for the NEXOSAI API service.
    This class holds the necessary configuration values for the NEXOSAI API service.
    """
    @classmethod
    @contextlib.contextmanager
    def use(cls) -> Generator["NexosAIAPIConfiguration"]:
        """Context manager to use the configuration."""
    base_url: str
    api_key: str
    version: str
    timeout: int
    retries: int
    exponential_backoff: bool
    minimum_wait: int
    maximum_wait: int
    reraise_exceptions: bool
    rate_limit: int
    follow_redirects: bool
