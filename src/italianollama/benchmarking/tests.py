"""Tests for benchmarking module."""

import os
import tempfile
import unittest
from unittest.mock import Mock

from .base import Benchmark, BenchmarkResult, BenchmarkRunner
from .config import BenchmarkConfig
from .file_io import FileWriteBenchmark, FileReadBenchmark
from .llm import ResponseTimeBenchmark
from .container import CPUBenchmark, MemoryBenchmark
from .reporters import ConsoleReporter, JSONReporter, CSVReporter
from .runner import BenchmarkRunner as Runner
from .utils import calculate_statistics, format_duration, format_bytes


class TestBenchmarkResult(unittest.TestCase):
    """Test BenchmarkResult class."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = BenchmarkResult(
            name="test",
            duration=1.234,
            iterations=5,
        )
        
        d = result.to_dict()
        self.assertEqual(d["name"], "test")
        self.assertEqual(d["duration"], 1.234)
        self.assertEqual(d["iterations"], 5)
        self.assertTrue(d["success"])
    
    def test_duration_per_iteration(self):
        """Test calculation of duration per iteration."""
        result = BenchmarkResult(
            name="test",
            duration=10.0,
            iterations=5,
        )
        self.assertEqual(result.duration_per_iteration, 2.0)


class TestFileBenchmarks(unittest.TestCase):
    """Test file I/O benchmarks."""
    
    def test_file_write_benchmark(self):
        """Test file write benchmark."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            
            benchmark = FileWriteBenchmark(
                filepath=filepath,
                size=1024,
                iterations=2,
            )
            
            result = benchmark.run()
            
            self.assertTrue(result.success)
            self.assertGreater(result.duration, 0)
            self.assertEqual(result.iterations, 1)
    
    def test_file_read_benchmark(self):
        """Test file read benchmark."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.txt")
            
            with open(filepath, "wb") as f:
                f.write(b"test data")
            
            benchmark = FileReadBenchmark(
                filepath=filepath,
                iterations=2,
            )
            
            result = benchmark.run()
            
            self.assertTrue(result.success)
            self.assertGreater(result.duration, 0)


class TestContainerBenchmarks(unittest.TestCase):
    """Test container benchmarks."""
    
    def test_cpu_benchmark(self):
        """Test CPU benchmark."""
        benchmark = CPUBenchmark(
            duration=1.0,
            interval=0.1,
        )
        
        result = benchmark.run()
        
        self.assertTrue(result.success)
        self.assertIn("avg_cpu_percent", result.metadata)
    
    def test_memory_benchmark(self):
        """Test memory benchmark."""
        benchmark = MemoryBenchmark(
            duration=1.0,
            interval=0.1,
        )
        
        result = benchmark.run()
        
        self.assertTrue(result.success)
        self.assertIn("avg_memory_mb", result.metadata)


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_calculate_statistics(self):
        """Test statistics calculation."""
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        stats = calculate_statistics(values)
        
        self.assertEqual(stats["min"], 1.0)
        self.assertEqual(stats["max"], 5.0)
        self.assertEqual(stats["avg"], 3.0)
        self.assertEqual(stats["count"], 5)
    
    def test_format_duration(self):
        """Test duration formatting."""
        self.assertEqual(format_duration(0.001), "1.00 ms")
        self.assertEqual(format_duration(1.5), "1.50 s")
        self.assertEqual(format_duration(125), "2m 5.00 s")
    
    def test_format_bytes(self):
        """Test byte formatting."""
        self.assertEqual(format_bytes(1024), "1.00 KB")
        self.assertEqual(format_bytes(1048576), "1.00 MB")


if __name__ == "__main__":
    unittest.main()
