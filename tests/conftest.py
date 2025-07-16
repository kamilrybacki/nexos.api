import logging
from pathlib import Path

import pytest
import testcontainers.core.config
import testcontainers.core.container
import testcontainers.core.waiting_utils

import tests.common

pytest_plugins = ["tests.mocks"]

ASSETS_DIR = Path(__file__).parent / "assets"


@pytest.fixture(autouse=True, scope="session")
def setup_logging_for_tests() -> None:
    tests.common.setup_logging(level=logging.INFO)


@pytest.fixture(autouse=True)
def configure_testcontainers_via_env() -> None:
    """
    Configures testcontainers to use the environment variables defined in the .env file.
    This is necessary for testcontainers to work correctly with the environment variables.
    """
    testcontainers.core.config.RYUK_DISABLED = True
