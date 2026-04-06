"""Benchmarking CLI commands for ItalianOllama.

Usage:
    python cli.py benchmark --help
    python cli.py benchmark system
    python cli.py benchmark llm
    python cli.py benchmark container
    python cli.py benchmark file
"""

import os
import sys
import asyncio

import click

from italianollama.cli.docker_helpers import (
    check_container_running,
    get_container_names,
    run_compose,
    run_command,
)


@click.group()
def benchmark():
    """Run system benchmarks."""
    pass


@benchmark.command()
@click.option(
    "--profile",
    "-p",
    type=click.Choice(["local", "cloud", "blablador-only", "aura"]),
    default="local",
    help="Docker Compose profile to use",
)
@click.option(
    "--model",
    "-m",
    default=None,
    help="Ollama model to pull and benchmark",
)
@click.option(
    "--iterations",
    "-i",
    default=3,
    type=int,
    help="Number of benchmark iterations",
)
@click.option(
    "--output",
    "-o",
    default="benchmark_results",
    help="Output directory for results",
)
def system(profile, model, iterations, output):
    """Run comprehensive system benchmarks."""
    from italianollama.benchmarking.config import BenchmarkConfig
    from italianollama.benchmarking.runner import BenchmarkRunner
    from italianollama.benchmarking.reporters import ConsoleReporter, JSONReporter, CSVReporter
    
    click.echo("=" * 60)
    click.echo("Starting Comprehensive System Benchmark")
    click.echo("=" * 60)
    
    config = BenchmarkConfig(
        name="system_benchmark",
        iterations=iterations,
        warmup_iterations=1,
        output_dir=output,
        output_format=["console", "json", "csv"],
        verbose=True,
    )
    
    runner = BenchmarkRunner(config=config)
    runner.add_reporter(ConsoleReporter(verbose=True))
    
    # Check Docker
    click.echo("\n✓ Checking Docker environment...")
    
    code, _, _ = run_command(["docker", "info"], capture_output=True, check=False)
    if code != 0:
        click.secho("✗ Docker is not running", fg="red")
        return 1
    
    # Start containers if needed
    if profile == "local":
        click.echo("\n✓ Starting local containers...")
        
        if not check_container_running("italian-tutor-ollama"):
            code, stdout, stderr = run_compose("up", profile=profile, detach=True)
            if code == 0:
                click.secho("✓ Containers started", fg="green")
            else:
                click.secho("✗ Failed to start containers", fg="red")
                if stderr:
                    click.echo(stderr, err=True)
                return 1
    
    # Pull model if needed
    if model or profile == "local":
        ollama_model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        click.echo(f"\n✓ Pulling Ollama model: {ollama_model}")
        
        code, stdout, stderr = run_command(
            ["ollama", "pull", ollama_model],
            capture_output=True,
            check=False,
        )
        
        if code == 0:
            click.secho(f"✓ Model {ollama_model} pulled successfully", fg="green")
        else:
            click.secho(f"✗ Failed to pull model: {stderr}", fg="red")
            return 1
    
    # Import benchmark modules
    try:
        from italianollama.benchmarking.container import (
            CPUBenchmark,
            MemoryBenchmark,
            IOMBenchmark,
        )
        from italianollama.benchmarking.file_io import FileWriteBenchmark, FileReadBenchmark
        from italianollama.benchmarking.llm import ResponseTimeBenchmark
        from italianollama.memory.neo4j_client import Neo4jClient
    except ImportError as e:
        click.secho(f"✗ Failed to import benchmark modules: {e}", fg="red")
        return 1
    
    # Create LLM client
    try:
        from italianollama.graph.nodes.base import LLMClient
        llm_client = LLMClient()
    except Exception as e:
        click.secho(f"✗ Failed to create LLM client: {e}", fg="red")
        return 1
    
    # Run benchmarks
    click.echo("\n" + "=" * 60)
    click.echo("Running Benchmarks")
    click.echo("=" * 60)
    
    # File I/O benchmarks
    click.echo("\n📁 Running file I/O benchmarks...")
    try:
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "benchmark_test.txt")
            
            file_write = FileWriteBenchmark(
                filepath=test_file,
                size=1024 * 1024,  # 1MB
                iterations=iterations,
            )
            
            file_read = FileReadBenchmark(
                filepath=test_file,
                iterations=iterations,
            )
            
            runner.add_benchmark(file_write)
            runner.add_benchmark(file_read)
            
            runner.run()
    except Exception as e:
        click.secho(f"✗ File I/O benchmark failed: {e}", fg="yellow")
    
    # Container benchmarks
    click.echo("\n📦 Running container benchmarks...")
    try:
        cpu_bench = CPUBenchmark(
            duration=5.0,
            interval=0.1,
        )
        
        memory_bench = MemoryBenchmark(
            duration=5.0,
            interval=0.1,
        )
        
        runner.add_benchmark(cpu_bench)
        runner.add_benchmark(memory_bench)
        
        runner.run()
    except Exception as e:
        click.secho(f"✗ Container benchmark failed: {e}", fg="yellow")
    
    # LLM benchmarks
    click.echo("\n🤖 Running LLM benchmarks...")
    try:
        test_prompt = "Say 'Ciao' in one word."
        
        llm_bench = ResponseTimeBenchmark(
            llm_client=llm_client,
            prompt=test_prompt,
            iterations=iterations,
        )
        
        runner.add_benchmark(llm_bench)
        
        runner.run()
    except Exception as e:
        click.secho(f"✗ LLM benchmark failed: {e}", fg="yellow")
    
    # Database benchmarks
    click.echo("\n💾 Running database benchmarks...")
    try:
        from italianollama.api.config import get_settings
        settings = get_settings()
        
        async def run_db_bench():
            client = Neo4jClient(
                uri=settings.neo4j_uri,
                user=settings.neo4j_user,
                password=settings.neo4j_password,
                database=settings.neo4j_database,
            )
            await client.connect()
            
            try:
                async with client._driver.session(database=client.database) as session:
                    # Simple query benchmark
                    start_time = __import__("time").perf_counter()
                    result = await session.run("RETURN 1 AS test")
                    await result.data()
                    duration = __import__("time").perf_counter() - start_time
                    
                    click.echo(f"✓ Database query executed in {duration:.4f}s")
            finally:
                await client.close()
        
        import asyncio
        asyncio.run(run_db_bench())
    except Exception as e:
        click.secho(f"⚠ Database benchmark skipped: {e}", fg="yellow")
    
    click.echo("\n" + "=" * 60)
    click.echo("Benchmark Complete!")
    click.echo("=" * 60)
    click.echo(f"\nResults saved to: {output}/")
    
    return 0


@benchmark.command()
@click.option(
    "--iterations",
    "-i",
    default=3,
    type=int,
    help="Number of benchmark iterations",
)
@click.option(
    "--output",
    "-o",
    default="benchmark_results/llm",
    help="Output directory for results",
)
def llm(iterations, output):
    """Run LLM-specific benchmarks."""
    from italianollama.benchmarking.config import BenchmarkConfig
    from italianollama.benchmarking.runner import BenchmarkRunner
    from italianollama.benchmarking.llm import ResponseTimeBenchmark, TokenBenchmark
    
    click.echo("Running LLM benchmarks...")
    
    config = BenchmarkConfig(
        name="llm_benchmark",
        iterations=iterations,
        output_dir=output,
        verbose=True,
    )
    
    runner = BenchmarkRunner(config=config)
    runner.configure_reporters(output)
    
    # Create LLM client
    try:
        from italianollama.graph.nodes.base import LLMClient
        llm_client = LLMClient()
    except Exception as e:
        click.secho(f"✗ Failed to create LLM client: {e}", fg="red")
        return 1
    
    # Response time benchmark
    prompt = "Describe Italian cuisine in 3 sentences."
    
    response_bench = ResponseTimeBenchmark(
        llm_client=llm_client,
        prompt=prompt,
        iterations=iterations,
        name="llm_response_time",
    )
    
    runner.add_benchmark(response_bench)
    
    # Run
    runner.run()
    
    click.echo(f"\nLLM benchmarks complete! Results: {output}/")
    
    return 0


@benchmark.command()
@click.option(
    "--duration",
    "-d",
    default=5.0,
    type=float,
    help="Duration per benchmark (seconds)",
)
@click.option(
    "--output",
    "-o",
    default="benchmark_results/container",
    help="Output directory for results",
)
def container(duration, output):
    """Run container performance benchmarks."""
    from italianollama.benchmarking.config import BenchmarkConfig
    from italianollama.benchmarking.runner import BenchmarkRunner
    from italianollama.benchmarking.container import CPUBenchmark, MemoryBenchmark
    
    click.echo("Running container benchmarks...")
    
    config = BenchmarkConfig(
        name="container_benchmark",
        iterations=3,
        output_dir=output,
        verbose=True,
    )
    
    runner = BenchmarkRunner(config=config)
    runner.configure_reporters(output)
    
    # CPU benchmark
    cpu_bench = CPUBenchmark(
        duration=duration,
        interval=0.1,
        name="cpu_usage",
    )
    
    # Memory benchmark
    memory_bench = MemoryBenchmark(
        duration=duration,
        interval=0.1,
        name="memory_usage",
    )
    
    runner.add_benchmark(cpu_bench)
    runner.add_benchmark(memory_bench)
    
    runner.run()
    
    click.echo(f"\nContainer benchmarks complete! Results: {output}/")
    
    return 0


@benchmark.command()
@click.option(
    "--iterations",
    "-i",
    default=3,
    type=int,
    help="Number of benchmark iterations",
)
@click.option(
    "--output",
    "-o",
    default="benchmark_results/file",
    help="Output directory for results",
)
def file(iterations, output):
    """Run file I/O benchmarks."""
    from italianollama.benchmarking.config import BenchmarkConfig
    from italianollama.benchmarking.runner import BenchmarkRunner
    from italianollama.benchmarking.file_io import FileWriteBenchmark, FileReadBenchmark
    
    click.echo("Running file I/O benchmarks...")
    
    config = BenchmarkConfig(
        name="file_benchmark",
        iterations=iterations,
        output_dir=output,
        verbose=True,
    )
    
    runner = BenchmarkRunner(config=config)
    runner.configure_reporters(output)
    
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "benchmark_test.txt")
        
        file_write = FileWriteBenchmark(
            filepath=test_file,
            size=1024 * 1024,  # 1MB
            iterations=iterations,
            name="file_write_1mb",
        )
        
        file_read = FileReadBenchmark(
            filepath=test_file,
            iterations=iterations,
            name="file_read_1mb",
        )
        
        runner.add_benchmark(file_write)
        runner.add_benchmark(file_read)
        
        runner.run()
    
    click.echo(f"\nFile I/O benchmarks complete! Results: {output}/")
    
    return 0


@benchmark.command()
def check():
    """Check benchmarking system status."""
    click.echo("Benchmarking System Check")
    click.echo("=" * 60)
    
    # Check Docker
    click.echo("\nDocker:")
    code, _, _ = run_command(["docker", "--version"], capture_output=True, check=False)
    if code == 0:
        click.echo("  ✓ Docker installed")
    else:
        click.echo("  ✗ Docker not installed")
    
    # Check Ollama
    click.echo("\nOllama:")
    code, _, _ = run_command(["ollama", "--version"], capture_output=True, check=False)
    if code == 0:
        click.echo("  ✓ Ollama installed")
    else:
        click.echo("  ✗ Ollama not installed")
    
    # Check benchmark modules
    click.echo("\nBenchmark modules:")
    try:
        from italianollama.benchmarking import BenchmarkRunner, BenchmarkConfig
        click.echo("  ✓ Benchmark core modules")
    except ImportError as e:
        click.echo(f"  ✗ Core modules: {e}")
    
    try:
        from italianollama.benchmarking.llm import ResponseTimeBenchmark
        click.echo("  ✓ LLM benchmark modules")
    except ImportError as e:
        click.echo(f"  ✗ LLM benchmarks: {e}")
    
    try:
        from italianollama.benchmarking.container import CPUDuration, MemoryBenchmark
        click.echo("  ✓ Container benchmark modules")
    except ImportError as e:
        click.echo(f"  ✗ Container benchmarks: {e}")
    
    click.echo("\n" + "=" * 60)
    click.echo("Benchmarking system ready!")
    
    return 0


@click.group()
def cli():
    """ItalianTutor - AI-powered Italian Language Learning."""
    pass


cli.add_command(benchmark)


if __name__ == "__main__":
    cli()
