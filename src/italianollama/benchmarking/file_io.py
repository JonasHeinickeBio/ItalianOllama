"""File I/O benchmark modules."""

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Benchmark, BenchmarkResult, FileBenchmark


class FileWriteBenchmark(FileBenchmark):
    """Benchmark for file write operations."""
    
    def __init__(
        self,
        filepath: str,
        size: int = 1024,
        iterations: int = 5,
        **kwargs: Any,
    ):
        super().__init__(filepath, **kwargs)
        self.size = size
        self.iterations = iterations
        self.data = os.urandom(size)
    
    def run(self, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run file write benchmark."""
        start_time = self._get_time()
        
        try:
            with open(self.filepath, "wb") as f:
                f.write(self.data)
            
            duration = self._get_time() - start_time
            
            return BenchmarkResult(
                name=f"file_write_{self.size}bytes",
                duration=duration,
                metadata={
                    "file_size": self.size,
                    "file_path": self.filepath,
                },
            )
        
        except Exception as e:
            return BenchmarkResult(
                name=f"file_write_{self.size}bytes",
                duration=0.0,
                success=False,
                error=str(e),
            )
    
    def _get_time(self) -> float:
        """Get current time."""
        import time
        return time.perf_counter()


class FileReadBenchmark(FileBenchmark):
    """Benchmark for file read operations."""
    
    def __init__(
        self,
        filepath: str,
        iterations: int = 5,
        **kwargs: Any,
    ):
        super().__init__(filepath, **kwargs)
        self.iterations = iterations
    
    def run(self, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run file read benchmark."""
        start_time = self._get_time()
        
        try:
            with open(self.filepath, "rb") as f:
                data = f.read()
            
            duration = self._get_time() - start_time
            
            return BenchmarkResult(
                name=f"file_read_{len(data)}bytes",
                duration=duration,
                metadata={
                    "file_size": len(data),
                    "file_path": self.filepath,
                },
            )
        
        except Exception as e:
            return BenchmarkResult(
                name=f"file_read_{self.filepath}",
                duration=0.0,
                success=False,
                error=str(e),
            )
    
    def _get_time(self) -> float:
        """Get current time."""
        import time
        return time.perf_counter()


class FileDeleteBenchmark(FileBenchmark):
    """Benchmark for file delete operations."""
    
    def run(self, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run file delete benchmark."""
        start_time = self._get_time()
        
        try:
            os.remove(self.filepath)
            duration = self._get_time() - start_time
            
            return BenchmarkResult(
                name=f"file_delete_{self.filepath}",
                duration=duration,
                metadata={
                    "file_path": self.filepath,
                },
            )
        
        except Exception as e:
            return BenchmarkResult(
                name=f"file_delete_{self.filepath}",
                duration=0.0,
                success=False,
                error=str(e),
            )
    
    def _get_time(self) -> float:
        """Get current time."""
        import time
        return time.perf_counter()


class DirectoryBenchmark(FileBenchmark):
    """Benchmark for directory operations."""
    
    def __init__(
        self,
        dirpath: str,
        num_files: int = 10,
        file_size: int = 1024,
        **kwargs: Any,
    ):
        super().__init__(dirpath, **kwargs)
        self.num_files = num_files
        self.file_size = file_size
    
    def run(self, *args: Any, **kwargs: Any) -> BenchmarkResult:
        """Run directory operations benchmark."""
        start_time = self._get_time()
        
        try:
            Path(self.filepath).mkdir(parents=True, exist_ok=True)
            
            for i in range(self.num_files):
                filepath = Path(self.filepath) / f"test_file_{i}.txt"
                with open(filepath, "wb") as f:
                    f.write(os.urandom(self.file_size))
            
            duration = self._get_time() - start_time
            
            return BenchmarkResult(
                name="directory_operations",
                duration=duration,
                metadata={
                    "num_files": self.num_files,
                    "file_size": self.file_size,
                    "dir_path": self.filepath,
                },
            )
        
        except Exception as e:
            return BenchmarkResult(
                name="directory_operations",
                duration=0.0,
                success=False,
                error=str(e),
            )
    
    def _get_time(self) -> float:
        """Get current time."""
        import time
        return time.perf_counter()
