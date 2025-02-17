# Function to calculate velocity RMS for a given sampling frequency
import numpy as np


def calculate_velocity_rms_for_frequency(frequency, duration, gravity_mean, noise_std):
    time = np.linspace(0, duration, int(frequency * duration), endpoint=False)
    raw_acceleration = np.random.normal(gravity_mean, noise_std, len(time))  # Simulate data
    velocity = np.cumsum(raw_acceleration) / frequency  # Integrate acceleration
    velocity_mm_per_sec = velocity * 1000  # Convert to mm/sec
    velocity_rms = np.sqrt(np.mean(velocity_mm_per_sec**2))  # Calculate RMS
    return velocity_rms

# Sampling frequencies from 10 Hz to 1000 Hz
frequencies = np.arange(10, 1001, 10)
velocity_rms_values = [
    calculate_velocity_rms_for_frequency(freq, duration, gravity_mean, noise_std)
    for freq in frequencies
]

# Combine results for output
list(zip(frequencies, velocity_rms_values))


# ===========================
# Corrected function with proper scaling using 9806.65 mm/s² for gravity
def calculate_corrected_velocity_rms_for_frequency(frequency, duration, gravity_mean, noise_std, gravity_mm_per_s2):
    time = np.linspace(0, duration, int(frequency * duration), endpoint=False)
    raw_acceleration = np.random.normal(gravity_mean, noise_std, len(time))  # Simulate data
    acceleration_mm_per_s2 = raw_acceleration * gravity_mm_per_s2 / gravity_mean  # Convert to mm/s²
    velocity = np.cumsum(acceleration_mm_per_s2) / frequency  # Integrate acceleration
    velocity_rms = np.sqrt(np.mean(velocity**2))  # Calculate RMS
    return velocity_rms

# Gravitational constant in mm/s²
gravity_mm_per_s2 = 9806.65

# Recalculate velocity RMS values using corrected scaling
corrected_velocity_rms_values = [
    calculate_corrected_velocity_rms_for_frequency(freq, duration, gravity_mean, noise_std, gravity_mm_per_s2)
    for freq in frequencies
]

# Combine results for output
corrected_results = list(zip(frequencies, corrected_velocity_rms_values))
corrected_results[:10]  # Display the first 10 results as a sample