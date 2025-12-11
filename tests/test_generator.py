"""
Tests for the AI Test Case Generator
"""

import pytest
from src.edge_cases import EdgeCaseAnalyzer
from src.formatters import TestCaseFormatter


class TestEdgeCaseAnalyzer:
    """Tests for EdgeCaseAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = EdgeCaseAnalyzer()
    
    def test_analyze_returns_list(self):
        """Test that analyze returns a list."""
        result = self.analyzer.analyze("Simple requirement")
        assert isinstance(result, list)
    
    def test_analyze_detects_email_patterns(self):
        """Test email-related edge cases are detected."""
        requirement = "User enters their email address"
        result = self.analyzer.analyze(requirement)
        
        assert "Invalid email format" in result
    
    def test_analyze_detects_password_patterns(self):
        """Test password-related edge cases are detected."""
        requirement = "User enters password to login"
        result = self.analyzer.analyze(requirement)
        
        assert "Minimum length boundary" in result
        assert "No special characters" in result
    
    def test_analyze_detects_file_patterns(self):
        """Test file upload edge cases are detected."""
        requirement = "User can upload a profile picture file"
        result = self.analyzer.analyze(requirement)
        
        assert "Empty file" in result
        assert "Very large file" in result
    
    def test_analyze_includes_universal_cases(self):
        """Test that universal edge cases are always included."""
        result = self.analyzer.analyze("Any requirement")
        
        assert "Concurrent user actions" in result
        assert "Browser back button" in result
    
    def test_analyze_with_categories(self):
        """Test categorized analysis."""
        requirement = "User enters email and password"
        result = self.analyzer.analyze_with_categories(requirement)
        
        assert isinstance(result, dict)
        assert "Universal" in result


class TestFormatter:
    """Tests for TestCaseFormatter."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = TestCaseFormatter()
        self.sample_test_cases = [
            {
                "name": "Successful login",
                "given": ["User is on login page", "User has valid credentials"],
                "when": ["User enters email", "User enters password", "User clicks login"],
                "then": ["User is redirected to dashboard"]
            }
        ]
    
    def test_format_gherkin(self):
        """Test Gherkin format output."""
        result = self.formatter.format(
            self.sample_test_cases,
            output_format="gherkin",
            feature_name="Login"
        )
        
        assert "Feature: Login" in result
        assert "Scenario: Successful login" in result
        assert "Given User is on login page" in result
        assert "When User enters email" in result
        assert "Then User is redirected to dashboard" in result
    
    def test_format_pytest(self):
        """Test pytest format output."""
        result = self.formatter.format(
            self.sample_test_cases,
            output_format="pytest",
            feature_name="Login"
        )
        
        assert "import pytest" in result
        assert "def test_" in result
        assert "# Arrange" in result
        assert "# Act" in result
        assert "# Assert" in result
    
    def test_format_testng(self):
        """Test TestNG format output."""
        result = self.formatter.format(
            self.sample_test_cases,
            output_format="testng",
            feature_name="Login"
        )
        
        assert "import org.testng" in result
        assert "@Test" in result
        assert "public void test" in result
    
    def test_format_plain(self):
        """Test plain text format output."""
        result = self.formatter.format(
            self.sample_test_cases,
            output_format="plain",
            feature_name="Login"
        )
        
        assert "Test Case #1" in result
        assert "Successful login" in result
    
    def test_format_json(self):
        """Test JSON format output."""
        import json
        
        result = self.formatter.format(
            self.sample_test_cases,
            output_format="json",
            feature_name="Login"
        )
        
        parsed = json.loads(result)
        assert parsed["feature"] == "Login"
        assert len(parsed["test_cases"]) == 1
    
    def test_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError):
            self.formatter.format(
                self.sample_test_cases,
                output_format="invalid_format"
            )


class TestSnakeCaseConversion:
    """Tests for case conversion utilities."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = TestCaseFormatter()
    
    def test_to_snake_case(self):
        """Test snake_case conversion."""
        assert self.formatter._to_snake_case("Hello World") == "hello_world"
        assert self.formatter._to_snake_case("Test Case Name") == "test_case_name"
        assert self.formatter._to_snake_case("already_snake") == "already_snake"
    
    def test_to_pascal_case(self):
        """Test PascalCase conversion."""
        assert self.formatter._to_pascal_case("hello world") == "HelloWorld"
        assert self.formatter._to_pascal_case("test case") == "TestCase"
    
    def test_to_camel_case(self):
        """Test camelCase conversion."""
        assert self.formatter._to_camel_case("hello world") == "helloWorld"
        assert self.formatter._to_camel_case("Test Case") == "testCase"


# Integration tests (require API key)
@pytest.mark.skipif(
    not pytest.importorskip("google.generativeai", reason="Gemini not available"),
    reason="Gemini API not configured"
)
class TestGeneratorIntegration:
    """Integration tests for TestCaseGenerator (requires API key)."""
    
    def test_generate_basic(self):
        """Test basic test case generation."""
        from src.generator import TestCaseGenerator
        import os
        
        if not os.getenv("GEMINI_API_KEY"):
            pytest.skip("GEMINI_API_KEY not set")
        
        generator = TestCaseGenerator()
        result = generator.generate(
            requirement="User can log in with email and password",
            output_format="plain",
            num_cases=3
        )
        
        assert len(result) > 0
        assert "login" in result.lower() or "email" in result.lower()

