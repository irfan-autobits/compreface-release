import matplotlib.pyplot as plt
import numpy as np
from scipy.fftpack import fft
import tkinter as tk
from tkinter import filedialog
import time

# Prompt user for file
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(filetypes=[("Two Column CSV", "*.csv")])
print(file_path)

# Load Data (assumes two column array)
tic = time.perf_counter()
t, x = np.genfromtxt(file_path, delimiter=',', unpack=True)
toc = time.perf_counter()
print("Load Time:", toc - tic)

# Determine variables
N = int(np.prod(t.shape))  # Length of the array
Fs = 1 / (t[1] - t[0])     # Sample rate (Hz)
T = 1 / Fs
print("# Samples:", N)

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
w = int(np.floor(Fs))  # Width of the window for computing RMS
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
xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))  # Ensure integer
yf = fft(x)
plt.plot(xf, 2.0 / N * np.abs(yf[: int(N / 2)]))
plt.grid()
plt.xlabel('Frequency (Hz)')
plt.ylabel('Accel (g)')
plt.title('FFT - ' + file_path)
toc = time.perf_counter()
print("FFT Time:", toc - tic)

plt.show()
