from PyQt5 import QtCore, QtWidgets
from time import sleep
import sys, os

class ConstantProgressBar(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ConstantProgressBar, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.resize(400, 81)
        self.progressBar.setMinimumSize(QtCore.QSize(400, 81))
        self.progressBar.show()
        self.progressBar.setRange(0, 1)
        layout.addWidget(self.progressBar)
        self.button = QtWidgets.QPushButton("Start", self)
        layout.addWidget(self.button)

        self.progressBar.show()
        QtCore.QCoreApplication.instance().processEvents()

        self.button.clicked.connect(self.onStart)

        self.myLongTask = TaskThread()
        self.myLongTask.taskFinished.connect(self.onFinished)

    def onStart(self):
        self.progressBar.setRange(0, 0)
        self.myLongTask.start()

    def onFinished(self):
        # Stop the pulsation
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(1)
        QtWidgets.QApplication.processEvents()
        self.progressBar.show()


class TaskThread(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()
    def run(self):
        sleep(9)
        self.taskFinished.emit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ConstantProgressBar()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())