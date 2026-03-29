"""CLI main module for Italian Tutor."""

import asyncio
import os

import click


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """ItalianTutor - AI-powered Italian Language Learning."""
    pass


@cli.group()
def neo4j():
    """Manage Neo4j connections."""
    pass


@neo4j.command("status")
def neo4j_status():
    """Show Neo4j connection status."""
    from italianollama.memory.neo4j_client import Neo4jClient

    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "")
    use_aura = os.getenv("USE_AURA", "false").lower() == "true"

    click.echo(f"URI: {uri}")
    click.echo(f"User: {user}")
    click.echo(f"Type: {'Neo4j Aura (Cloud)' if use_aura else 'Local Neo4j'}")

    async def check():
        client = Neo4jClient(uri=uri, user=user, password=password)
        try:
            await client.connect()
            await client.close()
            return True
        except Exception as e:
            click.secho(f"✗ Connection failed: {e}", fg="red")
            return False

    if asyncio.run(check()):
        click.secho("✓ Neo4j is reachable", fg="green")


@cli.group()
def llm():
    """Manage LLM providers."""
    pass


@llm.command("list")
def llm_list():
    """List available LLM providers."""
    providers = [
        ("blablador", "Helmholtz Blablador API"),
        ("ollama", "Local Ollama instance"),
        ("openai", "OpenAI GPT models"),
        ("anthropic", "Anthropic Claude models"),
    ]

    current = os.getenv("AISUITE_PROVIDER", "blablador")

    click.echo("\nAvailable LLM providers:\n")
    for name, desc in providers:
        marker = "●" if name == current else "○"
        click.echo(f"  {marker} {name:15} - {desc}")


@llm.command("test")
def llm_test():
    """Test LLM connection."""
    from italianollama.graph.nodes.base import LLMClient

    click.echo("Testing LLM connection...")

    client = LLMClient()

    async def test():
        return await client.chat(
            messages=[{"role": "user", "content": "Say 'Ciao' in Italian."}],
            system_prompt="You are a helpful Italian tutor.",
        )

    try:
        result = asyncio.run(test())
        click.secho(f"✓ Response: {result}", fg="green")
    except Exception as e:
        click.secho(f"✗ Error: {e}", fg="red")


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
        "USE_AURA",
        "AISUITE_PROVIDER",
        "BLABLADOR_API_URL",
        "LITELLM_BASE_URL",
    ]

    click.echo("\nCurrent configuration:\n")
    for var in vars_to_show:
        value = os.getenv(var, "(not set)")
        if "PASSWORD" in var or "KEY" in var:
            value = "***" if value else "(not set)"
        click.echo(f"  {var}: {value}")


if __name__ == "__main__":
    cli()
