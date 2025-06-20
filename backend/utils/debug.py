"""
Debug utility for handling debug prints throughout the application.
"""

from config.settings import DEBUG_MODE

class DebugManager:
    """Manages debug printing for the application."""
    
    def __init__(self):
        self._debug_enabled = DEBUG_MODE
    
    def is_enabled(self) -> bool:
        """Check if debug mode is enabled."""
        return self._debug_enabled
    
    def enable(self):
        """Enable debug mode."""
        self._debug_enabled = True
    
    def disable(self):
        """Disable debug mode."""
        self._debug_enabled = False
    
    def toggle(self) -> bool:
        """Toggle debug mode and return new state."""
        self._debug_enabled = not self._debug_enabled
        return self._debug_enabled
    
    def print(self, message: str, prefix: str = "DEBUG"):
        """Print debug message if debug mode is enabled."""
        if self._debug_enabled:
            print(f"{prefix}: {message}")
    
    def log_function_call(self, function_name: str, *args, **kwargs):
        """Log function call with arguments if debug mode is enabled."""
        if self._debug_enabled:
            args_str = ", ".join([str(arg) for arg in args])
            kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
            all_args = ", ".join(filter(None, [args_str, kwargs_str]))
            self.print(f"{function_name} called with: {all_args}")

# Global debug instance
debug = DebugManager()

# Convenience function for backward compatibility
def debug_print(message: str, prefix: str = "DEBUG"):
    """Convenience function for debug printing."""
    debug.print(message, prefix)
