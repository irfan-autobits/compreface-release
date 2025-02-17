import numpy as np
from scipy.integrate import cumulative_trapezoid
from call_fn import bandpass_filter, integrate_fft, compute_rms, compute_fft, compute_fft_rms, integrate_riemann, plot_signals, new_rms

def calc_rms(i):
    sampling_rate = 13156.67 #Sampling Freq.
    acceleration_signal = np.array(i['raw_data'][0:int(sampling_rate)])  
    # Apply the filter
    acceleration_signal = bandpass_filter(acceleration_signal, 10, 1000, sampling_rate)
    # acceleration_signal_mul = acceleration_signal * (9806.65)

    duration = len(acceleration_signal) / sampling_rate
    acceleration_signal -= np.mean(acceleration_signal)
    N = len(acceleration_signal)

    vRMS = new_rms(acceleration_signal, sampling_rate)
    print(f"new rms {vRMS}")

    # Numerical integration for velocity
    # velocity_signal = cumulative_trapezoid(acceleration_signal, dx=1/sampling_rate, initial=0)
    # dis_signal = cumulative_trapezoid(velocity_signal, dx=1/sampling_rate, initial=0)
    velocity_signal = integrate_riemann(acceleration_signal, sampling_rate)
    # velocity_signal = bandpass_filter(velocity_signal, 10, 1000, sampling_rate)

    velocity_signal -= np.mean(velocity_signal)
    velocity_signal = velocity_signal * 1000

    dis_signal = integrate_riemann(velocity_signal, sampling_rate)
    # dis_signal = bandpass_filter(dis_signal, 10, 1000, sampling_rate)

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
    print(f"Computed RMS (time-domain):aRMS {aRMS_computed:.6f} vRMS: {vRMS_computed:.6f} dRMS: {dRMS_computed:.6f}")
    print(f"{'FFT aRMS:':<31} {aRMS_fft:.6f} vRMS: {vRMS_fft:.6f} dRMS: {dRMS_fft:.6f}")
    print(f"{'-'*100}")  

    # Call the plotting function
    plot_signals(duration, sampling_rate, N, acceleration_signal, velocity_signal, a_fft_signal, v_fft_signal, dis_signal, d_fft_signal)
