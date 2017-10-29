#!/usr/bin/env python3

from __future__ import print_function, division

import sys
from select import select
from array import array

import pyaudio
import numpy as np
import matplotlib.pyplot as plt


FORMAT = pyaudio.paInt16
CHUNK_SIZE = 128            # Depends on human persistence of hearing
RATE = 2048                 # Depends on desired frequencies to capture
RESOLUTION = 0.5            # Desired resolution in Hz
THRESHOLD = 20000           # Minimum amplitude of the largest frequency spike
KAISER_BETA = 7.5           # The `beta' parameter of the Kaiser window


def tune(plotfreq=False, plottime=False, input_device_index=None):
    # Set up the Kaiser window
    n = np.arange(CHUNK_SIZE) + 0.5  # Assuming CHUNK_SIZE is even
    x = (n - CHUNK_SIZE / 2) / (CHUNK_SIZE / 2)
    window = np.i0(KAISER_BETA * np.sqrt(1 - x ** 2)) / np.i0(KAISER_BETA)

    # Get audio data
    p = pyaudio.PyAudio()
    #device_info = p.get_device_info_by_index(input_device_index)
    #print(device_info)
    stream = p.open(format=FORMAT, channels=1, rate=RATE, input=True,
                    input_device_index=input_device_index,
                    frames_per_buffer=CHUNK_SIZE)

    if plotfreq or plottime:
        # Set up plotting paraphernalia
        plt.interactive(True)
        if plottime:
            figtime = plt.figure()
            axtime = figtime.gca()
        if plotfreq:
            figfreq = plt.figure()
            axfreq = figfreq.gca()

    print('Press return to stop...')

    i = 0
    while 1:
        i += 1

        # Check if something has been input. If so, exit.
        if sys.stdin in select([sys.stdin, ], [], [], 0)[0]:
            # Absorb the input and break
            sys.stdin.readline()
            break

        # Acquire sound data
        snd_data = array('h', stream.read(CHUNK_SIZE))
        signal = np.array(snd_data, dtype=float)
        #if sys.byteorder == 'big':
            #snd_data.byteswap()

        if plottime:
            if i > 1:
                axtime.lines.remove(timeline)
            [timeline, ] = axtime.plot(signal, 'b-')
            figtime.canvas.draw()

        # Apply a Kaiser window on the signal before taking the FFT. This
        # makes the signal look better if it is periodic. Derivatives at the
        # edges of the signal match better, which means that the frequency
        # domain will have fewer side-lobes. However, it does cause each spike
        # to grow a bit broader.
        # One can change the value of beta to tradeoff between side-lobe height
        # and main lobe width.
        signal *= window
        spectrum = np.fft.rfft(signal, int(RATE / RESOLUTION))
        peak = np.argmax(abs(spectrum))         # peak directly gives the
                                                # desired frequency
        # Threshold on the maximum peak present in the signal (meaning we
        # expect the signal to be approximately unimodal)
        if spectrum[peak] > THRESHOLD:
            # Put a band-pass filter in place to look at only those frequencies
            # we want. The desired peak is the harmonic located in the
            # frequency region of interest.
            desired_peak = np.argmax(abs(spectrum[90:550]))
            print(desired_peak)

            if plotfreq:
                try:
                    axfreq.lines.remove(freqline)
                except UnboundLocalError:
                    pass
                [freqline, ] = axfreq.plot(abs(spectrum), 'b-')
                figfreq.canvas.draw()

    stream.stop_stream()
    stream.close()
    p.terminate()
