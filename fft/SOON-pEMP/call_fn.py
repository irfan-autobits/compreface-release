from matplotlib import pyplot as plt
import numpy as np

from scipy.signal import butter, filtfilt

def bandpass_filter(signal, lowcut, highcut, sampling_rate, order=4):
    nyquist = 0.5 * sampling_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

# def integrate_fft(signal, time_interval):
#     """Integrate signal using FFT."""
#     N = len(signal)
#     fft_signal = np.fft.fft(signal)
#     freqs = np.fft.fftfreq(N, d=time_interval)
#     # Avoid division by zero for DC component
#     fft_signal[1:] /= (2j * np.pi * freqs[1:])
#     fft_signal[0] = 0  # Set DC component explicitly to zero
#     return np.fft.ifft(fft_signal).real

def integrate_fft(signal, time_interval):
    N = len(signal)  # Number of data points
    frequencies = np.fft.fftfreq(N, d=time_interval)
    fft_signal = np.fft.fft(signal)
    
    # Avoid division by zero at DC component
    fft_integrated = np.zeros_like(fft_signal, dtype=complex)
    fft_integrated[1:] = fft_signal[1:] / (2j * np.pi * frequencies[1:])
    
    # Perform the inverse FFT and remove the mean to avoid drift
    # integrated_signal = np.fft.ifft(fft_integrated).real
    # integrated_signal -= np.mean(integrated_signal)
    return fft_integrated

import numpy as np

def velocity_fft_from_acceleration(acc_fft, time_interval):
    """
    Compute velocity FFT from acceleration FFT.

    Parameters:
    - acc_fft: np.ndarray
        The FFT of the acceleration signal (complex values).
    - frequencies: np.ndarray
        The frequency bins corresponding to the FFT.
    
    Returns:
    - velo_fft: np.ndarray
        The FFT of the velocity signal (complex values).
    """
    N = len(acc_fft)
    frequencies = np.fft.fftfreq(N, d=time_interval)  # Frequency bins

    # Initialize an array to store velocity FFT
    velo_fft = np.zeros_like(acc_fft, dtype=complex)
    
    # Avoid division by zero at the DC component (frequency = 0)
    nonzero_indices = frequencies != 0
    
    # Integrate in the frequency domain
    velo_fft[nonzero_indices] = acc_fft[nonzero_indices] / (2j * np.pi * frequencies[nonzero_indices])
    
    # Return velocity FFT
    return velo_fft

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
    positive_fft_magnitude = fft_result[:N // 2]
    fft_magnitude = (2 / N) * np.abs(positive_fft_magnitude)  # Single-sided spectrum
    fft_magnitude = fft_magnitude[200:]  # Remove DC component
    
    return fft_magnitude

def plot_signals(timestamps, frequencies, N, acc_signal, acc_positive_fft_magnitude, velo_signal, velo_positive_fft_magnitude, disp_signal, disp_positive_fft_magnitude, axis_label):
    positive_frequencies = frequencies[200:N // 2]  # Select positive frequencies

    # Create subplots: 3 rows and 2 columns
    fig, axs = plt.subplots(3, 2, figsize=(14, 12))

    # Plot acceleration signal (time domain)
    axs[0, 0].plot(timestamps / 1000, acc_signal, label=f"Acc{axis_label} (Time Domain)", color="blue")
    axs[0, 0].set_title(f"Acceleration Signal ({axis_label} Axis - Time Domain)")
    axs[0, 0].set_xlabel("Time (s)")
    axs[0, 0].set_ylabel("Acceleration (m/s²)")
    axs[0, 0].legend()
    axs[0, 0].grid()

    # Plot acceleration FFT (frequency domain)
    axs[0, 1].plot(positive_frequencies, acc_positive_fft_magnitude, label=f"FFT of Acc{axis_label} (Frequency Domain)", color="orange")
    axs[0, 1].set_title(f"Acceleration Signal ({axis_label} Axis - Frequency Domain)")
    axs[0, 1].set_xlabel("Frequency (Hz)")
    axs[0, 1].set_ylabel("Magnitude")
    axs[0, 1].legend()
    axs[0, 1].grid()
    # axs[1, 1].set_xlim(0, 0.001)

    # Plot velocity signal (time domain)
    axs[1, 0].plot(timestamps / 1000, velo_signal, label=f"Velocity{axis_label} (Time Domain)", color="green")
    axs[1, 0].set_title(f"Velocity Signal ({axis_label} Axis - Time Domain)")
    axs[1, 0].set_xlabel("Time (s)")
    axs[1, 0].set_ylabel("Velocity (m/s)")
    axs[1, 0].legend()
    axs[1, 0].grid()

    # Plot velocity FFT (frequency domain)
    axs[1, 1].plot(positive_frequencies, velo_positive_fft_magnitude, label=f"FFT of Velocity{axis_label} (Frequency Domain)", color="red")
    axs[1, 1].set_title(f"Velocity Signal ({axis_label} Axis - Frequency Domain)")
    axs[1, 1].set_xlabel("Frequency (Hz)")
    axs[1, 1].set_ylabel("Magnitude")
    axs[1, 1].legend()
    axs[1, 1].grid()
    # axs[1, 1].set_xlim(0, 0.001)

    # Plot displacement signal (time domain)
    axs[2, 0].plot(timestamps / 1000, disp_signal, label=f"Disp{axis_label} (Time Domain)", color="purple")
    axs[2, 0].set_title(f"Displacement Signal ({axis_label} Axis - Time Domain)")
    axs[2, 0].set_xlabel("Time (s)")
    axs[2, 0].set_ylabel("Displacement (m)")
    axs[2, 0].legend()
    axs[2, 0].grid()

    # Plot displacement FFT (frequency domain)
    axs[2, 1].plot(positive_frequencies, disp_positive_fft_magnitude, label=f"FFT of Disp{axis_label} (Frequency Domain)", color="brown")
    axs[2, 1].set_title(f"Displacement Signal ({axis_label} Axis - Frequency Domain)")
    axs[2, 1].set_xlabel("Frequency (Hz)")
    axs[2, 1].set_ylabel("Magnitude")
    axs[2, 1].legend()
    axs[2, 1].grid()
    # axs[1, 1].set_xlim(0, 0.001)

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
