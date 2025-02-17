
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import time
import pyfftw
import os
 
#####
# Functions for testing various FFT methods
#####
 
 
def fftw_builder_test(input_data):
    pyfftw.forget_wisdom()       # This is just here to keep the tests honest, normally pyfftw will remember setup parameters and go more quickly when it is run a second time
    a = np.array(input_data, dtype='float32')   # This turns the input list into a numpy array. We can make it a 32 bit float because the data is all real, no imaginary component
    fft_obj = pyfftw.builders.rfft(a)           # This creates an object which generates the FFT
    return fft_obj()                            # And calling the object returns the FFT
 
 
def fftw_fast_builder_test(input_data): # See fftw_builder_test for comments
    pyfftw.forget_wisdom()
    a = np.array(input_data, dtype='float32')
    fft_obj = pyfftw.builders.rfft(a, planner_effort='FFTW_ESTIMATE')   # FFTW_ESTIMATE is a lower effort planner than the default. This seems to work more quickly for over 8000 points
    return fft_obj()
 
def fftw_test(input_data):
    pyfftw.forget_wisdom()                  # This is just here to keep the tests honest
    outLength = len(input_data)//2 + 1      # For a real FFT, the output is symetrical. fftw returns only half the data in this case
    a = pyfftw.empty_aligned(len(input_data), dtype='float32')      # This is the input array. It will be cleared when the fft object is created
    outData = pyfftw.empty_aligned(outLength, dtype='complex64')    # This is the output array. Not that the size and type must be appropriate
    fft_obj = pyfftw.FFTW(a, outData, flags=('FFTW_ESTIMATE',),planning_timelimit=1.0)  # NB: The flags tuple has a comma
    a[:] = np.array(input_data, dtype='float32')    # We have to fill the array after fft_obj is created. NB: 'a[:] =' puts data into the existing array, 'a =' creates a new array
    return fft_obj()                        # Calling the object returns the FFT of the data now in a. The result is also in outData
 
 
def fftw_test_complex(input_data):  # This is fftw_test but running a complex FFT as opposed to a real input FFT. See fftw_test for comments
    pyfftw.forget_wisdom()
    outLengthMod = len(input_data)//2 + 1   # Size of expected return data
    outLength = len(input_data)             # For a complex input FFT, we get more data
    a = pyfftw.empty_aligned(len(input_data), dtype='complex64')    # The FFTW determines the type of FFT by the type of input
    outData = pyfftw.empty_aligned(outLength, dtype='complex64')
    fft_obj = pyfftw.FFTW(a, outData, flags=('FFTW_ESTIMATE',),planning_timelimit=1.0)
    a[:] = np.array(input_data, dtype='complex64')
    return fft_obj()[0:outLengthMod]
 
 
def fftw_test_default(input_data):  # This is fftw_test with different FFTW options. See fftw_test for comments
    pyfftw.forget_wisdom()
    outLength = len(input_data)//2 + 1
    a = pyfftw.empty_aligned(len(input_data), dtype='float32')
    outData = pyfftw.empty_aligned(outLength, dtype='complex64')
    fft_obj = pyfftw.FFTW(a, outData)
    a[:] = np.array(input_data, dtype='float32')
    return fft_obj()
 
 
def fftw_test_no_limit(input_data): # This is fftw_test with different FFTW options. See fftw_test for comments
    pyfftw.forget_wisdom()
    outLength = len(input_data)//2 + 1
    a = pyfftw.empty_aligned(len(input_data), dtype='float32')
    outData = pyfftw.empty_aligned(outLength, dtype='complex64')
    fft_obj = pyfftw.FFTW(a, outData, flags=('FFTW_ESTIMATE',))
    a[:] = np.array(input_data, dtype='float32')
    return fft_obj()
 
 
def fftw_test_no_flag(input_data):      # This is fftw_test with different FFTW options. See fftw_test for comments
    pyfftw.forget_wisdom()
    outLength = len(input_data)//2 + 1
    a = pyfftw.empty_aligned(len(input_data), dtype='float32')
    outData = pyfftw.empty_aligned(outLength, dtype='complex64')
    fft_obj = pyfftw.FFTW(a, outData,planning_timelimit=1.0)
    a[:] = np.array(input_data, dtype='float32')
    return fft_obj()
 
 
def numpy_test(inputData):
    return np.fft.rfft(inputData)       # Numpy is nice and simple!
 
 
#####
# Helper Functions
#####
 
def write_csv(csv_file_name, headers, data):        # Helper function for writing to the CSV file
    outString = ""
    for header in headers:
        outString += "%s," % (data.get(header, ""))
    outString += "\n"
    with open(csv_file_name, 'a') as f:
        f.write(outString)
 
 
#Prompt user for file
###
# RUN TIME OPTION!
# Set include_plots to True if you want to actually see the plot outputs. They will all be stored up and displayed
# at the end of the test
include_plots = True
if include_plots:
    root = tk.Tk()
    root.withdraw()
file_paths = filedialog.askopenfilenames(filetypes=[("Two Column CSV","*.csv")])
out_path = filedialog.asksaveasfilename(defaultextension=".csv")
print(file_paths)
 
# CSV Setup
output_headers = ["File", "File Size", "Number of Points", "FFT Time", "FFT Function", "Load Time", "Plot Time", "RMS Time" ]
with open(out_path, 'w+') as f:
    f.write(",".join(output_headers)+"\n")
 
# Tests to run:
# Format { "Name" : Function, etc } Test order is undefined
#test_functions = {"FFTW" : fftw_test, "FFTW-Complex" : fftw_test_complex, "FFTW-Builder": fftw_builder_test, "FFTW-Default" : fftw_test_default, "FFTW-NoLimit": fftw_test_no_limit, "FFTW-NoFlag": fftw_test_no_flag}
test_functions = {"FFTW" : fftw_test, "Builder": fftw_fast_builder_test}
figure_count = 1
# Loop through each file
for file_path in file_paths:
    # output_data holds the test info and results. This is written to the file after the FFT is complete
    output_data = {"File" : os.path.split(file_path)[-1]}
    output_data["File Size"] = os.path.getsize(file_path)
    tic = time.perf_counter()
    df = pd.read_csv(file_path,delimiter=',',header=None,names=["time","data"])
    t = df["time"]
    x = df["data"]
    toc = time.perf_counter()
    output_data["Load Time"] = toc-tic
    print("Load Time:",toc-tic)
 
    N = int(np.prod(t.shape))#length of the array
    # Determine variables
    Fs = 1/(t[1]-t[0])  #sample rate (Hz)
    T = 1/Fs
    output_data["Number of Points"] = N
    print("# Samples:",N)
 
    # Plot Data
    if include_plots:
        plt.figure(figure_count)
        figure_count += 1
        plt.plot(t, x)  #x
        plt.xlabel('Time (seconds)')
        plt.ylabel('Accel (g)')
        plt.title(file_path)
        plt.grid()
 
    # Compute RMS and Plot
    tic = time.perf_counter()
    w = int(np.floor(Fs))         #width of the window for computing RMS
    steps = np.int_(np.floor(N/w))   #Number of steps for RMS
    t_RMS = np.zeros((steps,1))      #Create array for RMS time values
    x_RMS = np.zeros((steps,1))      #Create array for RMS values
    for i in range (0, steps):
        t_RMS[i] = np.mean(t[(i*w):((i+1)*w)])
        x_RMS[i] = np.sqrt(np.mean(x[(i*w):((i+1)*w)]**2))
    if include_plots:
        plt.figure(figure_count)
        figure_count += 1
        plt.plot(t_RMS, x_RMS)
        plt.xlabel('Time (seconds)')
        plt.ylabel('RMS Accel (g)')
        plt.title('RMS - ' + file_path)
        plt.grid()
    toc = time.perf_counter()
    output_data["RMS Time"] = toc-tic
    print("RMS Time:",toc-tic)
 
    # Compute and Plot FFT
    # Run through each FFT function in test_functions, and test each one.
    # File data is not reloaded
    for func_name in test_functions:
        output_data["FFT Function"] = func_name
        tic = time.perf_counter()
        fftData = test_functions[func_name](x)          # Execute the FFT
        xf = np.linspace(0.0, 1.0/(2.0*T), len(fftData))
        if include_plots:
            plt.figure(figure_count)
            figure_count += 1
            plt.plot(xf, 2.0/N * np.abs(fftData))       #[0:int(N/2)]
            plt.grid()
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Accel (g)')
            plt.title('FFT (%s) - %s' % (func_name, file_path))
        toc = time.perf_counter()
        output_data["FFT Time"] = toc-tic
        print("FFT Time:",toc-tic)
        write_csv(out_path, output_headers, output_data)
if include_plots:
    print("Plotting...")
    plt.show()
print("Done!")
 