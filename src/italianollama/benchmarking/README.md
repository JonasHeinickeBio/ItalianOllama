# ItalianOllama Benchmarking Module

A modular and reusable benchmarking framework for the ItalianOllama project.

## Features

- **Modular Design**: Easy to add new benchmark types
- **Reusable Components**: Base classes and decorators for common patterns
- **Configurable Tests**: Flexible parameter configuration
- **Multiple Output Formats**: Console, JSON, and CSV reports

## Directory Structure

```
src/italianollama/benchmarking/
├── __init__.py          # Module exports
├── base.py              # Core base classes
├── config.py            # Configuration management
├── decorators.py        # Benchmark decorators
├── reporters.py         # Output reporters (console, JSON, CSV)
├── runner.py            # Benchmark runner
├── utils.py             # Utility functions
├── tests.py             # Unit tests
├── examples.py          # Example usage
├── file_io.py           # File I/O benchmarks
├── database.py          # Database query benchmarks
├── llm.py               # LLM response benchmarks
└── container.py         # Container performance benchmarks
```

## Quick Start

```python
from italianollama.benchmarking import (
    BenchmarkRunner,
    BenchmarkConfig,
    FileWriteBenchmark,
)

# Configure benchmark
config = BenchmarkConfig(
    iterations=5,
    output_format=["console", "json"],
)

# Create runner
runner = BenchmarkRunner(config=config)
runner.configure_reporters()

# Add benchmark
benchmark = FileWriteBenchmark(
    filepath="/tmp/test.txt",
    size=1024,
    iterations=5,
)

runner.add_benchmark(benchmark)
results = runner.run()
```

## Benchmark Types

### File I/O Benchmarks
- `FileWriteBenchmark`: Measure file write performance
- `FileReadBenchmark`: Measure file read performance
- `DirectoryBenchmark`: Measure directory operations

### Database Benchmarks
- `QueryBenchmark`: Measure query execution time
- `ConnectionBenchmark`: Measure connection overhead
- `TransactionBenchmark`: Measure transaction performance

### LLM Benchmarks
- `ResponseTimeBenchmark`: Measure LLM response time
- `TokenBenchmark`: Measure token processing
- `QualityBenchmark`: Measure response quality

### Container Benchmarks
- `CPUBenchmark`: Measure CPU usage
- `MemoryBenchmark`: Measure memory usage
- `IOMBenchmark`: Measure I/O operations
- `ContainerMetricsBenchmark`: Comprehensive metrics

## Configuration

Create a JSON config file:

```json
{
  "name": "my_benchmark",
  "iterations": 5,
  "warmup_iterations": 1,
  "timeout": 60.0,
  "output_dir": "./results",
  "output_format": ["console", "json", "csv"],
  "verbose": true
}
```

## Adding New Benchmarks

1. Create a new file in the benchmarking module
2. Extend the appropriate base class (`Benchmark`, `FileBenchmark`, etc.)
3. Implement the `run()` method
4. Return a `BenchmarkResult`

Example:

```python
from .base import Benchmark, BenchmarkResult

class CustomBenchmark(Benchmark):
    def run(self):
        start = time.perf_counter()
        # Your code here
        duration = time.perf_counter() - start
        
        return BenchmarkResult(
            name="custom_benchmark",
            duration=duration,
        )
```

## License

MIT License
