import numpy as np
import pytest
import calibrate_shaper
import textwrap

def test_parse_log_valid_csv():
    """
    Tests that the parse_log function can correctly parse a valid CSV file.
    """
    # Create a dummy CSV file for testing. The header includes "mzv" to
    # prevent the data from being normalized, allowing for a direct comparison.
    dummy_data = textwrap.dedent("""\
    freq,psd_x,psd_y,psd_z,psd_xyz,mzv
    10.0,100.0,110.0,120.0,330.0,0
    20.0,200.0,210.0,220.0,630.0,0
    30.0,300.0,310.0,320.0,930.0,0
    """)
    dummy_filepath = "tests/dummy_data.csv"
    with open(dummy_filepath, "w") as f:
        f.write(dummy_data)

    # Parse the dummy CSV file
    calibration_data = calibrate_shaper.parse_log(dummy_filepath)

    # Check that the parsed data is correct
    assert isinstance(calibration_data, object)  # shaper_calibrate.CalibrationData
    assert np.array_equal(calibration_data.freq_bins, np.array([10.0, 20.0, 30.0]))
    assert np.array_equal(calibration_data.psd_x, np.array([100.0, 200.0, 300.0]))
    assert np.array_equal(calibration_data.psd_y, np.array([110.0, 210.0, 310.0]))
    assert np.array_equal(calibration_data.psd_z, np.array([120.0, 220.0, 320.0]))
    assert np.array_equal(calibration_data.psd_sum, np.array([330.0, 630.0, 930.0]))


def test_parse_log_raw_accelerometer_data():
    """
    Tests that the parse_log function can correctly parse a CSV file with
    raw accelerometer data (no header).
    """
    # Create a dummy CSV file with raw accelerometer data
    dummy_data = textwrap.dedent("""\
    1.0,2.0,3.0
    4.0,5.0,6.0
    """)
    dummy_filepath = "tests/dummy_raw_data.csv"
    with open(dummy_filepath, "w") as f:
        f.write(dummy_data)

    # Parse the dummy CSV file
    data = calibrate_shaper.parse_log(dummy_filepath)

    # Check that the parsed data is a numpy array with the correct shape and values
    assert isinstance(data, np.ndarray)
    assert data.shape == (2, 3)
    assert np.array_equal(data, np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]))