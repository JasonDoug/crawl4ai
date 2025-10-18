"""Pytest configuration for browser service tests."""

import pytest


def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line("markers", "asyncio: mark test as requiring asyncio")
