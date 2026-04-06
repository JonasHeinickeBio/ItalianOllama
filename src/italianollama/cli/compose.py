"""Docker Compose CLI commands for ItalianOllama.

Usage:
    python cli.py docker ...
    python cli.py docker up local
    python cli.py docker down
    python cli.py docker status
"""

import click

from .docker_helpers import (
    check_container_running,
    confirm_action,
    docker_compose_wrapper,
    get_compose_services,
    get_container_logs,
    get_container_names,
    run_command,
    run_compose,
    show_compose_status,
    validate_services,
    wait_for_services,
)


@click.group()
def docker():
    """Manage Docker Compose services."""
    pass


@docker.command()
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["local", "cloud", "blablador-only", "aura"]),
    default="local",
    help="Docker Compose profile to use",
)
@click.option(
    "--services",
    "-s",
    multiple=True,
    help="Specific services to start (can be specified multiple times)",
)
@click.option(
    "--detach/--no-detach",
    "-d",
    default=True,
    help="Run in background (default: true)",
)
@click.option(
    "--force-recreate",
    is_flag=True,
    help="Recreate containers even if configuration hasn't changed",
)
@click.option(
    "--build/--no-build",
    "-b",
    default=False,
    help="Build images before starting (default: false)",
)
@docker_compose_wrapper
def up(profile, services, detach, force_recreate, build):
    """Start Docker Compose services.

    Starts all services in the specified profile or specific services.
    """
    cmd = ["-d"] if detach else []

    if force_recreate:
        cmd.append("--force-recreate")

    if build:
        cmd.append("--build")

    extra_args = cmd

    code, stdout, stderr = run_compose(
        "up", profile=profile, services=list(services) if services else None, extra_args=extra_args
    )

    if code == 0:
        if services:
            service_str = ", ".join(services)
            click.secho(f"✓ Started services: {service_str}", fg="green")
        else:
            click.secho(f"✓ Started profile: {profile}", fg="green")

        click.echo("\n" + stdout)
    else:
        click.secho("✗ Failed to start services", fg="red", err=True)
        if stderr:
            click.echo(stderr, err=True)


@docker.command()
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["local", "cloud", "blablador-only", "aura"]),
    default=None,
    help="Docker Compose profile (stops all if not specified)",
)
@click.option(
    "--services",
    "-s",
    multiple=True,
    help="Specific services to stop (can be specified multiple times)",
)
@click.option(
    "--volumes",
    "-v",
    is_flag=True,
    help="Remove volumes (destroys data!)",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=10,
    help="Shutdown timeout in seconds",
)
@docker_compose_wrapper
def down(profile, services, volumes, timeout):
    """Stop and remove Docker Compose services."""
    cmd = ["-t", str(timeout)]

    if volumes:
        cmd.append("-v")

    code, stdout, stderr = run_compose(
        "down", profile=profile, services=list(services) if services else None, extra_args=cmd
    )

    if code == 0:
        if services:
            service_str = ", ".join(services)
            click.secho(f"✓ Stopped services: {service_str}", fg="green")
        else:
            click.secho(f"✓ Stopped profile: {profile or 'all'}", fg="green")

        if volumes:
            click.secho("✓ Removed volumes", fg="yellow")
    else:
        click.secho("✗ Failed to stop services", fg="red", err=True)
        if stderr:
            click.echo(stderr, err=True)


@docker.command("ps")
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["local", "cloud", "blablador-only", "aura"]),
    default=None,
    help="Filter by profile",
)
def list_services(profile):
    """List Docker Compose services and their status."""
    code, output, _ = run_compose("ps", profile=profile, capture_output=True)

    if code == 0 and output.strip():
        click.echo("\n" + output)
    else:
        click.secho("No services found", fg="yellow")


@docker.command()
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["local", "cloud", "blablador-only", "aura"]),
    default=None,
    help="Docker Compose profile",
)
@click.option(
    "--services",
    "-s",
    multiple=True,
    help="Specific services to restart",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=10,
    help="Shutdown timeout in seconds",
)
@docker_compose_wrapper
def restart(profile, services, timeout):
    """Restart Docker Compose services."""
    cmd = ["-t", str(timeout)]

    code, stdout, stderr = run_compose(
        "restart", profile=profile, services=list(services) if services else None, extra_args=cmd
    )

    if code == 0:
        if services:
            service_str = ", ".join(services)
            click.secho(f"✓ Restarted services: {service_str}", fg="green")
        else:
            click.secho(f"✓ Restarted profile: {profile or 'all'}", fg="green")
    else:
        click.secho("✗ Failed to restart services", fg="red", err=True)
        if stderr:
            click.echo(stderr, err=True)


@docker.command()
@docker_compose_wrapper
def status():
    """Show Docker Compose status."""
    show_compose_status()


@docker.command()
@click.argument("service")
@click.option(
    "--tail",
    "-n",
    type=int,
    default=100,
    help="Number of lines to show",
)
@click.option(
    "--follow",
    "-f",
    is_flag=True,
    help="Follow log output",
)
@docker_compose_wrapper
def logs(service, tail, follow):
    """Show logs for a specific service."""
    container_names = get_container_names()

    if service not in container_names:
        available = ", ".join(container_names.keys())
        click.secho(f"✗ Unknown service '{service}'. Available: {available}", fg="red", err=True)
        return 1

    container_name = container_names[service]
    click.echo(f"\nLogs for {service} ({container_name}):")
    click.echo("=" * 60)

    code, stdout, stderr = get_container_logs(container_name, tail=tail, follow=follow)

    if code == 0:
        if stdout:
            click.echo(stdout)
    else:
        click.secho(f"✗ Failed to get logs for {service}", fg="red", err=True)
        if stderr:
            click.echo(stderr, err=True)
        return 1

    return 0


@docker.command()
@click.argument("services", nargs=-1)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=60,
    help="Timeout in seconds",
)
@docker_compose_wrapper
def wait(services, timeout):
    """Wait for services to become healthy."""
    if not services:
        click.secho("Error: At least one service name required", fg="red", err=True)
        click.echo("Usage: docker helpers wait <service> [service2] ...")
        return 1

    valid, invalid = validate_services(list(services))
    if not valid:
        click.secho(f"Error: Unknown services: {', '.join(invalid)}", fg="red", err=True)
        return 1

    click.echo(f"Waiting for {', '.join(services)} to become healthy...")

    if wait_for_services(list(services), timeout=timeout):
        click.secho("✓ All services are healthy!", fg="green")
        return 0
    else:
        click.secho("✗ Timeout waiting for services", fg="red", err=True)
        return 1


@docker.group()
def helpers():
    """Utility helpers for Docker management."""
    pass


@helpers.command()
@docker_compose_wrapper
def check():
    """Check Docker and Docker Compose installation."""
    click.echo("Checking Docker installation...")

    if check_container_running("italian-tutor-ollama"):
        click.secho("✓ ItalianOllama containers are running", fg="green")
    else:
        click.secho("○ No ItalianOllama containers found", fg="yellow")

    click.echo("\nDocker Compose profiles:")
    for profile, services in get_compose_services().items():
        click.echo(f"  • {profile}: {', '.join(services)}")

    click.echo("\nAvailable helpers:")
    click.echo("  • docker up      - Start services")
    click.echo("  • docker down    - Stop services")
    click.echo("  • docker ps      - List services")
    click.echo("  • docker logs    - View logs")
    click.echo("  • docker wait    - Wait for healthy services")


@helpers.command()
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["local", "cloud", "blablador-only", "aura"]),
    default="local",
    help="Profile to validate",
)
@docker_compose_wrapper
def validate(profile):
    """Validate docker-compose configuration."""
    code, stdout, stderr = run_compose("config", profile=profile, capture_output=True)

    if code == 0:
        click.secho("✓ Docker Compose configuration is valid", fg="green")
        click.echo(stdout)
    else:
        click.secho("✗ Docker Compose configuration has errors", fg="red", err=True)
        click.echo(stderr, err=True)
        return 1

    return 0


@helpers.command()
@docker_compose_wrapper
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["local", "cloud", "blablador-only", "aura"]),
    default=None,
    help="Profile to prune (prunes all if not specified)",
)
def prune(profile):
    """Clean up stopped containers, volumes, and networks."""
    confirm = confirm_action(
        "This will remove all stopped containers and unused volumes. Continue?", default=False
    )

    if not confirm:
        click.echo("Aborted.")
        return 0

    code, stdout, stderr = run_compose("down", profile=profile, extra_args=["--volumes"])

    if code == 0:
        click.secho("✓ Cleanup complete", fg="green")
    else:
        click.secho("✗ Cleanup failed", fg="red", err=True)
        if stderr:
            click.echo(stderr, err=True)

    return code


@helpers.command()
@click.option(
    "--services",
    "-s",
    multiple=True,
    help="Services to rebuild",
)
@docker_compose_wrapper
def rebuild(services):
    """Rebuild Docker images."""
    cmd = []

    if services:
        cmd.extend(services)
        click.echo(f"Rebuilding services: {', '.join(services)}")
    else:
        click.echo("Rebuilding all services...")

    code, stdout, stderr = run_compose("build", extra_args=cmd)

    if code == 0:
        click.secho("✓ Rebuild complete", fg="green")
    else:
        click.secho("✗ Rebuild failed", fg="red", err=True)
        if stderr:
            click.echo(stderr, err=True)

    return code


@helpers.command()
def info():
    """Show Docker Compose system information."""
    click.echo("Docker Compose System Information")
    click.echo("=" * 60)

    code, output, _ = run_command(["docker", "info"], capture_output=True, check=False)

    if code == 0:
        for line in output.split("\n")[:30]:
            click.echo(line)
        click.echo("...")
    else:
        click.secho("Error getting docker info", fg="red")

    click.echo("\nDocker Compose Version:")
    code, output, _ = run_command(
        ["docker", "compose", "version"], capture_output=True, check=False
    )
    if code == 0:
        click.echo(output.strip())
    else:
        click.secho("Error getting docker compose version", fg="red")


if __name__ == "__main__":
    docker()
