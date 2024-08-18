import os
import sys

import pytest
import vcr
from pathlib import Path

# Get the parent directory of the directory containing this file
parent_dir = Path(__file__).resolve().parent.parent

# Add the parent directory to sys.path
sys.path.insert(0, str(parent_dir))


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
    """Raise an error if any HTTP request is made."""

    def urlopen_mock(self, method, url, *args, **kwargs):
        raise RuntimeError(
            f"The test was about to make a real HTTP request to {method} {url}"
        )

    if os.environ.get("CI"):  # Only activate in CI environment
        monkeypatch.setattr(
            "urllib3.connectionpool.HTTPConnectionPool.urlopen", urlopen_mock
        )


# Ensure all tests use VCR
def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(pytest.mark.vcr)
