import customtkinter as ctk
from tkinter import ttk

class SystemHealthFrame(ctk.CTkFrame):
    def __init__(self, parent, application):
        super().__init__(parent)
        self.app = application
        self.create_widgets()
        self.refresh_data()
        
    def create_widgets(self):
        # System overview
        overview_frame = ctk.CTkFrame(self)
        overview_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(overview_frame, text="System Overview", font=("Arial", 16, "bold")).pack(anchor="w", pady=5)
        
        self.overview_tree = ttk.Treeview(overview_frame, columns=("value"), height=5)
        self.overview_tree.heading("#0", text="Component")
        self.overview_tree.heading("value", text="Value")
        self.overview_tree.pack(fill="x", padx=5, pady=5)
        
        # Issues list
        issues_frame = ctk.CTkFrame(self)
        issues_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(issues_frame, text="Detected Issues", font=("Arial", 16, "bold")).pack(anchor="w", pady=5)
        
        self.issues_tree = ttk.Treeview(issues_frame, columns=("severity", "repairable", "action"), height=10)
        self.issues_tree.heading("#0", text="Description")
        self.issues_tree.heading("severity", text="Severity")
        self.issues_tree.heading("repairable", text="Repairable")
        self.issues_tree.heading("action", text="Action")
        self.issues_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Repair button
        btn_frame = ctk.CTkFrame(issues_frame)
        btn_frame.pack(fill="x", pady=5)
        
        self.repair_btn = ctk.CTkButton(
            btn_frame,
            text="Repair Selected",
            command=self.repair_selected
        )
        self.repair_btn.pack(side="left", padx=5)
        
        self.refresh_btn = ctk.CTkButton(
            btn_frame,
            text="Refresh Status",
            command=self.refresh_data
        )
        self.refresh_btn.pack(side="right", padx=5)
        
    def refresh_data(self):
        # Clear existing data
        for item in self.overview_tree.get_children():
            self.overview_tree.delete(item)
            
        for item in self.issues_tree.get_children():
            self.issues_tree.delete(item)
            
        # Load current system status
        status = self.app.system_status
        
        # Populate overview
        self.overview_tree.insert("", "end", text="Operating System", values=(status['platform'],))
        self.overview_tree.insert("", "end", text="CPU Cores", values=(f"{status['cpu']['cores']} physical, {status['cpu']['logical_cores']} logical",))
        self.overview_tree.insert("", "end", text="Memory", values=(f"{status['memory']['total'] // 1024**3}GB total",))
        self.overview_tree.insert("", "end", text="Disk Space", values=(f"{status['disk']['free'] // 1024**3}GB free",))
        self.overview_tree.insert("", "end", text="Status", values=("Meets Requirements" if status['meets_requirements'] else "Issues Detected",))
        
        # Populate issues
        for issue in status['issues']:
            self.issues_tree.insert("", "end", text=issue['description'], values=(
                issue['severity'],
                "Yes" if issue.get('repairable', False) else "No",
                "Click Repair" if issue.get('repairable', False) else "Manual Fix Needed"
            ), tags=(issue['id'],))
            
    def repair_selected(self):
        selected = self.issues_tree.selection()
        if not selected:
            return
            
        issue_id = self.issues_tree.item(selected[0], "tags")[0]
        if self.app.repair_system(issue_id):
            self.refresh_data()