from _typeshed import Incomplete as Incomplete
from collections.abc import Generator

pytest_plugins: Incomplete
ASSETS_DIR: Incomplete

def setup_logging_for_tests() -> None: ...
def configure_testcontainers_via_env() -> None: ...
def add_test_domain_models() -> Generator[None]: ...
