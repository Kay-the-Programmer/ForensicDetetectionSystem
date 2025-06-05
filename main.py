"""
IoT Forensic Application

Main entry point for the IoT forensic application.
"""

import sys
from src.cli import cli
from src.gui import App # Import the App class from src.gui

if __name__ == "__main__":
    if "--gui" in sys.argv:
        # Launch the GUI application
        gui_app = App()
        gui_app.run()
    elif len(sys.argv) > 1 and sys.argv[1] not in ["--help", "-h"]: # Basic check for other unknown args
        print(f"Unknown argument: {sys.argv[1]}")
        print("Usage: python main.py [--gui | --help]")
        print("Defaulting to CLI mode.")
        cli()
    elif "--help" in sys.argv or "-h" in sys.argv:
        print("IoT Forensic Tool")
        print("Usage: python main.py [command]")
        print("\nOptions:")
        print("  --gui         Launch the Graphical User Interface.")
        print("  --help, -h    Show this help message and exit.")
        print("\nIf no options are provided, the Command Line Interface (CLI) will start.")
        print("For CLI specific help, run the CLI and use its 'help' command.")
    else:
        # Default to CLI if no arguments or only known non-GUI arguments are present
        cli()