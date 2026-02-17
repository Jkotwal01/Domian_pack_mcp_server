#!/usr/bin/env python
"""Test runner script for chatbot module tests.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --integration # Run only integration tests
    python run_tests.py --e2e        # Run only E2E tests
    python run_tests.py --coverage   # Run with coverage report
"""
import sys
import subprocess
import argparse


def run_tests(test_type=None, coverage=False):
    """Run tests with specified options."""
    cmd = ["pytest", "tests/", "-v"]
    
    # Add test type marker
    if test_type == "unit":
        cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
    elif test_type == "e2e":
        cmd.extend(["-m", "e2e"])
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    # Run tests
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run chatbot module tests")
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Run only unit tests"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run only integration tests"
    )
    parser.add_argument(
        "--e2e",
        action="store_true",
        help="Run only end-to-end tests"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    
    args = parser.parse_args()
    
    # Determine test type
    test_type = None
    if args.unit:
        test_type = "unit"
    elif args.integration:
        test_type = "integration"
    elif args.e2e:
        test_type = "e2e"
    
    # Run tests
    exit_code = run_tests(test_type, args.coverage)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
