from mcp.server.fastmcp import FastMCP
import os
import subprocess
import sys
import json
from typing import Optional

mcp = FastMCP("AICoder")

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
#@mcp.tool()
#def add(a: int, b: int) -> int:
#    """Add two numbers"""
#    return a + b


@mcp.tool()
def get_expense_comparator_requirements() -> str:
    """
    Get the detailed requirements for the Expense Comparator application.
    This is a specialized tool for the Expense Comparator project.
    
    Returns:
        Detailed requirements specification
    """
    
    requirements = """
    EXPENSE COMPARATOR APPLICATION REQUIREMENTS
    ============================================
    
    1. DATA MODEL REQUIREMENTS:
       - Expense class with: id, amount, category, date, description
       - Category enumeration: GROCERIES, TRANSPORTATION, ENTERTAINMENT, 
         UTILITIES, HEALTHCARE, DINING, SHOPPING, OTHER
       - Date range class for comparison periods
    
    2. EXPENSE MANAGEMENT:
       - Add new expense with category, amount, date, description
       - Edit existing expense
       - Delete expense
       - List all expenses
       - Filter expenses by category
       - Filter expenses by date range
    
    3. COMPARISON FEATURES:
       - Compare total spending between two date ranges
       - Compare spending by category between two date ranges
       - Calculate percentage change between periods
       - Identify top spending categories
    
    4. VISUALIZATION REQUIREMENTS:
       - Generate bar charts for category comparison
       - Generate pie charts for expense distribution
       - Generate line charts for spending trends over time
       - Export charts as images
    
    5. DATA PERSISTENCE:
       - Save expenses to JSON file
       - Load expenses from JSON file
       - Support for multiple user profiles (optional)
    
    6. REPORTING:
       - Generate summary report for a date range
       - Export reports as text or JSON
       - Calculate statistics: total, average, min, max spending
    
    7. USER INTERFACE:
       - Command-line interface for all operations
       - Input validation for amounts and dates
       - Clear error messages
       - Help documentation
    
    8. CODE QUALITY:
       - Type hints for all functions
       - Docstrings for all classes and methods
       - Unit tests with 80%+ coverage
       - Clean code structure with separation of concerns
    """
    return requirements

@mcp.tool()
def validate_python_syntax(code: str) -> str:
    """
    Validate Python code syntax without executing it.
    
    Args:
        code: The Python code to validate
    
    Returns:
        Validation result (valid or error details)
    """
    try:
        compile(code, '<string>', 'exec')
        return "Syntax is valid"
    except SyntaxError as e:
        return f"Syntax error at line {e.lineno}: {e.msg}"


@mcp.tool()
def run_tests(test_filename: str) -> str:
    """
    Run pytest on a test file and return results.
    
    Args:
        test_filename: The test file to run (relative to output directory)
    
    Returns:
        Test results output
    """
    full_path = os.path.join(OUTPUT_DIR, test_filename)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", full_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=OUTPUT_DIR
        )
        
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        
        return output if output else "Tests completed with no output"
    except subprocess.TimeoutExpired:
        return "Error: Tests timed out after 120 seconds"
    except Exception as e:
        return f"Error running tests: {str(e)}"



@mcp.tool()
def write_file(filename: str, content: str) -> str:
    """
    Write content to a file in the output directory.
    
    Args:
        filename: The name of the file to write (relative to output directory)
        content: The content to write to the file
    
    Returns:
        Success message or error description
    """
    full_path = os.path.join(OUTPUT_DIR, filename)
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote file: {full_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
def read_file(filename: str) -> str:
    """
    Read content from a file in the output directory.
    
    Args:
        filename: The name of the file to read (relative to output directory)
    
    Returns:
        File content or error description
    """
    full_path = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {full_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def create_directory(path: str) -> str:
    """
    Create a directory at the specified path.
    
    Args:
        path: The directory path to create (relative to output directory)
    
    Returns:
        Success message or error description
    """
    full_path = os.path.join(OUTPUT_DIR, path)
    try:
        os.makedirs(full_path, exist_ok=True)
        return f"Successfully created directory: {full_path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


@mcp.tool()
def append_to_file(filename: str, content: str) -> str:
    """
    Append content to an existing file.
    
    Args:
        filename: The file to append to (relative to output directory)
        content: The content to append
    
    Returns:
        Success message or error description
    """
    full_path = os.path.join(OUTPUT_DIR, filename)
    try:
        with open(full_path, 'a', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully appended to file: {full_path}"
    except Exception as e:
        return f"Error appending to file: {str(e)}"


if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    mcp.run(transport="stdio")