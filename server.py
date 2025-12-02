# server.py
# Name: Junxi Chen, Mark Qiu, Sung Jin Kim
# Student ID: 70714925
#
# Description: MCP Server for the AI Coder Multi-Agent System
# This module implements the MCP server that provides tools for the agents.
# It handles file operations, code validation, and test execution.

"""
MCP Server for the AI Coder Multi-Agent System.

This server implements the Model Context Protocol (MCP) and provides
tools that the multi-agent system uses to:
1. Read and write files in the output directory
2. Validate Python syntax
3. Run pytest tests
4. Get domain-specific requirements

The server runs as a subprocess and communicates via stdio transport.

Tools Provided:
- get_expense_comparator_requirements: Get detailed requirements template
- validate_python_syntax: Check Python code for syntax errors
- run_tests: Execute pytest on test files
- write_file: Write content to files in output directory
- read_file: Read content from files in output directory
- create_directory: Create directories in output directory
- append_to_file: Append content to existing files
"""

from mcp.server.fastmcp import FastMCP
import os
import subprocess
import sys
import json
from typing import Optional

# Initialize the FastMCP server with application name
# This creates the MCP server that will handle tool requests from clients
mcp = FastMCP("AICoder")

# Define the output directory where all generated files will be stored
# This keeps generated code separate from the system code
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")


# =============================================================================
# DOMAIN-SPECIFIC TOOLS
# =============================================================================
# These tools provide specialized functionality for the Expense Comparator project.
# =============================================================================

@mcp.tool()
def get_expense_comparator_requirements() -> str:
    """
    Get the detailed requirements for the Expense Comparator application.
    
    This tool provides a comprehensive requirements specification that guides
    the code generation process. It includes:
    - Data model requirements
    - Core functionality requirements
    - User interface requirements
    - Testing requirements
    
    Returns:
        str: Detailed requirements specification as formatted text
    """
    
    requirements = """
    EXPENSE COMPARATOR APPLICATION REQUIREMENTS
    ============================================
    
    1. DATA MODEL REQUIREMENTS:
       - Expense class with: id (UUID string), amount (float), category (Category enum), 
         date (datetime), description (string)
       - Category enumeration: GROCERIES, TRANSPORTATION, ENTERTAINMENT, 
         UTILITIES, HEALTHCARE, DINING, SHOPPING, OTHER
       - DateRange class for comparison periods with: start_date, end_date (both datetime)
    
    2. EXPENSE MANAGEMENT (ExpenseManager class):
       - add_expense(amount, category, date, description) -> Expense
         Creates a new expense with auto-generated UUID
       - get_expense(id) -> Optional[Expense]
         Retrieves expense by ID, returns None if not found
       - update_expense(id, **kwargs) -> bool
         Updates expense fields, returns True if successful
       - delete_expense(id) -> bool
         Removes expense, returns True if successful
       - list_expenses() -> List[Expense]
         Returns all expenses
       - filter_by_category(category: Category) -> List[Expense]
         Returns expenses matching category
       - filter_by_date_range(start: datetime, end: datetime) -> List[Expense]
         Returns expenses within date range (inclusive)
    
    3. COMPARISON FEATURES (comparator module):
       - compare_periods(expenses1, expenses2) -> dict
         Compare total spending between two expense lists
         Returns: {period1_total, period2_total, difference, percentage_change}
       - get_category_totals(expenses) -> dict
         Calculate total spending per category
         Returns: {category_name: total_amount, ...}
       - calculate_percentage_change(old_value, new_value) -> float
         Calculate percentage change between values
       - get_spending_summary(expenses) -> dict
         Returns: {total, average, min, max, count}
    
    4. VISUALIZATION REQUIREMENTS (visualizer module, using matplotlib):
       - create_bar_chart(data: dict, title: str, filename: str) -> str
         Generate bar chart from category totals, save as PNG
       - create_pie_chart(data: dict, title: str, filename: str) -> str
         Generate pie chart for expense distribution
       - create_comparison_chart(period1: dict, period2: dict, filename: str) -> str
         Generate side-by-side comparison bar chart
    
    5. DATA PERSISTENCE (data_store module):
       - save_expenses(expenses: List[Expense], filename: str) -> bool
         Serialize expenses to JSON file
       - load_expenses(filename: str) -> List[Expense]
         Deserialize expenses from JSON file
       - expense_to_dict(expense: Expense) -> dict
         Convert Expense to JSON-serializable dict
       - dict_to_expense(data: dict) -> Expense
         Convert dict back to Expense object
    
    6. REPORTING:
       - Generate summary report for a date range
       - Export reports as text or JSON
       - Calculate statistics: total, average, min, max spending
    
    7. USER INTERFACE (cli module):
       - Command-line interface using argparse
       - Commands:
         * add: Add new expense (--amount, --category, --date, --description)
         * list: List all expenses (optional: --category, --start-date, --end-date)
         * delete: Delete expense by ID (--id)
         * compare: Compare two date ranges
         * visualize: Generate charts (--type, --output)
         * export: Save expenses to JSON file
         * import: Load expenses from JSON file
       - Input validation for amounts (positive numbers) and dates (valid format)
       - Clear error messages for invalid input
       - Help documentation for all commands
    
    8. CODE QUALITY REQUIREMENTS:
       - Type hints for ALL function parameters and return values
       - Docstrings for ALL classes, methods, and functions
       - Follow PEP 8 style guidelines
       - Proper exception handling
       - Unit tests with 80%+ coverage
       - Clean code structure with separation of concerns
    """
    return requirements


# =============================================================================
# CODE VALIDATION TOOLS
# =============================================================================
# These tools help ensure generated code is syntactically correct.
# =============================================================================

@mcp.tool()
def validate_python_syntax(code: str) -> str:
    """
    Validate Python code syntax without executing it.
    
    This tool compiles the provided Python code to check for syntax errors.
    It does NOT execute the code, making it safe to use on untrusted input.
    
    Args:
        code: The Python code string to validate
    
    Returns:
        str: "Syntax is valid" if no errors, or error details with line number
        
    Example:
        >>> validate_python_syntax("def foo():\\n    return 1")
        "Syntax is valid"
        >>> validate_python_syntax("def foo(")
        "Syntax error at line 1: unexpected EOF while parsing"
    """
    try:
        # Compile the code without executing it
        # '<string>' is the filename used in error messages
        # 'exec' mode allows multi-line code
        compile(code, '<string>', 'exec')
        return "Syntax is valid"
    except SyntaxError as e:
        return f"Syntax error at line {e.lineno}: {e.msg}"


# =============================================================================
# TEST EXECUTION TOOLS
# =============================================================================
# These tools handle running pytest on generated test files.
# =============================================================================

@mcp.tool()
def run_tests(test_filename: str) -> str:
    """
    Run pytest on a test file and return the results.
    
    This tool executes pytest in a subprocess on the specified test file.
    It captures both stdout and stderr output and returns the combined result.
    
    Args:
        test_filename: The test file to run (path relative to output directory)
                      Example: "test_expense_comparator.py"
    
    Returns:
        str: Pytest output including test results, passes, failures, and any errors
        
    Note:
        - Has a 120-second timeout to prevent hanging
        - Runs with -v flag for verbose output
        - Uses --tb=short for concise tracebacks
    """
    full_path = os.path.join(OUTPUT_DIR, test_filename)
    
    try:
        # Run pytest as a subprocess
        # Using sys.executable ensures we use the same Python interpreter
        result = subprocess.run(
            [sys.executable, "-m", "pytest", full_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120,  # 2-minute timeout
            cwd=OUTPUT_DIR  # Run from output directory for proper imports
        )
        
        # Combine stdout and stderr for complete output
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += f"\nSTDERR:\n{result.stderr}"
        
        return output if output else "Tests completed with no output"
    
    except subprocess.TimeoutExpired:
        return "Error: Tests timed out after 120 seconds"
    except FileNotFoundError:
        return f"Error: Test file not found: {full_path}"
    except Exception as e:
        return f"Error running tests: {str(e)}"


# =============================================================================
# FILE OPERATION TOOLS
# =============================================================================
# These tools handle file I/O operations in the output directory.
# All paths are relative to the OUTPUT_DIR for security.
# =============================================================================

@mcp.tool()
def write_file(filename: str, content: str) -> str:
    """
    Write content to a file in the output directory.
    
    This tool creates or overwrites a file with the given content.
    It automatically creates any necessary parent directories.
    
    Args:
        filename: Path relative to output directory (e.g., "expense_comparator/models.py")
        content: The content to write to the file
    
    Returns:
        str: Success message with full path, or error description
        
    Note:
        - Creates parent directories automatically
        - Overwrites existing files without warning
        - Uses UTF-8 encoding
    """
    full_path = os.path.join(OUTPUT_DIR, filename)
    
    try:
        # Ensure the directory exists (handles nested paths like "expense_comparator/models.py")
        dir_path = os.path.dirname(full_path)
        if dir_path:  # Only create if there's a directory component
            os.makedirs(dir_path, exist_ok=True)
        
        # Write the content
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote file: {full_path}"
    
    except PermissionError:
        return f"Error: Permission denied writing to {full_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"


@mcp.tool()
def read_file(filename: str) -> str:
    """
    Read content from a file in the output directory.
    
    This tool reads and returns the entire content of a file.
    Useful for the Test Generator Agent to read generated code.
    
    Args:
        filename: Path relative to output directory (e.g., "expense_comparator/models.py")
    
    Returns:
        str: File content, or error description if file not found
    """
    full_path = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found: {full_path}"
    except PermissionError:
        return f"Error: Permission denied reading {full_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def create_directory(path: str) -> str:
    """
    Create a directory at the specified path.
    
    This tool creates a directory and any necessary parent directories.
    It's idempotent - won't fail if the directory already exists.
    
    Args:
        path: Directory path relative to output directory
              Example: "expense_comparator" or "expense_comparator/tests"
    
    Returns:
        str: Success message with full path, or error description
    """
    full_path = os.path.join(OUTPUT_DIR, path)
    
    try:
        os.makedirs(full_path, exist_ok=True)
        return f"Successfully created directory: {full_path}"
    except PermissionError:
        return f"Error: Permission denied creating {full_path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"


@mcp.tool()
def append_to_file(filename: str, content: str) -> str:
    """
    Append content to an existing file.
    
    This tool adds content to the end of an existing file without
    overwriting the current content. Creates the file if it doesn't exist.
    
    Args:
        filename: Path relative to output directory
        content: The content to append
    
    Returns:
        str: Success message, or error description
    """
    full_path = os.path.join(OUTPUT_DIR, filename)
    
    try:
        # Ensure directory exists
        dir_path = os.path.dirname(full_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
        
        with open(full_path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully appended to file: {full_path}"
    
    except PermissionError:
        return f"Error: Permission denied appending to {full_path}"
    except Exception as e:
        return f"Error appending to file: {str(e)}"


@mcp.tool()
def list_directory(path: str = "") -> str:
    """
    List contents of a directory in the output folder.
    
    This tool returns a list of files and subdirectories at the given path.
    Useful for verifying that files were created correctly.
    
    Args:
        path: Directory path relative to output directory (empty string for root)
    
    Returns:
        str: Formatted list of directory contents, or error description
    """
    full_path = os.path.join(OUTPUT_DIR, path)
    
    try:
        if not os.path.exists(full_path):
            return f"Error: Directory not found: {full_path}"
        
        if not os.path.isdir(full_path):
            return f"Error: Not a directory: {full_path}"
        
        entries = os.listdir(full_path)
        
        if not entries:
            return f"Directory is empty: {full_path}"
        
        # Format the output with type indicators
        result = [f"Contents of {full_path}:"]
        for entry in sorted(entries):
            entry_path = os.path.join(full_path, entry)
            if os.path.isdir(entry_path):
                result.append(f"  📁 {entry}/")
            else:
                result.append(f"  📄 {entry}")
        
        return "\n".join(result)
    
    except PermissionError:
        return f"Error: Permission denied listing {full_path}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
# Start the MCP server when this script is run directly.
# =============================================================================

if __name__ == "__main__":
    # Ensure output directory exists before starting the server
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"MCP Server starting... Output directory: {OUTPUT_DIR}", file=sys.stderr)
    
    # Run the MCP server using stdio transport
    # This allows the server to communicate with clients via stdin/stdout
    mcp.run(transport="stdio")
