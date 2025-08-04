# ui/git_history_viewer.py
# This component defines a window for viewing Git commit history.

import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

class GitHistoryViewer(tk.Toplevel):
    """
    A Toplevel window for displaying Git commit history.
    """
    def __init__(self, parent, history_text):
        super().__init__(parent)
        self.parent = parent
        self.title("Git Commit History")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()

        self.create_widgets(history_text)

    def create_widgets(self, history_text):
        """Creates the widgets for the history viewer."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        history_label = ttk.Label(main_frame, text="Commit History:", font=("Arial", 12, "bold"))
        history_label.pack(anchor=tk.W, pady=(0, 5))

        # Use a ScrolledText for a scrollable display of the history
        self.history_text_widget = ScrolledText(main_frame, wrap=tk.WORD)
        self.history_text_widget.pack(fill=tk.BOTH, expand=True)

        self.history_text_widget.insert(tk.END, history_text)
        self.history_text_widget.config(state='disabled') # Make it read-only

