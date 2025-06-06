import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import cv2 # Added
import numpy as np # Added
from PIL import Image, ImageTk # Added
import src.video_acquisition as va # Added
import src.video_analysis as vanl # Added
# Existing src imports like knowledge_base, acquisition, analysis, reporting
# Make sure these are correctly imported as per existing structure. For example:
from src.knowledge_base import list_devices as kb_list_devices, get_device as kb_get_device, add_device, delete_device, update_device
import src.acquisition as acq
import src.analysis as anl
import src.reporting as rep

# Placeholder for actual forensic data store - This might be removed if not used by the final GUI structure
# forensic_data_store = {} # Commenting out as it seems unused in the provided final structure

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("IoT Forensic Tool")
        self.geometry("900x700") # Increased size slightly for new tab

        # Video analysis specific attributes
        self.webcam_stream = None
        self.video_processing_active = False
        self.motion_detector = None
        self.face_detector = None
        self.face_recognizer = None
        # Path for known faces. Assumes script is run from project root.
        self.known_faces_dir = "known_faces_for_gui_test"

        self.motion_detection_var = tk.BooleanVar()
        self.facial_detection_var = tk.BooleanVar()
        self.facial_recognition_var = tk.BooleanVar()

        main_frame = tk.Frame(self) # Main frame
        main_frame.pack(fill=tk.BOTH, expand=True)

        sidebar_frame = tk.Frame(main_frame, width=180, bg='#ECECEC') # Sidebar
        sidebar_frame.pack(fill=tk.Y, side=tk.LEFT, padx=10, pady=10)

        style = ttk.Style()
        style.configure("Sidebar.TButton", relief=tk.FLAT, padding=(10, 5))

        tab_names = ["Knowledge Base", "Data Acquisition", "Data Analysis", "Reporting", "Real-time Video Analysis"]
        for i, name in enumerate(tab_names):
            btn = ttk.Button(sidebar_frame, text=name, command=lambda idx=i: self.notebook.select(idx), style="Sidebar.TButton")
            btn.pack(pady=5, padx=5, fill=tk.X)

        content_frame = tk.Frame(main_frame) # Content frame
        content_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
        self.notebook = ttk.Notebook(content_frame)

        self.kb_frame = ttk.Frame(self.notebook)
        self.da_frame = ttk.Frame(self.notebook)
        self.analysis_frame = ttk.Frame(self.notebook)
        self.reporting_frame = ttk.Frame(self.notebook)
        self.video_analysis_frame = ttk.Frame(self.notebook) # New frame for video analysis

        self.setup_kb_tab(self.kb_frame)
        self.setup_acquisition_tab(self.da_frame)
        self.setup_analysis_tab(self.analysis_frame)
        self.setup_reporting_tab(self.reporting_frame)
        self.setup_video_analysis_tab(self.video_analysis_frame) # Setup new tab

        self.notebook.add(self.kb_frame, text="Knowledge Base")
        self.notebook.add(self.da_frame, text="Data Acquisition")
        self.notebook.add(self.analysis_frame, text="Data Analysis")
        self.notebook.add(self.reporting_frame, text="Reporting")
        self.notebook.add(self.video_analysis_frame, text="Real-time Video Analysis") # Add new tab

        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Methods for Knowledge Base Tab (Copied from current file content for completeness)
    def setup_kb_tab(self, tab_frame):
        main_kb_frame = ttk.Frame(tab_frame)
        main_kb_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        button_frame = ttk.Frame(main_kb_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Refresh List", command=self.refresh_kb_device_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add Device", command=self.open_add_device_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="View Details", command=lambda: print("View Details clicked (placeholder)")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update Device", command=self.open_update_device_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Device", command=self.delete_selected_device).pack(side=tk.LEFT, padx=5)
        content_frame = ttk.Frame(main_kb_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        content_frame.columnconfigure(1, weight=3)
        content_frame.rowconfigure(0, weight=1)
        listbox_frame = ttk.Frame(content_frame)
        listbox_frame.grid(row=0, column=0, sticky="nswe", padx=(0,5))
        self.kb_device_listbox = tk.Listbox(listbox_frame, exportselection=False)
        self.kb_device_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        kb_list_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.kb_device_listbox.yview)
        kb_list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.kb_device_listbox.config(yscrollcommand=kb_list_scrollbar.set)
        self.kb_device_listbox.bind("<<ListboxSelect>>", self.on_kb_device_select)
        details_frame = ttk.Frame(content_frame)
        details_frame.grid(row=0, column=1, sticky="nswe")
        self.kb_device_details_text = tk.Text(details_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.kb_device_details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        kb_details_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.kb_device_details_text.yview)
        kb_details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.kb_device_details_text.config(yscrollcommand=kb_details_scrollbar.set)
        self.refresh_kb_device_list()

    def refresh_kb_device_list(self):
        self.kb_device_listbox.delete(0, tk.END)
        devices = kb_list_devices()
        if not devices:
            self.kb_device_listbox.insert(tk.END, "No devices found in Knowledge Base.")
            self.update_kb_device_details_display(None)
            return
        for device in devices:
            self.kb_device_listbox.insert(tk.END, f"{device.get('name', 'Unknown Name')} (ID: {device.get('id', 'Unknown ID')})")

    def on_kb_device_select(self, event=None):
        selection = self.kb_device_listbox.curselection()
        if not selection:
            self.update_kb_device_details_display(None)
            return
        selected_index = selection[0]
        selected_item_text = self.kb_device_listbox.get(selected_index)
        try:
            id_part = selected_item_text.rfind("(ID: ")
            if id_part == -1: raise ValueError("ID tag not found in list item")
            device_id = selected_item_text[id_part + len("(ID: "):-1]
        except Exception as e:
            print(f"Error parsing device ID: {e}")
            self.update_kb_device_details_display({"error": f"Could not parse device ID from '{selected_item_text}'."})
            return
        device_info = kb_get_device(device_id)
        self.update_kb_device_details_display(device_info)

    def update_kb_device_details_display(self, device_data):
        self.kb_device_details_text.config(state=tk.NORMAL)
        self.kb_device_details_text.delete(1.0, tk.END)
        if device_data is None:
            self.kb_device_details_text.insert(tk.END, "No device selected or device not found.")
        elif isinstance(device_data, dict):
            if "error" in device_data:
                self.kb_device_details_text.insert(tk.END, f"Error: {device_data['error']}")
            else:
                for key, value in device_data.items():
                    display_key = key.replace('_', ' ').title()
                    if isinstance(value, list): display_value = ", ".join(map(str, value))
                    else: display_value = str(value)
                    self.kb_device_details_text.insert(tk.END, f"{display_key}: {display_value}\n")
        else:
            self.kb_device_details_text.insert(tk.END, str(device_data))
        self.kb_device_details_text.config(state=tk.DISABLED)

    def open_add_device_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New IoT Device")
        dialog.geometry("500x450")
        dialog.grab_set()
        fields = [("Name", True), ("Manufacturer", True), ("Model", True), ("OS", True), ("Storage Type", True), ("Data Paths (comma-sep)", True), ("Protocols (comma-sep)", True), ("Cloud Service", True), ("Notes", False)]
        entries = {}
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        for i, (label_text, is_required) in enumerate(fields):
            ttk.Label(form_frame, text=f"{label_text}{'*' if is_required else ''}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=5)
            entries[label_text.split(" (")[0].lower().replace(" ", "_")] = entry
        form_frame.columnconfigure(1, weight=1)
        button_frame = ttk.Frame(dialog, padding=(0, 10, 0, 10))
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(button_frame, text="Save", command=lambda: self.save_new_device(dialog, entries)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        dialog.transient(self)
        dialog.wait_window()

    def save_new_device(self, dialog, entries):
        device_data = {}
        required_fields_def = ["Name", "Manufacturer", "Model", "OS", "Storage Type", "Data Paths (comma-sep)", "Protocols (comma-sep)", "Cloud Service"]
        for key, entry_widget in entries.items(): device_data[key] = entry_widget.get().strip()
        for field_label in required_fields_def:
            field_key = field_label.split(" (")[0].lower().replace(" ", "_")
            if not device_data.get(field_key):
                messagebox.showerror("Validation Error", f"'{field_label}' is required.", parent=dialog)
                return
        try:
            device_data["data_paths"] = [p.strip() for p in device_data["data_paths"].split(',') if p.strip()]
            device_data["communication_protocols"] = [p.strip() for p in device_data["protocols"].split(',') if p.strip()]
            if not device_data["data_paths"]:
                 messagebox.showerror("Validation Error", "At least one Data Path is required.", parent=dialog)
                 return
            if not device_data["communication_protocols"]:
                 messagebox.showerror("Validation Error", "At least one Protocol is required.", parent=dialog)
                 return
        except Exception as e:
            messagebox.showerror("Input Error", f"Error parsing comma-separated fields: {e}", parent=dialog)
            return
        final_device_data = {"name": device_data["name"], "manufacturer": device_data["manufacturer"], "model": device_data["model"], "os": device_data["os"], "storage_type": device_data["storage_type"], "data_paths": device_data["data_paths"], "communication_protocols": device_data["communication_protocols"], "cloud_service": device_data["cloud_service"], "notes": device_data.get("notes", "")}
        try:
            new_device_id = add_device(**final_device_data)
            if new_device_id:
                messagebox.showinfo("Success", f"Device '{final_device_data['name']}' added successfully with ID: {new_device_id}", parent=dialog)
                self.refresh_kb_device_list()
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add device. Unknown error.", parent=dialog)
        except Exception as e:
            messagebox.showerror("Storage Error", f"Failed to add device: {e}", parent=dialog)

    def delete_selected_device(self):
        selection = self.kb_device_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a device to delete.", parent=self)
            return
        selected_index = selection[0]
        selected_item_text = self.kb_device_listbox.get(selected_index)
        try:
            id_part = selected_item_text.rfind("(ID: ")
            if id_part == -1: raise ValueError("ID tag not found in list item")
            device_id = selected_item_text[id_part + len("(ID: "):-1]
        except Exception as e:
            messagebox.showerror("Error", f"Could not parse device ID: {e}", parent=self)
            return
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete device '{selected_item_text.split(' (ID:')[0]}' (ID: {device_id})?", parent=self)
        if confirm:
            try:
                if delete_device(device_id):
                    messagebox.showinfo("Success", f"Device '{selected_item_text.split(' (ID:')[0]}' (ID: {device_id}) deleted successfully.", parent=self)
                    self.refresh_kb_device_list()
                    self.update_kb_device_details_display(None)
                else:
                    messagebox.showerror("Error", f"Failed to delete device ID: {device_id}. Device not found or error during deletion.", parent=self)
            except Exception as e:
                messagebox.showerror("Deletion Error", f"An error occurred while deleting device ID: {device_id}.\n{e}", parent=self)

    def open_update_device_dialog(self):
        selection = self.kb_device_listbox.curselection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select a device to update.", parent=self)
            return
        selected_index = selection[0]
        selected_item_text = self.kb_device_listbox.get(selected_index)
        try:
            id_part = selected_item_text.rfind("(ID: ")
            if id_part == -1: raise ValueError("ID tag not found")
            device_id = selected_item_text[id_part + len("(ID: "):-1]
        except Exception as e:
            messagebox.showerror("Error", f"Could not parse device ID for update: {e}", parent=self)
            return
        device_details = kb_get_device(device_id)
        if not device_details:
            messagebox.showerror("Error", f"Could not retrieve details for device ID: {device_id}.", parent=self)
            return
        dialog = tk.Toplevel(self)
        dialog.title(f"Update Device - ID: {device_id}")
        dialog.geometry("500x450")
        dialog.grab_set()
        fields_config = [("name", "Name", False), ("manufacturer", "Manufacturer", False), ("model", "Model", False), ("os", "OS", False), ("storage_type", "Storage Type", False), ("data_paths", "Data Paths (comma-sep)", True), ("communication_protocols", "Protocols (comma-sep)", True), ("cloud_service", "Cloud Service", False), ("notes", "Notes", False)]
        entries = {}
        form_frame = ttk.Frame(dialog, padding="10")
        form_frame.pack(fill=tk.BOTH, expand=True)
        for i, (key, label_text, is_list) in enumerate(fields_config):
            ttk.Label(form_frame, text=f"{label_text}:").grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, sticky=tk.EW, pady=2, padx=5)
            current_value = device_details.get(key, "")
            if is_list: entry.insert(0, ", ".join(current_value) if isinstance(current_value, list) else "")
            else: entry.insert(0, current_value if current_value is not None else "")
            entries[key] = entry
        form_frame.columnconfigure(1, weight=1)
        button_frame = ttk.Frame(dialog, padding=(0, 10, 0, 10))
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(button_frame, text="Save Changes", command=lambda: self.save_updated_device(dialog, device_id, entries, device_details)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
        dialog.transient(self)
        dialog.wait_window()

    def save_updated_device(self, dialog, device_id, entries, original_details):
        updated_data = {}
        changed_fields = False
        field_keys = ["name", "manufacturer", "model", "os", "storage_type", "data_paths", "communication_protocols", "cloud_service", "notes"]
        for key in field_keys:
            entry_value = entries[key].get().strip()
            original_value = original_details.get(key)
            if key in ["data_paths", "communication_protocols"]:
                parsed_list = [p.strip() for p in entry_value.split(',') if p.strip()] if entry_value else []
                if set(parsed_list) != set(original_value if original_value is not None else []):
                    updated_data[key] = parsed_list
                    changed_fields = True
                elif not parsed_list and original_value:
                     updated_data[key] = []
                     changed_fields = True
                elif parsed_list and not original_value:
                    updated_data[key] = parsed_list
                    changed_fields = True
                else:
                    updated_data[key] = None
            else:
                if entry_value != (original_value if original_value is not None else ""):
                    updated_data[key] = entry_value
                    changed_fields = True
                else:
                    updated_data[key] = None
        if updated_data.get("name") == "":
             messagebox.showerror("Validation Error", "'Name' cannot be empty.", parent=dialog)
             return
        if not changed_fields:
            messagebox.showinfo("No Changes", "No changes were made to the device details.", parent=dialog)
            dialog.destroy()
            return
        final_update_payload = {k: v for k, v in updated_data.items() if v is not None or k in ["data_paths", "communication_protocols"]}
        if not final_update_payload:
            messagebox.showinfo("No Changes", "No effective changes were made to save.", parent=dialog)
            dialog.destroy()
            return
        try:
            if update_device(device_id=device_id, **final_update_payload):
                messagebox.showinfo("Success", f"Device ID: {device_id} updated successfully.", parent=dialog)
                self.refresh_kb_device_list()
                current_selection_indices = self.kb_device_listbox.curselection()
                if current_selection_indices:
                    current_selected_item_text = self.kb_device_listbox.get(current_selection_indices[0])
                    if f"(ID: {device_id})" in current_selected_item_text:
                        self.on_kb_device_select(None)
                dialog.destroy()
            else:
                messagebox.showerror("Error", f"Failed to update device ID: {device_id}.", parent=dialog)
        except Exception as e:
            messagebox.showerror("Update Error", f"An error occurred while updating device ID: {device_id}.\n{e}", parent=dialog)

    # Methods for Data Acquisition Tab (Copied from current file content for completeness)
    def setup_acquisition_tab(self, tab_frame):
        main_acq_frame = ttk.Frame(tab_frame, padding="10")
        main_acq_frame.pack(fill=tk.BOTH, expand=True)
        main_acq_frame.columnconfigure(0, weight=1)
        main_acq_frame.columnconfigure(1, weight=1)
        left_column_frame = ttk.Frame(main_acq_frame)
        left_column_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 10))
        left_column_frame.rowconfigure(1, weight=1)
        list_acq_frame = ttk.LabelFrame(left_column_frame, text="Past Acquisitions", padding="10")
        list_acq_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        list_acq_frame.columnconfigure(0, weight=1)
        list_acq_frame.rowconfigure(1, weight=1)
        ttk.Button(list_acq_frame, text="Refresh Acquisitions List", command=self.refresh_acquisitions_list).grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.EW)
        acq_list_frame = ttk.Frame(list_acq_frame)
        acq_list_frame.grid(row=1, column=0, columnspan=2, sticky="nswe")
        acq_list_frame.rowconfigure(0, weight=1)
        acq_list_frame.columnconfigure(0, weight=1)
        self.acq_listbox = tk.Listbox(acq_list_frame, exportselection=False)
        self.acq_listbox.grid(row=0, column=0, sticky="nswe")
        acq_scrollbar = ttk.Scrollbar(acq_list_frame, orient=tk.VERTICAL, command=self.acq_listbox.yview)
        acq_scrollbar.grid(row=0, column=1, sticky="ns")
        self.acq_listbox.config(yscrollcommand=acq_scrollbar.set)
        self.acq_listbox.bind("<<ListboxSelect>>", self.on_acq_listbox_select)
        self._past_acquisitions_data = []
        sim_acq_frame = ttk.LabelFrame(left_column_frame, text="Simulate Data Acquisition", padding="10")
        sim_acq_frame.pack(fill=tk.X, pady=10)
        sim_acq_frame.columnconfigure(1, weight=1)
        ttk.Label(sim_acq_frame, text="Device ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.acq_sim_device_id_combo = ttk.Combobox(sim_acq_frame, state="readonly")
        self.acq_sim_device_id_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Label(sim_acq_frame, text="Source Type:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.acq_sim_source_type_combo = ttk.Combobox(sim_acq_frame, values=["log", "config", "memory_dump", "firmware"], state="readonly")
        self.acq_sim_source_type_combo.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        self.acq_sim_source_type_combo.set("log")
        ttk.Label(sim_acq_frame, text="Output File (optional):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.acq_sim_output_file_entry = ttk.Entry(sim_acq_frame)
        self.acq_sim_output_file_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(sim_acq_frame, text="Simulate Acquisition", command=self.run_simulate_acquisition).grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.EW)
        right_column_frame = ttk.Frame(main_acq_frame)
        right_column_frame.grid(row=0, column=1, sticky="nswe")
        right_column_frame.rowconfigure(0, weight=1)
        acq_details_frame = ttk.LabelFrame(right_column_frame, text="Acquisition Details", padding="10")
        acq_details_frame.pack(fill=tk.BOTH, expand=True, pady=(0,10))
        acq_details_frame.columnconfigure(0, weight=1)
        acq_details_frame.rowconfigure(0, weight=1)
        self.acq_details_text = tk.Text(acq_details_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.acq_details_text.grid(row=0, column=0, sticky="nswe")
        acq_details_scrollbar = ttk.Scrollbar(acq_details_frame, orient=tk.VERTICAL, command=self.acq_details_text.yview)
        acq_details_scrollbar.grid(row=0, column=1, sticky="ns")
        self.acq_details_text.config(yscrollcommand=acq_details_scrollbar.set)
        verify_frame = ttk.LabelFrame(right_column_frame, text="Verify File Integrity", padding="10")
        verify_frame.pack(fill=tk.X, pady=10)
        verify_frame.columnconfigure(1, weight=1)
        ttk.Label(verify_frame, text="File Path:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.acq_verify_file_path_entry = ttk.Entry(verify_frame)
        self.acq_verify_file_path_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(verify_frame, text="Browse...", command=self.browse_verify_file).grid(row=0, column=2, padx=5, pady=2)
        ttk.Label(verify_frame, text="Expected SHA256:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.acq_verify_hash_entry = ttk.Entry(verify_frame)
        self.acq_verify_hash_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(verify_frame, text="Verify File", command=self.run_verify_integrity).grid(row=2, column=0, columnspan=3, pady=10, sticky=tk.EW)
        self.refresh_acq_sim_device_combo()
        self.refresh_acquisitions_list()

    def refresh_acq_sim_device_combo(self):
        try:
            devices = kb_list_devices()
            device_ids = [f"{d.get('name', 'Unknown')} (ID: {d.get('id', 'Unknown')})" for d in devices]
            self.acq_sim_device_id_combo['values'] = device_ids
            if device_ids: self.acq_sim_device_id_combo.set(device_ids[0])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load device list for simulation: {e}", parent=self)
            self.acq_sim_device_id_combo['values'] = []

    def refresh_acquisitions_list(self):
        self.acq_listbox.delete(0, tk.END)
        self.update_acq_details_display(None)
        try:
            self._past_acquisitions_data = acq.list_acquisitions()
            if not self._past_acquisitions_data:
                self.acq_listbox.insert(tk.END, "No acquisitions found.")
                return
            for i, item in enumerate(self._past_acquisitions_data):
                display_text = f"{item.get('device_id', 'N/A')} ({item.get('source_type', 'N/A')}) - {item.get('timestamp','N/A')}"
                self.acq_listbox.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load acquisitions list: {e}", parent=self)
            self.acq_listbox.insert(tk.END, "Error loading acquisitions.")
            self._past_acquisitions_data = []

    def on_acq_listbox_select(self, event=None):
        selection = self.acq_listbox.curselection()
        if not selection:
            self.update_acq_details_display(None)
            return
        selected_index = selection[0]
        if 0 <= selected_index < len(self._past_acquisitions_data):
            acquisition_data = self._past_acquisitions_data[selected_index]
            self.update_acq_details_display(acquisition_data)
        else:
            self.update_acq_details_display({"error": "Selected index out of range or data mismatch."})

    def update_acq_details_display(self, data):
        self.acq_details_text.config(state=tk.NORMAL)
        self.acq_details_text.delete(1.0, tk.END)
        if data is None: self.acq_details_text.insert(tk.END, "Select an acquisition to see details.")
        elif isinstance(data, dict):
            if "error" in data: self.acq_details_text.insert(tk.END, f"Error: {data['error']}")
            else:
                for key, value in data.items():
                    display_key = key.replace('_', ' ').title()
                    self.acq_details_text.insert(tk.END, f"{display_key}: {value}\n")
        else: self.acq_details_text.insert(tk.END, str(data))
        self.acq_details_text.config(state=tk.DISABLED)

    def run_simulate_acquisition(self):
        device_combo_val = self.acq_sim_device_id_combo.get()
        source_type = self.acq_sim_source_type_combo.get()
        output_file = self.acq_sim_output_file_entry.get().strip() or None
        if not device_combo_val:
            messagebox.showerror("Error", "Please select a Device ID.", parent=self)
            return
        if not source_type:
            messagebox.showerror("Error", "Please select a Source Type.", parent=self)
            return
        try: device_id = device_combo_val.split("(ID: ")[1].replace(")", "")
        except IndexError:
            messagebox.showerror("Error", "Invalid Device ID format in combobox.", parent=self)
            return
        try:
            output_path, sha256_hash, timestamp = acq.simulate_acquisition(device_id, source_type, output_file)
            messagebox.showinfo("Success", f"Acquisition simulated successfully for {device_id}.\nType: {source_type}\nOutput: {output_path}\nSHA256: {sha256_hash}", parent=self)
            self.refresh_acquisitions_list()
            self.acq_sim_output_file_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Simulation Error", f"Failed to simulate acquisition: {e}", parent=self)

    def browse_verify_file(self):
        filepath = filedialog.askopenfilename(title="Select File to Verify", parent=self)
        if filepath:
            self.acq_verify_file_path_entry.delete(0, tk.END)
            self.acq_verify_file_path_entry.insert(0, filepath)
            if os.path.exists(filepath + ".meta"):
                try:
                    with open(filepath + ".meta", 'r') as f: meta = json.load(f)
                    if "sha256_hash" in meta:
                        self.acq_verify_hash_entry.delete(0, tk.END)
                        self.acq_verify_hash_entry.insert(0, meta["sha256_hash"])
                except Exception as e: print(f"Error reading meta file for auto-hash: {e}")

    def run_verify_integrity(self):
        file_path = self.acq_verify_file_path_entry.get().strip()
        expected_hash = self.acq_verify_hash_entry.get().strip()
        if not file_path:
            messagebox.showerror("Error", "Please provide a File Path.", parent=self)
            return
        if not expected_hash:
            messagebox.showerror("Error", "Please provide the Expected SHA256 Hash.", parent=self)
            return
        try:
            is_valid = acq.verify_file_integrity(file_path, expected_hash)
            if is_valid: messagebox.showinfo("Verification Success", f"File integrity verified for:\n{file_path}\nSHA256 hash matches.", parent=self)
            else: messagebox.showwarning("Verification Failed", f"File integrity verification failed for:\n{file_path}\nSHA256 hash does NOT match or file not found.", parent=self)
        except Exception as e:
            messagebox.showerror("Verification Error", f"An error occurred during verification: {e}", parent=self)

    # Methods for Data Analysis Tab (Copied from current file content for completeness)
    def setup_analysis_tab(self, tab_frame):
        main_analysis_frame = ttk.Frame(tab_frame, padding="10")
        main_analysis_frame.pack(fill=tk.BOTH, expand=True)
        main_analysis_frame.columnconfigure(0, weight=1)
        main_analysis_frame.columnconfigure(1, weight=1)
        log_frame = ttk.LabelFrame(main_analysis_frame, text="Log File Analysis", padding="10")
        log_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 5), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(2, weight=1)
        log_file_input_frame = ttk.Frame(log_frame)
        log_file_input_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0,5))
        log_file_input_frame.columnconfigure(1, weight=1)
        ttk.Label(log_file_input_frame, text="Log File Path:").grid(row=0, column=0, sticky=tk.W, padx=(0,5))
        self.log_analysis_file_entry = ttk.Entry(log_file_input_frame)
        self.log_analysis_file_entry.grid(row=0, column=1, sticky=tk.EW)
        self.browse_log_file_button = ttk.Button(log_file_input_frame, text="Browse...", command=self.browse_log_file)
        self.browse_log_file_button.grid(row=0, column=2, sticky=tk.E, padx=(5,0))
        self.analyze_log_button = ttk.Button(log_frame, text="Analyze Log File", command=self.analyze_log_file_gui)
        self.analyze_log_button.grid(row=1, column=0, sticky=tk.EW, pady=5)
        log_results_frame = ttk.Frame(log_frame)
        log_results_frame.grid(row=2, column=0, sticky="nswe")
        log_results_frame.columnconfigure(0, weight=1)
        log_results_frame.rowconfigure(0, weight=1)
        self.log_analysis_results_text = tk.Text(log_results_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.log_analysis_results_text.grid(row=0, column=0, sticky="nswe")
        log_results_scrollbar = ttk.Scrollbar(log_results_frame, orient=tk.VERTICAL, command=self.log_analysis_results_text.yview)
        log_results_scrollbar.grid(row=0, column=1, sticky="ns")
        self.log_analysis_results_text.config(yscrollcommand=log_results_scrollbar.set)
        config_frame = ttk.LabelFrame(main_analysis_frame, text="Configuration File Analysis", padding="10")
        config_frame.grid(row=0, column=1, sticky="nswe", padx=(5, 0), pady=5)
        config_frame.columnconfigure(0, weight=1)
        config_frame.rowconfigure(2, weight=1)
        config_file_input_frame = ttk.Frame(config_frame)
        config_file_input_frame.grid(row=0, column=0, sticky=tk.EW, pady=(0,5))
        config_file_input_frame.columnconfigure(1, weight=1)
        ttk.Label(config_file_input_frame, text="Config File Path:").grid(row=0, column=0, sticky=tk.W, padx=(0,5))
        self.config_analysis_file_entry = ttk.Entry(config_file_input_frame)
        self.config_analysis_file_entry.grid(row=0, column=1, sticky=tk.EW)
        self.browse_config_file_button = ttk.Button(config_file_input_frame, text="Browse...", command=self.browse_config_file)
        self.browse_config_file_button.grid(row=0, column=2, sticky=tk.E, padx=(5,0))
        self.analyze_config_button = ttk.Button(config_frame, text="Analyze Config File", command=self.analyze_config_file_gui)
        self.analyze_config_button.grid(row=1, column=0, sticky=tk.EW, pady=5)
        config_results_frame = ttk.Frame(config_frame)
        config_results_frame.grid(row=2, column=0, sticky="nswe")
        config_results_frame.columnconfigure(0, weight=1)
        config_results_frame.rowconfigure(0, weight=1)
        self.config_analysis_results_text = tk.Text(config_results_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.config_analysis_results_text.grid(row=0, column=0, sticky="nswe")
        config_results_scrollbar = ttk.Scrollbar(config_results_frame, orient=tk.VERTICAL, command=self.config_analysis_results_text.yview)
        config_results_scrollbar.grid(row=0, column=1, sticky="ns")
        self.config_analysis_results_text.config(yscrollcommand=config_results_scrollbar.set)

    def _update_text_widget(self, text_widget, content):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)

    def browse_log_file(self):
        filepath = filedialog.askopenfilename(title="Select Log File", filetypes=(("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")), parent=self)
        if filepath:
            self.log_analysis_file_entry.delete(0, tk.END)
            self.log_analysis_file_entry.insert(0, filepath)
            self._update_text_widget(self.log_analysis_results_text, "")

    def analyze_log_file_gui(self):
        filepath = self.log_analysis_file_entry.get().strip()
        if not filepath:
            messagebox.showerror("Error", "Please provide a Log File Path.", parent=self)
            return
        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"Log file not found:\n{filepath}", parent=self)
            return
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: log_content = f.read()
            if not log_content.strip():
                self._update_text_widget(self.log_analysis_results_text, "Log file is empty.")
                return
            parsed_logs = anl.parse_log_file(log_content)
            if not parsed_logs:
                 self._update_text_widget(self.log_analysis_results_text, "No parsable log entries found or file format is unsupported by the current parser.")
                 return
            analysis_results = anl.analyze_log_events(parsed_logs)
            output = "--- Parsed Log Summary (First 5 entries) ---\n"
            for entry in parsed_logs[:5]: output += f"Timestamp: {entry.get('timestamp')}, Level: {entry.get('level')}, Message: {entry.get('message')[:100]}...\n"
            if len(parsed_logs) > 5: output += f"... and {len(parsed_logs) - 5} more entries.\n"
            output += "\n--- Analysis Results ---\n"
            output += json.dumps(analysis_results, indent=4)
            self._update_text_widget(self.log_analysis_results_text, output)
        except Exception as e:
            messagebox.showerror("Log Analysis Error", f"An error occurred: {e}", parent=self)
            self._update_text_widget(self.log_analysis_results_text, f"Error during analysis: {e}")

    def browse_config_file(self):
        filepath = filedialog.askopenfilename(title="Select Configuration File", filetypes=(("JSON files", "*.json"), ("Config files", "*.conf"), ("All files", "*.*")), parent=self)
        if filepath:
            self.config_analysis_file_entry.delete(0, tk.END)
            self.config_analysis_file_entry.insert(0, filepath)
            self._update_text_widget(self.config_analysis_results_text, "")

    def analyze_config_file_gui(self):
        filepath = self.config_analysis_file_entry.get().strip()
        if not filepath:
            messagebox.showerror("Error", "Please provide a Config File Path.", parent=self)
            return
        if not os.path.exists(filepath):
            messagebox.showerror("Error", f"Config file not found:\n{filepath}", parent=self)
            return
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f: config_content = f.read()
            if not config_content.strip():
                self._update_text_widget(self.config_analysis_results_text, "Configuration file is empty.")
                return
            parsed_config = anl.parse_config_file(config_content)
            if "error" in parsed_config:
                error_message = f"Failed to parse configuration file.\nError: {parsed_config['error']}"
                self._update_text_widget(self.config_analysis_results_text, error_message)
                return
            analysis_results = anl.analyze_config(parsed_config)
            output = json.dumps(analysis_results, indent=4)
            self._update_text_widget(self.config_analysis_results_text, output)
        except Exception as e:
            messagebox.showerror("Config Analysis Error", f"An error occurred: {e}", parent=self)
            self._update_text_widget(self.config_analysis_results_text, f"Error during analysis: {e}")

    # Methods for Reporting Tab (Copied from current file content for completeness)
    def setup_reporting_tab(self, tab_frame):
        main_report_frame = ttk.Frame(tab_frame, padding="10")
        main_report_frame.pack(fill=tk.BOTH, expand=True)
        main_report_frame.columnconfigure(0, weight=1)
        main_report_frame.columnconfigure(1, weight=1)
        gen_frame = ttk.LabelFrame(main_report_frame, text="Generate New Report", padding="10")
        gen_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 5), pady=5)
        gen_frame.columnconfigure(1, weight=1)
        row_idx = 0
        ttk.Label(gen_frame, text="Case Name:").grid(row=row_idx, column=0, sticky=tk.W, pady=2)
        self.report_case_name_entry = ttk.Entry(gen_frame)
        self.report_case_name_entry.grid(row=row_idx, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        row_idx += 1
        ttk.Label(gen_frame, text="Investigator Name:").grid(row=row_idx, column=0, sticky=tk.W, pady=2)
        self.report_investigator_name_entry = ttk.Entry(gen_frame)
        self.report_investigator_name_entry.grid(row=row_idx, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        row_idx += 1
        ttk.Label(gen_frame, text="Device ID:").grid(row=row_idx, column=0, sticky=tk.W, pady=2)
        self.report_device_id_combo = ttk.Combobox(gen_frame, state="readonly")
        self.report_device_id_combo.grid(row=row_idx, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        row_idx += 1
        ttk.Label(gen_frame, text="Acquisition IDs:").grid(row=row_idx, column=0, sticky=tk.W, pady=2)
        self.report_acq_ids_entry = ttk.Entry(gen_frame)
        self.report_acq_ids_entry.grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(gen_frame, text="Select...", command=self.open_select_acquisitions_dialog).grid(row=row_idx, column=2, sticky=tk.E, padx=(0,0))
        row_idx += 1
        ttk.Label(gen_frame, text="Analyzed Log File (opt.):").grid(row=row_idx, column=0, sticky=tk.W, pady=2)
        self.report_log_file_entry = ttk.Entry(gen_frame)
        self.report_log_file_entry.grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(gen_frame, text="Browse...", command=self.browse_report_log_file).grid(row=row_idx, column=2, sticky=tk.E, padx=(0,0))
        row_idx += 1
        ttk.Label(gen_frame, text="Analyzed Config File (opt.):").grid(row=row_idx, column=0, sticky=tk.W, pady=2)
        self.report_config_file_entry = ttk.Entry(gen_frame)
        self.report_config_file_entry.grid(row=row_idx, column=1, sticky=tk.EW, padx=5, pady=2)
        ttk.Button(gen_frame, text="Browse...", command=self.browse_report_config_file).grid(row=row_idx, column=2, sticky=tk.E, padx=(0,0))
        row_idx += 1
        ttk.Label(gen_frame, text="Notes:").grid(row=row_idx, column=0, sticky=tk.NW, pady=2)
        self.report_notes_text = tk.Text(gen_frame, height=5, wrap=tk.WORD)
        self.report_notes_text.grid(row=row_idx, column=1, columnspan=2, sticky="nswe", padx=5, pady=2)
        gen_frame.rowconfigure(row_idx, weight=1)
        row_idx += 1
        ttk.Button(gen_frame, text="Generate Report", command=self.generate_report_gui).grid(row=row_idx, column=0, columnspan=3, pady=10, sticky=tk.EW)
        view_frame = ttk.LabelFrame(main_report_frame, text="View Existing Reports", padding="10")
        view_frame.grid(row=0, column=1, sticky="nswe", padx=(5, 0), pady=5)
        view_frame.columnconfigure(0, weight=1)
        view_frame.rowconfigure(1, weight=1)
        view_frame.rowconfigure(2, weight=2)
        ttk.Button(view_frame, text="Refresh Reports List", command=self.refresh_reports_list).grid(row=0, column=0, pady=5, sticky=tk.EW)
        report_list_frame = ttk.Frame(view_frame)
        report_list_frame.grid(row=1, column=0, sticky="nswe", pady=(0,5))
        report_list_frame.columnconfigure(0, weight=1)
        report_list_frame.rowconfigure(0, weight=1)
        self.reports_listbox = tk.Listbox(report_list_frame, exportselection=False)
        self.reports_listbox.grid(row=0, column=0, sticky="nswe")
        reports_list_scrollbar = ttk.Scrollbar(report_list_frame, orient=tk.VERTICAL, command=self.reports_listbox.yview)
        reports_list_scrollbar.grid(row=0, column=1, sticky="ns")
        self.reports_listbox.config(yscrollcommand=reports_list_scrollbar.set)
        self.reports_listbox.bind("<<ListboxSelect>>", self.on_report_select)
        self._report_list_data = []
        report_details_frame = ttk.Frame(view_frame)
        report_details_frame.grid(row=2, column=0, sticky="nswe")
        report_details_frame.columnconfigure(0, weight=1)
        report_details_frame.rowconfigure(0, weight=1)
        self.report_details_text = tk.Text(report_details_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.report_details_text.grid(row=0, column=0, sticky="nswe")
        report_details_scrollbar = ttk.Scrollbar(report_details_frame, orient=tk.VERTICAL, command=self.report_details_text.yview)
        report_details_scrollbar.grid(row=0, column=1, sticky="ns")
        self.report_details_text.config(yscrollcommand=report_details_scrollbar.set)
        self.refresh_report_device_combo()
        self.refresh_reports_list()

    def refresh_report_device_combo(self):
        try:
            devices = kb_list_devices()
            device_display_list = [f"{d.get('name', 'Unknown')} (ID: {d.get('id', 'Unknown')})" for d in devices]
            self.report_device_id_combo['values'] = device_display_list
            if device_display_list: self.report_device_id_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load devices for report: {e}", parent=self)

    def browse_report_log_file(self):
        filepath = filedialog.askopenfilename(title="Select Analyzed Log File", filetypes=(("All files", "*.*"),), parent=self)
        if filepath:
            self.report_log_file_entry.delete(0, tk.END)
            self.report_log_file_entry.insert(0, filepath)

    def browse_report_config_file(self):
        filepath = filedialog.askopenfilename(title="Select Analyzed Config File", filetypes=(("All files", "*.*"),), parent=self)
        if filepath:
            self.report_config_file_entry.delete(0, tk.END)
            self.report_config_file_entry.insert(0, filepath)

    def open_select_acquisitions_dialog(self):
        selected_device_str = self.report_device_id_combo.get()
        device_id_filter = None
        if selected_device_str:
            try: device_id_filter = selected_device_str.split("(ID: ")[1].replace(")", "")
            except IndexError: pass
        dialog = tk.Toplevel(self)
        dialog.title("Select Acquisitions")
        dialog.geometry("400x300")
        dialog.grab_set()
        ttk.Label(dialog, text=f"Acquisitions (Filter by device: {device_id_filter or 'None'})").pack(pady=5)
        listbox_frame = ttk.Frame(dialog)
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        acq_listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, exportselection=False)
        acq_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        acq_scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=acq_listbox.yview)
        acq_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        acq_listbox.config(yscrollcommand=acq_scrollbar.set)
        all_acquisitions = acq.list_acquisitions()
        self._dialog_acq_data = []
        for item in all_acquisitions:
            acq_id = item.get('id', item.get('timestamp'))
            display_text = f"{item.get('device_id', 'N/A')} ({item.get('source_type', 'N/A')}) - {acq_id}"
            if device_id_filter and item.get('device_id') != device_id_filter: continue
            acq_listbox.insert(tk.END, display_text)
            self._dialog_acq_data.append((display_text, item.get('id', item.get('file_path'))))
        def on_ok():
            selected_indices = acq_listbox.curselection()
            selected_ids = [self._dialog_acq_data[i][1] for i in selected_indices]
            self.report_acq_ids_entry.delete(0, tk.END)
            self.report_acq_ids_entry.insert(0, ", ".join(selected_ids))
            dialog.destroy()
        ttk.Button(dialog, text="OK", command=on_ok).pack(pady=5)
        dialog.transient(self)
        dialog.wait_window()

    def generate_report_gui(self):
        case_name = self.report_case_name_entry.get().strip()
        investigator_name = self.report_investigator_name_entry.get().strip()
        device_combo_val = self.report_device_id_combo.get()
        acq_ids_str = self.report_acq_ids_entry.get().strip()
        log_file_path = self.report_log_file_entry.get().strip()
        config_file_path = self.report_config_file_entry.get().strip()
        notes = self.report_notes_text.get("1.0", tk.END).strip()
        if not case_name or not investigator_name or not device_combo_val:
            messagebox.showerror("Error", "Case Name, Investigator, and Device ID are required.", parent=self)
            return
        try: device_id = device_combo_val.split("(ID: ")[1].replace(")", "")
        except IndexError:
            messagebox.showerror("Error", "Invalid Device ID format.", parent=self)
            return
        device_info = kb_get_device(device_id)
        if not device_info:
            messagebox.showerror("Error", f"Could not retrieve details for Device ID: {device_id}", parent=self)
            return
        selected_acq_file_paths = [s.strip() for s in acq_ids_str.split(',') if s.strip()]
        acquisition_details_for_report = []
        all_acqs = acq.list_acquisitions()
        for fp_id in selected_acq_file_paths:
            found_acq = next((acq_item for acq_item in all_acqs if acq_item.get('file_path') == fp_id), None)
            if found_acq: acquisition_details_for_report.append(found_acq)
            else: print(f"Warning: Acquisition with ID/Path '{fp_id}' not found in full list.")
        analysis_data_for_report = {}
        if log_file_path and os.path.exists(log_file_path):
            try:
                with open(log_file_path, 'r', encoding='utf-8', errors='ignore') as f: log_content = f.read()
                parsed_logs = anl.parse_log_file(log_content)
                analysis_data_for_report["log_analysis"] = anl.analyze_log_events(parsed_logs)
            except Exception as e:
                messagebox.showwarning("Report Gen Warning", f"Could not process log file {log_file_path}: {e}", parent=self)
        if config_file_path and os.path.exists(config_file_path):
            try:
                with open(config_file_path, 'r', encoding='utf-8', errors='ignore') as f: config_content = f.read()
                parsed_config = anl.parse_config_file(config_content)
                if "error" not in parsed_config: analysis_data_for_report["config_analysis"] = anl.analyze_config(parsed_config)
                else: analysis_data_for_report["config_analysis"] = parsed_config
            except Exception as e:
                messagebox.showwarning("Report Gen Warning", f"Could not process config file {config_file_path}: {e}", parent=self)
        final_analysis_results = {}
        if "log_analysis" in analysis_data_for_report: final_analysis_results.update(analysis_data_for_report["log_analysis"])
        if "config_analysis" in analysis_data_for_report: final_analysis_results.update(analysis_data_for_report["config_analysis"])
        try:
            report_path = rep.generate_report(case_name=case_name, investigator=investigator_name, device_info=device_info, acquisition_details=acquisition_details_for_report, analysis_results=final_analysis_results, notes=notes)
            messagebox.showinfo("Success", f"Report generated successfully:\n{report_path}", parent=self)
            self.refresh_reports_list()
            self.report_case_name_entry.delete(0, tk.END)
            self.report_acq_ids_entry.delete(0, tk.END)
            self.report_log_file_entry.delete(0, tk.END)
            self.report_config_file_entry.delete(0, tk.END)
            self.report_notes_text.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Report Generation Error", f"Failed to generate report: {e}", parent=self)

    def refresh_reports_list(self):
        self.reports_listbox.delete(0, tk.END)
        self._update_text_widget(self.report_details_text, "Select a report to view details.")
        try:
            self._report_list_data = rep.list_reports()
            if not self._report_list_data:
                self.reports_listbox.insert(tk.END, "No reports found.")
                return
            for item in self._report_list_data:
                display_text = f"{item.get('case_name', 'N/A')} - {item.get('investigator', 'N/A')} ({item.get('timestamp', 'N/A')})"
                self.reports_listbox.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load reports list: {e}", parent=self)
            self._report_list_data = []

    def on_report_select(self, event=None):
        selection = self.reports_listbox.curselection()
        if not selection:
            self._update_text_widget(self.report_details_text, "Select a report to view details.")
            return
        selected_index = selection[0]
        if 0 <= selected_index < len(self._report_list_data):
            report_summary = self._report_list_data[selected_index]
            report_path = report_summary.get("path")
            if report_path:
                report_content = rep.get_report(report_path)
                if report_content and "error" not in report_content:
                    self._update_text_widget(self.report_details_text, json.dumps(report_content, indent=4))
                elif report_content and "error" in report_content:
                     self._update_text_widget(self.report_details_text, f"Error loading report:\n{report_content['error']}")
                else:
                    self._update_text_widget(self.report_details_text, f"Failed to load report content from: {report_path}")
            else:
                self._update_text_widget(self.report_details_text, "Error: Report path not found in summary data.")
        else:
            self._update_text_widget(self.report_details_text, "Error: Selection index out of bounds.")

    # --- Video Analysis Tab Methods ---
    def on_closing(self):
        if self.video_processing_active and self.webcam_stream:
            print("Attempting to stop webcam stream on closing...")
            self.webcam_stream.stop()
            self.video_processing_active = False
            print("Webcam stream stopped.")
        self.destroy()

    def setup_video_analysis_tab(self, tab_frame):
        tab_frame.columnconfigure(0, weight=1)
        tab_frame.rowconfigure(1, weight=1)

        controls_frame = ttk.Frame(tab_frame, padding="10")
        controls_frame.grid(row=0, column=0, sticky="ew")

        self.webcam_button = ttk.Button(controls_frame, text="Start Webcam", command=self.toggle_webcam)
        self.webcam_button.pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Checkbutton(controls_frame, text="Motion Detection", variable=self.motion_detection_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(controls_frame, text="Facial Detection", variable=self.facial_detection_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(controls_frame, text="Facial Recognition", variable=self.facial_recognition_var).pack(side=tk.LEFT, padx=5)

        self.video_label = ttk.Label(tab_frame, text="Webcam feed will appear here.", anchor=tk.CENTER, relief=tk.SUNKEN)
        self.video_label.grid(row=1, column=0, sticky="nswe", padx=10, pady=10)
        self.video_label.configure(background="black")

        self.analysis_status_label = ttk.Label(tab_frame, text="Status: Idle", anchor=tk.W)
        self.analysis_status_label.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

        try: # Create dummy known face for GUI testing if not present
            if not os.path.exists(self.known_faces_dir):
                os.makedirs(self.known_faces_dir, exist_ok=True)

            dummy_face_path = os.path.join(self.known_faces_dir, "person_test_gui.png")
            if not os.path.exists(dummy_face_path):
                dummy_known_face = np.zeros((100, 100, 3), dtype=np.uint8)
                dummy_known_face[:, :, 0] = 255
                cv2.imwrite(dummy_face_path, dummy_known_face)
                print(f"Created dummy known face: {dummy_face_path}")
        except Exception as e:
            print(f"Could not create dummy known face directory/file for GUI test: {e}")

    def toggle_webcam(self):
        if not self.video_processing_active:
            try:
                self.webcam_stream = va.WebcamVideoStream()
                self.webcam_stream.start()

                self.motion_detector = vanl.MotionDetector()
                self.face_detector = vanl.FaceDetector(model="hog") # Default to HOG for speed
                self.face_recognizer = vanl.FaceRecognizer()
                if os.path.exists(self.known_faces_dir):
                    self.face_recognizer.load_known_faces(self.known_faces_dir)
                    # Check if faces were actually loaded
                    if not self.face_recognizer.known_face_names:
                         self.analysis_status_label.config(text=f"Status: Known faces dir loaded, but no faces found/encoded in {self.known_faces_dir}")
                    else:
                         self.analysis_status_label.config(text=f"Status: Known faces loaded from {self.known_faces_dir}")
                else:
                    print(f"Known faces directory not found: {self.known_faces_dir}. Recognition may be limited.")
                    self.analysis_status_label.config(text=f"Status: Known faces dir not found at {self.known_faces_dir}")

                self.video_processing_active = True
                self.webcam_button.config(text="Stop Webcam")
                # Initial status after successful start, before first frame processing
                # self.analysis_status_label.config(text="Status: Webcam Active") # This might be overwritten quickly
                self.update_video_feed()
            except va.VideoCaptureError as e:
                messagebox.showerror("Webcam Error", f"Could not start webcam: {e}", parent=self)
                self.analysis_status_label.config(text=f"Status: Error - {e}")
                self.video_processing_active = False
            except Exception as e: # Catch other init errors (e.g., from vanl)
                messagebox.showerror("Initialization Error", f"Error initializing components: {e}", parent=self)
                self.analysis_status_label.config(text=f"Status: Error - {e}")
                self.video_processing_active = False
        else:
            self.video_processing_active = False # Signal to stop update_video_feed loop
            if self.webcam_stream:
                self.webcam_stream.stop()
            self.webcam_button.config(text="Start Webcam")
            # Clear the video label
            if hasattr(self.video_label, 'imgtk'): # Check if imgtk attribute exists
                self.video_label.config(image='') # Remove reference to PhotoImage
                self.video_label.imgtk = None # Explicitly remove our custom attribute
            self.analysis_status_label.config(text="Status: Idle. Webcam stopped.")

    def update_video_feed(self):
        if not self.video_processing_active or not self.webcam_stream or not self.webcam_stream.isOpened():
            self.video_processing_active = False # Ensure flag is set if stream died
            self.webcam_button.config(text="Start Webcam")
            self.analysis_status_label.config(text="Status: Webcam stopped or unavailable.")
            if hasattr(self.video_label, 'imgtk'):
                 self.video_label.config(image='')
                 self.video_label.imgtk = None
            return

        bgr_frame = self.webcam_stream.read()

        if bgr_frame is None: # End of stream or error
            self.analysis_status_label.config(text="Status: Failed to grab frame. Stopping.")
            self.video_processing_active = False # Stop processing
            self.webcam_button.config(text="Start Webcam")
            if hasattr(self.video_label, 'imgtk'):
                self.video_label.config(image='')
                self.video_label.imgtk = None
            return # Stop the update loop

        display_frame_rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        current_status_parts = ["Processing..."]

        if self.motion_detection_var.get() and self.motion_detector:
            motion_detected, areas, _ = self.motion_detector.detect_motion_background_subtraction(bgr_frame.copy()) # Use original BGR for MOG2
            if motion_detected:
                current_status_parts.append("Motion")
                for (x, y, w, h) in areas:
                    cv2.rectangle(display_frame_rgb, (x, y), (x+w, y+h), (0, 255, 0), 2) # Draw on RGB for display

        # Facial detection and recognition operate on RGB frames
        rgb_for_face_analysis = display_frame_rgb.copy() # Use a fresh copy for face analysis if needed, or use display_frame_rgb

        if self.facial_detection_var.get() and self.face_detector:
            face_locations = self.face_detector.detect_faces(rgb_for_face_analysis) # Pass RGB
            if face_locations:
                current_status_parts.append(f"Faces({len(face_locations)})")
                for (top, right, bottom, left) in face_locations:
                    cv2.rectangle(display_frame_rgb, (left, top), (right, bottom), (255, 0, 0), 2) # Draw on main display frame

                if self.facial_recognition_var.get() and self.face_recognizer and self.face_recognizer.known_face_names:
                    names = self.face_recognizer.recognize_faces(rgb_for_face_analysis, face_locations) # Pass RGB
                    recognized_names_display = [name for name in names if name != "Unknown"]
                    if recognized_names_display:
                        current_status_parts.append(f"Recog: {', '.join(recognized_names_display)}")
                    elif names:
                        current_status_parts.append("Unknown faces")

                    for i, name in enumerate(names): # Draw names on main display frame
                        (top, right, bottom, left) = face_locations[i]
                        cv2.putText(display_frame_rgb, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                elif self.facial_recognition_var.get() and (not self.face_recognizer or not self.face_recognizer.known_face_names):
                     current_status_parts.append("Recog (No Known Faces)")


        if len(current_status_parts) > 1:
            self.analysis_status_label.config(text="Status: " + " | ".join(current_status_parts[1:]))
        else:
             self.analysis_status_label.config(text="Status: " + current_status_parts[0])

        img = Image.fromarray(display_frame_rgb)

        label_width = self.video_label.winfo_width()
        label_height = self.video_label.winfo_height()
        if label_width > 1 and label_height > 1:
            img.thumbnail((label_width, label_height), Image.Resampling.LANCZOS)

        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

        if self.video_processing_active: # Check flag before scheduling next call
            self.after(30, self.update_video_feed) # Approx 33 FPS

    def run(self):
        # self.protocol("WM_DELETE_WINDOW", self.on_closing) # Already set in __init__
        self.mainloop()

if __name__ == "__main__":
    app = App()
    app.run()
