import logging


def setup_logging(level: int) -> logging.Logger:
    """
    Set up the logging configuration for the application.

    :param level: The logging level to set.
    """
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Set up basic configuration
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
    return new_logger
