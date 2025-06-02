"""
IoT Device Analysis Module

This module provides functionality to analyze data acquired from IoT devices,
including parsing log files and configuration files.
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

def parse_log_file(log_content: str) -> List[Dict[str, Any]]:
    """
    Parses a log file and extracts structured information.
    
    Args:
        log_content: The content of the log file
        
    Returns:
        List[Dict]: A list of parsed log entries
    """
    # Define a regex pattern to match log entries
    # Format: [timestamp] [level] message
    pattern = r'\[(.*?)\] \[(.*?)\] (.*)'
    
    parsed_entries = []
    
    # Process each line in the log content
    for line in log_content.strip().split('\n'):
        match = re.match(pattern, line)
        if match:
            timestamp_str, level, message = match.groups()
            
            try:
                # Parse the timestamp
                timestamp = datetime.fromisoformat(timestamp_str)
                
                # Create a structured log entry
                entry = {
                    "timestamp": timestamp.isoformat(),
                    "level": level,
                    "message": message
                }
                
                # Extract additional information based on the message content
                if "Sensor reading:" in message:
                    # Extract sensor reading value
                    sensor_match = re.search(r'Sensor reading: (\d+)', message)
                    if sensor_match:
                        entry["sensor_value"] = int(sensor_match.group(1))
                
                elif "Battery level:" in message:
                    # Extract battery level
                    battery_match = re.search(r'Battery level: (\d+)%', message)
                    if battery_match:
                        entry["battery_level"] = int(battery_match.group(1))
                
                parsed_entries.append(entry)
            except (ValueError, TypeError):
                # Skip entries with invalid timestamps
                continue
    
    return parsed_entries

def analyze_log_events(parsed_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes parsed log entries to extract insights.
    
    Args:
        parsed_logs: A list of parsed log entries
        
    Returns:
        Dict: Analysis results
    """
    if not parsed_logs:
        return {"error": "No log entries to analyze"}
    
    # Initialize counters and collectors
    event_counts = {}
    error_events = []
    warning_events = []
    sensor_readings = []
    battery_levels = []
    
    # Collect the earliest and latest timestamps
    timestamps = [datetime.fromisoformat(entry["timestamp"]) for entry in parsed_logs]
    start_time = min(timestamps)
    end_time = max(timestamps)
    
    # Process each log entry
    for entry in parsed_logs:
        # Count events by level
        level = entry["level"]
        event_counts[level] = event_counts.get(level, 0) + 1
        
        # Collect error and warning events
        if level == "ERROR":
            error_events.append(entry)
        elif level == "WARNING":
            warning_events.append(entry)
        
        # Collect sensor readings and battery levels
        if "sensor_value" in entry:
            sensor_readings.append(entry["sensor_value"])
        
        if "battery_level" in entry:
            battery_levels.append(entry["battery_level"])
    
    # Calculate statistics
    analysis = {
        "total_entries": len(parsed_logs),
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "event_counts": event_counts,
        "error_count": len(error_events),
        "warning_count": len(warning_events)
    }
    
    # Add sensor statistics if available
    if sensor_readings:
        analysis["sensor_stats"] = {
            "count": len(sensor_readings),
            "min": min(sensor_readings),
            "max": max(sensor_readings),
            "avg": sum(sensor_readings) / len(sensor_readings)
        }
    
    # Add battery statistics if available
    if battery_levels:
        analysis["battery_stats"] = {
            "count": len(battery_levels),
            "min": min(battery_levels),
            "max": max(battery_levels),
            "avg": sum(battery_levels) / len(battery_levels)
        }
    
    return analysis

def parse_config_file(config_content: str) -> Dict[str, Any]:
    """
    Parses a configuration file and extracts structured information.
    
    Args:
        config_content: The content of the configuration file
        
    Returns:
        Dict: The parsed configuration
    """
    try:
        # Attempt to parse as JSON
        config = json.loads(config_content)
        return config
    except json.JSONDecodeError:
        # If not valid JSON, return an error
        return {"error": "Invalid configuration format"}

def analyze_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes a device configuration to extract insights.
    
    Args:
        config: The parsed configuration
        
    Returns:
        Dict: Analysis results
    """
    if "error" in config:
        return config
    
    analysis = {
        "device_info": {},
        "network_info": {},
        "sensor_count": 0,
        "cloud_enabled": False,
        "security_issues": []
    }
    
    # Extract device information
    if "device" in config:
        device = config["device"]
        analysis["device_info"] = {
            "name": device.get("name", "Unknown"),
            "id": device.get("id", "Unknown"),
            "version": device.get("version", "Unknown")
        }
    
    # Extract network information
    if "network" in config:
        network = config["network"]
        analysis["network_info"] = {
            "type": network.get("type", "Unknown"),
            "ip": network.get("ip", "Unknown"),
            "port": network.get("port", "Unknown")
        }
        
        # Check for security issues
        if "password" in network:
            # Check if password is stored in plaintext
            analysis["security_issues"].append("Network password stored in plaintext")
            
            # Check if password is weak (less than 8 characters)
            if len(network["password"]) < 8:
                analysis["security_issues"].append("Weak network password (less than 8 characters)")
    
    # Count sensors
    if "sensors" in config and isinstance(config["sensors"], list):
        analysis["sensor_count"] = len(config["sensors"])
        
        # Extract sensor types
        sensor_types = [sensor.get("type", "Unknown") for sensor in config["sensors"]]
        analysis["sensor_types"] = list(set(sensor_types))
    
    # Check cloud configuration
    if "cloud" in config:
        cloud = config["cloud"]
        analysis["cloud_enabled"] = cloud.get("enabled", False)
        analysis["cloud_service"] = cloud.get("service", "Unknown")
        
        # Check for security issues
        if "api_key" in cloud:
            # Check if API key is stored in plaintext
            analysis["security_issues"].append("Cloud API key stored in plaintext")
    
    # Check settings
    if "settings" in config:
        settings = config["settings"]
        analysis["settings"] = {
            "logging_level": settings.get("logging_level", "Unknown"),
            "update_interval": settings.get("update_interval", "Unknown"),
            "timezone": settings.get("timezone", "Unknown")
        }
    
    return analysis

def extract_events_by_type(parsed_logs: List[Dict[str, Any]], event_type: str) -> List[Dict[str, Any]]:
    """
    Extracts log events of a specific type.
    
    Args:
        parsed_logs: A list of parsed log entries
        event_type: The type of events to extract (INFO, WARNING, ERROR, DEBUG)
        
    Returns:
        List[Dict]: Filtered log entries
    """
    return [entry for entry in parsed_logs if entry["level"] == event_type]

def extract_events_by_keyword(parsed_logs: List[Dict[str, Any]], keyword: str) -> List[Dict[str, Any]]:
    """
    Extracts log events containing a specific keyword in the message.
    
    Args:
        parsed_logs: A list of parsed log entries
        keyword: The keyword to search for
        
    Returns:
        List[Dict]: Filtered log entries
    """
    return [entry for entry in parsed_logs if keyword.lower() in entry["message"].lower()]

def extract_time_range(parsed_logs: List[Dict[str, Any]], start_time: str, end_time: str) -> List[Dict[str, Any]]:
    """
    Extracts log events within a specific time range.
    
    Args:
        parsed_logs: A list of parsed log entries
        start_time: The start time in ISO format
        end_time: The end time in ISO format
        
    Returns:
        List[Dict]: Filtered log entries
    """
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        
        return [
            entry for entry in parsed_logs 
            if start <= datetime.fromisoformat(entry["timestamp"]) <= end
        ]
    except ValueError:
        # Return empty list if time format is invalid
        return []