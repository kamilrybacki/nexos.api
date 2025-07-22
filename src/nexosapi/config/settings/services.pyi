from collections.abc import Generator

class NexosAIAPIConfiguration:
    @classmethod
    def use(cls) -> Generator[NexosAIAPIConfiguration]: ...
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
