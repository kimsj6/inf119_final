# server.py
# Name: Junxi Chen, Mark Qiu, Sung Jin Kim
# Student ID: 70714925, 36732598, 10906553
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
