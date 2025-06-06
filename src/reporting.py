"""
IoT Device Reporting Module

This module provides functionality to generate forensic reports based on
acquisition details and analysis findings.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

# Path to the forensic reports directory
FORENSIC_REPORTS_DIR = "forensic_reports"

def ensure_reports_dir_exists() -> None:
    """
    Ensures that the forensic reports directory exists.
    If it doesn't exist, creates it.
    """
    if not os.path.exists(FORENSIC_REPORTS_DIR):
        os.makedirs(FORENSIC_REPORTS_DIR)

def generate_report(
    case_name: str,
    investigator: str,
    device_info: Dict[str, Any],
    acquisition_details: List[Dict[str, Any]],
    analysis_results: Dict[str, Any],
    notes: str = "",
    video_analysis_results: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generates a forensic report based on acquisition details and analysis findings.
    
    Args:
        case_name: The name of the case
        investigator: The name of the investigator
        device_info: Information about the device
        acquisition_details: Details about the acquisition process
        analysis_results: Results of the analysis
        notes: Additional notes
        
    Returns:
        str: The path to the generated report
    """
    ensure_reports_dir_exists()
    
    # Generate a timestamp for the report
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Generate a filename for the report
    report_filename = f"{case_name.replace(' ', '_')}_{timestamp}.txt"
    report_path = os.path.join(FORENSIC_REPORTS_DIR, report_filename)
    
    # Generate the report content
    report_content = []
    
    # Add the header
    report_content.append("=" * 80)
    report_content.append(f"FORENSIC REPORT: {case_name}")
    report_content.append("=" * 80)
    report_content.append("")
    
    # Add the case information
    report_content.append("CASE INFORMATION")
    report_content.append("-" * 80)
    report_content.append(f"Case Name: {case_name}")
    report_content.append(f"Investigator: {investigator}")
    report_content.append(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_content.append("")
    
    # Add the device information
    report_content.append("DEVICE INFORMATION")
    report_content.append("-" * 80)
    report_content.append(f"Device ID: {device_info.get('id', 'Unknown')}")
    report_content.append(f"Device Name: {device_info.get('name', 'Unknown')}")
    report_content.append(f"Manufacturer: {device_info.get('manufacturer', 'Unknown')}")
    report_content.append(f"Model: {device_info.get('model', 'Unknown')}")
    report_content.append(f"Operating System: {device_info.get('os', 'Unknown')}")
    report_content.append(f"Storage Type: {device_info.get('storage_type', 'Unknown')}")
    
    # Add data paths if available
    if 'data_paths' in device_info and device_info['data_paths']:
        report_content.append("\nCommon Data Paths:")
        for path in device_info['data_paths']:
            report_content.append(f"- {path}")
    
    # Add communication protocols if available
    if 'communication_protocols' in device_info and device_info['communication_protocols']:
        report_content.append("\nCommunication Protocols:")
        for protocol in device_info['communication_protocols']:
            report_content.append(f"- {protocol}")
    
    report_content.append(f"\nCloud Service: {device_info.get('cloud_service', 'Unknown')}")
    
    if 'notes' in device_info and device_info['notes']:
        report_content.append(f"\nDevice Notes: {device_info['notes']}")
    
    report_content.append("")
    
    # Add the acquisition details
    report_content.append("ACQUISITION DETAILS")
    report_content.append("-" * 80)
    
    if acquisition_details:
        for i, acquisition in enumerate(acquisition_details, 1):
            report_content.append(f"Acquisition #{i}:")
            report_content.append(f"  Source Type: {acquisition.get('source_type', 'Unknown')}")
            report_content.append(f"  Timestamp: {acquisition.get('timestamp', 'Unknown')}")
            report_content.append(f"  File Path: {acquisition.get('file_path', 'Unknown')}")
            report_content.append(f"  File Size: {acquisition.get('file_size', 'Unknown')} bytes")
            report_content.append(f"  SHA256 Hash: {acquisition.get('sha256_hash', 'Unknown')}")
            report_content.append("")
    else:
        report_content.append("No acquisition details available.")
        report_content.append("")
    
    # Add the analysis results
    report_content.append("ANALYSIS FINDINGS")
    report_content.append("-" * 80)
    
    if analysis_results:
        # Check if we have log analysis results
        if "total_entries" in analysis_results:
            report_content.append("Log Analysis:")
            report_content.append(f"  Total Log Entries: {analysis_results.get('total_entries', 0)}")
            report_content.append(f"  Time Range: {analysis_results.get('start_time', 'Unknown')} to {analysis_results.get('end_time', 'Unknown')}")
            report_content.append(f"  Duration: {analysis_results.get('duration_seconds', 0)} seconds")
            
            # Add event counts if available
            if "event_counts" in analysis_results:
                report_content.append("\n  Event Counts:")
                for level, count in analysis_results["event_counts"].items():
                    report_content.append(f"    {level}: {count}")
            
            report_content.append(f"\n  Error Events: {analysis_results.get('error_count', 0)}")
            report_content.append(f"  Warning Events: {analysis_results.get('warning_count', 0)}")
            
            # Add sensor statistics if available
            if "sensor_stats" in analysis_results:
                stats = analysis_results["sensor_stats"]
                report_content.append("\n  Sensor Statistics:")
                report_content.append(f"    Count: {stats.get('count', 0)}")
                report_content.append(f"    Min: {stats.get('min', 'N/A')}")
                report_content.append(f"    Max: {stats.get('max', 'N/A')}")
                report_content.append(f"    Average: {stats.get('avg', 'N/A')}")
            
            # Add battery statistics if available
            if "battery_stats" in analysis_results:
                stats = analysis_results["battery_stats"]
                report_content.append("\n  Battery Statistics:")
                report_content.append(f"    Count: {stats.get('count', 0)}")
                report_content.append(f"    Min: {stats.get('min', 'N/A')}%")
                report_content.append(f"    Max: {stats.get('max', 'N/A')}%")
                report_content.append(f"    Average: {stats.get('avg', 'N/A')}%")
        
        # Check if we have config analysis results
        if "device_info" in analysis_results and isinstance(analysis_results["device_info"], dict):
            report_content.append("\nConfiguration Analysis:")
            
            # Add device info
            device_info = analysis_results["device_info"]
            report_content.append(f"  Device Name: {device_info.get('name', 'Unknown')}")
            report_content.append(f"  Device ID: {device_info.get('id', 'Unknown')}")
            report_content.append(f"  Version: {device_info.get('version', 'Unknown')}")
            
            # Add network info
            if "network_info" in analysis_results:
                network = analysis_results["network_info"]
                report_content.append("\n  Network Information:")
                report_content.append(f"    Type: {network.get('type', 'Unknown')}")
                report_content.append(f"    IP: {network.get('ip', 'Unknown')}")
                report_content.append(f"    Port: {network.get('port', 'Unknown')}")
            
            # Add sensor info
            if "sensor_count" in analysis_results:
                report_content.append(f"\n  Sensor Count: {analysis_results['sensor_count']}")
                
                if "sensor_types" in analysis_results:
                    report_content.append("  Sensor Types:")
                    for sensor_type in analysis_results["sensor_types"]:
                        report_content.append(f"    - {sensor_type}")
            
            # Add cloud info
            if "cloud_enabled" in analysis_results:
                report_content.append(f"\n  Cloud Enabled: {analysis_results['cloud_enabled']}")
                if analysis_results['cloud_enabled']:
                    report_content.append(f"  Cloud Service: {analysis_results.get('cloud_service', 'Unknown')}")
            
            # Add security issues
            if "security_issues" in analysis_results and analysis_results["security_issues"]:
                report_content.append("\n  Security Issues:")
                for issue in analysis_results["security_issues"]:
                    report_content.append(f"    - {issue}")
            
            # Add settings
            if "settings" in analysis_results:
                settings = analysis_results["settings"]
                report_content.append("\n  Settings:")
                report_content.append(f"    Logging Level: {settings.get('logging_level', 'Unknown')}")
                report_content.append(f"    Update Interval: {settings.get('update_interval', 'Unknown')} hours")
                report_content.append(f"    Timezone: {settings.get('timezone', 'Unknown')}")
        report_content.append("") # Add a blank line after config analysis or log analysis
    else:
        report_content.append("No analysis results available.")
        report_content.append("")

    # Add Video Analysis Findings
    report_content.append("VIDEO ANALYSIS FINDINGS")
    report_content.append("-" * 80)
    if video_analysis_results:
        report_content.append(f"Video Filename: {video_analysis_results.get('video_filename', 'N/A')}")
        report_content.append(f"Video Duration: {video_analysis_results.get('duration', 'N/A')} seconds")
        report_content.append(f"Detected Objects Count: {video_analysis_results.get('detected_objects_count', 0)}")
        report_content.append("Significant Events:")
        significant_events = video_analysis_results.get('significant_events')
        if significant_events and isinstance(significant_events, list):
            if significant_events:
                for event in significant_events:
                    report_content.append(f"- [{event.get('timestamp')}] {event.get('description')}")
            else: # list is empty
                report_content.append("No significant events recorded.")
        else: # not a list or None
            report_content.append("No significant events recorded.")
    else:
        report_content.append("No video analysis results available.")
    report_content.append("")
    
    # Add additional notes
    if notes:
        report_content.append("ADDITIONAL NOTES")
        report_content.append("-" * 80)
        report_content.append(notes)
        report_content.append("")
    
    # Add the footer
    report_content.append("=" * 80)
    report_content.append(f"END OF REPORT: {case_name}")
    report_content.append("=" * 80)
    
    # Write the report to a file
    with open(report_path, 'w') as f:
        f.write("\n".join(report_content))
    
    # Also create a JSON version of the report for machine readability
    report_data = {
        "case_name": case_name,
        "investigator": investigator,
        "timestamp": timestamp,
        "device_info": device_info,
        "acquisition_details": acquisition_details,
        "analysis_results": analysis_results,
        "video_analysis_results": video_analysis_results if video_analysis_results else {},
        "notes": notes
    }
    
    json_report_path = os.path.join(FORENSIC_REPORTS_DIR, f"{case_name.replace(' ', '_')}_{timestamp}.json")
    with open(json_report_path, 'w') as f:
        json.dump(report_data, f, indent=4)
    
    return report_path

def list_reports() -> List[Dict[str, Any]]:
    """
    Lists all reports in the forensic reports directory.
    
    Returns:
        List[Dict]: A list of report metadata
    """
    ensure_reports_dir_exists()
    
    reports = []
    
    # Iterate through all files in the forensic reports directory
    for filename in os.listdir(FORENSIC_REPORTS_DIR):
        if filename.endswith(".json"):
            # Read the JSON report file
            report_path = os.path.join(FORENSIC_REPORTS_DIR, filename)
            with open(report_path, 'r') as f:
                report_data = json.load(f)
            
            # Add basic metadata to the list
            reports.append({
                "filename": filename,
                "case_name": report_data.get("case_name", "Unknown"),
                "investigator": report_data.get("investigator", "Unknown"),
                "timestamp": report_data.get("timestamp", "Unknown"),
                "path": report_path
            })
    
    # Sort reports by timestamp (newest first)
    reports.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return reports

def get_report(report_path: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a report by its path.
    
    Args:
        report_path: The path to the report
        
    Returns:
        Dict or None: The report data if found, None otherwise
    """
    if not os.path.exists(report_path):
        return None
    
    # Check if it's a JSON report
    if report_path.endswith(".json"):
        with open(report_path, 'r') as f:
            return json.load(f)
    
    # If it's a text report, try to find the corresponding JSON report
    if report_path.endswith(".txt"):
        json_path = report_path.replace(".txt", ".json")
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.load(f)
    
    return None