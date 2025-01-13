import numpy as np
import matplotlib.pyplot as plt
import json
from scipy.fft import fft, fftfreq

# Load JSON data
with open("new.json", "r") as file:
    DecodedRawData = json.load(file)

# Parameters
Fs = 13156.67  # Sampling frequency (Hz)
tstep = 1 / Fs  # Time step (s)    
sensitivity = 0.00006  # 0.06 mg/LSB converted to g/LSB

# Read the raw data
y_raw = np.array(DecodedRawData['raw_data'][0: int(Fs)])
# Generate synthetic acceleration data (e.g., sine wave for testing)
y_raw = np.sin(2 * np.pi * 2000 * np.linspace(0, 1, int(Fs)))  # 2000 Hz sine wave signal

# y_raw = y_raw - np.mean(y_raw)

# Convert raw data to acceleration in g
y_acceleration = y_raw * sensitivity

# Velocity is the integral of acceleration (numerical integration)
velocity = np.cumsum(y_acceleration) * tstep
# Displacement is the integral of velocity (numerical integration)
displacement = np.cumsum(velocity) * tstep

# Apply FFT to the acceleration data
y_acceleration_fft = np.fft.fft(y_acceleration)

# Calculate the corresponding frequencies for the FFT
frequencies = np.fft.fftfreq(len(y_acceleration), tstep)

# Take the magnitude of the FFT (since we're interested in the amplitude)
y_acceleration_fft_magnitude = np.abs(y_acceleration_fft)

rms_acceleration = np.sqrt(np.mean(y_acceleration_fft_magnitude**2))
peak_acceleration = np.max(y_acceleration_fft_magnitude)
crest_factor = peak_acceleration / rms_acceleration


import matplotlib.pyplot as plt

# Plot acceleration, velocity, and displacement in the time domain
plt.figure(figsize=(12, 6))

plt.subplot(3, 1, 1)
plt.plot(np.arange(len(y_acceleration)) * tstep, y_acceleration)
plt.title("Acceleration (g)")
plt.xlabel("Time (s)")
plt.ylabel("Acceleration (g)")

plt.subplot(3, 1, 2)
plt.plot(np.arange(len(velocity)) * tstep, velocity)
plt.title("Velocity (in/s or m/s)")
plt.xlabel("Time (s)")
plt.ylabel("Velocity (in/s)")

plt.subplot(3, 1, 3)
plt.plot(np.arange(len(displacement)) * tstep, displacement)
plt.title("Displacement (in or mm or m)")
plt.xlabel("Time (s)")
plt.ylabel("Displacement (in)")

plt.tight_layout()
plt.show()# Plot the FFT magnitude of acceleration

plt.figure(figsize=(12, 6))
plt.plot(frequencies[:len(frequencies)//2], y_acceleration_fft_magnitude[:len(frequencies)//2])
plt.title("FFT of Acceleration")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.show()


