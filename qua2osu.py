import os
import sys
import time

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from convert import convertMapset

# gui.py is autogenerated from gui.ui (qt designer)

# use "pyuic5 -x gui/gui.ui -o gui/gui.py" after editing gui.ui with qt designer
from gui.gui import Ui_MainWindow


class IceMainWindow(QMainWindow, Ui_MainWindow):
    """Custom window class with all of the GUI functionality

    All of the objects themselves are managed by QT designer in the gui.ui (gui.py) file
    """

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.inputToolButton.clicked.connect(self.openInputDirectoryDialog)
        self.outputToolButton.clicked.connect(self.openOutputDirectoryDialog)
        self.convertPushButton.clicked.connect(self.convertOnClick)

        self.updateStatus("Finished setup")

    def openInputDirectoryDialog(self):
        """Opens the input directory dialog and sets the input path in the GUI"""

        path = str(QFileDialog.getExistingDirectory(
            self, "Select Input Folder"))
        self.inputLineEdit.setText(path)
        self.updateStatus("Set input path to " + path)

    def openOutputDirectoryDialog(self):
        """Opens the output directory dialog and sets the input path in the GUI"""

        path = str(QFileDialog.getExistingDirectory(
            self, "Select Output Folder"))
        self.outputLineEdit.setText(path)
        self.updateStatus("Set output path to " + path)

    def updateStatus(self, status):
        """Wrapper for updating the status label, always shows the two last lines"""

        currentText = self.statusLabel.text()
        lastLine = currentText.split("\n")[-1]
        self.statusLabel.setText(lastLine + "\n" + status)

    def updateProgressBarMax(self, maximum):
        """Wrapper for updating the progress bar maximum"""

        self.progressBar.setMaximum(maximum)

    def incrementProgressBarValue(self):
        """Increments the progress bar by one unit total, adds a smooth animation"""

        self.progressBar.setValue(self.progressBar.value() + 1)

    def initiateConverterThread(self, inputPath, outputPath, options):
        """Sets up the converter thread"""

        converterThread = ConverterThread(inputPath, outputPath, options)
        converterThread.updateStatus.connect(self.updateStatus)
        converterThread.updateProgressbarMax.connect(
            self.updateProgressBarMax)
        converterThread.incrementProgressbarValue.connect(
            self.incrementProgressBarValue)

        return converterThread

    def convertOnClick(self):
        """Starts the map conversion of the folder"""

        inputPath = self.inputLineEdit.text()
        outputPath = self.outputLineEdit.text()

        if inputPath == "" or outputPath == "":
            self.updateStatus("Empty paths detected, using default "
                              "samples input and default output path")
            if inputPath == "":
                inputPath = "samples"

            if outputPath == "":
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

        self.progressBar.setValue(0)

        self.converterThread = self.initiateConverterThread(
            inputPath, outputPath, options)
        self.converterThread.start()


class ConverterThread(QThread):
    """Using a different thread for the map conversion

    Otherwise the UI would freeze and become unresponsive during the conversion
    """

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
            path = os.path.join(self.inputPath, file)
            if file.endswith('.qp') and os.path.isfile(path):
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

                self.updateStatus.emit(f"({count}/{numberOfQpFiles}) "
                                       f"Converting {filePath}")

                convertMapset(filePath, self.outputPath, self.options)
                count += 1
                self.incrementProgressbarValue.emit()

            end = time.time()
            timeElapsed = round(end - start, 2)

            self.updateStatus.emit(
                f"Finished converting all mapsets,"
                f"total time elapsed: {timeElapsed} seconds"
            )

            return


class IceApp(QApplication):
    """Custom QApplication class for the sole purpose of applying the Fusion style"""

    def __init__(self):
        super().__init__(sys.argv)
        self.setStyle("Fusion")


def main():
    app = IceApp()
    iceApp = IceMainWindow()
    iceApp.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
