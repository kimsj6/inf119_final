# gui.py
# Name: Junxi Chen, Mark Qiu, Sung Jin Kim
# Student ID: 70714925
#
# Description: Gradio-based GUI for the AI Coder Multi-Agent System
# This module provides a user interface for inputting software requirements
# and displaying generated code, test cases, and model usage reports.

"""
Gradio GUI for the AI Coder Multi-Agent System.

This module creates an interactive web interface that allows users to:
1. Input software descriptions and requirements
2. View generated code in real-time
3. See test case results
4. Monitor model usage statistics

The GUI communicates with the multi-agent system via MCP protocol.
"""

import gradio as gr
import asyncio
import os
import sys
from typing import Tuple, Generator
import json

# Import our modules
from client import (
    run_requirements_agent,
    run_code_agent,
    run_test_agent,
    get_mcp_session
)
from usage_tracker import get_tracker, global_tracker


# Default Expense Comparator description
DEFAULT_DESCRIPTION = """Expense Comparator is a finance software application that helps users compare their expenses across different time periods. Users can input their expenses and categorize them into different categories such as groceries, transportation, entertainment, etc. The application will provide a visual representation of their expenses through charts and graphs, allowing users to easily compare their spending habits between different timeframes. Users can also set custom date ranges for comparison. The main function of the software is to provide users with a clear understanding of their spending patterns and identify areas where they can make adjustments to improve their financial well-being."""


async def run_agents_async(
    description: str,
    progress_callback=None
) -> Tuple[str, str, str, str, str]:
    """
    Run all agents asynchronously and return their outputs.
    
    This function orchestrates the multi-agent workflow:
    1. Requirements Analyzer Agent extracts structured requirements
    2. Code Generator Agent creates the application code
    3. Test Generator Agent creates and runs test cases
    
    Args:
        description: The software description to process
        progress_callback: Optional callback for progress updates
        
    Returns:
        Tuple of (requirements, code_summary, test_results, usage_report_json, usage_summary)
    """
    # Reset the usage tracker for a fresh run
    global_tracker.reset()
    
    # Get MCP session and run agents
    async with get_mcp_session() as session:
        # Step 1: Run Requirements Agent
        if progress_callback:
            progress_callback("🔍 Analyzing requirements...")
        
        requirements = await run_requirements_agent(description, session)
        
        # Step 2: Run Code Agent
        if progress_callback:
            progress_callback("💻 Generating code...")
            
        code_summary = await run_code_agent(requirements, session)
        
        # Step 3: Run Test Agent
        if progress_callback:
            progress_callback("🧪 Generating and running tests...")
            
        test_results = await run_test_agent(requirements, session)
    
    # Get usage report
    usage_json = global_tracker.get_usage_report_json()
    usage_summary = global_tracker.get_summary()
    
    # Save usage report to file
    global_tracker.save_report("output/model_usage_report.json")
    
    return requirements, code_summary, test_results, usage_json, usage_summary


def run_generation(description: str) -> Tuple[str, str, str, str, str]:
    """
    Synchronous wrapper for running the multi-agent system.
    
    This function is called by the Gradio interface when the user
    clicks the generate button.
    
    Args:
        description: The software description input by the user
        
    Returns:
        Tuple of outputs for the Gradio interface
    """
    if not description.strip():
        return (
            "❌ Error: Please provide a software description.",
            "",
            "",
            "{}",
            "No usage data - please run the system first."
        )
    
    try:
        # Run the async function
        result = asyncio.run(run_agents_async(description))
        return result
    except Exception as e:
        error_msg = f"❌ Error during generation: {str(e)}"
        return (
            error_msg,
            error_msg,
            error_msg,
            "{}",
            f"Error occurred: {str(e)}"
        )


def read_generated_files() -> str:
    """
    Read and display all generated code files.
    
    Scans the output directory and returns the contents of all
    generated Python files in a formatted string.
    
    Returns:
        Formatted string containing all generated code
    """
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    
    if not os.path.exists(output_dir):
        return "No generated files found. Run the generation first."
    
    result = []
    
    # Walk through output directory
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, output_dir)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    result.append(f"{'='*60}")
                    result.append(f"📄 FILE: {rel_path}")
                    result.append(f"{'='*60}")
                    result.append(content)
                    result.append("\n")
                except Exception as e:
                    result.append(f"Error reading {rel_path}: {e}\n")
    
    if not result:
        return "No Python files found in output directory."
    
    return "\n".join(result)


def refresh_files():
    """Refresh the generated files display."""
    return read_generated_files()


def get_test_file_content() -> str:
    """
    Read the generated test file content.
    
    Returns:
        The content of the test file or an error message
    """
    test_path = os.path.join(
        os.path.dirname(__file__), 
        "output", 
        "test_expense_comparator.py"
    )
    
    if os.path.exists(test_path):
        try:
            with open(test_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading test file: {e}"
    
    return "Test file not yet generated."


def get_usage_report() -> Tuple[str, str]:
    """
    Get the current usage report.
    
    Returns:
        Tuple of (JSON report, summary text)
    """
    return (
        global_tracker.get_usage_report_json(),
        global_tracker.get_summary()
    )


def create_gui() -> gr.Blocks:
    """
    Create and configure the Gradio interface.
    
    This function builds the complete GUI layout with:
    - Input section for software description
    - Output tabs for requirements, code, tests, and usage
    - Control buttons for generation and refresh
    
    Returns:
        Configured Gradio Blocks interface
    """
    
    # Custom CSS for better styling
    custom_css = """
    .main-container {
        max-width: 1400px;
        margin: auto;
    }
    .output-box {
        font-family: 'Fira Code', 'Monaco', monospace;
        font-size: 13px;
    }
    .header-text {
        text-align: center;
        margin-bottom: 20px;
    }
    .status-box {
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0;
    }
    """
    
    with gr.Blocks(
        title="AI Coder - Multi-Agent System",
        css=custom_css,
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="blue",
        )
    ) as demo:
        
        # Header
        gr.Markdown(
            """
            # 🤖 AI Coder - Multi-Agent System
            ### IN4MATX 119 Final Project
            
            This system uses **Model Context Protocol (MCP)** to coordinate multiple AI agents:
            - 🔍 **Requirements Analyzer**: Extracts structured requirements from descriptions
            - 💻 **Code Generator**: Creates runnable Python application code
            - 🧪 **Test Generator**: Produces and executes comprehensive test cases
            
            ---
            """,
            elem_classes=["header-text"]
        )
        
        with gr.Row():
            # Left column - Input
            with gr.Column(scale=1):
                gr.Markdown("### 📝 Input")
                
                description_input = gr.Textbox(
                    label="Software Description",
                    placeholder="Enter the software description and requirements...",
                    lines=12,
                    value=DEFAULT_DESCRIPTION,
                    info="Describe the software application you want to generate"
                )
                
                with gr.Row():
                    generate_btn = gr.Button(
                        "🚀 Generate Code & Tests",
                        variant="primary",
                        size="lg"
                    )
                    clear_btn = gr.Button(
                        "🗑️ Clear",
                        variant="secondary"
                    )
                
                status_output = gr.Textbox(
                    label="Status",
                    lines=2,
                    interactive=False,
                    value="Ready to generate..."
                )
            
            # Right column - Outputs
            with gr.Column(scale=2):
                gr.Markdown("### 📤 Output")
                
                with gr.Tabs():
                    # Requirements Tab
                    with gr.TabItem("📋 Requirements"):
                        requirements_output = gr.Textbox(
                            label="Analyzed Requirements",
                            lines=20,
                            interactive=False,
                            elem_classes=["output-box"]
                        )
                    
                    # Generated Code Tab
                    with gr.TabItem("💻 Generated Code"):
                        with gr.Row():
                            refresh_code_btn = gr.Button(
                                "🔄 Refresh Files",
                                size="sm"
                            )
                        code_output = gr.Textbox(
                            label="Code Summary",
                            lines=15,
                            interactive=False
                        )
                        files_output = gr.Textbox(
                            label="Generated Files",
                            lines=25,
                            interactive=False,
                            elem_classes=["output-box"]
                        )
                    
                    # Test Results Tab
                    with gr.TabItem("🧪 Test Results"):
                        test_output = gr.Textbox(
                            label="Test Generation & Execution Results",
                            lines=20,
                            interactive=False,
                            elem_classes=["output-box"]
                        )
                        test_code_output = gr.Textbox(
                            label="Test File Content",
                            lines=25,
                            interactive=False,
                            elem_classes=["output-box"]
                        )
                    
                    # Usage Report Tab
                    with gr.TabItem("📊 Model Usage"):
                        gr.Markdown(
                            """
                            ### Model Usage Tracking Report
                            This section displays the API usage statistics for each model
                            in the multi-agent system.
                            """
                        )
                        usage_json_output = gr.Code(
                            label="Usage Report (JSON)",
                            language="json",
                            lines=10
                        )
                        usage_summary_output = gr.Textbox(
                            label="Usage Summary",
                            lines=15,
                            interactive=False
                        )
        
        # Footer with instructions
        gr.Markdown(
            """
            ---
            ### 📖 Instructions
            1. Enter or modify the software description in the input box
            2. Click **Generate Code & Tests** to start the multi-agent system
            3. View results in the tabs above
            4. The **Model Usage** tab shows API call and token statistics
            
            ### ⚙️ How to Run Tests Manually
            ```bash
            cd output
            python -m pytest test_expense_comparator.py -v
            ```
            """
        )
        
        # Event handlers
        def on_generate(description):
            """
            Handle the generate button click.
            
            This function runs the multi-agent system and returns results
            for all output components in the GUI.
            """
            try:
                # Run the generation
                requirements, code_summary, test_results, usage_json, usage_summary = run_generation(description)
                
                # Read generated files
                files_content = read_generated_files()
                test_code = get_test_file_content()
                
                return (
                    "✅ Generation complete!",
                    requirements,
                    code_summary,
                    files_content,
                    test_results,
                    test_code,
                    usage_json,
                    usage_summary
                )
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                import traceback
                traceback.print_exc()
                return (
                    error_msg,
                    error_msg,
                    "",
                    "",
                    "",
                    "",
                    "{}",
                    ""
                )
        
        generate_btn.click(
            fn=on_generate,
            inputs=[description_input],
            outputs=[
                status_output,
                requirements_output,
                code_output,
                files_output,
                test_output,
                test_code_output,
                usage_json_output,
                usage_summary_output
            ]
        )
        
        def on_clear():
            """Clear all outputs and reset the interface."""
            return (
                DEFAULT_DESCRIPTION,  # description_input
                "Ready to generate...",  # status_output
                "",  # requirements_output
                "",  # code_output
                "",  # files_output
                "",  # test_output
                "",  # test_code_output
                "{}",  # usage_json_output
                ""  # usage_summary_output
            )
        
        clear_btn.click(
            fn=on_clear,
            outputs=[
                description_input,
                status_output,
                requirements_output,
                code_output,
                files_output,
                test_output,
                test_code_output,
                usage_json_output,
                usage_summary_output
            ]
        )
        
        refresh_code_btn.click(
            fn=refresh_files,
            outputs=[files_output]
        )
    
    return demo


def main():
    """
    Main entry point for the GUI application.
    
    Launches the Gradio interface on localhost.
    """
    print("🚀 Starting AI Coder GUI...")
    print("=" * 50)
    
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Create and launch the GUI
    demo = create_gui()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()

