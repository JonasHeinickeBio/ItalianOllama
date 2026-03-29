"""Tests for italianollama.api.middleware.errors module."""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from italianollama.api.middleware.errors import setup_error_handlers
from italianollama.api.exceptions import (
    AuthenticationError,
    NotFoundError,
    TutorException,
)


@pytest.fixture()
def app_with_handlers():
    app = FastAPI()
    setup_error_handlers(app)

    @app.get("/tutor-error")
    async def tutor_error():
        raise TutorException(status_code=400, detail="test error", error_type="test_error")

    @app.get("/not-found")
    async def not_found():
        raise NotFoundError(resource="Student")

    @app.get("/auth-error")
    async def auth_error():
        raise AuthenticationError()

    @app.get("/generic-error")
    async def generic_error():
        raise RuntimeError("unexpected crash")

    @app.get("/ok")
    async def ok():
        return {"status": "ok"}

    return app


@pytest.fixture()
def client(app_with_handlers):
    return TestClient(app_with_handlers, raise_server_exceptions=False)


class TestTutorExceptionHandler:
    def test_tutor_exception_returns_json(self, client):
        resp = client.get("/tutor-error")
        assert resp.status_code == 400
        data = resp.json()
        assert data["error"] == "test_error"
        assert data["message"] == "test error"
        assert "trace_id" in data

    def test_not_found_error(self, client):
        resp = client.get("/not-found")
        assert resp.status_code == 404

    def test_auth_error(self, client):
        resp = client.get("/auth-error")
        assert resp.status_code == 401


class TestGenericExceptionHandler:
    def test_generic_exception_returns_500(self, client):
        resp = client.get("/generic-error")
        assert resp.status_code == 500
        data = resp.json()
        assert "error" in data or "message" in data

    def test_ok_endpoint_unaffected(self, client):
        resp = client.get("/ok")
        assert resp.status_code == 200


class TestValidationErrorHandler:
    def test_pydantic_validation_error(self):
        app = FastAPI()
        setup_error_handlers(app)

        class Model(BaseModel):
            name: str
            age: int

        @app.post("/validate")
        async def validate(data: Model):
            return data

        test_client = TestClient(app, raise_server_exceptions=False)
        resp = test_client.post("/validate", json={"name": "test", "age": "not-an-int"})
        # FastAPI handles this before our handler for request body validation
        assert resp.status_code in (400, 422)

    def test_not_found_returns_json(self):
        app = FastAPI()
        setup_error_handlers(app)

        @app.get("/resource")
        async def resource():
            raise NotFoundError(resource="Item")

        test_client = TestClient(app, raise_server_exceptions=False)
        resp = test_client.get("/resource")
        assert resp.status_code == 404
        data = resp.json()
        assert data["error"] == "not_found_error"

    def test_pydantic_validation_error_raised_manually(self):
        """Test the Pydantic ValidationError handler with manually raised error."""
        from pydantic import BaseModel as PM

        app = FastAPI()
        setup_error_handlers(app)

        class InnerModel(PM):
            age: int

        @app.get("/manual-validate")
        async def manual_validate():
            InnerModel(age="not-an-int")  # type: ignore
            return {}

        test_client = TestClient(app, raise_server_exceptions=False)
        resp = test_client.get("/manual-validate")
        # Our handler returns 400
        assert resp.status_code == 400
