"""
Command Line Interface for AI Test Case Generator
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .generator import TestCaseGenerator
from .edge_cases import EdgeCaseAnalyzer


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="ai-test-generator",
        description="Generate test cases from requirements using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s generate --input requirements.txt
  %(prog)s generate --input story.txt --format pytest --output tests/
  %(prog)s generate --jira PROJ-123 --format gherkin
  %(prog)s interactive
  %(prog)s analyze --input requirements.txt
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate test cases")
    gen_parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input file containing requirement(s)"
    )
    gen_parser.add_argument(
        "--jira", "-j",
        type=str,
        help="Jira ticket ID to fetch requirement from"
    )
    gen_parser.add_argument(
        "--format", "-f",
        type=str,
        default="gherkin",
        choices=["gherkin", "pytest", "testng", "plain", "json"],
        help="Output format (default: gherkin)"
    )
    gen_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory or file"
    )
    gen_parser.add_argument(
        "--num-cases", "-n",
        type=int,
        default=10,
        help="Target number of test cases (default: 10)"
    )
    gen_parser.add_argument(
        "--no-edge-cases",
        action="store_true",
        help="Don't include edge cases"
    )
    
    # Interactive command
    int_parser = subparsers.add_parser("interactive", help="Interactive mode")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze requirements for edge cases")
    analyze_parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Input file containing requirement(s)"
    )
    
    return parser


def cmd_generate(args) -> int:
    """Handle the generate command."""
    # Get requirement text
    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"❌ Error: Input file not found: {args.input}", file=sys.stderr)
            return 1
        requirement = input_path.read_text()
    elif args.jira:
        try:
            from .jira_client import JiraClient
            client = JiraClient()
            requirement = client.get_ticket_description(args.jira)
        except ImportError:
            print("❌ Error: Jira integration requires additional setup", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"❌ Error fetching Jira ticket: {e}", file=sys.stderr)
            return 1
    else:
        print("❌ Error: Either --input or --jira is required", file=sys.stderr)
        return 1
    
    print("🧠 Generating test cases...")
    print(f"   Format: {args.format}")
    print(f"   Target cases: {args.num_cases}")
    print()
    
    # Generate test cases
    try:
        generator = TestCaseGenerator()
        result = generator.generate(
            requirement=requirement,
            output_format=args.format,
            num_cases=args.num_cases,
            include_edge_cases=not args.no_edge_cases
        )
    except Exception as e:
        print(f"❌ Error generating test cases: {e}", file=sys.stderr)
        return 1
    
    # Output result
    if args.output:
        output_path = Path(args.output)
        
        # Determine file extension
        extensions = {
            "gherkin": ".feature",
            "pytest": ".py",
            "testng": ".java",
            "plain": ".txt",
            "json": ".json"
        }
        
        if output_path.is_dir():
            output_file = output_path / f"generated_tests{extensions[args.format]}"
        else:
            output_file = output_path
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result)
        print(f"✅ Test cases written to: {output_file}")
    else:
        print(result)
    
    return 0


def cmd_interactive(args) -> int:
    """Handle interactive mode."""
    print("🧠 AI Test Case Generator - Interactive Mode")
    print("=" * 50)
    print("Enter your requirement (press Enter twice when done):")
    print()
    
    lines = []
    empty_count = 0
    
    while empty_count < 1:
        try:
            line = input()
            if line == "":
                empty_count += 1
            else:
                empty_count = 0
                lines.append(line)
        except EOFError:
            break
    
    requirement = "\n".join(lines)
    
    if not requirement.strip():
        print("❌ No requirement provided", file=sys.stderr)
        return 1
    
    # Get format preference
    print()
    print("Select output format:")
    print("  1. Gherkin/BDD (default)")
    print("  2. Python pytest")
    print("  3. Java TestNG")
    print("  4. Plain text")
    print("  5. JSON")
    
    try:
        choice = input("\nChoice [1]: ").strip() or "1"
        formats = {"1": "gherkin", "2": "pytest", "3": "testng", "4": "plain", "5": "json"}
        output_format = formats.get(choice, "gherkin")
    except EOFError:
        output_format = "gherkin"
    
    print()
    print("🧠 Generating test cases...")
    print()
    
    try:
        generator = TestCaseGenerator()
        result = generator.generate(
            requirement=requirement,
            output_format=output_format
        )
        print(result)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    
    return 0


def cmd_analyze(args) -> int:
    """Handle the analyze command."""
    input_path = Path(args.input)
    
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    
    requirement = input_path.read_text()
    
    print("🔍 Analyzing requirement for edge cases...")
    print()
    
    analyzer = EdgeCaseAnalyzer()
    categorized = analyzer.analyze_with_categories(requirement)
    
    total = 0
    for category, cases in categorized.items():
        print(f"📁 {category}:")
        for case in cases:
            print(f"   • {case}")
            total += 1
        print()
    
    print(f"📊 Total edge cases identified: {total}")
    
    return 0


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    commands = {
        "generate": cmd_generate,
        "interactive": cmd_interactive,
        "analyze": cmd_analyze,
    }
    
    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())

