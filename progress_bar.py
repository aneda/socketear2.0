from PyQt5 import QtCore, QtWidgets
from time import sleep
import sys, os


class ConstantProgressBar(QtWidgets.QDialog):
    def __init__(self, task_thread):
        super(ConstantProgressBar, self).__init__()

        layout = QtWidgets.QVBoxLayout(self)

        # Create a progress bar and a button and add them to the main layout
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.resize(400, 81)
        self.progressBar.setMinimumSize(QtCore.QSize(400, 81))
        self.progressBar.setRange(0, 0)
        self.progressBar.setValue(0)

        layout.addWidget(self.progressBar)
        # self.button = QtWidgets.QPushButton("Start", self)
        # layout.addWidget(self.button)

        # QtCore.QCoreApplication.instance().processEvents()
        self.task_thread = task_thread
        self.task_thread.finished.connect(self.onFinished)
        self.onStart()

    def onStart(self):
        print("progress bar is starting")
        self.progressBar.setRange(0, 0)
        self.progressBar.setValue(0)
        self.show()
        self.task_thread.start()

    def onFinished(self):
        print("progress bar is done")
        # Stop the pulsation
        self.progressBar.setRange(0, 1)
        self.progressBar.setValue(1)
        sleep(2)
        # self.hide()
        self.accept()


class TaskThread(QtCore.QThread):
    def run(self):
        print("task is running")
        for i in range(3):
            print('im sleeping %s' % i)
            sleep(1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    task_thread = TaskThread()
    window = ConstantProgressBar(task_thread)
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())
