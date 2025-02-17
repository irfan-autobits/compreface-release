import numpy as np
import matplotlib.pyplot as plt

# Parameters for the sine wave
frequency = 50  # Frequency of the sine wave in Hz
amplitude = 1   # Amplitude of the sine wave
duration = 1    # Duration of the signal in seconds
sampling_rate = 1000  # Sampling rate in Hz

# Time array
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# Generate the sine wave
sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)


# Compute the FFT of the sine wave
fft_result = np.fft.fft(sine_wave)
fft_freq = np.fft.fftfreq(len(t), 1/sampling_rate)

# Only take the positive half of the FFT (excluding Nyquist if sampling rate is even)
positive_freqs = fft_freq[:len(fft_freq)//2]
positive_fft_result = fft_result[:len(fft_freq)//2]

# Compute the magnitude of the FFT
fft_magnitude = np.abs(positive_fft_result)

# Energy in Time Domain (normalized by length)
energy_time_domain = np.sum(sine_wave**2) / len(sine_wave)

# Energy in Frequency Domain (double the positive frequencies' energy, normalized)
energy_freq_domain = 2 * np.sum(fft_magnitude**2) / (len(sine_wave) * sampling_rate)

# Display the energy comparison
print(f"Energy in Time Domain: {energy_time_domain:.4f}")
print(f"Energy in Frequency Domain: {energy_freq_domain:.4f}")

# Plot the time domain signal
plt.figure(figsize=(10, 4))
plt.plot(t, sine_wave)
plt.title('Sine Wave in Time Domain')
plt.xlabel('Time [s]')
plt.ylabel('Amplitude')
plt.grid(True)
plt.show()

# Plot the frequency domain signal (magnitude of FFT)
plt.figure(figsize=(10, 4))
plt.plot(positive_freqs, fft_magnitude)
plt.title('FFT of Sine Wave in Frequency Domain')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Magnitude')
plt.grid(True)
plt.show()