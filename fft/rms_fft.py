import json
import numpy as np
import matplotlib.pyplot as plt

# Read the raw data from JSON
with open("new.json", "r") as file:
    DecodedRawData = json.load(file)

Fs = 13156.67  # Sampling frequency (Hz)
tstep = 1 / Fs  # Sample time interval

y = DecodedRawData['raw_data'][0: int(Fs)]  # Take a sample of raw data for one second
N = len(y)  # Number of samples

v = np.array(y)
rms_value = np.sqrt(np.mean(v**2))
print(f"a-RMS Value time domain: {rms_value}")

# Calculate RMS of the velocity in the time domain
velocity = np.cumsum(v)*tstep
v_rms=np.sqrt(np.mean(velocity**2))
print("Vrms time domain:",v_rms)

t = np.linspace(0, (N-1) * tstep, N)  # Time vector
fstep = Fs / N  # Frequency step
f = np.linspace(0, (N-1) * fstep, N)  # Frequency vector

# FFT of raw data (acceleration in frequency domain)
x = np.fft.fft(y)
x_mag = np.abs(x) / N  # Magnitude of the FFT

# Eliminate low frequencies (e.g., below 1 Hz) to avoid noise
elimination_indices = (f >= 0) & (f < 1)
x_mag[elimination_indices] = 0

# Convert acceleration to velocity in the frequency domain
# For velocity: V(f) = A(f) / (j 2 * pi * f), we only need the magnitude
# We handle the 0 Hz (DC) case by setting it to zero
velocity_mag = np.zeros_like(x_mag)
velocity_mag[1:] = x_mag[1:] / (2 * np.pi * f[1:])  # Skip f[0] to avoid division by zero

# Calculate RMS of the velocity in the frequency domain
v_rms = np.sqrt(np.mean(velocity_mag**2))  # RMS of the velocity magnitude
print("RMS of velocity in frequency domain:", v_rms)

# Prepare the frequency plot for velocity
f_plot = f[0: int(N/2+1)]
velocity_mag_plot = 2 * velocity_mag[0: int(N/2+1)]
velocity_mag_plot[0] = velocity_mag_plot[0] / 2  # DC component adjustment

# Plot both acceleration and velocity in the time domain and frequency domain
fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1)

# Plot acceleration in the time domain
ax1.plot(t, y)
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Acceleration [m/s^2]")

# Plot velocity in the frequency domain
ax2.plot(f_plot, velocity_mag_plot)
ax2.set_xlabel("Frequency [Hz]")
ax2.set_ylabel("Velocity [m/s]")

plt.show()
