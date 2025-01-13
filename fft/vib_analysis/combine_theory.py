from matplotlib import pyplot as plt
import numpy as np
from scipy.integrate import cumulative_trapezoid

# Parameters
frequencies = [2]  # Hz
amplitudes = [1]  # m/s^2
sampling_rate = 1000  # Hz
duration = 1  # seconds
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# Generate acceleration signal
acceleration_signal = sum(
    amp * np.sin(2 * np.pi * freq * t) for amp, freq in zip(amplitudes, frequencies)
)
acceleration_signal -= np.mean(acceleration_signal)

# Numerical integration for velocity
velocity_signal = cumulative_trapezoid(acceleration_signal, dx=1/sampling_rate, initial=0)

# Computed RMS values
aRMS_computed = np.sqrt(np.mean(acceleration_signal**2))
vRMS_computed = np.sqrt(np.mean(velocity_signal**2))

# Perform FFT on acceleration signal
N = len(acceleration_signal)
fft_acc = np.fft.fft(acceleration_signal)
frequencies_fft = np.fft.fftfreq(N, d=1 / sampling_rate)  # Frequency bins
fft_acc_magnitude = (2 / N) * np.abs(fft_acc[:N // 2]) # Single-sided spectrum

# Remove DC component plot
fft_acc_magnitude = fft_acc_magnitude[1:]

# # Remove DC component
fft_acc_rms_magnitude = fft_acc_magnitude[1:]
a_rms_freq = np.sqrt(np.sum(fft_acc_rms_magnitude ** 2) * 2) / 2

# Perform FFT on velocity signal
N = len(velocity_signal)
fft_velo = np.fft.fft(velocity_signal)
frequencies_fft = np.fft.fftfreq(N, d=1 / sampling_rate)  # Frequency bins
fft_velo_magnitude = (2 / N) * np.abs(fft_velo[:N // 2]) # Single-sided spectrum

# Remove DC component
fft_velo_magnitude = fft_velo_magnitude[1:]
# v_rms_freq = np.sqrt(np.sum(fft_velo_magnitude ** 2) / len(fft_velo_magnitude))
v_rms_freq = np.sqrt(np.sum(fft_velo_magnitude ** 2) * 2) / 2
# v_rms_freq = np.sqrt(np.mean(fft_velo_magnitude**2))

print(f"Computed aRMS: {aRMS_computed:.6f} vRMS: {vRMS_computed:.6f} ")

print(f"fft aRMS: {a_rms_freq:.6f} vRMS: {v_rms_freq:.6f} lenth {len(fft_velo_magnitude)}")

# Apply a window to reduce spectral leakage
# from scipy.signal import windows
# window = windows.hann(len(acceleration_signal))
# acceleration_signal_windowed = acceleration_signal * window
# velocity_signal_windowed = velocity_signal * window

# # Compute window normalization factor
# window_gain = np.sum(window) / len(window)

# # Perform FFT on windowed signals and normalize by window gain
# fft_acc = np.fft.fft(acceleration_signal_windowed)
# fft_velo = np.fft.fft(velocity_signal_windowed)

# # Single-sided spectrum
# fft_acc_magnitude = (2 / N) * np.abs(fft_acc[:N // 2]) / window_gain
# fft_velo_magnitude = (2 / N) * np.abs(fft_velo[:N // 2]) / window_gain

# # Remove DC component
# fft_acc_magnitude = fft_acc_magnitude[1:]
# fft_velo_magnitude = fft_velo_magnitude[1:]

# # Compute RMS from FFT (with normalization)
# a_rms_freq = np.sqrt(np.sum(fft_acc_magnitude ** 2))
# v_rms_freq = np.sqrt(np.sum(fft_velo_magnitude ** 2))

# print(f"FFT aRMS (with windowing and normalization): {a_rms_freq:.6f}")
# print(f"FFT vRMS (with windowing and normalization): {v_rms_freq:.6f}")

# time_energy_acc = np.sum(acceleration_signal ** 2)
time_energy_acc = np.sum(np.abs(acceleration_signal)**2)
time_energy_velo = np.sum(velocity_signal ** 2)

# fft_energy_acc = np.sum(fft_acc_magnitude ** 2)
fft_energy_acc = np.sum(np.abs(fft_acc_magnitude)**2)
fft_energy_velo = np.sum(fft_velo_magnitude ** 2)

print(f"Time Domain Energy: {time_energy_acc:.6f}")
print(f"FFT Energy: {fft_energy_acc:.6f}")


# Theoretical RMS of acceleration
def aRMS_theoretical():
    aRMS_theoretical = np.sqrt(sum((amp ** 2) / 2 for amp in amplitudes))
    # Theoretical RMS of velocity
    vRMS_theoretical = np.sqrt(
        sum((amp / (2 * np.pi * freq)) ** 2 / 2 for amp, freq in zip(amplitudes, frequencies))
    )
    print(f"Theoretical aRMS: {aRMS_theoretical:.6f}")
    print(f"Theoretical vRMS: {vRMS_theoretical:.6f}")

# aRMS_theoretical()

def plot_signals(t, acceleration_signal, velocity_signal, frequencies_fft, fft_acc_magnitude, fft_velo_magnitude):
    # Combine the four plots in one figure with subplots
    fig, axs = plt.subplots(2, 2, figsize=(14, 8))

    # Plot the acceleration signal
    axs[0, 0].plot(t, acceleration_signal, label="Acceleration Signal")
    axs[0, 0].set_title("Acceleration Signal (Time Domain)")
    axs[0, 0].set_xlabel("Time (s)")
    axs[0, 0].set_ylabel("Acceleration (m/s²)")
    axs[0, 0].legend()
    axs[0, 0].grid()

    # Plot the FFT of the acceleration signal
    axs[0, 1].plot(frequencies_fft[1:len(frequencies_fft)//2], fft_acc_magnitude, label="FFT of Acceleration Signal")
    axs[0, 1].set_title("Acceleration Signal (Frequency Domain)")
    axs[0, 1].set_xlabel("Frequency (Hz)")
    axs[0, 1].set_ylabel("Magnitude")
    axs[0, 1].legend()
    axs[0, 1].grid()

    # Plot the velocity signal
    axs[1, 0].plot(t, velocity_signal, label="Velocity Signal")
    axs[1, 0].set_title("Velocity Signal (Time Domain)")
    axs[1, 0].set_xlabel("Time (s)")
    axs[1, 0].set_ylabel("Velocity (m/s)")
    axs[1, 0].legend()
    axs[1, 0].grid()

    # Plot the FFT of the velocity signal
    axs[1, 1].plot(frequencies_fft[1:len(frequencies_fft)//2], fft_velo_magnitude, label="FFT of Velocity Signal")
    axs[1, 1].set_title("Velocity Signal (Frequency Domain)")
    axs[1, 1].set_xlabel("Frequency (Hz)")
    axs[1, 1].set_ylabel("Magnitude")
    axs[1, 1].legend()
    axs[1, 1].grid()

    # Adjust layout
    plt.tight_layout()
    plt.show()

# Call the plotting function
plot_signals(t, acceleration_signal, velocity_signal, frequencies_fft, fft_acc_magnitude, fft_velo_magnitude)