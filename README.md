# ItalianOllama - AI-Powered Italian Tutor 🇮🇹

> Learn Italian with Sofia, your intelligent tutor powered by LangGraph, Neo4j, and LiteLLM.

## Overview

ItalianOllama is a production-ready language learning platform that combines conversational AI with a structured, data-driven approach to progress. Sofia, your AI tutor, adapts to your CEFR level and learning goals, providing real-time feedback and tracking your mastery in a Neo4j knowledge graph.

## The 7-Step Student Experience

1.  **Welcome**: Sofia greets you and explains the 2-minute level finding process.
2.  **Placement Test**: Adaptive quiz (A1-C2) to find your starting point.
3.  **Goal Setting**: Choose between Travel, Professional, Exam Prep, or Conversation.
4.  **Learning Session**: Warm-up conversation, vocabulary flashcards, and grammar focus.
5.  **Silent Feedback**: Sofia logs errors during conversation for later review.
6.  **Session Summary**: Instant feedback with score badges and streak counters.
7.  **Dashboard**: Track your progress via a multi-page Streamlit analytics suite.

## Quick Start

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Neo4j (Local or Aura)
- LLM API (Blablador, OpenAI, or Ollama)

### 2. Setup
```bash
git clone https://github.com/JonasHeinickeBio/ItalianOllama.git
cd ItalianOllama
cp .env.example .env  # Add your API keys and Neo4j credentials
```

### 3. Run with Docker
```bash
cd backend
docker compose up -d
```

### 4. Run Locally (Development)
**Terminal 1 (Backend API):**
```bash
poetry run uvicorn src.italianollama.api.main:app --port 8000
```
**Terminal 2 (Chat Interface):**
```bash
poetry run chainlit run src/italianollama/frontend/chainlit_app.py --port 8501
```
**Terminal 3 (Dashboard):**
```bash
export CHAINLIT_URL="http://localhost:8501"
poetry run streamlit run src/italianollama/frontend/streamlit/app_enhanced.py --server.port 8502
```

## Dashboard Features

- **💬 Chat**: Real-time conversation with Sofia.
- **📊 Progress**: KPI metrics and learning history.
- **📚 Vocabulary**: Confidence heatmap of learned words with spaced repetition.
- **✏️ Grammar**: Detailed error tracking with book-rule explanations.
- **🕸️ Knowledge Graph**: Interactive view of your personal learning network.
- **🎯 Test Readiness**: Skill radar charts for CEFR exam prep.
- **📝 Placement Test**: Interactive CEFR A1-C1 assessment with Neo4j persistence.
- **🎨 Professional Styling**: Custom CSS themes, card-based layouts, consistent theming.

## Documentation

For detailed technical specifications, architecture diagrams, and the development roadmap, see [DEVELOPMENT.md](./DEVELOPMENT.md).

## License
MIT License - see [LICENSE](./LICENSE) file.
