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
pip install -r requirements.txt
```

2. Ensure Ollama is installed and a local model is available. This scaffold uses a small wrapper that tries HTTP at `http://127.0.0.1:11434` and falls back to the `ollama` CLI.

3. Run the CLI app to try a sample prompt:

```bash
python -m italianollama.app --task grammar_explain --input "Mi chiamo Jonas e io essere felice" --model local-model
```

What I added
- `src/italianollama` package with an Ollama client wrapper, prompt templates, storage and CLI.
- `README.md` — quick start and notes
- `requirements.txt` — recommended packages
- `.gitignore`, `START.md`
- `.github/ISSUE_TEMPLATE/` with feature and bug templates

Next steps
- Replace `local-model` with your model name.
- Tune prompt templates in `prompts.py`.
- Hook up a UI (FastAPI or TUI) and add speech recognition later.

If you want, I can also init a git repo here and commit everything, or open these as real GitHub issues if you give repository & token access.

````
results = ftp_downloader.bulk_download_and_extract(
