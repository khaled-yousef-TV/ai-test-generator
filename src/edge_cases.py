"""
Edge Case Analyzer

Automatically detect potential edge cases from requirements.
"""

import re
from typing import List, Dict, Set


class EdgeCaseAnalyzer:
    """Analyze requirements to identify potential edge cases."""
    
    # Common patterns that suggest specific edge cases
    PATTERNS: Dict[str, List[str]] = {
        # Input-related patterns
        r"input|enter|type|field|form": [
            "Empty input",
            "Whitespace-only input",
            "Maximum length input",
            "Special characters",
            "Unicode/emoji characters",
            "SQL injection attempt",
            "XSS script injection",
        ],
        
        # Numeric patterns
        r"number|amount|count|quantity|price|age": [
            "Zero value",
            "Negative numbers",
            "Decimal numbers",
            "Very large numbers",
            "Non-numeric input",
            "Leading zeros",
        ],
        
        # Date/time patterns
        r"date|time|schedule|deadline|expire": [
            "Past dates",
            "Future dates far ahead",
            "Leap year dates (Feb 29)",
            "End of month (31st)",
            "Timezone edge cases",
            "Daylight saving transitions",
            "Invalid date format",
        ],
        
        # Email patterns
        r"email|e-mail": [
            "Invalid email format",
            "Email without @ symbol",
            "Email with multiple @ symbols",
            "Very long email address",
            "Email with special characters",
            "Uppercase email",
        ],
        
        # Password patterns
        r"password|pin|secret": [
            "Minimum length boundary",
            "Maximum length boundary",
            "No uppercase letters",
            "No lowercase letters",
            "No numbers",
            "No special characters",
            "Common/weak passwords",
            "Password with spaces",
        ],
        
        # File patterns
        r"file|upload|download|attachment": [
            "Empty file",
            "Very large file",
            "Unsupported file type",
            "Corrupted file",
            "File with special characters in name",
            "File with very long name",
            "Multiple files at once",
        ],
        
        # List/collection patterns
        r"list|items|results|records": [
            "Empty list",
            "Single item",
            "Maximum number of items",
            "Duplicate items",
            "Sorted/unsorted data",
        ],
        
        # Search patterns
        r"search|find|filter|query": [
            "No results found",
            "Exact match",
            "Partial match",
            "Case sensitivity",
            "Special characters in search",
            "Very long search query",
        ],
        
        # Authentication patterns
        r"login|logout|auth|session|token": [
            "Invalid credentials",
            "Expired session",
            "Concurrent sessions",
            "Session timeout",
            "Remember me functionality",
            "Account locked",
        ],
        
        # Payment patterns
        r"payment|pay|checkout|card|transaction": [
            "Insufficient funds",
            "Expired card",
            "Invalid card number",
            "Payment timeout",
            "Duplicate payment",
            "Refund scenarios",
        ],
        
        # Network patterns
        r"api|request|response|connection|network": [
            "Network timeout",
            "Connection lost",
            "Slow network",
            "API rate limiting",
            "Invalid API response",
        ],
    }
    
    # Universal edge cases that apply to most scenarios
    UNIVERSAL_EDGE_CASES: List[str] = [
        "Concurrent user actions",
        "Browser back button",
        "Page refresh during operation",
        "Multiple rapid clicks",
        "Mobile device viewport",
        "Screen reader accessibility",
    ]
    
    def analyze(self, requirement: str) -> List[str]:
        """
        Analyze a requirement and return relevant edge cases.
        
        Args:
            requirement: The requirement text to analyze
            
        Returns:
            List of potential edge cases
        """
        requirement_lower = requirement.lower()
        edge_cases: Set[str] = set()
        
        # Check each pattern
        for pattern, cases in self.PATTERNS.items():
            if re.search(pattern, requirement_lower):
                edge_cases.update(cases)
        
        # Add universal edge cases
        edge_cases.update(self.UNIVERSAL_EDGE_CASES)
        
        # Sort for consistent output
        return sorted(list(edge_cases))
    
    def analyze_with_categories(self, requirement: str) -> Dict[str, List[str]]:
        """
        Analyze and return edge cases grouped by category.
        
        Args:
            requirement: The requirement text to analyze
            
        Returns:
            Dictionary of category -> edge cases
        """
        requirement_lower = requirement.lower()
        categorized: Dict[str, List[str]] = {}
        
        for pattern, cases in self.PATTERNS.items():
            if re.search(pattern, requirement_lower):
                # Extract category name from pattern
                category = pattern.split("|")[0].replace(r"\\", "").title()
                if category not in categorized:
                    categorized[category] = []
                categorized[category].extend(cases)
        
        categorized["Universal"] = self.UNIVERSAL_EDGE_CASES
        
        return categorized


def main():
    """Demo the edge case analyzer."""
    analyzer = EdgeCaseAnalyzer()
    
    requirement = """
    As a user, I want to upload my profile picture,
    so that other users can identify me.
    
    The user enters their email and password to login,
    then navigates to the profile settings page.
    """
    
    print("📋 Analyzing requirement for edge cases...\n")
    
    edge_cases = analyzer.analyze(requirement)
    print("Detected Edge Cases:")
    for case in edge_cases:
        print(f"  • {case}")
    
    print("\n" + "="*50 + "\n")
    
    categorized = analyzer.analyze_with_categories(requirement)
    print("Edge Cases by Category:")
    for category, cases in categorized.items():
        print(f"\n{category}:")
        for case in cases:
            print(f"  • {case}")


if __name__ == "__main__":
    main()

