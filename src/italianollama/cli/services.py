import os
import shlex
import signal
import subprocess
import time

import click
import psutil


def get_services():
    """Return the services configuration, allowing for port overrides."""
    api_port = int(os.getenv("API_PORT", 8000))
    chainlit_port = int(os.getenv("CHAINLIT_PORT", 8501))
    streamlit_port = int(os.getenv("STREAMLIT_PORT", 8502))

    return {
        "api": {
            "command": f"poetry run uvicorn src.italianollama.api.main:app --host 127.0.0.1 --port {api_port}",
            "port": api_port,
            "keywords": ["uvicorn", "api.main"],
        },
        "chainlit": {
            "command": f"poetry run chainlit run src/italianollama/frontend/chainlit_app.py --port {chainlit_port}",
            "port": chainlit_port,
            "keywords": ["chainlit", "chainlit_app"],
        },
        "streamlit": {
            "command": f"poetry run streamlit run src/italianollama/frontend/streamlit/app_enhanced.py --server.port {streamlit_port}",
            "port": streamlit_port,
            "keywords": ["streamlit", "app_enhanced.py"],
            "env": {
                "CHAINLIT_URL": f"http://localhost:{chainlit_port}",
                "BACKEND_URL": os.getenv("BACKEND_URL", f"http://localhost:{api_port}"),
            },
        },
    }


def get_process_by_port(port, keywords=None):
    """Find a process listening on a port, and detect SSH tunnels."""
    is_tunnel = False
    found_proc = None

    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline_list = proc.info.get("cmdline") or []
            cmdline = " ".join(cmdline_list)
            name = (proc.info.get("name") or "").lower()

            # Check for SSH tunnel
            is_ssh = "ssh" in name or "-L" in cmdline

            for conn in proc.connections(kind="inet"):
                if conn.laddr.port == port and conn.status == "LISTEN":
                    if is_ssh:
                        is_tunnel = True
                        found_proc = proc
                        # Keep looking for a local service that might be on the same port
                        continue

                    # If we have keywords, ensure one matches the cmdline
                    if keywords:
                        if any(kw.lower() in cmdline.lower() for kw in keywords):
                            return proc, False
                        continue
                    return proc, False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception:
            continue

    if is_tunnel:
        return found_proc, True

    return None, False


def kill_proc_tree(pid, sig=signal.SIGTERM, include_parent=True, timeout=5):
    """Kill a process tree (process and all its children)."""
    try:
        parent = psutil.Process(pid)
    except psutil.NoSuchProcess:
        return

    children = parent.children(recursive=True)
    for child in children:
        try:
            child.send_signal(sig)
        except psutil.NoSuchProcess:
            pass

    if include_parent:
        try:
            parent.send_signal(sig)
        except psutil.NoSuchProcess:
            pass

    _, alive = psutil.wait_procs(children + ([parent] if include_parent else []), timeout=timeout)
    for p in alive:
        try:
            p.kill()
        except psutil.NoSuchProcess:
            pass


def is_service_running(name):
    services = get_services()
    svc = services.get(name)
    if not svc:
        return False
    proc, is_tunnel = get_process_by_port(svc["port"], svc.get("keywords"))
    return proc is not None


def start_service(name):
    services = get_services()
    proc, is_tunnel = get_process_by_port(services[name]["port"], services[name].get("keywords"))
    if proc:
        status_text = "REMOTE (TUNNEL)" if is_tunnel else "locally running"
        click.secho(
            f"⚠ Service '{name}' is already provided by a {status_text} process on port {services[name]['port']}.",
            fg="yellow",
        )
        return

    svc = services[name]
    click.echo(f"🚀 Starting {name} on port {svc['port']}...")

    env = os.environ.copy()
    if "env" in svc:
        env.update(svc["env"])

    os.makedirs("logs", exist_ok=True)
    log_file = open(f"logs/{name}.log", "a")

    process = subprocess.Popen(
        shlex.split(svc["command"]),
        stdout=log_file,
        stderr=subprocess.STDOUT,
        env=env,
        start_new_session=True,
    )

    # Wait for the port to actually open
    for _ in range(10):
        time.sleep(1)
        if is_service_running(name):
            click.secho(f"✓ {name} started successfully (PID: {process.pid})", fg="green")
            return
        if process.poll() is not None:
            click.secho(f"✗ Failed to start {name}. Check logs/{name}.log", fg="red")
            return

    click.secho(
        f"⚠ {name} started (PID: {process.pid}), but port {svc['port']} is not yet listening.",
        fg="yellow",
    )


def stop_service(name):
    services = get_services()
    svc = services.get(name)
    proc, is_tunnel = get_process_by_port(svc["port"], svc.get("keywords"))
    if proc:
        if is_tunnel:
            click.secho(
                f"⚠ Cannot stop '{name}': it is a REMOTE (TUNNEL) process (PID: {proc.pid}).",
                fg="yellow",
            )
            return
        click.echo(f"🛑 Stopping {name} (PID: {proc.pid})...")
        kill_proc_tree(proc.pid)
        click.secho(f"✓ {name} stopped.", fg="green")
    else:
        click.secho(f"⚠ Service '{name}' is not running.", fg="yellow")


def get_status():
    services = get_services()
    click.echo("\nService Status:")
    click.echo("-" * 60)
    for name, info in services.items():
        proc, is_tunnel = get_process_by_port(info["port"], info.get("keywords"))
        if proc:
            status = (
                click.style("REMOTE (TUNNEL)", fg="blue")
                if is_tunnel
                else click.style("RUNNING", fg="green")
            )
            pid_info = f"(PID: {proc.pid})"
        else:
            status = click.style("STOPPED", fg="red")
            pid_info = ""

        click.echo(f"{name:12} | {status:25} | Port: {info['port']:5} {pid_info}")
    click.echo("-" * 60)
