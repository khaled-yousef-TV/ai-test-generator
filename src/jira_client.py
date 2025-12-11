"""
Jira Integration Client

Fetch requirements and user stories from Jira tickets.
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class JiraClient:
    """Client for interacting with Jira API."""
    
    def __init__(
        self,
        url: Optional[str] = None,
        email: Optional[str] = None,
        api_token: Optional[str] = None
    ):
        """
        Initialize the Jira client.
        
        Args:
            url: Jira instance URL (e.g., https://company.atlassian.net)
            email: User email for authentication
            api_token: API token for authentication
        """
        self.url = url or os.getenv("JIRA_URL")
        self.email = email or os.getenv("JIRA_EMAIL")
        self.api_token = api_token or os.getenv("JIRA_API_TOKEN")
        
        if not all([self.url, self.email, self.api_token]):
            raise ValueError(
                "Jira credentials not configured. Set JIRA_URL, JIRA_EMAIL, "
                "and JIRA_API_TOKEN environment variables."
            )
        
        # Lazy import requests
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise ImportError("requests library required for Jira integration: pip install requests")
    
    def _get_auth(self):
        """Get authentication tuple."""
        return (self.email, self.api_token)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """
        Fetch a Jira ticket by ID.
        
        Args:
            ticket_id: The ticket ID (e.g., PROJ-123)
            
        Returns:
            Dictionary containing ticket data
        """
        url = f"{self.url}/rest/api/3/issue/{ticket_id}"
        
        response = self.requests.get(
            url,
            headers=self._get_headers(),
            auth=self._get_auth()
        )
        
        if response.status_code == 404:
            raise ValueError(f"Ticket not found: {ticket_id}")
        
        response.raise_for_status()
        return response.json()
    
    def get_ticket_description(self, ticket_id: str) -> str:
        """
        Get the description/requirement from a Jira ticket.
        
        Args:
            ticket_id: The ticket ID (e.g., PROJ-123)
            
        Returns:
            The ticket description as a string
        """
        ticket = self.get_ticket(ticket_id)
        fields = ticket.get("fields", {})
        
        # Build requirement string from various fields
        parts = []
        
        # Summary/Title
        summary = fields.get("summary", "")
        if summary:
            parts.append(f"Title: {summary}")
        
        # Description
        description = fields.get("description")
        if description:
            # Handle Atlassian Document Format (ADF)
            if isinstance(description, dict):
                description = self._parse_adf(description)
            parts.append(f"\nDescription:\n{description}")
        
        # Acceptance Criteria (custom field - may vary by Jira setup)
        # Common custom field names: customfield_10016, customfield_10020, etc.
        for field_key, field_value in fields.items():
            if "acceptance" in field_key.lower() or "criteria" in field_key.lower():
                if field_value:
                    if isinstance(field_value, dict):
                        field_value = self._parse_adf(field_value)
                    parts.append(f"\nAcceptance Criteria:\n{field_value}")
        
        return "\n".join(parts)
    
    def _parse_adf(self, adf: Dict[str, Any]) -> str:
        """
        Parse Atlassian Document Format to plain text.
        
        Args:
            adf: ADF document structure
            
        Returns:
            Plain text representation
        """
        if not isinstance(adf, dict):
            return str(adf)
        
        content = adf.get("content", [])
        text_parts = []
        
        for block in content:
            block_type = block.get("type", "")
            
            if block_type == "paragraph":
                para_text = self._extract_text(block)
                text_parts.append(para_text)
            
            elif block_type == "bulletList":
                for item in block.get("content", []):
                    item_text = self._extract_text(item)
                    text_parts.append(f"• {item_text}")
            
            elif block_type == "orderedList":
                for i, item in enumerate(block.get("content", []), 1):
                    item_text = self._extract_text(item)
                    text_parts.append(f"{i}. {item_text}")
            
            elif block_type == "heading":
                heading_text = self._extract_text(block)
                level = block.get("attrs", {}).get("level", 1)
                text_parts.append(f"{'#' * level} {heading_text}")
            
            elif block_type == "codeBlock":
                code_text = self._extract_text(block)
                text_parts.append(f"```\n{code_text}\n```")
        
        return "\n".join(text_parts)
    
    def _extract_text(self, block: Dict[str, Any]) -> str:
        """Extract text content from an ADF block."""
        content = block.get("content", [])
        text_parts = []
        
        for item in content:
            if item.get("type") == "text":
                text_parts.append(item.get("text", ""))
            elif "content" in item:
                text_parts.append(self._extract_text(item))
        
        return "".join(text_parts)
    
    def search_tickets(self, jql: str, max_results: int = 50) -> list:
        """
        Search for tickets using JQL.
        
        Args:
            jql: JQL query string
            max_results: Maximum number of results
            
        Returns:
            List of ticket dictionaries
        """
        url = f"{self.url}/rest/api/3/search"
        
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,description,status,issuetype"
        }
        
        response = self.requests.get(
            url,
            headers=self._get_headers(),
            auth=self._get_auth(),
            params=params
        )
        
        response.raise_for_status()
        return response.json().get("issues", [])


def main():
    """Demo the Jira client."""
    print("🔗 Jira Client Demo")
    print("=" * 50)
    print()
    print("To use the Jira client, set these environment variables:")
    print("  JIRA_URL=https://your-company.atlassian.net")
    print("  JIRA_EMAIL=your-email@company.com")
    print("  JIRA_API_TOKEN=your-api-token")
    print()
    print("Then use:")
    print("  client = JiraClient()")
    print("  description = client.get_ticket_description('PROJ-123')")


if __name__ == "__main__":
    main()

