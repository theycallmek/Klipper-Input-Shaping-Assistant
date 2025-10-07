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
import queue
import contextlib
import io

# Use TkAgg backend
matplotlib.use('TkAgg')
customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class QueueIO(io.TextIOBase):
    """
    A file-like object that writes to a queue. Used to redirect stdout.
    """
    def __init__(self, q: queue.Queue):
        self.q = q

    def write(self, s: str) -> int:
        self.q.put(s)
        return len(s.encode('utf-8'))


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

    # Clear the output textbox
    output_textbox.configure(state="normal")
    output_textbox.delete("1.0", "end")
    output_textbox.configure(state="disabled")

    button_run.configure(state="disabled", text="Running Calibration...")
    q = queue.Queue()
    q_io = QueueIO(q)

    def task() -> None:
        """The actual task to be run in the thread."""
        try:
            with contextlib.redirect_stdout(q_io):
                run_shaper(filepath)
        except Exception as e:
            # Also print exceptions to the queue
            print(f"An error occurred: {e}")
        finally:
            # Signal that the task is done
            q.put(None)

    # Create and start the thread
    thread: threading.Thread = threading.Thread(target=task)
    thread.start()
    # Start processing the queue
    process_queue(q)


def process_queue(q: queue.Queue) -> None:
    """
    Processes the queue of messages from the background thread and updates
    the GUI.
    """
    try:
        message = q.get_nowait()
        if message is None:
            # Task is done, re-enable the run button
            button_run.configure(state="normal", text="Run")
            return
        else:
            # Insert the message into the textbox
            output_textbox.configure(state="normal")
            output_textbox.insert("end", message)
            output_textbox.configure(state="disabled")
    except queue.Empty:
        pass  # Queue is empty, do nothing

    # Check again after 100ms
    window.after(100, lambda: process_queue(q))


def _exit() -> None:
    """Exits the application."""
    exit()


# GUI root window
window: customtkinter.CTk = customtkinter.CTk()
window.title("Shaper Calibration Assistant by RoyalT")
window.geometry("700x500")

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

# Output Textbox
output_textbox: customtkinter.CTkTextbox = customtkinter.CTkTextbox(
    window,
    width=660,
    height=300,
    state="disabled"  # Start as read-only
)

# Grid
label_file_explorer.grid(row=0, column=0, padx=20, pady=10, columnspan=2)
button_explore.grid(row=1, column=0, padx=20, pady=10)
button_run.grid(row=1, column=1, padx=20, pady=10)
output_textbox.grid(row=2, column=0, padx=20, pady=10, columnspan=2)
button_exit.grid(row=3, column=0, padx=20, pady=10, columnspan=2)


# Drive it like you stole it
window.mainloop()