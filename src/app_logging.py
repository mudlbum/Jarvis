import logging
import os
import sys

LOG_FILENAME = "screen_automator.log"

def get_log_file_path():
    """Determines the path for the log file."""
    # If running as a PyInstaller bundle, sys._MEIPASS might be set
    # and we'd want the log file next to the executable.
    if hasattr(sys, '_MEIPASS'):
        # For a bundled app, place log in the directory of the executable
        return os.path.join(os.path.dirname(sys.executable), LOG_FILENAME)
    else:
        # For source code execution, place log in the 'src' directory or project root.
        # Let's choose project root for easier access during development.
        # Assuming this file (app_logging.py) is in src/
        project_root = os.path.dirname(os.path.abspath(__file__)) # This gives src/
        project_root = os.path.dirname(project_root) # This gives project root /app
        return os.path.join(project_root, LOG_FILENAME)

def setup_logger(logger_name="ScreenAutomator", level=logging.INFO):
    """Sets up a logger instance."""
    logger = logging.getLogger(logger_name)

    # Prevent adding multiple handlers if setup_logger is called multiple times
    if logger.hasHandlers():
        logger.handlers.clear() # Or just return logger if already configured

    logger.setLevel(level)

    log_path = get_log_file_path()

    # File Handler
    fh = logging.FileHandler(log_path)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Optional: Console Handler (for development or if CLI needs immediate console output)
    # ch = logging.StreamHandler()
    # ch.setFormatter(formatter)
    # logger.addHandler(ch)

    logger.info(f"Logger '{logger_name}' initialized. Logging to: {log_path}")
    return logger

# Initialize and get the main logger instance for the application
# This can be imported by other modules.
logger = setup_logger()

if __name__ == '__main__':
    # Example usage:
    logger.info("Logging setup complete (test message from app_logging.py).")
    logger.warning("This is a test warning.")
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("Test exception occurred.")
