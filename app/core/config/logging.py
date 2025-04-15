from logging.config import dictConfig


def setup_logging(log_level: str) -> None:
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
                "level": log_level,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },
        "loggers": {
            "core": {
                "level": log_level,
                "handlers": ["console"],
                "propagate": False,
            },
        },
    })
