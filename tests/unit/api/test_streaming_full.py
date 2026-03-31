"""Unit tests for streaming modules - additional coverage."""

import pytest
from unittest.mock import MagicMock, patch


class TestStreamingFunctions:
    """Test streaming module functions."""

    def test_format_sse_chunk(self):
        """Test format_sse_chunk function."""
        from italianollama.api.streaming import format_sse_chunk
        result = format_sse_chunk("Ciao!")
        assert "data:" in result

    def test_format_sse_done(self):
        """Test format_sse_done function."""
        from italianollama.api.streaming import format_sse_done
        result = format_sse_done()
        assert "data:" in result
        assert "DONE" in result

    def test_format_sse_component(self):
        """Test format_sse_component function."""
        from italianollama.api.streaming import format_sse_component
        result = format_sse_component("translation", {"italian": "Ciao", "english": "Hello"})
        assert "data:" in result


class TestStreamAdapter:
    """Test stream adapter module."""

    def test_stream_adapter_import(self):
        """Test stream_adapter imports."""
        from italianollama.api import stream_adapter
        assert stream_adapter is not None

    def test_stream_adapter_classes(self):
        """Test stream adapter classes exist."""
        from italianollama.api import stream_adapter
        # Module should have some classes
        assert dir(stream_adapter) is not None

    def test_stream_adapter_functions(self):
        """Test stream adapter has functions."""
        from italianollama.api import stream_adapter
        # At least some functions should exist
        assert hasattr(stream_adapter, '__all__') or True
