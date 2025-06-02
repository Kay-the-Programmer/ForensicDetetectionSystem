"""
IoT Forensic Application CLI

This module provides a command-line interface for the IoT forensic application
using the Click library.
"""

import os
import click
import json
from datetime import datetime
from typing import Dict, List, Any

from src import knowledge_base as kb
from src import acquisition as acq
from src import analysis as anl
from src import reporting as rep

@click.group()
def cli():
    """IoT Forensic Application - A tool for IoT device forensic analysis."""
    pass

# Knowledge Base Commands
@cli.group()
def kb_cmd():
    """Commands for managing the IoT device knowledge base."""
    pass

@kb_cmd.command("add")
@click.option("--name", required=True, help="Device name")
@click.option("--manufacturer", required=True, help="Device manufacturer")
@click.option("--model", required=True, help="Device model")
@click.option("--os", required=True, help="Operating system")
@click.option("--storage-type", required=True, help="Type of storage")
@click.option("--data-paths", required=True, help="Common data paths (comma-separated)")
@click.option("--protocols", required=True, help="Communication protocols (comma-separated)")
@click.option("--cloud-service", required=True, help="Associated cloud service")
@click.option("--notes", default="", help="Additional notes")
def kb_add(name, manufacturer, model, os, storage_type, data_paths, protocols, cloud_service, notes):
    """Add a new device to the knowledge base."""
    # Parse comma-separated lists
    data_paths_list = [path.strip() for path in data_paths.split(",")]
    protocols_list = [protocol.strip() for protocol in protocols.split(",")]
    
    # Add the device to the knowledge base
    device_id = kb.add_device(
        name=name,
        manufacturer=manufacturer,
        model=model,
        os=os,
        storage_type=storage_type,
        data_paths=data_paths_list,
        communication_protocols=protocols_list,
        cloud_service=cloud_service,
        notes=notes
    )
    
    click.echo(f"Device added successfully with ID: {device_id}")

@kb_cmd.command("list")
def kb_list():
    """List all devices in the knowledge base."""
    devices = kb.list_devices()
    
    if not devices:
        click.echo("No devices found in the knowledge base.")
        return
    
    click.echo("\nDevices in the knowledge base:")
    click.echo("-" * 80)
    
    for device in devices:
        click.echo(f"ID: {device['id']}")
        click.echo(f"Name: {device['name']}")
        click.echo(f"Manufacturer: {device['manufacturer']}")
        click.echo(f"Model: {device['model']}")
        click.echo("-" * 80)

@kb_cmd.command("get")
@click.argument("device_id")
def kb_get(device_id):
    """Get details of a specific device."""
    device = kb.get_device(device_id)
    
    if not device:
        click.echo(f"Device with ID {device_id} not found.")
        return
    
    click.echo("\nDevice Details:")
    click.echo("-" * 80)
    click.echo(f"ID: {device['id']}")
    click.echo(f"Name: {device['name']}")
    click.echo(f"Manufacturer: {device['manufacturer']}")
    click.echo(f"Model: {device['model']}")
    click.echo(f"OS: {device['os']}")
    click.echo(f"Storage Type: {device['storage_type']}")
    
    click.echo("\nData Paths:")
    for path in device['data_paths']:
        click.echo(f"- {path}")
    
    click.echo("\nCommunication Protocols:")
    for protocol in device['communication_protocols']:
        click.echo(f"- {protocol}")
    
    click.echo(f"\nCloud Service: {device['cloud_service']}")
    
    if device['notes']:
        click.echo(f"\nNotes: {device['notes']}")
    
    click.echo(f"\nDate Added: {device['date_added']}")

@kb_cmd.command("update")
@click.argument("device_id")
@click.option("--name", help="Device name")
@click.option("--manufacturer", help="Device manufacturer")
@click.option("--model", help="Device model")
@click.option("--os", help="Operating system")
@click.option("--storage-type", help="Type of storage")
@click.option("--data-paths", help="Common data paths (comma-separated)")
@click.option("--protocols", help="Communication protocols (comma-separated)")
@click.option("--cloud-service", help="Associated cloud service")
@click.option("--notes", help="Additional notes")
def kb_update(device_id, name, manufacturer, model, os, storage_type, data_paths, protocols, cloud_service, notes):
    """Update a device in the knowledge base."""
    # Parse comma-separated lists if provided
    data_paths_list = None
    if data_paths:
        data_paths_list = [path.strip() for path in data_paths.split(",")]
    
    protocols_list = None
    if protocols:
        protocols_list = [protocol.strip() for protocol in protocols.split(",")]
    
    # Update the device
    success = kb.update_device(
        device_id=device_id,
        name=name,
        manufacturer=manufacturer,
        model=model,
        os=os,
        storage_type=storage_type,
        data_paths=data_paths_list,
        communication_protocols=protocols_list,
        cloud_service=cloud_service,
        notes=notes
    )
    
    if success:
        click.echo(f"Device {device_id} updated successfully.")
    else:
        click.echo(f"Device with ID {device_id} not found.")

@kb_cmd.command("delete")
@click.argument("device_id")
@click.confirmation_option(prompt="Are you sure you want to delete this device?")
def kb_delete(device_id):
    """Delete a device from the knowledge base."""
    success = kb.delete_device(device_id)
    
    if success:
        click.echo(f"Device {device_id} deleted successfully.")
    else:
        click.echo(f"Device with ID {device_id} not found.")

# Acquisition Commands
@cli.group()
def acquire():
    """Commands for acquiring data from IoT devices."""
    pass

@acquire.command("simulate")
@click.argument("device_id")
@click.option("--source-type", required=True, type=click.Choice(["log", "config"]), help="Type of data to acquire")
@click.option("--output-file", help="Name of the output file")
def acquire_simulate(device_id, source_type, output_file):
    """Simulate data acquisition from a device."""
    # Check if the device exists
    device = kb.get_device(device_id)
    if not device:
        click.echo(f"Device with ID {device_id} not found.")
        return
    
    # Simulate the acquisition
    output_path, sha256_hash, timestamp = acq.simulate_acquisition(
        device_id=device_id,
        source_type=source_type,
        output_filename=output_file
    )
    
    click.echo(f"Acquisition completed successfully.")
    click.echo(f"Output file: {output_path}")
    click.echo(f"SHA256 hash: {sha256_hash}")
    click.echo(f"Timestamp: {timestamp}")

@acquire.command("verify")
@click.argument("file_path")
@click.argument("expected_hash")
def acquire_verify(file_path, expected_hash):
    """Verify the integrity of an acquired file."""
    # Verify the file integrity
    is_intact = acq.verify_file_integrity(file_path, expected_hash)
    
    if is_intact:
        click.echo(f"File integrity verified: {file_path}")
        click.echo(f"Hash matches: {expected_hash}")
    else:
        click.echo(f"File integrity check failed: {file_path}")
        click.echo(f"Expected hash: {expected_hash}")

@acquire.command("list")
def acquire_list():
    """List all acquisitions."""
    acquisitions = acq.list_acquisitions()
    
    if not acquisitions:
        click.echo("No acquisitions found.")
        return
    
    click.echo("\nAcquisitions:")
    click.echo("-" * 80)
    
    for i, acquisition in enumerate(acquisitions, 1):
        click.echo(f"Acquisition #{i}:")
        click.echo(f"  Device ID: {acquisition['device_id']}")
        click.echo(f"  Source Type: {acquisition['source_type']}")
        click.echo(f"  Timestamp: {acquisition['timestamp']}")
        click.echo(f"  File Path: {acquisition['file_path']}")
        click.echo(f"  SHA256 Hash: {acquisition['sha256_hash']}")
        click.echo("-" * 80)

# Analysis Commands
@cli.group()
def analyze():
    """Commands for analyzing acquired data."""
    pass

@analyze.command("parse-log")
@click.argument("file_path")
@click.option("--output-file", help="Path to save the parsed results")
def analyze_parse_log(file_path, output_file):
    """Parse a log file and extract structured information."""
    # Check if the file exists
    if not os.path.exists(file_path):
        click.echo(f"File not found: {file_path}")
        return
    
    # Read the file content
    with open(file_path, 'r') as f:
        log_content = f.read()
    
    # Parse the log file
    parsed_logs = anl.parse_log_file(log_content)
    
    # Analyze the parsed logs
    analysis_results = anl.analyze_log_events(parsed_logs)
    
    # Display a summary
    click.echo(f"\nLog Analysis Summary:")
    click.echo(f"Total Entries: {analysis_results.get('total_entries', 0)}")
    click.echo(f"Time Range: {analysis_results.get('start_time', 'Unknown')} to {analysis_results.get('end_time', 'Unknown')}")
    click.echo(f"Duration: {analysis_results.get('duration_seconds', 0)} seconds")
    
    if "event_counts" in analysis_results:
        click.echo("\nEvent Counts:")
        for level, count in analysis_results["event_counts"].items():
            click.echo(f"  {level}: {count}")
    
    click.echo(f"\nError Events: {analysis_results.get('error_count', 0)}")
    click.echo(f"Warning Events: {analysis_results.get('warning_count', 0)}")
    
    # Save the results if an output file is specified
    if output_file:
        output_data = {
            "parsed_logs": parsed_logs,
            "analysis_results": analysis_results
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=4)
        
        click.echo(f"\nResults saved to: {output_file}")
    
    return parsed_logs, analysis_results

@analyze.command("parse-config")
@click.argument("file_path")
@click.option("--output-file", help="Path to save the parsed results")
def analyze_parse_config(file_path, output_file):
    """Parse a configuration file and extract structured information."""
    # Check if the file exists
    if not os.path.exists(file_path):
        click.echo(f"File not found: {file_path}")
        return
    
    # Read the file content
    with open(file_path, 'r') as f:
        config_content = f.read()
    
    # Parse the configuration file
    parsed_config = anl.parse_config_file(config_content)
    
    if "error" in parsed_config:
        click.echo(f"Error parsing configuration: {parsed_config['error']}")
        return
    
    # Analyze the parsed configuration
    analysis_results = anl.analyze_config(parsed_config)
    
    # Display a summary
    click.echo(f"\nConfiguration Analysis Summary:")
    
    if "device_info" in analysis_results:
        device_info = analysis_results["device_info"]
        click.echo(f"Device Name: {device_info.get('name', 'Unknown')}")
        click.echo(f"Device ID: {device_info.get('id', 'Unknown')}")
        click.echo(f"Version: {device_info.get('version', 'Unknown')}")
    
    if "network_info" in analysis_results:
        network = analysis_results["network_info"]
        click.echo(f"\nNetwork Type: {network.get('type', 'Unknown')}")
        click.echo(f"IP: {network.get('ip', 'Unknown')}")
    
    if "sensor_count" in analysis_results:
        click.echo(f"\nSensor Count: {analysis_results['sensor_count']}")
    
    if "cloud_enabled" in analysis_results:
        click.echo(f"\nCloud Enabled: {analysis_results['cloud_enabled']}")
        if analysis_results['cloud_enabled']:
            click.echo(f"Cloud Service: {analysis_results.get('cloud_service', 'Unknown')}")
    
    if "security_issues" in analysis_results and analysis_results["security_issues"]:
        click.echo("\nSecurity Issues:")
        for issue in analysis_results["security_issues"]:
            click.echo(f"- {issue}")
    
    # Save the results if an output file is specified
    if output_file:
        output_data = {
            "parsed_config": parsed_config,
            "analysis_results": analysis_results
        }
        
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=4)
        
        click.echo(f"\nResults saved to: {output_file}")
    
    return parsed_config, analysis_results

# Reporting Commands
@cli.group()
def report():
    """Commands for generating forensic reports."""
    pass

@report.command("generate")
@click.option("--case-name", required=True, help="Name of the case")
@click.option("--investigator", required=True, help="Name of the investigator")
@click.option("--device-id", required=True, help="ID of the device")
@click.option("--acquisition-ids", required=True, help="Comma-separated list of acquisition timestamps")
@click.option("--log-file", help="Path to the analyzed log file")
@click.option("--config-file", help="Path to the analyzed configuration file")
@click.option("--notes", default="", help="Additional notes")
def report_generate(case_name, investigator, device_id, acquisition_ids, log_file, config_file, notes):
    """Generate a forensic report."""
    # Get the device information
    device = kb.get_device(device_id)
    if not device:
        click.echo(f"Device with ID {device_id} not found.")
        return
    
    # Get the acquisition details
    acquisition_timestamps = [timestamp.strip() for timestamp in acquisition_ids.split(",")]
    acquisitions = acq.list_acquisitions()
    
    acquisition_details = []
    for acquisition in acquisitions:
        if acquisition["timestamp"] in acquisition_timestamps:
            acquisition_details.append(acquisition)
    
    if not acquisition_details:
        click.echo("No matching acquisitions found.")
        return
    
    # Initialize analysis results
    analysis_results = {}
    
    # Add log analysis results if a log file is provided
    if log_file and os.path.exists(log_file):
        with open(log_file, 'r') as f:
            log_data = json.load(f)
            if "analysis_results" in log_data:
                analysis_results.update(log_data["analysis_results"])
    
    # Add config analysis results if a config file is provided
    if config_file and os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config_data = json.load(f)
            if "analysis_results" in config_data:
                # Merge with existing analysis results
                for key, value in config_data["analysis_results"].items():
                    if key not in analysis_results:
                        analysis_results[key] = value
    
    # Generate the report
    report_path = rep.generate_report(
        case_name=case_name,
        investigator=investigator,
        device_info=device,
        acquisition_details=acquisition_details,
        analysis_results=analysis_results,
        notes=notes
    )
    
    click.echo(f"Report generated successfully: {report_path}")

@report.command("list")
def report_list():
    """List all generated reports."""
    reports = rep.list_reports()
    
    if not reports:
        click.echo("No reports found.")
        return
    
    click.echo("\nReports:")
    click.echo("-" * 80)
    
    for i, report in enumerate(reports, 1):
        click.echo(f"Report #{i}:")
        click.echo(f"  Case Name: {report['case_name']}")
        click.echo(f"  Investigator: {report['investigator']}")
        click.echo(f"  Timestamp: {report['timestamp']}")
        click.echo(f"  Path: {report['path']}")
        click.echo("-" * 80)

@report.command("get")
@click.argument("report_path")
def report_get(report_path):
    """Get a specific report."""
    report_data = rep.get_report(report_path)
    
    if not report_data:
        click.echo(f"Report not found: {report_path}")
        return
    
    click.echo("\nReport Details:")
    click.echo("-" * 80)
    click.echo(f"Case Name: {report_data.get('case_name', 'Unknown')}")
    click.echo(f"Investigator: {report_data.get('investigator', 'Unknown')}")
    click.echo(f"Timestamp: {report_data.get('timestamp', 'Unknown')}")
    
    # Display a summary of the report content
    click.echo("\nReport contains:")
    
    if "device_info" in report_data:
        click.echo("- Device information")
    
    if "acquisition_details" in report_data:
        click.echo(f"- {len(report_data['acquisition_details'])} acquisition(s)")
    
    if "analysis_results" in report_data:
        analysis = report_data["analysis_results"]
        if "total_entries" in analysis:
            click.echo(f"- Log analysis with {analysis['total_entries']} entries")
        if "device_info" in analysis:
            click.echo("- Configuration analysis")
    
    if "notes" in report_data and report_data["notes"]:
        click.echo("- Additional notes")
    
    click.echo(f"\nFull report available at: {report_path}")

if __name__ == "__main__":
    cli()