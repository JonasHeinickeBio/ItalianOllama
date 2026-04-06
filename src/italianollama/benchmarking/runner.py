"""Benchmark runner for executing tests."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .base import Benchmark, BenchmarkResult
from .config import BenchmarkConfig
from .reporters import BaseReporter, ConsoleReporter, CSVReporter, JSONReporter


class BenchmarkRunner:
    """Runner for executing benchmarks."""
    
    def __init__(self, config: Optional[BenchmarkConfig] = None):
        self.config = config or BenchmarkConfig()
        self.benchmarks: List[Benchmark] = []
        self.results: List[BenchmarkResult] = []
        self.reporters: List[BaseReporter] = []
    
    def add_benchmark(self, benchmark: Benchmark) -> "BenchmarkRunner":
        """Add a benchmark to run."""
        self.benchmarks.append(benchmark)
        return self
    
    def add_benchmarks(self, benchmarks: List[Benchmark]) -> "BenchmarkRunner":
        """Add multiple benchmarks."""
        self.benchmarks.extend(benchmarks)
        return self
    
    def add_reporter(self, reporter: BaseReporter) -> "BenchmarkRunner":
        """Add a reporter for output."""
        self.reporters.append(reporter)
        return self
    
    def configure_reporters(self, output_dir: Optional[str] = None) -> None:
        """Configure reporters based on config."""
        output_dir = output_dir or self.config.output_dir
        output_path = Path(output_dir)
        
        for fmt in self.config.output_format:
            if fmt == "console":
                self.add_reporter(ConsoleReporter(verbose=self.config.verbose))
            elif fmt == "json":
                self.add_reporter(JSONReporter(output_path / "results.json"))
            elif fmt == "csv":
                self.add_reporter(CSVReporter(output_path / "results.csv"))
    
    def run(self, *args: Any, **kwargs: Any) -> List[BenchmarkResult]:
        """Run all benchmarks."""
        self.results = []
        
        for benchmark in self.benchmarks:
            try:
                if self.config.warmup_iterations > 0:
                    benchmark.run_multiple(self.config.warmup_iterations, *args, **kwargs)
                
                results = benchmark.run_multiple(self.config.iterations, *args, **kwargs)
                self.results.extend(results)
                
                if self.config.verbose:
                    print(f"Completed benchmark: {benchmark.name}")
            
            except Exception as e:
                if self.config.verbose:
                    print(f"Error running benchmark {benchmark.name}: {e}")
        
        self._generate_reports()
        return self.results
    
    def _generate_reports(self) -> None:
        """Generate reports for all results."""
        for reporter in self.reporters:
            reporter.results = self.results
            reporter.report()
            if reporter.output_path:
                reporter.save()
