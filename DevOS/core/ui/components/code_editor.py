import tkinter as tk
import customtkinter as ctk
from tkinter import scrolledtext
import pygments
import pygments.lexers
import pygments.styles
from pygments import lex
from pygments.token import Token
from pygments.util import ClassNotFound

class CodeEditor(ctk.CTkFrame):
    LEXERS = {
        "python": pygments.lexers.PythonLexer,
        "javascript": pygments.lexers.JavascriptLexer,
        "c": pygments.lexers.CLexer,
        "cpp": pygments.lexers.CppLexer,
        "java": pygments.lexers.JavaLexer,
        "html": pygments.lexers.HtmlLexer,
        "css": pygments.lexers.CssLexer,
        "yaml": pygments.lexers.YamlLexer,
        "json": pygments.lexers.JsonLexer,
        "markdown": pygments.lexers.MarkdownLexer,
        "docker": pygments.lexers.DockerLexer,
        "make": pygments.lexers.MakefileLexer,
        "bash": pygments.lexers.BashLexer
    }
    
    def __init__(self, parent, application):
        super().__init__(parent)
        self.app = application
        self.file_path = None
        self.language = "text"
        self.create_widgets()
        
    def create_widgets(self):
        # Toolbar
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        self.language_var = ctk.StringVar(value="text")
        language_menu = ctk.CTkComboBox(
            toolbar, 
            variable=self.language_var,
            values=list(self.LEXERS.keys()),
            command=self.set_language
        )
        language_menu.pack(side="left", padx=5)
        
        save_btn = ctk.CTkButton(toolbar, text="Save", command=self.save_file)
        save_btn.pack(side="right", padx=5)
        
        # Editor area
        self.editor = scrolledtext.ScrolledText(
            self, 
            wrap=tk.WORD, 
            font=("Consolas", 12),
            undo=True
        )
        self.editor.pack(fill="both", expand=True, padx=5, pady=5)
        self.editor.bind("<KeyRelease>", self.highlight_syntax)
        
    def open_file(self, file_path):
        """Open a file in the editor"""
        try:
            with open(file_path, "r") as f:
                content = f.read()
                self.editor.delete(1.0, tk.END)
                self.editor.insert(tk.END, content)
                
            self.file_path = file_path
            self.detect_language(file_path)
            self.highlight_syntax()
            return True
        except Exception as e:
            self.app.error_handler.handle(e, "open_file")
            return False
            
    def save_file(self):
        """Save current file"""
        if not self.file_path:
            return False
            
        try:
            content = self.editor.get(1.0, tk.END)
            with open(self.file_path, "w") as f:
                f.write(content)
                
            self.app.notifications.success("File Saved", f"Saved {self.file_path}")
            return True
        except Exception as e:
            self.app.error_handler.handle(e, "save_file")
            return False
            
    def detect_language(self, file_path):
        """Detect programming language from file extension"""
        ext = os.path.splitext(file_path)[1][1:].lower()
        self.language = ext if ext in self.LEXERS else "text"
        self.language_var.set(self.language)
        
    def set_language(self, choice):
        """Set programming language manually"""
        self.language = choice
        self.highlight_syntax()
        
    def highlight_syntax(self, event=None):
        """Apply syntax highlighting"""
        if self.language == "text":
            return
            
        try:
            lexer = self.LEXERS[self.language]()
        except (KeyError, ClassNotFound):
            return
            
        # Remove previous tags
        for tag in self.editor.tag_names():
            self.editor.tag_remove(tag, "1.0", "end")
            
        # Get text and lex it
        text = self.editor.get("1.0", "end-1c")
        pos = 0
        
        # Apply highlighting
        for token, value in lex(text, lexer):
            start = f"1.0 + {pos}c"
            end = f"1.0 + {pos + len(value)}c"
            
            # Get style for token
            style = pygments.styles.get_style_by_name("default")
            color = style.style_for_token(token)["color"]
            
            if color:
                # Convert #rrggbb to Tkinter color
                color = f"#{color}"
                tag_name = str(token).replace(".", "_")
                
                # Create tag if doesn't exist
                if not self.editor.tag_cget(tag_name, "foreground"):
                    self.editor.tag_configure(tag_name, foreground=color)
                
                # Apply tag
                self.editor.tag_add(tag_name, start, end)
                
            pos += len(value)