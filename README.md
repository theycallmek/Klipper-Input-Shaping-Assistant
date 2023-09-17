# Klipper-Input-Shaping-Assistant
Run Klipper's input shaping calibration without the need for a full Klipper setup or knowledge of Python.

![Screenshot of Klipper Input Shaper Assistant](https://i.imgur.com/8lTut0D.png)

This project aims to make it easy for users who have little knowledge of Python to run Klipper's input shaping calibration on Windows and view the resulting recommendations.

# 🔌Usage
Run it, select the CSV file you'd like to analyze, click the run button, the graph and results are shown to the user.

# 📦Download
[Releases](https://github.com/theycallmek/Klipper-Input-Shaping-Assistant/releases)

EXE packaged by pyinstaller. Build cmd:
> pyinstaller main.py --onefile --add-data="extras/*;extras"
