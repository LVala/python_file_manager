from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAbstractButton, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt

class PicButton(QAbstractButton):
    def __init__(self, pixmap, x, y, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap = pixmap.scaled(x, y, Qt.KeepAspectRatio)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return self.pixmap.size()


class FileDirElem(QWidget):
    def __init__(self, pixmap, x, y):
        super().__init__()
        image = PicButton(pixmap, x, y, parent=self)
        label = QLabel("Test Test")

        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(image)
        layout.addWidget(label)
