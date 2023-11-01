# Simple GUI for Klipper Input Shaper Calibration.
# Made by RoyalT

from tkinter import *
from tkinter import filedialog
import calibrate_shaper
import matplotlib

# Use TkAgg backend
matplotlib.use('TkAgg')


def browse_files():
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select a File",
        filetypes=(
            ("CSV files", "*.csv"),
            ("all files", "*.*")
        )
    )
    # Change label contents
    label_file_explorer.configure(text="File Opened: " + filename)


def run_shaper(filename):
    max_freq = 200
    # Parse data
    args = [f'{filename}']
    datas = [calibrate_shaper.parse_log(fn) for fn in args]
    # Calibrate shaper and generate outputs
    selected_shaper, shapers, calibration_data = calibrate_shaper.calibrate_shaper(datas, None, None)
    # Draw graph
    calibrate_shaper.setup_matplotlib(None)
    fig = calibrate_shaper.plot_freq_response(args, calibration_data, shapers, selected_shaper, max_freq)
    fig.show()


def _exit():
    exit()


# GUI root window
window = Tk()
window.title("Shaper Calibration Assistant by RoyalT")
# Labels and buttons
label_file_explorer = Label(
    window,
    text="Select a CSV file to run shaper calibration on",
    width=100,
    height=4,
    fg="blue"
)
button_explore = Button(window, text="Select CSV File", command=browse_files)
button_exit = Button(window, text="Exit", command=_exit)
button_run = Button(
    window,
    text="Run",
    command=lambda: run_shaper(label_file_explorer.cget("text").split(": ")[1])
)
# Grid
label_file_explorer.grid(column=1, row=1)
button_explore.grid(column=1, row=2)
button_run.grid(column=1, row=3)
button_exit.grid(column=1, row=4)
# Drive it like you stole it
window.mainloop()
