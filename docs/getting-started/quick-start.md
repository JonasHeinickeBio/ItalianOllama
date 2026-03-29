# Quick Start Guide

Get up and running with ItalianOllama in just a few minutes.

## TL;DR

```bash
# 1. Clone and setup
git clone https://github.com/JonasHeinickeBio/ItalianOllama.git
cd ItalianOllama

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start services
cd backend && docker compose up -d

# 4. Access the app
# Open http://localhost/chat
```

## Step-by-Step

### Step 1: Get API Credentials

You need at least one LLM provider. Options:

1. **Blablador** (Recommended - Helmholtz AI):
   - Request access at https://gitlab.jsc.fz-juelich.de/se-paper匿/llm-api
   - Get your API key

2. **Ollama** (Local):
   - Install: https://ollama.ai
   - Run: `ollama pull llama3.2`

3. **OpenAI**:
   - Get key from https://platform.openai.com

### Step 2: Start the Backend

```bash
cd backend
docker compose up -d

# Verify services are running
docker compose ps
```

Expected output:
```
NAME                IMAGE               STATUS
backend-api-1       italianollama/api   Up
backend-litellm-1   litellm/litellm     Up
backend-neo4j-1     neo4j:5             Up (healthy)
```

### Step 3: Access the Chat Interface

Open your browser to: **http://localhost/chat**

You should see:
- Sofia, your Italian tutor
- A welcome message in Italian
- A chat input box

### Step 4: Start Learning!

Try these commands:

```
Ciao! (Hello!)
Voglio imparare l'italiano. (I want to learn Italian)
Fai un test di livello. (Do a placement test)
```

## First Conversation

When you first start, the tutor will:

1. **Greet you** in Italian
2. **Assess your level** with a quick CEFR placement test
3. **Create your profile** in Neo4j
4. **Recommend exercises** based on your level

## Exercise Types

| Command | Exercise |
|---------|----------|
| `Fai vocab` | Vocabulary flashcards |
| `Fai grammatica` | Grammar drills |
| `Fai traduzione` | Translation practice |
| `Scrivi qualcosa` | Free writing with feedback |
| `Fai un test` | Exam preparation |

## Accessing the Dashboard

For analytics and progress tracking, visit:

**http://localhost/dashboard**

Features:
- CEFR level progress
- Vocabulary insights
- Grammar error patterns
- Knowledge graph visualization
- Test readiness scores

## Common Commands

```
# Get help
Aiuto! / Help!

# Change level
Voglio cambiare livello / I want to change level

# Practice specific topic
Fai esercizi sui verbi / Practice verbs
Fai vocab su cibo / Vocabulary about food

# Check progress
Mostra il mio progresso / Show my progress
```

## Next Steps

- [Installation Guide](installation.md) - Detailed setup
- [Architecture Overview](../architecture/overview.md) - Understand the system
- [Features Guide](../features/chat-interface.md) - Explore all features
