# main.py
# Name: Junxi Chen, Mark Qiu, Sung Jin Kim
# Student ID: 70714925
#
# Description: Main entry point for the AI Coder Multi-Agent System
# This module provides a unified entry point for running the system in
# either GUI mode or CLI mode.

"""
Main Entry Point for AI Coder Multi-Agent System.

This module provides a simple way to start the application:
- Default: Launches the Gradio GUI
- With --cli flag: Runs the command-line interface

Usage:
    python main.py          # Start GUI
    python main.py --cli    # Run CLI mode
"""

import sys
import argparse


def main():
    """
    Main entry point that parses arguments and launches the appropriate mode.
    
    Modes:
        GUI (default): Launches Gradio web interface on http://127.0.0.1:7860
        CLI: Runs the multi-agent system directly in terminal
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="AI Coder - Multi-Agent System for Code Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Start the GUI
  python main.py --cli        # Run in CLI mode
  python main.py --help       # Show this help message

For more information, see README.md
        """
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run in command-line mode instead of GUI'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=7860,
        help='Port for GUI server (default: 7860)'
    )
    
    args = parser.parse_args()
    
    if args.cli:
        # Run in CLI mode
        print("=" * 60)
        print("AI CODER - MULTI-AGENT SYSTEM (CLI MODE)")
        print("=" * 60)
        
        import asyncio
        from client import main as run_client
        
        asyncio.run(run_client())
    else:
        # Run in GUI mode
        print("=" * 60)
        print("AI CODER - MULTI-AGENT SYSTEM (GUI MODE)")
        print("=" * 60)
        print(f"\nStarting Gradio interface on port {args.port}...")
        print(f"Open your browser to: http://127.0.0.1:{args.port}")
        print("\nPress Ctrl+C to stop the server.")
        print("=" * 60)
        
        from gui import create_gui
        import gradio as gr
        import os
        
        # Ensure output directory exists
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create and launch the GUI
        demo, custom_css = create_gui()
        demo.launch(
            server_name="127.0.0.1",
            server_port=args.port,
            share=False,
            show_error=True,
            css=custom_css,
            theme=gr.themes.Soft(
                primary_hue="indigo",
                secondary_hue="blue",
            ),
        )


if __name__ == "__main__":
    main()

