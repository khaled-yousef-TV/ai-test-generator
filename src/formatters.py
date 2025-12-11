"""
Output Formatters

Format generated test cases into various output formats.
"""

import json
from typing import List, Dict, Any
from pathlib import Path

# Try to import Jinja2 for template rendering
try:
    from jinja2 import Environment, FileSystemLoader
    JINJA_AVAILABLE = True
except ImportError:
    JINJA_AVAILABLE = False


class TestCaseFormatter:
    """Format test cases into various output formats."""
    
    SUPPORTED_FORMATS = ["gherkin", "pytest", "testng", "plain", "json"]
    
    def __init__(self, templates_dir: str = None):
        """
        Initialize the formatter.
        
        Args:
            templates_dir: Directory containing Jinja2 templates
        """
        self.templates_dir = templates_dir or Path(__file__).parent.parent / "templates"
        
        if JINJA_AVAILABLE and Path(self.templates_dir).exists():
            self.env = Environment(loader=FileSystemLoader(self.templates_dir))
        else:
            self.env = None
    
    def format(
        self,
        test_cases: List[Dict[str, Any]],
        output_format: str = "gherkin",
        feature_name: str = "Feature"
    ) -> str:
        """
        Format test cases into the specified format.
        
        Args:
            test_cases: List of test case dictionaries
            output_format: Target format
            feature_name: Name of the feature (for Gherkin)
            
        Returns:
            Formatted test cases as string
        """
        if output_format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {output_format}. Use one of {self.SUPPORTED_FORMATS}")
        
        formatter_method = getattr(self, f"_format_{output_format}")
        return formatter_method(test_cases, feature_name)
    
    def _format_gherkin(self, test_cases: List[Dict[str, Any]], feature_name: str) -> str:
        """Format as Gherkin/BDD."""
        lines = [f"Feature: {feature_name}", ""]
        
        for tc in test_cases:
            lines.append(f"  Scenario: {tc.get('name', 'Unnamed Scenario')}")
            
            # Given steps
            for given in tc.get("given", []):
                lines.append(f"    Given {given}")
            
            # When steps
            for when in tc.get("when", []):
                lines.append(f"    When {when}")
            
            # Then steps
            for then in tc.get("then", []):
                lines.append(f"    Then {then}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_pytest(self, test_cases: List[Dict[str, Any]], feature_name: str) -> str:
        """Format as Python pytest."""
        lines = [
            '"""',
            f'Test cases for {feature_name}',
            '"""',
            '',
            'import pytest',
            '',
            ''
        ]
        
        for tc in test_cases:
            func_name = self._to_snake_case(tc.get("name", "unnamed"))
            lines.append(f"def test_{func_name}():")
            lines.append(f'    """')
            lines.append(f'    {tc.get("name", "Unnamed test")}')
            lines.append(f'    """')
            lines.append("    # Arrange")
            
            for given in tc.get("given", ["# Setup preconditions"]):
                lines.append(f"    # {given}")
            
            lines.append("")
            lines.append("    # Act")
            
            for when in tc.get("when", ["# Perform action"]):
                lines.append(f"    # {when}")
            
            lines.append("")
            lines.append("    # Assert")
            
            for then in tc.get("then", ["# Verify result"]):
                lines.append(f"    # {then}")
            
            lines.append("    assert True  # TODO: Implement assertion")
            lines.append("")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_testng(self, test_cases: List[Dict[str, Any]], feature_name: str) -> str:
        """Format as Java TestNG."""
        class_name = self._to_pascal_case(feature_name)
        
        lines = [
            "import org.testng.Assert;",
            "import org.testng.annotations.Test;",
            "",
            f"public class {class_name}Test {{",
            ""
        ]
        
        for tc in test_cases:
            method_name = self._to_camel_case(tc.get("name", "unnamed"))
            lines.append("    @Test")
            lines.append(f"    public void test{self._to_pascal_case(tc.get('name', 'Unnamed'))}() {{")
            lines.append(f"        // {tc.get('name', 'Unnamed test')}")
            lines.append("")
            lines.append("        // Arrange")
            
            for given in tc.get("given", []):
                lines.append(f"        // {given}")
            
            lines.append("")
            lines.append("        // Act")
            
            for when in tc.get("when", []):
                lines.append(f"        // {when}")
            
            lines.append("")
            lines.append("        // Assert")
            
            for then in tc.get("then", []):
                lines.append(f"        // {then}")
            
            lines.append("        Assert.assertTrue(true); // TODO: Implement")
            lines.append("    }")
            lines.append("")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _format_plain(self, test_cases: List[Dict[str, Any]], feature_name: str) -> str:
        """Format as plain text."""
        lines = [
            f"Test Cases for: {feature_name}",
            "=" * 50,
            ""
        ]
        
        for i, tc in enumerate(test_cases, 1):
            lines.append(f"Test Case #{i}: {tc.get('name', 'Unnamed')}")
            lines.append("-" * 40)
            
            if tc.get("given"):
                lines.append("Preconditions:")
                for given in tc["given"]:
                    lines.append(f"  • {given}")
            
            if tc.get("when"):
                lines.append("Steps:")
                for j, when in enumerate(tc["when"], 1):
                    lines.append(f"  {j}. {when}")
            
            if tc.get("then"):
                lines.append("Expected Results:")
                for then in tc["then"]:
                    lines.append(f"  ✓ {then}")
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_json(self, test_cases: List[Dict[str, Any]], feature_name: str) -> str:
        """Format as JSON."""
        output = {
            "feature": feature_name,
            "test_cases": test_cases
        }
        return json.dumps(output, indent=2)
    
    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case."""
        import re
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', '_', text.strip().lower())
        return text
    
    def _to_camel_case(self, text: str) -> str:
        """Convert text to camelCase."""
        words = self._to_snake_case(text).split('_')
        return words[0] + ''.join(word.capitalize() for word in words[1:])
    
    def _to_pascal_case(self, text: str) -> str:
        """Convert text to PascalCase."""
        words = self._to_snake_case(text).split('_')
        return ''.join(word.capitalize() for word in words)


def format_output(test_cases: List[Dict[str, Any]], output_format: str, feature_name: str = "Feature") -> str:
    """
    Convenience function to format test cases.
    
    Args:
        test_cases: List of test case dictionaries
        output_format: Target format
        feature_name: Name of the feature
        
    Returns:
        Formatted string
    """
    formatter = TestCaseFormatter()
    return formatter.format(test_cases, output_format, feature_name)

