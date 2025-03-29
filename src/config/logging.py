import logging
from logging.config import dictConfig


def setup_logging() -> None:
    """Set up logging configuration for the entire application."""
    dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": "DEBUG",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "loggers": {
            "src": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    })
