"""Main CLI entry point for ItalianOllama."""

import os

import click


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ItalianOllama - Italian Language Learning with AI."""
    pass


@cli.group()
def start():
    """Start services (API, Neo4j, LLM)."""
    pass


@start.command("api")
@click.option("--host", default="0.0.0.0", help="API host")
@click.option("--port", default=8000, help="API port")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def start_api(host: str, port: int, reload: bool):
    """Start the API server."""
    import uvicorn

    click.echo(f"Starting API on {host}:{port}")
    uvicorn.run(
        "italianollama.api.main:app",
        host=host,
        port=port,
        reload=reload,
    )


@cli.group()
def neo4j():
    """Manage Neo4j connections (Aura or local)."""
    pass


@neo4j.command("connect")
@click.option("--uri", help="Neo4j URI (defaults to env)")
@click.option("--user", help="Neo4j user (defaults to env)")
@click.option("--password", help="Neo4j password (defaults to env)")
def neo4j_connect(uri: str | None, user: str | None, password: str | None):
    """Test connection to Neo4j."""
    from italianollama.memory.graph import MemoryGraph

    uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = user or os.getenv("NEO4J_USER", "neo4j")
    password = password or os.getenv("NEO4J_PASSWORD", "")

    click.echo(f"Connecting to Neo4j: {uri}")

    graph = MemoryGraph(uri=uri, user=user, password=password)

    import asyncio

    async def test():
        await graph.connect()
        await graph.close()

    asyncio.run(test())
    click.secho("✓ Connected successfully!", fg="green")


@neo4j.command("status")
def neo4j_status():
    """Show Neo4j connection status."""
    from italianollama.memory.graph import MemoryGraph

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    use_aura = os.getenv("USE_AURA", "false").lower() == "true"

    click.echo(f"URI: {uri}")
    click.echo(f"User: {user}")
    click.echo(f"Type: {'Neo4j Aura (Cloud)' if use_aura else 'Local Neo4j'}")

    import asyncio

    async def check():
        graph = MemoryGraph(uri=uri, user=user, password=password)
        try:
            await graph.connect()
            await graph.close()
            return True
        except Exception as e:
            click.secho(f"✗ Connection failed: {e}", fg="red")
            return False

    if asyncio.run(check()):
        click.secho("✓ Neo4j is reachable", fg="green")


@cli.group()
def llm():
    """Manage LLM providers (Ollama, Blablador, OpenAI)."""
    pass


@llm.command("list")
def llm_list():
    """List available LLM providers."""
    providers = [
        ("ollama", "Local Ollama instance"),
        ("blablador", "Helmholtz Blablador API"),
        ("openai", "OpenAI GPT models"),
        ("anthropic", "Anthropic Claude models"),
    ]

    current = os.getenv("AISUITE_PROVIDER", "ollama")

    click.echo("Available LLM providers:\n")
    for name, desc in providers:
        marker = "●" if name == current else "○"
        click.echo(f"  {marker} {name:15} - {desc}")


@llm.command("chat")
@click.argument("prompt")
@click.option("--model", help="Model name (defaults to provider default)")
@click.option("--system", "system_prompt", help="System prompt")
def llm_chat(prompt: str, model: str | None, system_prompt: str | None):
    """Send a chat message to the LLM."""
    from italianollama.llm.client import LLMClient

    provider = os.getenv("AISUITE_PROVIDER", "ollama")

    click.echo(f"Using provider: {provider}")

    client = LLMClient(provider=provider, model=model)

    import asyncio

    async def chat():
        response = await client.generate(
            prompt=prompt,
            system_prompt=system_prompt,
        )
        return response

    result = asyncio.run(chat())
    click.echo(f"\n{result}")


@llm.command("test")
def llm_test():
    """Test LLM connection."""
    from italianollama.llm.client import LLMClient

    provider = os.getenv("AISUITE_PROVIDER", "ollama")
    model = os.getenv(f"{provider.upper()}_MODEL", "")

    click.echo(f"Testing {provider} provider...")

    client = LLMClient(provider=provider, model=model or None)

    import asyncio

    async def test():
        return await client.generate("Say 'Hello' in Italian.")

    try:
        result = asyncio.run(test())
        click.secho(f"✓ Response: {result}", fg="green")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")


@cli.group()
def vocab():
    """Manage vocabulary in Neo4j."""
    pass


@vocab.command("add")
@click.argument("word")
@click.argument("translation")
@click.option("--examples", "-e", multiple=True, help="Example sentences")
@click.option("--topic", default="general", help="Topic/category")
@click.option("--language", default="italian", help="Target language")
def vocab_add(word: str, translation: str, examples: tuple, topic: str, language: str):
    """Add a vocabulary word."""
    import asyncio

    from italianollama.memory.graph import MemoryGraph

    async def add():
        graph = MemoryGraph(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", ""),
        )
        await graph.connect()

        node_id = await graph.add_vocabulary(
            word=word,
            translation=translation,
            examples=list(examples),
            topic=topic,
            language=language,
        )

        await graph.close()
        return node_id

    result = asyncio.run(add())
    click.secho(f"✓ Added '{word}' (ID: {result})", fg="green")


@vocab.command("list")
@click.option("--topic", help="Filter by topic")
@click.option("--language", default="italian", help="Language")
@click.option("--limit", default=20, help="Max results")
def vocab_list(topic: str | None, language: str, limit: int):
    """List vocabulary words."""
    import asyncio

    from italianollama.memory.graph import MemoryGraph

    async def list_vocab():
        graph = MemoryGraph(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", ""),
        )
        await graph.connect()

        items = await graph.get_vocabulary(
            language=language,
            topic=topic,
            limit=limit,
        )

        await graph.close()
        return items

    items = asyncio.run(list_vocab())

    if not items:
        click.echo("No vocabulary found.")
        return

    click.echo(f"\nVocabulary ({len(items)} items):\n")
    for item in items:
        click.echo(f"  • {item['word']} - {item['translation']}")
        click.echo(f"    Topic: {item['topic']}")


@vocab.command("stats")
def vocab_stats():
    """Show vocabulary statistics."""
    import asyncio

    from italianollama.memory.graph import MemoryGraph

    async def get_stats():
        graph = MemoryGraph(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", ""),
        )
        await graph.connect()

        stats = await graph.get_vocabulary_stats()

        await graph.close()
        return stats

    stats = asyncio.run(get_stats())

    click.echo(f"\nTotal words: {stats['total']}")
    if stats.get("by_topic"):
        click.echo("\nBy topic:")
        for topic, count in stats["by_topic"].items():
            click.echo(f"  • {topic}: {count}")


@cli.group()
def docker():
    """Docker compose management."""
    pass


@docker.command("up")
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["local", "aura", "minimal", "webui"]),
    default="aura",
    help="Profile to use",
)
@click.option("--no-ollama", is_flag=True, help="Don't start Ollama container")
def docker_up(profile: str, no_ollama: bool):
    """Start services with docker compose."""
    import subprocess

    cmd = ["docker", "compose", "-f", "docker/docker-compose.yml"]

    if profile != "minimal":
        cmd.extend(["--profile", profile])

    cmd.extend(["up", "-d"])

    if no_ollama:
        cmd.append("--no-attach")
        cmd.append("ollama")

    click.echo(f"Running: {' '.join(cmd)}")
    subprocess.run(
        cmd, cwd=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )


@docker.command("down")
def docker_down():
    """Stop all services."""
    import subprocess

    subprocess.run(["docker", "compose", "-f", "docker/docker-compose.yml", "down"])
    click.secho("✓ Services stopped", fg="green")


@docker.command("status")
def docker_status():
    """Show service status."""
    import subprocess

    result = subprocess.run(
        ["docker", "compose", "-f", "docker/docker-compose.yml", "ps"],
        capture_output=True,
        text=True,
    )

    click.echo(result.stdout)


@cli.group()
def config():
    """Configuration management."""
    pass


@config.command("show")
def config_show():
    """Show current configuration."""
    vars_to_show = [
        "NEO4J_URI",
        "NEO4J_USER",
        "NEO4J_DATABASE",
        "USE_AURA",
        "AISUITE_PROVIDER",
        "OLLAMA_BASE_URL",
        "BLABLADOR_API_URL",
        "BLABLADOR_MODEL",
    ]

    click.echo("\nCurrent configuration:\n")
    for var in vars_to_show:
        value = os.getenv(var, "(not set)")
        if "PASSWORD" in var or "KEY" in var:
            value = "***" if value else "(not set)"
        click.echo(f"  {var}: {value}")


@config.command("set")
@click.argument("key")
@click.argument("value")
def config_set(key: str, value: str):
    """Set an environment variable."""
    os.environ[key] = value
    click.secho(f"✓ Set {key}={value}", fg="green")


if __name__ == "__main__":
    cli()
