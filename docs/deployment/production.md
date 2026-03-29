# Production Deployment Guide

This guide covers deploying ItalianOllama in a production environment.

## Overview

The production stack includes:
- **Chainlit** - Chat interface (port 8000)
- **Streamlit** - Analytics dashboard (port 8501)
- **FastAPI** - Backend API (port 8000)
- **LiteLLM** - LLM proxy (port 4000)
- **Neo4j Aura** - Cloud database
- **Nginx** - Reverse proxy with WebSocket support

## Prerequisites

### Required Accounts

| Service | Purpose | Sign Up |
|---------|---------|---------|
| Neo4j Aura | Database | https://neo4j.com/cloud/ |
| Blablador | LLM (recommended) | Contact Helmholtz |
| (Optional) GitHub | Repository | https://github.com/ |

### Server Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Storage | 20 GB | 50+ GB |
| Docker | 20.10+ | Latest |

## Step-by-Step Deployment

### 1. Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. Clone Repository

```bash
git clone https://github.com/JonasHeinickeBio/ItalianOllama.git
cd ItalianOllama
```

### 3. Configure Environment

```bash
# Create production .env file
cat > .env << 'EOF'
# Neo4j Aura (Cloud)
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=your_username
NEO4J_PASSWORD=your_secure_password
NEO4J_DATABASE=neo4j
USE_AURA=true

# Blablador (LLM)
BLABLADOR_API_URL=https://api.helmholtz-blablador.fz-juelich.de/v1/
BLABLADOR_API_KEY=your_api_key
BLABLADOR_MODEL=alias-fast

# LiteLLM
LITELLM_BASE_URL=http://litellm:4000
LITELLM_MODEL=tutor
LITELLM_API_KEY=dummy

# Authentication
AUTH_SECRET=$(openssl rand -hex 32)

# Logging
LOG_LEVEL=INFO
EOF
```

### 4. Generate AUTH_SECRET

```bash
# Generate secure JWT secret
export AUTH_SECRET=$(openssl rand -hex 32)
echo $AUTH_SECRET
# Save this value - you'll need it for the .env file
```

### 5. Start Production Stack

```bash
cd frontend
docker compose up -d

# Verify all services
docker compose ps
```

### 6. Verify Deployment

```bash
# Check health endpoint
curl https://your-domain.com/health

# Check Nginx status
docker compose logs nginx
```

## SSL/HTTPS Configuration

### Using Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Nginx SSL Config

```nginx
# frontend/nginx-ssl.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    
    # ... rest of config
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## Security Considerations

### Firewall Configuration

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Docker Security

```bash
# Use non-root users in Dockerfiles
USER appuser

# Limit container capabilities
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE ...

# Enable Docker content trust
export DOCKER_CONTENT_TRUST=1
```

### Secrets Management

```bash
# Use Docker secrets in production
echo "your_secret" | docker secret create neo4j_password -

# Or use a secrets manager
# AWS Secrets Manager, HashiCorp Vault, etc.
```

## Monitoring

### Health Checks

```bash
# Add to crontab
*/5 * * * * curl -f https://your-domain.com/health || alert
```

### Logging

```bash
# View logs
docker compose logs -f --tail=100

# Use Loggly, Papertrail, or ELK stack for centralized logging
```

### Metrics

```bash
# Install Prometheus node exporter
docker run -d \
  --name node-exporter \
  -p 9100:9100 \
  --net italianollama_frontend \
  prom/node-exporter
```

## Backup and Recovery

### Neo4j Aura Backups

Neo4j Aura provides automatic backups. To restore:

```bash
# Contact Neo4j support or use Aura console
# For manual backup:
docker exec neo4j cypher-shell -u neo4j -p password \
  "CALL apoc.export.json.all('backup.json', {})"
```

### Application Backups

```bash
# Backup .env file (secure location)
cp .env ~/.backup/italianollama.env

# Backup Nginx config
cp frontend/nginx.conf ~/.backup/nginx.conf
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      replicas: 2
  
  chainlit:
    deploy:
      replicas: 2
```

### Load Balancing

Use Nginx upstream with multiple backend instances:

```nginx
upstream api_servers {
    server api:8000;
    server api2:8000;
}
```

## Troubleshooting Production

### Check Service Health

```bash
# All services
docker compose ps

# API
curl http://localhost:8000/health

# LiteLLM
curl http://localhost:4000/health

# Neo4j
docker exec neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

### Common Issues

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check Nginx and backend logs |
| WebSocket failed | Verify Nginx WebSocket headers |
| Database connection | Check NEO4J_URI and credentials |
| LLM timeout | Increase proxy_read_timeout |

## Related Documentation

- [Docker Deployment](docker.md)
- [Nginx Configuration](nginx.md)
- [Troubleshooting](../troubleshooting/common-issues.md)
