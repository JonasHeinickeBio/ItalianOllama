#!/bin/bash
set -e

# ============================================
# Neo4j Secrets (local)
# ============================================
export NEO4J_PASSWORD=$(cat /run/secrets/neo4j_password 2>/dev/null || echo "")

# ============================================
# Neo4j Aura Secrets (cloud)
# ============================================
# Check if Aura credentials exist
if [ -f /run/secrets/neo4j_aura_uri ]; then
    export NEO4J_URI=$(cat /run/secrets/neo4j_aura_uri)
    export NEO4J_USER=$(cat /run/secrets/neo4j_aura_username)
    export NEO4J_PASSWORD=$(cat /run/secrets/neo4j_aura_password)
    export NEO4J_DATABASE="neo4j"
    echo "Using Neo4j Aura: $NEO4J_URI"
else
    echo "Using local Neo4j: $NEO4J_URI"
fi

# ============================================
# Other Secrets
# ============================================
export BLABLADOR_API_KEY=$(cat /run/secrets/blablador_api_key 2>/dev/null || echo "")
export WEBUI_SECRET_KEY=$(cat /run/secrets/webui_secret_key 2>/dev/null || echo "")
export OPENWEBUI_API_KEY=$(cat /run/secrets/openwebui_api_key 2>/dev/null || echo "")

# Optional secrets
export BLABLADOR_API_URL=$(cat /run/secrets/blablador_api_url 2>/dev/null || echo "https://api.helmholtz-blablador.fz-juelich.de/v1/")
export BLABLADOR_MODEL=$(cat /run/secrets/blablador_model 2>/dev/null || echo "alias-fast")

# ============================================
# Log Startup
# ============================================
echo "Starting ItalianOllama Language Service..."
echo "Neo4j URI: $NEO4J_URI"
echo "Neo4j User: $NEO4J_USER"
echo "Ollama URL: $OLLAMA_BASE_URL"
echo "Blablador URL: $BLABLADOR_API_URL"

# Execute the original command
exec "$@"
