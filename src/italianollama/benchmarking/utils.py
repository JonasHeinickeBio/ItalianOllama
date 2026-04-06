"""Utility functions for benchmarking."""

import time
from typing import Any, Callable, Dict, List, Optional, Union


def measure_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure function execution time."""
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} executed in {end - start:.6f} seconds")
        return result
    return wrapper


def warmup(
    func: Callable[..., Any],
    iterations: int = 1,
    *args: Any,
    **kwargs: Any,
) -> List[float]:
    """Warmup function for benchmarking."""
    durations = []
    for _ in range(iterations):
        start = time.perf_counter()
        func(*args, **kwargs)
        end = time.perf_counter()
        durations.append(end - start)
    return durations


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate statistics for a list of values."""
    if not values:
        return {}
    
    return {
        "min": min(values),
        "max": max(values),
        "avg": sum(values) / len(values),
        "sum": sum(values),
        "count": len(values),
    }


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.2f} μs"
    elif seconds < 1:
        return f"{seconds * 1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f} s"


def format_bytes(bytes_: int) -> str:
    """Format byte count in human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_ < 1024:
            return f"{bytes_:.2f} {unit}"
        bytes_ /= 1024
    return f"{bytes_:.2f} PB"


def run_with_timeout(
    func: Callable[..., Any],
    timeout: float,
    *args: Any,
    **kwargs: Any,
) -> Union[Any, None]:
    """Run function with timeout."""
    import threading
    
    result = [None]
    exception = [None]
    
    def target():
        try:
            result[0] = func(*args, **kwargs)
        except Exception as e:
            exception[0] = e
    
    thread = threading.Thread(target=target, daemon=True)
    thread.start()
    thread.join(timeout=timeout)
    
    if thread.is_alive():
        raise TimeoutError(f"Function exceeded timeout of {timeout} seconds")
    
    if exception[0]:
        raise exception[0]
    
    return result[0]
