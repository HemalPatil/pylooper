from PyQt5 import QtWidgets
from ui import PyLooperWindow

import numpy as np
import pyaudio
import sys

# Start PyAudio session
pa = pyaudio.PyAudio()

input_devices = []
output_devices = []

# Get the list of devices and sort them out into input and output devices
# PyLooper currently only supports stereo devices and 44.1kHz sample rate
for i in range(pa.get_device_count()):
    device_info = pa.get_device_info_by_index(i)
    if int(device_info["defaultSampleRate"]) != 44100:
        continue
    if device_info["maxInputChannels"] == 2:
        input_devices.append(device_info)
    elif device_info["maxOutputChannels"] == 2:
        output_devices.append(device_info)

if len(input_devices) == 0:
    print("No stereo input devices found. Exiting.")
    exit()

if len(output_devices) == 0:
    print("No stereo output devices found. Exiting.")
    exit()

app = QtWidgets.QApplication(sys.argv)
pyLooperWindow = PyLooperWindow()
pyLooperWindow.setMinimumWidth(1000)
pyLooperWindow.setMinimumHeight(600)
pyLooperWindow.setWindowTitle("PyLooper")
pyLooperWindow.registerPyAudio(pa)
pyLooperWindow.registerInputDevices(input_devices)
pyLooperWindow.registerOutputDevices(output_devices)
pyLooperWindow.show()
app.exec_()
pa.terminate()
