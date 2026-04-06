"""Benchmark decorators."""

import time
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

from .base import BenchmarkResult

F = TypeVar("F", bound=Callable[..., Any])


def benchmark(
    iterations: int = 1,
    name: Optional[str] = None,
    collect_metrics: bool = True,
) -> Callable[[F], F]:
    """Decorator for benchmarking functions.
    
    Args:
        iterations: Number of times to run the function
        name: Optional benchmark name
        collect_metrics: Whether to collect detailed metrics
    
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = None
            start_time = time.perf_counter()
            
            for _ in range(iterations):
                result = func(*args, **kwargs)
            
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            if collect_metrics:
                benchmark_result = BenchmarkResult(
                    name=name or func.__name__,
                    duration=duration,
                    iterations=iterations,
                )
                wrapper._last_benchmark = benchmark_result
            
            return result
        
        return wrapper
    return decorator
