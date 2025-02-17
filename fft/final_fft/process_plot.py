import json
import numpy as np
import socketio
from scipy.integrate import cumulative_trapezoid
# from call_fn import bandpass_filter, integrate_riemann, compute_rms, compute_fft, compute_fft_rms, plot_signals
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


def calc_rms(i):
    # Processing raw data
    sampling_rate = 13156.67  # Sampling frequency
    acceleration_signal = np.array(i['raw_data'][0:int(sampling_rate)])
    axis = i["axis"]
    acceleration_signal = bandpass_filter(acceleration_signal, 10, 1000, sampling_rate)
    duration = len(acceleration_signal) / sampling_rate
    acceleration_signal -= np.mean(acceleration_signal)

    # Numerical integration for velocity and displacement
    velocity_signal = integrate_riemann(acceleration_signal, sampling_rate)
    velocity_signal -= np.mean(velocity_signal)
    velocity_signal *= 1000  # Scale velocity

    dis_signal = integrate_riemann(velocity_signal, sampling_rate)
    dis_signal -= np.mean(dis_signal)

    # Compute FFT and prepare data for plotting
    N = len(acceleration_signal)
    a_fft_signal = compute_fft(acceleration_signal, N, sampling_rate)
    v_fft_signal = compute_fft(velocity_signal, N, sampling_rate)
    d_fft_signal = compute_fft(dis_signal, N, sampling_rate)

    frequencies_fft = np.fft.fftfreq(N, d=1 / sampling_rate)  # Frequency bins
    freq = frequencies_fft[1:len(frequencies_fft) // 2]
    # plot_signals(duration, sampling_rate, N, acceleration_signal, velocity_signal, a_fft_signal, v_fft_signal, dis_signal, d_fft_signal)

    # Prepare plot data
    plot_sig = {
        "fft": {
            "freq_bin": freq.tolist(),
            "velocity": v_fft_signal.tolist(),
            "displacement": d_fft_signal.tolist(),
            "acceleration": a_fft_signal.tolist(),
        }
    }
    return plot_sig


def send_to_socket(data):
    sio = socketio.Client()
    # try:
    # Include the token in the URL as a query parameter
    sio.connect('http://192.168.1.213:3001?token=yqjdHAvNM2y6kB2r2Lq7PLEXEtXTnPF6')
    print("connected")
    sio.emit("custom_socket_data", data)  # Emit data
    print("Data sent successfully!")
    # except Exception as e:
    #     print(f"Error: {e}")
    # finally:
    #     sio.disconnect()
