import pytest
from _typeshed import Incomplete
from collections.abc import Callable as Callable, Generator
from contextlib import AbstractContextManager
from nexosapi.services.http import NexosAIAPIService
from tests.conftest import ASSETS_DIR as ASSETS_DIR
from tests.mocks import MockAIAPIService as MockAIAPIService

MOCK_API_DIR: Incomplete
MOCK_API_PORT: int
MOCK_API_KEY: str

@pytest.fixture
def service_environment(monkeypatch: pytest.MonkeyPatch) -> Callable[..., Generator]: ...
@pytest.fixture
def initialize_nexosai_api_service() -> Callable[[], NexosAIAPIService]: ...

MOCK_API_DATA_JSON_PATH: Incomplete
MOCK_API_DATA: Incomplete

@pytest.fixture
def using_test_api_container() -> Callable[..., Generator[str]]: ...
def mock_api_injected_into_services_wiring(
    service: type[MockAIAPIService],
) -> AbstractContextManager[Callable[..., Generator[None]]]:
    """
    Context manager to inject a mock API service into the given service class.

    :param service: The service class to inject the mock API service into.
    :return: A context manager that yields the mock API service.
    """

@pytest.fixture
def initialized_controller[ControllerType](
    using_test_api_container: Callable[[], NexosAIAPIService], service_environment: Callable[..., Generator]
) -> Callable[..., Generator[ControllerType]]:
    """
    Fixture to initialize the NexosAI API service controller.

    This fixture sets up the environment variables and starts the test API container.

    :param using_test_api_container: A callable that starts the test API container.
    :param service_environment: A callable that patches the environment variables.

    """
