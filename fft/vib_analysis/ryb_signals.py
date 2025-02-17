import numpy as np
import matplotlib.pyplot as plt

# Define parameters for the three-phase signals
frequency = 1  # Hz
amplitude = 1
sampling_rate = 1000  # Hz
duration = 1  # seconds
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# Define phases for R, Y, B
phases = [0, 2 * np.pi / 3, 4 * np.pi / 3]  # 0°, 120°, 240° in radians
labels = ["R Phase", "Y Phase", "B Phase"]

# Generate the signals
signals = [amplitude * np.sin(2 * np.pi * frequency * t + phase) for phase in phases]

# Plot the signals
plt.figure(figsize=(10, 6))
for signal, label in zip(signals, labels):
    plt.plot(t, signal, label=label)
plt.title("Three-Phase Signals")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)
plt.show()
