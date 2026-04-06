"""Docker Compose helper functions for ItalianOllama CLI.

Provides modular, scalable functions for managing Docker services.
"""

from collections.abc import Callable
import functools
import os
from pathlib import Path
import subprocess
import time

import click


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent.parent


def get_backend_dir() -> Path:
    """Get the backend directory containing docker-compose.yml."""
    return get_project_root() / "backend"


def get_env_file() -> Path:
    """Get the .env file path."""
    return get_project_root() / ".env"


def run_command(
    cmd: list[str],
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    capture_output: bool = False,
    check: bool = True,
) -> tuple[int, str, str]:
    """Run a shell command with proper error handling.

    Args:
        cmd: Command to run as list
        cwd: Working directory
        env: Environment variables
        capture_output: Whether to capture stdout/stderr
        check: Whether to raise on non-zero exit

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    env = env or os.environ.copy()
    cwd = cwd or get_backend_dir()

    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            env=env,
            capture_output=capture_output,
            text=True,
            check=False,
        )
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode, cmd, result.stdout, result.stderr
            )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 127, "", "Command not found"
    except Exception as e:
        return 1, "", str(e)


def check_docker_installed() -> bool:
    """Check if docker is installed and accessible."""
    code, _, _ = run_command(["docker", "--version"], capture_output=True, check=False)
    return code == 0


def check_docker_compose_installed() -> bool:
    """Check if docker compose plugin is installed."""
    code, _, _ = run_command(["docker", "compose", "--version"], capture_output=True, check=False)
    return code == 0


def get_compose_files() -> list[Path]:
    """Get available docker-compose files."""
    backend_dir = get_backend_dir()
    files = list(backend_dir.glob("docker-compose*.yml"))
    return files


def get_compose_env() -> dict[str, str]:
    """Load environment variables from .env file."""
    env = os.environ.copy()
    env_file = get_env_file()

    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env[key.strip()] = value.strip()

    return env


def format_compose_command(
    action: str,
    profile: str | None = None,
    services: list[str] | None = None,
    extra_args: list[str] | None = None,
) -> list[str]:
    """Format a docker compose command.

    Args:
        action: docker compose action (up, down, ps, etc.)
        profile: Optional profile name
        services: Optional list of services
        extra_args: Optional extra arguments

    Returns:
        List of command parts
    """
    cmd = ["docker", "compose"]

    if profile:
        cmd.extend(["--profile", profile])

    files = get_compose_files()
    if len(files) > 1:
        for f in files:
            cmd.extend(["-f", str(f)])

    cmd.append(action)

    if services:
        cmd.extend(services)

    if extra_args:
        cmd.extend(extra_args)

    return cmd


def run_compose(
    action: str,
    profile: str | None = None,
    services: list[str] | None = None,
    extra_args: list[str] | None = None,
    capture_output: bool = False,
) -> tuple[int, str, str]:
    """Run a docker compose command.

    Args:
        action: docker compose action
        profile: Optional profile
        services: Optional services to target
        extra_args: Optional extra arguments
        capture_output: Whether to capture output

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = format_compose_command(action, profile, services, extra_args)
    return run_command(
        cmd, cwd=get_backend_dir(), env=get_compose_env(), capture_output=capture_output
    )


def get_compose_profiles() -> list[str]:
    """Get available docker compose profiles from docker-compose.yml files."""
    profiles = ["local", "cloud", "blablador-only", "aura"]
    return profiles


def get_compose_services() -> dict[str, list[str]]:
    """Get services organized by profile from docker-compose.yml files."""
    return {
        "local": ["ollama", "litellm", "neo4j", "fastapi", "chainlit"],
        "cloud": ["neo4j", "fastapi", "chainlit"],
        "blablador-only": ["neo4j", "fastapi", "chainlit"],
        "aura": ["fastapi", "chainlit"],
    }


def validate_services(services: list[str]) -> tuple[bool, list[str]]:
    """Validate that all services exist in docker-compose.

    Args:
        services: List of service names to validate

    Returns:
        Tuple of (is_valid, invalid_services)
    """
    valid_services = []
    for profile_services in get_compose_services().values():
        valid_services.extend(profile_services)
    valid_services = list(set(valid_services))

    invalid = [s for s in services if s not in valid_services]
    return len(invalid) == 0, invalid


def wait_for_services(
    services: list[str],
    timeout: int = 60,
    interval: int = 2,
    on_progress: Callable[[str, int], None] | None = None,
) -> bool:
    """Wait for services to become healthy.

    Args:
        services: List of service names
        timeout: Total timeout in seconds
        interval: Polling interval in seconds
        on_progress: Optional callback(progress, total)

    Returns:
        True if all services are healthy, False on timeout
    """
    start_time = time.time()
    healthy = set()
    total = len(services)

    while time.time() - start_time < timeout:
        code, output, _ = run_compose("ps", capture_output=True)
        if code != 0:
            time.sleep(interval)
            continue

        for line in output.split("\n"):
            for service in services:
                if (
                    service in line
                    and "Health: running" in line
                    or service in line
                    and "Up" in line
                    and "healthy" in line
                ):
                    healthy.add(service)

        if on_progress:
            on_progress(len(healthy), total)

        if len(healthy) >= total:
            return True

        time.sleep(interval)

    return False


def show_compose_status():
    """Display docker compose status in a user-friendly format."""
    click.echo("\n" + "=" * 60)
    click.echo("Docker Compose Status")
    click.echo("=" * 60)

    code, output, _ = run_compose("ps", capture_output=True)

    if code == 0 and output.strip():
        click.echo("\nRunning Services:")
        click.echo("-" * 60)
        click.echo(output)
    else:
        click.secho("\nNo services are currently running.", fg="yellow")

    click.echo("\nAvailable Profiles:")
    click.echo("-" * 60)
    for profile, services in get_compose_services().items():
        status = "✓" if any(s in output for s in services) else "○"
        click.echo(f"  {status} {profile:20} → {', '.join(services)}")

    click.echo("=" * 60 + "\n")


def get_container_names() -> dict[str, str]:
    """Get container names for each service."""
    return {
        "ollama": "italian-tutor-ollama",
        "litellm": "italian-tutor-litellm",
        "neo4j": "italian-tutor-neo4j",
        "fastapi": "italian-tutor-api",
        "chainlit": "italian-tutor-chainlit",
        "streamlit": "italian-tutor-streamlit",
    }


def check_container_running(container_name: str) -> bool:
    """Check if a specific container is running."""
    code, output, _ = run_command(
        ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
        capture_output=True,
        check=False,
    )
    return container_name in output


def get_container_logs(
    container_name: str, tail: int = 100, follow: bool = False
) -> tuple[int, str, str]:
    """Get logs from a container.

    Args:
        container_name: Name of the container
        tail: Number of lines to show
        follow: Whether to follow logs

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = ["docker", "logs"]
    if follow:
        cmd.append("-f")
    else:
        cmd.extend(["-n", str(tail)])
    cmd.append(container_name)

    return run_command(cmd, capture_output=not follow, check=False)


def docker_compose_wrapper(func):
    """Decorator for CLI commands that need docker compose checks."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not check_docker_installed():
            click.secho(
                "Error: Docker is not installed or not in PATH",
                fg="red",
                err=True,
            )
            click.echo("Please install Docker: https://docs.docker.com/get-docker/")
            return 1

        if not check_docker_compose_installed():
            click.secho(
                "Error: Docker Compose plugin is not installed",
                fg="red",
                err=True,
            )
            click.echo("Please update Docker: https://docs.docker.com/compose/install/")
            return 1

        return func(*args, **kwargs)

    return wrapper


def confirm_action(message: str, default: bool = True) -> bool:
    """Prompt user for confirmation.

    Args:
        message: Question to ask
        default: Default answer

    Returns:
        User's answer
    """
    choice = "[Y/n]" if default else "[y/N]"
    result = click.prompt(f"{message} {choice}", default=default, type=bool)
    return result


def build_image(
    service: str,
    no_cache: bool = False,
    pull: bool = False,
    extra_args: list[str] | None = None,
) -> tuple[int, str, str]:
    """Build a Docker image for a service.

    Args:
        service: Service name (e.g., "fastapi", "chainlit")
        no_cache: Don't use cache when building
        pull: Always pull base image
        extra_args: Additional docker build arguments

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = ["docker", "compose", "build"]

    if no_cache:
        cmd.append("--no-cache")
    if pull:
        cmd.append("--pull")
    if extra_args:
        cmd.extend(extra_args)

    cmd.append(service)

    return run_command(cmd, cwd=get_backend_dir(), env=get_compose_env(), capture_output=True)


def restart_service(
    service: str,
    timeout: int = 30,
    wait_healthy: bool = True,
) -> tuple[int, str, str]:
    """Restart a service and optionally wait for it to be healthy.

    Args:
        service: Service name to restart
        timeout: Wait timeout in seconds
        wait_healthy: Whether to wait for healthcheck

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    # Stop service
    code, stdout, stderr = run_compose(
        "stop",
        services=[service],
        extra_args=["-t", str(timeout)],
    )
    if code != 0:
        return code, stdout, stderr

    # Start service
    code, stdout, stderr = run_compose("start", services=[service])
    if code != 0:
        return code, stdout, stderr

    if wait_healthy:
        if not wait_for_services([service], timeout=timeout):
            return 1, "", f"Service {service} did not become healthy in {timeout}s"

    return 0, "", ""


def get_container_status(container_name: str) -> dict:
    """Get detailed status of a container.

    Args:
        container_name: Name of the container

    Returns:
        Dict with status info
    """
    code, output, _ = run_command(
        [
            "docker",
            "ps",
            "--filter",
            f"name={container_name}",
            "--format",
            "{{.Names}}|{{.Status}}|{{.Ports}}|{{.Image}}",
        ],
        capture_output=True,
        check=False,
    )

    if code != 0 or not output.strip():
        return {
            "running": False,
            "status": "not_found",
            "ports": "",
            "image": "",
        }

    lines = output.strip().split("\n")
    if not lines or not lines[0]:
        return {
            "running": False,
            "status": "not_found",
            "ports": "",
            "image": "",
        }

    parts = lines[0].split("|")
    return {
        "running": True,
        "status": parts[1] if len(parts) > 1 else "unknown",
        "ports": parts[2] if len(parts) > 2 else "",
        "image": parts[3] if len(parts) > 3 else "",
    }


def stop_container(container_name: str, timeout: int = 10) -> tuple[int, str, str]:
    """Stop a container gracefully.

    Args:
        container_name: Name of the container
        timeout: Seconds to wait before killing

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = ["docker", "stop", "-t", str(timeout), container_name]
    return run_command(cmd, capture_output=True, check=False)


def start_container(container_name: str) -> tuple[int, str, str]:
    """Start a stopped container.

    Args:
        container_name: Name of the container

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = ["docker", "start", container_name]
    return run_command(cmd, capture_output=True, check=False)


def remove_container(container_name: str, force: bool = False) -> tuple[int, str, str]:
    """Remove a container.

    Args:
        container_name: Name of the container
        force: Force removal (even if running)

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = ["docker", "rm"]
    if force:
        cmd.append("-f")
    cmd.append(container_name)
    return run_command(cmd, capture_output=True, check=False)


def inspect_container(container_name: str) -> tuple[int, str, str]:
    """Get detailed container information.

    Args:
        container_name: Name of the container

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = ["docker", "inspect", container_name]
    return run_command(cmd, capture_output=True, check=False)


def pull_image(image_name: str) -> tuple[int, str, str]:
    """Pull a Docker image.

    Args:
        image_name: Full image name with tag

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = ["docker", "pull", image_name]
    return run_command(cmd, capture_output=True, check=False)


def get_container_health(container_name: str) -> str:
    """Get container health status.

    Args:
        container_name: Name of the container

    Returns:
        Health status string (empty if not tracked)
    """
    code, output, _ = run_command(
        [
            "docker",
            "ps",
            "--filter",
            f"name={container_name}",
            "--format",
            "{{.Health}}",
        ],
        capture_output=True,
        check=False,
    )

    if code == 0 and output.strip():
        return output.strip()
    return ""


def get_container_ip(container_name: str) -> str:
    """Get container IP address.

    Args:
        container_name: Name of the container

    Returns:
        IP address string
    """
    code, output, _ = run_command(
        [
            "docker",
            "inspect",
            container_name,
            "--format",
            "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
        ],
        capture_output=True,
        check=False,
    )

    if code == 0 and output.strip():
        return output.strip()
    return ""


def rebuild_service(
    service: str,
    no_cache: bool = False,
    pull: bool = False,
    wait_healthy: bool = True,
    timeout: int = 120,
) -> tuple[int, str, str]:
    """Rebuild and restart a service with updated code.

    Args:
        service: Service name to rebuild
        no_cache: Don't use build cache
        pull: Always pull base image
        wait_healthy: Wait for service to be healthy
        timeout: Build/restart timeout in seconds

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    code, stdout, stderr = build_image(
        service,
        no_cache=no_cache,
        pull=pull,
    )
    if code != 0:
        return code, stdout, stderr

    code, stdout, stderr = restart_service(
        service,
        timeout=timeout,
        wait_healthy=wait_healthy,
    )
    return code, stdout, stderr


def get_all_containers() -> list[dict]:
    """Get status of all containers.

    Returns:
        List of container status dicts
    """
    code, output, _ = run_command(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}|{{.Status}}|{{.Ports}}|{{.Image}}",
        ],
        capture_output=True,
        check=False,
    )

    containers = []
    if code == 0 and output.strip():
        for line in output.strip().split("\n"):
            if line:
                parts = line.split("|")
                containers.append({
                    "name": parts[0] if len(parts) > 0 else "",
                    "status": parts[1] if len(parts) > 1 else "",
                    "ports": parts[2] if len(parts) > 2 else "",
                    "image": parts[3] if len(parts) > 3 else "",
                })

    return containers


def is_service_healthy(service_name: str) -> bool:
    """Check if a service is healthy.

    Args:
        service_name: Service name to check

    Returns:
        True if healthy
    """
    container_names = get_container_names()
    container_name = container_names.get(service_name)
    if not container_name:
        return False

    health = get_container_health(container_name)
    return health.lower() in ["healthy", "running"]


def wait_for_service(
    service_name: str,
    timeout: int = 60,
    interval: int = 2,
) -> bool:
    """Wait for a service to become healthy.

    Args:
        service_name: Service name to wait for
        timeout: Wait timeout in seconds
        interval: Polling interval in seconds

    Returns:
        True if healthy within timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if is_service_healthy(service_name):
            return True
        time.sleep(interval)
    
    return False


def exec_in_container(
    container_name: str,
    command: list[str],
    capture_output: bool = True,
) -> tuple[int, str, str]:
    """Execute a command inside a running container.

    Args:
        container_name: Name of the container
        command: Command to execute as list
        capture_output: Whether to capture stdout/stderr

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    cmd = ["docker", "exec", container_name] + command
    return run_command(cmd, capture_output=capture_output, check=False)


def get_container_env(
    container_name: str,
    env_var: str | None = None,
) -> dict[str, str] | str:
    """Get environment variables from a container.

    Args:
        container_name: Name of the container
        env_var: Optional specific variable to get

    Returns:
        Dict of all env vars or value of specific var
    """
    code, output, _ = run_command(
        ["docker", "exec", container_name, "env"],
        capture_output=True,
        check=False,
    )

    if code != 0:
        return {} if env_var is None else ""

    env_vars = {}
    for line in output.strip().split("\n"):
        if "=" in line:
            key, value = line.split("=", 1)
            env_vars[key] = value

    if env_var:
        return env_vars.get(env_var, "")
    return env_vars


def check_container_healthcheck(container_name: str) -> dict:
    """Check container healthcheck status.

    Args:
        container_name: Name of the container

    Returns:
        Dict with healthcheck details
    """
    code, output, _ = run_command(
        [
            "docker",
            "inspect",
            container_name,
            "--format",
            "{{json .State.Health}}",
        ],
        capture_output=True,
        check=False,
    )

    if code != 0:
        return {"status": "not_found"}

    import json

    try:
        health = json.loads(output.strip()) if output.strip() else {}
        return {
            "status": health.get("Status", "unknown") if health else "no_healthcheck",
            "failing_streak": health.get("FailingStreak", 0) if health else 0,
            "log": health.get("Log", []) if health else [],
        }
    except json.JSONDecodeError:
        return {"status": "parse_error"}


def service_logs(
    service_name: str,
    tail: int = 50,
    follow: bool = False,
    timestamps: bool = False,
) -> tuple[int, str, str]:
    """Get logs for a service.

    Args:
        service_name: Service name
        tail: Number of lines
        follow: Whether to follow logs
        timestamps: Whether to show timestamps

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    container_names = get_container_names()
    container_name = container_names.get(service_name)
    if not container_name:
        return 1, "", f"Service {service_name} not found"

    cmd = ["docker", "logs"]
    if follow:
        cmd.append("-f")
    else:
        cmd.extend(["-n", str(tail)])
    if timestamps:
        cmd.append("-t")
    cmd.append(container_name)

    return run_command(cmd, capture_output=not follow, check=False)


def container_exists(container_name: str) -> bool:
    """Check if a container exists.

    Args:
        container_name: Name of the container

    Returns:
        True if container exists
    """
    code, _, _ = run_command(
        ["docker", "inspect", container_name],
        capture_output=True,
        check=False,
    )
    return code == 0


def container_is_running(container_name: str) -> bool:
    """Check if a container is running (not just exists).

    Args:
        container_name: Name of the container

    Returns:
        True if container is running
    """
    status = get_container_status(container_name)
    return status.get("running", False)


def get_container_id(container_name: str) -> str:
    """Get container ID by name.

    Args:
        container_name: Name of the container

    Returns:
        Container ID string
    """
    code, output, _ = run_command(
        [
            "docker",
            "ps",
            "--filter",
            f"name={container_name}",
            "--format",
            "{{.ID}}",
        ],
        capture_output=True,
        check=False,
    )

    if code == 0 and output.strip():
        return output.strip()
    return ""


def pull_and_update(
    service: str,
    wait_healthy: bool = True,
    timeout: int = 120,
) -> tuple[int, str, str]:
    """Pull latest image and rebuild service.

    Args:
        service: Service name
        wait_healthy: Wait for health
        timeout: Timeout in seconds

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    container_names = get_container_names()
    container_name = container_names.get(service)
    
    if container_name:
        code, stdout, stderr = stop_container(container_name)
        if code != 0:
            return code, stdout, stderr

    code, stdout, stderr = run_compose(
        "pull",
        services=[service] if service else None,
    )
    if code != 0:
        return code, stdout, stderr

    code, stdout, stderr = build_image(
        service,
        no_cache=True,
        pull=True,
    )
    if code != 0:
        return code, stdout, stderr

    if container_name:
        code, stdout, stderr = start_container(container_name)
        if code != 0:
            return code, stdout, stderr

        if wait_healthy:
            if not wait_for_service(service, timeout=timeout):
                return 1, "", f"Service {service} did not become healthy"

    return 0, "", ""


def get_container_stats(container_name: str) -> dict:
    """Get container resource usage stats.

    Args:
        container_name: Name of the container

    Returns:
        Dict with stats
    """
    code, output, _ = run_command(
        [
            "docker",
            "stats",
            container_name,
            "--no-stream",
            "--format",
            "{{.Name}}|{{.CPUPerc}}|{{.MemUsage}}|{{.MemPerc}}|{{.NetIO}}|{{.BlockIO}}",
        ],
        capture_output=True,
        check=False,
    )

    if code != 0 or not output.strip():
        return {
            "name": container_name,
            "cpu": "N/A",
            "memory": "N/A",
            "memory_percent": "N/A",
            "network": "N/A",
            "block": "N/A",
        }

    parts = output.strip().split("|")
    return {
        "name": parts[0] if len(parts) > 0 else container_name,
        "cpu": parts[1] if len(parts) > 1 else "N/A",
        "memory": parts[2] if len(parts) > 2 else "N/A",
        "memory_percent": parts[3] if len(parts) > 3 else "N/A",
        "network": parts[4] if len(parts) > 4 else "N/A",
        "block": parts[5] if len(parts) > 5 else "N/A",
    }


def is_port_published(container_name: str, port: int) -> bool:
    """Check if a specific port is published.

    Args:
        container_name: Name of the container
        port: Port number

    Returns:
        True if port is published
    """
    status = get_container_status(container_name)
    ports_str = status.get("ports", "")
    return f":{port}->" in ports_str


def get_container_uptime(container_name: str) -> str:
    """Get container uptime.

    Args:
        container_name: Name of the container

    Returns:
        Uptime string
    """
    code, output, _ = run_command(
        [
            "docker",
            "ps",
            "--filter",
            f"name={container_name}",
            "--format",
            "{{.RunningFor}}",
        ],
        capture_output=True,
        check=False,
    )

    if code == 0 and output.strip():
        return output.strip()
    return "unknown"


def stop_and_remove_container(container_name: str, force: bool = False) -> tuple[int, str, str]:
    """Stop and remove a container.

    Args:
        container_name: Name of the container
        force: Force removal (even if running)

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    if container_is_running(container_name):
        code, stdout, stderr = stop_container(container_name)
        if code != 0:
            return code, stdout, stderr

    return remove_container(container_name, force=force)


def restart_with_rebuild(
    service: str,
    no_cache: bool = False,
    pull: bool = False,
    wait_healthy: bool = True,
    timeout: int = 120,
) -> tuple[int, str, str]:
    """Restart a service with full rebuild.

    Args:
        service: Service name to restart
        no_cache: Don't use build cache
        pull: Always pull base image
        wait_healthy: Wait for service to be healthy
        timeout: Build/restart timeout in seconds

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    container_names = get_container_names()
    container_name = container_names.get(service)

    if container_name and container_is_running(container_name):
        code, stdout, stderr = stop_container(container_name)
        if code != 0:
            return code, stdout, stderr

    code, stdout, stderr = rebuild_service(
        service,
        no_cache=no_cache,
        pull=pull,
        wait_healthy=wait_healthy,
        timeout=timeout,
    )
    return code, stdout, stderr


def get_all_services_status() -> list[dict]:
    """Get status of all defined services.

    Returns:
        List of service status dicts with name, running, status, ports, image
    """
    services_status = []
    container_names = get_container_names()

    for service_name, container_name in container_names.items():
        status = get_container_status(container_name)
        services_status.append({
            "name": service_name,
            "container_name": container_name,
            "running": status.get("running", False),
            "status": status.get("status", "not_found"),
            "ports": status.get("ports", ""),
            "image": status.get("image", ""),
        })

    return services_status


def get_services_by_status(status: str = "running") -> list[str]:
    """Get list of services by status.

    Args:
        status: Status to filter by (running, stopped, not_found)

    Returns:
        List of service names matching status
    """
    services = get_all_services_status()
    if status == "running":
        return [s["name"] for s in services if s["running"]]
    elif status == "stopped":
        return [s["name"] for s in services if not s["running"] and s["status"] != "not_found"]
    elif status == "not_found":
        return [s["name"] for s in services if s["status"] == "not_found"]
    return []


def wait_for_containers(
    container_names: list[str],
    timeout: int = 60,
    interval: int = 2,
) -> tuple[bool, dict[str, bool]]:
    """Wait for multiple containers to become healthy.

    Args:
        container_names: List of container names
        timeout: Total timeout in seconds
        interval: Polling interval in seconds

    Returns:
        Tuple of (all_healthy, dict of container -> is_healthy)
    """
    start_time = time.time()
    healthy = {name: False for name in container_names}

    while time.time() - start_time < timeout:
        all_healthy = True
        for container_name in container_names:
            if not healthy[container_name]:
                health = get_container_health(container_name)
                if health.lower() in ["healthy", "running"]:
                    healthy[container_name] = True
                else:
                    all_healthy = False

        if all_healthy:
            return True, healthy

        time.sleep(interval)

    return False, healthy


def service_exec(
    service_name: str,
    command: list[str],
    capture_output: bool = True,
) -> tuple[int, str, str]:
    """Execute command in a service container.

    Args:
        service_name: Service name
        command: Command to execute as list
        capture_output: Whether to capture stdout/stderr

    Returns:
        Tuple of (returncode, stdout, stderr)
    """
    container_names = get_container_names()
    container_name = container_names.get(service_name)

    if not container_name:
        return 1, "", f"Service {service_name} not found"

    return exec_in_container(container_name, command, capture_output=capture_output)


def get_service_env(
    service_name: str,
    env_var: str | None = None,
) -> dict[str, str] | str:
    """Get environment variables from a service container.

    Args:
        service_name: Service name
        env_var: Optional specific variable to get

    Returns:
        Dict of all env vars or value of specific var
    """
    container_names = get_container_names()
    container_name = container_names.get(service_name)

    if not container_name:
        return {} if env_var is None else ""

    return get_container_env(container_name, env_var=env_var)


def service_healthcheck(service_name: str) -> dict:
    """Check healthcheck status for a service.

    Args:
        service_name: Service name

    Returns:
        Dict with healthcheck details
    """
    container_names = get_container_names()
    container_name = container_names.get(service_name)

    if not container_name:
        return {"status": "not_found"}

    return check_container_healthcheck(container_name)
