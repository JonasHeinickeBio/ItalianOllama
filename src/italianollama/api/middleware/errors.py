"""Error handling middleware for standardized error responses."""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from italianollama.api.exceptions import TutorException

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI) -> None:
    """Register error handlers on FastAPI app.

    Handles:
    - TutorException: Custom app exceptions with trace_id
    - ValidationError: Pydantic validation errors
    - Exception: Catch-all for unexpected errors
    """

    @app.exception_handler(TutorException)
    async def tutor_exception_handler(request: Request, exc: TutorException):
        """Handle custom tutor exceptions."""
        request_id = getattr(request.state, "request_id", "unknown")

        logger.warning(
            f"TutorException | {exc.error_type} | "
            f"status={exc.status_code} | "
            f"trace_id={exc.trace_id} | "
            f"request_id={request_id} | "
            f"message={exc.detail.get('message', '')}"
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )

    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors."""
        from italianollama.api.exceptions import ValidationError as TutorValidationError

        request_id = getattr(request.state, "request_id", "unknown")

        # Extract validation errors
        errors = []
        for error in exc.errors():
            errors.append(
                {
                    "field": ".".join(str(x) for x in error["loc"][1:]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        logger.warning(
            f"ValidationError | {len(errors)} errors | request_id={request_id} | errors={errors}"
        )

        # Return proper validation error response
        tutor_exc = TutorValidationError(
            detail=f"Validation failed: {len(errors)} error(s)",
        )
        tutor_exc.detail["validation_errors"] = errors

        return JSONResponse(
            status_code=400,
            content=tutor_exc.detail,
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        from italianollama.api.exceptions import InternalServerError

        request_id = getattr(request.state, "request_id", "unknown")

        logger.error(
            f"UnexpectedException | {type(exc).__name__} | "
            f"request_id={request_id} | "
            f"message={str(exc)}",
            exc_info=True,
        )

        # Don't expose internal error messages in production
        safe_message = "An unexpected error occurred"
        tutor_exc = InternalServerError(detail=safe_message)

        return JSONResponse(
            status_code=500,
            content=tutor_exc.detail,
        )
