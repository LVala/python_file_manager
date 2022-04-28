import qrc_res

import os
from PyQt5.QtGui import QPainter, QPixmap
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

class FileButton(QWidget):
    def __init__(self, path, x, y, parent=None):
        super().__init__()
        pixmap = QPixmap(":folder.svg") if os.path.isdir(path) else QPixmap(":file.svg")
        self.parent = parent;
        image = PicButton(pixmap, x, y, parent=self)
        image.setFixedSize(x, y)
        self.setFixedWidth(y+20)
        self.path = path
        self.label = QLabel(path.split(os.sep)[-1])
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(image)
        layout.addWidget(self.label)

        image.mouseDoubleClickEvent = self.mouseDoubleClickEvent
    
    def mouseDoubleClickEvent(self, event):
        if os.path.isdir(self.path):
            self.parent.jumpToDir(self.path, True)

    def mouseReleaseEvent(self, event):
        modifiers = Qt.KeyboardModifier()
        self.parent.addToHighlited(self.path, modifiers == Qt.ControlModifier)
