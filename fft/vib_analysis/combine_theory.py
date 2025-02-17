import numpy as np
from scipy.integrate import cumulative_trapezoid
from call_fn import integrate_fft, integrate_riemann, compute_rms, compute_fft, compute_fft_rms, plot_signals

# Define signals as (frequency, amplitude, phase)
signals = [
    (30, 1, 0),              # R phase
    (30, 1, 2 * np.pi / 3),  # Y phase
    (30, 1, 4 * np.pi / 3),  # B phase
]
sampling_rate = 1000  # Hz
duration = 1  # seconds
t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

# Generate acceleration signal
acceleration_signal = sum(
    amp * np.sin(2 * np.pi * freq * t + phase) for freq, amp, phase in signals
)
acceleration_signal -= np.mean(acceleration_signal)
N = len(acceleration_signal)
acceleration_signal = acceleration_signal * 9806.65

# Velocity and displacement using FFT integration
# velocity_signal = integrate_fft(acceleration_signal, sampling_rate)
# dis_signal = integrate_fft(velocity_signal, sampling_rate)
# # Numerical integration for velocity
# velocity_signal = cumulative_trapezoid(acceleration_signal, dx=1/sampling_rate, initial=0)
# dis_signal = cumulative_trapezoid(velocity_signal, dx=1/sampling_rate, initial=0)

velocity_signal = integrate_riemann(acceleration_signal, sampling_rate)
velocity_signal -= np.mean(velocity_signal)

dis_signal = integrate_riemann(velocity_signal, sampling_rate)
dis_signal -= np.mean(dis_signal)

# Compute time-domain RMS
aRMS_computed = compute_rms(acceleration_signal)
vRMS_computed = compute_rms(velocity_signal)
dRMS_computed = compute_rms(dis_signal)

# Compute FFT
a_fft_signal = compute_fft(acceleration_signal, N, sampling_rate)
v_fft_signal = compute_fft(velocity_signal, N, sampling_rate)
d_fft_signal = compute_fft(dis_signal, N, sampling_rate)

# Compute FFT RMS
aRMS_fft = compute_fft_rms(a_fft_signal)
vRMS_fft = compute_fft_rms(v_fft_signal)
dRMS_fft = compute_fft_rms(d_fft_signal)

# Results
print(f"Computed aRMS (time-domain): {aRMS_computed:.6f}")
print(f"Computed vRMS (time-domain): {vRMS_computed:.6f}")
print(f"Computed dRMS (time-domain): {dRMS_computed:.6f}")
print(f"FFT aRMS: {aRMS_fft:.6f}")
print(f"FFT vRMS: {vRMS_fft:.6f}")
print(f"FFT dRMS: {dRMS_fft:.6f}")

# Time-domain energy
time_energy_acc = np.sum(acceleration_signal**2)
time_energy_velo = np.sum(velocity_signal**2)
time_energy_disp = np.sum(dis_signal**2)

# Frequency-domain energy (correct scaling)
fft_energy_acc = np.sum(np.abs(a_fft_signal)**2) * (N / 2)
fft_energy_velo = np.sum(np.abs(v_fft_signal)**2) * (N / 2)
fft_energy_disp = np.sum(np.abs(d_fft_signal)**2) * (N / 2)

print(f"Time Domain Energy (Acceleration): {time_energy_acc:.6f}")
print(f"Time Domain Energy (Velocity): {time_energy_velo:.6f}")
print(f"Time Domain Energy (Displacement): {time_energy_disp:.6f}")

print(f"FFT Energy (Acceleration): {fft_energy_acc:.6f}")
print(f"FFT Energy (Velocity): {fft_energy_velo:.6f}")
print(f"FFT Energy (Displacement): {fft_energy_disp:.6f}")

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
# frequencies_fft = np.fft.fftfreq(N, d=1 / sampling_rate)  # Frequency bins
# print("frequencies_fft",frequencies_fft)
# print("v_fft_signal",v_fft_signal)

# Call the plotting function
plot_signals(duration, sampling_rate, N, acceleration_signal, velocity_signal, a_fft_signal, v_fft_signal, dis_signal, d_fft_signal)