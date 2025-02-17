import numpy as np
from scipy.signal import butter, filtfilt
from scipy.integrate import cumulative_trapezoid

# Example vibration signal parameters
sampling_rate = 1000  # Hz
duration = 1  # seconds
frequencies = [25, 100, 300]  # Hz
amplitudes = [0.1, 0.05, 0.02]  # mm/s^2
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# Generate synthetic acceleration signal
acceleration_signal = sum(
    amp * np.sin(2 * np.pi * freq * t) for amp, freq in zip(amplitudes, frequencies)
)
# Band-pass filter (10 Hz to 499 Hz)
def bandpass_filter(signal, lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs  # Nyquist frequency
    low = lowcut / nyquist
    high = highcut / nyquist
    if not (0 < low < 1 and 0 < high < 1):
        raise ValueError("Cutoff frequencies must be between 0 and the Nyquist frequency.")
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

# Apply the bandpass filter with adjusted highcut
filtered_signal = bandpass_filter(acceleration_signal, 10, 499, sampling_rate)

# Convert acceleration to velocity using numerical integration
velocity_signal = cumulative_trapezoid(filtered_signal, dx=1/sampling_rate, initial=0)

# Compute RMS velocity
vRMS = np.sqrt(np.mean(velocity_signal**2))
print(f"RMS Velocity: {vRMS:.6f} mm/s")

# ISO 10816 thresholds (example values)
if vRMS < 2.3:
    severity = "Zone A: Good"
elif vRMS < 4.5:
    severity = "Zone B: Satisfactory"
elif vRMS < 7.1:
    severity = "Zone C: Unsatisfactory"
else:
    severity = "Zone D: Dangerous"

print(f"Vibration Severity: {severity}")
