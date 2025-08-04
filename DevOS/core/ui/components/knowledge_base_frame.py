import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from core.knowledge_base import KnowledgeBase
import webbrowser

class KnowledgeBaseFrame(ctk.CTkFrame):
    def __init__(self, parent, application):
        super().__init__(parent)
        self.app = application
        self.create_widgets()
        
    def create_widgets(self):
        # Search bar
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame, 
            textvariable=self.search_var,
            placeholder_text="Search knowledge base..."
        )
        search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        search_btn = ctk.CTkButton(
            search_frame,
            text="Search",
            command=self.perform_search
        )
        search_btn.pack(side="right", padx=5)
        
        # Results tree
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("category", "updated"), show="headings")
        self.tree.heading("#0", text="Title")
        self.tree.heading("category", text="Category")
        self.tree.heading("updated", text="Updated")
        
        self.tree.column("#0", width=300)
        self.tree.column("category", width=150)
        self.tree.column("updated", width=150)
        
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self.on_resource_select)
        
        # Resource view
        self.resource_frame = ctk.CTkFrame(self)
        self.resource_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.title_label = ctk.CTkLabel(self.resource_frame, text="", font=("Arial", 14, "bold"))
        self.title_label.pack(anchor="w", padx=10, pady=5)
        
        self.category_label = ctk.CTkLabel(self.resource_frame, text="", font=("Arial", 12))
        self.category_label.pack(anchor="w", padx=10, pady=2)
        
        self.content_text = tk.Text(
            self.resource_frame, 
            wrap="word",
            height=15
        )
        self.content_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.content_text.config(state="disabled")
        
        self.url_btn = ctk.CTkButton(
            self.resource_frame,
            text="Open Resource",
            command=self.open_resource_url
        )
        self.url_btn.pack(anchor="e", padx=10, pady=5)
        self.url_btn.pack_forget()  # Hide initially
        
        # Initial search for popular topics
        self.perform_search("development")
        
    def perform_search(self, query=None):
        """Perform a knowledge base search"""
        if query is None:
            query = self.search_var.get()
            
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Perform search
        results = self.app.search_knowledge(query)
        
        # Populate tree
        for result in results:
            self.tree.insert("", "end", 
                text=result['title'],
                values=(result['category'], result['last_updated']),
                tags=(result['id'],)
            )
        
        # Show first result if any
        if results:
            self.tree.selection_set(self.tree.get_children()[0])
            self.on_resource_select()
    
    def on_resource_select(self, event=None):
        """Handle resource selection"""
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        resource_id = item['tags'][0]
        
        # Get full resource
        resource = self.app.knowledge_base.get_resource_by_id(resource_id)
        if not resource:
            return
            
        # Display resource
        self.title_label.configure(text=resource['title'])
        self.category_label.configure(text=f"Category: {resource['category']}")
        
        self.content_text.config(state="normal")
        self.content_text.delete(1.0, "end")
        self.content_text.insert(1.0, resource['content'])
        self.content_text.config(state="disabled")
        
        # Show URL button if resource has URL
        if resource.get('url'):
            self.url_btn.configure(text=f"Open: {resource['url']}")
            self.url_btn.pack(anchor="e", padx=10, pady=5)
        else:
            self.url_btn.pack_forget()
    
    def open_resource_url(self):
        """Open resource URL in browser"""
        selected = self.tree.selection()
        if not selected:
            return
            
        item = self.tree.item(selected[0])
        resource_id = item['tags'][0]
        resource = self.app.knowledge_base.get_resource_by_id(resource_id)
        
        if resource and resource.get('url'):
            webbrowser.open(resource['url'])