import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft
from scipy import signal
import tkinter as tk
from tkinter import filedialog
import time
from call_func import integrate_riemann, bandpass_filter

# Prompt user for file
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("Two Column CSV", "*.csv")])
print(file_path)

def gen_signal(Fs):
    # Define signals as (frequency, amplitude, phase)
    signals = [
        (3, 1, 0),      
        (70, 1, np.pi/2),
        # (30, 1, np.pi),  
        # (40, 1, 0),      
    ]
    sampling_rate = Fs  # Hz
    duration = 4  # seconds
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)

    # Generate acceleration signal
    acceleration_signal = sum(
        amp * np.sin(2 * np.pi * freq * t + phase) for freq, amp, phase in signals
    )
    acceleration_signal -= np.mean(acceleration_signal)
    return t, acceleration_signal

# Load Data (assumes two column array)
tic = time.perf_counter()
t, x = np.genfromtxt(file_path, delimiter=',', unpack=True)
toc = time.perf_counter()
print("Load Time:", toc - tic)

# Determine variables
N = int(np.prod(t.shape))  # Length of the array
Fs = 1 / (t[1] - t[0])     # Sample rate (Hz)
T = 1 / Fs                 # Sampling interval

# Fs = 2500
# t ,x  = gen_signal(Fs)
# N = len(x)
# T = 1 / Fs                 # Sampling interval
# x = x * 9806.65
print("# Samples:", N)
print("Sample rate", Fs)

# Plot Data
tic = time.perf_counter()
plt.figure(1)
plt.plot(t, x)
plt.xlabel('Time (seconds)')
plt.ylabel('Accel (g)')
plt.title(file_path)
plt.grid()
toc = time.perf_counter()
print("Plot Time:", toc - tic)


# Compute RMS and Plot
tic = time.perf_counter()
w = int(np.floor(Fs))      # Width of the window for computing RMS
steps = int(np.floor(N / w))  # Number of steps for RMS
t_RMS = np.zeros(steps)       # Create array for RMS time values
x_RMS = np.zeros(steps)       # Create array for RMS values
for i in range(steps):
    t_RMS[i] = np.mean(t[i * w : (i + 1) * w])
    x_RMS[i] = np.sqrt(np.mean(x[i * w : (i + 1) * w]**2))
plt.figure(2)
plt.plot(t_RMS, x_RMS)
plt.xlabel('Time (seconds)')
plt.ylabel('RMS Accel (g)')
plt.title('RMS - ' + file_path)
plt.grid()
toc = time.perf_counter()
print("RMS Time:", toc - tic)

# Compute and Plot FFT
tic = time.perf_counter()
plt.figure(3)
xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))  # Fixed to ensure int type
yf = fft(x)
plt.plot(xf, 2.0 / N * np.abs(yf[: int(N / 2)]))
plt.grid()
plt.xlabel('Frequency (Hz)')
plt.ylabel('Accel (g)')
plt.title('FFT - ' + file_path)
toc = time.perf_counter()
print("FFT Time:", toc - tic)

# Plot Data-------- velo
velo_x = integrate_riemann(x, dx=T)
velo_x = bandpass_filter(velo_x, 10, 1000, Fs)
tic = time.perf_counter()
plt.figure(5)
plt.plot(t, velo_x)
plt.xlabel('Time (seconds)')
plt.ylabel('velo (g)')
plt.title(file_path)
plt.grid()
toc = time.perf_counter()
print("Plot Time:", toc - tic)

# Compute and Plot FFT-------- velo
tic = time.perf_counter()
plt.figure(6)
xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))  # Fixed to ensure int type
yf = fft(velo_x)
# V_f = yf[500: int(N / 2)] / (1j * 2 * np.pi * xf[500:]) 
plt.plot(xf, 2.0 / N * np.abs(yf[: int(N / 2)]))
plt.grid()
plt.xlabel('Frequency (Hz)')
plt.ylabel('Velo (g)')
plt.title('FFT - ' + file_path)
toc = time.perf_counter()
ax = plt.gca()  # Get current axes
# ax.set_xlim(0, 100)  # Set x-axis limit to 100 Hz
print("FFT Time:", toc - tic)

# Compute and Plot Spectrogram
tic = time.perf_counter()
plt.figure(4)
f, t2, Sxx = signal.spectrogram(x, Fs, nperseg=int(Fs / 4))  # Fixed `nperseg` to int
plt.pcolormesh(t2, f, np.log(Sxx), shading='gouraud')
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.title('Spectrogram - ' + file_path)
toc = time.perf_counter()
print("Spectrogram Time:", toc - tic)
plt.show()
