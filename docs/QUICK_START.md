"""
QUICK START GUIDE - Enhanced Backend & Streamlit

Getting Started in 5 Minutes
"""

# ============================================================================
# QUICK START (5 MINUTES)
# ============================================================================

## 1. Verify Prerequisites

python --version  # Python 3.10+
pip list | grep -E "fastapi|streamlit|neo4j"

## 2. Install Dependencies (if needed)

cd backend
pip install -r requirements.txt

## 3. Configure Environment

cat > .env << 'EOF'
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

LITELLM_BASE_URL=http://localhost:4000
LITELLM_API_KEY=dummy

AUTH_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=4

CORS_ORIGINS=http://localhost:8501,http://localhost:8000,http://localhost:3000
BACKEND_URL=http://localhost:8000

LOG_LEVEL=DEBUG
EOF

## 4. Load Demo Data

# Option A: Using Neo4j Browser (easiest)
# 1. Open http://localhost:7474 (Neo4j Browser)
# 2. Login with neo4j/password
# 3. Copy-paste contents of /neo4j/demo_student_complete_setup.cypher
# 4. Execute (Ctrl+Enter)
# 5. Should see: "Maria Doe created with 2 sessions, 12 attempts"

# Option B: Using Command Line
cypher-shell -u neo4j -p password < neo4j/demo_student_complete_setup.cypher

# Option C: Using Python
python << 'PYEND'
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

with open("neo4j/demo_student_complete_setup.cypher") as f:
    cypher_content = f.read()

with driver.session() as session:
    for statement in cypher_content.split(";"):
        if statement.strip():
            session.run(statement)

print("✅ Demo data loaded!")
PYEND

## 5. Start FastAPI Backend (Enhanced)

# Option A: Direct Python
cd src
python -m uvicorn italianollama.api.main_enhanced:app --reload --port 8000

# Option B: Using Docker
cd backend
docker-compose -f docker-compose.yml up fastapi

# You should see:
# Uvicorn running on http://127.0.0.1:8000
# Visit http://localhost:8000/docs for Swagger UI

## 6. Start Streamlit Frontend (Enhanced)

# In another terminal:
cd src
streamlit run italianollama/frontend/streamlit/app_enhanced.py

# You should see:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501

## 7. Test the System

# Browser: http://localhost:8501

# Login as:
# Student ID: maria_doe_001

# You should see:
# - Dashboard with 1050 XP, 7 day streak
# - Learning velocity: ~11 XP/day
# - Skills breakdown (vocabulary, grammar)
# - 3 vocabulary entries
# - Recommended next module

## 8. Verify Backend Endpoints

# In another terminal:
curl http://localhost:8000/health | jq

# Should show:
# {
#   "status": "ok",
#   "neo4j": "connected",
#   "litellm": "unreachable"  (OK if litellm not running)
# }

# Test token generation:
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"student_id": "test_user"}' | jq

# Should show:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer",
#   "expires_in": 14400
# }

# ============================================================================
# TESTING NEW FEATURES
# ============================================================================

## Test 1: Student Creation & Profile

STUDENT_ID="test_user_123"

TOKEN=$(curl -s -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT_ID\"}" | jq -r '.access_token')

echo "Token: $TOKEN"

# Create student
curl -X POST http://localhost:8000/students \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT_ID\", \"name\": \"Test User\"}" | jq

# Get student profile
curl http://localhost:8000/students/$STUDENT_ID \
  -H "Authorization: Bearer $TOKEN" | jq

## Test 2: Session & Exercise Attempt

# Create session
RESPONSE=$(curl -s -X POST http://localhost:8000/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT_ID\", \"topic\": \"greetings\", \"exercise_type\": \"flashcard\"}")

SESSION_ID=$(echo $RESPONSE | jq -r '.session_id')
echo "Session ID: $SESSION_ID"

# Record exercise attempt
curl -X POST http://localhost:8000/attempts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"student_id\": \"$STUDENT_ID\",
    \"exercise_template_id\": \"exercise_001\",
    \"exercise_type\": \"flashcard\",
    \"correct\": true,
    \"confidence\": 4,
    \"duration_seconds\": 12,
    \"hints_used\": 0,
    \"retries\": 0
  }" | jq

# End session
curl -X POST http://localhost:8000/sessions/$SESSION_ID/end \
  -H "Authorization: Bearer $TOKEN" | jq

## Test 3: Vocabulary Management

# Add vocabulary
VOCAB=$(curl -s -X POST http://localhost:8000/vocabulary \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"student_id\": \"$STUDENT_ID\",
    \"italian_word\": \"gatto\",
    \"english_translation\": \"cat\",
    \"part_of_speech\": \"noun\",
    \"cefr_level\": \"A1\",
    \"topic\": \"animals\"
  }")

VOCAB_ID=$(echo $VOCAB | jq -r '.vocabulary_id')
echo "Vocabulary ID: $VOCAB_ID"

# Get vocabulary
curl http://localhost:8000/vocabulary/$STUDENT_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# Update vocabulary confidence (spaced repetition)
curl -X POST http://localhost:8000/vocabulary/$VOCAB_ID/confidence \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "confidence=5" | jq

## Test 4: Analytics

# Learning velocity
curl http://localhost:8000/analytics/velocity/$STUDENT_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# Skill breakdown
curl http://localhost:8000/analytics/skills/$STUDENT_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# Common errors
curl http://localhost:8000/analytics/errors/$STUDENT_ID \
  -H "Authorization: Bearer $TOKEN" | jq

## Test 5: Recommendations

# Next module
curl http://localhost:8000/recommendations/next-module/$STUDENT_ID \
  -H "Authorization: Bearer $TOKEN" | jq

# ============================================================================
# MIGRATION: OLD MAIN.PY → NEW MAIN_ENHANCED.PY
# ============================================================================

## Option 1: Parallel Deployment

# Terminal 1: Old backend (port 8000)
cd src
python -m uvicorn italianollama.api.main:app --port 8000

# Terminal 2: New backend (port 8001)
cd src
python -m uvicorn italianollama.api.main_enhanced:app --port 8001

# Terminal 3: Streamlit (points to port 8001)
BACKEND_URL=http://localhost:8001 streamlit run app_enhanced.py

## Option 2: Direct Replacement

# 1. Backup old main.py
cp src/italianollama/api/main.py src/italianollama/api/main.py.bak

# 2. Copy new main_enhanced.py
cp src/italianollama/api/main_enhanced.py src/italianollama/api/main.py

# 3. Restart backend
pkill -f "python -m uvicorn"
cd src
python -m uvicorn italianollama.api.main:app --port 8000

# 4. Update Streamlit to use app_enhanced.py
streamlit run src/italianollama/frontend/streamlit/app_enhanced.py

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

## Problem: "ConnectionError: Could not connect to backend"

# Check if FastAPI is running:
curl http://localhost:8000/health

# If not:
cd src
python -m uvicorn italianollama.api.main_enhanced:app --port 8000

## Problem: "neo4j: [CONNECTION_FAILURE]"

# Check Neo4j is running:
curl http://localhost:7474 -u neo4j:password

# Or use neo4j-admin:
neo4j-admin server status

# Or restart Neo4j:
docker-compose -f backend/docker-compose.yml restart neo4j

## Problem: "ValidationError: student_id is required"

# Make sure request body has correct format:
curl -X POST http://localhost:8000/students \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"student_id": "user_123", "name": "Full Name"}'  # ✓ Correct

## Problem: "token verification failed"

# Token is expired or invalid. Re-login:
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"student_id": "user_123", "expires_in_hours": 4}'

# Use the new token in Authorization header:
curl http://localhost:8000/students/user_123 \
  -H "Authorization: Bearer <NEW_TOKEN>"

## Problem: Streamlit cache getting stale data

# Clear Streamlit cache:
rm -rf ~/.streamlit/cache

# Or restart Streamlit:
pkill -f streamlit
streamlit run src/italianollama/frontend/streamlit/app_enhanced.py

# ============================================================================
# NEXT STEPS AFTER QUICK START
# ============================================================================

1. Load production data:
   - Replace demo_student_complete_setup.cypher with your data
   - Or write Python script to bulk import from CSV/JSON

2. Set up monitoring:
   - Enable Sentry for error tracking (add SENTRY_DSN to .env)
   - Set up Prometheus for metrics collection
   - View logs with: docker-compose logs -f fastapi

3. Customize for your needs:
   - Update rate limits in middleware/rate_limit.py
   - Add new endpoints to main_enhanced.py
   - Add new Neo4j methods to neo4j_client_enhanced.py
   - Extend Streamlit UI in app_enhanced.py

4. Deploy to production:
   - Use Docker compose file in backend/
   - Set environment variables in .env (or secrets manager)
   - Use Gunicorn for FastAPI: gunicorn -w 4 -k uvicorn.workers.UvicornWorker
   - Use Streamlit Cloud or self-host via Docker

5. Integrate LiteLLM:
   - Start LiteLLM service: litellm --model ollama/neural-chat
   - Update LITELLM_BASE_URL in .env
   - Health check should show litellm: connected

# ============================================================================
"""

if __name__ == "__main__":
    print(__doc__)
