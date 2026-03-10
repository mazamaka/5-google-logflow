from __future__ import annotations

import logging
import os
import sys

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """Route standard logging messages to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logger() -> logger.__class__:
    """Configure loguru logger for the application."""
    log_level = (settings.log_level or "INFO").upper()
    logger.remove()

    logger.add(
        sys.stderr,
        level=log_level,
        colorize=True,
        backtrace=True,
        diagnose=True,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    )

    try:
        os.makedirs("logs", exist_ok=True)
        logger.add(
            "logs/debug.log",
            level=log_level,
            rotation="10 MB",
            compression="zip",
            enqueue=True,
            format="{time} {level} {message}",
        )
    except OSError:
        pass

    if getattr(settings, "intercept_handler_logging", True):
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
        for name in (
            "uvicorn", "uvicorn.error", "uvicorn.access",
            "gunicorn", "gunicorn.error", "gunicorn.access",
            "sqlalchemy",
        ):
            log = logging.getLogger(name)
            log.handlers = [InterceptHandler()]
            log.propagate = True

    logger.info("Logger configured (level={})", log_level)
    return logger


logger = setup_logger()
