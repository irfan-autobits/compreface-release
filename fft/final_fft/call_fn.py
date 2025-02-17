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

def integrate_riemann(signal, frequency):
    """Integrate using the midpoint Riemann sum."""
    return np.cumsum(signal) / frequency

def new_rms(raw_acceleration, frequency):
    velocity = np.cumsum(raw_acceleration) / frequency  # Integrate acceleration
    velocity_mm_per_sec = velocity * 1000  # Convert to mm/sec
    velocity_rms = np.sqrt(np.mean(velocity_mm_per_sec**2))  # Calculate RMS
    return velocity_rms

def compute_rms(signal):
    """Compute RMS of a time-domain signal."""
    return np.sqrt(np.mean(signal**2))

def compute_fft(signal, N, sampling_rate):
    """Compute RMS from the FFT spectrum of a signal."""
    fft_result = np.fft.fft(signal)
    fft_magnitude = (2 / N) * np.abs(fft_result[:N // 2])  # Single-sided spectrum
    fft_magnitude = fft_magnitude[1:]  # Remove DC component
    
    return fft_magnitude

def compute_fft_rms(fft_magnitude):
    """Compute RMS from the FFT spectrum of a signal."""
    return np.sqrt(np.sum(fft_magnitude**2) * 2) / 2

def plot_signals(duration, sampling_rate, N, acceleration_signal, velocity_signal, fft_acc_magnitude, fft_velo_magnitude, dis_signal, d_fft_signal):
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # Make sure frequencies_fft and fft_acc_magnitude have the same length
    frequencies_fft = np.fft.fftfreq(N, d=1 / sampling_rate)  # Frequency bins

    # Combine the four plots in one figure with subplots
    fig, axs = plt.subplots(3, 2, figsize=(14, 8))

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
    # Set the x-axis limits to zoom in on the first 10,000 Hz
    axs[0, 1].set_xlim(0, 200)  

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
    axs[1, 1].set_xlim(0, 200)  

    # Plot the displacement signal
    axs[2, 0].plot(t, dis_signal, label="Displacement Signal")
    axs[2, 0].set_title("Displacement Signal (Time Domain)")
    axs[2, 0].set_xlabel("Time (s)")
    axs[2, 0].set_ylabel("Displacement (m)")
    axs[2, 0].legend()
    axs[2, 0].grid()
    # Plot the FFT of the displacement signal
    axs[2, 1].plot(frequencies_fft[1:len(frequencies_fft)//2], d_fft_signal, label="FFT of Displacement Signal")
    axs[2, 1].set_title("Displacement Signal (Frequency Domain)")
    axs[2, 1].set_xlabel("Frequency (Hz)")
    axs[2, 1].set_ylabel("Magnitude")
    axs[2, 1].legend()
    axs[2, 1].grid()
    axs[2, 1].set_xlim(0, 200)  

    # Adjust layout
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
