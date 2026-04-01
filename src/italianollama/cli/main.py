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
        "BACKEND_URL",
        "CHAINLIT_URL",
    ]

    click.echo("\nCurrent configuration:\n")
    for var in vars_to_show:
        value = os.getenv(var, "(not set)")
        if "PASSWORD" in var or "KEY" in var:
            value = "***" if value else "(not set)"
        click.echo(f"  {var}: {value}")


@cli.group()
def kg():
    """Directly interact with the Neo4j Knowledge Graph."""
    pass


@kg.command("summary")
def kg_summary():
    """Show counts of nodes and relationships in the graph."""
    from italianollama.api.config import get_settings
    from italianollama.memory.neo4j_client import Neo4jClient

    settings = get_settings()

    async def get_summary():
        client = Neo4jClient(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
            database=settings.neo4j_database,
        )
        await client.connect()
        async with client._driver.session(database=client.database) as session:
            # Count nodes by label
            node_counts = await session.run(
                "MATCH (n) RETURN labels(n)[0] AS label, count(*) AS count"
            )
            # Count rels by type
            rel_counts = await session.run(
                "MATCH ()-[r]->() RETURN type(r) AS type, count(*) AS count"
            )

            nodes = await node_counts.data()
            rels = await rel_counts.data()
            return nodes, rels

    nodes, rels = asyncio.run(get_summary())

    click.secho("\n--- Node Summary ---", fg="cyan", bold=True)
    if not nodes:
        click.echo("No nodes found.")
    for n in nodes:
        click.echo(f"  {n['label'] or 'Unlabeled'}: {n['count']}")

    click.secho("\n--- Relationship Summary ---", fg="magenta", bold=True)
    if not rels:
        click.echo("No relationships found.")
    for r in rels:
        click.echo(f"  {r['type']}: {r['count']}")
    click.echo("")


@kg.command("query")
@click.argument("cypher")
def kg_query(cypher):
    """Execute a raw Cypher query and show JSON results."""
    import json

    from italianollama.api.config import get_settings
    from italianollama.memory.neo4j_client import Neo4jClient

    settings = get_settings()

    async def run_query():
        client = Neo4jClient(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
            database=settings.neo4j_database,
        )
        await client.connect()
        async with client._driver.session(database=client.database) as session:
            result = await session.run(cypher)
            return await result.data()

    try:
        data = asyncio.run(run_query())
        click.echo(json.dumps(data, indent=2, default=str))
    except Exception as e:
        click.secho(f"Error: {e}", fg="red")


@kg.command("list-nodes")
@click.option("--label", "-l", help="Filter by node label")
@click.option("--limit", "-n", default=20, help="Max nodes to show")
def kg_list_nodes(label, limit):
    """List nodes in the graph."""
    from italianollama.api.config import get_settings
    from italianollama.memory.neo4j_client import Neo4jClient

    settings = get_settings()
    query = f"MATCH (n{':' + label if label else ''}) RETURN n LIMIT {limit}"

    async def get_nodes():
        client = Neo4jClient(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
            database=settings.neo4j_database,
        )
        await client.connect()
        async with client._driver.session(database=client.database) as session:
            result = await session.run(query)
            # return the actual records to keep metadata like labels
            nodes = []
            async for record in result:
                nodes.append(record["n"])
            return nodes

    nodes = asyncio.run(get_nodes())
    for node in nodes:
        labels = list(node.labels)
        click.secho(f"[{labels[0] if labels else 'Node'}] ", fg="green", nl=False)
        click.echo(f"ID: {node.element_id} | Props: {dict(node)}")


@kg.command("list-rels")
@click.option("--type", "-t", "rel_type", help="Filter by relationship type")
@click.option("--limit", "-n", default=20, help="Max relationships to show")
def kg_list_rels(rel_type, limit):
    """List relationships in the graph."""
    from italianollama.api.config import get_settings
    from italianollama.memory.neo4j_client import Neo4jClient

    settings = get_settings()
    query = f"MATCH (s)-[r{':' + rel_type if rel_type else ''}]->(t) RETURN s, r, t LIMIT {limit}"

    async def get_rels():
        client = Neo4jClient(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password,
            database=settings.neo4j_database,
        )
        await client.connect()
        async with client._driver.session(database=client.database) as session:
            result = await session.run(query)
            rels = []
            async for record in result:
                rels.append((record["s"], record["r"], record["t"]))
            return rels

    rels = asyncio.run(get_rels())
    if not rels:
        click.echo("No relationships found.")
    for s, r, t in rels:
        s_label = list(s.labels)[0] if s.labels else "Node"
        t_label = list(t.labels)[0] if t.labels else "Node"
        click.echo(
            f"({s_label} {s.get('student_id') or s.element_id}) -[:{r.type}]-> ({t_label} {t.get('word') or t.get('code') or t.element_id})"
        )


# ============ Service Management ============


@cli.group()
def service():
    """Manage ItalianOllama services (API, Chat, Dashboard)."""
    pass


@service.command("start")
@click.argument("name", type=click.Choice(["api", "chainlit", "streamlit", "all"]), default="all")
def service_start(name):
    """Start services (api, chainlit, streamlit, or all)."""
    from italianollama.cli.services import start_service

    if name == "all":
        for svc in ["api", "chainlit", "streamlit"]:
            start_service(svc)
            import time

            time.sleep(1)  # Small pause to let ports bind
    else:
        start_service(name)


@service.command("stop")
@click.argument("name", type=click.Choice(["api", "chainlit", "streamlit", "all"]), default="all")
def service_stop(name):
    """Stop services (api, chainlit, streamlit, or all)."""
    from italianollama.cli.services import stop_service

    if name == "all":
        for svc in ["api", "chainlit", "streamlit"]:
            stop_service(svc)
    else:
        stop_service(name)


@service.command("restart")
@click.argument("name", type=click.Choice(["api", "chainlit", "streamlit", "all"]), default="all")
@click.option("--delay", type=int, default=15, help="Delay (seconds) between service startups")
def service_restart(name, delay):
    """Restart services with sequential startup and configurable delay."""
    from italianollama.cli.services import (
        is_service_running,
        restart_services_sequentially,
        start_service,
        stop_service,
    )

    names = ["api", "chainlit", "streamlit"] if name == "all" else [name]

    if len(names) == 1:
        # Single service: use old logic (no delay)
        svc = names[0]
        if is_service_running(svc):
            stop_service(svc)
            # Wait for port to clear
            for _ in range(5):
                import time

                time.sleep(1)
                if not is_service_running(svc):
                    break
        start_service(svc)
    else:
        # Multiple services: use sequential restart with delay
        restart_services_sequentially(names, startup_delay=delay)


@service.command("status")
def service_status():
    """Show current status of all services."""
    from italianollama.cli.services import get_status

    get_status()


@service.command("logs")
@click.argument("name", type=click.Choice(["api", "chainlit", "streamlit"]))
@click.option("--lines", "-n", default=20, help="Number of lines to show")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
def service_logs(name, lines, follow):
    """Show logs for a specific service."""
    import subprocess

    log_file = f"logs/{name}.log"
    if not os.path.exists(log_file):
        click.secho(f"⚠ Log file {log_file} not found.", fg="yellow")
        return

    cmd = ["tail", f"-n{lines}", log_file]
    if follow:
        cmd.insert(1, "-f")

    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli()
