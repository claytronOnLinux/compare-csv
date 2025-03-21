import csv
import json
import time
import os.path
import customtkinter as ctk
from tkinter import filedialog, messagebox
from datetime import datetime

# Set appearance mode and default color theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def compare_csv_files(file1_path, file2_path, key_columns, name_columns):
    """Compare two CSV files and identify differences."""
    start_time = time.time()
    
    # Read data from both files
    data1, headers = read_csv_data(file1_path, key_columns)
    data2, _ = read_csv_data(file2_path, key_columns, read_header=False)
    
    # Find differences using dictionary comprehensions
    differences = {
        "only_in_file1": [{"key": k, "row": data1[k]} for k in data1 if k not in data2],
        "only_in_file2": [{"key": k, "row": data2[k]} for k in data2 if k not in data1],
        "modified": []
    }
    
    # Process modified rows
    for key in [k for k in data1 if k in data2 and data1[k] != data2[k]]:
        changes = [
            {
                "column": headers[i],
                "old_value": val1,
                "new_value": val2
            }
            for i, (val1, val2) in enumerate(zip(data1[key], data2[key])) 
            if val1 != val2
        ]
        
        differences["modified"].append({
            "key": key,
            "row": data1[key],
            "row2": data2[key],
            "changes": changes
        })
    
    print(f"Comparison completed in {time.time() - start_time:.4f} seconds")
    return differences, headers

def read_csv_data(file_path, key_columns, read_header=True):
    """Read CSV file and return data dictionary and optional headers."""
    data = {}
    headers = []
    
    with open(file_path, 'r', newline='') as f:
        reader = csv.reader(f)
        headers = next(reader) if read_header else []
        
        for row in reader:
            key = tuple(row[i] for i in key_columns)
            data[key] = row
    
    return data, headers

class CSVComparisonApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("CSV Comparison Tool")
        self.geometry("1100x800")
        self.minsize(900, 700)
        
        # State variables
        self.file1_path = ""
        self.file2_path = ""
        self.key_columns = [0]  # Always use column 0 as key
        self.name_columns = []
        self.headers = []
        self.comparison_results = None
        self.filtered_results = {
            "modified": [],
            "only_in_file1": [],
            "only_in_file2": []
        }
        
        # Create main UI container
        self.main_scrollable_frame = ctk.CTkScrollableFrame(self)
        self.main_scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Create UI components
        self.create_widgets()
        
        # Status message
        self.status_bar = ctk.CTkLabel(
            self, text="Ready", font=("Segoe UI", 12), anchor="w", height=30
        )
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=5)
    
    def create_widgets(self):
        """Create all UI widgets by calling specialized methods."""
        self.create_header_section()
        self.create_file_selection_section()
        self.create_column_selection_section()
        self.create_results_section()
    
    def create_header_section(self):
        """Create the header section with app title and description."""
        header_frame = ctk.CTkFrame(self.main_scrollable_frame, corner_radius=10)
        header_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header_frame, 
            text="CSV Comparison Tool",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")
        
        ctk.CTkLabel(
            header_frame,
            text="Compare two CSV files and identify differences",
            font=ctk.CTkFont(family="Segoe UI", size=14)
        ).grid(row=1, column=0, padx=20, pady=(0, 15), sticky="w")
    
    def create_file_selection_section(self):
        """Create file selection section with browse buttons."""
        middle_frame = ctk.CTkFrame(self.main_scrollable_frame, corner_radius=10)
        middle_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        middle_frame.grid_columnconfigure(0, weight=1)
        
        file_frame = ctk.CTkFrame(middle_frame, corner_radius=10)
        file_frame.grid(row=0, column=0, padx=15, pady=15, sticky="ew")
        file_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            file_frame,
            text="Step 1: Select CSV Files",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=15, pady=(15, 10), sticky="w")
        
        # File 1 selection
        self.file1_entry = self.create_file_selector(
            file_frame, 1, "First CSV File:", self.browse_file1
        )
        
        # File 2 selection
        self.file2_entry = self.create_file_selector(
            file_frame, 2, "Second CSV File:", self.browse_file2
        )
    
    def create_file_selector(self, parent, row, label_text, browse_command):
        """Create a file selector row with label, entry, and browse button."""
        ctk.CTkLabel(
            parent, text=label_text, font=("Segoe UI", 12)
        ).grid(row=row, column=0, padx=15, pady=10, sticky="w")
        
        entry = ctk.CTkEntry(parent, font=("Segoe UI", 12), height=32)
        entry.grid(row=row, column=1, padx=(0, 10), pady=10, sticky="ew")
        
        ctk.CTkButton(
            parent, 
            text="Browse...", 
            command=browse_command,
            font=("Segoe UI", 12),
            height=32
        ).grid(row=row, column=2, padx=(0, 15), pady=10)
        
        return entry
    
    def create_column_selection_section(self):
        """Create column selection area with available and selected columns."""
        middle_frame = self.main_scrollable_frame.winfo_children()[1]
        
        column_frame = ctk.CTkFrame(middle_frame, corner_radius=10)
        column_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="ew")
        column_frame.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(
            column_frame,
            text="Step 2: Select Display Columns",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=15, pady=(15, 10), sticky="w")
        
        # Available columns frame
        self.available_listbox = self.create_column_list(
            column_frame, 0, "Available Columns (click to add)"
        )
        
        # Selected columns frame
        self.selected_listbox = self.create_column_list(
            column_frame, 1, "Display Columns (click to remove)"
        )
        
        # Initialize button lists
        self.available_buttons = []
        self.selected_buttons = []
    
    def create_column_list(self, parent, col, title_text):
        """Create a column list frame with title and scrollable area."""
        frame = ctk.CTkFrame(parent)
        frame.grid(row=1, column=col, padx=15, pady=(0, 15), sticky="nsew")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame,
            text=title_text,
            font=("Segoe UI", 12, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        listbox = ctk.CTkScrollableFrame(frame)
        listbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        listbox.grid_columnconfigure(0, weight=1)
        
        return listbox
    
    def create_results_section(self):
        """Create results section with filter, format options and tabs."""
        results_frame = ctk.CTkFrame(self.main_scrollable_frame, corner_radius=10)
        results_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        results_frame.grid_rowconfigure(1, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        
        # Results title and controls
        controls_frame = ctk.CTkFrame(results_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        controls_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            controls_frame,
            text="Step 3: View Results",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        ).grid(row=0, column=0, padx=(0, 15), pady=0, sticky="w")
        
        # Filter controls
        self.create_filter_controls(controls_frame)
        
        # Results tabs
        self.results_tabs = ctk.CTkTabview(results_frame, corner_radius=10, height=300)
        self.results_tabs.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        
        # Create tabs with text widgets
        tab_names = ["Modified Rows", "Only in First File", "Only in Second File"]
        self.result_text_widgets = {}
        
        for tab_name in tab_names:
            tab = self.results_tabs.add(tab_name)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_columnconfigure(0, weight=1)
            
            text_widget = ctk.CTkTextbox(tab, font=("Segoe UI", 12))
            text_widget.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
            self.result_text_widgets[tab_name] = text_widget
    
    def create_filter_controls(self, parent):
        """Create filter controls including text entry and output options."""
        # Filter label and entry
        ctk.CTkLabel(
            parent, text="Filter:", font=("Segoe UI", 12)
        ).grid(row=0, column=1, padx=(15, 5), pady=0, sticky="e")
        
        self.filter_entry = ctk.CTkEntry(
            parent, font=("Segoe UI", 12), height=32, width=200
        )
        self.filter_entry.grid(row=0, column=2, padx=(0, 5), pady=0, sticky="e")
        self.filter_entry.bind("<KeyRelease>", self.apply_filter)
        
        # Exact match checkbox
        self.exact_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            parent, text="Exact", variable=self.exact_var,
            command=self.apply_filter, font=("Segoe UI", 12), height=32
        ).grid(row=0, column=3, padx=(5, 5), pady=0, sticky="e")
        
        # Output format selection
        ctk.CTkLabel(
            parent, text="Output:", font=("Segoe UI", 12)
        ).grid(row=0, column=4, padx=(5, 5), pady=0, sticky="e")
        
        self.output_format_var = ctk.StringVar(value="Text")
        ctk.CTkOptionMenu(
            parent, values=["Text", "CSV", "JSON"],
            variable=self.output_format_var,
            command=self.change_output_format,
            font=("Segoe UI", 12), height=32, width=100
        ).grid(row=0, column=5, padx=(0, 5), pady=0, sticky="e")
        
        # Download button
        ctk.CTkButton(
            parent, text="Download",
            command=self.download_results,
            font=("Segoe UI", 12), height=32, width=100
        ).grid(row=0, column=6, padx=(5, 0), pady=0, sticky="e")
    
    def browse_file1(self):
        """Browse for first CSV file."""
        self.browse_file(is_first=True)
    
    def browse_file2(self):
        """Browse for second CSV file."""
        self.browse_file(is_first=False)
    
    def browse_file(self, is_first=True):
        """Generic file browser that updates the appropriate entry."""
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not filename:
            return
            
        if is_first:
            self.file1_path = filename
            self.file1_entry.delete(0, "end")
            self.file1_entry.insert(0, filename)
        else:
            self.file2_path = filename
            self.file2_entry.delete(0, "end")
            self.file2_entry.insert(0, filename)
        
        self.check_and_load_headers()
    
    def check_and_load_headers(self):
        """Check if both files are selected and load headers."""
        if (self.file1_path and os.path.isfile(self.file1_path) and 
            self.file2_path and os.path.isfile(self.file2_path)):
            self.load_headers()
    
    def load_headers(self):
        """Load headers from the first CSV file and populate column lists."""
        if not self.file1_path or not os.path.isfile(self.file1_path):
            messagebox.showerror("Error", "Please select a valid first CSV file")
            return
        
        try:
            with open(self.file1_path, 'r', newline='') as f:
                reader = csv.reader(f)
                self.headers = next(reader)
                
                # Clear existing buttons
                for button in self.available_buttons + self.selected_buttons:
                    button.destroy()
                self.available_buttons = []
                self.selected_buttons = []
                
                # Reset name columns
                self.name_columns = []
                
                # Populate available columns
                for i, header in enumerate(self.headers):
                    item_text = f"{i}: {header}"
                    btn = ctk.CTkButton(
                        self.available_listbox,
                        text=item_text,
                        command=lambda idx=i, txt=item_text: self.add_display_column(idx, txt),
                        font=("Segoe UI", 12),
                        anchor="w",
                        height=30,
                        fg_color=("#3B8ED0" if i % 2 == 0 else "#1F6AA5")
                    )
                    btn.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
                    self.available_buttons.append(btn)
                
                self.status_bar.configure(text=f"Loaded {len(self.headers)} columns")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load headers: {str(e)}")
    
    def add_display_column(self, col_index, item_text):
        """Add a column to the display columns list."""
        if col_index in self.name_columns:
            return
            
        self.name_columns.append(col_index)
        
        # Create removal button
        btn = ctk.CTkButton(
            self.selected_listbox,
            text=item_text,
            command=lambda idx=col_index: self.remove_display_column(idx),
            font=("Segoe UI", 12),
            anchor="w",
            height=30,
            fg_color="#E74C3C"
        )
        btn.grid(row=len(self.selected_buttons), column=0, padx=5, pady=2, sticky="ew")
        self.selected_buttons.append(btn)
        
        self.status_bar.configure(text=f"Added '{item_text.split(':', 1)[1].strip()}' as a display column")
        
        # Auto-run comparison
        self.compare_files()
    
    def remove_display_column(self, col_index):
        """Remove a column from the display columns list."""
        if col_index not in self.name_columns:
            return
            
        idx = self.name_columns.index(col_index)
        self.name_columns.remove(col_index)
        
        # Remove and destroy button
        self.selected_buttons[idx].destroy()
        self.selected_buttons.pop(idx)
        
        # Reposition remaining buttons
        for i, btn in enumerate(self.selected_buttons):
            btn.grid(row=i, column=0, padx=5, pady=2, sticky="ew")
        
        column_name = self.headers[col_index] if col_index < len(self.headers) else "Unknown"
        self.status_bar.configure(text=f"Removed '{column_name}' from display columns")
        
        # Update results
        if self.name_columns:
            self.compare_files()
        else:
            self.clear_results()
    
    def clear_results(self):
        """Clear all result text widgets."""
        for text_widget in self.result_text_widgets.values():
            text_widget.delete("1.0", "end")
    
    def apply_filter(self, event=None):
        """Apply filter to the results as user types."""
        if not self.comparison_results:
            return
        
        self.display_results(
            self.comparison_results, 
            self.filter_entry.get().lower(),
            self.exact_var.get(),
            self.output_format_var.get()
        )
    
    def change_output_format(self, choice):
        """Handle output format change."""
        if not self.comparison_results:
            return
        
        self.display_results(
            self.comparison_results,
            self.filter_entry.get().lower(),
            self.exact_var.get(),
            choice
        )
    
    def compare_files(self):
        """Compare the two CSV files and show results."""
        # Validate inputs
        if (not self.file1_path or not os.path.isfile(self.file1_path) or
            not self.file2_path or not os.path.isfile(self.file2_path) or
            not self.name_columns):
            return
        
        self.status_bar.configure(text="Comparing files...")
        self.update_idletasks()
        
        try:
            self.comparison_results = compare_csv_files(
                self.file1_path, self.file2_path, self.key_columns, self.name_columns
            )
            
            self.display_results(
                self.comparison_results,
                self.filter_entry.get().lower(),
                self.exact_var.get(),
                self.output_format_var.get()
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed: {str(e)}")
            self.status_bar.configure(text="Comparison failed")
    
    def display_results(self, comparison_data, filter_text="", exact_mode=False, output_format="Text"):
        """Display results with optional filtering in the selected format."""
        differences, headers = comparison_data
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
        
        # Select display method based on format
        display_methods = {
            "Text": self.display_text_format,
            "CSV": self.display_csv_format,
            "JSON": self.display_json_format
        }
        
        # Call appropriate display method
        display_methods[output_format](filtered_modified, filtered_file1, filtered_file2, headers)
        
        # Update status message
        counts = {
            "Modified": len(filtered_modified),
            "Only in first": len(filtered_file1),
            "Only in second": len(filtered_file2)
        }
        
        status_parts = []
        if filter_text:
            status_parts.append(f"Filtered by '{filter_text}'")
            if exact_mode:
                status_parts.append("Exact mode enabled")
        
        status_parts.extend([f"{label}: {count}" for label, count in counts.items() if count > 0])
        self.status_bar.configure(text=". ".join(status_parts) if status_parts else "No differences found")
        
        # Switch to tab with most differences
        max_count = max(counts.values(), default=0)
        if max_count > 0:
            if max_count == counts["Modified"]:
                self.results_tabs.set("Modified Rows")
            elif max_count == counts["Only in first"]:
                self.results_tabs.set("Only in First File")
            elif max_count == counts["Only in second"]:
                self.results_tabs.set("Only in Second File")
    
    def get_display_name(self, row):
        """Get display name from a row using name columns."""
        return " ".join(row[col] for col in self.name_columns)
    
    def display_text_format(self, filtered_modified, filtered_file1, filtered_file2, headers):
        """Display results in text format."""
        # Modified rows
        modified_text = self.result_text_widgets["Modified Rows"]
        modified_text.insert("1.0", f"Modified Rows: {len(filtered_modified)}\n\n")
        
        for i, mod in enumerate(filtered_modified):
            modified_text.insert("end", f"{i+1}. {self.get_display_name(mod['row'])}\n")
            
            # Show changes based on filter settings
            filter_text = self.filter_entry.get().lower()
            exact_mode = self.exact_var.get()
            
            changes_to_show = mod["changes"]
            if filter_text and exact_mode:
                # In exact mode, only show matching columns
                changes_to_show = [
                    c for c in mod["changes"]
                    if (filter_text in str(c["column"]).lower() or
                        filter_text in str(c["old_value"]).lower() or
                        filter_text in str(c["new_value"]).lower())
                ]
            
            for change in changes_to_show:
                modified_text.insert(
                    "end", 
                    f"   Column '{change['column']}': '{change['old_value']}' → '{change['new_value']}'\n"
                )
            
            modified_text.insert("end", "\n")
        
        # Rows only in file 1
        self.display_file_only_text(
            self.result_text_widgets["Only in First File"],
            filtered_file1, 
            "Rows only in first file:",
            headers
        )
        
        # Rows only in file 2
        self.display_file_only_text(
            self.result_text_widgets["Only in Second File"],
            filtered_file2, 
            "Rows only in second file:",
            headers
        )
    
    def display_file_only_text(self, text_widget, items, title, headers):
        """Display items that are only in one file in text format."""
        text_widget.insert("1.0", f"{title} {len(items)}\n\n")
        
        filter_text = self.filter_entry.get().lower()
        exact_mode = self.exact_var.get()
        
        for i, item in enumerate(items):
            text_widget.insert("end", f"{i+1}. {self.get_display_name(item['row'])}\n")
            
            # Determine which fields to show based on filter
            for j, val in enumerate(item["row"]):
                if j >= len(headers):
                    continue
                    
                # Skip non-matching fields in exact mode with filter
                if filter_text and exact_mode and filter_text not in str(val).lower():
                    continue
                    
                text_widget.insert("end", f"   {headers[j]}: {val}\n")
            
            text_widget.insert("end", "\n")
    
    def display_csv_format(self, filtered_modified, filtered_file1, filtered_file2, headers):
        """Display results in CSV format."""
        # Modified rows
        modified_text = self.result_text_widgets["Modified Rows"]
        modified_text.insert("1.0", f"Modified Rows: {len(filtered_modified)}\n\n")
        
        if filtered_modified:
            # Create header row
            header_row = "Item #,Name"
            for h in headers:
                header_row += f",{h} (Old),{h} (New)"
            modified_text.insert("end", header_row + "\n")
            
            # Create data rows
            for i, item in enumerate(filtered_modified):
                row = f"{i+1},{self.get_display_name(item['row'])}"
                for j in range(len(headers)):
                    old_val = item["row"][j] if j < len(item["row"]) else ""
                    new_val = item["row2"][j] if j < len(item["row2"]) else ""
                    row += f",{old_val},{new_val}"
                
                modified_text.insert("end", row + "\n")
        
        # Only in file 1
        self.display_file_only_csv(
            self.result_text_widgets["Only in First File"],
            filtered_file1,
            "Rows only in first file:",
            headers
        )
        
        # Only in file 2
        self.display_file_only_csv(
            self.result_text_widgets["Only in Second File"],
            filtered_file2,
            "Rows only in second file:",
            headers
        )
    
    def display_file_only_csv(self, text_widget, items, title, headers):
        """Display items that are only in one file in CSV format."""
        text_widget.insert("1.0", f"{title} {len(items)}\n\n")
        
        if items:
            # Header row
            text_widget.insert("end", "Item #,Name," + ",".join(headers) + "\n")
            
            # Data rows
            for i, item in enumerate(items):
                row = f"{i+1},{self.get_display_name(item['row'])}"
                for j in range(len(headers)):
                    val = item["row"][j] if j < len(item["row"]) else ""
                    row += f",{val}"
                
                text_widget.insert("end", row + "\n")
    
    def display_json_format(self, filtered_modified, filtered_file1, filtered_file2, headers):
        """Display results in JSON format."""
        # Create JSON strings for each tab
        modified_json = self.create_json_string(filtered_modified, "modified", headers)
        file1_json = self.create_json_string(filtered_file1, "only_in_file1", headers)
        file2_json = self.create_json_string(filtered_file2, "only_in_file2", headers)
        
        # Insert into text widgets
        self.result_text_widgets["Modified Rows"].insert("1.0", f"Modified Rows: {len(filtered_modified)}\n\n{modified_json}")
        self.result_text_widgets["Only in First File"].insert("1.0", f"Rows only in first file: {len(filtered_file1)}\n\n{file1_json}")
        self.result_text_widgets["Only in Second File"].insert("1.0", f"Rows only in second file: {len(filtered_file2)}\n\n{file2_json}")
    
    def create_json_string(self, items, item_type, headers):
        """Create a JSON string from the filtered items."""
        if not items:
            return f"No {item_type.replace('_', ' ')} rows found."
        
        filter_text = self.filter_entry.get().lower()
        exact_mode = self.exact_var.get()
        
        json_data = []
        for item in items:
            name_display = self.get_display_name(item["row"])
            
            if item_type == "modified":
                # For modified items
                if exact_mode and filter_text:
                    # Only include matching fields in exact mode
                    original_row = {
                        headers[i]: val for i, val in enumerate(item["row"])
                        if i < len(headers) and filter_text in str(val).lower()
                    }
                    
                    new_row = {
                        headers[i]: val for i, val in enumerate(item["row2"])
                        if i < len(headers) and filter_text in str(val).lower()
                    }
                    
                    filtered_changes = [
                        {
                            "column": c["column"],
                            "old_value": c["old_value"],
                            "new_value": c["new_value"]
                        }
                        for c in item["changes"]
                        if (filter_text in str(c["column"]).lower() or
                            filter_text in str(c["old_value"]).lower() or
                            filter_text in str(c["new_value"]).lower())
                    ]
                    
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
                        "original_row": {headers[i]: val for i, val in enumerate(item["row"]) if i < len(headers)},
                        "new_row": {headers[i]: val for i, val in enumerate(item["row2"]) if i < len(headers)},
                        "changes": [
                            {
                                "column": c["column"],
                                "old_value": c["old_value"],
                                "new_value": c["new_value"]
                            }
                            for c in item["changes"]
                        ]
                    }
            else:
                # For items only in one file
                if exact_mode and filter_text:
                    # Only include matching fields in exact mode
                    filtered_row = {
                        headers[i]: val for i, val in enumerate(item["row"])
                        if i < len(headers) and filter_text in str(val).lower()
                    }
                    
                    json_item = {
                        "name": name_display,
                        "row": filtered_row
                    }
                else:
                    # Include all fields
                    json_item = {
                        "name": name_display,
                        "row": {headers[i]: val for i, val in enumerate(item["row"]) if i < len(headers)}
                    }
            
            json_data.append(json_item)
        
        return json.dumps(json_data, indent=2)
    
    def filter_items(self, items, filter_text, exact_mode=False):
        """Filter items based on filter text."""
        if not filter_text:
            return items
        
        filtered_items = []
        
        for item in items:
            # Handle modified items with changes
            if "changes" in item:
                if any(self.matches_filter(change, filter_text) for change in item["changes"]):
                    filtered_items.append(item)
            # Handle items only in one file
            elif any(filter_text in str(val).lower() for val in item["row"]):
                filtered_items.append(item)
        
        return filtered_items
    
    def matches_filter(self, change, filter_text):
        """Check if a change matches the filter text."""
        return (filter_text in str(change["column"]).lower() or
                filter_text in str(change["old_value"]).lower() or
                filter_text in str(change["new_value"]).lower())
    
    def download_results(self):
        """Download the current results in the selected format."""
        if not self.comparison_results:
            messagebox.showinfo("No Data", "No comparison results to download.")
            return
        
        # Get current tab and data type
        tab_to_type = {
            "Modified Rows": "modified",
            "Only in First File": "only_in_file1",
            "Only in Second File": "only_in_file2"
        }
        
        current_tab = self.results_tabs.get()
        data_type = tab_to_type[current_tab]
        items = self.filtered_results[data_type]
        
        # Configure file format options
        format_config = {
            "CSV": {
                "ext": ".csv",
                "filetypes": [("CSV files", "*.csv")],
                "save_func": self.save_as_csv
            },
            "JSON": {
                "ext": ".json",
                "filetypes": [("JSON files", "*.json")],
                "save_func": self.save_as_json
            },
            "Text": {
                "ext": ".txt",
                "filetypes": [("Text files", "*.txt")],
                "save_func": self.save_as_text
            }
        }
        
        output_format = self.output_format_var.get()
        config = format_config[output_format]
        
        # Generate timestamp and filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"csv_comparison_{data_type}_{timestamp}"
        
        filename = filedialog.asksaveasfilename(
            defaultextension=config["ext"],
            filetypes=config["filetypes"],
            initialfile=f"{base_filename}{config['ext']}"
        )
        
        if filename:
            try:
                config["save_func"](filename, items, data_type)
                self.status_bar.configure(text=f"Results saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
    
    def save_as_csv(self, filename, items, data_type):
        """Save the filtered results as a CSV file."""
        headers = self.filtered_results["headers"]
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if data_type == "modified":
                # Write header for modified items
                header_row = ["Item #", "Name"]
                for h in headers:
                    header_row.extend([f"{h} (Old)", f"{h} (New)"])
                header_row.append("Changes")
                writer.writerow(header_row)
                
                # Write data rows
                for i, item in enumerate(items):
                    changes_str = "; ".join([
                        f"{c['column']}: '{c['old_value']}' -> '{c['new_value']}'"
                        for c in item["changes"]
                    ])
                    
                    row_data = [str(i+1), self.get_display_name(item["row"])]
                    for j in range(len(headers)):
                        row_data.append(item["row"][j] if j < len(item["row"]) else "")
                        row_data.append(item["row2"][j] if j < len(item["row2"]) else "")
                    
                    row_data.append(changes_str)
                    writer.writerow(row_data)
            else:
                # Write header for items only in one file
                writer.writerow(["Item #", "Name"] + headers)
                
                # Write data rows
                for i, item in enumerate(items):
                    writer.writerow([str(i+1), self.get_display_name(item["row"])] + item["row"])
    
    def save_as_json(self, filename, items, data_type):
        """Save the filtered results as a JSON file."""
        json_str = self.create_json_string(items, data_type, self.filtered_results["headers"])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json_str)
    
    def save_as_text(self, filename, items, data_type):
        """Save the filtered results as a text file."""
        headers = self.filtered_results["headers"]
        
        with open(filename, 'w', encoding='utf-8') as f:
            if data_type == "modified":
                f.write(f"Modified Rows: {len(items)}\n\n")
                for i, mod in enumerate(items):
                    f.write(f"{i+1}. {self.get_display_name(mod['row'])}\n")
                    
                    for change in mod["changes"]:
                        f.write(f"   Column '{change['column']}': '{change['old_value']}' -> '{change['new_value']}'\n")
                    
                    f.write("\n")
            else:
                title = "Rows only in first file:" if data_type == "only_in_file1" else "Rows only in second file:"
                f.write(f"{title} {len(items)}\n\n")
                
                for i, item in enumerate(items):
                    f.write(f"{i+1}. {self.get_display_name(item['row'])}\n")
                    
                    for j, val in enumerate(item["row"]):
                        if j < len(headers):
                            f.write(f"   {headers[j]}: {val}\n")
                    
                    f.write("\n")

if __name__ == "__main__":
    app = CSVComparisonApp()
    app.mainloop()
