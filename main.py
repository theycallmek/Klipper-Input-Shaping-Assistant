# Simple GUI for Klipper Input Shaper Calibration.
# Made by RoyalT

import customtkinter
from tkinter import filedialog
import calibrate_shaper
import matplotlib
import threading
from typing import List, Any, Tuple, Union
from matplotlib.figure import Figure
import numpy as np

# Use TkAgg backend
matplotlib.use('TkAgg')
customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


def browse_files() -> None:
    """
    Opens a file dialog to select a CSV file and updates the GUI to reflect
    the selected file.
    """
    filename: str = filedialog.askopenfilename(
        initialdir="/",
        title="Select a File",
        filetypes=(
            ("CSV files", "*.csv*"),
            ("all files", "*.*")
        )
    )
    if filename:
        # Change label contents
        label_file_explorer.configure(text="File Opened: " + filename)
        button_run.configure(state="normal")


def run_shaper(filename: str) -> None:
    """
    Runs the shaper calibration process on the given file.

    Args:
        filename (str): The path to the CSV file to analyze.
    """
    max_freq: int = 200
    # Parse data
    args: List[str] = [f'{filename}']
    datas: List[Union[np.ndarray, Any]] = [calibrate_shaper.parse_log(fn) for fn in args]
    # Calibrate shaper and generate outputs
    selected_shaper: str
    shapers: Any
    calibration_data: Any
    selected_shaper, shapers, calibration_data = calibrate_shaper.calibrate_shaper(datas, None, None)
    # Draw graph
    calibrate_shaper.setup_matplotlib(None)
    fig: Figure = calibrate_shaper.plot_freq_response(args, calibration_data, shapers, selected_shaper, max_freq)
    fig.show()


def run_shaper_threaded() -> None:
    """
    Runs the shaper calibration in a separate thread to prevent the GUI from
    freezing. Disables the run button during execution and re-enables it
    when finished.
    """
    try:
        filepath: str = label_file_explorer.cget("text").split(": ")[1]
    except IndexError:
        label_file_explorer.configure(text="Please select a file first!")
        return

    button_run.configure(state="disabled", text="Running Calibration...")

    def task() -> None:
        """The actual task to be run in the thread."""
        try:
            run_shaper(filepath)
        except Exception as e:
            print(f"An error occurred: {e}")
            # Update the GUI to show the error
            label_file_explorer.configure(text=f"Error: {e}")
        finally:
            # Re-enable the run button
            button_run.configure(state="normal", text="Run")

    # Create and start the thread
    thread: threading.Thread = threading.Thread(target=task)
    thread.start()


def _exit() -> None:
    """Exits the application."""
    exit()


# GUI root window
window: customtkinter.CTk = customtkinter.CTk()
window.title("Shaper Calibration Assistant by RoyalT")
window.geometry("500x250")

# Labels and buttons
label_file_explorer: customtkinter.CTkLabel = customtkinter.CTkLabel(
    window,
    text="Select a CSV file to run shaper calibration on",
    width=100,
    height=4,
)
button_explore: customtkinter.CTkButton = customtkinter.CTkButton(window, text="Select CSV File", command=browse_files)
button_exit: customtkinter.CTkButton = customtkinter.CTkButton(window, text="Exit", command=_exit)
button_run: customtkinter.CTkButton = customtkinter.CTkButton(
    window,
    text="Run",
    command=run_shaper_threaded
)
button_run.configure(state="disabled")

# Grid
label_file_explorer.grid(row=0, column=0, padx=20, pady=20, columnspan=2)
button_explore.grid(row=1, column=0, padx=20, pady=10)
button_run.grid(row=1, column=1, padx=20, pady=10)
button_exit.grid(row=2, column=0, padx=20, pady=10, columnspan=2)

# Drive it like you stole it
window.mainloop()