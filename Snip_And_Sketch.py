import sys
from os.path import basename
from PyQt5.QtCore import QPoint, Qt, QRect
from PyQt5.QtWidgets import QAction, QMainWindow, QApplication, QPushButton, QMenu, QFileDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen

import tkinter as tk
import numpy as np
import cv2
from PIL import ImageGrab
from PyQt5 import QtWidgets, QtCore, QtGui
import Snip_And_Sketch
from PyQt5.QtCore import Qt


class SnippingWidget(QtWidgets.QWidget):
    num_snip = 0
    is_snipping = False
    background = True

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__()
        self.parent = parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        root = tk.Tk()
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

    def start(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        SnippingWidget.background = False
        SnippingWidget.is_snipping = True
        self.setWindowOpacity(0.3)
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))
        print('Capture the screen...')
        print('Press q if you want to quit...')
        self.show()

    def paintEvent(self, event):
        if SnippingWidget.is_snipping:
            brush_color = (128, 128, 255, 100)
            lw = 3
            opacity = 0.3
        else:
            # reset points, so the rectangle won't show up again.
            self.begin = QtCore.QPoint()
            self.end = QtCore.QPoint()
            brush_color = (0, 0, 0, 0)
            lw = 0
            opacity = 0

        self.setWindowOpacity(opacity)
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor('black'), lw))
        qp.setBrush(QtGui.QColor(*brush_color))
        rect = QtCore.QRectF(self.begin, self.end)
        qp.drawRect(rect)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Q:
            print('Quit')
            self.close()
        event.accept()

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        SnippingWidget.num_snip += 1
        SnippingWidget.is_snipping = False
        QtWidgets.QApplication.restoreOverrideCursor()
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        self.repaint()
        QtWidgets.QApplication.processEvents()
        img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        QtWidgets.QApplication.processEvents()
        img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
        self.close()
        # add to the snips list the object that opens a window of the image
        Snip_And_Sketch.Menu(img, SnippingWidget.num_snip, (x1, y1, x2, y2))

class Menu(QMainWindow):
    COLORS = ['Red', 'Black', 'Blue', 'Green', 'Yellow']
    SIZES = [1, 3, 5, 7, 9, 11]
    default_title = "Snip And Sketch"

    def __init__(self, numpy_image=None, snip_number=None, start_position=(300, 300, 350, 250)):
        super().__init__()

        self.drawing = False
        self.brushSize = 3
        self.brushColor = Qt.red
        self.lastPoint = QPoint()
        self.total_snips = 0
        self.title = Menu.default_title
        
        new_snip_action = QAction('New', self)
        new_snip_action.setShortcut('Ctrl+N')
        new_snip_action.setStatusTip('Snip!')
        new_snip_action.triggered.connect(self.new_image_window)

        brush_color_button = QPushButton("Brush Color")
        colorMenu = QMenu()
        for color in Menu.COLORS:
            colorMenu.addAction(color)
        brush_color_button.setMenu(colorMenu)
        colorMenu.triggered.connect(lambda action: change_brush_color(action.text()))

        brush_size_button = QPushButton("Brush Size")
        sizeMenu = QMenu()
        for size in Menu.SIZES:
            sizeMenu.addAction("{0}px".format(str(size)))
        brush_size_button.setMenu(sizeMenu)
        sizeMenu.triggered.connect(lambda action: change_brush_size(action.text()))

        # Saving
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save')
        save_action.triggered.connect(self.save_file)

        # Exit
        exit_window = QAction('Exit', self)
        exit_window.setShortcut('Esc')
        exit_window.setStatusTip('Exit application')
        exit_window.triggered.connect(self.close)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(new_snip_action)
        self.toolbar.addAction(save_action)
        self.toolbar.addWidget(brush_color_button)
        self.toolbar.addWidget(brush_size_button)
        self.toolbar.addAction(exit_window)

        self.snippingTool = SnippingWidget()
        self.setGeometry(*start_position)

        # From the second initialization, both arguments will be valid
        if numpy_image is not None and snip_number is not None:
            self.image = self.convert_numpy_img_to_qpixmap(numpy_image)
            self.change_and_set_title("Snip #{0}".format(snip_number))
        else:
            self.image = QPixmap("background.PNG")
            self.change_and_set_title(Menu.default_title)

        self.resize(self.image.width(), self.image.height() + self.toolbar.height())
        self.show()

        def change_brush_color(new_color):
            self.brushColor = eval("Qt.{0}".format(new_color.lower()))

        def change_brush_size(new_size):
            self.brushSize = int(''.join(filter(lambda x: x.isdigit(), new_size)))

    def new_image_window(self):
        if self.snippingTool.background:
            self.close()
        self.total_snips += 1
        self.snippingTool.start()

    def save_file(self):
        file_path, name = QFileDialog.getSaveFileName(self, "Save file", self.title, "PNG Image file (*.png)")
        if file_path:
            self.image.save(file_path)
            self.change_and_set_title(basename(file_path))
            print(self.title, 'Saved')

    def change_and_set_title(self, new_title):
        self.title = new_title
        self.setWindowTitle(self.title)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = QRect(0,  self.toolbar.height(), self.image.width(), self.image.height())
        painter.drawPixmap(rect, self.image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos() - QPoint(0, self.toolbar.height())

    def mouseMoveEvent(self, event):
        if event.buttons() and Qt.LeftButton and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos() - QPoint(0, self.toolbar.height()))
            self.lastPoint = event.pos() - QPoint(0, self.toolbar.height())
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button == Qt.LeftButton:
            self.drawing = False

    def closeEvent(self, event):
        event.accept()

    @staticmethod
    def convert_numpy_img_to_qpixmap(np_img):
        height, width, channel = np_img.shape
        bytesPerLine = 3 * width
        return QPixmap(QImage(np_img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainMenu = Menu()
    sys.exit(app.exec_())