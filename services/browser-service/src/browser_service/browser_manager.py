"""Browser manager for handling Playwright browser instances."""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)


class SessionInfo:
    """Information about a browser session."""

    def __init__(self, session_id: str, context: BrowserContext):
        """Initialize session info."""
        self.session_id = session_id
        self.context = context
        self.created_at = datetime.utcnow()
        self.last_used = datetime.utcnow()
        self.page_count = 0

    def touch(self):
        """Update last used timestamp."""
        self.last_used = datetime.utcnow()


class BrowserManager:
    """Manages Playwright browser instances and page actions."""

    def __init__(self, session_ttl_minutes: int = 30):
        """Initialize the browser manager.

        Args:
            session_ttl_minutes: Session time-to-live in minutes
        """
        self.playwright = None
        self.browser: Optional[Browser] = None
        self._active_pages = 0
        self._sessions: Dict[str, SessionInfo] = {}
        self._sessions_lock = asyncio.Lock()
        self._session_ttl = timedelta(minutes=session_ttl_minutes)
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the browser manager and launch browser."""
        logger.info("Starting Playwright browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        logger.info("Browser launched successfully")

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_sessions())
        logger.info("Session cleanup task started")

    async def stop(self):
        """Stop the browser manager and close browser."""
        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Close all sessions
        async with self._sessions_lock:
            session_ids = list(self._sessions.keys())

        for session_id in session_ids:
            await self.close_session(session_id)

        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser stopped")

    async def _cleanup_sessions(self):
        """Background task to cleanup expired sessions."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                now = datetime.utcnow()

                # Collect expired session IDs while holding the lock
                async with self._sessions_lock:
                    expired = [
                        session_id
                        for session_id, session_info in self._sessions.items()
                        if now - session_info.last_used > self._session_ttl
                    ]

                # Close sessions outside the lock to avoid deadlock
                for session_id in expired:
                    logger.info(f"Cleaning up expired session: {session_id}")
                    await self.close_session(session_id)

            except asyncio.CancelledError:
                break
            except Exception:
                logger.exception("Error in session cleanup")

    def active_count(self) -> int:
        """Get count of active pages."""
        return self._active_pages

    def session_count(self) -> int:
        """Get count of active sessions."""
        return len(self._sessions)

    async def create_session(
        self,
        user_agent: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        headers: Optional[Dict[str, str]] = None,
        locale: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> str:
        """Create a new browser session.

        Args:
            user_agent: Custom user agent
            viewport: Viewport size
            headers: Custom headers
            locale: Locale setting
            timezone: Timezone setting

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        context_options = {}
        if user_agent:
            context_options["user_agent"] = user_agent
        if viewport:
            context_options["viewport"] = viewport
        if headers:
            context_options["extra_http_headers"] = headers
        if locale:
            context_options["locale"] = locale
        if timezone:
            context_options["timezone_id"] = timezone

        context = await self.browser.new_context(**context_options)

        async with self._sessions_lock:
            self._sessions[session_id] = SessionInfo(session_id, context)

        logger.info(f"Created new session: {session_id}")
        return session_id

    async def close_session(self, session_id: str):
        """Close a browser session.

        Args:
            session_id: Session ID to close

        Raises:
            ValueError: If session_id is not found
        """
        async with self._sessions_lock:
            if session_id not in self._sessions:
                raise ValueError(f"Session not found: {session_id}")

            session_info = self._sessions[session_id]

        # Close context outside the lock to avoid blocking other operations
        await session_info.context.close()

        async with self._sessions_lock:
            # Remove from dict after closing
            if session_id in self._sessions:
                del self._sessions[session_id]

        logger.info(f"Closed session: {session_id}")

    async def add_cookies(self, session_id: str, cookies: Dict[str, str], url: str):
        """Add cookies to a session.

        Args:
            session_id: Session ID
            cookies: Cookies to add
            url: URL for cookie context
        """
        async with self._sessions_lock:
            if session_id not in self._sessions:
                raise ValueError(f"Session not found: {session_id}")

            session_info = self._sessions[session_id]
            session_info.touch()

        # Add cookies outside the lock to avoid blocking
        await session_info.context.add_cookies(
            [{"name": k, "value": v, "url": url} for k, v in cookies.items()]
        )

    async def get_cookies(self, session_id: str) -> Dict[str, str]:
        """Get cookies from a session.

        Args:
            session_id: Session ID

        Returns:
            Dictionary of cookies
        """
        async with self._sessions_lock:
            if session_id not in self._sessions:
                raise ValueError(f"Session not found: {session_id}")

            session_info = self._sessions[session_id]
            session_info.touch()

        # Get cookies outside the lock to avoid blocking
        cookies = await session_info.context.cookies()
        return {cookie["name"]: cookie["value"] for cookie in cookies}

    async def navigate(
        self,
        url: str,
        action: str = "navigate",
        session_id: Optional[str] = None,
        timeout: int = 30,
        wait_time: float = 0,
        wait_for_selector: Optional[str] = None,
        user_agent: Optional[str] = None,
        viewport: Optional[Dict[str, int]] = None,
        javascript: Optional[str] = None,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Navigate to URL and perform action.

        Args:
            url: URL to navigate to
            action: Action to perform
            session_id: Optional session ID for persistent context
            timeout: Timeout in seconds
            wait_time: Wait time after action in seconds
            wait_for_selector: CSS selector to wait for
            user_agent: Custom user agent
            viewport: Viewport size
            javascript: JavaScript to execute
            cookies: Cookies to set
            headers: Custom headers
            proxy: Proxy URL

        Returns:
            Dictionary with action results

        Raises:
            ValueError: If session_id is provided but not found
            TimeoutError: If navigation or action times out
        """
        context: Optional[BrowserContext] = None
        page: Optional[Page] = None
        should_close_context = True

        try:
            self._active_pages += 1

            # Use existing session or create temporary context
            if session_id:
                async with self._sessions_lock:
                    if session_id not in self._sessions:
                        raise ValueError(f"Session not found: {session_id}")

                    session_info = self._sessions[session_id]
                    session_info.touch()
                    session_info.page_count += 1

                context = session_info.context
                should_close_context = False
            else:
                # Create temporary context with options
                context_options = {}
                if user_agent:
                    context_options["user_agent"] = user_agent
                if viewport:
                    context_options["viewport"] = viewport
                if headers:
                    context_options["extra_http_headers"] = headers

                context = await self.browser.new_context(**context_options)

                # Set cookies if provided
                if cookies:
                    await context.add_cookies(
                        [
                            {"name": k, "value": v, "url": url}
                            for k, v in cookies.items()
                        ]
                    )

            # Create new page
            page = await context.new_page()

            # Navigate to URL
            try:
                await page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
            except Exception as e:
                # Try with domcontentloaded if networkidle fails
                logger.warning(f"Network idle failed, trying domcontentloaded: {e}")
                await page.goto(
                    url, timeout=timeout * 1000, wait_until="domcontentloaded"
                )

            # Wait for selector if provided
            if wait_for_selector:
                await page.wait_for_selector(wait_for_selector, timeout=timeout * 1000)

            # Wait if requested
            if wait_time > 0:
                await page.wait_for_timeout(int(wait_time * 1000))

            result = {"url": page.url, "title": await page.title()}

            # Perform action
            if action == "get_html":
                result["html"] = await page.content()

            elif action == "screenshot":
                screenshot_bytes = await page.screenshot(full_page=True)
                import base64

                result["screenshot"] = base64.b64encode(screenshot_bytes).decode()

            elif action == "execute_js" and javascript:
                result["javascript_result"] = await page.evaluate(javascript)
                result["html"] = await page.content()

            elif action == "click" and wait_for_selector:
                await page.click(wait_for_selector)
                result["html"] = await page.content()

            elif action == "scroll":
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(1000)  # Wait for lazy load
                result["html"] = await page.content()

            else:  # navigate
                result["html"] = await page.content()

            # Get cookies
            result["cookies"] = {
                cookie["name"]: cookie["value"] for cookie in await context.cookies()
            }

            # Get page metadata
            result["metadata"] = {
                "viewport": page.viewport_size,
                "url": page.url,
                "title": await page.title(),
            }

            return result

        except asyncio.TimeoutError as e:
            logger.error(f"Timeout navigating to {url}: {e}")
            raise TimeoutError(f"Navigation timeout: {url}") from e
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            raise
        finally:
            self._active_pages -= 1
            if page:
                await page.close()
            if context and should_close_context:
                await context.close()
