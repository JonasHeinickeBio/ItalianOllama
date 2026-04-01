"""
Browser-level session persistence using streamlit-cookies-manager.

This module handles:
- Persisting JWT tokens to browser cookies (survives page reloads)
- Persisting student ID to browser cookies
- Automatic session restoration on page load
- Automatic cleanup on logout
"""

import logging
from typing import Optional, Tuple

import streamlit as st

try:
    from streamlit_cookies_manager import CookieManager

    COOKIES_AVAILABLE = True
except ImportError:
    COOKIES_AVAILABLE = False
    CookieManager = None  # type: ignore

logger = logging.getLogger("browser_storage")
logger.setLevel(logging.INFO)


def get_cookie_manager() -> Optional["CookieManager"]:
    """Initialize and return cookie manager for persistent browser storage."""
    if not COOKIES_AVAILABLE:
        logger.warning(
            "⚠️ streamlit-cookies-manager not installed - session won't persist across reloads"
        )
        return None

    if "cookie_manager" not in st.session_state:
        try:
            st.session_state.cookie_manager = CookieManager()
            logger.info("✓ Cookie manager initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize cookie manager: {e}")
            return None

    return st.session_state.cookie_manager


def save_session_to_cookies(student_id: str, access_token: str, expires_days: int = 7) -> bool:
    """
    Save JWT token and student_id to browser cookies for persistence.

    Args:
        student_id: The authenticated student's ID
        access_token: JWT token from backend
        expires_days: How long to persist (default 7 days)

    Returns:
        True if saved successfully, False otherwise
    """
    cookies = get_cookie_manager()
    if not cookies:
        logger.warning("⚠️ Cookies not available - session won't persist")
        return False

    try:
        cookies["student_id"] = student_id
        cookies["access_token"] = access_token
        cookies["expires_days"] = str(expires_days)
        cookies.save()
        logger.info(f"✓ Session saved to cookies | student_id={student_id}")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to save session to cookies: {e}")
        return False


def restore_session_from_cookies() -> Tuple[Optional[str], Optional[str]]:
    """
    Restore JWT token and student_id from browser cookies if they exist.

    Returns:
        Tuple of (student_id, access_token) or (None, None) if not found
    """
    cookies = get_cookie_manager()
    if not cookies:
        logger.debug("⚠️ Cookies not available")
        return None, None

    try:
        student_id = cookies.get("student_id")
        access_token = cookies.get("access_token")

        if student_id and access_token:
            logger.info(f"✓ Session restored from cookies | student_id={student_id}")
            return student_id, access_token
        else:
            logger.debug("ℹ️ No active session in cookies")
            return None, None
    except Exception as e:
        logger.error(f"❌ Failed to restore session from cookies: {e}")
        return None, None


def clear_session_cookies() -> bool:
    """
    Clear all session cookies on logout.

    Returns:
        True if cleared successfully, False otherwise
    """
    cookies = get_cookie_manager()
    if not cookies:
        logger.warning("⚠️ Cookies not available")
        return False

    try:
        cookies.delete("student_id", "access_token", "expires_days")
        cookies.save()
        logger.info("✓ Session cleared from cookies")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to clear cookies: {e}")
        return False
