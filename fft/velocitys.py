import json
import numpy as np
import matplotlib.pyplot as plt

# Read the raw data from JSON
with open("latest.json", "r") as file:
    DecodedRawData = json.load(file)

Fs = 13156.67  # Sampling frequency (Hz)
tstep = 1 / Fs  # Sample time interval

DecodedRawData = DecodedRawData['decodedRawData']
# y = np.array(DecodedRawData['raw_data'][int(Fs): 3 * int(Fs)])  # Convert the list to a NumPy array
y = np.array(DecodedRawData['raw_data'][0:int(Fs)])  # Convert the list to a NumPy array
N = len(y)  # Number of samples
# print('data length',len(y))
# print("Mean of acceleration:", np.mean(y))

y = y * 1000  # Convert from m/s² to mm/s²

# Remove DC component from acceleration
y = y - np.mean(y)
# print("Standard deviation of acceleration:", np.std(y))

# Calculate velocity in the time domain
velocity = np.cumsum(y) * tstep
# print("velocitys:",velocity, "len:", len(velocity))

# Prepare time vector
t = np.linspace(0, (N-1) * tstep, N)  # Time vector

# Frequency domain calculations
fstep = Fs / N  # Frequency step
f = np.linspace(0, (N-1) * fstep, N)  # Frequency vector

# FFT of raw data (acceleration in frequency domain)
x = np.fft.fft(velocity)
x = np.abs(x) / N  # Magnitude of the FFT

# Prepare frequency domain plot for velocity
# velocity_mag_plot = 2 * x[50: int(N/2+1)]
velocity_mag_plot = 2 * x[10: 1000]
# velocity_mag_plot[0] = velocity_mag_plot[0] / 2  # Adjust the DC component for better visualization

# Frequency vector for plotting
# f_plot = f[50: int(N/2+1)]
f_plot = f[10: 1000]

# Compute RMS for the sliced frequency-domain velocity
rms_velocity_freq = np.sqrt(np.sum(velocity_mag_plot**2))
print(f"RMS of velocity in frequency domain: {rms_velocity_freq}")

# Compute peak value of the sliced frequency-domain velocity
# peak_value = np.max(np.abs(velocity_mag_plot))
peak_value = np.max(velocity_mag_plot)
print("Peak value:", peak_value)

cf=rms_velocity_freq/peak_value
print("crest factor:",cf)

# Plotting the graphs for velocity
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(8, 8))

# Plot velocity in time domain
ax1.plot(t, velocity, color='black', linewidth=1)
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Velocity [mm/s]")
ax1.set_title("Velocity in Time Domain")

# Plot velocity in frequency domain
ax2.plot(f_plot, velocity_mag_plot, color='black', linewidth=1)
ax2.set_xlabel("Frequency [Hz]")
ax2.set_ylabel("Magnitude [Velocity]")
ax2.set_title("Velocity in Frequency Domain")

plt.tight_layout()
plt.savefig("plot_velocity.png")

# plt.show()
