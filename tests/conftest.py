import os
import sys

import pytest
import urllib3
import vcr
from pathlib import Path
from loguru import logger

# Get the parent directory of the directory containing this file
parent_dir = Path(__file__).resolve().parent.parent

# Add the parent directory to sys.path
sys.path.insert(0, str(parent_dir))

def pytest_addoption(parser):
    parser.addoption(
        "--ci",
        action="store_true",
        default=False,
        help="Run tests as if in a CI environment",
    )


def pytest_configure(config):
    # Ensure we're using VCR
    config.addinivalue_line("markers", "vcr: mark test to use VCR")


@pytest.fixture(scope="session", autouse=True)
def vcr_config():
    return {
        "filter_headers": ["authorization", "x-api-key"],
        "record_mode": "none" if os.environ.get("CI") else "once",
    }


@pytest.fixture(autouse=True)
def no_http_requests(monkeypatch):
    """Raise an error if any HTTP request is made, except for tiktoken encodings."""
    original_urlopen = urllib3.connectionpool.HTTPConnectionPool.urlopen
    logger.info("no_http_requests fixture setup")

    def urlopen_mock(self, method, url, *args, **kwargs):
        logger.debug(f"Intercepted request: {method} {url}")
        if "tiktoken" in url:
            logger.debug(f"Allowing tiktoken request: {method} {url}")
            return original_urlopen(self, method, url, *args, **kwargs)
        logger.debug(f"Blocking HTTP request: {method} {url}")
        raise RuntimeError(
            f"The test was about to make a real HTTP request to {method} {url}"
        )

    if os.environ.get("CI"):
        logger.debug("CI environment detected, activating no_http_requests fixture")
        monkeypatch.setattr(
            "urllib3.connectionpool.HTTPConnectionPool.urlopen", urlopen_mock
        )
    else:
        logger.debug(
            "Non-CI environment detected, no_http_requests fixture not activated"
        )

    yield

    logger.debug("no_http_requests fixture cleanup")


# Ensure all tests use VCR
def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.vcr)
