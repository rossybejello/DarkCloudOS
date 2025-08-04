import customtkinter as ctk
import webbrowser
from modules.frameworks import FrameworkManager

class FrameworkFrame(ctk.CTkFrame):
    def __init__(self, parent, application):
        super().__init__(parent)
        self.app = application
        self.framework_manager = FrameworkManager()
        self.create_widgets()
        
    def create_widgets(self):
        notebook = ctk.CTkTabview(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # React/React Native Tab
        react_tab = notebook.add("React/React Native")
        self.create_react_panel(react_tab)
        
        # Flutter/Dart Tab
        flutter_tab = notebook.add("Flutter/Dart")
        self.create_flutter_panel(flutter_tab)
        
        # Jetpack Compose/Kotlin Tab
        compose_tab = notebook.add("Jetpack Compose")
        self.create_compose_panel(compose_tab)
        
    def create_react_panel(self, parent):
        # Resources section
        ctk.CTkLabel(parent, text="React Resources:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=5)
        
        resources = [
            ("React Documentation", "https://react.dev/learn"),
            ("React Native Docs", "https://reactnative.dev/docs/getting-started"),
            ("React Security Guide", "https://react-security.dev/")
        ]
        
        for text, url in resources:
            btn = ctk.CTkButton(
                parent, 
                text=text,
                command=lambda u=url: webbrowser.open(u),
                fg_color="transparent",
                border_width=1
            )
            btn.pack(fill="x", padx=20, pady=2)
            
        # Project tools
        ctk.CTkLabel(parent, text="Project Tools:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        
        btn_frame = ctk.CTkFrame(parent)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Create React App",
            command=self.create_react_app
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Run React Native (Android)",
            command=lambda: self.run_react_native("android")
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="Run React Native (iOS)",
            command=lambda: self.run_react_native("ios")
        ).pack(side="left", padx=5)
        
        # Progress tracking
        ctk.CTkLabel(parent, text="Development Progress:", font=("Arial", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        
        progress_frame = ctk.CTkFrame(parent)
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(progress_frame, text="Project Completion:").pack(side="left", padx=5)
        self.react_progress = ctk.CTkProgressBar(progress_frame, width=300)
        self.react_progress.pack(side="left", padx=5, fill="x", expand=True)
        self.react_progress.set(0.65)  # Example value
        
        ctk.CTkLabel(progress_frame, text="65%").pack(side="left", padx=5)
        
    def create_react_app(self):
        try:
            result = self.framework_manager.create_react_app()
            self.app.notifications.success("Project Created", "New React app created successfully")
        except Exception as e:
            self.app.error_handler.handle(e, "create_react_app")
            
    def run_react_native(self, platform):
        try:
            result = self.framework_manager.run_react_native(platform)
            self.app.notifications.info("Build Started", f"Building React Native app for {platform}")
        except Exception as e:
            self.app.error_handler.handle(e, "run_react_native")
    
    # Similar methods for Flutter and Compose...