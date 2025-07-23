import pytest
from _typeshed import Incomplete as Incomplete
from collections.abc import Callable as Callable, Generator
from nexosapi.services.http import NexosAPIService as NexosAPIService

MOCK_API_DIR: Incomplete
MOCK_API_PORT: int
MOCK_API_KEY: str

def service_environment(monkeypatch: pytest.MonkeyPatch) -> Callable[..., Generator]: ...
def initialize_nexosai_api_service() -> Callable[[], NexosAPIService]: ...

MOCK_API_DATA_JSON_PATH: Incomplete
MOCK_API_DATA: Incomplete

def using_test_api_container() -> Callable[..., Generator[str]]: ...
