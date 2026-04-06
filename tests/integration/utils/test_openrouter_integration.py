"""Integration tests for OpenRouter API class."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from italianollama.utils.openrouter import OpenRouterAPI


@pytest.mark.asyncio
async def test_openrouter_api_initialization():
    """Test OpenRouterAPI class initialization."""
    api = OpenRouterAPI(api_key="test-key-123")
    
    assert api.api_key == "test-key-123"
    assert api.client is None
    assert api._base_url == "https://openrouter.ai/api/v1"
    assert api.DEFAULT_TIMEOUT == 30.0


@pytest.mark.asyncio
async def test_openrouter_api_env_var_initialization():
    """Test OpenRouterAPI initialization from environment variable."""
    import os
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "env-key-456"}):
        api = OpenRouterAPI()
        
        assert api.api_key == "env-key-456"


@pytest.mark.asyncio
async def test_openrouter_api_async_context_management():
    """Test OpenRouterAPI async context manager."""
    import os
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        api = OpenRouterAPI()
        
        async with api:
            client = await api._get_client()
            assert client is not None
            assert api.client is not None
        
        assert api.client is None


@pytest.mark.asyncio
async def test_openrouter_api_get_client_lazy_initialization():
    """Test _get_client() lazy initialization."""
    api = OpenRouterAPI(api_key="test-key")
    
    assert api.client is None
    
    client = await api._get_client()
    
    assert api.client is not None
    assert api.client == client
    assert str(client.base_url) == "https://openrouter.ai/api/v1/"


@pytest.mark.asyncio
async def test_openrouter_api_get_client_headers():
    """Test HTTP headers in _get_client()."""
    import os
    
    with patch.dict(
        os.environ,
        {
            "OPENROUTER_API_KEY": "test-key",
            "OPENROUTER_HTTP_REFERER": "https://example.com",
            "OPENROUTER_X_TITLE": "TestApp",
        },
        clear=True,
    ):
        api = OpenRouterAPI()
        client = await api._get_client()
        
        headers = client.headers
        
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["HTTP-Referer"] == "https://example.com"
        assert headers["X-Title"] == "TestApp"


@pytest.mark.asyncio
async def test_openrouter_api_get_client_default_headers():
    """Test default HTTP headers when env vars not set."""
    import os
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}, clear=True):
        api = OpenRouterAPI()
        client = await api._get_client()
        
        headers = client.headers
        
        assert headers["HTTP-Referer"] == ""
        assert headers["X-Title"] == "ItalianOllama"


@pytest.mark.asyncio
async def test_openrouter_api_get_models():
    """Test get_models() method."""
    api = OpenRouterAPI(api_key="test-key")
    
    mock_response = Mock()
    mock_response.json = Mock(return_value={
        "data": [
            {"id": "model1", "name": "Model 1", "pricing": {"prompt": "0.1", "completion": "0.2"}},
            {"id": "model2", "name": "Model 2", "pricing": {"prompt": "0", "completion": "0"}},
        ]
    })
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    
    with patch.object(api, "_get_client", return_value=mock_client):
        models = await api.get_models()
        
        assert len(models) == 2
        assert models[0]["id"] == "model1"
        assert models[1]["id"] == "model2"


@pytest.mark.asyncio
async def test_openrouter_api_get_models_free_only():
    """Test get_models() with free_only filter."""
    api = OpenRouterAPI(api_key="test-key")
    
    mock_response = Mock()
    mock_response.json = Mock(return_value={
        "data": [
            {"id": "paid-model", "name": "Paid Model", "pricing": {"prompt": "0.1", "completion": "0.2"}},
            {"id": "free-model", "name": "Free Model", "pricing": {"prompt": "0", "completion": "0"}},
            {"id": "another-free", "name": "Another Free", "pricing": {"prompt": "0.0", "completion": "0.0"}},
        ]
    })
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    
    with patch.object(api, "_get_client", return_value=mock_client):
        models = await api.get_models(free_only=True)
        
        assert len(models) == 2
        assert all(api._is_free_model(m) for m in models)


@pytest.mark.asyncio
async def test_openrouter_api_get_model_pricing():
    """Test get_model_pricing() method."""
    api = OpenRouterAPI(api_key="test-key")
    
    mock_response = Mock()
    mock_response.json = Mock(return_value={
        "data": {
            "id": "openai/gpt-4o-mini",
            "name": "GPT-4o Mini",
            "pricing": {"prompt": "0.0000001", "completion": "0.0000002"},
            "context_window": 128000,
        }
    })
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    
    with patch.object(api, "_get_client", return_value=mock_client):
        pricing = await api.get_model_pricing("openai/gpt-4o-mini")
        
        assert pricing["id"] == "openai/gpt-4o-mini"
        assert pricing["pricing"]["prompt"] == "0.0000001"
        assert "context_window" in pricing


@pytest.mark.asyncio
async def test_openrouter_api_close():
    """Test close() method."""
    api = OpenRouterAPI(api_key="test-key")
    
    mock_client = AsyncMock()
    api.client = mock_client
    
    await api.close()
    
    assert api.client is None
    mock_client.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_openrouter_api_close_no_client():
    """Test close() when client is None."""
    api = OpenRouterAPI(api_key="test-key")
    
    await api.close()
    
    assert api.client is None


@pytest.mark.asyncio
async def test_openrouter_api_error_missing_api_key():
    """Test error handling for missing API key when using discover_free_models."""
    import os
    
    with patch.dict(os.environ, {}, clear=True):
        from italianollama.utils.openrouter import discover_free_models
        
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable not set"):
            await discover_free_models()


@pytest.mark.asyncio
async def test_openrouter_api_http_headers_referer_and_title():
    """Test that HTTP headers HTTP-Referer and X-Title are properly set."""
    import os
    
    with patch.dict(
        os.environ,
        {
            "OPENROUTER_API_KEY": "test-key-789",
            "OPENROUTER_HTTP_REFERER": "https://myapp.com/italian-tutor",
            "OPENROUTER_X_TITLE": "ItalianTutor",
        },
        clear=True,
    ):
        api = OpenRouterAPI()
        client = await api._get_client()
        
        headers = client.headers
        
        assert "HTTP-Referer" in headers
        assert "X-Title" in headers
        assert headers["HTTP-Referer"] == "https://myapp.com/italian-tutor"
        assert headers["X-Title"] == "ItalianTutor"


@pytest.mark.asyncio
async def test_openrouter_api_get_client_returns_same_instance():
    """Test that _get_client() returns the same client instance on subsequent calls."""
    api = OpenRouterAPI(api_key="test-key")
    
    client1 = await api._get_client()
    client2 = await api._get_client()
    client3 = await api._get_client()
    
    assert client1 is client2
    assert client2 is client3
    assert api.client is client1


@pytest.mark.asyncio
async def test_openrouter_api_close_clears_client_reference():
    """Test that close() clears the client reference."""
    api = OpenRouterAPI(api_key="test-key")
    
    await api._get_client()
    assert api.client is not None
    
    await api.close()
    assert api.client is None


@pytest.mark.asyncio
async def test_openrouter_api_context_manager_exception_handling():
    """Test async context manager handles exceptions properly."""
    import os
    
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
        api = OpenRouterAPI()
        
        try:
            async with api:
                client = await api._get_client()
                assert client is not None
                raise ValueError("Simulated error")
        except ValueError:
            pass
        
        assert api.client is None


@pytest.mark.asyncio
async def test_openrouter_api_get_models_response_validation():
    """Test get_models() response validation."""
    api = OpenRouterAPI(api_key="test-key")
    
    mock_response = Mock()
    mock_response.json = Mock(return_value={
        "data": [
            {
                "id": "openai/gpt-4o",
                "name": "GPT-4o",
                "pricing": {"prompt": "0.000005", "completion": "0.000015"},
                "context_window": 128000,
            }
        ]
    })
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    
    with patch.object(api, "_get_client", return_value=mock_client):
        models = await api.get_models()
        
        assert len(models) == 1
        model = models[0]
        assert "id" in model
        assert "name" in model
        assert "pricing" in model
        assert model["id"] == "openai/gpt-4o"


@pytest.mark.asyncio
async def test_openrouter_api_get_model_pricing_validation():
    """Test get_model_pricing() response structure."""
    api = OpenRouterAPI(api_key="test-key")
    
    mock_response = Mock()
    mock_response.json = Mock(return_value={
        "data": {
            "id": "google/gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "pricing": {"prompt": "0", "completion": "0"},
            "context_window": 1000000,
        }
    })
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    
    with patch.object(api, "_get_client", return_value=mock_client):
        pricing = await api.get_model_pricing("google/gemini-1.5-flash")
        
        assert "id" in pricing
        assert "name" in pricing
        assert "pricing" in pricing
        assert "context_window" in pricing
        assert pricing["id"] == "google/gemini-1.5-flash"


@pytest.mark.asyncio
async def test_openrouter_api_multiple_api_keys():
    """Test that different API keys create different client configurations."""
    api1 = OpenRouterAPI(api_key="key-1")
    api2 = OpenRouterAPI(api_key="key-2")
    
    client1 = await api1._get_client()
    client2 = await api2._get_client()
    
    assert client1.headers["Authorization"] == "Bearer key-1"
    assert client2.headers["Authorization"] == "Bearer key-2"


@pytest.mark.asyncio
async def test_openrouter_api_is_free_model_exact_zero():
    """Test _is_free_model() with exact zero pricing."""
    api = OpenRouterAPI(api_key="test-key")
    
    model = {
        "id": "test/model",
        "pricing": {"prompt": "0", "completion": "0"},
    }
    
    assert api._is_free_model(model) is True


@pytest.mark.asyncio
async def test_openrouter_api_is_free_model_float_zero():
    """Test _is_free_model() with float zero pricing."""
    api = OpenRouterAPI(api_key="test-key")
    
    model = {
        "id": "test/model",
        "pricing": {"prompt": 0.0, "completion": 0.0},
    }
    
    assert api._is_free_model(model) is True


@pytest.mark.asyncio
async def test_openrouter_api_is_free_model_non_zero():
    """Test _is_free_model() with non-zero pricing."""
    api = OpenRouterAPI(api_key="test-key")
    
    model = {
        "id": "test/model",
        "pricing": {"prompt": "0.001", "completion": "0.002"},
    }
    
    assert api._is_free_model(model) is False


@pytest.mark.asyncio
async def test_openrouter_api_is_free_model_empty_pricing():
    """Test _is_free_model() with empty pricing dict."""
    api = OpenRouterAPI(api_key="test-key")
    
    model = {
        "id": "test/model",
        "pricing": {},
    }
    
    assert api._is_free_model(model) is True


@pytest.mark.asyncio
async def test_openrouter_api_is_free_model_none_value():
    """Test _is_free_model() with None pricing values."""
    api = OpenRouterAPI(api_key="test-key")
    
    model = {
        "id": "test/model",
        "pricing": {"prompt": None, "completion": None},
    }
    
    assert api._is_free_model(model) is False


@pytest.mark.asyncio
async def test_openrouter_api_get_free_models_alias():
    """Test that get_free_models() is an alias for get_models(free_only=True)."""
    api = OpenRouterAPI(api_key="test-key")
    
    mock_response = Mock()
    mock_response.json = Mock(return_value={
        "data": [
            {"id": "free1", "pricing": {"prompt": "0", "completion": "0"}},
            {"id": "paid1", "pricing": {"prompt": "0.1", "completion": "0.2"}},
            {"id": "free2", "pricing": {"prompt": "0", "completion": "0"}},
        ]
    })
    mock_response.raise_for_status = Mock()
    
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    
    with patch.object(api, "_get_client", return_value=mock_client):
        free_models = await api.get_free_models()
        
        assert len(free_models) == 2
        assert all(api._is_free_model(m) for m in free_models)
        assert all("free" in m["id"] for m in free_models)
