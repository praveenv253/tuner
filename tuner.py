#!/usr/bin/env python

from sys import byteorder
from array import array

import pyaudio
import numpy as np
import matplotlib.pyplot as plt

FORMAT = pyaudio.paInt16
CHUNK_SIZE = 128            # Depends on human persistence of hearing
RATE = 2048                 # Depends on desired frequencies to capture
RESOLUTION = 0.5            # Desired resolution in Hz
THRESHOLD = 2000

if __name__ == '__main__':
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE, input=True,
                    output=True, frames_per_buffer=CHUNK_SIZE)

    i = 0
    #plt.ion()
    #plt.figure(0)
    while 1:
        plt.clf()
        i += 1

        # Little endian, signed short
        snd_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            snd_data.byteswap()

        signal = np.array(snd_data)
        #signal_repeated = np.zeros(1,)
        #for i in range(int(np.ceil(float(RATE) / CHUNK_SIZE))):
        #    signal_repeated = np.hstack((signal_repeated, signal))

        spectrum = np.fft.rfft(signal, int(RATE / RESOLUTION))
        peak = np.argmax(abs(spectrum))         # peak directly gives the
                                                # desired frequency
        if spectrum[peak] < THRESHOLD:
            continue

        print peak
        #plt.plot(abs(spectrum))
        #plt.draw()

    stream.stop_stream()
    stream.close()
    p.terminate()

