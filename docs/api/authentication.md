# Authentication Guide

This guide covers authentication and authorization in ItalianOllama.

## Overview

ItalianOllama uses JWT (JSON Web Tokens) for authentication between:
- Chainlit frontend and backend
- Streamlit frontend and backend
- Single Sign-On (SSO) between frontends

## Authentication Flow

### Chainlit Authentication

```
User → Chainlit OAuth → Google → Callback → JWT → Session
```

### Streamlit Authentication

```
User clicks dashboard link → Extract JWT → Validate → Session
```

### SSO Flow

```
1. User logs in to Chainlit
2. Chainlit creates JWT with student_id
3. Dashboard link includes JWT
4. User clicks link → Streamlit validates JWT
5. Session created without additional login
```

## JWT Tokens

### Token Structure

```python
{
    "student_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "name": "John Doe",
    "exp": 1704067200,  # Expiration timestamp
    "iat": 1701388800   # Issued at timestamp
}
```

### Token Generation

```python
import jwt
from datetime import datetime, timedelta

def create_token(student_id: str, email: str, name: str, secret: str) -> str:
    """Create JWT token for student."""
    now = datetime.utcnow()
    payload = {
        "student_id": student_id,
        "email": email,
        "name": name,
        "exp": now + timedelta(hours=4),  # 4-hour expiration
        "iat": now
    }
    return jwt.encode(payload, secret, algorithm="HS256")
```

### Token Validation

```python
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

def validate_token(token: str, secret: str) -> dict:
    """Validate JWT token."""
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    except InvalidTokenError:
        raise ValueError("Invalid token")
```

## AUTH_SECRET

### Generation

```bash
# Generate secure secret
export AUTH_SECRET=$(openssl rand -hex 32)
echo $AUTH_SECRET
```

### Configuration

```bash
# .env
AUTH_SECRET=your_generated_secret_here
```

### Docker Configuration

```yaml
# docker-compose.yml
services:
  chainlit:
    environment:
      - AUTH_SECRET=${AUTH_SECRET}
  
  streamlit:
    environment:
      - AUTH_SECRET=${AUTH_SECRET}
```

## Chainlit Authentication

### OAuth2 Setup

```python
# frontend/chainlit/auth/oauth.py
import chainlit as cl
from authlib.integrations.requests_client import OAuth2Session

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

@cl.oauth_callback
def oauth_callback(provider: str, token: dict, default_api: bool):
    """Handle OAuth callback from Google."""
    if provider == "google":
        # Get user info
        user_info = get_google_user_info(token["access_token"])
        
        # Create or update student in Neo4j
        student = neo4j_client.get_or_create_student(
            email=user_info["email"],
            name=user_info["name"]
        )
        
        # Create JWT for dashboard
        dashboard_token = create_token(
            student_id=student["student_id"],
            email=student["email"],
            name=student["name"],
            secret=AUTH_SECRET
        )
        
        return student
    
    return None
```

### Dev Mode (No OAuth)

```bash
# Disable OAuth for development
export DISABLE_OAUTH=true

# Or in .env
DISABLE_OAUTH=true
```

## Streamlit Authentication

### Session Validation

```python
# frontend/streamlit/auth/session.py
import streamlit as st
import jwt

def get_current_student() -> dict | None:
    """Get current student from session."""
    # Check session first
    if "student" in st.session_state:
        return st.session_state["student"]
    
    # Check for JWT in URL
    token = get_token_from_url()
    if token:
        try:
            payload = jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
            
            # Validate with Neo4j
            student = neo4j_client.get_student(payload["student_id"])
            if student:
                st.session_state["student"] = student
                return student
        except:
            pass
    
    return None

def require_student() -> dict:
    """Require authenticated student or redirect."""
    student = get_current_student()
    
    if not student:
        st.error("Please log in through the chat interface")
        st.stop()
    
    return student
```

### Dashboard Link

```python
# In Chainlit greeting
def get_greeting(student: dict) -> str:
    """Generate greeting with dashboard link."""
    token = create_token(
        student_id=student["student_id"],
        email=student["email"],
        name=student["name"],
        secret=AUTH_SECRET
    )
    
    dashboard_url = f"http://localhost/dashboard/?token={token}"
    
    return f"""
    Ciao {student['name']}! 👋
    
    Il tuo livello attuale: **{student['cefr_level']}**
    
    [📊 Visualizza Dashboard]({dashboard_url})
    """
```

## 3-Layer Auth (Streamlit)

### Layer 1: JWT Validation

```python
def validate_jwt(token: str) -> dict | None:
    """Layer 1: Validate JWT signature and expiration."""
    try:
        return jwt.decode(token, AUTH_SECRET, algorithms=["HS256"])
    except:
        return None
```

### Layer 2: Session Cache

```python
def get_session(student_id: str) -> dict | None:
    """Layer 2: Check session cache."""
    if f"session_{student_id}" in st.session_state:
        return st.session_state[f"session_{student_id}"]
    return None
```

### Layer 3: Email Gate

```python
def verify_student_email(student_id: str) -> bool:
    """Layer 3: Verify student exists in database."""
    student = neo4j_client.get_student(student_id)
    return student is not None
```

## Security Best Practices

### Token Security

```python
# Use strong algorithm
jwt.encode(payload, secret, algorithm="HS256")

# Set appropriate expiration
{"exp": datetime.utcnow() + timedelta(hours=4)}

# Never expose secrets in code
# Use environment variables
AUTH_SECRET = os.environ["AUTH_SECRET"]
```

### HTTPS Required

In production, always use HTTPS:

```nginx
# Nginx SSL configuration
server {
    listen 443 ssl;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ...
}
```

### Token Refresh

```python
def refresh_token_if_needed(token: str) -> str:
    """Refresh token if expiring soon."""
    payload = jwt.decode(token, options={"verify_signature": False})
    exp = payload.get("exp")
    
    # Refresh if less than 30 minutes left
    if exp - time.time() < 1800:
        return create_new_token(payload)
    
    return token
```

## Testing Authentication

### Test Token Generation

```python
# Test token creation
token = create_token("test-123", "test@example.com", "Test User", "secret")
print(f"Token: {token}")

# Test validation
payload = validate_token(token, "secret")
print(f"Payload: {payload}")
```

### Test Auth Flow

```bash
# Create test student
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "email": "test@example.com"}'

# Use the token
TOKEN=$(python3 -c "import jwt; print(jwt.encode({'student_id': '...'}, 'secret', algorithm='HS256'))")
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/students/...
```

## Troubleshooting

### Invalid Token Error

```python
# Check token format
print(f"Token: {token[:50]}...")

# Verify secret matches
print(f"Expected: {AUTH_SECRET}")
```

### Token Expired Error

```python
# Check expiration
payload = jwt.decode(token, options={"verify_signature": False})
print(f"Expires: {datetime.fromtimestamp(payload['exp'])}")
print(f"Now: {datetime.utcnow()}")
```

### Session Not Persisting

```python
# Check session state
print(st.session_state)

# Verify AUTH_SECRET is set
import os
print(os.environ.get("AUTH_SECRET"))
```

## Related Documentation

- [API Endpoints](endpoints.md)
- [Frontend Architecture](../architecture/frontend.md)
- [Production Deployment](../deployment/production.md)
