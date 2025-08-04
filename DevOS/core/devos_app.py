import tkinter as tk
from tkinter import ttk
import os
import subprocess
import time
import psutil
import json
import threading
from typing import Dict, List, Any

# We'll use this for the Git integration, but mock it for now since we don't have a real library
class M# core/devos_app.py
# This file contains the final DevOS application class and its core logic.
# It has been updated to integrate all advanced features: collaboration,
# advanced editing, debugging, and enhanced AI.

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter.scrolledtext import ScrolledText
import os
import sys
import logging
import datetime
import json
from typing import Dict, Any, List

# --- New Dependencies ---
try:
    import psutil
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    logging.warning("Matplotlib not found. Metrics plotting will be disabled.")

# Add the project directories to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ui'))

# Import all core components
from git_integration import GitIntegration
from ai_integrator import AIIntegrator
from metrics_monitor import MetricsMonitor
from settings_manager import SettingsManager
from firebase_manager import FirebaseManager
from linter_manager import LinterManager

# Import all UI components
from code_editor import CodeEditor
from git_history_viewer import GitHistoryViewer
from settings_dialog import SettingsDialog
from collaboration_panel import CollaborationPanel
from debugging_panel import DebuggingPanel

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Helper Functions ---
def show_message(title: str, message: str, level: str = 'info'):
    """Displays a message to the user in a non-blocking dialog."""
    if level == 'error':
        messagebox.showerror(title, message)
    elif level == 'warning':
        messagebox.showwarning(title, message)
    else:
        messagebox.showinfo(title, message)

# --- Main Application Class ---
class DevOS(tk.Tk):
    """
    Main application window for the DevOS project.
    Integrates all components: Code Editor, Git, AI, Metrics, Settings, and now Firebase for collaboration.
    """
    def __init__(self):
        super().__init__()
        self.title("DevOS")
        self.geometry("1400x900")

        # Initialize managers
        self.settings_manager = SettingsManager()
        self.load_settings()

        # Firebase setup
        # Replace this with your actual Firebase config
        firebase_config = {
            "type": "service_account",
            "project_id": "your-project-id",
            "private_key_id": "your-private-key-id",
            "private_key": "your-private-key".replace("\\n", "\n"),
            "client_email": "your-client-email",
            "client_id": "your-client-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-client-email"
        }
        self.firebase_manager = FirebaseManager(firebase_config)

        self.current_file_path = None
        self.project_path = None
        self.git_integration = None
        self.ai_integrator = AIIntegrator()
        self.metrics_monitor = MetricsMonitor()
        self.linter_manager = LinterManager()

        self.create_widgets()
        self.create_menubar()

        # Start a periodic check for AI results
        self.after(100, self.check_ai_results)

        # Bind the close event to our custom handler
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_settings(self):
        """Load settings and apply them to the application."""
        settings = self.settings_manager.load_settings()
        self.font_name = settings.get('font_name', 'Consolas')
        self.font_size = settings.get('font_size', 12)
        self.theme = settings.get('theme', 'light')

    def save_settings(self):
        """Save current settings to a file."""
        settings = {
            'font_name': self.font_name,
            'font_size': self.font_size,
            'theme': self.theme
        }
        self.settings_manager.save_settings(settings)

    def create_widgets(self):
        """Create and lay out the main UI components."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.paned_window_h = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned_window_h.pack(fill=tk.BOTH, expand=True)

        # Left side - Project Explorer
        left_frame = ttk.Frame(self.paned_window_h)
        self.paned_window_h.add(left_frame, weight=1)

        # Center - Editor and Terminal
        center_frame = ttk.Frame(self.paned_window_h)
        self.paned_window_h.add(center_frame, weight=3)

        # Right side - Collaboration, Debug, AI, Linter
        right_frame = ttk.Frame(self.paned_window_h)
        self.paned_window_h.add(right_frame, weight=1)

        # --- Left Frame Contents ---
        ttk.Label(left_frame, text="Project Explorer", font=("Arial", 14, "bold")).pack(pady=5)
        self.project_tree = ttk.Treeview(left_frame)
        self.project_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.project_tree.bind("<<TreeviewSelect>>", self.on_file_select)

        ttk.Label(left_frame, text="Git Status", font=("Arial", 14, "bold")).pack(pady=5)
        self.git_status_text = ScrolledText(left_frame, height=10, state='disabled')
        self.git_status_text.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        # --- Center Frame Contents ---
        self.paned_window_v = ttk.PanedWindow(center_frame, orient=tk.VERTICAL)
        self.paned_window_v.pack(fill=tk.BOTH, expand=True)

        # Top half - Tabbed Editor
        top_half = ttk.Frame(self.paned_window_v)
        self.paned_window_v.add(top_half, weight=3)

        self.notebook = ttk.Notebook(top_half)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.open_editors = {}

        # Bottom half - Terminal/Linter/Console
        bottom_half = ttk.Frame(self.paned_window_v)
        self.paned_window_v.add(bottom_half, weight=1)

        self.bottom_notebook = ttk.Notebook(bottom_half)
        self.bottom_notebook.pack(fill=tk.BOTH, expand=True)

        self.ai_console_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.ai_console_frame, text="Console")
        self.ai_console = ScrolledText(self.ai_console_frame, state='disabled')
        self.ai_console.pack(fill=tk.BOTH, expand=True)

        self.linter_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.linter_frame, text="Linter")
        self.linter_output = ScrolledText(self.linter_frame, state='disabled')
        self.linter_output.pack(fill=tk.BOTH, expand=True)

        self.terminal_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.terminal_frame, text="Terminal")
        self.terminal_output = ScrolledText(self.terminal_frame, state='disabled')
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_input_frame = ttk.Frame(self.terminal_frame)
        self.terminal_input_frame.pack(fill=tk.X)
        ttk.Label(self.terminal_input_frame, text=">").pack(side=tk.LEFT)
        self.terminal_input = ttk.Entry(self.terminal_input_frame)
        self.terminal_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.terminal_input.bind("<Return>", self.execute_terminal_command)

        # --- Right Frame Contents ---
        self.right_notebook = ttk.Notebook(right_frame)
        self.right_notebook.pack(fill=tk.BOTH, expand=True)

        self.collaboration_panel = CollaborationPanel(self.right_notebook, self, self.firebase_manager)
        self.right_notebook.add(self.collaboration_panel, text="Collaboration")

        self.debugging_panel = DebuggingPanel(self.right_notebook, self)
        self.right_notebook.add(self.debugging_panel, text="Debugger")

        self.ai_chat_frame = ttk.Frame(self.right_notebook)
        self.right_notebook.add(self.ai_chat_frame, text="AI Chat")
        self.ai_chat_history = ScrolledText(self.ai_chat_frame, state='disabled')
        self.ai_chat_history.pack(fill=tk.BOTH, expand=True)
        self.ai_chat_input_frame = ttk.Frame(self.ai_chat_frame)
        self.ai_chat_input_frame.pack(fill=tk.X)
        self.ai_chat_input = ScrolledText(self.ai_chat_input_frame, height=3, wrap='word')
        self.ai_chat_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ai_chat_input.bind("<Return>", self.send_ai_chat_message)
        ttk.Button(self.ai_chat_input_frame, text="Send", command=self.send_ai_chat_message).pack(side=tk.RIGHT, padx=5)

    def create_menubar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Project...", command=self.new_project_dialog)
        file_menu.add_command(label="Open Project...", command=self.open_project)
        file_menu.add_command(label="Open File...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_current_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menubar.add_cascade(label="File", menu=file_menu)

        git_menu = tk.Menu(menubar, tearoff=0)
        git_menu.add_command(label="Git Init", command=self.git_init)
        git_menu.add_command(label="Git Status", command=self.git_status)
        git_menu.add_command(label="Git Add All", command=self.git_add_all)
        git_menu.add_command(label="Git Commit...", command=self.git_commit_dialog)
        git_menu.add_command(label="Git Push", command=self.git_push)
        git_menu.add_separator()
        git_menu.add_command(label="View History", command=self.git_show_history)
        git_menu.add_command(label="Create Branch...", command=self.git_create_branch)
        git_menu.add_command(label="Switch Branch...", command=self.git_switch_branch)
        git_menu.add_command(label="Git Diff", command=self.git_diff)
        menubar.add_cascade(label="Git", menu=git_menu)

        ai_menu = tk.Menu(menubar, tearoff=0)
        ai_menu.add_command(label="Ask AI for Code", command=lambda: self.get_current_editor().ask_ai_for_code())
        ai_menu.add_command(label="Explain Code", command=lambda: self.get_current_editor().explain_code_with_ai())
        ai_menu.add_command(label="Generate Docstring", command=lambda: self.get_current_editor().generate_docstring_with_ai())
        ai_menu.add_command(label="Refactor Code", command=lambda: self.get_current_editor().refactor_with_ai())
        ai_menu.add_command(label="Generate Unit Tests", command=lambda: self.get_current_editor().generate_unit_tests())
        menubar.add_cascade(label="AI", menu=ai_menu)

        tools_menu = tk.Menu(menubar, tearoff=0)
        tools_menu.add_command(label="Start Metrics Monitor", command=self.metrics_monitor.start_monitoring)
        tools_menu.add_command(label="Stop Metrics Monitor", command=self.metrics_monitor.stop_monitoring)
        tools_menu.add_command(label="Plot Metrics", command=self.plot_metrics)
        tools_menu.add_command(label="Run Linter", command=self.run_linter_for_current_file)
        menubar.add_cascade(label="Tools", menu=tools_menu)

        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Preferences...", command=self.open_settings_dialog)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        self.config(menu=menubar)

    def get_current_editor(self) -> CodeEditor:
        """Returns the CodeEditor instance in the currently active tab."""
        tab_id = self.notebook.select()
        if tab_id:
            return self.nametowidget(tab_id).editor
        return None

    # --- Project and File Management ---
    def new_project_dialog(self):
        """Creates a new project directory and initializes Git."""
        project_name = simpledialog.askstring("New Project", "Enter the project name:")
        if not project_name:
            return

        project_path_parent = filedialog.askdirectory(title="Select a directory for the new project")
        if not project_path_parent:
            return

        self.project_path = os.path.join(project_path_parent, project_name)
        try:
            os.makedirs(self.project_path, exist_ok=False)
            self.git_integration = GitIntegration(self.project_path)
            self.load_project_tree()
            self.git_init()
            show_message("Success", f"Project '{project_name}' created at {self.project_path}")
        except FileExistsError:
            show_message("Error", "A project with this name already exists.", 'error')
        except Exception as e:
            show_message("Error", f"Failed to create project: {e}", 'error')

    def open_project(self):
        """Opens an existing project directory."""
        project_path = filedialog.askdirectory(title="Open a project directory")
        if project_path:
            self.project_path = project_path
            self.git_integration = GitIntegration(self.project_path)
            self.load_project_tree()
            show_message("Success", f"Opened project at {self.project_path}")

    def load_project_tree(self):
        """Loads the project directory structure into the Treeview."""
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)

        if self.project_path and os.path.isdir(self.project_path):
            self.insert_tree_items("", self.project_path)

    def insert_tree_items(self, parent, path):
        """Recursively inserts directory contents into the Treeview."""
        for entry in sorted(os.listdir(path)):
            full_path = os.path.join(path, entry)
            is_dir = os.path.isdir(full_path)

            if os.path.basename(full_path) == '.git':
                continue

            if is_dir:
                item_id = self.project_tree.insert(parent, "end", text=entry, open=False)
                self.insert_tree_items(item_id, full_path)
            else:
                self.project_tree.insert(parent, "end", text=entry, values=[full_path])

    def on_file_select(self, event):
        """Handles a file selection in the project tree."""
        selected_item = self.project_tree.selection()[0]
        file_path = self.project_tree.item(selected_item, "values")
        if file_path:
            self.open_file(file_path[0])

    def open_file(self, file_path=None):
        """Opens a file in the tabbed code editor."""
        if not file_path:
            file_path = filedialog.askopenfilename(
                title="Open a file",
                initialdir=self.project_path or os.getcwd()
            )

        if file_path and file_path not in self.open_editors:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()

                    tab_frame = ttk.Frame(self.notebook)
                    self.notebook.add(tab_frame, text=os.path.basename(file_path))

                    editor = CodeEditor(
                        tab_frame,
                        devos_app=self,
                        file_path=file_path,
                        font=(self.font_name, self.font_size)
                    )
                    editor.set_content(content)
                    editor.pack(fill=tk.BOTH, expand=True)

                    self.open_editors[file_path] = editor
                    self.notebook.select(tab_frame)
                    self.current_file_path = file_path

                    # Start a real-time listener for this file
                    self.start_file_collaboration(file_path)

            except FileNotFoundError:
                show_message("Error", f"File not found: {file_path}", 'error')
            except Exception as e:
                show_message("Error", f"Failed to open file: {e}", 'error')
        elif file_path:
            for tab_id, editor in self.open_editors.items():
                if tab_id == file_path:
                    self.notebook.select(self.notebook.tabs()[list(self.open_editors.keys()).index(tab_id)])
                    self.current_file_path = file_path
                    break

    def save_current_file(self):
        """Saves the current file, or prompts for a new path if none is open."""
        editor = self.get_current_editor()
        if editor and editor.file_path:
            try:
                with open(editor.file_path, "w", encoding="utf-8") as file:
                    file.write(editor.get_content())
                show_message("Success", f"File saved: {os.path.basename(editor.file_path)}")
            except Exception as e:
                show_message("Error", f"Failed to save file: {e}", 'error')
        elif editor:
            self.save_file_as()

    def save_file_as(self):
        """Saves the current file with a new file path."""
        editor = self.get_current_editor()
        if not editor:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialdir=self.project_path or os.getcwd(),
            title="Save file as"
        )
        if file_path:
            editor.file_path = file_path
            self.notebook.tab(self.notebook.select(), text=os.path.basename(file_path))
            self.save_current_file()
            self.load_project_tree()

    # --- Git Integration Methods ---
    def git_init(self):
        if not self.project_path:
            show_message("Error", "Please open a project first.", 'error')
            return
        result = self.git_integration.init_repo()
        self.log_to_console(result)

    def git_status(self):
        if not self.git_integration:
            show_message("Error", "Please open a project with a Git repository.", 'error')
            return
        result = self.git_integration.status()
        self.git_status_text.config(state='normal')
        self.git_status_text.delete("1.0", tk.END)
        if result.get('success'):
            self.git_status_text.insert(tk.END, result['stdout'])
        else:
            self.git_status_text.insert(tk.END, result.get('error', 'Unknown Error'))
        self.git_status_text.config(state='disabled')

    def git_add_all(self):
        if not self.git_integration:
            show_message("Error", "Please open a project with a Git repository.", 'error')
            return
        result = self.git_integration.add(["."])
        self.log_to_console(result)
        self.git_status()

    def git_commit_dialog(self):
        if not self.git_integration:
            show_message("Error", "Please open a project with a Git repository.", 'error')
            return

        message = simpledialog.askstring("Git Commit", "Enter commit message:", parent=self)
        if message:
            result = self.git_integration.commit(message)
            self.log_to_console(result)
            self.git_status()

    def git_push(self):
        if not self.git_integration:
            show_message("Error", "Please open a project with a Git repository.", 'error')
            return
        result = self.git_integration.push()
        self.log_to_console(result)

    def git_show_history(self):
        if not self.git_integration:
            show_message("Error", "Please open a project with a Git repository.", 'error')
            return

        history_data = self.git_integration.log_history()
        if history_data.get('success'):
            GitHistoryViewer(self, history_data['stdout'])
        else:
            show_message("Error", history_data.get('error', 'Could not get git history.'), 'error')

    def git_create_branch(self):
        if not self.git_integration:
            show_message("Error", "Please open a project with a Git repository.", 'error')
            return
        branch_name = simpledialog.askstring("Create Branch", "Enter new branch name:", parent=self)
        if branch_name:
            result = self.git_integration.create_branch(branch_name)
            self.log_to_console(result)
            self.git_status()

    def git_switch_branch(self):
        if not self.git_integration:
            show_message("Error", "Please open a project with a Git repository.", 'error')
            return

        branches_data = self.git_integration.get_branches()
        if not branches_data['success']:
            show_message("Error", branches_data.get('error', 'Could not get branch list.'), 'error')
            return

        branches = [b.strip() for b in branches_data['stdout'].split('\n') if b.strip()]

        branch_to_switch = simpledialog.askstring("Switch Branch", "Enter branch name to switch to:", parent=self)
        if branch_to_switch in branches:
            result = self.git_integration.switch_branch(branch_to_switch)
            self.log_to_console(result)
            self.git_status()
        elif branch_to_switch:
            show_message("Error", f"Branch '{branch_to_switch}' not found.", 'error')

    def git_diff(self):
        editor = self.get_current_editor()
        if not self.git_integration or not editor or not editor.file_path:
            show_message("Error", "Please open a project and select a file.", 'error')
            return

        result = self.git_integration.diff(editor.file_path)
        self.log_to_console(result)

    # --- AI Integration Methods ---
    def ask_ai_for_code(self, prompt: str, request_type: str = "code_generation"):
        task_id = f"ai-task-{datetime.datetime.now().isoformat()}"
        request = {"type": request_type, "prompt": prompt}
        self.ai_integrator.add_request(task_id, request)
        self.log_to_console({"stdout": f"Sending request to AI for task {task_id}..."})

    def check_ai_results(self):
        result = self.ai_integrator.get_result()
        if result:
            task_id, data = result
            if data.get('success'):
                self.log_to_console({"stdout": f"AI response for task {task_id}:\n{data.get('response')}"})
            else:
                self.log_to_console({"error": f"AI task {task_id} failed: {data.get('error')}"})

        self.after(1000, self.check_ai_results)

    def send_ai_chat_message(self, event=None):
        """Handles sending a message to the interactive AI chat."""
        message = self.ai_chat_input.get("1.0", tk.END).strip()
        if message:
            self.ai_chat_input.delete("1.0", tk.END)
            self.log_ai_chat(f"You: {message}")
            self.ask_ai_for_code(message, request_type="chat_response")

    def log_ai_chat(self, message: str):
        self.ai_chat_history.config(state='normal')
        self.ai_chat_history.insert(tk.END, f"{message}\n\n")
        self.ai_chat_history.config(state='disabled')
        self.ai_chat_history.see(tk.END)

    # --- Metrics and Tools ---
    def plot_metrics(self):
        if not HAS_MATPLOTLIB:
            show_message("Error", "Matplotlib is not installed. Cannot plot metrics.", 'error')
            return

        metrics = self.metrics_monitor.get_metrics()
        if not metrics["timestamps"]:
            show_message("Info", "No metrics have been recorded yet.", 'info')
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        ax1.plot(metrics["timestamps"], metrics["cpu_usage"], 'r-')
        ax1.set_title('CPU Usage')
        ax1.set_ylabel('Percentage')
        ax1.set_ylim(0, 100)

        ax2.plot(metrics["timestamps"], metrics["memory_usage"], 'b-')
        ax2.set_title('Memory Usage')
        ax2.set_ylabel('Percentage')
        ax2.set_ylim(0, 100)

        plt.tight_layout()

        plot_window = tk.Toplevel(self)
        plot_window.title("System Metrics")
        canvas = FigureCanvasTkAgg(fig, master=plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def execute_terminal_command(self, event):
        command = self.terminal_input.get()
        self.terminal_input.delete(0, tk.END)
        self.log_to_terminal(f"\n> {command}")

        try:
            result = subprocess.run(
                command.split(),
                cwd=self.project_path or os.getcwd(),
                capture_output=True,
                text=True,
                timeout=5,
                check=True
            )
            self.log_to_terminal(result.stdout)
        except Exception as e:
            self.log_to_terminal(f"ERROR: {e}")

    def log_to_console(self, result: Dict[str, Any]):
        self.ai_console.config(state='normal')
        if result.get('success', True):
            output_text = result.get('stdout', '')
            if output_text:
                self.ai_console.insert(tk.END, f"{output_text}\n")
        else:
            error_text = result.get('error', 'Unknown Error')
            self.ai_console.insert(tk.END, f"ERROR: {error_text}\n")
        self.ai_console.config(state='disabled')
        self.ai_console.see(tk.END)

    def log_to_terminal(self, message: str):
        self.terminal_output.config(state='normal')
        self.terminal_output.insert(tk.END, f"{message}\n")
        self.terminal_output.config(state='disabled')
        self.terminal_output.see(tk.END)

    def log_to_linter(self, message: str):
        self.linter_output.config(state='normal')
        self.linter_output.delete("1.0", tk.END)
        self.linter_output.insert(tk.END, message)
        self.linter_output.config(state='disabled')

    def run_linter_for_current_file(self):
        editor = self.get_current_editor()
        if not editor or not editor.file_path:
            show_message("Error", "Please open a file to lint.", 'error')
            return

        file_content = editor.get_content()
        lint_results = self.linter_manager.lint_code(file_content, editor.file_path)
        self.log_to_linter(lint_results)
        self.bottom_notebook.select(self.linter_frame)

    # --- Collaboration Logic ---
    def start_file_collaboration(self, file_path: str):
        """Initializes real-time collaboration for the given file."""
        collection_path = f"projects/{self.project_path}/files"
        doc_path = f"{collection_path}/{os.path.basename(file_path)}"

        # Set up a listener for file content changes
        self.firebase_manager.set_realtime_listener(
            doc_path,
            self.on_file_content_update
        )

    def on_file_content_update(self, data: Dict[str, Any]):
        """Callback for when a file's content is updated in Firestore."""
        # This is a simplified listener. A full implementation would handle
        # patches or diffs to prevent full rewrites.
        file_content = data.get('content', '')
        editor = self.get_current_editor()
        if editor and editor.get_content() != file_content:
            editor.set_content(file_content)

    def update_file_in_firestore(self, file_path: str, content: str):
        """Updates a file's content in Firestore."""
        doc_path = f"projects/{self.project_path}/files/{os.path.basename(file_path)}"
        data = {
            'content': content,
            'last_modified_by': self.firebase_manager.get_user_id(),
            'timestamp': firestore.SERVER_TIMESTAMP
        }
        self.firebase_manager.update_document(doc_path, data)

    # --- Settings Management ---
    def open_settings_dialog(self):
        """Opens the settings dialog window."""
        SettingsDialog(self)

    def on_close(self):
        """Handles application closing."""
        self.metrics_monitor.stop_monitoring()
        self.quit()
        self.destroy()

ockGit:
    """A mock class for Git operations."""
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.logger = print

    def init(self):
        self.logger(f"Git: Initializing repo at {self.repo_path}")

    def add(self, files: List[str]):
        self.logger(f"Git: Adding files: {files}")

    def commit(self, message: str):
        self.logger(f"Git: Committing with message: '{message}'")

    def status(self) -> str:
        return "On branch main\nYour branch is up to date with 'origin/main'."

# Mock classes for other components mentioned in the file
class Project:
    """Mock Project class for managing project structure."""
    def __init__(self, name: str, base_path: str):
        self.name = name
        self.path = os.path.join(base_path, name)
        self.config_file = os.path.join(self.path, '.devos_project.json')

    def create(self):
        """Creates the project directory and config file."""
        os.makedirs(self.path, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump({'name': self.name, 'created_at': time.time()}, f, indent=2)
        print(f"Project '{self.name}' created at {self.path}")

class SystemMonitor:
    """Mock SystemMonitor class to track system resources."""
    def __init__(self):
        self.metrics = {'cpu': [], 'memory': [], 'timestamps': []}
        self.is_monitoring = False
        self.monitor_thread = None

    def start_monitoring(self, interval: int = 1):
        """Start a thread to collect system metrics."""
        if self.is_monitoring:
            return
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("System monitoring started.")

    def stop_monitoring(self):
        """Stop the monitoring thread."""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("System monitoring stopped.")

    def _monitor_loop(self, interval):
        """The main monitoring loop."""
        while self.is_monitoring:
            try:
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                timestamp = time.strftime('%H:%M:%S')

                self.metrics['cpu'].append(cpu_percent)
                self.metrics['memory'].append(memory_percent)
                self.metrics['timestamps'].append(timestamp)

                # Keep a limited history
                if len(self.metrics['timestamps']) > 60:
                    for key in self.metrics:
                        self.metrics[key].pop(0)

                time.sleep(interval)
            except Exception as e:
                print(f"Monitoring failed: {e}")
                self.is_monitoring = False

# Main application class for the DevOS toolkit
class DevOSApp(tk.Tk):
    """The main application window and GUI."""
    def __init__(self):
        super().__init__()
        self.title("DevOS Toolkit")
        self.geometry("1200x800")
        self.style = ttk.Style(self)
        self.style.theme_use('clam')

        self.style.configure('TNotebook', background='#333', borderwidth=0)
        self.style.map('TNotebook.Tab', background=[('selected', '#555')], foreground=[('selected', '#fff')])
        self.style.configure('TFrame', background='#1E1E1E')
        self.style.configure('TLabel', background='#1E1E1E', foreground='#CCC')

        self.project = None
        self.system_monitor = SystemMonitor()

        self.create_widgets()
        self.create_tabs()

        self.system_monitor.start_monitoring()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_widgets(self):
        """Create the main GUI widgets."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    def create_tabs(self):
        """Create the tabs for the notebook."""
        self.tab_os_dev = ttk.Frame(self.notebook)
        self.tab_vm = ttk.Frame(self.notebook)
        self.tab_docker = ttk.Frame(self.notebook)
        self.tab_git = ttk.Frame(self.notebook)
        self.tab_monitor = ttk.Frame(self.notebook)
        self.tab_resources = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_os_dev, text="OS Development")
        self.notebook.add(self.tab_vm, text="VM Deployment")
        self.notebook.add(self.tab_docker, text="Docker & Containers")
        self.notebook.add(self.tab_git, text="Git Integration")
        self.notebook.add(self.tab_monitor, text="System Monitor")
        self.notebook.add(self.tab_resources, text="Resources")

        self.create_os_dev_tab()
        self.create_git_tab()
        self.create_monitor_tab()
        self.create_resources_tab()

    def create_os_dev_tab(self):
        """Create content for the OS Development tab."""
        label = ttk.Label(self.tab_os_dev, text="OS Development Tools", font=("Helvetica", 16, "bold"))
        label.pack(padx=20, pady=20)

        # We can add more widgets for kernel building, bootloaders, etc.
        # This is just a placeholder for now.

    def create_git_tab(self):
        """Create content for the Git Integration tab."""
        frame = ttk.Frame(self.tab_git, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(frame, text="Git Integration", font=("Helvetica", 16, "bold"))
        label.pack(pady=10)

        self.git_status_text = tk.Text(frame, height=10, bg="#2D2D2D", fg="#F8F8F2", insertbackground="#F8F8F2")
        self.git_status_text.pack(fill=tk.BOTH, expand=True, pady=10)
        self.git_status_text.insert(tk.END, "Git Status: No repository loaded.")

        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Init Repo", command=self.init_git_repo).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add All", command=self.add_all_git).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Commit", command=self.commit_git).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Status", command=self.update_git_status).pack(side=tk.LEFT, padx=5)

    def create_monitor_tab(self):
        """Create content for the System Monitor tab."""
        frame = ttk.Frame(self.tab_monitor, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(frame, text="System Resource Monitor", font=("Helvetica", 16, "bold"))
        label.pack(pady=10)

        self.monitor_label = ttk.Label(frame, text="Monitoring CPU and Memory...")
        self.monitor_label.pack(pady=10)

        self.after(1000, self.update_monitor_data)

    def update_monitor_data(self):
        """Update the system monitor labels with the latest data."""
        cpu = self.system_monitor.metrics['cpu'][-1] if self.system_monitor.metrics['cpu'] else 0
        mem = self.system_monitor.metrics['memory'][-1] if self.system_monitor.metrics['memory'] else 0

        self.monitor_label.config(text=f"CPU: {cpu:.2f}% | Memory: {mem:.2f}%")
        self.after(1000, self.update_monitor_data)

    def create_resources_tab(self):
        """Create content for the Resources tab."""
        label = ttk.Label(self.tab_resources, text="Resource Links and Templates", font=("Helvetica", 16, "bold"))
        label.pack(padx=20, pady=20)

        # We can add links to documentation, tools, etc. here.

    # Placeholder methods for Git integration
    def init_git_repo(self):
        if self.project:
            git = MockGit(self.project.path)
            git.init()
            self.update_git_status()
        else:
            print("No project loaded.")

    def add_all_git(self):
        if self.project:
            git = MockGit(self.project.path)
            git.add(['.'])
            self.update_git_status()
        else:
            print("No project loaded.")

    def commit_git(self):
        if self.project:
            # In a real app, we would open a dialog for the commit message
            commit_msg = "Initial commit"
            git = MockGit(self.project.path)
            git.commit(commit_msg)
            self.update_git_status()
        else:
            print("No project loaded.")

    def update_git_status(self):
        if self.project:
            git = MockGit(self.project.path)
            status = git.status()
            self.git_status_text.delete('1.0', tk.END)
            self.git_status_text.insert(tk.END, status)
        else:
            self.git_status_text.delete('1.0', tk.END)
            self.git_status_text.insert(tk.END, "Git Status: No project loaded.")

    def on_close(self):
        """Handle application close event."""
        self.system_monitor.stop_monitoring()
        self.destroy()

if __name__ == "__main__":
    app = DevOSApp()
    # For demonstration, let's create a mock project
    mock_project = Project("MyFirstOS", ".")
    mock_project.create()
    app.project = mock_project
    app.update_git_status()
    app.mainloop()
