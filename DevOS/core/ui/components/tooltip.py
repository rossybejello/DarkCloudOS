import tkinter as tk
import time

class Tooltip:
    _tooltips = {}
    
    @classmethod
    def register(cls, widget, text):
        """Register a widget with tooltip text"""
        widget_id = str(widget)
        cls._tooltips[widget_id] = text
        
        # Bind events
        widget.bind("<Enter>", cls._on_enter)
        widget.bind("<Leave>", cls._on_leave)
        widget.bind("<Motion>", cls._on_motion)
    
    @classmethod
    def _on_enter(cls, event):
        widget = event.widget
        widget_id = str(widget)
        if widget_id in cls._tooltips:
            cls._show_tooltip(widget, event.x_root, event.y_root)
    
    @classmethod
    def _on_leave(cls, event):
        cls._hide_tooltip()
    
    @classmethod
    def _on_motion(cls, event):
        if hasattr(cls, "_tooltip_window") and cls._tooltip_window:
            cls._tooltip_window.geometry(f"+{event.x_root+15}+{event.y_root+10}")
    
    @classmethod
    def _show_tooltip(cls, widget, x, y):
        # Destroy existing tooltip if any
        cls._hide_tooltip()
        
        # Create new tooltip
        cls._tooltip_window = tk.Toplevel(widget)
        cls._tooltip_window.wm_overrideredirect(True)
        cls._tooltip_window.wm_geometry(f"+{x+15}+{y+10}")
        
        label = tk.Label(
            cls._tooltip_window, 
            text=cls._tooltips[str(widget)],
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=5,
            pady=3
        )
        label.pack()
        
        # Schedule auto-dismiss
        cls._tooltip_window.after(5000, cls._hide_tooltip)
    
    @classmethod
    def _hide_tooltip(cls):
        if hasattr(cls, "_tooltip_window") and cls._tooltip_window:
            cls._tooltip_window.destroy()
            cls._tooltip_window = None