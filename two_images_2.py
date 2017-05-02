import sys
from PyQt5 import QtWidgets, QtGui
import functools

class Example(QtWidgets.QMainWindow):

    def __init__(self):
        super(Example, self).__init__()
        self.initUI()

    def initUI(self):
        QtWidgets.QToolTip.setFont(QtGui.QFont('Test', 10))
        self.setToolTip('This is a <b>QWidget</b> widget')

        # Show  image
        self.pic = QtWidgets.QLabel(self)
        self.pic.setGeometry(10, 10, 800, 800)
        self.image = "C:\\Users\\Neda\\Desktop\\posters\\letgo.png"
        self.pic.setPixmap(QtGui.QPixmap(self.image))

        # Show button
        btn = QtWidgets.QPushButton('Button', self)
        btn.setToolTip('This is a <b>QPushButton</b> widget')
        btn.resize(btn.sizeHint())
        btn.clicked.connect(self.fun)
        btn.move(50, 50)


        self.setGeometry(300, 300, 2000, 1500)
        self.setWindowTitle('Tooltips')
        self.show()

    # Connect button to image updating
    def fun(self):
        print("FuN")
        if self.image == "C:\\Users\\Neda\\Desktop\\posters\\letgo.png":
            self.pic.setPixmap(QtGui.QPixmap( "C:\\Users\\Neda\\Desktop\\posters\\rumi.png"))
            self.image = "C:\\Users\\Neda\\Desktop\\posters\\rumi.png"

        elif self.image == "C:\\Users\\Neda\\Desktop\\posters\\rumi.png":
            self.pic.setPixmap(QtGui.QPixmap("C:\\Users\\Neda\\Desktop\\posters\\letgo.png"))
            self.image = "C:\\Users\\Neda\\Desktop\\posters\\letgo.png"


def main():

    app = QtWidgets.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()