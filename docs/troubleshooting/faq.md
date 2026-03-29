# Frequently Asked Questions

## General Questions

### What is ItalianOllama?

ItalianOllama is an AI-powered Italian language learning application that provides personalized lessons through conversation. It uses LangGraph for workflow management, Neo4j for data storage, and supports multiple LLM providers.

### What does "Ollama" mean in the name?

Ollama was originally used as the LLM provider for local inference. The name persists even though it now supports multiple providers (Blablador, OpenAI, Anthropic).

### What CEFR levels are supported?

All six CEFR levels are supported:
- A1 (Beginner)
- A2 (Elementary)
- B1 (Intermediate)
- B2 (Upper Intermediate)
- C1 (Advanced)
- C2 (Mastery)

### Which languages can I learn?

Currently, the focus is on Italian, but the architecture can be extended to other languages.

## Technical Questions

### What are the system requirements?

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 cores | 4+ cores |
| RAM | 4 GB | 8+ GB |
| Storage | 20 GB | 50+ GB |
| Docker | 20.10+ | Latest |

### Do I need an LLM API key?

Yes, you need at least one LLM provider. Options:
- **Blablador** (recommended, free for research)
- **Ollama** (local, free)
- **OpenAI** (paid)
- **Anthropic** (paid)

### Can I run this locally without Docker?

Yes, but it's more complex. You'd need to install:
- Python 3.10+
- Neo4j
- Ollama (or LLM API)
- All Python dependencies from requirements.txt

### Is Neo4j required?

Yes, Neo4j is required for storing:
- Student profiles
- Vocabulary
- Grammar errors
- Exercise history
- Progress data

You can use Neo4j Aura (cloud) or local Neo4j.

## Usage Questions

### How do I start learning?

1. Go to http://localhost/chat
2. Say "Ciao" or "Voglio imparare l'italiano"
3. Complete the placement test
4. Start practicing!

### How does the placement test work?

The placement test asks 10-15 questions to assess your Italian level. It covers:
- Vocabulary
- Grammar
- Comprehension

Based on your answers, you receive a CEFR level recommendation.

### How does spaced repetition work?

The system tracks your confidence for each vocabulary word. Words you're less confident about appear more frequently. As confidence increases, review intervals lengthen.

| Confidence | Review Interval |
|------------|-----------------|
| < 50% | Every session |
| 50-70% | Every 3 days |
| 70-90% | Every 7 days |
| > 90% | Every 14 days |

### What exercise types are available?

1. **Vocabulary** - Flashcard practice
2. **Grammar** - Error detection drills
3. **Translation** - IT↔EN translation
4. **Free Writing** - Writing with feedback
5. **Exam Prep** - TELC/Goethe practice

### How do I switch between exercises?

Use Italian commands:
- "Fai vocab" - Vocabulary
- "Fai grammatica" - Grammar
- "Fai traduzione" - Translation
- "Scrivi qualcosa" - Writing
- "Fai un test" - Exam prep

## Account & Data

### Is my data private?

Yes. Your data is stored in your own Neo4j database. It is not shared with third parties.

### Can I export my progress?

Yes, from the dashboard you can export:
- Vocabulary list (CSV)
- Progress report (PDF)

### How do I reset my progress?

Contact support or manually delete your student data from Neo4j:
```cypher
MATCH (s:Student {student_id: 'your-id'})
DETACH DELETE s
```

### Can I have multiple students on one account?

Currently, each account is for one student. Multi-student support is planned.

## Deployment Questions

### Can I deploy to production?

Yes. See the [Production Deployment Guide](../deployment/production.md) for:
- SSL/HTTPS configuration
- Neo4j Aura setup
- Security best practices

### Is there a hosted version?

Not currently. You need to self-host the application.

### Can I use my own domain?

Yes, configure Nginx with your domain and SSL certificates.

## Troubleshooting Questions

### Why is the chat not responding?

Check these common issues:
1. API service running? `docker compose ps`
2. LLM connected? `curl http://localhost:4000/health`
3. Neo4j connected? `curl http://localhost:8000/health`

### Why are components not showing?

This is usually a WebSocket or SSE streaming issue. Check:
1. Nginx WebSocket headers configured
2. Browser console for errors
3. API logs for streaming errors

### Why is it running slow?

Possible causes:
- LLM provider slow
- Network issues between containers
- Neo4j queries need optimization
- Insufficient server resources

### How do I get help?

1. Check this troubleshooting guide
2. Check the logs: `docker compose logs`
3. Open an issue on GitHub

## Billing Questions

### How much does it cost to run?

Costs depend on your LLM choice:
- **Blablador**: Free (for Helmholtz research)
- **Ollama**: Free (local electricity)
- **OpenAI**: ~$5-20/month depending on usage
- **Anthropic**: ~$10-30/month depending on usage

Neo4j Aura costs ~$50/month for basic tier.

### Is there a free tier?

Yes:
- Neo4j Desktop (local, free)
- Ollama (local, free)
- Blablador (for research institutions)

## Contributing Questions

### How can I contribute?

1. Fork the repository
2. Create a feature branch
3. Make changes following coding standards
4. Add tests
5. Submit a pull request

### What coding standards should I follow?

See [Coding Standards](../development/coding-standards.md):
- PEP 8 with Black formatting
- Type hints required
- Google-style docstrings
- Conventional commits

### Are there contribution guidelines?

Yes, see CONTRIBUTING.md in the repository root.

## Feature Questions

### Will you add more languages?

The architecture supports adding languages. Contact us to request a specific language.

### Can I add custom vocabulary?

Not currently, but this is on the roadmap.

### Is there a mobile app?

Not at the moment. The web interface is responsive and works on mobile browsers.

### Can I use my own LLM model?

Yes, configure any OpenAI-compatible API in LiteLLM.

## Security Questions

### Is my API key secure?

API keys are stored in environment variables and never committed to git. In production, use Docker secrets.

### Do you support 2FA?

Not directly, but you can enable 2FA on your Google account for OAuth login.

### Is the chat encrypted?

In production with HTTPS, all traffic is encrypted.

## Future Questions

### What's coming next?

Check the GitHub issues for upcoming features:
- More exercise types
- Mobile app
- Community features
- AI voice conversation

### How can I request a feature?

Open a GitHub issue with:
- Feature description
- Use case
- Proposed implementation (optional)

## Miscellaneous

### Why is it called "Sofia"?

Sofia is the default tutor name. It can be customized in the configuration.

### How do I pronounce "ItalianOllama"?

Approximated as: "ih-tal-ee-an oh-lah-ma"

### Where can I find the logo?

The logo is in the repository under `assets/` or at the top of README.md.

---

**Still have questions?** Open an issue on GitHub or check the troubleshooting guide.
