"""
IoT Device Acquisition Module

This module provides functionality to simulate data acquisition from IoT devices
and ensure data integrity through SHA256 hashing.
"""

import os
import hashlib
import json
import random
import string
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Path to the forensic output directory
FORENSIC_OUTPUT_DIR = "forensic_output"

def ensure_output_dir_exists() -> None:
    """
    Ensures that the forensic output directory exists.
    If it doesn't exist, creates it.
    """
    if not os.path.exists(FORENSIC_OUTPUT_DIR):
        os.makedirs(FORENSIC_OUTPUT_DIR)

def generate_random_content(size: int = 1024, content_type: str = "log") -> str:
    """
    Generates random content to simulate acquired data.
    
    Args:
        size: Size of the content in bytes
        content_type: Type of content to generate (log, config, etc.)
        
    Returns:
        str: The generated content
    """
    if content_type == "log":
        # Generate simulated log entries
        log_entries = []
        current_time = datetime.now()
        
        for i in range(size // 100):  # Approximate number of log entries
            event_types = ["INFO", "WARNING", "ERROR", "DEBUG"]
            event_type = random.choice(event_types)
            
            # Generate a random timestamp within the last 24 hours
            timestamp = current_time.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            ).isoformat()
            
            # Generate a random message
            messages = [
                "Device started",
                "Connection established",
                "Data sent to cloud",
                "Configuration updated",
                "Firmware update available",
                "Sensor reading: {}".format(random.randint(0, 100)),
                "Battery level: {}%".format(random.randint(0, 100)),
                "Connection lost",
                "Reconnecting...",
                "Device shutdown"
            ]
            message = random.choice(messages)
            
            log_entry = f"[{timestamp}] [{event_type}] {message}"
            log_entries.append(log_entry)
        
        return "\n".join(log_entries)
    
    elif content_type == "config":
        # Generate simulated configuration data
        config = {
            "device": {
                "name": "".join(random.choices(string.ascii_uppercase + string.digits, k=8)),
                "id": "".join(random.choices(string.ascii_uppercase + string.digits, k=16)),
                "version": f"{random.randint(1, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}"
            },
            "network": {
                "ssid": "".join(random.choices(string.ascii_uppercase + string.digits, k=10)),
                "password": "".join(random.choices(string.ascii_letters + string.digits, k=16)),
                "type": random.choice(["WiFi", "Ethernet", "Bluetooth", "Zigbee", "Z-Wave"]),
                "ip": f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
                "port": random.randint(1024, 65535)
            },
            "sensors": [
                {
                    "id": f"SENSOR_{i}",
                    "type": random.choice(["temperature", "humidity", "motion", "light", "sound"]),
                    "interval": random.randint(1, 60),
                    "unit": random.choice(["C", "%", "lux", "dB"])
                }
                for i in range(random.randint(1, 5))
            ],
            "cloud": {
                "enabled": random.choice([True, False]),
                "service": random.choice(["AWS IoT", "Azure IoT Hub", "Google Cloud IoT", "Custom"]),
                "endpoint": f"https://{''.join(random.choices(string.ascii_lowercase, k=8))}.{''.join(random.choices(string.ascii_lowercase, k=5))}.com/api",
                "api_key": "".join(random.choices(string.ascii_letters + string.digits, k=32))
            },
            "settings": {
                "logging_level": random.choice(["DEBUG", "INFO", "WARNING", "ERROR"]),
                "update_interval": random.randint(1, 24),
                "timezone": random.choice(["UTC", "EST", "CST", "PST", "GMT"]),
                "language": random.choice(["en", "fr", "es", "de", "zh"])
            }
        }
        
        return json.dumps(config, indent=4)
    
    else:
        # Generate random binary-like data
        return ''.join(random.choices(string.printable, k=size))

def calculate_sha256(data: str) -> str:
    """
    Calculates the SHA256 hash of the given data.
    
    Args:
        data: The data to hash
        
    Returns:
        str: The SHA256 hash
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def simulate_acquisition(
    device_id: str,
    source_type: str,
    output_filename: Optional[str] = None
) -> Tuple[str, str, str]:
    """
    Simulates data acquisition from a device.
    
    Args:
        device_id: The ID of the device to acquire data from
        source_type: The type of data to acquire (log, config, etc.)
        output_filename: The name of the output file (optional)
        
    Returns:
        Tuple[str, str, str]: The output file path, the SHA256 hash, and the acquisition timestamp
    """
    ensure_output_dir_exists()
    
    # Generate a timestamp for the acquisition
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Generate a filename if not provided
    if output_filename is None:
        output_filename = f"{device_id}_{source_type}_{timestamp}.dat"
    
    # Generate the output file path
    output_path = os.path.join(FORENSIC_OUTPUT_DIR, output_filename)
    
    # Generate random content based on the source type
    content = generate_random_content(size=random.randint(1024, 10240), content_type=source_type)
    
    # Calculate the SHA256 hash of the content
    sha256_hash = calculate_sha256(content)
    
    # Write the content to the output file
    with open(output_path, 'w') as f:
        f.write(content)
    
    # Create a metadata file with acquisition details
    metadata = {
        "device_id": device_id,
        "source_type": source_type,
        "timestamp": timestamp,
        "sha256_hash": sha256_hash,
        "file_path": output_path,
        "file_size": len(content)
    }
    
    metadata_path = f"{output_path}.meta"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    return output_path, sha256_hash, timestamp

def verify_file_integrity(file_path: str, expected_hash: str) -> bool:
    """
    Verifies the integrity of a file by comparing its SHA256 hash with the expected hash.
    
    Args:
        file_path: The path to the file to verify
        expected_hash: The expected SHA256 hash
        
    Returns:
        bool: True if the file is intact, False otherwise
    """
    if not os.path.exists(file_path):
        return False
    
    # Read the file content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Calculate the SHA256 hash of the content
    actual_hash = calculate_sha256(content)
    
    # Compare the actual hash with the expected hash
    return actual_hash == expected_hash

def list_acquisitions() -> List[Dict]:
    """
    Lists all acquisitions in the forensic output directory.
    
    Returns:
        List[Dict]: A list of acquisition metadata
    """
    ensure_output_dir_exists()
    
    acquisitions = []
    
    # Iterate through all files in the forensic output directory
    for filename in os.listdir(FORENSIC_OUTPUT_DIR):
        if filename.endswith(".meta"):
            # Read the metadata file
            metadata_path = os.path.join(FORENSIC_OUTPUT_DIR, filename)
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            acquisitions.append(metadata)
    
    return acquisitions