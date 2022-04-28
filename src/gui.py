import sys
import os
from pathlib import Path

import qrc_res
from FlowLayout import FlowLayout
from FileButton import FileButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow, 
    QAction, 
    QLineEdit, 
    QLabel, 
    QCompleter, 
    QSplitter,
    QComboBox,
    QStackedLayout,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QTreeWidgetItem,
)
from PyQt5.QtGui import (
    QIcon, 
    QPalette, 
    QColor,
)
from file_mgn import listAllFiles

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("pyfm")
        self.resize(900, 700)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.curPath = os.getenv("HOME")
        self.files = listAllFiles(self.curPath)
        self.highlited = []
        self.historyIndex = 0
        self.history = [os.getenv("HOME")]

        self._createActions()
        self._createMenuBar()
        self._createToolBars()
        self._createContextMenu()
        self._createStatusBar()
        self._createSidePanel()
        self._createMainPanel()

        layout = QHBoxLayout(self.centralWidget)
        splitter = QSplitter(self.centralWidget)
        layout.addWidget(splitter);
        splitter.addWidget(self.sidePanel)
        splitter.addWidget(self.mainPanel)

    ##### MISCELLANEOUS #####

    def _addToHist(self, dir_path):
        if self.historyIndex == len(self.history)-1:
            self.history.append(dir_path)
            self.historyIndex += 1
        else:
            self.historyIndex += 1
            self.history[self.historyIndex] = dir_path
            self.history = self.history[:self.historyIndex+1]

    def _clearHighlited(self):
        # TODO przywrocenie kolorkow do oryginalnych
        self.highlited.clear()
        pass

    def addToHighlited(self, path, ctrl):
        # TODO zmienianie kolorków podświetlonych elementów
        if ctrl and path not in self.highlited:
            self.highlited.append(path)
        elif not ctrl and path not in self.highlited:
            self._clearHighlited()
            self.highlited.append(path)

    ##### ACTIONS AND ACTION HANDLING #####

    def _handleGoPrevAction(self):
        if self.historyIndex > 0:
            self.historyIndex -= 1
            self.jumpToDir(self.history[self.historyIndex], False)

    def _handleGoNextAction(self):
        if self.historyIndex < len(self.history)-1:
            self.historyIndex += 1
            self.jumpToDir(self.history[self.historyIndex], False)

    def _handleGoParentAction(self):
        pathob = Path(self.curPath)
        path = pathob.parent.absolute()
        self.jumpToDir(path, True)

    def _handleGoHomeAction(self):
        self.jumpToDir(os.getenv("HOME"), True)

    def _handleGoToAction(self):
        self.jumpToDir(self.dirPathSpinBox.text(), True)

    def _createActions(self):
        self.newWindowAction = QAction(QIcon(":add.svg"), "&New Window", self)
        self.closeWindowAction = QAction(QIcon(":minus.svg"), "&Close Window")
        self.newFolderAction = QAction(QIcon(":folder.svg"), "&Folder", self)
        self.newFileAction = QAction(QIcon(":file.svg"), "&File", self)
        self.folderPropAction = QAction("&Folder Properties", self)

        self.openAction = QAction(QIcon(":add.svg"), "&Open", self)
        self.cutAction = QAction(QIcon(":scissors.svg"), "C&ut", self)
        self.copyAction = QAction("&Copy", self)
        self.pasteAction = QAction("&Paste", self)
        self.removeAction = QAction(QIcon(":delete.svg"), "&Remove", self)
        self.getPropAction = QAction("&Properties", self)
        self.renameAction = QAction(QIcon(":edit.svg"), "&Rename", self)
        self.selectAllAction = QAction("&Select All", self)

        self.reloadFolderAction = QAction(QIcon(":refresh.svg"), "&Reload Folder", self)
        self.showHiddenAction = QAction("&Show Hidden", self)

        self.goPrevAction = QAction(QIcon(":left.svg"), "&Previous Folder", self)
        self.goPrevAction.triggered.connect(self._handleGoPrevAction)
        self.goNextAction = QAction(QIcon(":right.svg"), "&Next Folder", self)
        self.goNextAction.triggered.connect(self._handleGoNextAction)
        self.goParentAction = QAction(QIcon(":down.svg"), "&Parent Folder", self)
        self.goParentAction.triggered.connect(self._handleGoParentAction)
        self.goHomeAction = QAction(QIcon(":home.svg"), "&Home", self)
        self.goHomeAction.triggered.connect(self._handleGoHomeAction)

        self.helpAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)

        self.goToAction = QAction(QIcon(":forward.svg"), "&Go to the path in the location bar", self);
        self.goToAction.triggered.connect(self._handleGoToAction)

    ##### CREATIONG OF MENU, TOOLBAR, CONTEXT MENU, STATUS BAR #####

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

        self.dirPathSpinBox = QLineEdit()
        self.dirPathSpinBox.setText(self.curPath)
        # self._setLocationBarCompleter() TODO
        toolBar.addWidget(self.dirPathSpinBox)

        toolBar.addAction(self.goToAction);

    # def _setLocationBarCompleter(self): TODO
    #     names = [f.split(os.sep)[-1] for f in self.files]
    #     completer = QCompleter(names)
    #     self.dirPathSpinBox.setCompleter(completer)

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

    ##### CREATION OF SIDE AND MAIN PANELS #####
    
    def _createSidePanel(self):
        def switchPage():
            stackedLayout.setCurrentIndex(pageCombo.currentIndex())

        self.sidePanel = QWidget(self.centralWidget)
        layout = QVBoxLayout()
        self.sidePanel.setLayout(layout)
        # combo box to switch between pages
        pageCombo = QComboBox()
        pageCombo.addItems(["Directory Tree", "Places"])
        pageCombo.activated.connect(switchPage)
        # stacked layout to switch between pages
        stackedLayout = QStackedLayout()
        # pages
        dirTreePage = QWidget(self.sidePanel)
        stackedLayout.addWidget(dirTreePage)

        placesPage = QWidget(self.sidePanel)
        stackedLayout.addWidget(placesPage)

        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(200, 200, 200))
        dirTreePage.setAutoFillBackground(True)
        dirTreePage.setPalette(pal)

        pal2 = QPalette()
        pal2.setColor(QPalette.Window, QColor(150, 150, 150))
        placesPage.setAutoFillBackground(True)
        placesPage.setPalette(pal2)

        pal3 = QPalette()
        pal3.setColor(QPalette.Window, QColor(50, 50, 50))
        self.sidePanel.setAutoFillBackground(True)
        self.sidePanel.setPalette(pal3)
        self.sidePanel.setMinimumWidth(100)
        self.sidePanel.setMaximumWidth(300)  # TODO initial splitter ratio
        
        layout.addWidget(pageCombo)
        layout.addLayout(stackedLayout)

    def jumpToDir(self, dir_path, addToHist):
        if os.path.isdir(dir_path):
            if addToHist: 
                self._addToHist(dir_path);

            self.curPath = dir_path
            self.files = listAllFiles(self.curPath)
            self.dirPathSpinBox.setText(self.curPath)
            self.highlited.clear()
            self._updateMainPanel()

    def _updateMainPanel(self):
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        for f in self.files:
            fileButton = FileButton(f, 70, 70, parent=self)
            self.grid_layout.addWidget(fileButton)

    def _createMainPanel(self):
        grid = QWidget()
        self.grid_layout = FlowLayout()
        grid.setLayout(self.grid_layout)

        self.mainPanel = QScrollArea();
        self.mainPanel.setWidgetResizable(True)
        self.mainPanel.setWidget(grid)

        self._updateMainPanel()

        pal = QPalette()
        pal.setColor(QPalette.Window, QColor(100, 100, 100))
        self.mainPanel.setAutoFillBackground(True)
        self.mainPanel.setPalette(pal)

def main():
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()