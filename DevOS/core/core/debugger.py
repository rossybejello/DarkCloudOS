import sys
import traceback
import logging
from bdb import Bdb
from io import StringIO

class Debugger(Bdb):
    BREAKPOINT_TYPES = ["line", "function", "conditional"]
    
    def __init__(self):
        super().__init__()
        self.breakpoints = {}
        self.logger = logging.getLogger('Debugger')
        self.output = StringIO()
        self.current_frame = None
        
    def set_breakpoint(self, file, line, condition=None):
        """Set a breakpoint at specific location"""
        self.set_break(file, line, condition)
        if file not in self.breakpoints:
            self.breakpoints[file] = []
        self.breakpoints[file].append(line)
        
    def remove_breakpoint(self, file, line):
        """Remove a breakpoint"""
        self.clear_break(file, line)
        if file in self.breakpoints and line in self.breakpoints[file]:
            self.breakpoints[file].remove(line)
            
    def execute(self, code, context=None):
        """Execute code in debugger"""
        self.output.truncate(0)
        self.output.seek(0)
        
        # Redirect stdout
        old_stdout = sys.stdout
        sys.stdout = self.output
        
        try:
            if context is None:
                context = {}
                
            # Create a wrapper function to capture the code
            wrapper_code = f"def __debug_wrapper__():\n{code}"
            exec(wrapper_code, context)
            
            # Start debugging
            self.run("context['__debug_wrapper__']()", context)
            
        except Exception as e:
            traceback.print_exc()
        finally:
            # Restore stdout
            sys.stdout = old_stdout
            
        return self.output.getvalue()
    
    def user_line(self, frame):
        """Called when we stop at a breakpoint or line"""
        self.current_frame = frame
        self.logger.info(f"Stopped at {frame.f_code.co_filename}:{frame.f_lineno}")
        
        # Print variables in scope
        for name, value in frame.f_locals.items():
            self.logger.debug(f"{name} = {repr(value)}")
            
        # Wait for user input (in a real UI, this would be interactive)
        self.set_step()
        
    def get_stack_trace(self):
        """Get current stack trace"""
        if not self.current_frame:
            return []
            
        frames = []
        frame = self.current_frame
        
        while frame:
            frames.append({
                "filename": frame.f_code.co_filename,
                "line": frame.f_lineno,
                "function": frame.f_code.co_name,
                "locals": {k: repr(v) for k, v in frame.f_locals.items()}
            })
            frame = frame.f_back
            
        return frames