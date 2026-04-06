"""Container performance benchmark modules."""

import os
import psutil
import time
from typing import Any, Dict, List, Optional

from .base import Benchmark, BenchmarkResult


class ContainerBenchmark(Benchmark):
    """Base class for container benchmarks."""
    
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)


class CPUBenchmark(ContainerBenchmark):
    """Benchmark for CPU usage."""
    
    def __init__(
        self,
        target_func: Any = None,
        duration: float = 5.0,
        interval: float = 0.1,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.target_func = target_func
        self.duration = duration
        self.interval = interval
    
    def run(self, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run CPU usage benchmark."""
        process = psutil.Process(os.getpid())
        cpu_percentages = []
        
        start_time = time.perf_counter()
        
        if self.target_func:
            end_time = start_time + self.duration
            while time.perf_counter() < end_time:
                cpu_percentages.append(process.cpu_percent(interval=self.interval))
        
        else:
            time.sleep(self.duration)
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        if not cpu_percentages:
            cpu_percentages = [process.cpu_percent()]
        
        return BenchmarkResult(
            name="cpu_usage",
            duration=duration,
            metadata={
                "avg_cpu_percent": sum(cpu_percentages) / len(cpu_percentages),
                "max_cpu_percent": max(cpu_percentages),
                "min_cpu_percent": min(cpu_percentages),
                "cpu_percentages": cpu_percentages,
            },
        )


class MemoryBenchmark(ContainerBenchmark):
    """Benchmark for memory usage."""
    
    def __init__(
        self,
        target_func: Any = None,
        duration: float = 5.0,
        interval: float = 0.1,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.target_func = target_func
        self.duration = duration
        self.interval = interval
    
    def run(self, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run memory usage benchmark."""
        process = psutil.Process(os.getpid())
        memory_values = []
        
        start_time = time.perf_counter()
        
        if self.target_func:
            end_time = start_time + self.duration
            while time.perf_counter() < end_time:
                memory_values.append(process.memory_info().rss)
                time.sleep(self.interval)
        
        else:
            time.sleep(self.duration)
            memory_values.append(process.memory_info().rss)
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        return BenchmarkResult(
            name="memory_usage",
            duration=duration,
            metadata={
                "avg_memory_bytes": sum(memory_values) / len(memory_values),
                "max_memory_bytes": max(memory_values),
                "min_memory_bytes": min(memory_values),
                "memory_bytes": memory_values,
                "avg_memory_mb": sum(memory_values) / len(memory_values) / (1024 * 1024),
            },
        )


class IOMBenchmark(ContainerBenchmark):
    """Benchmark for I/O operations."""
    
    def __init__(
        self,
        read_size: int = 1024 * 1024,
        write_size: int = 1024 * 1024,
        iterations: int = 5,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.read_size = read_size
        self.write_size = write_size
        self.iterations = iterations
    
    def run(self, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run I/O benchmark."""
        process = psutil.Process(os.getpid())
        
        read_times = []
        write_times = []
        
        import tempfile
        
        for _ in range(self.iterations):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                temp_path = f.name
                
                start = time.perf_counter()
                f.write(b"x" * self.write_size)
                f.flush()
                write_times.append(time.perf_counter() - start)
                
                start = time.perf_counter()
                with open(temp_path, "rb") as rf:
                    rf.read(self.read_size)
                read_times.append(time.perf_counter() - start)
        
        os.unlink(temp_path)
        
        return BenchmarkResult(
            name="io_operations",
            duration=sum(read_times) + sum(write_times),
            metadata={
                "read_times": read_times,
                "write_times": write_times,
                "avg_read_time": sum(read_times) / len(read_times),
                "avg_write_time": sum(write_times) / len(write_times),
                "read_size_bytes": self.read_size,
                "write_size_bytes": self.write_size,
            },
        )


class ContainerMetricsBenchmark(ContainerBenchmark):
    """Benchmark for comprehensive container metrics."""
    
    def __init__(
        self,
        duration: float = 10.0,
        interval: float = 0.5,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.duration = duration
        self.interval = interval
    
    def run(self, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run comprehensive container metrics benchmark."""
        process = psutil.Process(os.getpid())
        metrics = {
            "cpu_percentages": [],
            "memory_bytes": [],
            "disk_read_bytes": [],
            "disk_write_bytes": [],
            "network_bytes_sent": [],
            "network_bytes_recv": [],
        }
        
        start_time = time.perf_counter()
        end_time = start_time + self.duration
        
        disk_io_start = process.io_counters()
        net_io_start = psutil.net_io_counters()
        
        while time.perf_counter() < end_time:
            metrics["cpu_percentages"].append(process.cpu_percent())
            metrics["memory_bytes"].append(process.memory_info().rss)
            
            disk_io = process.io_counters()
            metrics["disk_read_bytes"].append(disk_io.read_bytes - disk_io_start.read_bytes)
            metrics["disk_write_bytes"].append(disk_io.write_bytes - disk_io_start.write_bytes)
            
            net_io = psutil.net_io_counters()
            metrics["network_bytes_sent"].append(net_io.bytes_sent - net_io_start.bytes_sent)
            metrics["network_bytes_recv"].append(net_io.bytes_recv - net_io_start.bytes_recv)
            
            time.sleep(self.interval)
        
        end_time = time.perf_counter()
        duration = end_time - start_time
        
        return BenchmarkResult(
            name="container_metrics",
            duration=duration,
            metadata={
                "duration_seconds": duration,
                **{k: {
                    "avg": sum(v) / len(v) if v else 0,
                    "max": max(v) if v else 0,
                    "min": min(v) if v else 0,
                } for k, v in metrics.items()},
            },
        )
