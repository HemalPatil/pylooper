from PyQt5 import QtCore, QtGui, QtWidgets
from track import PyLooperTrack

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
