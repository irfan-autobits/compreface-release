"""
@file: GbfbSpectrogrammer.py
@brief: Make a spectrogram from a CSV. This code was used to create the images available in the Mide blog
post on Vibrations, Compressors, and Food: Analyzing Vibrations in an Industrial Setting, at
https://blog.mide.com/industrial-vibrations
This code runs with python 2.7, numpy, pandas, and matplotlib, all available in the standard anaconda install package
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
inputFile = Path("SSX56018_6018_DC-Accel.csv")
outputDir = str(Path())

NFFT = 512

def get_slice(inputList, inputRange):
    """
    :param inputList: list of ascending by a consistent step (eg [1, 2, 3], not [1, 2, 4])
    :param inputRange: value range to extract. Not index range
    :return: extracted slice, starting index (from original list), ending index (from original list)
    """
    if inputRange is None:
        return inputList, 0, len(inputList)
    stepSize = inputList[1] - inputList[0]
    start = int(inputRange[0]/stepSize)
    end = int(inputRange[1]/stepSize)
    return inputList[start:end], start, end

def save_3d_plot(x, y, z, file, xRange=None, yRange=None, show=False, norm=None, title=None):
    """
    :param x, y, z:  3D plot inputs. Z must be 2 dimensional array
    :param file: File name to save
    :param xRange: X axis values (not indices) to display
    :param yRange: Y axis values (not indices) to display
    :param show: True to show the plot while software is running
    :param norm: 2 value tuple of normalization range for Z axis data
    :param title: Title to display on plot
    :return: NA
    """
    myNorm = None
    if norm is not None:
        myNorm = matplotlib.colors.Normalize(vmin=norm[1], vmax=norm[0])
    myX, xStart, xEnd = get_slice(x, xRange)
    myY, yStart, yEnd = get_slice(y, yRange)
    myZ = z[yStart:yEnd, xStart:xEnd]
    plt.pcolormesh(myX, myY, myZ, norm=myNorm, cmap='coolwarm')
    if title is not None:
        plt.title(title)
    plt.savefig(file)
    if show:
        plt.show()
    plt.cla()

def generate_spectrogram(dataset, dataAxis=' "Z (DC)"', timeAxis='Time', removeMean=True, NFFT=512, noverlap=0):
    """
    :param dataset: Full pandas set of data
    :param dataAxis: Index of input transform data
    :param timeAxis: Index of time data for transform
    :param removeMean: True to remove the 0 Hz data before transform
    :param NFFT: Fourier window size
    :param noverlap: Number of points to overlap
    :return: Z, frequency list, time list, max of Z, min of Z
    """
    dataLength = len(inputData[dataAxis])
    Fs = dataLength / (inputData[timeAxis][dataLength - 1] - inputData[timeAxis][0])
    if removeMean:
        inputData[dataAxis] -= np.mean(inputData[dataAxis])
    Pxx, freqs, t, im = plt.specgram(inputData[dataAxis], NFFT=NFFT, Fs=Fs, noverlap=noverlap, cmap=plt.cm.viridis)
    return Pxx, freqs, t, np.max(Pxx), np.min(Pxx)


inputData = pd.read_csv(inputFile)
ampX, freqs, t, maxX, minX = generate_spectrogram(inputData, dataAxis=' "X (DC)"', timeAxis='Time',
                                                removeMean=True, NFFT=NFFT, noverlap=0)
ampY, _, __, maxY, minY    = generate_spectrogram(inputData, dataAxis=' "Y (DC)"', timeAxis='Time',
                                                removeMean=True, NFFT=NFFT, noverlap=0)
ampZ, _, __, maxZ, minZ    = generate_spectrogram(inputData, dataAxis=' "Z (DC)"', timeAxis='Time',
                                                removeMean=True, NFFT=NFFT, noverlap=0)
maxVal = np.max([maxX, maxY, maxZ])
minVal = np.min([minX, minY, minZ])
save_3d_plot(t, freqs, ampZ, outputDir + 'Z_Full.png', title="Z Axis")
save_3d_plot(t, freqs, ampZ, outputDir + 'Z_Zoom.png', xRange=(900, 1000), yRange=(0, 250), title="Z Axis")
save_3d_plot(t, freqs, ampX, outputDir + 'X_Full.png', title="X Axis")
save_3d_plot(t, freqs, ampY, outputDir + 'Y_Full.png', title="Y Axis")
