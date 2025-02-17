import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

# Parameters
Fs = 1000  # Sampling frequency in Hz
duration = 1  # Duration in seconds
frequency = 50  # Sine wave frequency in Hz
amplitude = 1  # Amplitude in G

# Time vector
t = np.linspace(0, duration, int(Fs * duration), endpoint=False)

# Generate sine wave
sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)

# FFT
fft_result = fft(sine_wave)
N = len(sine_wave)
fft_magnitude = (2 / N) * np.abs(fft_result[:N // 2])  # Normalize and keep single-sided spectrum
frequencies = fftfreq(N, 1 / Fs)[:N // 2]

# Plot time-domain signal
plt.figure(figsize=(12, 6))

# Time-domain plot
plt.subplot(1, 2, 1)
plt.plot(t, sine_wave, label="Sine Wave", color="blue")
plt.title("Time Domain: Sine Wave (Amplitude = 1 G)")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude (G)")
plt.grid()
plt.legend()

# Frequency-domain plot
plt.subplot(1, 2, 2)
plt.plot(frequencies, fft_magnitude, label="FFT Magnitude", color="red")
plt.title("Frequency Domain: FFT of Sine Wave")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude (G)")
plt.grid()
plt.legend()

plt.tight_layout()
plt.show()
