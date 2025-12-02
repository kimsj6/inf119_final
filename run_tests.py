# run_tests.py
# Name: Junxi Chen, Mark Qiu, Sung Jin Kim
# Student ID: 70714925
#
# Description: Script to automatically run all generated tests
# This script executes pytest on the generated test file and displays results.

"""
Test Runner Script for AI Coder Generated Tests.

This script provides an easy way to run all generated tests:
1. Navigates to the output directory
2. Runs pytest with verbose output
3. Displays pass/fail summary

Usage:
    python run_tests.py
"""

import subprocess
import sys
import os


def run_tests():
    """
    Run all generated tests and display results.
    
    Executes pytest on the test_expense_comparator.py file in the output
    directory and prints the results with verbose output.
    
    Returns:
        int: Exit code from pytest (0 = all tests passed)
    """
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "output")
    test_file = os.path.join(output_dir, "test_expense_comparator.py")
    
    print("=" * 60)
    print("AI CODER - TEST RUNNER")
    print("=" * 60)
    
    # Check if test file exists
    if not os.path.exists(test_file):
        print(f"\n❌ Error: Test file not found!")
        print(f"   Expected: {test_file}")
        print("\n   Please run the code generation first:")
        print("   python main.py --cli")
        print("   or")
        print("   python gui.py")
        return 1
    
    print(f"\n📂 Output directory: {output_dir}")
    print(f"🧪 Test file: test_expense_comparator.py")
    print("\n" + "-" * 60)
    print("Running tests...")
    print("-" * 60 + "\n")
    
    # Run pytest
    try:
        result = subprocess.run(
            [
                sys.executable, "-m", "pytest",
                test_file,
                "-v",           # Verbose output
                "--tb=short",   # Short tracebacks
                "-rA"           # Show all test results
            ],
            cwd=output_dir
        )
        
        print("\n" + "-" * 60)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
        else:
            print(f"⚠️  Some tests failed (exit code: {result.returncode})")
        
        print("-" * 60)
        return result.returncode
        
    except FileNotFoundError:
        print("\n❌ Error: pytest not found!")
        print("   Install with: pip install pytest")
        return 1
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)

