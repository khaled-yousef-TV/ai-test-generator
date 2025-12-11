# 🧠 AI Test Case Generator

Automatically generate comprehensive test cases from user stories, requirements, or acceptance criteria using Large Language Models.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![LangChain](https://img.shields.io/badge/LangChain-Powered-green)
![Gemini](https://img.shields.io/badge/Gemini-AI-purple)

## ✨ Features

- 📝 **Generate from Requirements** - Convert user stories to detailed test cases
- 🔍 **Smart Edge Case Detection** - AI identifies edge cases you might miss
- 📋 **Multiple Output Formats** - Gherkin/BDD, pytest, plain text
- 🔗 **Jira Integration** - Pull requirements directly from Jira tickets
- 🎯 **Customizable Templates** - Define your own test case structure
- 📊 **Coverage Analysis** - Ensure comprehensive test coverage

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/khaled-yousef-TV/ai-test-generator.git
cd ai-test-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API key
echo "GEMINI_API_KEY=your-api-key" > .env
```

### Basic Usage

```python
from src.generator import TestCaseGenerator

generator = TestCaseGenerator()

# Generate from a user story
test_cases = generator.generate(
    requirement="""
    As a user, I want to reset my password 
    so that I can regain access to my account.
    
    Acceptance Criteria:
    - User receives reset email within 5 minutes
    - Reset link expires after 24 hours
    - Password must meet complexity requirements
    """,
    output_format="gherkin"
)

print(test_cases)
```

### Output Example

```gherkin
Feature: Password Reset

  Scenario: Successful password reset request
    Given I am on the login page
    When I click "Forgot Password"
    And I enter my registered email "user@example.com"
    And I click "Send Reset Link"
    Then I should see "Reset link sent to your email"
    And I should receive an email within 5 minutes

  Scenario: Reset link expiration
    Given I have a password reset link older than 24 hours
    When I click on the reset link
    Then I should see "This link has expired"
    And I should be prompted to request a new link

  Scenario: Password complexity validation
    Given I am on the password reset page with a valid link
    When I enter a new password "weak"
    Then I should see "Password does not meet requirements"
    
  # ... more test cases including edge cases
```

## 📖 CLI Usage

```bash
# Generate from a text file
python -m src.cli generate --input requirements.txt --output tests/

# Generate from Jira ticket
python -m src.cli generate --jira PROJ-123 --output tests/

# Generate with specific format
python -m src.cli generate --input story.txt --format pytest

# Interactive mode
python -m src.cli interactive
```

## 🔧 Configuration

Create a `config.yaml` file:

```yaml
model:
  provider: gemini  # or openai
  name: gemini-2.0-flash
  temperature: 0.7

output:
  default_format: gherkin  # gherkin, pytest, testng, plain
  include_edge_cases: true
  max_test_cases: 20

jira:
  url: https://your-company.atlassian.net
  # Credentials via environment variables
```

## 📋 Supported Output Formats

| Format | Description | File Extension |
|--------|-------------|----------------|
| `gherkin` | BDD/Cucumber format | `.feature` |
| `pytest` | Python pytest functions | `.py` |
| `testng` | Java TestNG format | `.java` |
| `plain` | Human-readable text | `.txt` |
| `json` | Structured JSON | `.json` |

## 🔌 API Reference

### TestCaseGenerator

```python
generator = TestCaseGenerator(
    model="gemini-2.0-flash",  # LLM model to use
    temperature=0.7,           # Creativity (0-1)
    max_tokens=4000            # Max output length
)

# Generate test cases
result = generator.generate(
    requirement="...",         # User story or requirement
    output_format="gherkin",   # Output format
    context="...",             # Optional: additional context
    num_cases=10               # Optional: target number of cases
)

# Generate from Jira
result = generator.from_jira(
    ticket_id="PROJ-123",
    output_format="pytest"
)
```

### Edge Case Detection

```python
from src.edge_cases import EdgeCaseAnalyzer

analyzer = EdgeCaseAnalyzer()
edge_cases = analyzer.analyze(requirement)

# Returns: ["Empty input", "Special characters", "Max length exceeded", ...]
```

## 🏗️ Project Structure

```
ai-test-generator/
├── src/
│   ├── __init__.py
│   ├── generator.py      # Main test case generator
│   ├── edge_cases.py     # Edge case detection
│   ├── formatters.py     # Output formatters
│   ├── jira_client.py    # Jira integration
│   └── cli.py            # Command-line interface
├── templates/
│   ├── gherkin.j2        # Gherkin template
│   ├── pytest.j2         # Pytest template
│   └── testng.j2         # TestNG template
├── examples/
│   └── user_stories.txt  # Example requirements
├── tests/
│   └── test_generator.py # Unit tests
├── requirements.txt
├── config.yaml
└── README.md
```

## 🔒 Security

- API keys stored in `.env` (git-ignored)
- No sensitive data logged
- Jira credentials via environment variables only

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with ❤️ by [Khaled Yousef](https://khaledyousef.io)**

