import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import convolve
import sounddevice as sd

# a
fs_impr, impr = wavfile.read("roomIR.wav")

# 如果是立体声，转单声道
if len(impr.shape) > 1:
    impr = impr.mean(axis=1)

# b
plt.figure(figsize=(10, 4))
plt.plot(impr)
plt.xlabel("Samples")
plt.ylabel("Amplitude")
plt.title("Room Impulse Response")
plt.grid(True)
plt.show()

# 播放 impulse response
sd.play(impr, fs_impr)
sd.wait()

# c
fs_y, y = wavfile.read("convolution.wav")

if len(y.shape) > 1:
    y = y.mean(axis=1)

# d
x = convolve(y, impr)

plt.figure(figsize=(10, 4))
plt.plot(x)
plt.xlabel("Samples")
plt.ylabel("y's impulse response")
plt.title("Convolution Result")
plt.grid(True)
plt.show()
