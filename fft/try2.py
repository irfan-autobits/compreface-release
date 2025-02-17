
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import daata

Fs = 13156.67  # Sampling Frequency
tstep = 1 / Fs  # Sample time interval

y = np.array(daata.raw_data[0:13156])  # Convert to NumPy array and extract the first 13,156 samples
N = len(y)  # Number of samples in the signal

# Calculate RMS value
rms_value = np.sqrt(np.mean(y**2))
print(f"RMS Value: {rms_value}")

# Calculate absolute peak value
absolute_peak_value = np.max(np.abs(y))
print(f"Absolute Peak Value: {absolute_peak_value}")

# Generate time steps
t = np.linspace(0, (N-1)*tstep, N)

# Frequency interval
fstep = Fs / N
f = np.linspace(0, (N-1)*fstep, N)  # Frequency steps

# Compute FFT and magnitude
x = np.fft.fft(y)
x_mag = np.abs(x) / N

# Eliminate low frequencies (0 to 1 Hz)
elimination_indices = (f >= 0) & (f < 1)
x_mag[elimination_indices] = 0

# Prepare data for plotting
f_plot = f[0: int(N/2+1)]
x_mag_plot = 2 * x_mag[0:int(N/2+1)]
x_mag_plot[0] = x_mag_plot[0] / 2

# Find all positive peaks in the time-domain signal
peaks, _ = find_peaks(y)

# Plotting the signal and its frequency spectrum
fig, [ax1, ax2] = plt.subplots(nrows=2, ncols=1, figsize=(10, 8))

ax1.plot(t, y, label='Signal')
ax1.plot(t[peaks], y[peaks], "x", label='Peaks')
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Acceleration")
ax1.legend()

ax2.plot(f_plot, x_mag_plot)
ax2.set_xlabel("Frequency [Hz]")
ax2.set_ylabel("Acceleration")

plt.tight_layout()
plt.show()
