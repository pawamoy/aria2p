"""Configuration for the pytest test suite."""

import os
from pathlib import Path

import pytest

from aria2p import enable_logger


@pytest.fixture(autouse=True)
def gitlab_logs(request):
    # put logs in tests/logs
    log_path = Path("tests") / "logs"

    # tidy logs in subdirectories based on test module and class names
    module = request.module
    class_ = request.cls
    name = request.node.name + ".log"

    if module:
        log_path /= module.__name__.replace("tests.", "")
    if class_:
        log_path /= class_.__name__

    log_path.mkdir(parents=True, exist_ok=True)

    # append last part of the name and enable logger
    log_path /= name
    if log_path.exists():
        log_path.unlink()
    enable_logger(sink=log_path, level=os.environ.get("PYTEST_LOG_LEVEL", "TRACE"))
