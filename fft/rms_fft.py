import json
import numpy as np
import matplotlib.pyplot as plt

# Read the raw data from JSON
with open("new_rmx.json", "r") as file:
    DecodedRawData = json.load(file)

Fs = 13156.67  # Sampling frequency (Hz)
tstep = 1 / Fs  # Sample time interval

y = np.array(DecodedRawData['raw_data'][0: int(Fs)])  # Convert the list to a NumPy array
N = len(y)  # Number of samples

# Calculate RMS of the acceleration in the time domain
rms_value = np.sqrt(np.mean(y**2))
print(f"a-RMS Value time domain: {rms_value}")

y = y * 1000  # Convert from m/s² to mm/s²

# Remove DC component from acceleration
y = y - np.mean(y)

# Calculate RMS of the velocity in the time domain
velocity = np.cumsum(y) * tstep
print("velocitys:",velocity, "len:", len(velocity))
v_rms = np.sqrt(np.mean(velocity**2))
print("Vrms time domain:", v_rms)

# Prepare time vector
t = np.linspace(0, (N-1) * tstep, N)  # Time vector

# Frequency domain calculations
fstep = Fs / N  # Frequency step
f = np.linspace(0, (N-1) * fstep, N)  # Frequency vector

# FFT of raw data (acceleration in frequency domain)
x = np.fft.fft(y)
x = np.abs(x) / N  # Magnitude of the FFT

# Eliminate low frequencies (e.g., below 1 Hz) to avoid noise
elimination_indices = (f >= 0) & (f < 1)
x[elimination_indices] = 0

# Convert acceleration to velocity in the frequency domain
velocity_mag = np.zeros_like(x)
velocity_mag[1:] = x[1:] / (2 * np.pi * f[1:])  # Skip f[0] to avoid division by zero
velocity_mag[0] = 0  # Set DC component to zero

# Frequency domain plot for acceleration
# x_mag_plot = 2 * x[0: int(N/2+1)]
x_mag_plot = 2 * x[10: 4000]
x_mag_plot[0] = x_mag_plot[0] / 2  # Adjust the DC component for better visualization

# Frequency domain plot for velocity
# velocity_mag_plot = 2 * velocity_mag[0: int(N/2+1)]
velocity_mag_plot = 2 * velocity_mag[10: 4000]

# Prepare the frequency plot for acceleration and velocity
# f_plot = f[0: int(N/2+1)]
f_plot = f[10: 4000]

# Calculate RMS of the velocity in the frequency domain
v_rms_freq = np.sqrt(np.mean(velocity_mag**2))  # RMS of the velocity magnitude
print("RMS of velocity in frequency domain:", v_rms_freq)

# Plotting the graphs with acceleration on the right and velocity on the left
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

# Plot velocity in time domain (Top-left)
ax3.plot(t, velocity, linewidth=0.5)
ax3.set_xlabel("Time [s]")
ax3.set_ylabel("Velocity [m/s]")
ax3.set_title("Velocity in Time Domain")

# Plot velocity in frequency domain (Bottom-left)
ax4.plot(f_plot, velocity_mag_plot, linewidth=0.5)
ax4.set_xlabel("Frequency [Hz]")
ax4.set_ylabel("Magnitude [Velocity]")
ax4.set_title("Velocity in Frequency Domain")

# Plot acceleration in time domain (Top-right)
ax1.plot(t, y, linewidth=0.5)
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Acceleration [m/s^2]")
ax1.set_title("Acceleration in Time Domain")

# Plot acceleration in frequency domain (Bottom-right)
ax2.plot(f_plot, x_mag_plot, linewidth=0.5)
ax2.set_xlabel("Frequency [Hz]")
ax2.set_ylabel("Magnitude [Acceleration]")
ax2.set_title("Acceleration in Frequency Domain")

plt.tight_layout()
# plt.show()
plt.savefig("acc_velocity.png")

