"""Example benchmarks for ItalianOllama."""

import os
import tempfile
from pathlib import Path

from base import BenchmarkRunner, BenchmarkConfig
from file_io import FileWriteBenchmark, FileReadBenchmark
from llm import ResponseTimeBenchmark
from container import CPUBenchmark, MemoryBenchmark


def run_all_benchmarks():
    """Run all benchmarks and generate reports."""
    config = BenchmarkConfig(
        name="italianollama_benchmarks",
        iterations=3,
        warmup_iterations=1,
        output_dir="./benchmark_results",
        output_format=["console", "json", "csv"],
        verbose=True,
    )
    
    runner = BenchmarkRunner(config=config)
    runner.configure_reporters()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = os.path.join(tmpdir, "test_file.txt")
        
        file_write_benchmark = FileWriteBenchmark(
            filepath=filepath,
            size=1024,
            iterations=3,
        )
        
        file_read_benchmark = FileReadBenchmark(
            filepath=filepath,
            iterations=3,
        )
        
        cpu_benchmark = CPUBenchmark(
            duration=2.0,
            interval=0.1,
        )
        
        memory_benchmark = MemoryBenchmark(
            duration=2.0,
            interval=0.1,
        )
        
        runner.add_benchmarks([
            file_write_benchmark,
            file_read_benchmark,
            cpu_benchmark,
            memory_benchmark,
        ])
        
        results = runner.run()
        
        return results


if __name__ == "__main__":
    run_all_benchmarks()
