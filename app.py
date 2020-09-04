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
        # print("Input Device:")
        # print(device_info)
    elif device_info["maxOutputChannels"] == 2:
        output_devices.append(device_info)
        # print("Output Device:")
        # print(device_info)

if len(input_devices) == 0:
    print("No stereo input devices found. Exiting.")
    exit()

if len(output_devices) == 0:
    print("No stereo output devices found. Exiting.")
    exit()

# main_output_stream = None
# main_output_device = None
# main_output_sample_rate = None

# def setup_main_output(device):
#     main_output_device = device
#     main_output_sample_rate = device["defaultSampleRate"]

# main_output_stream2 = None
# main_output_device2 = None
# main_output_sample_rate2 = None

# sine = None
# sine_readp = 0
# def gen_sine():
#     global sine
#     silence_1s = np.zeros(1 * main_output_sample_rate, dtype=np.int16)
#     duration = 1
#     frequency = 1000
#     sample_index = np.arange(duration * main_output_sample_rate)
#     sine_1000 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     frequency = 2000
#     sine_2000 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     frequency = 500
#     sine_500 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     frequency = 3000
#     sine_3000 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     frequency = 6000
#     sine_6000 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     frequency = 1500
#     sine_1500 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     sine_left = np.concatenate((sine_1000, sine_2000, sine_500))
#     sine_right = np.concatenate((sine_3000, sine_1500, sine_6000))
#     # sine = np.insert(sine_right, np.arange(len(sine_left)), sine_left)
#     sine = np.column_stack([sine_left, sine_right])
#     print("Shape: " + str(sine.shape))

# def main_output_stream_callback(in_data, frame_count, time_info, status):
#     global sine_readp
#     print(in_data)
#     print(frame_count)
#     print(time_info)
#     print(status)
#     temp_sine_readp = sine_readp
#     sine_readp = (sine_readp + frame_count) % (main_output_sample_rate * 3)
#     print("temp_sine_readp: " + str(temp_sine_readp))
#     print("sine_readp: " + str(sine_readp))
#     return (sine[temp_sine_readp:temp_sine_readp + frame_count], pyaudio.paContinue)
#     # return (in_data, pyaudio.paContinue)

# sine2 = None
# sine_readp2 = 0

# def gen_sine2():
#     global sine2
#     # silence_1s = np.zeros(1 * main_output_sample_rate, dtype=np.int16)
#     duration = 2
#     frequency = 50
#     sample_index = np.arange(duration * main_output_sample_rate)
#     sine_100 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     # frequency = 2000
#     # sine_2000 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     # frequency = 500
#     # sine_500 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     # frequency = 3000
#     # sine_3000 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     # frequency = 6000
#     # sine_6000 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     # frequency = 1500
#     # sine_1500 = np.int16(np.sin(2 * np.pi * sample_index * frequency / main_output_sample_rate) * 0.1 * np.iinfo(np.int16).max)
#     # sine_left = np.concatenate((sine_1000, sine_2000, sine_500))
#     # sine_right = np.concatenate((sine_3000, sine_1500, sine_6000))
#     # sine = np.insert(sine_right, np.arange(len(sine_left)), sine_left)
#     sine2 = np.column_stack([sine_100, sine_100])
#     print("Shape: " + str(sine2.shape))

# def main_output_stream_callback2(in_data, frame_count, time_info, status):
#     global sine_readp2
#     # print(in_data)
#     # print(frame_count)
#     # print(time_info)
#     # print(status)
#     temp_sine_readp2 = sine_readp2
#     sine_readp2 = (sine_readp2 + frame_count) % (main_output_sample_rate * 2)
#     print("temp_sine_readp2: " + str(temp_sine_readp2))
#     print("sine_readp: " + str(sine_readp2))
#     return (sine2[temp_sine_readp2:temp_sine_readp2 + frame_count], pyaudio.paContinue)

# def main_output_stream_changed(index):
#     global main_output_stream
#     global main_output_device
#     global main_output_sample_rate
#     global main_output_stream2
#     global main_output_device2
#     global main_output_sample_rate2
#     main_output_device = output_devices[index]
#     main_output_sample_rate = int(main_output_device["defaultSampleRate"])
#     print("Selected: " + main_output_device["name"])
#     if main_output_stream:
#         main_output_stream.stop_stream()
#         main_output_stream.close()
#     gen_sine()
#     gen_sine2()
#     print(sine[0:10])
#     main_output_stream = pa.open(format = pyaudio.paInt16,
#                                  channels = main_output_device["maxOutputChannels"],
#                                  rate = main_output_sample_rate,
#                                  input = False,
#                                  output = True,
#                                  frames_per_buffer = int(main_output_sample_rate/10),
#                                  stream_callback = main_output_stream_callback,
#                                  output_device_index = main_output_device["index"])
#     main_output_stream2 = pa.open(format = pyaudio.paInt16,
#                                  channels = main_output_device["maxOutputChannels"],
#                                  rate = main_output_sample_rate,
#                                  input = False,
#                                  output = True,
#                                  frames_per_buffer = int(main_output_sample_rate/10),
#                                  stream_callback = main_output_stream_callback2,
#                                  output_device_index = main_output_device["index"])

app = QtWidgets.QApplication(sys.argv)
pyLooperWindow = PyLooperWindow()
pyLooperWindow.setMinimumWidth(1000)
pyLooperWindow.setMinimumHeight(600)
pyLooperWindow.setWindowTitle("PyLooper")
pyLooperWindow.registerPyAudio(pa)
pyLooperWindow.registerInputDevices(input_devices)
# print(pyLooperWindow.recordInputCombo.currentIndex())
pyLooperWindow.registerOutputDevices(output_devices)
# pyLooperWindow.mainOutputCombo.adjustSize()
# pyLooperWindow.registerMainOutputChanged(main_output_stream_changed)
pyLooperWindow.show()
app.exec_()
# if main_output_stream:
#     main_output_stream.stop_stream()
#     main_output_stream.close()
# pyLooperWindow.closeStreams()
pa.terminate()
