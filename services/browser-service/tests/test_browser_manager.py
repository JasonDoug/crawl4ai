"""Tests for browser manager functionality."""

import pytest
import asyncio
from browser_service.browser_manager import BrowserManager


@pytest.mark.asyncio
async def test_browser_start_stop():
    """Test browser startup and shutdown."""
    manager = BrowserManager()
    await manager.start()

    assert manager.browser is not None
    assert manager.playwright is not None

    await manager.stop()


@pytest.mark.asyncio
async def test_session_creation():
    """Test browser session creation and cleanup."""
    manager = BrowserManager()
    await manager.start()

    # Create session
    session_id = await manager.create_session(user_agent="TestAgent/1.0")

    assert session_id is not None
    assert manager.session_count() == 1

    # Close session
    await manager.close_session(session_id)
    assert manager.session_count() == 0

    await manager.stop()


@pytest.mark.asyncio
async def test_navigate_basic():
    """Test basic navigation functionality."""
    manager = BrowserManager()
    await manager.start()

    result = await manager.navigate(
        url="https://example.com",
        action="get_html",
        timeout=30,
    )

    assert "url" in result
    assert "html" in result
    assert len(result["html"]) > 0

    await manager.stop()


@pytest.mark.asyncio
async def test_navigate_with_session():
    """Test navigation with persistent session."""
    manager = BrowserManager()
    await manager.start()

    # Create session
    session_id = await manager.create_session()

    # Navigate with session
    result = await manager.navigate(
        url="https://example.com",
        session_id=session_id,
        action="get_html",
    )

    assert "url" in result
    assert "html" in result

    # Navigate again with same session
    result2 = await manager.navigate(
        url="https://example.org",
        session_id=session_id,
        action="get_html",
    )

    assert "url" in result2

    await manager.close_session(session_id)
    await manager.stop()


@pytest.mark.asyncio
async def test_cookie_management():
    """Test cookie add and get functionality."""
    manager = BrowserManager()
    await manager.start()

    session_id = await manager.create_session()

    # Add cookies
    await manager.add_cookies(
        session_id=session_id,
        cookies={"test_cookie": "test_value"},
        url="https://example.com",
    )

    # Get cookies
    cookies = await manager.get_cookies(session_id)
    assert isinstance(cookies, dict)

    await manager.close_session(session_id)
    await manager.stop()


@pytest.mark.asyncio
async def test_concurrent_pages():
    """Test handling multiple concurrent page operations."""
    manager = BrowserManager()
    await manager.start()

    # Create multiple navigation tasks
    tasks = [
        manager.navigate(
            url=f"https://example.com?page={i}",
            action="get_html",
        )
        for i in range(3)
    ]

    results = await asyncio.gather(*tasks)

    assert len(results) == 3
    for result in results:
        assert "html" in result

    await manager.stop()
