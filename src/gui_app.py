import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os # For os.path.basename, os.makedirs
from PIL import Image, ImageTk # For RegionSelector screenshot display

# Application logging setup
try:
    from .app_logging import logger
except ImportError:
    # Fallback if running gui_app.py directly and src is not in PYTHONPATH correctly
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__))) # Add src to path
    from app_logging import logger


# Attempt to import functions from cli_app
try:
    # Relative import for when gui_app is part of a package structure (e.g., running as module)
    from . import cli_app
except ImportError:
    # Direct import for standalone execution or if 'src' is in PYTHONPATH
    import cli_app

class ScreenInteractionGUI:
    """Main class for the Screen Interaction GUI application."""
    def __init__(self, master: tk.Tk):
        """
        Initializes the GUI application.
        Sets up the main window, frames, widgets, and variables.
        """
        self.master = master
        master.title("Screen Interaction GUI")
        master.geometry("550x500") # Adjusted size for better spacing

        # --- Variables ---
        self.status_var = tk.StringVar()
        self.status_var.set("Status: Ready. Select an action.")
        logger.info("ScreenInteractionGUI initialized.") # Log GUI initialization
        self.template_path_var = tk.StringVar()
        self.selected_region_var = tk.StringVar() # For displaying selected region
        self.selected_region_var.set("None (Full Screen)")
        self.search_region = None # Stores (x,y,w,h)
        self.confidence_var = tk.DoubleVar(value=0.9) # For confidence scale
        self.mouse_x_var = tk.StringVar()
        self.mouse_y_var = tk.StringVar()
        self.type_text_var = tk.StringVar()

        # --- Style ---
        # Using ttk for themed widgets, which generally look better.
        # style = ttk.Style()
        # style.theme_use('clam') # Example: 'clam', 'alt', 'default', 'classic'
        master.geometry("600x650") # Increased window size for new elements


        # --- Main Frame ---
        # This frame will hold all other sections.
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True) # Fill entire window and allow expansion

        # --- Section 1: Screen Capture ---
        capture_frame = ttk.LabelFrame(main_frame, text="Screen Capture", padding="10")
        capture_frame.pack(fill=tk.X, pady=(0, 10)) # Fill horizontally, add padding below

        self.capture_full_btn = ttk.Button(capture_frame, text="Capture Full Screen & Save As...", command=self.handle_capture_full_screen)
        self.capture_full_btn.pack(pady=5, fill=tk.X, expand=True)

        # Note: Capturing a specific region via GUI is more complex as it requires
        # either input fields for coordinates or a screen overlay, so omitted for this PoC.

        # --- Section 2: Image Recognition ---
        image_rec_frame = ttk.LabelFrame(main_frame, text="Image Recognition", padding="10")
        image_rec_frame.pack(fill=tk.X, pady=10)

        # Template image path display and selection
        path_frame = ttk.Frame(image_rec_frame)
        path_frame.pack(fill=tk.X, pady=(0,5))
        ttk.Label(path_frame, text="Template Image:").pack(side=tk.LEFT, padx=(0,5))
        self.template_entry = ttk.Entry(path_frame, textvariable=self.template_path_var, width=30, state="readonly")
        self.template_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.browse_btn = ttk.Button(path_frame, text="Browse...", command=self.handle_browse_template)
        self.browse_btn.pack(side=tk.LEFT, padx=(5,0))

        # Region Selection
        region_frame = ttk.Frame(image_rec_frame)
        region_frame.pack(fill=tk.X, pady=5)
        self.select_region_btn = ttk.Button(region_frame, text="Select Search Region", command=self.handle_select_search_region)
        self.select_region_btn.pack(side=tk.LEFT, padx=(0,5), fill=tk.X, expand=True)
        self.clear_region_btn = ttk.Button(region_frame, text="Clear Region", command=self.handle_clear_search_region)
        self.clear_region_btn.pack(side=tk.LEFT, padx=(5,0))

        region_display_frame = ttk.Frame(image_rec_frame)
        region_display_frame.pack(fill=tk.X, pady=(0,5))
        ttk.Label(region_display_frame, text="Selected Region:").pack(side=tk.LEFT, padx=(0,5))
        self.region_label = ttk.Label(region_display_frame, textvariable=self.selected_region_var)
        self.region_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Confidence Scale
        confidence_frame = ttk.Frame(image_rec_frame)
        confidence_frame.pack(fill=tk.X, pady=5)
        ttk.Label(confidence_frame, text="Confidence:").pack(side=tk.LEFT, padx=(0,5))
        self.confidence_scale = ttk.Scale(
            confidence_frame,
            from_=0.5,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.confidence_var,
            command=lambda s: self.confidence_var.set(round(float(s), 2)) # Show 2 decimal places
        )
        self.confidence_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.confidence_value_label = ttk.Label(confidence_frame, textvariable=self.confidence_var, width=4)
        self.confidence_value_label.pack(side=tk.LEFT)
        self.confidence_var.trace_add("write", self._update_confidence_label_text)


        self.find_image_btn = ttk.Button(image_rec_frame, text="Find Image on Screen", command=self.handle_find_image)
        self.find_image_btn.pack(pady=(10,0), fill=tk.X, expand=True)

        # --- Section 3: Mouse Control ---
        mouse_frame = ttk.LabelFrame(main_frame, text="Mouse Control (Click at Coordinates)", padding="10")
        mouse_frame.pack(fill=tk.X, pady=10)

        coords_frame = ttk.Frame(mouse_frame)
        coords_frame.pack(fill=tk.X)

        ttk.Label(coords_frame, text="X:").pack(side=tk.LEFT, padx=(0,5))
        self.mouse_x_entry = ttk.Entry(coords_frame, textvariable=self.mouse_x_var, width=8)
        self.mouse_x_entry.pack(side=tk.LEFT, padx=(0,10))

        ttk.Label(coords_frame, text="Y:").pack(side=tk.LEFT, padx=(0,5))
        self.mouse_y_entry = ttk.Entry(coords_frame, textvariable=self.mouse_y_var, width=8)
        self.mouse_y_entry.pack(side=tk.LEFT, padx=(0,10))

        self.click_btn = ttk.Button(mouse_frame, text="Move & Click (Left Button)", command=self.handle_click_at)
        self.click_btn.pack(pady=(10,0), fill=tk.X, expand=True)

        # --- Section 4: Keyboard Control ---
        keyboard_frame = ttk.LabelFrame(main_frame, text="Keyboard Control", padding="10")
        keyboard_frame.pack(fill=tk.X, pady=10)

        text_entry_frame = ttk.Frame(keyboard_frame)
        text_entry_frame.pack(fill=tk.X)
        ttk.Label(text_entry_frame, text="Text to Type:").pack(side=tk.LEFT, padx=(0,5))
        self.type_text_entry = ttk.Entry(text_entry_frame, textvariable=self.type_text_var, width=30)
        self.type_text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.type_btn = ttk.Button(keyboard_frame, text="Type Text", command=self.handle_type_text)
        self.type_btn.pack(pady=(10,0), fill=tk.X, expand=True)

        # --- Status Bar ---
        # Positioned at the bottom of the master window.
        status_bar = ttk.Label(master, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding="5")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # --- Event Handlers ---
    def _update_confidence_label_text(self, *args):
        """Updates the confidence value label next to the scale."""
        # This ensures the label always shows the rounded value from the scale.
        # self.confidence_value_label.config(text=f"{self.confidence_var.get():.2f}") # Original approach
        # Alternative: directly set the string var if the label uses it, or format here.
        current_val = self.confidence_var.get()
        self.confidence_value_label.config(text=f"{current_val:.2f}")


    def handle_capture_full_screen(self):
        """Handles the 'Capture Full Screen & Save As...' button click."""
        logger.info("Attempting to capture full screen.")
        self.status_var.set("Status: Initiating screen capture...")
        self.master.update_idletasks() # Ensure GUI updates before potentially blocking file dialog

        # Ensure screenshots directory exists
        screenshots_dir = "screenshots"
        try:
            os.makedirs(screenshots_dir, exist_ok=True)
        except OSError as e: # More specific exception
            logger.exception("Error creating screenshots directory %s:", screenshots_dir)
            messagebox.showerror("Directory Creation Error", f"Could not create directory for screenshots at '{screenshots_dir}'.\n\nDetails: {e}\n\nPlease ensure you have permissions to write to this location.")
            self.status_var.set(f"Status: Error creating '{screenshots_dir}' directory.")
            return

        filename = filedialog.asksaveasfilename(
            initialdir=screenshots_dir,
            title="Save Full Screen Screenshot As",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")] # Common image formats
        )
        if filename: # If a filename was provided (dialog not cancelled)
            self.status_var.set(f"Status: Capturing to {os.path.basename(filename)}...")
            self.master.update_idletasks()
            try:
                if cli_app.capture_screen(filename):
                    logger.info("Screen captured successfully to %s", filename)
                    messagebox.showinfo("Success", f"Screen captured and saved to:\n{filename}")
                    self.status_var.set(f"Status: Screen captured to {os.path.basename(filename)}")
                else:
                    # cli_app.capture_screen logs its own errors
                    logger.warning("cli_app.capture_screen reported failure for %s. See logs.", filename)
                    messagebox.showerror("Screen Capture Failed", "The screen capture process failed. Please check the application logs (screen_automator.log) for more details.")
                    self.status_var.set("Status: Screen capture failed.")
            except Exception as e: # Catch any other unexpected error during the process
                logger.exception("Unexpected error during screen capture for %s:", filename)
                messagebox.showerror("Unexpected Capture Error", f"An unexpected error occurred during screen capture:\n{e}\n\nPlease check logs.")
                self.status_var.set("Status: Screen capture error.")
        else:
            logger.info("Screen capture cancelled by user.")
            self.status_var.set("Status: Screen capture cancelled by user.")

    def handle_browse_template(self):
        """Handles the 'Browse...' button click to select a template image."""
        logger.info("Browsing for template image.")
        self.status_var.set("Status: Browsing for template image...")
        filepath = filedialog.askopenfilename(
            title="Select Template Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")]
        )
        if filepath: # If a file was selected
            logger.info("Template image selected: %s", filepath)
            self.template_path_var.set(filepath)
            self.status_var.set(f"Status: Template image selected: {os.path.basename(filepath)}")
        else:
            logger.info("Template image selection cancelled.")
            self.status_var.set("Status: Template image selection cancelled.")

    def handle_find_image(self):
        """Handles the 'Find Image on Screen' button click."""
        template_path = self.template_path_var.get()
        if not template_path:
            logger.warning("Find image action initiated but no template path provided.")
            messagebox.showwarning("Template Image Required", "Please select a template image first using the 'Browse...' button.") # More specific title
            self.status_var.set("Status: Find image cancelled - no template selected.")
            return

        confidence = self.confidence_var.get()
        region_to_search = self.search_region
        logger.info("Attempting to find image '%s' with confidence %.2f in region %s",
                    os.path.basename(template_path), confidence, region_to_search or "full screen")

        self.status_var.set(f"Status: Searching for '{os.path.basename(template_path)}' on screen...")
        self.master.update_idletasks() # Refresh GUI before potentially blocking operation

        try:
            # Get confidence from the scale
            # Get region from stored variable (self.search_region)

            result = cli_app.find_image_on_screen(template_path, confidence=confidence, region=region_to_search)

            if result:
                coords_str = f"X={result[0]}, Y={result[1]}, W={result[2]}, H={result[3]}"
                area_msg = f"in region {region_to_search}" if region_to_search else "on full screen"
                logger.info("Image '%s' found %s at %s with confidence %.2f",
                            os.path.basename(template_path), area_msg, coords_str, confidence)
                messagebox.showinfo("Image Found", f"Image '{os.path.basename(template_path)}' found {area_msg} at:\n{coords_str}\n(Confidence: {confidence:.2f})")
                self.status_var.set(f"Status: Image found: {coords_str} {area_msg}")
            else:
                # cli_app.find_image_on_screen logs its own "not found"
                logger.warning("Image '%s' not found %s with confidence %.2f",
                             os.path.basename(template_path),
                             f"in region {region_to_search}" if region_to_search else "on full screen",
                             confidence)
                messagebox.showwarning("Image Not Found", f"Image '{os.path.basename(template_path)}' was not found {f'in region {region_to_search}' if region_to_search else 'on full screen'}.\n(Using confidence: {confidence:.2f})\n\nTry adjusting confidence or selecting a different region/template.")
                self.status_var.set(f"Status: Image '{os.path.basename(template_path)}' not found {f'in region {region_to_search}' if region_to_search else 'on full screen'}.")
        except pyautogui.PyAutoGUIException as pae: # Specific exception from pyautogui
            logger.exception("PyAutoGUI error during find_image_on_screen for '%s':", template_path)
            messagebox.showerror("Image Search Operation Error", f"A PyAutoGUI error occurred while searching for the image:\n'{pae}'\n\nThis might be due to screen access issues or invalid image format. Check logs.")
            self.status_var.set("Status: PyAutoGUI error during image search.")
        except Exception as e: # Catch any other unexpected error
            logger.exception("Unexpected error during find_image_on_screen for '%s':", template_path)
            messagebox.showerror("Unexpected Find Image Error", f"An unexpected error occurred while searching for the image:\n{e}\n\nPlease check logs.")
            self.status_var.set("Status: Unexpected error during image search.")

    def handle_select_search_region(self):
        """Handles the 'Select Search Region' button click."""
        logger.info("Initiating screen region selection.")
        self.status_var.set("Status: Opening region selector... Main window will be hidden.")
        self.master.withdraw()

        try:
            # Pass self.master as the parent for the Toplevel window
            selector_window = RegionSelector(self.master, self.set_search_region_callback, self.status_var)
        except Exception as e:
            logger.exception("Failed to create or run RegionSelector window.")
            messagebox.showerror("Region Selector Error", f"Could not open region selector:\n{e}\n\nPlease check logs.")
            # Ensure main window is restored if RegionSelector fails to init
            if not self.master.winfo_viewable():
                 self.master.deiconify()
            self.master.lift()
            self.master.focus_force()
            self.status_var.set("Status: Failed to open region selector.")


    def set_search_region_callback(self, region_coords):
        """Callback function for the RegionSelector to set the selected region."""
        self.master.deiconify() # Ensure main window is shown
        if region_coords:
            self.search_region = region_coords
            self.selected_region_var.set(f"X:{region_coords[0]}, Y:{region_coords[1]}, W:{region_coords[2]}, H:{region_coords[3]}")
            logger.info("Search region selected: %s", region_coords)
            self.status_var.set("Status: Search region selected.")
        else:
            logger.info("Region selection cancelled or no valid region provided by RegionSelector.")
            # self.search_region = None # Optionally keep old region or clear it
            # self.selected_region_var.set("None (Full Screen)") # Optionally update display
            self.status_var.set("Status: Region selection cancelled or window closed.")

        # Ensure main window is brought to front and focused
        self.master.lift()
        self.master.focus_force()


    def handle_clear_search_region(self):
        """Clears the selected search region."""
        logger.info("Search region cleared by user.")
        self.search_region = None
        self.selected_region_var.set("None (Full Screen)")
        self.status_var.set("Status: Search region cleared. Will search full screen.")


    def handle_click_at(self):
        """Handles the 'Move & Click' button click."""
        x_str = self.mouse_x_var.get()
        y_str = self.mouse_y_var.get()

        if not x_str or not y_str:
            logger.warning("Click action initiated but coordinates missing.")
            messagebox.showwarning("Coordinates Required", "Please enter both X and Y coordinates for the click action.")
            self.status_var.set("Status: Click cancelled - coordinates missing.")
            return

        try:
            x = int(x_str)
            y = int(y_str)
            logger.info("Attempting to click at coordinates X=%d, Y=%d", x, y)

            self.status_var.set(f"Status: Attempting to click at ({x},{y})...")
            self.master.update_idletasks()

            cli_app.click_at(x, y)
            logger.info("Successfully clicked at X=%d, Y=%d", x, y)
            messagebox.showinfo("Click Successful", f"Successfully clicked at ({x}, {y}).")
            self.status_var.set(f"Status: Clicked at ({x},{y}).")
        except ValueError: # Specific error for int conversion
            logger.warning("Invalid coordinates for click: X='%s', Y='%s'. Must be integers.", x_str, y_str, exc_info=True)
            messagebox.showerror("Invalid Coordinates", "X and Y coordinates must be valid integers.")
            self.status_var.set("Status: Click failed - invalid coordinates.")
        except pyautogui.PyAutoGUIException as pae: # Specific error from pyautogui
            logger.exception("PyAutoGUI error during click at X=%s, Y=%s:", x_str, y_str)
            messagebox.showerror("Mouse Click Operation Error", f"A PyAutoGUI error occurred during the click operation:\n'{pae}'\n\nThis might be due to screen access or control issues. Check logs.")
            self.status_var.set(f"Status: Click operation failed (PyAutoGUI error).")
        except Exception as e: # Catch any other unexpected error
            logger.exception("Unexpected error during click at X=%s, Y=%s:", x_str, y_str)
            messagebox.showerror("Unexpected Click Error", f"An unexpected error occurred during the click operation:\n{e}\n\nPlease check logs.")
            self.status_var.set(f"Status: Click operation failed (unexpected error).")


    def handle_type_text(self):
        """Handles the 'Type Text' button click."""
        text_to_type = self.type_text_var.get()
        if not text_to_type:
            logger.warning("Type text action initiated but no text provided.")
            messagebox.showwarning("Text Required", "Please enter some text to type in the input field.")
            self.status_var.set("Status: Type text cancelled - no text provided.")
            return

        logger.info("Preparing to type text. Length: %d. Text preview: '%s...'", len(text_to_type), text_to_type[:20])
        self.status_var.set(f"Status: Preparing to type. Switch to target window if needed...")

        # Countdown and then type
        self.master.after(1000, lambda: self.status_var.set("Status: Typing in 3..."))
        self.master.after(2000, lambda: self.status_var.set("Status: Typing in 2..."))
        self.master.after(3000, lambda: self.status_var.set("Status: Typing in 1..."))
        self.master.after(4000, lambda: self._execute_typing(text_to_type))

    def _execute_typing(self, text_to_type: str):
        """Executes the typing action after a delay."""
        logger.info("Executing typing action for text: '%s...'", text_to_type[:20])
        self.status_var.set(f"Status: Typing '{text_to_type[:20]}...'")
        self.master.update_idletasks()
        try:
            cli_app.type_text(text_to_type)
            logger.info("Successfully typed text.")
            messagebox.showinfo("Typing Successful", f"Successfully typed:\n'{text_to_type}'")
            self.status_var.set(f"Status: Text typed successfully.")
        except pyautogui.PyAutoGUIException as pae: # Specific error from pyautogui
            logger.exception("PyAutoGUI error during typing:")
            messagebox.showerror("Typing Operation Error", f"A PyAutoGUI error occurred during typing:\n'{pae}'\n\nThis might be due to input control issues. Check logs.")
            self.status_var.set(f"Status: Typing failed (PyAutoGUI error).")
        except Exception as e: # Catch any other unexpected error
            logger.exception("Unexpected error during typing:")
            messagebox.showerror("Unexpected Typing Error", f"An unexpected error occurred while typing:\n{e}\n\nPlease check logs.")
            self.status_var.set(f"Status: Typing failed (unexpected error).")


def main():
    """Sets up and runs the Tkinter GUI application."""
    logger.info("Application starting via main() function.")

    try:
        # Basic check for cli_app import and a key function
        if not hasattr(cli_app, 'capture_screen'):
            raise ImportError("cli_app is missing 'capture_screen' function or not imported.")
    except NameError: # cli_app module itself not found
        logger.critical("Fatal Error: cli_app module (cli_app.py) not found or not imported. Application cannot start.")
        # Tkinter might not be fully initialized here for a messagebox, try print as fallback
        print("FATAL ERROR: cli_app.py not found. Cannot start GUI.")
        messagebox.showerror(
            "Fatal Error: Core Module Missing",
            "The core logic module (cli_app.py) could not be imported. "
            "Please ensure 'cli_app.py' is in the 'src' directory or accessible in PYTHONPATH."
        )
        return
    except ImportError as e: # Other import-related issues within cli_app or its dependencies
        logger.critical("Fatal Error: cli_app module is incomplete or has critical import issues: %s", e, exc_info=True)
        print(f"FATAL ERROR: cli_app.py incomplete or error during its import: {e}. Cannot start GUI.")
        messagebox.showerror(
            "Fatal Error: Core Module Error",
            f"The core logic module (cli_app.py) is incomplete or has issues:\n{e}\n"
            "Please check logs and ensure all dependencies are correctly installed."
        )
        return

    try:
        root = tk.Tk()
        app = ScreenInteractionGUI(root)
        logger.info("Tkinter root window created and ScreenInteractionGUI instantiated successfully.")
        root.mainloop()
    except tk.TclError as tcle:
        logger.critical("Fatal Tkinter Error: %s. Application cannot start or continue.", tcle, exc_info=True)
        # This error often means display environment is not available (e.g. running in a headless environment)
        print(f"FATAL TKINTER ERROR: {tcle}. Could not start GUI. Ensure a display environment is available.")
        # Optionally, show a simple messagebox if possible, but Tk might be too broken.
    except Exception as e:
        logger.critical("Fatal error during GUI application setup or mainloop: %s", e, exc_info=True)
        print(f"FATAL APPLICATION ERROR: {e}. GUI could not run. Check logs.")

    logger.info("Application mainloop exited.")

# --- RegionSelector Class (for interactive region selection) ---
class RegionSelector:
    """
    A Toplevel window for interactively selecting a screen region.
    Displays a full-screen, semi-transparent overlay with a screenshot,
    allowing the user to draw a rectangle to define the region.
    """
    def __init__(self, parent_gui, callback_func, status_var_ref):
        """
        Initializes the RegionSelector window.
        Args:
            parent_gui (tk.Tk or tk.Toplevel): The main GUI window.
            callback_func (function): Function to call with the selected region coordinates (x,y,w,h) or None.
            status_var_ref (tk.StringVar): StringVar from the main GUI to update status messages.
        """
        logger.info("RegionSelector initializing.")
        self.parent_gui_master = parent_gui
        self.callback = callback_func
        self.status_var = status_var_ref

        self.selector_window = tk.Toplevel(self.parent_gui_master)
        self.selector_window.title("Region Selector")

        self.selector_window.overrideredirect(True)
        self.selector_window.attributes('-topmost', True)
        self.selector_window.attributes('-alpha', 0.75)

        try:
            self.screen_width = self.selector_window.winfo_screenwidth()
            self.screen_height = self.selector_window.winfo_screenheight()
            self.selector_window.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

            self.status_var.set("Status: Capturing screen for region selection...")
            self.parent_gui_master.update_idletasks()

            self.screenshot_tk = None
            try:
                screenshot_pil = pyautogui.screenshot()
                self.screenshot_tk = ImageTk.PhotoImage(screenshot_pil)
                logger.info("Screen captured successfully for RegionSelector display.")
            except pyautogui.PyAutoGUIException as pae: # Specific to pyautogui errors
                logger.exception("RegionSelector: PyAutoGUI failed to capture screen.")
                messagebox.showerror("Screen Capture Error (PyAutoGUI)", f"PyAutoGUI failed to capture screen for region selection:\n{pae}", parent=self.selector_window)
                self.status_var.set("Status: Screen capture for region failed (PyAutoGUI).")
                self._cleanup_and_cancel()
                return
            except Exception as e: # Other errors (e.g., PIL/ImageTk)
                logger.exception("RegionSelector: Generic error during screen capture or image processing.")
                messagebox.showerror("Screen Capture Error (Processing)", f"Failed during screen capture processing for region selection:\n{e}", parent=self.selector_window)
                self.status_var.set("Status: Screen capture processing failed.")
                self._cleanup_and_cancel()
                return

            self.canvas = tk.Canvas(self.selector_window, width=self.screen_width, height=self.screen_height, cursor="crosshair")
            if self.screenshot_tk:
                self.canvas.create_image(0, 0, image=self.screenshot_tk, anchor=tk.NW)
            else: # Should not happen if previous try-except worked, but as a safeguard
                logger.error("RegionSelector: Screenshot TK image is None after capture. Cannot display.")
                messagebox.showerror("Display Error", "Failed to prepare screenshot for display.", parent=self.selector_window)
                self._cleanup_and_cancel()
                return

            self.canvas.pack(fill=tk.BOTH, expand=True)

            self.start_x = None
            self.start_y = None
            self.current_rect_id = None

            self.canvas.bind("<ButtonPress-1>", self._on_button_press)
            self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
            self.canvas.bind("<ButtonRelease-1>", self._on_button_release)

            self.selector_window.protocol("WM_DELETE_WINDOW", self._on_window_close)
            self.selector_window.bind("<Escape>", self._on_window_close)

            self.status_var.set("Status: Drag on screen to select region. Press ESC to cancel.")
            self.selector_window.focus_force()
            logger.info("RegionSelector initialized and displayed successfully.")
        except Exception as e: # Catch-all for any other init errors
            logger.exception("Critical error during RegionSelector initialization sequence.")
            self.status_var.set("Status: Critical error initializing region selector.")
            self._cleanup_and_cancel() # Call cleanup

    def _cleanup_and_cancel(self):
        """Centralized cleanup for RegionSelector failure or cancellation."""
        if hasattr(self, 'selector_window') and self.selector_window.winfo_exists():
            self.selector_window.destroy()
        self.callback(None)


    def _on_button_press(self, event):
        """Handles mouse button press to start drawing the selection rectangle."""
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        if self.current_rect_id:
            self.canvas.delete(self.current_rect_id)
        logger.debug("RegionSelector: Button press at (%s, %s)", self.start_x, self.start_y)

    def _on_mouse_drag(self, event):
        """Handles mouse drag to draw/update the selection rectangle."""
        if self.start_x is None or self.start_y is None:
            return

        cur_x = self.canvas.canvasx(event.x)
        cur_y = self.canvas.canvasy(event.y)

        if self.current_rect_id:
            self.canvas.delete(self.current_rect_id)

        self.current_rect_id = self.canvas.create_rectangle(
            self.start_x, self.start_y, cur_x, cur_y,
            outline='red', width=2, dash=(4, 2)
        )
        # logger.debug("RegionSelector: Drag to (%s, %s)", cur_x, cur_y) # Too verbose for INFO
        self.status_var.set(f"Status: Selecting... from ({int(self.start_x)},{int(self.start_y)}) to ({int(cur_x)},{int(cur_y)})")

    def _on_button_release(self, event):
        """Handles mouse button release to finalize the selection rectangle."""
        if self.start_x is None or self.start_y is None:
            logger.warning("RegionSelector: Button release with no start point.")
            self._on_window_close()
            return

        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)
        logger.debug("RegionSelector: Button release at (%s, %s)", end_x, end_y)

        x1 = min(self.start_x, end_x)
        y1 = min(self.start_y, end_y)
        x2 = max(self.start_x, end_x)
        y2 = max(self.start_y, end_y)

        width = x2 - x1
        height = y2 - y1

        if width >= 5 and height >= 5:
            final_x = max(0, int(x1))
            final_y = max(0, int(y1))
            final_width = min(self.screen_width - final_x, int(width))
            final_height = min(self.screen_height - final_y, int(height))

            selected_coords = (final_x, final_y, final_width, final_height)
            logger.info("RegionSelector: Region selected: %s", selected_coords)
            self.status_var.set(f"Status: Region selected: X:{final_x} Y:{final_y} W:{final_width} H:{final_height}")
            self.callback(selected_coords)
        else:
            logger.warning("RegionSelector: Invalid region selected (too small): w=%s, h=%s. Selection cancelled.", width, height)
            self.status_var.set("Status: Invalid region selected (too small). Selection cancelled.")
            self.callback(None)

        self.selector_window.destroy()

    def _on_window_close(self, event=None):
        """Handles premature closing of the selector window (e.g., Escape key)."""
        logger.info("RegionSelector: Window closed by user or event. Selection cancelled.")
        self.status_var.set("Status: Region selection cancelled by user.")
        if hasattr(self, 'selector_window') and self.selector_window.winfo_exists():
            self.selector_window.destroy()
        self.callback(None)


if __name__ == "__main__":
    main()
