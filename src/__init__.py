"""AI Test Case Generator - Generate test cases from requirements using LLMs."""

from .generator import TestCaseGenerator
from .edge_cases import EdgeCaseAnalyzer

__version__ = "1.0.0"
__all__ = ["TestCaseGenerator", "EdgeCaseAnalyzer"]

