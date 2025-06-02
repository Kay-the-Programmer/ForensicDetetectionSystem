"""
IoT Device Knowledge Base Manager Module

This module provides functionality to manage a knowledge base of IoT devices.
It allows adding, listing, retrieving, updating, and deleting device entries.
The data is stored in a JSON file.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

# Path to the knowledge base file
KB_FILE_PATH = os.path.join("data", "device_knowledge_base.json")

def ensure_kb_file_exists() -> None:
    """
    Ensures that the knowledge base file exists.
    If it doesn't exist, creates it with an empty devices list.
    """
    if not os.path.exists(os.path.dirname(KB_FILE_PATH)):
        os.makedirs(os.path.dirname(KB_FILE_PATH))
    
    if not os.path.exists(KB_FILE_PATH):
        with open(KB_FILE_PATH, 'w') as f:
            json.dump({"devices": []}, f, indent=4)

def load_kb() -> Dict[str, List[Dict[str, Any]]]:
    """
    Loads the knowledge base from the JSON file.
    
    Returns:
        Dict: The knowledge base data
    """
    ensure_kb_file_exists()
    with open(KB_FILE_PATH, 'r') as f:
        return json.load(f)

def save_kb(kb_data: Dict[str, List[Dict[str, Any]]]) -> None:
    """
    Saves the knowledge base to the JSON file.
    
    Args:
        kb_data (Dict): The knowledge base data to save
    """
    ensure_kb_file_exists()
    with open(KB_FILE_PATH, 'w') as f:
        json.dump(kb_data, f, indent=4)

def add_device(
    name: str,
    manufacturer: str,
    model: str,
    os: str,
    storage_type: str,
    data_paths: List[str],
    communication_protocols: List[str],
    cloud_service: str,
    notes: str = ""
) -> str:
    """
    Adds a new device to the knowledge base.
    
    Args:
        name: Device name
        manufacturer: Device manufacturer
        model: Device model
        os: Operating system
        storage_type: Type of storage
        data_paths: Common data paths
        communication_protocols: Communication protocols
        cloud_service: Associated cloud service
        notes: Additional notes
        
    Returns:
        str: The ID of the newly added device
    """
    kb_data = load_kb()
    
    # Generate a unique ID
    device_id = f"DEV_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Create the device entry
    device = {
        "id": device_id,
        "name": name,
        "manufacturer": manufacturer,
        "model": model,
        "os": os,
        "storage_type": storage_type,
        "data_paths": data_paths,
        "communication_protocols": communication_protocols,
        "cloud_service": cloud_service,
        "notes": notes,
        "date_added": datetime.now().isoformat()
    }
    
    # Add the device to the knowledge base
    kb_data["devices"].append(device)
    save_kb(kb_data)
    
    return device_id

def list_devices() -> List[Dict[str, Any]]:
    """
    Lists all devices in the knowledge base.
    
    Returns:
        List[Dict]: A list of all devices
    """
    kb_data = load_kb()
    return kb_data["devices"]

def get_device(device_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a device by its ID.
    
    Args:
        device_id: The ID of the device to retrieve
        
    Returns:
        Dict or None: The device data if found, None otherwise
    """
    kb_data = load_kb()
    
    for device in kb_data["devices"]:
        if device["id"] == device_id:
            return device
    
    return None

def update_device(
    device_id: str,
    name: Optional[str] = None,
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    os: Optional[str] = None,
    storage_type: Optional[str] = None,
    data_paths: Optional[List[str]] = None,
    communication_protocols: Optional[List[str]] = None,
    cloud_service: Optional[str] = None,
    notes: Optional[str] = None
) -> bool:
    """
    Updates a device in the knowledge base.
    
    Args:
        device_id: The ID of the device to update
        name: Device name
        manufacturer: Device manufacturer
        model: Device model
        os: Operating system
        storage_type: Type of storage
        data_paths: Common data paths
        communication_protocols: Communication protocols
        cloud_service: Associated cloud service
        notes: Additional notes
        
    Returns:
        bool: True if the device was updated, False otherwise
    """
    kb_data = load_kb()
    
    for i, device in enumerate(kb_data["devices"]):
        if device["id"] == device_id:
            # Update only the provided fields
            if name is not None:
                device["name"] = name
            if manufacturer is not None:
                device["manufacturer"] = manufacturer
            if model is not None:
                device["model"] = model
            if os is not None:
                device["os"] = os
            if storage_type is not None:
                device["storage_type"] = storage_type
            if data_paths is not None:
                device["data_paths"] = data_paths
            if communication_protocols is not None:
                device["communication_protocols"] = communication_protocols
            if cloud_service is not None:
                device["cloud_service"] = cloud_service
            if notes is not None:
                device["notes"] = notes
            
            # Update the device in the knowledge base
            kb_data["devices"][i] = device
            save_kb(kb_data)
            
            return True
    
    return False

def delete_device(device_id: str) -> bool:
    """
    Deletes a device from the knowledge base.
    
    Args:
        device_id: The ID of the device to delete
        
    Returns:
        bool: True if the device was deleted, False otherwise
    """
    kb_data = load_kb()
    
    for i, device in enumerate(kb_data["devices"]):
        if device["id"] == device_id:
            # Remove the device from the knowledge base
            kb_data["devices"].pop(i)
            save_kb(kb_data)
            
            return True
    
    return False