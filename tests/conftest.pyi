from _typeshed import Incomplete
from collections.abc import Generator
from tests.mocks import MockRequestModel as MockRequestModel, MockResponseModel as MockResponseModel

pytest_plugins: Incomplete
ASSETS_DIR: Incomplete

def setup_logging_for_tests() -> None: ...
def configure_testcontainers_via_env() -> None:
    """
    Configures testcontainers to use the environment variables defined in the .env file.
    This is necessary for testcontainers to work correctly with the environment variables.
    """

def add_test_domain_models() -> Generator[None]:
    """
    Adds the test domain models to the global namespace.
    This is necessary for the tests to access the domain models.
    """
