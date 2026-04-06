"""Benchmark configuration management."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class BenchmarkConfig:
    """Configuration for benchmarking."""
    name: str = "default"
    iterations: int = 5
    warmup_iterations: int = 1
    timeout: Optional[float] = None
    output_dir: str = "./benchmark_results"
    output_format: List[str] = field(default_factory=lambda: ["console", "json"])
    verbose: bool = True
    collect_metrics: bool = True
    seed: Optional[int] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "BenchmarkConfig":
        """Create config from dictionary."""
        return cls(**config_dict)
    
    @classmethod
    def from_json(cls, json_path: Union[str, Path]) -> "BenchmarkConfig":
        """Load config from JSON file."""
        with open(json_path, "r") as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "name": self.name,
            "iterations": self.iterations,
            "warmup_iterations": self.warmup_iterations,
            "timeout": self.timeout,
            "output_dir": self.output_dir,
            "output_format": self.output_format,
            "verbose": self.verbose,
            "collect_metrics": self.collect_metrics,
            "seed": self.seed,
            "custom_params": self.custom_params,
        }
    
    def to_json(self, json_path: Union[str, Path]) -> None:
        """Save config to JSON file."""
        with open(json_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
