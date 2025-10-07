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
import pyperclip

from theme import CatppuccinMocha

# Use TkAgg backend
matplotlib.use('TkAgg')
customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"


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


def run_shaper(filename: str) -> Figure:
    """
    Runs the shaper calibration process on the given file.

    Args:
        filename (str): The path to the CSV file to analyze.

    Returns:
        Figure: The matplotlib figure containing the plot.
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
    return fig


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
                fig = run_shaper(filepath)
            # Pass the figure to the main thread for showing
            q.put(fig)
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
        elif isinstance(message, Figure):
            # If the message is a figure, show it
            message.show()
        else:
            # Otherwise, it's a string, so insert it into the textbox
            output_textbox.configure(state="normal")
            output_textbox.insert("end", str(message))
            output_textbox.configure(state="disabled")
    except queue.Empty:
        pass  # Queue is empty, do nothing

    # Check again after 100ms
    window.after(100, lambda: process_queue(q))


def _exit() -> None:
    """Exits the application."""
    exit()


def copy_to_clipboard() -> None:
    """
    Copies the content of the output textbox to the clipboard.
    """
    text_to_copy = output_textbox.get("1.0", "end-1c")
    if not text_to_copy:
        return  # Don't do anything if there's nothing to copy
    pyperclip.copy(text_to_copy)
    # Provide user feedback
    button_copy.configure(text="✅ Copied!")
    window.after(2000, lambda: button_copy.configure(text="📋 Copy Output"))


# GUI root window
window: customtkinter.CTk = customtkinter.CTk()
window.title("Shaper Calibration Assistant")
window.geometry("700x550")
window.configure(fg_color=CatppuccinMocha.BASE)

# --- Configure grid layout for responsiveness ---
# Make columns expand equally
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
# Make the textbox row expand vertically
window.grid_rowconfigure(2, weight=1)

# --- Create Widgets ---
label_file_explorer: customtkinter.CTkLabel = customtkinter.CTkLabel(
    window,
    text="Select a resonance data file (.csv) to begin",
    text_color=CatppuccinMocha.TEXT,
    font=("Arial", 14, "bold"),
)

button_explore: customtkinter.CTkButton = customtkinter.CTkButton(
    window,
    text="📄 Select CSV",
    command=browse_files,
    fg_color=CatppuccinMocha.BLUE,
    hover_color=CatppuccinMocha.SAPPHIRE,
    text_color=CatppuccinMocha.BASE,
    font=("Arial", 12, "bold")
)

button_run: customtkinter.CTkButton = customtkinter.CTkButton(
    window,
    text="🚀 Run Calibration",
    command=run_shaper_threaded,
    fg_color=CatppuccinMocha.GREEN,
    hover_color=CatppuccinMocha.TEAL,
    text_color=CatppuccinMocha.BASE,
    font=("Arial", 12, "bold")
)
button_run.configure(state="disabled")

button_copy: customtkinter.CTkButton = customtkinter.CTkButton(
    window,
    text="📋 Copy Output",
    command=copy_to_clipboard,
    fg_color=CatppuccinMocha.MAUVE,
    hover_color=CatppuccinMocha.LAVENDER,
    text_color=CatppuccinMocha.BASE,
    font=("Arial", 12, "bold")
)

button_exit: customtkinter.CTkButton = customtkinter.CTkButton(
    window,
    text="🚪 Exit",
    command=_exit,
    fg_color=CatppuccinMocha.RED,
    hover_color=CatppuccinMocha.MAROON,
    text_color=CatppuccinMocha.BASE,
    font=("Arial", 12, "bold")
)

output_textbox: customtkinter.CTkTextbox = customtkinter.CTkTextbox(
    window,
    state="disabled",
    fg_color=CatppuccinMocha.MANTLE,
    text_color=CatppuccinMocha.TEXT,
    border_color=CatppuccinMocha.OVERLAY0,
    border_width=2,
    corner_radius=10,
    font=("Consolas", 12)
)

# --- Place Widgets on Grid ---
label_file_explorer.grid(row=0, column=0, padx=20, pady=(20, 10), columnspan=2)

button_explore.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="ew")
button_run.grid(row=1, column=1, padx=(10, 20), pady=10, sticky="ew")

output_textbox.grid(row=2, column=0, padx=20, pady=10, columnspan=2, sticky="nsew")

button_copy.grid(row=3, column=0, padx=(20, 10), pady=10, sticky="ew")
button_exit.grid(row=3, column=1, padx=(10, 20), pady=10, sticky="ew")

# Drive it like you stole it
window.mainloop()