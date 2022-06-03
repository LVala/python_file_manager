import pyfm.qrcRes

import os
from PyQt5.QtGui import QPainter, QPixmap, QColor, QBrush, QPen
from PyQt5.QtWidgets import QAbstractButton, QAction, QWidget, QVBoxLayout, QLabel, QApplication, QMenu
from PyQt5.QtCore import Qt

class PicButton(QAbstractButton):
    def __init__(self, pixmap, x, y, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap = pixmap
        self.pixmap = pixmap.scaled(x, y, Qt.KeepAspectRatio)
        self.pixmapCopy = pixmap
        self.pixmapCopy = pixmap.scaled(x, y, Qt.KeepAspectRatio)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def highlight(self):
        mask = QPainter(self.pixmap)
        brush = QBrush(QColor(0,0,0,128))
        pen = QPen(QColor(0,0,0,0))
        mask.setBrush(brush)
        mask.setPen(pen)
        mask.drawRect(0,0,200,200)
        self.update()

    def deHighlight(self):
        self.pixmap = self.pixmapCopy.copy()
        self.update()

    def sizeHint(self):
        return self.pixmap.size()


class FileButton(QWidget):
    def __init__(self, path, x, y, parent=None):
        super().__init__()
        pixmap = QPixmap(":folder.svg") if os.path.isdir(path) else QPixmap(":file.svg")
        self.parent = parent;
        self.image = PicButton(pixmap, x, y, parent=self)
        self.image.setFixedSize(x, y)
        self.setFixedWidth(y+20)

        self.path = path
        self.label = QLabel(path.split(os.sep)[-1])
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.layout.addWidget(self.image)
        self.layout.addWidget(self.label)

        self.image.mouseDoubleClickEvent = self.mouseDoubleClickEvent
        self.image.mouseReleaseEvent = self.mouseReleaseEvent

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self);

        separator1 = QAction(self)
        separator1.setSeparator(True)
        separator2 = QAction(self)
        separator2.setSeparator(True)
        separator3 = QAction(self)
        separator3.setSeparator(True)

        contextMenu.addAction(self.parent.openAction)
        contextMenu.addAction(separator1)
        contextMenu.addAction(self.parent.cutAction)
        contextMenu.addAction(self.parent.copyAction)
        contextMenu.addAction(self.parent.removeAction)
        contextMenu.addAction(separator2)
        contextMenu.addAction(self.parent.renameAction)
        contextMenu.addAction(separator3)
        contextMenu.addAction(self.parent.getPropAction)

        self.parent.manageHighlighted(self, False)
        contextMenu.exec_(self.mapToGlobal(event.pos()))
    
    def highlight(self):
        self.image.highlight() 
    
    def deHighlight(self):
        self.image.deHighlight()
    
    def mouseDoubleClickEvent(self, event):
        self.parent.jumpToDir(self.path, True)

    def mouseReleaseEvent(self, event):
        modifiers = QApplication.keyboardModifiers()
        if self.parent.curPath != self.path:
            self.parent.manageHighlighted(self, modifiers == Qt.ControlModifier)
