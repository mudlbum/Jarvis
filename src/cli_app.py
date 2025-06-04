import logging # For potential basicConfig if run standalone
import mss
import pyautogui # For fallback screen capture and other GUI automation
import os # To ensure directory exists for saving screenshots
import cv2 # For image recognition (even if using pyautogui first)
import numpy # Dependency for opencv

# Import the application logger
try:
    from .app_logging import logger, setup_logger, get_log_file_path # Import setup_logger for standalone CLI
except ImportError:
    # Fallback if running cli_app.py directly and src is not in PYTHONPATH correctly
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__))) # Add src to path
    from app_logging import logger, setup_logger, get_log_file_path


# This is the main application file.
logger.info("CLI Application/Module Loaded.")

# --- Core Functions ---

def capture_screen(filename="screenshot.png"):
    logger.info("Attempting to capture full screen to %s", filename)
    """
    Captures the full screen and saves it to a file.
    Uses mss for speed, with a pyautogui fallback.
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with mss.mss() as sct:
            sct.shot(output=filename)
        logger.info("Screen captured to %s using mss.", filename)
        return True
    except mss.exception.ScreenShotError as e_mss: # Specific MSS error
        logger.warning("mss screen capture failed for %s: %s. Trying pyautogui fallback.", filename, e_mss, exc_info=False) # exc_info=False as it's an expected path
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            logger.info("Screen captured to %s using pyautogui (fallback).", filename)
            return True
        except pyautogui.PyAutoGUIException as e_pyautogui: # Specific PyAutoGUI error
            logger.error("PyAutoGUI screen capture fallback failed for %s: %s", filename, e_pyautogui, exc_info=True)
            return False
        except Exception as e_other_fallback: # Other errors during fallback
            logger.error("Other error during PyAutoGUI screen capture fallback for %s: %s", filename, e_other_fallback, exc_info=True)
            return False
    except OSError as e_os: # File system errors
        logger.error("OS error during full screen capture to %s: %s", filename, e_os, exc_info=True)
        return False
    except Exception as e_general: # Catch-all for truly unexpected errors
        logger.error("Unexpected general error during full screen capture to %s: %s", filename, e_general, exc_info=True)
        return False


def capture_region(x, y, width, height, filename="region.png"):
    logger.info("Attempting to capture region (x=%d, y=%d, w=%d, h=%d) to %s", x, y, width, height, filename)
    """
    Captures a specific region of the screen.
    Uses mss for speed, with a pyautogui fallback.
    """
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with mss.mss() as sct:
            monitor = {"top": y, "left": x, "width": width, "height": height}
            sct_img = sct.grab(monitor)
            mss.tools.to_png(sct_img.rgb, sct_img.size, output=filename)
        logger.info("Region (%d,%d,%d,%d) captured to %s using mss.", x, y, width, height, filename)
        return True
    except mss.exception.ScreenShotError as e_mss: # Specific MSS error
        logger.warning("mss region capture failed for %s: %s. Trying pyautogui fallback.", filename, e_mss, exc_info=False) # exc_info=False
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            screenshot.save(filename)
            logger.info("Region (%d,%d,%d,%d) captured to %s using pyautogui (fallback).", x, y, width, height, filename)
            return True
        except pyautogui.PyAutoGUIException as e_pyautogui: # Specific PyAutoGUI error
            logger.error("PyAutoGUI region capture fallback failed for %s: %s", filename, e_pyautogui, exc_info=True)
            return False
        except Exception as e_other_fallback: # Other errors during fallback
            logger.error("Other error during PyAutoGUI region capture fallback for %s: %s", filename, e_other_fallback, exc_info=True)
            return False
    except OSError as e_os: # File system errors
        logger.error("OS error during region capture to %s: %s", filename, e_os, exc_info=True)
        return False
    except Exception as e_general: # Catch-all for truly unexpected errors
        logger.error("Unexpected general error during region capture to %s: %s", filename, e_general, exc_info=True)
        return False

def find_image_on_screen(template_image_path, confidence=0.9, region=None):
    logger.info("Attempting to find image '%s' with confidence %.2f in region %s.",
                os.path.basename(template_image_path), confidence, region or "full screen")
    """
    Finds an image (template) on the screen.
    Uses pyautogui.locateOnScreen for simplicity in this PoC.
    It requires Pillow to be installed. For confidence < 1.0 or non-PNG/BMP
    template images, opencv-python is also required by pyautogui.

    Args:
        template_image_path (str): Path to the image file to find.
        confidence (float): The confidence level for matching (0.0 to 1.0).
        region (tuple, optional): A tuple (left, top, width, height) defining the
                                  search region. Defaults to None (full screen).

    Returns:
        tuple: (x, y, width, height) of the found image, or None.
    """
    if not os.path.exists(template_image_path): # FileNotFoundError could be raised by open() if not careful
        logger.error("Template image file not found at '%s'.", template_image_path)
        return None
    try:
        location = pyautogui.locateOnScreen(template_image_path, confidence=confidence, region=region)
        if location:
            search_area_msg = f"in region {region}" if region else "on full screen"
            logger.info("Image '%s' found %s at: (L:%d, T:%d, W:%d, H:%d) with confidence %.2f.",
                        os.path.basename(template_image_path), search_area_msg,
                        location.left, location.top, location.width, location.height, confidence)
            return location.left, location.top, location.width, location.height
        else:
            search_area_msg = f"in region {region}" if region else "on full screen"
            logger.info("Image '%s' not found %s with confidence %.2f.",
                        os.path.basename(template_image_path), search_area_msg, confidence)
            return None
    except pyautogui.PyAutoGUIException as e_pyautogui: # Specific PyAutoGUI operational error
        search_area_msg = f"in region {region}" if region else "on full screen"
        logger.error("PyAutoGUI error during image search for '%s' %s: %s.",
                        template_image_path, search_area_msg, e_pyautogui, exc_info=True) # Full stack for unexpected Lib errors
        return None
    except FileNotFoundError: # Should be caught by os.path.exists, but as safeguard for image loading within PyAutoGUI
        logger.error("Template image file disappeared or could not be opened by Pillow/OpenCV: '%s'.", template_image_path, exc_info=True)
        return None
    except Exception as e_general: # Catch-all for other unexpected errors (e.g. Pillow image format error)
        search_area_msg = f"in region {region}" if region else "on full screen"
        logger.error("Unexpected error during image search for '%s' %s: %s.",
                        template_image_path, search_area_msg, e_general, exc_info=True)
        return None

def move_mouse_to(x, y):
    """Moves the mouse cursor to the specified (x, y) coordinates."""
    logger.info("Moving mouse to X=%d, Y=%d.", x, y)
    try:
        pyautogui.moveTo(x, y, duration=0.25)
        logger.info("Mouse moved successfully to X=%d, Y=%d.", x, y)
    except pyautogui.PyAutoGUIException as e_pyautogui: # Specific PyAutoGUI error
        logger.error("PyAutoGUI error moving mouse to X=%d, Y=%d: %s.", x, y, e_pyautogui, exc_info=True)
    except Exception as e_general: # Catch-all
        logger.error("Unexpected error moving mouse to X=%d, Y=%d: %s.", x, y, e_general, exc_info=True)


def click_at(x, y, button='left'):
    """Moves the mouse to (x,y) and performs a click with the specified button."""
    logger.info("Attempting to click %s button at X=%d, Y=%d.", button, x, y)
    try:
        pyautogui.click(x, y, button=button)
        logger.info("Successfully clicked %s button at X=%d, Y=%d.", button, x, y)
    except pyautogui.PyAutoGUIException as e_pyautogui: # Specific PyAutoGUI error
        logger.error("PyAutoGUI error clicking %s button at X=%d, Y=%d: %s.", button, x, y, e_pyautogui, exc_info=True)
    except Exception as e_general: # Catch-all
        logger.error("Unexpected error clicking %s button at X=%d, Y=%d: %s.", button, x, y, e_general, exc_info=True)


def type_text(text_to_type):
    """Types the given string using the keyboard."""
    logger.info("Attempting to type text (length: %d). First 20 chars: '%s...'", len(text_to_type), text_to_type[:20])
    try:
        pyautogui.typewrite(text_to_type, interval=0.05)
        logger.info("Successfully typed text.")
    except pyautogui.PyAutoGUIException as e_pyautogui: # Specific PyAutoGUI error
        logger.error("PyAutoGUI error typing text: %s.", e_pyautogui, exc_info=True)
    except Exception as e_general: # Catch-all
        logger.error("Unexpected error typing text: %s.", e_general, exc_info=True)

# --- CLI Interaction ---

def display_menu():
    """Prints the main menu options to the console."""
    print("\n--- CLI Screen Interaction PoC ---")
    print("1. Capture full screen (saves to 'screenshots/')")
    print("2. Capture screen region (saves to 'screenshots/')")
    print("3. Find an image on screen (provide template path)")
    print("4. Move mouse and click (provide X, Y coords)")
    print("5. Type text (simulates keyboard input)")
    print("0. Exit")
    print("------------------------------------")

def _ensure_cli_logging_configured():
    """Ensure basic console logging if no handlers are configured for the root logger or our app logger."""
    # This is a simple check; more sophisticated checks might look at specific handlers.
    # The goal is to provide some output if only cli_app is run.
    # app_logging.logger should already have a file handler.
    # We add a console handler if one isn't present on THIS logger instance,
    # or if the root logger has no handlers (common in basic script runs).

    # Check if our specific logger has any handlers. If app_logging.py worked, it should.
    # If not, or if we want CLI to *also* print to console regardless of file logging:
    has_console_handler = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    if not logger.handlers or not has_console_handler: # If no handlers on our logger, or no console handler
        # If app_logging.py didn't set up (e.g. import error, or it only made a file handler)
        # or if we want to ensure CLI always prints to console.

        # Check if root logger has handlers. If not, basicConfig will set one.
        # If it does, we might not want to basicConfig.
        # For simplicity, if our logger has no console handler, add one.
        # This avoids double logging if root also gets a handler from elsewhere.
        if not has_console_handler:
            # Add a console handler to our specific logger
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s') # Simpler format for CLI
            ch.setFormatter(formatter)
            logger.addHandler(ch)
            # Set level for console output for CLI mode, could be different from file
            ch.setLevel(logging.INFO)
            logger.info("Added console handler for CLI mode as no console handler was found.")


if __name__ == "__main__":
    # When run as a script, ensure logger is set up (app_logging.py should do this)
    # and add a console handler for immediate feedback if needed.
    # setup_logger() # Call this if logger from app_logging might not be initialized
    _ensure_cli_logging_configured()

    logger.info("CLI Application started directly.")

    screenshots_dir = "screenshots"
    try:
        os.makedirs(screenshots_dir, exist_ok=True)
        logger.info("Ensured 'screenshots' directory exists at %s", os.path.abspath(screenshots_dir))
    except OSError as e:
        logger.error("Failed to create 'screenshots' directory at %s: %s", os.path.abspath(screenshots_dir), e)
        print(f"Error: Could not create screenshots directory: {e}. Screenshots might fail to save.")


    while True:
        display_menu()
        choice = input("Enter your choice (0-5): ")
        logger.info("CLI Main Menu: User choice: %s", choice)

        if choice == '1':
            default_filename = os.path.join(screenshots_dir, "fullscreen.png")
            filename_input = input(f"Enter filename (default: {default_filename}): ")
            filename = filename_input if filename_input else default_filename
            if os.path.dirname(filename) == "" or os.path.dirname(filename) == ".": # if only basename is given
                filename = os.path.join(screenshots_dir, os.path.basename(filename))
            logger.info("CLI Option 1: Capture Full Screen. Filename: %s", filename)
            capture_screen(filename)

        elif choice == '2':
            try:
                print("Enter details for the screen region to capture:")
                x_str = input("  Enter X coordinate (top-left): ")
                y_str = input("  Enter Y coordinate (top-left): ")
                w_str = input("  Enter width of region: ")
                h_str = input("  Enter height of region: ")
                x, y, width, height = int(x_str), int(y_str), int(w_str), int(h_str)

                default_filename = os.path.join(screenshots_dir, "region.png")
                filename_input = input(f"  Enter filename (default: {default_filename}): ")
                filename = filename_input if filename_input else default_filename
                if os.path.dirname(filename) == "" or os.path.dirname(filename) == ".":
                    filename = os.path.join(screenshots_dir, os.path.basename(filename))

                logger.info("CLI Option 2: Capture Region. X=%d, Y=%d, W=%d, H=%d, Filename: %s", x, y, width, height, filename)
                capture_region(x, y, width, height, filename)
            except ValueError:
                logger.warning("Invalid input for region capture coordinates/dimensions.", exc_info=True)
                print("Invalid input. Coordinates, width, and height must be integers.")
            except Exception as e:
                logger.error("Error during CLI region capture: %s", e, exc_info=True)
                print(f"An error occurred during region capture: {e}")

        elif choice == '3':
            template_path = input("Enter path to the template image file (e.g., 'template.png'): ")
            confidence_str = input("Enter confidence level (0.0 to 1.0, press Enter for 0.9): ")
            confidence_val = 0.9
            if confidence_str:
                try:
                    parsed_conf = float(confidence_str)
                    if 0.0 <= parsed_conf <= 1.0:
                        confidence_val = parsed_conf
                    else:
                        print(f"Confidence out of range (0.0-1.0). Using default {confidence_val}.")
                except ValueError:
                    print(f"Invalid confidence value. Using default {confidence_val}.")

            logger.info("CLI Option 3: Find Image. Template: %s, Confidence: %.2f", template_path, confidence_val)
            result = find_image_on_screen(template_path, confidence=confidence_val, region=None)
            if result:
                print(f"Image found by CLI: X={result[0]}, Y={result[1]}, W={result[2]}, H={result[3]}")
            else:
                print("Image not found by CLI.")


        elif choice == '4':
            try:
                print("Enter coordinates to move the mouse to and click:")
                x_str = input("  Enter X coordinate: ")
                y_str = input("  Enter Y coordinate: ")
                x, y = int(x_str), int(y_str)

                button_choice = input("  Enter mouse button ('left', 'right', 'middle', press Enter for 'left'): ").strip().lower()
                if not button_choice: button_choice = 'left'
                if button_choice not in ['left', 'right', 'middle']:
                    print("Invalid button specified. Defaulting to 'left' click.")
                    button_choice = 'left'

                logger.info("CLI Option 4: Move & Click. X=%d, Y=%d, Button: %s", x, y, button_choice)
                click_at(x, y, button=button_choice)
            except ValueError:
                logger.warning("Invalid input for click coordinates.", exc_info=True)
                print("Invalid input. Coordinates must be integers.")
            except Exception as e:
                logger.error("Error during CLI click operation: %s", e, exc_info=True)
                print(f"An error occurred during mouse operation: {e}")

        elif choice == '5':
            text_to_type = input("Enter the text you want to type: ")
            if text_to_type:
                logger.info("CLI Option 5: Type Text. Text length: %d", len(text_to_type))
                # print(f"Typing: '{text_to_type}'...") # Replaced by logger in function
                type_text(text_to_type)
            else:
                logger.info("CLI Option 5: Type Text. No text provided.")
                print("No text provided to type.")

        elif choice == '0':
            logger.info("CLI Main Menu: User chose to exit.")
            print("Exiting application. Goodbye!")
            break

        else:
            logger.warning("CLI Main Menu: Invalid choice: %s", choice)
            print("Invalid choice. Please enter a number from the menu (0-5).")
