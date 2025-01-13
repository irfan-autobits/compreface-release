from matplotlib import pyplot as plt
import numpy as np

from scipy.signal import butter, filtfilt

def bandpass_filter(signal, lowcut, highcut, sampling_rate, order=4):
    nyquist = 0.5 * sampling_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

def integrate_fft(signal, sampling_rate):
    """Integrate signal using FFT."""
    N = len(signal)
    fft_signal = np.fft.fft(signal)
    freqs = np.fft.fftfreq(N, d=1/sampling_rate)
    # Avoid division by zero for DC component
    fft_signal[1:] /= (2j * np.pi * freqs[1:])
    fft_signal[0] = 0  # Set DC component explicitly to zero
    return np.fft.ifft(fft_signal).real


def compute_rms(signal):
    """Compute RMS of a time-domain signal."""
    return np.sqrt(np.mean(signal**2))

def compute_fft_rms(fft_magnitude):
    """Compute RMS from the FFT spectrum of a signal."""
    return np.sqrt(np.sum(fft_magnitude**2) * 2) / 2

def integrate_riemann(signal, dx):
    """Integrate using the midpoint Riemann sum."""
    signal = np.cumsum(signal) * dx
    signal -= np.mean(signal)
    return signal

def compute_fft(signal, N):
    """Compute RMS from the FFT spectrum of a signal."""
    # Compute FFT
    fft_result = np.fft.fft(signal)  # Compute FFT
    fft_magnitude = np.abs(fft_result) / N  # Normalize FFT magnitude

    positive_fft_magnitude = fft_magnitude[:N // 2]
    return positive_fft_magnitude

def plot_signals(timestamps, time_interval, N, acc_x, acc_positive_fft_magnitude, velo_x, velo_positive_fft_magnitude, disp_x, disp_positive_fft_magnitude):
    frequencies = np.fft.fftfreq(N, d=time_interval)  # Frequency bins
    positive_frequencies = frequencies[:N // 2]  # Select positive frequencies

    # Create subplots: 3 rows and 2 columns
    fig, axs = plt.subplots(3, 2, figsize=(14, 12))

    # Plot acceleration signal (time domain)
    axs[0, 0].plot(timestamps / 1000, acc_x, label="AccX (Time Domain)", color="blue")
    axs[0, 0].set_title("Acceleration Signal (Time Domain)")
    axs[0, 0].set_xlabel("Time (s)")
    axs[0, 0].set_ylabel("Acceleration (m/s²)")
    axs[0, 0].legend()
    axs[0, 0].grid()

    # Plot acceleration FFT (frequency domain)
    axs[0, 1].plot(positive_frequencies, acc_positive_fft_magnitude, label="FFT of AccX (Frequency Domain)", color="orange")
    axs[0, 1].set_title("Acceleration Signal (Frequency Domain)")
    axs[0, 1].set_xlabel("Frequency (Hz)")
    axs[0, 1].set_ylabel("Magnitude")
    axs[0, 1].legend()
    axs[0, 1].grid()
    # axs[0, 1].set_xlim(0, 10000)  # Zoom in on the first 10,000 Hz

    # Plot velocity signal (time domain)
    axs[1, 0].plot(timestamps / 1000, velo_x, label="VelocityX (Time Domain)", color="green")
    axs[1, 0].set_title("Velocity Signal (Time Domain)")
    axs[1, 0].set_xlabel("Time (s)")
    axs[1, 0].set_ylabel("Velocity (m/s)")
    axs[1, 0].legend()
    axs[1, 0].grid()

    # Plot velocity FFT (frequency domain)
    axs[1, 1].plot(positive_frequencies, velo_positive_fft_magnitude, label="FFT of VelocityX (Frequency Domain)", color="red")
    axs[1, 1].set_title("Velocity Signal (Frequency Domain)")
    axs[1, 1].set_xlabel("Frequency (Hz)")
    axs[1, 1].set_ylabel("Magnitude")
    axs[1, 1].legend()
    axs[1, 1].grid()
    # axs[1, 1].set_xlim(0, 10000)  # Zoom in on the first 10,000 Hz

    # Plot displacement signal (time domain)
    axs[2, 0].plot(timestamps / 1000, disp_x, label="DispX (Time Domain)", color="purple")
    axs[2, 0].set_title("Displacement Signal (Time Domain)")
    axs[2, 0].set_xlabel("Time (s)")
    axs[2, 0].set_ylabel("Displacement (m)")
    axs[2, 0].legend()
    axs[2, 0].grid()

    # Plot displacement FFT (frequency domain)
    axs[2, 1].plot(positive_frequencies, disp_positive_fft_magnitude, label="FFT of DispX (Frequency Domain)", color="brown")
    axs[2, 1].set_title("Displacement Signal (Frequency Domain)")
    axs[2, 1].set_xlabel("Frequency (Hz)")
    axs[2, 1].set_ylabel("Magnitude")
    axs[2, 1].legend()
    axs[2, 1].grid()
    # axs[2, 1].set_xlim(0, 10000)  # Zoom in on the first 10,000 Hz

    # Adjust layout for better spacing
    plt.tight_layout()
    plt.show()

# Theoretical RMS of acceleration
def aRMS_theoretical(amplitudes, frequencies):
    aRMS_theoretical = np.sqrt(sum((amp ** 2) / 2 for amp in amplitudes))
    # Theoretical RMS of velocity
    vRMS_theoretical = np.sqrt(
        sum((amp / (2 * np.pi * freq)) ** 2 / 2 for amp, freq in zip(amplitudes, frequencies))
    )
    print(f"Theoretical aRMS: {aRMS_theoretical:.6f}")
    print(f"Theoretical vRMS: {vRMS_theoretical:.6f}")
