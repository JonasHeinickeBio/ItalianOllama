"""Benchmark reporters for output generation."""

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, TextIO

from .base import BenchmarkResult


class BaseReporter(ABC):
    """Base class for benchmark reporters."""
    
    def __init__(self, output_path: Optional[Path] = None):
        self.output_path = output_path
        self.results: List[BenchmarkResult] = []
    
    def add_result(self, result: BenchmarkResult) -> None:
        """Add a benchmark result."""
        self.results.append(result)
    
    @abstractmethod
    def report(self, results: Optional[List[BenchmarkResult]] = None) -> None:
        """Generate report for benchmark results."""
        pass
    
    @abstractmethod
    def save(self, path: Optional[Path] = None) -> None:
        """Save results to file."""
        pass


class ConsoleReporter(BaseReporter):
    """Reporter that outputs to console/terminal."""
    
    def __init__(self, verbose: bool = True):
        super().__init__()
        self.verbose = verbose
    
    def report(self, results: Optional[List[BenchmarkResult]] = None) -> None:
        """Print results to console."""
        results = results or self.results
        
        print("\n" + "=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)
        
        for result in results:
            print(f"\nBenchmark: {result.name}")
            print(f"  Duration: {result.duration:.6f} seconds")
            print(f"  Iterations: {result.iterations}")
            print(f"  Avg/iteration: {result.duration_per_iteration:.6f} seconds")
            
            if result.metadata and self.verbose:
                print(f"  Metadata:")
                for key, value in result.metadata.items():
                    print(f"    {key}: {value}")
            
            if not result.success:
                print(f"  Error: {result.error}")
        
        print("\n" + "=" * 60)
    
    def save(self, path: Optional[Path] = None) -> None:
        """Console reporter doesn't save to file."""
        pass


class JSONReporter(BaseReporter):
    """Reporter that outputs results to JSON format."""
    
    def report(self, results: Optional[List[BenchmarkResult]] = None) -> None:
        """Print JSON results to console."""
        results = results or self.results
        output = {
            "results": [r.to_dict() for r in results],
            "summary": self._calculate_summary(results),
        }
        print(json.dumps(output, indent=2))
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save results to JSON file."""
        path = path or self.output_path
        if not path:
            raise ValueError("No output path specified")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        output = {
            "results": [r.to_dict() for r in self.results],
            "summary": self._calculate_summary(self.results),
        }
        
        with open(path, "w") as f:
            json.dump(output, f, indent=2)
    
    def _calculate_summary(self, results: List[BenchmarkResult]) -> Dict[str, Any]:
        """Calculate summary statistics."""
        if not results:
            return {}
        
        durations = [r.duration for r in results]
        total_time = sum(durations)
        avg_time = total_time / len(durations)
        
        return {
            "total_benchmarks": len(results),
            "total_time": total_time,
            "average_time": avg_time,
            "success_count": sum(1 for r in results if r.success),
            "failed_count": sum(1 for r in results if not r.success),
        }


class CSVReporter(BaseReporter):
    """Reporter that outputs results to CSV format."""
    
    def __init__(self, fieldnames: Optional[List[str]] = None):
        super().__init__()
        self.fieldnames = fieldnames or [
            "name", "duration", "timestamp", "iterations", 
            "duration_per_iteration", "success", "error"
        ]
    
    def report(self, results: Optional[List[BenchmarkResult]] = None) -> None:
        """Print CSV results to console."""
        results = results or self.results
        
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=self.fieldnames)
        writer.writeheader()
        
        for result in results:
            row = {
                "name": result.name,
                "duration": result.duration,
                "timestamp": result.timestamp.isoformat(),
                "iterations": result.iterations,
                "duration_per_iteration": result.duration_per_iteration,
                "success": result.success,
                "error": result.error or "",
            }
            writer.writerow(row)
        
        print(output.getvalue())
    
    def save(self, path: Optional[Path] = None) -> None:
        """Save results to CSV file."""
        path = path or self.output_path
        if not path:
            raise ValueError("No output path specified")
        
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            
            for result in self.results:
                row = {
                    "name": result.name,
                    "duration": result.duration,
                    "timestamp": result.timestamp.isoformat(),
                    "iterations": result.iterations,
                    "duration_per_iteration": result.duration_per_iteration,
                    "success": result.success,
                    "error": result.error or "",
                }
                writer.writerow(row)
