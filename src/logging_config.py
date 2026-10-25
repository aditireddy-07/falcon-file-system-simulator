import logging
import os


def setup_logger(project_root=None):
    """
    Configure FALCON logging.

    Logs are written to logs/falcon.log and displayed in the terminal
    at WARNING level and above.
    """

    if project_root is None:
        project_root = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

    log_directory = os.path.join(project_root, "logs")
    os.makedirs(log_directory, exist_ok=True)

    log_file = os.path.join(log_directory, "falcon.log")

    logger = logging.getLogger("FALCON")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate messages if setup_logger() is called again.
    if logger.handlers:
        return logger

    # Log detailed events to a persistent file.
    file_handler = logging.FileHandler(
        log_file,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)

    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_format)

    # Display warnings and errors in the terminal.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    console_format = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    console_handler.setFormatter(console_format)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
