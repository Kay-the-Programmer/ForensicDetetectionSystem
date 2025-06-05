# IoT Forensic Application

A command-line application and graphical user interface (GUI) for acquiring, analyzing, and reporting on data from IoT devices.

## Overview

This application provides a foundational approach for IoT device forensics, with the following core modules, accessible via both CLI and GUI:

1.  **IoT Device Knowledge Base Manager**: Store and manage information about IoT devices.
2.  **Acquisition Module**: Simulate data acquisition from devices and ensure data integrity.
3.  **Analysis Module**: Parse and analyze common IoT data types (log files, configuration files).
4.  **Reporting Module**: Generate forensic reports based on acquisition and analysis results.

## Project Structure

```
ForensicDetection/
├── data/                      # Directory for storing the device knowledge base
├── forensic_output/           # Directory for storing acquired data
├── forensic_reports/          # Directory for storing generated reports
├── src/                       # Source code
│   ├── knowledge_base.py      # IoT Device Knowledge Base Manager module
│   ├── acquisition.py         # Acquisition module
│   ├── analysis.py            # Analysis module
│   ├── reporting.py           # Reporting module
│   └── cli.py                 # Command-line interface
└── main.py                    # Main entry point
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ForensicDetection.git
   cd ForensicDetection
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```
   pip install click
   ```

## Usage

The application can be run via its Command Line Interface (CLI) or a Graphical User Interface (GUI).

### Launching the Application

*   **To start the Command Line Interface (CLI):**
    ```bash
    python main.py
    ```
    Once the CLI is running, type `help` or `[command] --help` for detailed options for each command group (e.g., `kb-cmd --help`).

*   **To start the Graphical User Interface (GUI):**
    ```bash
    python main.py --gui
    ```
    This will launch the desktop application, providing access to all forensic modules through a user-friendly interface.

### CLI Commands Overview

The application provides a command-line interface with various commands for managing the IoT forensic workflow.

### Knowledge Base Commands

```
# Add a device to the knowledge base
python main.py kb-cmd add --name "Smart Thermostat" --manufacturer "EcoTemp" --model "ET-100" --os "EcoOS 2.1" --storage-type "Flash" --data-paths "/var/log/,/etc/config/" --protocols "WiFi,MQTT" --cloud-service "AWS IoT" --notes "Common in residential settings"

# List all devices in the knowledge base
python main.py kb-cmd list

# Get details of a specific device
python main.py kb-cmd get DEV_20230101123456

# Update a device in the knowledge base
python main.py kb-cmd update DEV_20230101123456 --name "Smart Thermostat Pro"

# Delete a device from the knowledge base
python main.py kb-cmd delete DEV_20230101123456
```

### Acquisition Commands

```
# Simulate data acquisition from a device
python main.py acquire simulate DEV_20230101123456 --source-type log

# Verify the integrity of an acquired file
python main.py acquire verify forensic_output/DEV_20230101123456_log_20230101123456.dat 5f4dcc3b5aa765d61d8327deb882cf99

# List all acquisitions
python main.py acquire list
```

### Analysis Commands

```
# Parse and analyze a log file
python main.py analyze parse-log forensic_output/DEV_20230101123456_log_20230101123456.dat --output-file analysis_results/log_analysis.json

# Parse and analyze a configuration file
python main.py analyze parse-config forensic_output/DEV_20230101123456_config_20230101123456.dat --output-file analysis_results/config_analysis.json
```

### Reporting Commands

```
# Generate a forensic report
python main.py report generate --case-name "IoT Security Incident" --investigator "John Doe" --device-id DEV_20230101123456 --acquisition-ids 20230101123456,20230101123457 --log-file analysis_results/log_analysis.json --config-file analysis_results/config_analysis.json --notes "Suspicious activity detected"

# List all reports
python main.py report list

# Get details of a specific report
python main.py report get forensic_reports/IoT_Security_Incident_20230101123456.json
```

## Example Workflow

1. Add a device to the knowledge base:
   ```
   python main.py kb-cmd add --name "Smart Camera" --manufacturer "SecureCam" --model "SC-200" --os "SecureOS 3.0" --storage-type "SD Card" --data-paths "/var/log/,/media/footage/" --protocols "WiFi,RTSP" --cloud-service "Google Cloud" --notes "Used for home security"
   ```

2. Simulate data acquisition:
   ```
   python main.py acquire simulate DEV_20230101123456 --source-type log
   python main.py acquire simulate DEV_20230101123456 --source-type config
   ```

3. Analyze the acquired data:
   ```
   python main.py analyze parse-log forensic_output/DEV_20230101123456_log_20230101123456.dat --output-file log_analysis.json
   python main.py analyze parse-config forensic_output/DEV_20230101123456_config_20230101123456.dat --output-file config_analysis.json
   ```

4. Generate a forensic report:
   ```
   python main.py report generate --case-name "Camera Investigation" --investigator "Jane Smith" --device-id DEV_20230101123456 --acquisition-ids 20230101123456,20230101123457 --log-file log_analysis.json --config-file config_analysis.json --notes "Investigation of unauthorized access"
   ```

## Technical Details

- **Language**: Python 3.x
- **Libraries**: Click (for CLI), hashlib (for SHA256 hashing), json, os, datetime, re (for regex parsing)
- **Data Storage**: JSON files for the device knowledge base and report metadata

## Future Enhancements

- Database integration for more robust data storage
- Support for real device acquisition (not just simulation)
- Advanced analysis techniques using machine learning
- Web interface for easier interaction
- Integration with other forensic tools and frameworks

## License

This project is licensed under the MIT License - see the LICENSE file for details.