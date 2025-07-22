import logging
from collections.abc import Generator
from pathlib import Path

import pytest
import testcontainers.core.config
import testcontainers.core.container
import testcontainers.core.waiting_utils

import nexosapi.domain.requests
import nexosapi.domain.responses
import tests.common
from tests.mocks import MockRequestModel, MockResponseModel

pytest_plugins = ["tests.services"]

ASSETS_DIR = Path(__file__).parent / "assets"


@pytest.fixture(autouse=True, scope="session")
def setup_logging_for_tests() -> None:
    tests.common.setup_logging_for_tests(level=logging.INFO)


@pytest.fixture(autouse=True)
def configure_testcontainers_via_env() -> None:
    """
    Configures testcontainers to use the environment variables defined in the .env file.
    This is necessary for testcontainers to work correctly with the environment variables.
    """
    testcontainers.core.config.RYUK_DISABLED = True


@pytest.fixture(autouse=True, scope="session")
def add_test_domain_models() -> Generator[None]:
    """
    Adds the test domain models to the global namespace.
    This is necessary for the tests to access the domain models.
    """
    nexosapi.domain.requests.MockRequestModel = MockRequestModel
    nexosapi.domain.responses.MockResponseModel = MockResponseModel
    yield
    # Cleanup if necessary
    delattr(nexosapi.domain.requests, "MockRequestModel")
    delattr(nexosapi.domain.responses, "MockResponseModel")
