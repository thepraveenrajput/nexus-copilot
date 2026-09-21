import logging
import sys


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    logging.getLogger("kafka").setLevel(logging.WARNING)


def get_logger(name: str):
    return logging.getLogger(name)