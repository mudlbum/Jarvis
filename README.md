# Screen Automator

Screen Automator is a Python-based GUI application that allows users to interact with their screen through various automation tasks. It provides functionalities for screen capture, image recognition within a selected screen region or full screen, mouse control, and keyboard input simulation.

## Features

*   **Screen Capture:** Capture the full screen and save it to a file.
*   **Image Search on Screen:**
    *   Find a template image on the screen.
    *   Select a specific region on the screen to search within.
    *   Adjust the confidence level for image matching.
*   **Mouse Control:** Move the mouse cursor to specified coordinates and perform a click.
*   **Keyboard Typing:** Simulate typing text input.
*   **Interactive Region Selection:** Visually select a screen region for targeted image searches.
*   **Confidence Adjustment:** Fine-tune the confidence for image recognition.

## Dependencies

To run this application from source, you need Python 3 and the dependencies listed in `requirements.txt`.

1.  Ensure you have Python 3 installed.
2.  Clone this repository (if you haven't already).
3.  Navigate to the project root directory.
4.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Running from Source

Once dependencies are installed, you can run the application directly from source:

```bash
python src/gui_app.py
```

## Building from Source

To package the application into a standalone executable, ensure all dependencies, including `pyinstaller` (as listed in `requirements.txt`), are installed.

Then, run the following command from the project root directory:

```bash
python -m PyInstaller --name ScreenAutomator --windowed --onefile src/gui_app.py
```

*   `--name ScreenAutomator`: Specifies the name of the executable and the `.spec` file.
*   `--windowed`: Prevents a command-line console window from appearing when the GUI application is run.
*   `--onefile`: Packages everything into a single executable file.
*   `src/gui_app.py`: The entry point script for the application.

The build process will create a `build` directory, a `dist` directory, and a `ScreenAutomator.spec` file. The final executable will be located in the `dist` directory.

## Running the Packaged Application

After successfully building the application:

1.  Navigate to the `dist` directory created by PyInstaller.
2.  Run the `ScreenAutomator` executable (e.g., `ScreenAutomator.exe` on Windows, `./ScreenAutomator` on macOS/Linux).

---
*Note: GUI functionality requiring screen interaction (capture, image finding, mouse/keyboard control) will need appropriate OS permissions (e.g., screen recording, accessibility access on macOS).*
