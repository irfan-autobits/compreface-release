import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from paths import DATABASE_DIR
from call_fn import compute_fft, plot_signals, integrate_riemann
file_name = DATABASE_DIR / "01-m1_half_shaft_speed_no_mechanical_load.csv"

# Load the CSV file
data = pd.read_csv(str(file_name)) 

# Extract columns
timestamps = data["Timestamp"]
acc_x = data["AccX"]
acc_y = data["AccY"]
acc_z = data["AccZ"]

acc_x -= np.mean(acc_x)

# Ensure timestamps are evenly spaced (required for FFT)
time_interval = np.mean(np.diff(timestamps)) / 1000  # Convert to seconds if timestamps are in ms
sampling_rate = 1 / time_interval  # Sampling frequency in Hz

N = len(acc_x)  # Number of data points
acc_positive_fft_magnitude = compute_fft(acc_x, N)

velo_x = integrate_riemann(acc_x, dx=1/sampling_rate)
velo_positive_fft_magnitude = compute_fft(velo_x, N)

disp_x = integrate_riemann(velo_x, dx=1/sampling_rate)
disp_positive_fft_magnitude = compute_fft(disp_x, N)

# Call the plotting function with the calculated signals and their FFT magnitudes
plot_signals(
    timestamps=np.array(timestamps),  # Ensure it's a numpy array
    time_interval=time_interval,
    N=N,
    acc_x=np.array(acc_x),                                    # Acceleration signal (time domain)
    acc_positive_fft_magnitude=acc_positive_fft_magnitude,    # Acceleration FFT
    velo_x=np.array(velo_x),                                  # Velocity signal (time domain)
    velo_positive_fft_magnitude=velo_positive_fft_magnitude,  # Velocity FFT
    disp_x=np.array(disp_x),                                  # Displacement signal (time domain)
    disp_positive_fft_magnitude=disp_positive_fft_magnitude   # Displacement FFT
)

