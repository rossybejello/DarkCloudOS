# main.py
# This is the main entry point for the DevOS application.
# It has been updated to initialize the new, fully integrated DevOS class.

import tkinter as tk
import os
import sys

# Add the core directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core'))

# Import the new, fully integrated DevOS application class
from devos_app import DevOS

if __name__ == "__main__":
    app = DevOS()
    app.mainloop()

