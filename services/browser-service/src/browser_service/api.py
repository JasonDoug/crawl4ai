"""Browser service API endpoints."""

import time
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from crawl4ai_schemas import BrowserRequest, BrowserResponse

router = APIRouter(tags=["browser"])


class SessionCreateRequest(BaseModel):
    """Request to create a new browser session."""

    user_agent: Optional[str] = None
    viewport: Optional[dict] = None
    headers: Optional[dict] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None


class SessionResponse(BaseModel):
    """Response with session information."""

    session_id: str
    message: str


@router.post("/navigate", response_model=BrowserResponse)
async def navigate(request: BrowserRequest, app_request: Request) -> BrowserResponse:
    """Navigate to a URL and perform actions.

    Args:
        request: Browser request with URL and actions
        app_request: FastAPI request object

    Returns:
        Browser response with HTML and metadata

    Raises:
        HTTPException: If navigation fails
    """
    start_time = time.time()
    browser_manager = app_request.app.state.browser_manager

    try:
        result = await browser_manager.navigate(
            url=str(request.url),
            action=request.action,
            session_id=request.session_id,
            timeout=request.timeout,
            wait_time=request.wait_time,
            wait_for_selector=request.wait_for_selector,
            user_agent=request.user_agent,
            viewport=request.viewport,
            javascript=request.javascript,
            cookies=request.cookies,
            headers=request.headers,
            proxy=request.proxy,
        )

        duration_ms = (time.time() - start_time) * 1000

        return BrowserResponse(
            success=True,
            url=result.get("url", str(request.url)),
            html=result.get("html"),
            screenshot=result.get("screenshot"),
            javascript_result=result.get("javascript_result"),
            cookies=result.get("cookies"),
            duration_ms=duration_ms,
            metadata=request.metadata,
        )

    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        return BrowserResponse(
            success=False,
            url=str(request.url),
            error=str(e),
            duration_ms=duration_ms,
            metadata=request.metadata,
        )


@router.post("/sessions", response_model=SessionResponse)
async def create_session(
    request: SessionCreateRequest, app_request: Request
) -> SessionResponse:
    """Create a new browser session.

    Args:
        request: Session creation request
        app_request: FastAPI request object

    Returns:
        Session ID and message

    Raises:
        HTTPException: If session creation fails
    """
    browser_manager = app_request.app.state.browser_manager

    try:
        session_id = await browser_manager.create_session(
            user_agent=request.user_agent,
            viewport=request.viewport,
            headers=request.headers,
            locale=request.locale,
            timezone=request.timezone,
        )

        return SessionResponse(
            session_id=session_id, message="Session created successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create session: {str(e)}"
        )


@router.delete("/sessions/{session_id}", response_model=SessionResponse)
async def close_session(session_id: str, app_request: Request) -> SessionResponse:
    """Close a browser session.

    Args:
        session_id: Session ID to close
        app_request: FastAPI request object

    Returns:
        Session ID and message

    Raises:
        HTTPException: If session close fails
    """
    browser_manager = app_request.app.state.browser_manager

    try:
        await browser_manager.close_session(session_id)
        return SessionResponse(
            session_id=session_id, message="Session closed successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to close session: {str(e)}"
        )


@router.post("/sessions/{session_id}/cookies")
async def add_cookies(session_id: str, cookies: dict, url: str, app_request: Request):
    """Add cookies to a session.

    Args:
        session_id: Session ID
        cookies: Cookies to add
        url: URL for cookie context
        app_request: FastAPI request object

    Returns:
        Success message

    Raises:
        HTTPException: If adding cookies fails
    """
    browser_manager = app_request.app.state.browser_manager

    try:
        await browser_manager.add_cookies(session_id, cookies, url)
        return {"message": "Cookies added successfully"}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add cookies: {str(e)}")


@router.get("/sessions/{session_id}/cookies")
async def get_cookies(session_id: str, app_request: Request):
    """Get cookies from a session.

    Args:
        session_id: Session ID
        app_request: FastAPI request object

    Returns:
        Dictionary of cookies

    Raises:
        HTTPException: If getting cookies fails
    """
    browser_manager = app_request.app.state.browser_manager

    try:
        cookies = await browser_manager.get_cookies(session_id)
        return {"cookies": cookies}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cookies: {str(e)}")


@router.get("/status")
async def status(app_request: Request):
    """Get browser service status.

    Returns:
        Service status information
    """
    browser_manager = app_request.app.state.browser_manager
    return {
        "status": "running",
        "active_pages": browser_manager.active_count(),
        "active_sessions": browser_manager.session_count(),
        "version": "0.1.0",
    }
