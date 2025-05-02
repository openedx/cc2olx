import logging
from pathlib import Path
from typing import Optional

from django.conf import settings
from rich.logging import RichHandler

default_formatter = logging.Formatter(settings.LOG_FORMAT)


def build_console_logger(name: str) -> logging.Logger:
    """
    Build the console logger with rich output.
    """
    logger = logging.getLogger(f"console_{name}")

    handler = RichHandler(rich_tracebacks=True, show_time=False, show_level=False, show_path=False)
    handler.setFormatter(default_formatter)
    logger.addHandler(handler)

    return logger


def build_file_logger(name: str, *, logs_file_path: Optional[Path]) -> logging.Logger:
    """
    Build the logger that writes logs to a file.
    """
    logger = logging.getLogger(f"file_{name}_{logs_file_path}")

    if logs_file_path:
        logs_file_path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(logs_file_path, mode="a", encoding="utf-8")
    else:
        handler = logging.NullHandler()
    handler.setFormatter(default_formatter)
    logger.addHandler(handler)

    return logger


def build_input_processing_file_logger(
    name: str,
    *,
    logs_dir_path: Optional[Path],
    input_file_path: Path,
) -> logging.Logger:
    """
    Build a file logger for the input file processing logging.
    """
    logs_file_path = logs_dir_path / f"{input_file_path.name}.log" if logs_dir_path else None
    return build_file_logger(name, logs_file_path=logs_file_path)
