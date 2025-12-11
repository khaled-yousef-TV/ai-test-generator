"""
AI Test Case Generator

Generate comprehensive test cases from user stories and requirements using LLMs.
"""

import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

from .edge_cases import EdgeCaseAnalyzer
from .formatters import format_output

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


class TestCaseGenerator:
    """Generate test cases from requirements using LLMs."""
    
    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.7,
        max_tokens: int = 4000
    ):
        """
        Initialize the test case generator.
        
        Args:
            model: The LLM model to use
            temperature: Creativity level (0-1)
            max_tokens: Maximum output tokens
        """
        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.model = genai.GenerativeModel(model)
        self.edge_analyzer = EdgeCaseAnalyzer()
    
    def generate(
        self,
        requirement: str,
        output_format: str = "gherkin",
        context: Optional[str] = None,
        num_cases: int = 10,
        include_edge_cases: bool = True
    ) -> str:
        """
        Generate test cases from a requirement.
        
        Args:
            requirement: The user story or requirement text
            output_format: Output format (gherkin, pytest, testng, plain, json)
            context: Optional additional context
            num_cases: Target number of test cases
            include_edge_cases: Whether to include edge cases
            
        Returns:
            Generated test cases in the specified format
        """
        # Analyze for edge cases
        edge_cases = []
        if include_edge_cases:
            edge_cases = self.edge_analyzer.analyze(requirement)
        
        # Build the prompt
        prompt = self._build_prompt(
            requirement=requirement,
            output_format=output_format,
            context=context,
            num_cases=num_cases,
            edge_cases=edge_cases
        )
        
        # Generate with Gemini
        response = self.model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens
            )
        )
        
        return response.text
    
    def generate_from_dict(self, data: Dict[str, Any]) -> str:
        """Generate test cases from a dictionary of requirement data."""
        requirement = data.get("requirement", "")
        acceptance_criteria = data.get("acceptance_criteria", [])
        
        # Combine into a single requirement string
        full_requirement = requirement
        if acceptance_criteria:
            full_requirement += "\n\nAcceptance Criteria:\n"
            for criterion in acceptance_criteria:
                full_requirement += f"- {criterion}\n"
        
        return self.generate(
            requirement=full_requirement,
            output_format=data.get("format", "gherkin"),
            context=data.get("context"),
            num_cases=data.get("num_cases", 10)
        )
    
    def _build_prompt(
        self,
        requirement: str,
        output_format: str,
        context: Optional[str],
        num_cases: int,
        edge_cases: List[str]
    ) -> str:
        """Build the prompt for the LLM."""
        
        format_instructions = self._get_format_instructions(output_format)
        
        prompt = f"""You are an expert QA engineer. Generate comprehensive test cases for the following requirement.

## Requirement:
{requirement}

"""
        
        if context:
            prompt += f"""## Additional Context:
{context}

"""
        
        if edge_cases:
            prompt += f"""## Edge Cases to Consider:
{chr(10).join(f'- {ec}' for ec in edge_cases)}

"""
        
        prompt += f"""## Instructions:
1. Generate approximately {num_cases} test cases
2. Cover both happy path and negative scenarios
3. Include the edge cases listed above
4. Be specific with test data examples
5. Consider boundary conditions

## Output Format:
{format_instructions}

Generate the test cases now:
"""
        
        return prompt
    
    def _get_format_instructions(self, output_format: str) -> str:
        """Get format-specific instructions."""
        
        formats = {
            "gherkin": """Use Gherkin/BDD format:
Feature: [Feature Name]
  Scenario: [Scenario Name]
    Given [precondition]
    When [action]
    Then [expected result]""",
            
            "pytest": """Use Python pytest format:
def test_scenario_name():
    # Arrange
    ...
    # Act
    ...
    # Assert
    assert ...""",
            
            "testng": """Use Java TestNG format:
@Test
public void testScenarioName() {
    // Arrange
    // Act
    // Assert
}""",
            
            "plain": """Use plain text format:
Test Case: [Name]
Preconditions: [Setup required]
Steps:
1. [Step 1]
2. [Step 2]
Expected Result: [What should happen]""",
            
            "json": """Use JSON format:
{
  "test_cases": [
    {
      "name": "...",
      "preconditions": "...",
      "steps": ["...", "..."],
      "expected_result": "..."
    }
  ]
}"""
        }
        
        return formats.get(output_format, formats["plain"])


def main():
    """Demo the test case generator."""
    generator = TestCaseGenerator()
    
    requirement = """
    As a user, I want to log in to my account using email and password,
    so that I can access my personalized dashboard.
    
    Acceptance Criteria:
    - Email field validates proper email format
    - Password must be at least 8 characters
    - Show error message for invalid credentials
    - Lock account after 5 failed attempts
    - Remember me option available
    """
    
    print("🧠 Generating test cases...\n")
    test_cases = generator.generate(requirement, output_format="gherkin")
    print(test_cases)


if __name__ == "__main__":
    main()

