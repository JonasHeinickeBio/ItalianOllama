#!/bin/bash
# ============================================
# ItalianOllama - Easy Start Script
# ============================================
#
# Usage:
#   ./start.sh aura          # Neo4j Aura + Ollama
#   ./start.sh aura-blab     # Neo4j Aura + Blablador (no Ollama container)
#   ./start.sh local         # Local Neo4j + Ollama
#   ./start.sh minimal       # API + Ollama only
#   ./start.sh webui         # Full stack with WebUI
#   ./start.sh stop          # Stop all containers
#   ./start.sh logs          # View logs
#
# ============================================

set -e

COMPOSE_FILE="docker/docker-compose.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        log_warn ".env file not found. Creating from template..."
        if [ -f ".env.example" ]; then
            cp .env.example .env
            log_info ".env created. Please edit it with your settings."
        else
            log_warn "No .env.example found. You'll need to set environment variables."
        fi
    fi
}

# Start with aura profile
aura() {
    log_info "Starting with Neo4j Aura (cloud)..."
    check_env
    docker compose --profile aura -f $COMPOSE_FILE up -d
    log_info "Services started!"
    log_info "API: http://localhost:8000"
    log_info "Neo4j: Your Aura instance (check console.neo4j.io)"
}

# Start with aura + blablador (no ollama container)
aura_blab() {
    log_info "Starting with Neo4j Aura + Blablador..."
    check_env

    # Check for blablador config
    if [ ! -f "secrets/blablador_api_key.txt" ]; then
        log_error "Blablador API key not found!"
        echo "  Create secrets/blablador_api_key.txt with your API key"
        exit 1
    fi

    # Remove ollama service, use aura
    docker compose --profile aura -f $COMPOSE_FILE up -d --remove-orphans
    docker compose stop ollama 2>/dev/null || true

    log_info "Services started!"
    log_info "API: http://localhost:8000"
    log_info "LLM: Blablador (external)"
}

# Start with local neo4j
local() {
    log_info "Starting with local Neo4j..."
    check_env
    docker compose --profile local -f $COMPOSE_FILE up -d
    log_info "Services started!"
    log_info "API: http://localhost:8000"
    log_info "Neo4j Browser: http://localhost:7474"
    log_info "Neo4j Bolt: localhost:7687"
}

# Minimal: API + Ollama only
minimal() {
    log_info "Starting minimal setup (API + Ollama)..."
    check_env
    docker compose --profile minimal -f $COMPOSE_FILE up -d
    log_info "Services started!"
    log_info "API: http://localhost:8000"
    log_info "Ollama: http://localhost:11434"
}

# Full stack with WebUI
webui() {
    log_info "Starting with WebUI..."
    check_env
    docker compose --profile webui -f $COMPOSE_FILE up -d
    log_info "Services started!"
    log_info "API: http://localhost:8000"
    log_info "WebUI: http://localhost:8080"
}

# External Ollama (on host or elsewhere)
external_ollama() {
    log_info "Starting with external Ollama..."
    check_env

    export OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://host.docker.internal:11434}"
    log_info "Using Ollama at: $OLLAMA_BASE_URL"

    # Start without ollama container
    docker compose -f $COMPOSE_FILE up -d --no-attach ollama
    log_info "Services started (without local Ollama container)!"
}

# Stop all services
stop() {
    log_info "Stopping all services..."
    docker compose -f $COMPOSE_FILE down
    log_info "All services stopped."
}

# View logs
logs() {
    docker compose -f $COMPOSE_FILE logs -f
}

# Show status
status() {
    docker compose -f $COMPOSE_FILE ps
}

# Show help
help() {
    echo ""
    echo "ItalianOllama - Easy Start Script"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  aura           Start with Neo4j Aura (cloud) + Ollama"
    echo "  aura-blab      Start with Neo4j Aura + Blablador (no Ollama)"
    echo "  local          Start with local Neo4j + Ollama"
    echo "  minimal        Start minimal (API + Ollama only)"
    echo "  webui          Start with WebUI (full stack)"
    echo "  external       Start with external Ollama (no container)"
    echo "  stop           Stop all services"
    echo "  logs           View logs"
    echo "  status         Show service status"
    echo "  help           Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 aura                    # Use Aura + local Ollama"
    echo "  $0 aura-blab               # Use Aura + Blablador"
    echo "  OLLAMA_BASE_URL=http://localhost:11434 $0 external"
    echo ""
}

# Main
case "${1:-help}" in
    aura)
        aura
        ;;
    aura-blab)
        aura_blab
        ;;
    local)
        local
        ;;
    minimal)
        minimal
        ;;
    webui)
        webui
        ;;
    external)
        external_ollama
        ;;
    stop|down)
        stop
        ;;
    logs)
        logs
        ;;
    status|ps)
        status
        ;;
    help|--help|-h)
        help
        ;;
    *)
        log_error "Unknown command: $1"
        help
        exit 1
        ;;
esac
