# Nginx Configuration Guide

This guide covers the Nginx reverse proxy configuration for ItalianOllama.

## Overview

Nginx serves as the single entry point for all services, handling:
- HTTP/HTTPS routing
- WebSocket support for real-time chat
- Load balancing
- SSL termination
- Request timeouts

## Configuration File

### Complete Configuration

```nginx
# frontend/nginx.conf
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    # Upstream definitions
    upstream chainlit_backend {
        least_conn;
        server chainlit:8000;
    }
    
    upstream streamlit_backend {
        least_conn;
        server streamlit:8501;
    }
    
    upstream api_backend {
        least_conn;
        server api:8000;
    }
    
    upstream litellm_backend {
        least_conn;
        server litellm:4000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        client_max_body_size 100M;
        
        # Long timeouts for streaming
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        
        # Health check endpoint
        location /health {
            proxy_pass http://api_backend/health;
            access_log off;
        }
        
        # Chainlit WebSocket route
        location /chat/ {
            proxy_pass http://chainlit_backend/;
            
            proxy_http_version 1.1;
            
            # WebSocket headers
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            
            # Pass headers
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket specific
            proxy_read_timeout 300s;
        }
        
        # Streamlit route
        location /dashboard/ {
            proxy_pass http://streamlit_backend/;
            
            proxy_http_version 1.1;
            
            # Streamlit needs this for base path
            proxy_set_header X-Script-Name /dashboard;
            
            # Pass headers
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # API routes
        location /api/ {
            proxy_pass http://api_backend/;
            
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # LiteLLM route (internal)
        location /llm/ {
            proxy_pass http://litellm_backend/;
            
            proxy_http_version 1.1;
            
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        # Redirect root to chat
        location = / {
            return 301 /chat/;
        }
        
        # Deny access to hidden files
        location ~ /\. {
            deny all;
            access_log off;
            log_not_found off;
        }
    }
}
```

## SSL Configuration

### With Let's Encrypt

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # ... rest of config
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## WebSocket Support

### Key Configuration

```nginx
location /chat/ {
    proxy_pass http://chainlit_backend/;
    
    # Required for WebSocket
    proxy_http_version 1.1;
    
    # WebSocket upgrade headers
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    
    # Prevent connection timeout
    proxy_read_timeout 300s;
}
```

### Verify WebSocket

```bash
# Test WebSocket connection
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Sec-WebSocket-Key: $(echo -n 'random' | base64)" \
  http://localhost/chat/
```

## Timeout Configuration

### Why 300 Seconds?

Streaming LLM responses can take a long time. Configuration:

```nginx
# Prevent premature timeout
proxy_read_timeout 300s;    # Wait for response
proxy_connect_timeout 300s; # Connection establishment
proxy_send_timeout 300s;    # Sending to upstream
```

### Chunked Transfer

```nginx
# Enable chunked transfer encoding
chunked_transfer_encoding off;
```

## Load Balancing

### Multiple Backends

```nginx
upstream chainlit_backend {
    least_conn;  # Route to server with fewest connections
    server chainlit1:8000 weight=3;
    server chainlit2:8000 weight=2;
    server chainlit3:8000;
    
    # Health check
    server chainlit1:8000 down;
}
```

### Health Checks

```nginx
upstream api_backend {
    server api:8000 max_fails=3 fail_timeout=30s;
}
```

## Caching

### Static Assets

```nginx
location /static/ {
    proxy_pass http://streamlit_backend/static/;
    
    # Cache static files
    expires 1d;
    add_header Cache-Control "public, immutable";
}
```

## Security Headers

### Recommended Headers

```nginx
server {
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Content Security Policy
    # add_header Content-Security-Policy "..." always;
}
```

## Rate Limiting

### Basic Rate Limit

```nginx
http {
    # Define limit zone
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=api_limit burst=20 nodelay;
            proxy_pass http://api_backend/;
        }
    }
}
```

## Logging

### Access Log Format

```nginx
log_format detailed '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" '
                    '"$upstream_addr" "$upstream_status" '
                    '$request_time';
```

### Conditional Logging

```nginx
# Disable access log for health checks
location /health {
    access_log off;
    proxy_pass http://api_backend/health;
}
```

## Troubleshooting

### Test Configuration

```bash
# Test nginx config
docker compose exec nginx nginx -t

# Reload after changes
docker compose exec nginx nginx -s reload
```

### Debug Connection

```bash
# Check upstream connectivity
docker compose exec nginx curl -v http://chainlit:8000
docker compose exec nginx curl -v http://streamlit:8501
docker compose exec nginx curl -v http://api:8000/health
```

### View Logs

```bash
# Nginx error log
docker compose logs nginx | grep error

# Access log (live)
docker compose logs -f nginx | grep "/chat/"
```

## Related Documentation

- [Production Deployment](production.md)
- [Docker Deployment](docker.md)
- [Troubleshooting](../troubleshooting/common-issues.md)
