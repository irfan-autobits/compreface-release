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
sensitivity = 16  # mV/g
scale_factor = 1  # Convert to g

# Extract raw data and scale to acceleration in g
y_raw = np.array(DecodedRawData['raw_data'])
y_raw = y_raw - np.mean(y_raw)

y_scaled = y_raw * scale_factor / sensitivity

# Time domain analysis
t = np.arange(len(y_scaled)) * tstep

# Frequency domain (FFT)
N = len(y_scaled)
Y_FFT = fft(y_scaled)
frequencies = fftfreq(N, d=tstep)[:N // 2]
amplitudes = np.abs(Y_FFT)[:N // 2] / N

# Velocity and displacement in frequency domain
velocity = amplitudes / (2 * np.pi * frequencies)
displacement = velocity / (2 * np.pi * frequencies)
velocity[frequencies == 0] = 0
displacement[frequencies == 0] = 0

# Compute RMS, Peak, and Crest Factor for acceleration
RMS = np.sqrt(np.mean(y_scaled**2))
Peak = np.max(np.abs(y_scaled))
Crest_Factor = Peak / RMS

# Plot acceleration, velocity, and displacement in frequency domain
plt.figure(figsize=(12, 6))
plt.subplot(3, 1, 1)
plt.plot(frequencies, amplitudes)
plt.title("Acceleration (g) in Frequency Domain")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude (g)")

plt.subplot(3, 1, 2)
plt.plot(frequencies, velocity)
plt.title("Velocity (mm/s) in Frequency Domain")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude (mm/s)")

plt.subplot(3, 1, 3)
plt.plot(frequencies, displacement)
plt.title("Displacement (mil) in Frequency Domain")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude (mil)")

plt.tight_layout()
plt.show()

# Display calculated parameters
print(f"RMS: {RMS:.4f} g")
print(f"Peak: {Peak:.4f} g")
print(f"Crest Factor: {Crest_Factor:.4f}")
