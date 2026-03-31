"""API client module for backend communication.

Provides HTTP clients for:
- Student profile retrieval (get_student_profile)
- Student creation (create_student)
- Streaming chat completions (stream_chat_completions)
- Token generation (get_auth_token)
"""

from .client import create_student, get_auth_token, get_student_profile, stream_chat_completions
from .errors import (
    BackendConnectionError,
    BackendError,
    StreamingError,
    StudentNotFoundError,
)

__all__ = [
    "get_student_profile",
    "create_student",
    "stream_chat_completions",
    "get_auth_token",
    "BackendError",
    "StudentNotFoundError",
    "BackendConnectionError",
    "StreamingError",
]
