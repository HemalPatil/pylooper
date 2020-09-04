from PyQt5 import QtCore, QtGui, QtWidgets

import enum
import numpy as np
import pyaudio

class PyLooperTrackState(enum.Enum):
    Idle = "Idle"
    Recording = "Recording"
    Looping = "Looping"

class PyLooperTrack(QtWidgets.QGroupBox):
    def __init__(self, objectName, title, window):
        super(PyLooperTrack, self).__init__(window)
        self.setObjectName(objectName + "_trackGroup")
        self.setTitle(title)

        self.armed = QtWidgets.QCheckBox(self)
        self.armed.setGeometry(QtCore.QRect(35, 25, 61, 20))
        self.armed.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.armed.setObjectName(objectName + "_armed")
        self.armed.setText("Armed")
        self.armed.adjustSize()

        self.loopButton = QtWidgets.QPushButton(self)
        self.loopButton.setGeometry(QtCore.QRect(70, 50, 51, 51))
        self.loopButton.setObjectName(objectName + "_loopButton")
        self.loopButton.setText("⟳")
        self.loopButton.setFont(QtGui.QFont("Segoe UI", 15))
        self.loopButton.clicked.connect(self.loopButtonClicked)

        self.recordButton = QtWidgets.QPushButton(self)
        self.recordButton.setGeometry(QtCore.QRect(10, 50, 51, 51))
        self.recordButton.setObjectName(objectName + "_recordButton")
        self.recordButton.setText("⬤")
        self.recordButton.clicked.connect(self.recordButtonClicked)

        self.eqLabel = QtWidgets.QLabel(self)
        self.eqLabel.setGeometry(QtCore.QRect(20, 130, 21, 16))
        self.eqLabel.setObjectName(objectName + "_eqLabel")
        self.eqLabel.setText("EQ")

        self.eqSlider = QtWidgets.QSlider(self)
        self.eqSlider.setGeometry(QtCore.QRect(20, 160, 21, 91))
        self.eqSlider.setOrientation(QtCore.Qt.Vertical)
        self.eqSlider.setObjectName(objectName + "_eqSlider")
        self.eqSlider.setValue(50)

        self.clearButton = QtWidgets.QPushButton(self)
        self.clearButton.setGeometry(QtCore.QRect(70, 200, 51, 51))
        self.clearButton.setObjectName(objectName + "_clearButton")
        self.clearButton.setText("🗑")
        self.clearButton.clicked.connect(self.clearButtonClicked)

        self.oneOffButton = QtWidgets.QPushButton(self)
        self.oneOffButton.setGeometry(QtCore.QRect(70, 110, 51, 51))
        self.oneOffButton.setObjectName(objectName + "_oneOffButton")
        self.oneOffButton.setText("One-off")
        self.oneOffButton.clicked.connect(self.oneOffButtonClicked)

        # Maybe this could be used to sync all tracks or sync to metronome, need to figure out
        # self.syncButton = QtWidgets.QPushButton(self)
        # self.syncButton.setGeometry(QtCore.QRect(70, 170, 51, 51))
        # self.syncButton.setObjectName(objectName + "_syncButton")
        # self.syncButton.setText("Sync")

        self.panSlider = QtWidgets.QSlider(self)
        self.panSlider.setGeometry(QtCore.QRect(40, 270, 51, 22))
        self.panSlider.setOrientation(QtCore.Qt.Horizontal)
        self.panSlider.setObjectName(objectName + "_panSlider")
        self.panSlider.setValue(50)

        self.leftLabel = QtWidgets.QLabel(self)
        self.leftLabel.setGeometry(QtCore.QRect(20, 270, 16, 16))
        self.leftLabel.setObjectName(objectName + "_leftLabel")
        self.leftLabel.setText("L")
        self.leftLabel.adjustSize()

        self.rightLabel = QtWidgets.QLabel(self)
        self.rightLabel.setGeometry(QtCore.QRect(100, 270, 21, 16))
        self.rightLabel.setObjectName(objectName + "_rightLabel")
        self.rightLabel.setText("R")
        self.rightLabel.adjustSize()

        self.pa = None

        self.isRecording = False
        self.recordInputDevice = None
        self.recordInputStream = None
        self.recordInputSampleRate = None
        self.recordInputChunkSize = None
        self.recordInputBufferSize = 0
        self.recordInputBuffer = np.empty(shape = (0, 2), dtype = np.float32)

        self.recordOutputDevice = None
        self.recordOutputStream = None
        self.recordOutputSampleRate = None
        self.recordOutputBufferSize = None

        self.isLooping = False
        self.loopOutputDevice = None
        self.loopOutputStream = None
        self.loopOutputSampleRate = None
        self.loopOutputBufferSize = None
        self.loopOutputSilence = None
        self.loopPointer = 0
        self.currentTrackState = PyLooperTrackState.Idle
        self.setTrackState(PyLooperTrackState.Idle)

    def updateTrackUI(self):
        self.setTrackState(self.currentTrackState)

    def setTrackState(self, state):
        self.currentTrackState = state
        if state == PyLooperTrackState.Idle:
            self.recordButton.setStyleSheet("background-color: #dddddd; color: black")
            self.recordButton.setEnabled(True)
            if len(self.recordInputBuffer) > 0:
                self.loopButton.setStyleSheet("background-color: lawngreen; color: black")
                self.loopButton.setEnabled(True)
                self.oneOffButton.setStyleSheet("background-color: dodgerblue; color: black")
                self.oneOffButton.setEnabled(True)
                self.clearButton.setStyleSheet("background-color: black; color: white")
                self.clearButton.setEnabled(True)
            else:
                
                self.loopButton.setStyleSheet("background-color: #dddddd; color: black")
                self.loopButton.setEnabled(False)
                self.oneOffButton.setStyleSheet("background-color: #dddddd; color: black")
                self.oneOffButton.setEnabled(False)
                self.clearButton.setStyleSheet("background-color: #dddddd; color: black")
                self.clearButton.setEnabled(False)
        elif state == PyLooperTrackState.Recording:
            self.recordButton.setStyleSheet("background-color: red; color: white")
            self.recordButton.setEnabled(True)
            self.loopButton.setStyleSheet("background-color: #dddddd; color: black")
            self.loopButton.setEnabled(False)
            self.oneOffButton.setStyleSheet("background-color: #dddddd; color: black")
            self.oneOffButton.setEnabled(False)
            self.clearButton.setStyleSheet("background-color: #dddddd; color: black")
            self.clearButton.setEnabled(False)
        elif state == PyLooperTrackState.Looping:
            self.recordButton.setStyleSheet("background-color: #dddddd; color: black")
            self.recordButton.setEnabled(False)
            self.oneOffButton.setStyleSheet("background-color: dodgerblue; color: black")
            self.oneOffButton.setEnabled(True)
            self.clearButton.setStyleSheet("background-color: #dddddd; color: black")
            self.clearButton.setEnabled(False)

    def recordButtonClicked(self):
        # Flip isRecoding first so record callback starts immediately and then update UI
        self.isRecording = not self.isRecording
        if self.isRecording:
            self.setTrackState(PyLooperTrackState.Recording)
        else:
            self.setTrackState(PyLooperTrackState.Idle)

    def loopButtonClicked(self):
        # Flip isRecoding first so record callback starts immediately and then update UI
        self.isLooping = not self.isLooping
        if self.isLooping:
            self.setTrackState(PyLooperTrackState.Looping)
        else:
            self.setTrackState(PyLooperTrackState.Idle)

    def oneOffButtonClicked(self):
        self.loopPointer = 0
        self.updateTrackUI()

    def clearButtonClicked(self):
        self.recordInputBuffer = np.empty(shape = (0, 2), dtype = np.float32)
        self.updateTrackUI()

    def registerPyAudio(self, pyaudio):
        self.pa = pyaudio

    def setRecordInputDevice(self, device):
        if self.recordInputDevice == device:
            return
        print(self.title() + ": record input device changed. Initializing new stream.")
        self.recordInputDevice = device
        self.recordInputSampleRate = int(self.recordInputDevice["defaultSampleRate"])
        self.recordInputChunkSize = int(self.recordInputSampleRate / 100)
        self.closeStream(self.recordInputStream)
        self.recordInputStream = self.pa.open(format = pyaudio.paFloat32,
                                            channels = self.recordInputDevice["maxInputChannels"],
                                            rate = self.recordInputSampleRate,
                                            input = True,
                                            frames_per_buffer = self.recordInputChunkSize,
                                            stream_callback = self.recordInputCallback,
                                            input_device_index = self.recordInputDevice["index"])

    def setRecordOutputDevice(self, device):
        if self.recordOutputDevice == device:
            return
        self.recordOutputDevice = device

    def setLoopOutputDevice(self, device):
        if self.loopOutputDevice == device:
            return
        print(self.title() + ": loop output device changed. Initializing new stream.")
        self.loopOutputDevice = device
        self.loopOutputSampleRate = int(self.loopOutputDevice["defaultSampleRate"])
        self.loopOutputBufferSize = int(self.loopOutputSampleRate / 100)
        self.closeStream(self.loopOutputStream)
        self.loopOutputSilence = self.getSilence(self.loopOutputBufferSize)
        self.loopOutputStream = self.pa.open(format = pyaudio.paFloat32,
                                            channels = self.loopOutputDevice["maxOutputChannels"],
                                            rate = self.loopOutputSampleRate,
                                            output = True,
                                            frames_per_buffer = self.loopOutputBufferSize,
                                            stream_callback = self.loopOutputCallback,
                                            output_device_index = self.loopOutputDevice["index"])

    def getSilence(self, bufferSize):
        silence_one_channel = np.zeros(bufferSize, dtype = np.float32)
        return np.column_stack([silence_one_channel, silence_one_channel])

    def focus(self):
        self.setStyleSheet("background-color: #bbbbbb")

    def unfocus(self):
        self.setStyleSheet("background-color: #eeeeee")

    def recordInputCallback(self, in_data, frame_count, time_info, status):
        if self.isRecording:
            dataInterleaved = np.fromstring(in_data, dtype = np.float32)
            dataChannelSeparated = np.reshape(dataInterleaved, (self.recordInputChunkSize, 2))
            self.recordInputBuffer = np.concatenate([self.recordInputBuffer, dataChannelSeparated])
            self.recordInputBufferSize = len(self.recordInputBuffer)
        return (None, pyaudio.paContinue)

    def loopOutputCallback(self, in_data, frame_count, time_info, status):
        # Output the buffer if armed else return silence.
        # If silence is not returned the loopback is not called again.
        if self.isLooping and self.armed.isChecked():
            tmpPointer = self.loopPointer
            self.loopPointer = (self.loopPointer + self.recordInputChunkSize) % self.recordInputBufferSize
            chunk = self.convertToLoopChunk(self.recordInputBuffer[tmpPointer:tmpPointer + self.recordInputChunkSize])

            # Adjust volume and do balance panning on stereo audio
            # Possibly add a selector for panning modes - Balance panning/combined panning
            chunkEqualized = np.multiply(chunk, self.eqSlider.value() / 100)
            panValue = self.panSlider.value()
            leftPan = (100 - panValue) / 50
            rightPan = panValue / 50
            chunkPanned = np.column_stack([np.multiply(chunkEqualized[:, 0], leftPan), np.multiply(chunkEqualized[:, 1], rightPan)])
            return (chunkPanned, pyaudio.paContinue)
        else:
            return (self.loopOutputSilence, pyaudio.paContinue)

    def convertToLoopChunk(self, chunk):
        # Right now PyLooper supports only 44.1kHz across all devices
        # This method is added for future proofing so that resampling can be done if more sampling rates are supported
        return chunk

    def closeStream(self, stream):
        if stream:
            stream.stop_stream()
            stream.close()

    def closeStreams(self):
        print(self.title() + ": closing streams")
        self.closeStream(self.recordInputStream)
        self.closeStream(self.recordOutputStream)
        self.closeStream(self.loopOutputStream)
