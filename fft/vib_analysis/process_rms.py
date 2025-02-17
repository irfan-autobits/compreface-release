import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import get_window
from matplotlib import pyplot as plt
import numpy as np
from scipy.integrate import cumulative_trapezoid

def gen_sine(t):
    # Generate sine waves
    frequencies = [55, 78, 21, 42]  # Hz
    amplitudes = [1.0, 1.0, 1.0, 1.0]  # m/s^2
    phases = [0, np.pi , np.pi , 0]  # Phase offsets

    # Combine sine waves to form acceleration signal
    acceleration_signal = sum(
        amp * np.sin(2 * np.pi * freq * t + phase)
        for amp, freq, phase in zip(amplitudes, frequencies, phases)
    )
    Theo_test(amplitudes, frequencies)
    # Plot the acceleration signal
    plt.figure(figsize=(10, 4))
    plt.plot(t, acceleration_signal, label="Acceleration Signal")
    plt.title("Acceleration Signal (Time Domain)")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration (m/s²)")
    plt.legend()
    plt.grid()
    plt.show()

    return acceleration_signal

def Theo_test(amplitudes, frequencies):
    # Theoretical RMS of acceleration
    aRMS_theoretical = np.sqrt(sum((amp ** 2) / 2 for amp in amplitudes))
    print(f"Theoretical aRMS: {aRMS_theoretical:.6f}")

    # Theoretical RMS of velocity
    vRMS_theoretical = np.sqrt(
        sum((amp / (2 * np.pi * freq)) ** 2 / 2 for amp, freq in zip(amplitudes, frequencies))
    )
    print(f"Theoretical vRMS: {vRMS_theoretical:.6f}")


def calc_rms(i):
    sampling_rate = 13180.4619140625  # Hz
    # Parameters
    # sampling_rate = 1000  # Hz
    duration = 2  # seconds
    t = np.linspace(0, duration, int(sampling_rate * duration), endpoint=False)  # Time vector

    # acceleration_signal = np.array(i['raw_data'][0: int(sampling_rate)])  
    acceleration_signal = gen_sine(t)

    # Numerical integration for velocity
    velocity_signal = cumulative_trapezoid(acceleration_signal, dx=1/sampling_rate, initial=0)

    # Remove DC offset from velocity
    velocity_signal -= np.mean(velocity_signal)

    # Perform FFT on acceleration signal
    N = len(acceleration_signal)
    fft_acc = np.fft.fft(acceleration_signal)
    frequencies_fft = np.fft.fftfreq(N, d=1 / sampling_rate)  # Frequency bins
    fft_acc_magnitude = (2 / N) * np.abs(fft_acc[:N // 2])  # Single-sided spectrum

    # Perform FFT on velocity signal
    N = len(velocity_signal)
    fft_velo = np.fft.fft(velocity_signal)
    frequencies_fft = np.fft.fftfreq(N, d=1 / sampling_rate)  # Frequency bins
    fft_velo_magnitude = (2 / N) * np.abs(fft_velo[:N // 2])  # Single-sided spectrum

    # Remove DC component
    fft_acc_magnitude = fft_acc_magnitude[1:]
    fft_velo_magnitude = fft_velo_magnitude[1:]

    # Compute RMS from FFT
    a_rms_freq = np.sqrt(np.sum(fft_acc_magnitude ** 2))
    v_rms_freq = np.sqrt(np.sum(fft_velo_magnitude ** 2))

    # Computed RMS values
    aRMS_computed = np.sqrt(np.mean(acceleration_signal**2))
    vRMS_computed = np.sqrt(np.mean(velocity_signal**2))


    print(f"Computed aRMS: {aRMS_computed:.6f} vRMS: {vRMS_computed:.6f}")
    print(f"fft aRMS: {a_rms_freq:.6f} vRMS: {v_rms_freq:.6f}")

calc_rms(1)