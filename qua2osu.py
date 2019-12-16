import os
import sys
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from convert import convertMapset
# autogenerated .py from qt designer
# use "pyuic5 -x gui.ui -o gui.py" after editing gui.ui with qt designer
from gui import Ui_MainWindow


class IceMainWindow(QMainWindow, Ui_MainWindow):

    progressbarSmoothness = 10

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.inputToolButton.clicked.connect(self.openInputDirectoryDialog)
        self.outputToolButton.clicked.connect(self.openOutputDirectoryDialog)
        self.convertPushButton.clicked.connect(self.convertOnClick)

        self.updateStatus("Finished setup")

    def openInputDirectoryDialog(self):
        path = str(QFileDialog.getExistingDirectory(
            self, "Select Input Folder"))
        self.inputLineEdit.setText(path)
        self.updateStatus("Set input path to " + path)

    def openOutputDirectoryDialog(self):
        path = str(QFileDialog.getExistingDirectory(
            self, "Select Output Folder"))
        self.outputLineEdit.setText(path)
        self.updateStatus("Set output path to " + path)

    def updateConvertButtonIfValidPath(self):
        # TODO
        pass

    def updateStatus(self, status):
        currentText = self.statusLabel.text()
        lastLine = currentText.split("\n")[-1]
        self.statusLabel.setText(lastLine + "\n" + status)

    def updateProgressBarMax(self, maximum):
        self.progressBar.setMaximum(maximum * self.progressbarSmoothness)

    def incrementProgressBarValue(self):
        for i in range(self.progressbarSmoothness):
            self.progressBar.setValue(self.progressBar.value() + 1)
            time.sleep(0.04 * 1/self.progressbarSmoothness)

    def initiateConverterThread(self, inputPath, outputPath, options):
        converterThread = ConverterThread(inputPath, outputPath, options)
        converterThread.updateStatus.connect(self.updateStatus)
        converterThread.updateProgressbarMax.connect(
            self.updateProgressBarMax)
        converterThread.incrementProgressbarValue.connect(
            self.incrementProgressBarValue)

        return converterThread

    def convertOnClick(self):
        inputPath = self.inputLineEdit.text()
        outputPath = self.outputLineEdit.text()

        if inputPath == "" or outputPath == "":
            self.updateStatus(
                "No paths detected, using default samples input and default output path")
            inputPath = "samples"
            outputPath = "output"

        selectedOd = self.odDoubleSpinBox.value()
        selectedHp = self.hpDoubleSpinBox.value()
        selectedHitSoundVolume = self.hsVolumeSpinBox.value()

        # please tell me if there's an easier way to lookup
        # which radio button is checked because this is horrible
        selectedSampleSet = ""
        sampleSetButtons = [
            self.sampleSetNormalRadioButton,
            self.sampleSetSoftRadioButton,
            self.sampleSetDrumRadioButton
        ]

        for button in sampleSetButtons:
            if button.isChecked():
                selectedSampleSet = button.text()
                break

        options = {
            "od": selectedOd,
            "hp": selectedHp,
            "hitSoundVolume": selectedHitSoundVolume,
            "sampleSet": selectedSampleSet
        }

        self.converterThread = self.initiateConverterThread(
            inputPath, outputPath, options)
        self.converterThread.start()


class IceApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setStyle("Fusion")


class ConverterThread(QThread):

    updateStatus = pyqtSignal(str)
    incrementProgressbarValue = pyqtSignal()
    updateProgressbarMax = pyqtSignal(int)

    def __init__(self, inputPath, outputPath, options):
        QThread.__init__(self)
        self.inputPath = inputPath
        self.outputPath = outputPath
        self.options = options

    def __del__(self):
        self.wait()

    def run(self):
        qpFilesInInputDir = []

        for file in os.listdir(self.inputPath):
            if file.endswith('.qp') and os.path.isfile(os.path.join(self.inputPath, file)):
                qpFilesInInputDir.append(file)

        numberOfQpFiles = len(qpFilesInInputDir)

        if numberOfQpFiles == 0:
            self.updateStatus.emit("No mapsets found in " + self.inputPath)
            return

        else:
            self.updateProgressbarMax.emit(numberOfQpFiles)

            start = time.time()
            count = 1
            for file in qpFilesInInputDir:
                filePath = os.path.join(self.inputPath, file)
                self.updateStatus.emit(f"({count}/{numberOfQpFiles}) Converting {filePath}")
                convertMapset(filePath, self.outputPath, self.options)
                count += 1
                self.incrementProgressbarValue.emit()

            end = time.time()
            timeElapsed = round(end-start, 2)
            self.updateStatus.emit(
                f"Finished converting all mapsets, total time elapsed: {timeElapsed} seconds")
            return


if __name__ == '__main__':
    app = IceApp()
    iceApp = IceMainWindow()
    iceApp.show()
    sys.exit(app.exec_())