"""Sofia – Modular Chainlit Frontend for Italian Tutor.

This package provides a production-ready, modular Chainlit frontend for the
Italian Tutor application. It handles student profiling, message streaming,
and UI state management with clear separation of concerns.

Key components:
- config: Settings management with env var validation
- api: HTTP client for backend communication
- ui: UI components (greetings, message handlers, session management)
- chainlit_app: Main Chainlit application orchestrator
"""

__version__ = "0.2.0"
__all__ = ["config", "api", "ui"]
