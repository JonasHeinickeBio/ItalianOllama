# ItalianOllama — Local Italian learning assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ItalianOllama is a lightweight Python scaffold for building an Italian language learning assistant powered by a local Ollama LLM.

## Key goals

- Prompt templates for grammar, vocabulary and writing practice
- Automatic corrections with explanations and short practice items
- Simple storage for saving vocabulary and corrected texts for later revision
- Room to prototype spoken interaction (speech-to-text and text-to-speech)

## Quickstart (macOS / zsh)

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure Ollama is installed and a local model is available. The scaffold will try the Ollama HTTP API at `http://127.0.0.1:11434` and fall back to the `ollama` CLI if needed.

4. Try the CLI (replace `local-model` with your model name):

```bash
python -m italianollama.app run --task grammar_explain --input "Mi chiamo Jonas e io essere felice" --model local-model
```

## Repository layout

- `src/italianollama/` — package code: prompt templates, `OllamaClient`, storage, CLI
- `requirements.txt` — suggested Python dependencies
- `tests/` — small smoke tests and unit tests
- `.github/ISSUE_TEMPLATE/`, `issues/` — templates and initial project issues

## Development notes

- Update `src/italianollama/prompts.py` to tune prompts and task templates.
- `src/italianollama/storage.py` provides a simple SQLite-backed save/list API for study items.
- Consider adding a small FastAPI UI or TUI for interactive practice sessions.

## Contributing

- Create a feature branch from `main`, open a PR, and add tests for new behavior.

## License

- MIT — see `LICENSE` for details.

## Next steps I can help with

- Add a short example notebook demonstrating typical flows
- Implement a minimal FastAPI server for interactive practice
- Create CI workflow(s) that run tests and linting for PRs

If you want any of the above, tell me which and I'll implement it on `cleanup-scaffold` or a dedicated feature branch.
# PyEuropePMC

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-200%2B%20passed-green.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-90%2B%25-brightgreen.svg)](htmlcov/)


**PyEuropePMC** is a robust Python toolkit for automated search, extraction, and analysis of scientific literature from [Europe PMC](https://europepmc.org/).

## ✨ Key Features


- 🔍 **Comprehensive Search API** - Query Europe PMC with advanced search options
- 📄 **Full-Text Retrieval** - Download PDFs, XML, and HTML content from open access articles
- 📊 **Multiple Output Formats** - JSON, XML, Dublin Core (DC)
- 📦 **Bulk FTP Downloads** - Efficient bulk PDF downloads from Europe PMC FTP servers
- 🔄 **Smart Pagination** - Automatic handling of large result sets
- 🛡️ **Robust Error Handling** - Built-in retry logic and connection management
- 🧑‍💻 **Type Safety** - Extensive use of type annotations and validation
- ⚡ **Rate Limiting** - Respectful API usage with configurable delays
- 🧪 **Extensively Tested** - 200+ tests with 90%+ code coverage

## 🚀 Quick Start

### Installation

```bash
pip install pyeuropepmc
````markdown
# ItalianOllama — Local Italian learning assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Lightweight Python scaffold for an Italian language learning app that uses a local Ollama LLM.

Goals:
- Provide prompt templates for grammar, vocabulary, and writing tasks.
- Produce corrections and explanations for learner input.
- Save important facts (vocabulary, grammar points, corrected texts) for later revision.
- Explore future spoken interaction features.

Requirements
- Python 3.10+
- Ollama installed and a local model available (see https://ollama.ai)
- (Optional) Create a Python virtualenv

Quick start

1. Create and activate virtualenv (macOS zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
# ItalianOllama — Local Italian learning assistant

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Lightweight Python scaffold for an Italian language learning app that uses a local Ollama LLM.

Goals
- Provide prompt templates for grammar, vocabulary, and writing tasks.
- Produce corrections and explanations for learner input.
- Save important facts (vocabulary, grammar points, corrected texts) for later revision.
- Explore future spoken interaction features.

Requirements
- Python 3.10+
- Ollama installed and a local model available (see https://ollama.ai)

Quick start

1. Create and activate a virtualenv (macOS zsh):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Ensure Ollama is installed and a local model is available. This scaffold uses a small wrapper that tries HTTP at `http://127.0.0.1:11434` and falls back to the `ollama` CLI.

3. Run the CLI app to try a sample prompt:

```bash
python -m italianollama.app run --task grammar_explain --input "Mi chiamo Jonas e io essere felice" --model local-model
```

What this repo contains
- `src/italianollama/` — the package with prompt templates, an Ollama client wrapper, storage, and a small CLI
- `requirements.txt` — recommended runtime deps
- `tests/` — minimal tests for the scaffold
- `.github/ISSUE_TEMPLATE/` + `issues/` — templates and initial issues to track features

Development notes
- Replace `local-model` with your Ollama model name.
- Tune or extend prompt templates in `src/italianollama/prompts.py`.
- To prototype speech I/O, add a new feature branch (I can help wire Whisper/VOSK later).

Contributing
- Create feature branches off `main` and open PRs. CI checks (if any) will run on PRs.

License
- MIT — see `LICENSE` for details.

```
