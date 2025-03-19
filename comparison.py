import csv
import time
import os.path
import customtkinter as ctk
from tkinter import filedialog, messagebox

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
        
        # Results title
        self.results_title = ctk.CTkLabel(
            self.results_frame,
            text="Step 3: View Results",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
        )
        self.results_title.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="w")
        
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
            differences, headers = compare_csv_files(file1, file2, self.key_columns, self.name_columns)
            
            # Clear result text widgets
            self.clear_results()
            
            # Display modified rows
            self.modified_text.insert("1.0", f"Modified Rows: {len(differences['modified'])}\n\n")
            for i, mod in enumerate(differences["modified"]):
                # Get the name from the row data using name_columns
                name_parts = [mod["row"][col] for col in self.name_columns]
                name_display = " ".join(name_parts)
                
                self.modified_text.insert("end", f"{i+1}. {name_display}\n")
                for change in mod["changes"]:
                    self.modified_text.insert("end", f"   Column '{change['column']}': '{change['old_value']}' → '{change['new_value']}'\n")
                self.modified_text.insert("end", "\n")
            
            # Display rows only in file 1
            self.only_in_file1_text.insert("1.0", f"Rows only in first file: {len(differences['only_in_file1'])}\n\n")
            for i, item in enumerate(differences['only_in_file1']):
                name_parts = [item["row"][col] for col in self.name_columns]
                name_display = " ".join(name_parts)
                self.only_in_file1_text.insert("end", f"{i+1}. {name_display}\n")
                for j, val in enumerate(item["row"]):
                    if j < len(headers):
                        self.only_in_file1_text.insert("end", f"   {headers[j]}: {val}\n")
                self.only_in_file1_text.insert("end", "\n")
            
            # Display rows only in file 2
            self.only_in_file2_text.insert("1.0", f"Rows only in second file: {len(differences['only_in_file2'])}\n\n")
            for i, item in enumerate(differences['only_in_file2']):
                name_parts = [item["row"][col] for col in self.name_columns]
                name_display = " ".join(name_parts)
                self.only_in_file2_text.insert("end", f"{i+1}. {name_display}\n")
                for j, val in enumerate(item["row"]):
                    if j < len(headers):
                        self.only_in_file2_text.insert("end", f"   {headers[j]}: {val}\n")
                self.only_in_file2_text.insert("end", "\n")
            
            # Update status
            modified_count = len(differences['modified'])
            only_in_file1_count = len(differences['only_in_file1'])
            only_in_file2_count = len(differences['only_in_file2'])
            
            status_text = f"Comparison complete. "
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
            max_diff = max(modified_count, only_in_file1_count, only_in_file2_count)
            
            if max_diff == modified_count:
                self.results_tabs.set("Modified Rows")
            elif max_diff == only_in_file1_count:
                self.results_tabs.set("Only in First File")
            else:
                self.results_tabs.set("Only in Second File")
                
        except Exception as e:
            messagebox.showerror("Error", f"Comparison failed: {str(e)}")
            self.status_bar.configure(text="Comparison failed")

if __name__ == "__main__":
    app = CSVComparisonApp()
    app.mainloop()
