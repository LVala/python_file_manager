import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QAction, QComboBox, QLabel
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtGui import QIcon, QPalette, QColor
import qrc_res

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("pyfm")
        self.resize(400, 200)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._createContextMenu()
        self._createStatusBar()
        self._createSidePanel()
        self._createMainPanel()

        layout = QHBoxLayout(self.centralWidget)
        layout.addWidget(self.sidePanel)
        layout.addWidget(self.mainPanel)


    def _createActions(self):
        self.newWindowAction = QAction("&New Window", self)
        self.closeWindowAction = QAction("&Close Window")
        self.newFolderAction = QAction("&Folder", self)
        self.newFileAction = QAction("&File", self)
        self.folderPropAction = QAction("&Folder Properties", self)

        self.openAction = QAction("&Open", self)
        self.cutAction = QAction("C&ut", self)
        self.copyAction = QAction("&Copy", self)
        self.pasteAction = QAction("&Paste", self)
        self.removeAction = QAction("&Remove", self)
        self.getPropAction = QAction("&Properties", self)
        self.renameAction = QAction("&Rename", self)
        self.selectAllAction = QAction("&Select All", self)

        self.reloadFolderAction = QAction("&Reload Folder", self)
        self.showHiddenAction = QAction("&Show Hidden", self)

        self.goPrevAction = QAction(QIcon(":arrow-left.svg"), "&Previous Folder", self)
        self.goNextAction = QAction(QIcon(":arrow-right.svg"), "&Next Folder", self)
        self.goParentAction = QAction("&Parent Folder", self)
        self.goHomeAction = QAction(QIcon(":home.svg"), "&Home", self)

        self.helpAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)

    def _createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(self.newWindowAction)
        fileMenu.addSeparator()
        createMenu = fileMenu.addMenu("&Create")
        createMenu.addAction(self.newFolderAction)
        createMenu.addAction(self.newFileAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.folderPropAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.closeWindowAction)

        editMenu = menuBar.addMenu("Edit")
        editMenu.addAction(self.openAction)
        editMenu.addSeparator()
        editMenu.addAction(self.cutAction)
        editMenu.addAction(self.copyAction)
        editMenu.addAction(self.pasteAction)
        editMenu.addAction(self.removeAction)
        editMenu.addSeparator()
        editMenu.addAction(self.getPropAction)
        editMenu.addSeparator()
        editMenu.addAction(self.renameAction)
        editMenu.addSeparator()
        editMenu.addAction(self.selectAllAction)

        viewMenu = menuBar.addMenu("&View")
        viewMenu.addAction(self.reloadFolderAction)
        viewMenu.addAction(self.showHiddenAction)

        goMenu = menuBar.addMenu("&Go")
        goMenu.addAction(self.goPrevAction)
        goMenu.addAction(self.goNextAction)
        goMenu.addAction(self.goParentAction)
        goMenu.addAction(self.goHomeAction)

        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.helpAction)
        helpMenu.addAction(self.aboutAction)

    def _createToolBars(self):
        toolBar = self.addToolBar("File")
        toolBar.setMovable(False)
        toolBar.addAction(self.goPrevAction)
        toolBar.addAction(self.goNextAction)
        toolBar.addAction(self.goHomeAction)
        self.dirPathSpinBox = QComboBox()
        self.dirPathSpinBox.setEditable(True)
        toolBar.addWidget(self.dirPathSpinBox)

    def _createContextMenu(self):
        self.centralWidget.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.centralWidget.addAction(self.newFileAction)
        self.centralWidget.addAction(self.openAction)
        self.centralWidget.addAction(self.copyAction)
        self.centralWidget.addAction(self.pasteAction)
        self.centralWidget.addAction(self.cutAction)

    def _createStatusBar(self):
        self.statusbar = self.statusBar()
        self.testLabel = QLabel("Test message")
        self.statusbar.addPermanentWidget(self.testLabel)
    
    def _createSidePanel(self):
        self.sidePanel = QWidget(self.centralWidget)
        self.sidePanel.resize(300, 200)
        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(255, 255, 255))
    


        self.sidePanel.setAutoFillBackground(True)
        self.sidePanel.setPalette(pal)

    def _createMainPanel(self):
        self.mainPanel = QWidget()


def main():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()