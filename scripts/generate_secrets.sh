#!/bin/bash
# Generate secure secrets for Docker deployment

set -e

SECRETS_DIR="./secrets"

# Create secrets directory
mkdir -p "$SECRETS_DIR"

echo "📝 Generating secure secrets for Italian Tutor..."
echo ""

# Function to generate random string
gen_secret() {
    openssl rand -base64 32
}

# Function to create secret file if it doesn't exist
create_secret() {
    local name=$1
    local file="$SECRETS_DIR/$name.txt"

    if [ -f "$file" ]; then
        echo "⚠️  $file already exists, skipping..."
    else
        echo "✓ Generating $name..."
        gen_secret > "$file"
        chmod 600 "$file"
    fi
}

# Generate all required secrets
create_secret "neo4j_password"
create_secret "auth_secret_key"
create_secret "litellm_api_key"
create_secret "litellm_salt_key"
create_secret "webui_secret_key"

echo ""
echo "✅ Secrets generated successfully!"
echo ""
echo "📁 Location: $SECRETS_DIR/"
echo "  - neo4j_password.txt"
echo "  - auth_secret_key.txt"
echo "  - litellm_api_key.txt"
echo "  - litellm_salt_key.txt"
echo "  - webui_secret_key.txt"
echo ""
echo "🔒 Permissions: 600 (read/write for owner only)"
echo ""
echo "⚠️  IMPORTANT:"
echo "   1. Store these secrets securely (backup/version control)"
echo "   2. Use Docker Secrets in production (Swarm/K8s)"
echo "   3. Rotate secrets regularly"
echo "   4. Add secrets/ to .gitignore"
echo ""
