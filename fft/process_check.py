import json
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import scipy
import scipy.signal

with open("new.json", "r") as file:
    DecodedRawData = json.load(file)

Fs = 13156.67 #Sampling Freq.
tstep = 1 / Fs   #sample time interval

y = DecodedRawData['raw_data'][0: int(Fs)]
N = len(y) #Numbers of sample of signal
 
v = np.array(y)
rms_value = np.sqrt(np.mean(v**2))
print(f"RMS Value: {rms_value}")

peak_value = np.max(np.abs(y))
print("Peak value:", peak_value)

cf=rms_value/peak_value
print("crest factor:",cf)

velocity = np.cumsum(v)*tstep
print("velocitys:",velocity, "length:",len(velocity))
v_rms=np.sqrt(np.mean(velocity**2))
print("Vrms:",v_rms)

t = np.linspace(0, (N-1)*tstep, N)  #time steps
fstep = Fs / N   #freq interval
f = np.linspace(0, (N-1)*fstep, N) #  freq. steps

x = np.fft.fft(y)
x_mag = np.abs(x) / N

elimination_indices = (f >= 0) & (f < 1)
x_mag[elimination_indices] = 0

f_plot = f[0: int(N/2+1)]
x_mag_plot = 2 * x_mag[0:int(N/2+1)]
x_mag_plot[0] = x_mag_plot[0] / 2
peak=max(y)
# print(peak)
fig, [ax1, ax2] = plt.subplots(nrows=2,ncols=1)
ax1.plot(t,y)
ax2.plot(f_plot,x_mag_plot)

ax1.set_xlabel("Time")
ax1.set_ylabel("Acceleration")
# ax2.set_xlabel("Freq[Hz]")
ax2.set_ylabel("Acceleration")

plt.show()