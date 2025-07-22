import testcontainers.core

from nexosapi.common.logging import setup_logging


def setup_logging_for_tests(level: int) -> None:
    """
    Sets up logging for the tests based on the level environment variable.
    """
    new_logger = setup_logging(level=level)
    testcontainers.core.waiting_utils.logger = new_logger
    testcontainers.core.container.logger = new_logger
