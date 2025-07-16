import logging

import testcontainers.core


def setup_logging(level: int) -> None:
    """
    Sets up logging for the tests based on the level environment variable.
    """
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.root.handlers.clear()

    new_logger = logging.getLogger()
    new_logger.setLevel(level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler.setFormatter(formatter)
    new_logger.addHandler(stream_handler)
    new_logger.propagate = False
    logging.root = new_logger  # type: ignore
    testcontainers.core.waiting_utils.logger = new_logger
    testcontainers.core.container.logger = new_logger
