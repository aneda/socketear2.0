
from PyQt5 import QtWidgets, QtGui, QtCore

image1 = "C:\\Users\\Neda\\Desktop\\posters\\letgo.png"
image2 = "C:\\Users\\Neda\\Desktop\\posters\\rumi.png"

app = QtWidgets.QApplication([])

pm1 = QtGui.QPixmap(image1)
pm2 =QtGui.QPixmap(image2)

pm = QtGui.QPixmap(400, 200)

label = QtWidgets.QLabel()

left_rectF = QtCore.QRectF(0, 0, 200, 200)     #the left half
right_rectF = QtCore.QRectF(200, 0, 400, 200)  #the right half

painter = QtGui.QPainter(pm)
painter.drawPixmap(left_rectF, pm1, QtCore.QRectF(pm1.rect()))
painter.drawPixmap(right_rectF, pm2, QtCore.QRectF(pm2.rect()))

label.setPixmap(pm)
label.show()


app.exec_()