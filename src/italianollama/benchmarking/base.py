"""Base classes for benchmarking."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable
from datetime import datetime


@runtime_checkable
class Benchmarkable(Protocol):
    """Protocol for benchmarkable objects."""
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    name: str
    duration: float
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    iterations: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'name': self.name,
            'duration': self.duration,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata,
            'success': self.success,
            'error': self.error,
            'iterations': self.iterations,
        }
    
    @property
    def duration_per_iteration(self) -> float:
        """Get average duration per iteration."""
        if self.iterations == 0:
            return 0.0
        return self.duration / self.iterations


class Benchmark(ABC):
    """Base class for all benchmarks."""
    
    def __init__(
        self,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.name = name or self.__class__.__name__
        self.config = config or {}
        self._results: List[BenchmarkResult] = []
    
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run the benchmark."""
        pass
    
    def run_multiple(self, iterations: int = 1, *args: Any, **kwargs: Any) -> List[BenchmarkResult]:
        """Run benchmark multiple times."""
        self._results = []
        for _ in range(iterations):
            result = self.run(*args, **kwargs)
            self._results.append(result)
        return self._results
    
    def get_results(self) -> List[BenchmarkResult]:
        """Get all benchmark results."""
        return self._results
    
    def reset(self) -> None:
        """Reset benchmark state."""
        self._results = []


class FileBenchmark(Benchmark):
    """Base class for file I/O benchmarks."""
    
    def __init__(self, filepath: str, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.filepath = filepath


class FunctionBenchmark(Benchmark):
    """Base class for function/subfunction benchmarks."""
    
    def __init__(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self.func = func


class LLMBenchmark(Benchmark):
    """Base class for LLM response benchmarks."""
    
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)


class ContainerBenchmark(Benchmark):
    """Base class for container performance benchmarks."""
    
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)


class BenchmarkRunner:
    """Runner for executing benchmarks and managing results."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._benchmarks: List[Benchmark] = []
        self._results: List[BenchmarkResult] = []
    
    def add_benchmark(self, benchmark: Benchmark) -> None:
        """Add a benchmark to the runner."""
        self._benchmarks.append(benchmark)
    
    def add_benchmarks(self, benchmarks: List[Benchmark]) -> None:
        """Add multiple benchmarks to the runner."""
        self._benchmarks.extend(benchmarks)
    
    def run_all(self, *args: Any, **kwargs: Any) -> List[BenchmarkResult]:
        """Run all benchmarks and collect results."""
        self._results = []
        for benchmark in self._benchmarks:
            try:
                result = benchmark.run(*args, **kwargs)
                self._results.append(result)
            except Exception as e:
                self._results.append(
                    BenchmarkResult(
                        name=benchmark.name,
                        duration=0.0,
                        success=False,
                        error=str(e),
                    )
                )
        return self._results
    
    def get_results(self) -> List[BenchmarkResult]:
        """Get all benchmark results."""
        return self._results
    
    def reset(self) -> None:
        """Reset runner state."""
        self._benchmarks = []
        self._results = []
