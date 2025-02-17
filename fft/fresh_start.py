import numpy as np
import matplotlib.pyplot as plt
import json
from scipy.fft import fft, fftfreq
from scipy.signal import get_window

# Load JSON data
with open("new_rmx.json", "r") as file:
    DecodedRawData = json.load(file)

# Parameters
Fs = 13156.67  # Sampling frequency (Hz)
tstep = 1 / Fs  # Time step (s)    
# sensitivity = 0.00006  # 0.06 mg/LSB converted to g/LSB
# sensitivity = 9.81 / 1000  # 9.81 m/s^2 converted to g

# Read the raw data
y_raw = np.array(DecodedRawData['raw_data'][0: int(Fs)])
# Generate synthetic acceleration data (e.g., sine wave for testing)
amplitude = 1  # Set the desired amplitude here
# y_raw = amplitude * np.sin(2 * np.pi * 50 * np.linspace(0, 1, int(Fs)))  # 2000 Hz sine wave signal

# Convert raw data to acceleration in g
y_acceleration = y_raw * 1

y_acceleration = y_acceleration - np.mean(y_acceleration)

# Parameters
window = get_window('hann', len(y_acceleration))  # Hann window
# y_acceleration = y_acceleration * window

# FFT on windowed acceleration
y_acceleration_fft = np.fft.fft(y_acceleration)
# y_acceleration_fft = fft(y_acceleration)
N = len(y_acceleration)
fft_magnitude = (2 / N) * np.abs(y_acceleration_fft[:N // 2]) 
# fft_magnitude = fft_magnitude[10: 1000]

# Velocity is the integral of acceleration (numerical integration)
velocity = np.cumsum(y_acceleration) * tstep
velocity_fft = np.fft.fft(velocity)
velo_fft_magnitude = (2 / N) * np.abs(velocity_fft[:N // 2]) 
# velo_fft_magnitude = velo_fft_magnitude[10: 1000]

# Displacement is the integral of velocity (numerical integration)
displacement = np.cumsum(velocity) * tstep
displacement_fft = np.fft.fft(displacement)
dis_fft_magnitude = (2 / N) * np.abs(displacement_fft[:N // 2]) 
# dis_fft_magnitude = dis_fft_magnitude[10: 1000]

# Frequencies corresponding to the FFT
frequencies = np.fft.fftfreq(len(y_acceleration), tstep)
# frequencies = frequencies[10: 1000]

# RMS, Peak, and Crest Factor
# rms_acceleration = np.sqrt(np.mean(y_acceleration_fft**2))
rms_acceleration = np.sqrt(np.mean(y_acceleration**2))
peak_acceleration = np.max(y_acceleration_fft)
crest_factor = peak_acceleration / rms_acceleration

print('rms-----------',rms_acceleration)
# Plot acceleration, velocity, and displacement in time and frequency domains
fig, axes = plt.subplots(3, 2, figsize=(15, 12))

# Time-domain plots
axes[0, 0].plot(np.arange(len(y_acceleration)) * tstep, y_acceleration)
axes[0, 0].set_title("Acceleration (g) - Time Domain")
axes[0, 0].set_xlabel("Time (s)")
axes[0, 0].set_ylabel("Acceleration (g)")

axes[1, 0].plot(np.arange(len(velocity)) * tstep, velocity)
axes[1, 0].set_title("Velocity - Time Domain")
axes[1, 0].set_xlabel("Time (s)")
axes[1, 0].set_ylabel("Velocity (m/s or in/s)")

axes[2, 0].plot(np.arange(len(displacement)) * tstep, displacement)
axes[2, 0].set_title("Displacement - Time Domain")
axes[2, 0].set_xlabel("Time (s)")
axes[2, 0].set_ylabel("Displacement (m or in)")

# Frequency-domain plots
# axes[0, 1].plot(frequencies[:len(frequencies)//2], y_acceleration_fft[:len(frequencies)//2])
axes[0, 1].plot(frequencies[:len(frequencies)//2], fft_magnitude)
axes[0, 1].set_title("Acceleration (g) - Frequency Domain")
axes[0, 1].set_xlabel("Frequency (Hz)")
axes[0, 1].set_ylabel("Magnitude")

axes[1, 1].plot(frequencies[:len(frequencies)//2], velo_fft_magnitude)
axes[1, 1].set_title("Velocity - Frequency Domain")
axes[1, 1].set_xlabel("Frequency (Hz)")
axes[1, 1].set_ylabel("Magnitude")

axes[2, 1].plot(frequencies[:len(frequencies)//2], dis_fft_magnitude)
axes[2, 1].set_title("Displacement - Frequency Domain")
axes[2, 1].set_xlabel("Frequency (Hz)")
axes[2, 1].set_ylabel("Magnitude")

# Adjust layout for better appearance
plt.tight_layout()
plt.show()
