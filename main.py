"""
IoT Forensic Application

Main entry point for the IoT forensic application.
"""

import sys
from src.cli import cli
# from src.gui import App # Import is now conditional

if __name__ == "__main__":
    if "--gui" in sys.argv:
        # Launch the GUI application
        from src.gui import App # Conditional import
        gui_app = App()
        gui_app.run()
    # Check if any CLI command is being invoked or if it's just 'python main.py'
    # Click handles its own help, so we only need to ensure CLI is called if not --gui.
    # If sys.argv has more than 'main.py' and it's not '--gui', assume it's for CLI.
    # Or if it's just 'python main.py', default to CLI.
    elif len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] != "--gui"):
        cli()
    # The original help logic for main.py might be redundant if Click handles all CLI paths.
    # However, keeping a simple main.py help if user types `python main.py --help`
    elif "--help" in sys.argv or "-h" in sys.argv: # This specific check might be less necessary now
        print("IoT Forensic Tool")
        print("Usage: python main.py [CLI_COMMANDS... | --gui]")
        print("\nOptions:")
        print("  --gui         Launch the Graphical User Interface.")
        print("  --help, -h    Show this help message (for main.py itself).")
        print("\nFor CLI commands and help, run 'python main.py [COMMAND] --help'.")
        print("If no options are provided, the Command Line Interface (CLI) will start by default.")
    # Fallback, though the above elif should cover most CLI cases.
    else:
        cli()