import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from paths import DATABASE_DIR
from call_fn import compute_fft, plot_signals, integrate_riemann, bandpass_filter, integrate_fft, velocity_fft_from_acceleration
file_name = DATABASE_DIR / "01-m1_half_shaft_speed_no_mechanical_load.csv"
# file_name = DATABASE_DIR / "03-m1_mechanically_imbalanced_half_speed.csv"
file_name = "aircraft.csv"


# Load the CSV file
data = pd.read_csv(str(file_name)) 

# Dictionary to map axis names to data
axes_data = {
    "X": data["AccX"],
    # "Y": data["AccY"],
    # "Z": data["AccZ"]
}

# Ensure timestamps are evenly spaced (required for FFT)
timestamps = data["Timestamp"]
time_interval = np.mean(np.diff(timestamps))  # Convert to seconds if timestamps are in ms
sampling_rate = 1 / time_interval  # Sampling frequency in Hz
timestamps = np.array(timestamps)
print("sampling_rate",sampling_rate)
print("time_interval",time_interval)
for axis, acc_data in axes_data.items():
    # Remove mean from the acceleration data
    acc_data -= np.mean(acc_data)
    
    N = len(acc_data)  # Number of data points
    frequencies = np.fft.fftfreq(N, d=1/sampling_rate)  # Frequency bins
    
    velo_data = integrate_riemann(acc_data, dx=time_interval)
    disp_data = integrate_riemann(velo_data, dx=time_interval)
    
    # Compute FFT, velocity, and displacement
    acc_positive_fft_magnitude = compute_fft(acc_data, N)
    velo_positive_fft_magnitude = compute_fft(velo_data, N)
    disp_positive_fft_magnitude = compute_fft(disp_data, N)
    # velo_positive_fft_magnitude = integrate_fft(acc_positive_fft_magnitude, time_interval)
    # disp_positive_fft_magnitude = integrate_fft(acc_positive_fft_magnitude, time_interval)
    # velo_positive_fft_magnitude = velocity_fft_from_acceleration(acc_positive_fft_magnitude, time_interval)
    # disp_positive_fft_magnitude = velocity_fft_from_acceleration(velo_positive_fft_magnitude, time_interval)

    # Plot the signals for the current axis
    plot_signals(
        timestamps=timestamps,
        frequencies=frequencies,
        N=N,
        acc_signal=np.array(acc_data),                           # Acceleration signal (time domain)
        acc_positive_fft_magnitude=acc_positive_fft_magnitude,   # Acceleration FFT
        velo_signal=np.array(velo_data),                         # Velocity signal (time domain)
        velo_positive_fft_magnitude=velo_positive_fft_magnitude, # Velocity FFT
        disp_signal=np.array(disp_data),                         # Displacement signal (time domain)
        disp_positive_fft_magnitude=disp_positive_fft_magnitude, # Displacement FFT
        axis_label=axis                                          # Axis label for titles
    )

