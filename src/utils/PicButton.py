from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QAbstractButton
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
