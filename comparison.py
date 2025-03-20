import csv
import json
import time
import os.path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

# Set appearance mode and default color theme
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

def compare_csv_files(file1_path, file2_path, key_columns, name_columns):
    """
    Compare two CSV files and identify differences.
    
    Args:
        file1_path: Path to the first CSV file
        file2_path: Path to the second CSV file
        key_columns: List of column indices to use as a composite key
        name_columns: List of column indices to use for displaying names
    
    Returns:
        Dictionary with differences categorized and headers
    """
    start_time = time.time()
    
    # Store data from both files
    data1 = {}
    data2 = {}
    
    # Read headers and data from first file
    with open(file1_path, 'r', newline='') as f1:
        reader = csv.reader(f1)
        headers = next(reader)
        
        for row in reader:
            # Create a composite key from the specified columns
            key = tuple(row[i] for i in key_columns)
            data1[key] = row
    
    # Read data from second file
    with open(file2_path, 'r', newline='') as f2:
        reader = csv.reader(f2)
        # Skip header row, assuming headers are the same
        next(reader)
        
        for row in reader:
            key = tuple(row[i] for i in key_columns)
            data2[key] = row
    
    # Find differences
    differences = {
        "only_in_file1": [],
        "only_in_file2": [],
        "modified": []
    }
    
    # Keys only in file 1
    for key in data1:
        if key not in data2:
            differences["only_in_file1"].append({
                "key": key,
                "row": data1[key]
            })
    
    # Keys only in file 2
    for key in data2:
        if key not in data1:
            differences["only_in_file2"].append({
                "key": key,
                "row": data2[key]
            })
    
    # Modified rows (same key, different values)
    for key in data1:
        if key in data2 and data1[key] != data2[key]:
            # Find which columns changed
            changes = []
            for i, (val1, val2) in enumerate(zip(data1[key], data2[key])):
                if val1 != val2:
                    changes.append({
                        "column": headers[i],
                        "old_value": val1,
                        "new_value": val2
                    })
            
            differences["modified"].append({
                "key": key,
                "row": data1[key],
                "row2": data2[key],  # Add the second row for CSV export
                "changes": changes
            })
    
    elapsed_time = time.time() - start_time
    print(f"Comparison completed in {elapsed_time:.4f} seconds")
    
    return differences, headers

class ScrollableTextFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # Create a text widget with scrollbar
        self.text = ctk.CTkTextbox(self, wrap="word", font=("Segoe UI", 12))
        self.text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def insert(self, text, tag=None):
        self.text.insert("end", text)
    
    def clear(self):
        self.text.delete("1.0", "end")

class CSVComparisonApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("CSV Comparison Tool")
        self.geometry("1100x800")
        self.minsize(900, 700)
        
        # File paths
        self.file1_path = ""
        self.file2_path = ""
        
        # Column selections - always use column 0 as key
        self.key_columns = [0]
        self.name_columns = []
        
        # Headers from CSV
        self.headers = []
        
        # Store the comparison results
        self.comparison_results = None
        
        # Store filtered results for export
        self.filtered_results = {
            "modified": [],
            "only_in_file1": [],
            "only_in_file2": []
        }
        
        # Create a main scrollable frame that will contain all UI elements
        self.main_scrollable_frame = ctk.CTkScrollableFrame(self)
        self.main_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Create the UI inside the scrollable frame
        self.create_widgets()
        
        # Status message
        self.status_message = "Ready"
    
    def create_widgets(self):
        # Top frame - App title and description
        self.top_frame = ctk.CTkFrame(self.main_scrollable_frame, corner_radius=10)
        self.top_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        self.top_frame.grid_columnconfigure(0, weight=1)
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.top_frame, 
            text="CSV Comparison Tool",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        # App description
        self.desc_label = ctk.CTkLabel(
            self.top_frame,
            text="Compare two CSV files and identify differences",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        )
        self.desc_label.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
        
        # Middle frame - File selection and column selection
        self.middle_frame = ctk.CTkFrame(self.main_scrollable_frame, corner_radius=10)
        self.middle_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        self.middle_frame.grid_columnconfigure(0, weight=1)
        
        # File selection section
        self.file_frame = ctk.CTkFrame(self.middle_frame, corner_radius=10)
        self.file_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        self.file_frame.grid_columnconfigure(1, weight=1)
        
        # Section title
        self.file_title = ctk.CTkLabel(
            self.file_frame,
            text="Step 1: Select CSV Files",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.file_title.grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")
        
        # File 1 selection
        self.file1_label = ctk.CTkLabel(self.file_frame, text="First CSV File:", font=("Segoe UI", 12))
        self.file1_label.grid(row=1, column=0, padx=15, pady=10, sticky="w")
        
        self.file1_entry = ctk.CTkEntry(self.file_frame, font=("Segoe UI", 12), height=32)
        self.file1_entry.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ew")
        
        self.file1_button = ctk.CTkButton(
            self.file_frame, 
            text="Browse...", 
            command=self.browse_file1,
            font=("Segoe UI", 12),
            height=32
        )
        self.file1_button.grid(row=1, column=2, padx=(0, 15), pady=10)
        
        # File 2 selection
        self.file2_label = ctk.CTkLabel(self.file_frame, text="Second CSV File:", font=("Segoe UI", 12))
        self.file2_label.grid(row=2, column=0, padx=15, pady=10, sticky="w")
        
        self.file2_entry = ctk.CTkEntry(self.file_frame, font=("Segoe UI", 12), height=32)
        self.file2_entry.grid(row=2, column=1, padx=(0, 10), pady=10, sticky="ew")
        
        self.file2_button = ctk.CTkButton(
            self.file_frame, 
            text="Browse...", 
            command=self.browse_file2,
            font=("Segoe UI", 12),
            height=32
        )
        self.file2_button.grid(row=2, column=2, padx=(0, 15), pady=10)
        
        # Column selection section
        self.column_frame = ctk.CTkFrame(self.middle_frame, corner_radius=10)
        self.column_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        self.column_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Section title
        self.column_title = ctk.CTkLabel(
            self.column_frame,
            text="Step 2: Select Display Columns",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.column_title.grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        
        # Available columns frame
        self.avail_frame = ctk.CTkFrame(self.column_frame)
        self.avail_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.avail_frame.grid_rowconfigure(1, weight=1)
        self.avail_frame.grid_columnconfigure(0, weight=1)
        
        self.avail_label = ctk.CTkLabel(
            self.avail_frame,
            text="Available Columns (click to add)",
            font=("Segoe UI", 12, "bold")
        )
        self.avail_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.available_listbox = ctk.CTkScrollableFrame(self.avail_frame)
        self.available_listbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.available_listbox.grid_columnconfigure(0, weight=1)
        
        # We'll populate this with buttons dynamically
        self.available_buttons = []
        
        # Selected columns frame
        self.selected_frame = ctk.CTkFrame(self.column_frame)
        self.selected_frame.grid(row=1, column=1, padx=15, pady=(0, 15), sticky="nsew")
        self.selected_frame.grid_rowconfigure(1, weight=1)
        self.selected_frame.grid_columnconfigure(0, weight=1)
        
        self.selected_label = ctk.CTkLabel(
            self.selected_frame,
            text="Display Columns (click to remove)",
            font=("Segoe UI", 12, "bold")
        )
        self.selected_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.selected_listbox = ctk.CTkScrollableFrame(self.selected_frame)
        self.selected_listbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.selected_listbox.grid_columnconfigure(0, weight=1)
        
        # We'll populate this with buttons dynamically
        self.selected_buttons = []
        
        # Results frame
        self.results_frame = ctk.CTkFrame(self.main_scrollable_frame, corner_radius=10)
        self.results_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        self.results_frame.grid_rowconfigure(1, weight=1)
        self.results_frame.grid_columnconfigure(0, weight=1)
        
        # Results title and filter frame
        self.results_title_frame = ctk.CTkFrame(self.results_frame, fg_color="transparent")
        self.results_title_frame.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        self.results_title_frame.grid_columnconfigure(1, weight=1)
        
        # Results title
        self.results_title = ctk.CTkLabel(
            self.results_title_frame,
            text="Step 3: View Results",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.results_title.grid(row=0, column=0, padx=(0, 15), pady=0, sticky="w")
        
        # Filter label
        self.filter_label = ctk.CTkLabel(
            self.results_title_frame,
            text="Filter:",
            font=("Segoe UI", 12)
        )
        self.filter_label.grid(row=0, column=1, padx=(15, 5), pady=0, sticky="e")
        
        # Filter entry
        self.filter_entry = ctk.CTkEntry(
            self.results_title_frame,
            font=("Segoe UI", 12),
            height=32,
            width=200
        )
        self.filter_entry.grid(row=0, column=2, padx=(0, 5), pady=0, sticky="e")
        # Bind the entry to update filter as user types
        self.filter_entry.bind("<KeyRelease>", self.apply_filter)
        
        # Exact checkbox
        self.exact_var = ctk.BooleanVar(value=False)
        self.exact_checkbox = ctk.CTkCheckBox(
            self.results_title_frame,
            text="Exact",
            variable=self.exact_var,
            command=self.apply_filter,
            font=("Segoe UI", 12),
            height=32
        )
        self.exact_checkbox.grid(row=0, column=3, padx=(5, 5), pady=0, sticky="e")
        
        # Output format label
        self.output_label = ctk.CTkLabel(
            self.results_title_frame,
            text="Output:",
            font=("Segoe UI", 12)
        )
        self.output_label.grid(row=0, column=4, padx=(5, 5), pady=0, sticky="e")
        
        # Output format dropdown
        self.output_format_var = ctk.StringVar(value="Text")
        self.output_format = ctk.CTkOptionMenu(
            self.results_title_frame,
            values=["Text", "CSV", "JSON"],
            variable=self.output_format_var,
            command=self.change_output_format,
            font=("Segoe UI", 12),
            height=32,
            width=100
        )
        self.output_format.grid(row=0, column=5, padx=(0, 5), pady=0, sticky="e")
        
        # Download button
        self.download_button = ctk.CTkButton(
            self.results_title_frame,
            text="Download",
            command=self.download_results,
            font=("Segoe UI", 12),
            height=32,
            width=100
        )
        self.download_button.grid(row=0, column=6, padx=(5, 0), pady=0, sticky="e")
        
        # Tabview for results
        self.results_tabs = ctk.CTkTabview(self.results_frame, corner_radius=10, height=300)
        self.results_tabs.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        # Create tabs
        self.modified_tab = self.results_tabs.add("Modified Rows")
        self.only_in_file1_tab = self.results_tabs.add("Only in First File")
        self.only_in_file2_tab = self.results_tabs.add("Only in Second File")
        
        # Configure tab grid
        for tab in [self.modified_tab, self.only_in_file1_tab, self.only_in_file2_tab]:
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)
        
        # Create text widgets for each tab
        self.modified_text = ctk.CTkTextbox(self.modified_tab, font=("Segoe UI", 12))
        self.modified_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.only_in_file1_text = ctk.CTkTextbox(self.only_in_file1_tab, font=("Segoe UI", 12))
        self.only_in_file1_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.only_in_file2_text = ctk.CTkTextbox(self.only_in_file2_tab, font=("Segoe UI", 12))
        self.only_in_file2_text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Status bar (outside the scrollable frame)
        self.status_bar = ctk.CTkLabel(
            self,
            text="Ready",
            font=("Segoe UI", 12),
            anchor="w",
            height=30
        )
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
    
    def browse_file1(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            self.file1_path = filename
            self.file1_entry.delete(0, "end")
            self.file1_entry.insert(0, filename)
            self.check_and_load_headers()
    
    def browse_file2(self):
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            self.file2_path = filename
            self.file2_entry.delete(0, "end")
            self.file2_entry.insert(0, filename)
            self.check_and_load_headers()
    
    def check_and_load_headers(self):
        """Check if both files are selected and load headers automatically"""
        if self.file1_path and os.path.isfile(self.file1_path) and \
           self.file2_path and os.path.isfile(self.file2_path):
            self.load_headers()
    
    def load_headers(self):
        file1 = self.file1_path
        if not file1 or not os.path.isfile(file1):
            messagebox.showerror("Error", "Please select a valid first CSV file")
            return
        
        try:
            with open(file1, 'r', newline='') as f:
                reader = csv.reader(f)
                self.headers = next(reader)
                
                # Clear existing buttons
                for button in self.available_buttons:
                    button.destroy()
                self.available_buttons = []
                
                for button in self.selected_buttons:
                    button.destroy()
                self.selected_buttons = []
                
                # Reset name columns
                self.name_columns = []
                
                # Populate available columns (including column 0)
                for i, header in enumerate(self.headers):
                    item_text = f"{i}: {header}"
                    
                    # Create a button for each column
                    btn = ctk.CTkButton(
                        self.available_listbox,
                        text=item_text,
                        command=lambda idx=i, txt=item_text: self.add_display_column(idx, txt),
                        font=("Segoe UI", 12),
                        anchor="w",
                        height=30,
                        fg_color=("#3B8ED0" if i % 2 == 0 else "#1F6AA5")  # Alternating colors
                    )
                    btn.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
                    self.available_buttons.append(btn)
                
                # Update status
                key_column_name = self.headers[0] if self.headers else "Unknown"
                self.status_bar.configure(text=f"Loaded {len(self.headers)} columns")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load headers: {str(e)}")
    
    def add_display_column(self, col_index, item_text):
        # Add to name columns if not already there
        if col_index not in self.name_columns:
            self.name_columns.append(col_index)
            
            # Create a button in the selected list
            btn = ctk.CTkButton(
                self.selected_listbox,
                text=item_text,
                command=lambda idx=col_index: self.remove_display_column(idx),
                font=("Segoe UI", 12),
                anchor="w",
                height=30,
                fg_color="#E74C3C"  # Red color for removal buttons
            )
            btn.grid(row=len(self.selected_buttons), column=0, padx=5, pady=2, sticky="ew")
            self.selected_buttons.append(btn)
            
            # Update status
            self.status_bar.configure(text=f"Added '{item_text.split(':', 1)[1].strip()}' as a display column")
            
            # Automatically run comparison when a display column is added
            self.compare_files()
    
    def remove_display_column(self, col_index):
        # Remove from name columns
        if col_index in self.name_columns:
            idx = self.name_columns.index(col_index)
            self.name_columns.remove(col_index)
            
            # Remove the button
            self.selected_buttons[idx].destroy()
            self.selected_buttons.pop(idx)
            
            # Reposition remaining buttons
            for i, btn in enumerate(self.selected_buttons):
                btn.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
            
            # Update status
            column_name = self.headers[col_index] if col_index < len(self.headers) else "Unknown"
            self.status_bar.configure(text=f"Removed '{column_name}' from display columns")
            
            # If there are still display columns, run comparison again
            if self.name_columns:
                self.compare_files()
            else:
                # Clear results if no display columns are selected
                self.clear_results()
    
    def clear_results(self):
        """Clear all result text widgets"""
        self.modified_text.delete("1.0", "end")
        self.only_in_file1_text.delete("1.0", "end")
        self.only_in_file2_text.delete("1.0", "end")
    
    def apply_filter(self, event=None):
        """Apply filter to the results as user types"""
        if not self.comparison_results:
            return
        
        filter_text = self.filter_entry.get().lower()
        exact_mode = self.exact_var.get()
        output_format = self.output_format_var.get()
        self.display_results(self.comparison_results, filter_text, exact_mode, output_format)


    
    def change_output_format(self, choice):
        """Handle output format change"""
        if not self.comparison_results:
            return
        
        filter_text = self.filter_entry.get().lower()
        exact_mode = self.exact_var.get()
        self.display_results(self.comparison_results, filter_text, exact_mode, choice)
    
    def compare_files(self):
        # Get file paths
        file1 = self.file1_path
        file2 = self.file2_path
        
        # Validate files
        if not file1 or not os.path.isfile(file1):
            return
        
        if not file2 or not os.path.isfile(file2):
            return
        
        # Validate name columns
        if not self.name_columns:
            return
        
        # Update status
        self.status_bar.configure(text="Comparing files...")
        self.update_idletasks()
        
        try:
            # Perform comparison
            self.comparison_results = compare_csv_files(file1, file2, self.key_columns, self.name_columns)
            
            # Display results with current filter
            filter_text = self.filter_entry.get().lower()
            exact_mode = self.exact_var.get()
            output_format = self.output_format_var.get()
            self.display_results(self.comparison_results, filter_text, exact_mode, output_format)
            
        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed: {str(e)}")
            self.status_bar.configure(text="Comparison failed")
    
    def display_results(self, comparison_data, filter_text="", exact_mode=False, output_format="Text"):
        """Display results with optional filtering and in the selected format"""
        differences, headers = comparison_data
        
        # Clear result text widgets
        self.clear_results()
        
        # Filter items
        filtered_modified = self.filter_items(differences['modified'], filter_text, exact_mode)
        filtered_file1 = self.filter_items(differences['only_in_file1'], filter_text, exact_mode)
        filtered_file2 = self.filter_items(differences['only_in_file2'], filter_text, exact_mode)
        
        # Store filtered results for export
        self.filtered_results = {
            "modified": filtered_modified,
            "only_in_file1": filtered_file1,
            "only_in_file2": filtered_file2,
            "headers": headers
        }
        
        # Display based on output format
        if output_format == "Text":
            self.display_text_format(filtered_modified, filtered_file1, filtered_file2, headers, filter_text, exact_mode)
        elif output_format == "CSV":
            self.display_csv_format(filtered_modified, filtered_file1, filtered_file2, headers)
        elif output_format == "JSON":
            self.display_json_format(filtered_modified, filtered_file1, filtered_file2, headers)
        
        # Update status
        modified_count = len(filtered_modified)
        only_in_file1_count = len(filtered_file1)
        only_in_file2_count = len(filtered_file2)
        
        status_text = f"Comparison complete. "
        if filter_text:
            status_text = f"Filtered by '{filter_text}'. "
            if exact_mode:
                status_text += "Exact mode enabled. "
                
        if modified_count > 0:
            status_text += f"Modified: {modified_count}, "
        if only_in_file1_count > 0:
            status_text += f"Only in first: {only_in_file1_count}, "
        if only_in_file2_count > 0:
            status_text += f"Only in second: {only_in_file2_count}"
        
        # Remove trailing comma if needed
        if status_text.endswith(", "):
            status_text = status_text[:-2]
            
        self.status_bar.configure(text=status_text)
        
        # Switch to the tab with the most differences
        max_diff = max([modified_count, only_in_file1_count, only_in_file2_count], default=0)

        if max_diff == modified_count and modified_count > 0:
            self.results_tabs.set("Modified Rows")
        elif max_diff == only_in_file1_count and only_in_file1_count > 0:
            self.results_tabs.set("Only in First File")
        elif only_in_file2_count > 0:
            self.results_tabs.set("Only in Second File")

    def display_csv_format(self, filtered_modified, filtered_file1, filtered_file2, headers):
        """Display results in CSV format in the text widgets"""
        # Clear previous content
        self.modified_text.delete("1.0", "end")
        self.only_in_file1_text.delete("1.0", "end")
        self.only_in_file2_text.delete("1.0", "end")
        
        # Display CSV format for modified rows
        self.modified_text.insert("1.0", f"Modified Rows: {len(filtered_modified)}\n\n")
        if filtered_modified:
            # Create header row
            header_row = "Item #,Name"
            for h in headers:
                header_row += f",{h} (Old),{h} (New)"
            self.modified_text.insert("end", header_row + "\n")
            
            # Create data rows
            for i, item in enumerate(filtered_modified):
                name_parts = [item["row"][col] for col in self.name_columns]
                name_display = " ".join(name_parts)
                
                row = f"{i+1},{name_display}"
                for j in range(len(headers)):
                    old_val = item["row"][j] if j < len(item["row"]) else ""
                    new_val = item["row2"][j] if j < len(item["row2"]) else ""
                    row += f",{old_val},{new_val}"
                
                self.modified_text.insert("end", row + "\n")
        
        # Display CSV format for rows only in file 1
        self.only_in_file1_text.insert("1.0", f"Rows only in first file: {len(filtered_file1)}\n\n")
        if filtered_file1:
            # Create header row
            header_row = "Item #,Name," + ",".join(headers)
            self.only_in_file1_text.insert("end", header_row + "\n")
            
            # Create data rows
            for i, item in enumerate(filtered_file1):
                name_parts = [item["row"][col] for col in self.name_columns]
                name_display = " ".join(name_parts)
                
                row = f"{i+1},{name_display}"
                for j in range(len(headers)):
                    val = item["row"][j] if j < len(item["row"]) else ""
                    row += f",{val}"
                
                self.only_in_file1_text.insert("end", row + "\n")
        
        # Display CSV format for rows only in file 2
        self.only_in_file2_text.insert("1.0", f"Rows only in second file: {len(filtered_file2)}\n\n")
        if filtered_file2:
            # Create header row
            header_row = "Item #,Name," + ",".join(headers)
            self.only_in_file2_text.insert("end", header_row + "\n")
            
            # Create data rows
            for i, item in enumerate(filtered_file2):
                name_parts = [item["row"][col] for col in self.name_columns]
                name_display = " ".join(name_parts)
                
                row = f"{i+1},{name_display}"
                for j in range(len(headers)):
                    val = item["row"][j] if j < len(item["row"]) else ""
                    row += f",{val}"
                
                self.only_in_file2_text.insert("end", row + "\n")

    def display_json_format(self, filtered_modified, filtered_file1, filtered_file2, headers):
        """Display results in JSON format in the text widgets"""
        # Clear previous content
        self.modified_text.delete("1.0", "end")
        self.only_in_file1_text.delete("1.0", "end")
        self.only_in_file2_text.delete("1.0", "end")
        
        # Display JSON format for modified rows
        modified_json = self.create_json_string(filtered_modified, "modified")
        self.modified_text.insert("1.0", f"Modified Rows: {len(filtered_modified)}\n\n")
        self.modified_text.insert("end", modified_json)
        
        # Display JSON format for rows only in file 1
        file1_json = self.create_json_string(filtered_file1, "only_in_file1")
        self.only_in_file1_text.insert("1.0", f"Rows only in first file: {len(filtered_file1)}\n\n")
        self.only_in_file1_text.insert("end", file1_json)
        
        # Display JSON format for rows only in file 2
        file2_json = self.create_json_string(filtered_file2, "only_in_file2")
        self.only_in_file2_text.insert("1.0", f"Rows only in second file: {len(filtered_file2)}\n\n")
        self.only_in_file2_text.insert("end", file2_json)

    
    def display_text_format(self, filtered_modified, filtered_file1, filtered_file2, headers, filter_text, exact_mode):
        """Display results in text format"""
        # Display modified rows
        self.modified_text.insert("1.0", f"Modified Rows: {len(filtered_modified)} (of {len(self.comparison_results[0]['modified'])})\n\n")
        filter_text_lower = filter_text.lower() if filter_text else ""
        
        for i, mod in enumerate(filtered_modified):
            # Get the name from the row data using name_columns
            name_parts = [mod["row"][col] for col in self.name_columns]
            name_display = " ".join(name_parts)
            
            self.modified_text.insert("end", f"{i+1}. {name_display}\n")
            
            if filter_text:
                if exact_mode:
                    # In exact mode, only show columns that contain the filter text
                    for change in mod["changes"]:
                        col_str = str(change["column"]).lower()
                        old_val_str = str(change["old_value"]).lower()
                        new_val_str = str(change["new_value"]).lower()
                        
                        # Check if any part of this change contains the filter text
                        if (filter_text_lower in col_str or 
                            filter_text_lower in old_val_str or 
                            filter_text_lower in new_val_str):
                            self.modified_text.insert("end", 
                                f"   Column '{change['column']}': '{change['old_value']}' → '{change['new_value']}'\n")
                else:
                    # When not in exact mode, show ALL columns that changed for matched rows
                    for change in mod["changes"]:
                        self.modified_text.insert("end", 
                            f"   Column '{change['column']}': '{change['old_value']}' → '{change['new_value']}'\n")
            else:
                # No filter means show all changes
                for change in mod["changes"]:
                    self.modified_text.insert("end", 
                        f"   Column '{change['column']}': '{change['old_value']}' → '{change['new_value']}'\n")
            
            self.modified_text.insert("end", "\n")
        
        # Display rows only in file 1
        self.only_in_file1_text.insert("1.0", f"Rows only in first file: {len(filtered_file1)} (of {len(self.comparison_results[0]['only_in_file1'])})\n\n")
        for i, item in enumerate(filtered_file1):
            name_parts = [item["row"][col] for col in self.name_columns]
            name_display = " ".join(name_parts)
            self.only_in_file1_text.insert("end", f"{i+1}. {name_display}\n")
            
            # If filter is active, decide which fields to show
            if filter_text:
                if exact_mode:
                    # In exact mode, only show fields that contain the filter text
                    for j, val in enumerate(item["row"]):
                        if j < len(headers):
                            val_str = str(val).lower()
                            if filter_text_lower in val_str:
                                self.only_in_file1_text.insert("end", f"   {headers[j]}: {val}\n")
                else:
                    # Not in exact mode, show all fields for matched rows
                    for j, val in enumerate(item["row"]):
                        if j < len(headers):
                            self.only_in_file1_text.insert("end", f"   {headers[j]}: {val}\n")
            else:
                # No filter means show all fields
                for j, val in enumerate(item["row"]):
                    if j < len(headers):
                        self.only_in_file1_text.insert("end", f"   {headers[j]}: {val}\n")
            
            self.only_in_file1_text.insert("end", "\n")
        
        # Display rows only in file 2
        self.only_in_file2_text.insert("1.0", f"Rows only in second file: {len(filtered_file2)} (of {len(self.comparison_results[0]['only_in_file2'])})\n\n")
        for i, item in enumerate(filtered_file2):
            name_parts = [item["row"][col] for col in self.name_columns]
            name_display = " ".join(name_parts)
            self.only_in_file2_text.insert("end", f"{i+1}. {name_display}\n")
            
            # If filter is active, decide which fields to show
            if filter_text:
                if exact_mode:
                    # In exact mode, only show fields that contain the filter text
                    for j, val in enumerate(item["row"]):
                        if j < len(headers):
                            val_str = str(val).lower()
                            if filter_text_lower in val_str:
                                self.only_in_file2_text.insert("end", f"   {headers[j]}: {val}\n")
                else:
                    # Not in exact mode, show all fields for matched rows
                    for j, val in enumerate(item["row"]):
                        if j < len(headers):
                            self.only_in_file2_text.insert("end", f"   {headers[j]}: {val}\n")
            else:
                # No filter means show all fields
                for j, val in enumerate(item["row"]):
                    if j < len(headers):
                        self.only_in_file2_text.insert("end", f"   {headers[j]}: {val}\n")
            
            self.only_in_file2_text.insert("end", "\n")

    
    def create_json_string(self, items, item_type):
        """Create a JSON string from the filtered items"""
        if not items:
            return f"No {item_type.replace('_', ' ')} rows found."
        
        # Create a list of dictionaries for JSON output
        json_data = []
        
        filter_text = self.filter_entry.get().lower()
        exact_mode = self.exact_var.get()
        
        for item in items:
            if item_type == "modified":
                # For modified items, include original row, changes, and name
                name_parts = [item["row"][col] for col in self.name_columns]
                name_display = " ".join(name_parts)
                
                # If exact mode and filter are active, only include matching fields
                if exact_mode and filter_text:
                    # Create filtered original and new rows
                    original_row = {}
                    new_row = {}
                    
                    # Only include fields that match the filter
                    for i, (val1, val2) in enumerate(zip(item["row"], item["row2"])):
                        if i < len(self.headers):
                            # Include field if it matches the filter exactly
                            if (filter_text == str(val1).lower().strip() or 
                                filter_text == str(val2).lower().strip() or
                                filter_text == str(self.headers[i]).lower().strip()):
                                original_row[self.headers[i]] = val1
                                new_row[self.headers[i]] = val2
                    
                    # Filter changes to only include exact matches
                    filtered_changes = []
                    for change in item["changes"]:
                        if (filter_text == str(change["column"]).lower().strip() or
                            filter_text == str(change["old_value"]).lower().strip() or
                            filter_text == str(change["new_value"]).lower().strip()):
                            filtered_changes.append({
                                "column": change["column"],
                                "old_value": change["old_value"],
                                "new_value": change["new_value"]
                            })
                    
                    json_item = {
                        "name": name_display,
                        "original_row": original_row,
                        "new_row": new_row,
                        "changes": filtered_changes
                    }
                else:
                    # Include all fields
                    json_item = {
                        "name": name_display,
                        "original_row": {self.headers[i]: val for i, val in enumerate(item["row"]) if i < len(self.headers)},
                        "new_row": {self.headers[i]: val for i, val in enumerate(item["row2"]) if i < len(self.headers)},
                        "changes": [
                            {
                                "column": change["column"],
                                "old_value": change["old_value"],
                                "new_value": change["new_value"]
                            }
                            for change in item["changes"]
                        ]
                    }
            else:
                # For items only in one file, include row data and name
                name_parts = [item["row"][col] for col in self.name_columns]
                name_display = " ".join(name_parts)
                
                # If exact mode and filter are active, only include matching fields
                if exact_mode and filter_text:
                    filtered_row = {}
                    for i, val in enumerate(item["row"]):
                        if i < len(self.headers) and filter_text == str(val).lower().strip():
                            filtered_row[self.headers[i]] = val
                    
                    json_item = {
                        "name": name_display,
                        "row": filtered_row
                    }
                else:
                    json_item = {
                        "name": name_display,
                        "row": {self.headers[i]: val for i, val in enumerate(item["row"]) if i < len(self.headers)}
                    }
                
            json_data.append(json_item)
        
        # Convert to pretty-printed JSON
        return json.dumps(json_data, indent=2)

    
    def download_results(self):
        """Download the current results in the selected format"""
        if not self.comparison_results:
            messagebox.showinfo("No Data", "No comparison results to download.")
            return
        
        # Get current tab and output format
        current_tab = self.results_tabs.get()
        output_format = self.output_format_var.get()
        
        # Determine which data to download
        if current_tab == "Modified Rows":
            data_type = "modified"
            items = self.filtered_results["modified"]
        elif current_tab == "Only in First File":
            data_type = "only_in_file1"
            items = self.filtered_results["only_in_file1"]
        else:  # "Only in Second File"
            data_type = "only_in_file2"
            items = self.filtered_results["only_in_file2"]
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"csv_comparison_{data_type}_{timestamp}"
        
        if output_format == "CSV":
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")],
                initialfile=f"{base_filename}.csv"
            )
            if filename:
                self.save_as_csv(filename, items, data_type)
        
        elif output_format == "JSON":
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")],
                initialfile=f"{base_filename}.json"
            )
            if filename:
                self.save_as_json(filename, items, data_type)
        
        else:  # Text format
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                initialfile=f"{base_filename}.txt"
            )
            if filename:
                self.save_as_text(filename, items, data_type)
    
    def save_as_csv(self, filename, items, data_type):
        """Save the filtered results as a CSV file"""
        try:
            headers = self.filtered_results["headers"]
            
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                if data_type == "modified":
                    # Write header row for modified items
                    modified_headers = ["Item #", "Name"]
                    for h in headers:
                        modified_headers.extend([f"{h} (Old)", f"{h} (New)"])
                    modified_headers.append("Changes")
                    writer.writerow(modified_headers)
                    
                    # Write data rows
                    for i, item in enumerate(items):
                        name_parts = [item["row"][col] for col in self.name_columns]
                        name_display = " ".join(name_parts)
                        
                        # Create a string of changes
                        changes_str = "; ".join([
                            f"{change['column']}: '{change['old_value']}' -> '{change['new_value']}'"
                            for change in item["changes"]
                        ])
                        
                        # Create interleaved row with old and new values side by side
                        row_data = [str(i+1), name_display]
                        for j in range(len(headers)):
                            if j < len(item["row"]):
                                row_data.append(item["row"][j])
                            else:
                                row_data.append("")
                                
                            if j < len(item["row2"]):
                                row_data.append(item["row2"][j])
                            else:
                                row_data.append("")
                        
                        row_data.append(changes_str)
                        writer.writerow(row_data)
                else:
                    # Write header row for items only in one file
                    writer.writerow(["Item #", "Name"] + headers)
                    
                    # Write data rows
                    for i, item in enumerate(items):
                        name_parts = [item["row"][col] for col in self.name_columns]
                        name_display = " ".join(name_parts)
                        writer.writerow([str(i+1), name_display] + item["row"])
            
            self.status_bar.configure(text=f"Results saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV file: {str(e)}")

    
    def save_as_json(self, filename, items, data_type):
        """Save the filtered results as a JSON file"""
        try:
            # Create a list of dictionaries for JSON output
            json_data = []
            headers = self.filtered_results["headers"]
            
            for item in items:
                if data_type == "modified":
                    # For modified items, include original row, changes, and name
                    name_parts = [item["row"][col] for col in self.name_columns]
                    name_display = " ".join(name_parts)
                    
                    # Create dictionaries for original and new rows
                    original_row = {}
                    new_row = {}
                    
                    for i in range(min(len(headers), len(item["row"]))):
                        original_row[headers[i]] = item["row"][i]
                    
                    for i in range(min(len(headers), len(item["row2"]))):
                        new_row[headers[i]] = item["row2"][i]
                    
                    json_item = {
                        "name": name_display,
                        "original_row": original_row,
                        "new_row": new_row,
                        "changes": [
                            {
                                "column": change["column"],
                                "old_value": change["old_value"],
                                "new_value": change["new_value"]
                            }
                            for change in item["changes"]
                        ]
                    }
                else:
                    # For items only in one file, include row data and name
                    name_parts = [item["row"][col] for col in self.name_columns]
                    name_display = " ".join(name_parts)
                    
                    # Create a dictionary for the row
                    row_data = {}
                    for i in range(min(len(headers), len(item["row"]))):
                        row_data[headers[i]] = item["row"][i]
                    
                    json_item = {
                        "name": name_display,
                        "row": row_data
                    }
                
                json_data.append(json_item)
            
            # Write to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            
            self.status_bar.configure(text=f"Results saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save JSON file: {str(e)}")

    
    def save_as_text(self, filename, items, data_type):
        """Save the filtered results as a text file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if data_type == "modified":
                    f.write(f"Modified Rows: {len(items)}\n\n")
                    for i, mod in enumerate(items):
                        # Get the name from the row data using name_columns
                        name_parts = [mod["row"][col] for col in self.name_columns]
                        name_display = " ".join(name_parts)
                        
                        f.write(f"{i+1}. {name_display}\n")
                        
                        # Show all changes
                        for change in mod["changes"]:
                            f.write(f"   Column '{change['column']}': '{change['old_value']}' -> '{change['new_value']}'\n")
                        
                        f.write("\n")
                
                elif data_type == "only_in_file1":
                    f.write(f"Rows only in first file: {len(items)}\n\n")
                    for i, item in enumerate(items):
                        name_parts = [item["row"][col] for col in self.name_columns]
                        name_display = " ".join(name_parts)
                        f.write(f"{i+1}. {name_display}\n")
                        
                        # Show all fields
                        for j, val in enumerate(item["row"]):
                            if j < len(self.headers):
                                f.write(f"   {self.headers[j]}: {val}\n")
                        
                        f.write("\n")
                
                else:  # only_in_file2
                    f.write(f"Rows only in second file: {len(items)}\n\n")
                    for i, item in enumerate(items):
                        name_parts = [item["row"][col] for col in self.name_columns]
                        name_display = " ".join(name_parts)
                        f.write(f"{i+1}. {name_display}\n")
                        
                        # Show all fields
                        for j, val in enumerate(item["row"]):
                            if j < len(self.headers):
                                f.write(f"   {self.headers[j]}: {val}\n")
                        
                        f.write("\n")
            
            self.status_bar.configure(text=f"Results saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save text file: {str(e)}")
    
    def filter_items(self, items, filter_text, exact_mode=False):
        """
        Filter items based on filter text
        
        exact_mode: When True, filters for exact matches of the substring (case-insensitive)
                    When False, allows for broader matching (e.g., partial word matches)
        """
        if not filter_text:
            return items
        
        filtered_items = []
        filter_text_lower = filter_text.lower()
        
        for item in items:
            # For modified items (with changes)
            if "changes" in item:
                # Check if any changes match the filter
                has_matching_changes = False
                for change in item["changes"]:
                    col_str = str(change["column"]).lower()
                    old_val_str = str(change["old_value"]).lower()
                    new_val_str = str(change["new_value"]).lower()
                    
                    if filter_text_lower in col_str or filter_text_lower in old_val_str or filter_text_lower in new_val_str:
                        has_matching_changes = True
                        break
                
                # Only include the item if at least one change matches the filter
                if has_matching_changes:
                    filtered_items.append(item)
            
            # For items only in one file
            else:
                item_match = False
                for val in item["row"]:
                    val_str = str(val).lower()
                    if filter_text_lower in val_str:
                        item_match = True
                        break
                
                if item_match:
                    filtered_items.append(item)
        
        return filtered_items


    def filter_changes(self, changes, filter_text, exact_mode=False):
        """
        Filter changes to only include those that match the filter text
        
        exact_mode: When True, requires the filter_text to match exactly as typed
                    (case-sensitive). When False, case-insensitive match.
        """
        if not filter_text:
            return changes
        
        filtered_changes = []
        
        for change in changes:
            col_str = str(change["column"])
            old_val_str = str(change["old_value"])
            new_val_str = str(change["new_value"])
            
            if exact_mode:
                # Case-sensitive substring match
                if (filter_text in col_str or 
                    filter_text in old_val_str or 
                    filter_text in new_val_str):
                    filtered_changes.append(change)
            else:
                # Case-insensitive substring match
                if (filter_text.lower() in col_str.lower() or 
                    filter_text.lower() in old_val_str.lower() or 
                    filter_text.lower() in new_val_str.lower()):
                    filtered_changes.append(change)
        
        return filtered_changes


if __name__ == "__main__":
    app = CSVComparisonApp()
    app.mainloop()
