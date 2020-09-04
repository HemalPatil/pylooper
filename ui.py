from PyQt5 import QtCore, QtGui, QtWidgets

import numpy as np
import pyaudio

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
        self.loopButton.setStyleSheet("background-color: red; color: white")
        # self.loopButton.setEnabled(False)
        self.loopButton.clicked.connect(self.loopButtonClicked)

        self.recordButton = QtWidgets.QPushButton(self)
        self.recordButton.setGeometry(QtCore.QRect(10, 50, 51, 51))
        self.recordButton.setObjectName(objectName + "_recordButton")
        self.recordButton.setText("⬤")
        self.recordButton.setStyleSheet("background-color: lawngreen; color: black")
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

        self.oneOffButton = QtWidgets.QPushButton(self)
        self.oneOffButton.setGeometry(QtCore.QRect(70, 110, 51, 51))
        self.oneOffButton.setObjectName(objectName + "_oneOffButton")
        self.oneOffButton.setText("One-off")

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

    def recordButtonClicked(self):
        self.isRecording = not self.isRecording

    def loopButtonClicked(self):
        self.isLooping = not self.isLooping

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
            # print("In_data size: " + str(len(in_data)))
            # print(in_data)
            dataInterleaved = np.fromstring(in_data, dtype = np.float32)
            dataChannelSeparated = np.reshape(dataInterleaved, (self.recordInputChunkSize, 2))
            self.recordInputBuffer = np.concatenate([self.recordInputBuffer, dataChannelSeparated])
            self.recordInputBufferSize = len(self.recordInputBuffer)
            print(self.title() + " buffer size: " + str(len(self.recordInputBuffer)) + " buffer shape: " + str(self.recordInputBuffer.shape))
        return (None, pyaudio.paContinue)

    def loopOutputCallback(self, in_data, frame_count, time_info, status):
        # print(self.title() + ' loop callback')
        # Output the buffer if armed else return silence.
        # If silence is not returned the loopback is not called again.
        if self.isLooping and self.armed.isChecked():
            print(self.title() + '  armedloop callback')
            tmpPointer = self.loopPointer
            self.loopPointer = (self.loopPointer + self.recordInputChunkSize) % self.recordInputBufferSize
            chunk = self.convertToLoopChunk(self.recordInputBuffer[tmpPointer:tmpPointer + self.recordInputChunkSize])
            # print("chunk.shape: " + str(chunk.shape))
            # return (chunk, pyaudio.paContinue)
            # Adjust volume and do balance panning on stereo audio
            # Possibly add a selector for panning modes - Balance panning/combined panning
            chunkEqualized = np.multiply(chunk, self.eqSlider.value() / 100)
            print("chunkEqualized.shape: " + str(chunkEqualized.shape))
            return (chunkEqualized, pyaudio.paContinue)
            panValue = self.panSlider.value()
            leftPan = (100 - panValue) / 100
            rightPan = panValue / 100
            chunkPanned = np.apply_along_axis(lambda a: (a[0] * leftPan, a[1] * rightPan), 1, chunkEqualized)
            print("chunkPanned.shape: " + str(chunkPanned.shape))
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
        print(self.recordInputBuffer.tolist())

class PyLooperWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(PyLooperWindow, self).__init__()

        self.consoleGroup = QtWidgets.QGroupBox(self)
        self.consoleGroup.setGeometry(QtCore.QRect(20, 10, 661, 151))
        self.consoleGroup.setObjectName("consoleGroup")
        self.consoleGroup.setTitle("Console")

        self.recordInputLabel = QtWidgets.QLabel(self.consoleGroup)
        self.recordInputLabel.setGeometry(QtCore.QRect(20, 70, 81, 16))
        self.recordInputLabel.setObjectName("recordInputLabel")
        self.recordInputLabel.setText("Record Input")

        self.recordOutputLabel = QtWidgets.QLabel(self.consoleGroup)
        self.recordOutputLabel.setGeometry(QtCore.QRect(20, 110, 81, 16))
        self.recordOutputLabel.setObjectName("recordOutputLabel")
        self.recordOutputLabel.setText("Record Output")

        self.selectTrackLabel = QtWidgets.QLabel(self.consoleGroup)
        self.selectTrackLabel.setGeometry(QtCore.QRect(20, 30, 81, 16))
        self.selectTrackLabel.setObjectName("selectTrackLabel")
        self.selectTrackLabel.setText("Track")

        self.loopOutputLabel = QtWidgets.QLabel(self.consoleGroup)
        self.loopOutputLabel.setGeometry(QtCore.QRect(260, 70, 71, 16))
        self.loopOutputLabel.setObjectName("loopOutputLabel")
        self.loopOutputLabel.setText("Loop Output")

        self.selectTrackCombo = QtWidgets.QComboBox(self.consoleGroup)
        self.selectTrackCombo.setGeometry(QtCore.QRect(110, 25, 121, 22))
        self.selectTrackCombo.setObjectName("selectTrackCombo")
        self.selectTrackCombo.currentIndexChanged.connect(self.trackChanged)

        self.recordInputCombo = QtWidgets.QComboBox(self.consoleGroup)
        self.recordInputCombo.setGeometry(QtCore.QRect(110, 65, 121, 22))
        self.recordInputCombo.setObjectName("recordInputCombo")
        self.recordInputCombo.currentIndexChanged.connect(self.recordInputChanged)

        self.recordOutputCombo = QtWidgets.QComboBox(self.consoleGroup)
        self.recordOutputCombo.setGeometry(QtCore.QRect(110, 105, 121, 22))
        self.recordOutputCombo.setObjectName("recordOutputCombo")
        self.recordOutputCombo.currentIndexChanged.connect(self.recordOutputChanged)

        self.loopOutputCombo = QtWidgets.QComboBox(self.consoleGroup)
        self.loopOutputCombo.setGeometry(QtCore.QRect(340, 65, 121, 22))
        self.loopOutputCombo.setObjectName("loopOutputCombo")
        self.loopOutputCombo.currentIndexChanged.connect(self.loopOutputChanged)

        track1 = PyLooperTrack("track1", "Track 1", self)
        track1.setGeometry(QtCore.QRect(20, 180, 140, 310))
        track2 = PyLooperTrack("track2", "Track 2", self)
        track2.setGeometry(QtCore.QRect(200, 180, 140, 310))
        track3 = PyLooperTrack("track3", "Track 3", self)
        track3.setGeometry(QtCore.QRect(380, 180, 140, 310))
        track4 = PyLooperTrack("track4", "Track 4", self)
        track4.setGeometry(QtCore.QRect(560, 180, 140, 310))

        self.tracks = [track1, track2, track3, track4]
        self.track_devices = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.currentTrack = self.tracks[0]
        self.selectTrackCombo.addItems(track.title() for track in self.tracks)
        self.selectTrackCombo.setCurrentIndex(0)

        self.pa = None
        self.input_devices = None
        self.output_devices = None

    def registerPyAudio(self, pyaudio):
        self.pa = pyaudio
        for track in self.tracks:
            track.registerPyAudio(pyaudio)

    def registerInputDevices(self, input_devices):
        self.input_devices = input_devices
        self.recordInputCombo.addItems(device["name"] for device in input_devices)
        self.recordInputCombo.setCurrentIndex(0)
        for track in self.tracks:
            track.setRecordInputDevice(input_devices[0])

    def registerOutputDevices(self, output_devices):
        self.output_devices = output_devices
        self.recordOutputCombo.addItems(device["name"] for device in output_devices)
        self.recordOutputCombo.setCurrentIndex(0)
        self.loopOutputCombo.addItems(device["name"] for device in output_devices)
        self.loopOutputCombo.setCurrentIndex(0)
        for track in self.tracks:
            track.setRecordOutputDevice(output_devices[0])
            track.setLoopOutputDevice(output_devices[0])

    def trackChanged(self, index):
        self.currentTrack.unfocus()
        self.currentTrack = self.tracks[index]
        self.currentTrack.focus()
        self.recordInputCombo.setCurrentIndex(self.track_devices[index][0])
        self.recordOutputCombo.setCurrentIndex(self.track_devices[index][1])
        self.loopOutputCombo.setCurrentIndex(self.track_devices[index][2])

    def recordInputChanged(self, index):
        self.currentTrack.setRecordInputDevice(self.input_devices[index])
        self.track_devices[self.selectTrackCombo.currentIndex()][0] = index

    def recordOutputChanged(self, index):
        self.currentTrack.setRecordOutputDevice(self.output_devices[index])
        self.track_devices[self.selectTrackCombo.currentIndex()][1] = index

    def loopOutputChanged(self, index):
        self.currentTrack.setLoopOutputDevice(self.output_devices[index])
        self.track_devices[self.selectTrackCombo.currentIndex()][2] = index

    def closeEvent(self, event):
        for track in self.tracks:
            track.closeStreams()
        event.accept()
