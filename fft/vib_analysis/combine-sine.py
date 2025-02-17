import numpy as np
import matplotlib.pyplot as plt

# Parameters
sampling_rate = 1000  # Hz
duration = 2  # seconds
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)  # Time vector

# Generate sine waves
frequencies = [55, 78, 21, 42]  # Hz
amplitudes = [1.0, 1.0, 1.0, 1.0]  # m/s^2
phases = [0, np.pi , np.pi , 0]  # Phase offsets

# Combine sine waves to form acceleration signal
acceleration_signal = sum(
    amp * np.sin(2 * np.pi * freq * t + phase)
    for amp, freq, phase in zip(amplitudes, frequencies, phases)
)

# Plot the acceleration signal
plt.figure(figsize=(10, 4))
plt.plot(t, acceleration_signal, label="Acceleration Signal")
plt.title("Acceleration Signal (Time Domain)")
plt.xlabel("Time (s)")
plt.ylabel("Acceleration (m/s²)")
plt.legend()
plt.grid()
plt.show()

# Perform FFT on acceleration signal
N = len(acceleration_signal)
fft_acc = np.fft.fft(acceleration_signal)
frequencies_fft = np.fft.fftfreq(N, d=1 / sampling_rate)  # Frequency bins
fft_acc_magnitude = (2 / N) * np.abs(fft_acc[:N // 2])  # Single-sided spectrum

# Integrate in the frequency domain to derive velocity
fft_velocity = fft_acc / (2j * np.pi * frequencies_fft + 1e-12)  # Avoid divide-by-zero
fft_velocity[0] = 0  # Zero-out the DC component for velocity
fft_vel_magnitude = (2 / N) * np.abs(fft_velocity[:N // 2])  # Single-sided spectrum

# Compute RMS for acceleration and velocity
a_rms_freq = np.sqrt(np.sum(fft_acc_magnitude ** 2))
v_rms_freq = np.sqrt(np.sum(fft_vel_magnitude ** 2))

# Plot FFT results
plt.figure(figsize=(10, 4))
plt.plot(frequencies_fft[:N // 2], fft_acc_magnitude, label="Acceleration FFT")
plt.plot(frequencies_fft[:N // 2], fft_vel_magnitude, label="Velocity FFT")
plt.title("Frequency Domain Analysis")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.legend()
plt.grid()
plt.show()

# Print results
print(f"Acceleration RMS (Frequency Domain): {a_rms_freq:.6f} m/s²")
print(f"Velocity RMS (Frequency Domain): {v_rms_freq:.6f} mm/s")
