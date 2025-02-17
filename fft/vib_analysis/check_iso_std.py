import numpy as np
from scipy.integrate import simpson

def calc_rms(i):
    sampling_rate = 13180.4619140625  # Hz
    # Parameters
    Fs = 1000  # Sampling frequency in Hz
    duration = 1  # Duration in seconds
    frequency = 50  # Sine wave frequency in Hz
    amplitude = 1  # Amplitude in G

    # Time vector
    t = np.linspace(0, duration, int(Fs * duration), endpoint=False)

    # Generate sine wave
    raw_data = amplitude * np.sin(2 * np.pi * frequency * t)

    # raw_data = np.array(i['raw_data'][0: int(sampling_rate)])  
    # Example raw data
    # axis = i['axis']

    # Step 1: Calculate RMS of acceleration
    raw_data = np.array(raw_data)
    raw_data = raw_data - np.mean(raw_data)

    a_rms = np.sqrt(np.mean(np.square(raw_data)))

    # Step 2: Calculate velocity RMS
    delta_t = 1 / sampling_rate  # Time interval (s)
    velocity = np.cumsum(raw_data * delta_t) * 1000  # Convert to mm/s
    v_rms = np.sqrt(np.mean(np.square(velocity)))

    # Simpson's Rule
    # time = np.linspace(0, len(raw_data) * delta_t, len(raw_data))
    # velocity_simpson = simpson(raw_data, x=time) * 1000  # mm/s
    # v_rms = np.sqrt(np.mean(np.square(velocity_simpson)))

    # Step 3: Calculate Crest Factor
    peak_acceleration = np.max(np.abs(raw_data))
    crest_factor = peak_acceleration / a_rms

    # fft part
    a_fft_result = np.fft.rfft(raw_data)  # FFT (real-valued input)
    # v_fft_result = np.fft.rfft(velocity)  # FFT (real-valued input)

    # Take the magnitude (absolute value) of the FFT result before calculating RMS
    f_a_rms = np.sqrt(np.mean(np.square(np.abs(a_fft_result))))  # Use abs() to take magnitude
    # f_v_rms = np.sqrt(np.mean(np.square(np.abs(v_fft_result))))  # Use abs() to take magnitude

    # Take the peak magnitude for Crest Factor
    f_peak_acceleration = np.max(np.abs(a_fft_result))
    f_crest_factor = f_peak_acceleration / f_a_rms

    # Step 1: Perform FFT
    freq_min = 10  # Minimum frequency (Hz)
    freq_max = 800  # Maximum frequency (Hz)
    N = len(raw_data)
    fft_result = np.fft.rfft(raw_data)  # Real FFT
    frequencies = np.fft.rfftfreq(N, d=1/sampling_rate)  # Frequency bins
    amplitudes = np.abs(fft_result) / (N/2)  # Normalize amplitude

    # velo
    # velocity_fft = np.fft.rfft(velocity)  # Real FFT
    # velo_fft_magnitude = (2 / N) * np.abs(velocity_fft[:N // 2])  # Amplitude spectrum
    # velo_rms_fft = np.sqrt((2 / N) ** 2 * np.sum(np.abs(velocity_fft[:N // 2]) ** 2))

    # Step 2: Filter frequencies
    freq_filter = (frequencies >= freq_min) & (frequencies <= freq_max)
    filtered_amplitudes = amplitudes[freq_filter]

    # Step 3: Calculate RMS from FFT
    aRMS_fft = np.sqrt(np.sum(filtered_amplitudes**2))
    # Header line
    print(f"{'-'*100}")  
    # print(f"{'Time Domain':<45} | {'Frequency Domain':<45} {axis}")
    print(f"{'-'*100}")  

    # Data rows
    print(f"{'Acceleration RMS (aRMS):':<27} {a_rms:>10.6f} m/s² | {'Acceleration RMS (aRMS):':<25} {f_a_rms:>10.6f} m/s²")
    print(f"{'Acceleration RMS (aRMS):':<27} {a_rms:>10.6f} m/s² | {'Acceleration RMS (aRMS):':<25} {aRMS_fft:>10.6f} m/s²")
    print(f"{'Velocity RMS (vRMS):':<25} {v_rms:>10.6f} mm/s     | {'Velocity RMS (vRMS):':<25} {v_rms:>10.6f} mm/s")
    print(f"{'Crest Factor (CF):':<25} {crest_factor:>10.6f}          | {'Crest Factor (CF):':<25} {f_crest_factor:>10.6f}")
    print(f"{'-'*100}")  

