import numpy as np
from scipy.signal import butter, filtfilt

def integrate_riemann(signal, dx):
    """Integrate using the midpoint Riemann sum."""
    signal = np.cumsum(signal) * dx
    signal -= np.mean(signal)
    return signal

def bandpass_filter(signal, lowcut, highcut, sampling_rate, order=4):
    nyquist = 0.5 * sampling_rate
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)