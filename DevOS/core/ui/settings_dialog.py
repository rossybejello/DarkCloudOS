# ui/settings_dialog.py
# This component defines the settings dialog window.

import tkinter as tk
from tkinter import ttk, simpledialog, font

class SettingsDialog(tk.Toplevel):
    """
    A Toplevel window for managing application settings.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Preferences")
        self.geometry("400x300")
        self.transient(parent)  # Set the parent window
        self.grab_set()         # Make it modal

        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the settings dialog."""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Font settings
        ttk.Label(main_frame, text="Font Settings", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        # Font Name
        font_frame = ttk.Frame(main_frame)
        font_frame.pack(fill=tk.X, pady=5)
        ttk.Label(font_frame, text="Font:").pack(side=tk.LEFT, padx=(0, 5))
        self.font_names = sorted(list(font.families()))
        self.font_name_var = tk.StringVar(value=self.parent.font_name)
        self.font_name_combobox = ttk.Combobox(font_frame, textvariable=self.font_name_var, values=self.font_names, state="readonly")
        self.font_name_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Font Size
        size_frame = ttk.Frame(main_frame)
        size_frame.pack(fill=tk.X, pady=5)
        ttk.Label(size_frame, text="Size:").pack(side=tk.LEFT, padx=(0, 5))
        self.font_size_var = tk.StringVar(value=str(self.parent.font_size))
        self.font_size_spinbox = ttk.Spinbox(size_frame, from_=8, to=48, textvariable=self.font_size_var)
        self.font_size_spinbox.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Theme settings
        ttk.Label(main_frame, text="Theme", font=("Arial", 12, "bold")).pack(pady=(10, 5))

        theme_frame = ttk.Frame(main_frame)
        theme_frame.pack(fill=tk.X, pady=5)
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT, padx=(0, 5))
        self.theme_var = tk.StringVar(value=self.parent.theme)
        self.theme_radio_light = ttk.Radiobutton(theme_frame, text="Light", variable=self.theme_var, value="light")
        self.theme_radio_light.pack(side=tk.LEFT, padx=5)
        self.theme_radio_dark = ttk.Radiobutton(theme_frame, text="Dark", variable=self.theme_var, value="dark")
        self.theme_radio_dark.pack(side=tk.LEFT, padx=5)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="Save", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def save_settings(self):
        """Saves the settings and applies them to the main application."""
        new_font_name = self.font_name_var.get()
        new_font_size = int(self.font_size_spinbox.get())
        new_theme = self.theme_var.get()

        # Update main app's settings
        self.parent.font_name = new_font_name
        self.parent.font_size = new_font_size
        self.parent.theme = new_theme

        # Save settings to file
        self.parent.save_settings()

        # Re-apply settings to open editors
        for editor in self.parent.open_editors.values():
            editor.configure(font=(new_font_name, new_font_size))
            if new_theme == 'dark':
                editor.configure(bg="#2b2b2b", fg="#cccccc", insertbackground="white")
            else:
                editor.configure(bg="white", fg="black", insertbackground="black")

        self.destroy()

