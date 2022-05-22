import sys
import os
import subprocess
from pathlib import Path
from copy import copy

import qrc_res
from FlowLayout import FlowLayout
from FileButton import FileButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow,
    QDialog,
    QDialogButtonBox,
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
    QTreeWidget,
    QInputDialog,
)
from PyQt5.QtGui import (
    QIcon, 
    QPalette, 
    QColor,
)
from file_mgn import *

class PropertiesDialog(QDialog):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Properties')
        layout = QVBoxLayout()
        # btns = QDialogButtonBox()
        # btns.setStandardButtons(QDialogButtonBox.Ok)
        # layout.addWidget(btns)
        self.setLayout(layout)

        info = getFileInfo(path)
        name = QLabel(f"Name: {path.split(os.sep)[-1]}")
        location = QLabel(f"Location: {'/'.join(path.split(os.sep)[0:-1])}")
        ftype = QLabel(f"Type: {info['type']}")
        permissions = QLabel(f"Permissions: {info['permissions']}")
        size = QLabel(f"Size: {info['size']} K")
        lastmod = QLabel(f"Last modification date: {info['lastmod']}")
        lastaccess = QLabel(f"Last access date: {info['lastaccess']}")
        lastmeta = QLabel(f"Last metadata modification date: {info['lastmeta']}")
        layout.addWidget(name)
        layout.addWidget(location)
        layout.addWidget(ftype)
        layout.addWidget(permissions)
        layout.addWidget(size)
        layout.addWidget(lastmod)
        layout.addWidget(lastaccess)
        layout.addWidget(lastmeta)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("pyfm")
        self.resize(900, 700)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.curPath = os.getenv("HOME")
        self.files = listAllFiles(self.curPath)
        self.highlighted = []
        self.clipboard = []
        self.clipaction = None
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
        for i in self.highlighted:
            i.deHighlight()
        self.highlighted.clear()

        self._getItemCount()

    def manageHighlighted(self, button, ctrl):
        if button not in self.highlighted:
            if ctrl:
                button.highlight()
                self.highlighted.append(button)
            else:
                self._clearHighlited()
                button.highlight()
                self.highlighted.append(button)
        else:
            if ctrl:
                button.deHighlight()
                self.highlighted.remove(button)

        self._getItemCount()

    def jumpToDir(self, dir_path, addToHist):
        dir_path = os.path.realpath(dir_path)
        if os.path.isdir(dir_path):
            if addToHist: 
                self._addToHist(dir_path);

            self.curPath = dir_path
            self.files = listAllFiles(self.curPath)
            self.dirPathSpinBox.setText(self.curPath)
            self._updateMainPanel()
            self._clearHighlited()

    def printDirTree(self, startpath, tree):
        for element in os.listdir(startpath):
            path_info = startpath + "/" + element
            if os.path.isdir(path_info):
                parent_itm = QTreeWidgetItem(tree, [os.path.basename(element)])
                parent_itm.path = path_info
                self.printDirTree(path_info, parent_itm)
                parent_itm.setIcon(0, QIcon(":folder.svg"))

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

    def _handleNewWindowAction(self):
        subprocess.Popen(["python", "./gui.py"])

    def _handleCloseWindowAction(self):
        exit(0)

    def _handleRemoveAction(self):
        removeAllFiles([button.path for button in self.highlighted])
        self.files = listAllFiles(self.curPath)
        self._updateMainPanel()

    def _handleSelectAllAction(self):
        self._clearHighlited()
        for i in reversed(range(self.grid_layout.count())): 
            self.manageHighlighted(self.grid_layout.itemAt(i).widget(), True)

    def _handleReloadFolderAction(self):
        self.files = listAllFiles(self.curPath)
        self._updateMainPanel()

    def _handleCutAction(self):
        self.clipboard = copy([button.path for button in self.highlighted])
        self.clipaction = moveAllFiles

    def _handleCopyAction(self):
        self.clipboard = copy([button.path for button in self.highlighted])
        self.clipaction = copyAllFiles

    def _handlePasteAction(self):
        if len(self.clipboard) > 0:
            self.clipaction(self.clipboard, self.curPath)
            self.clipboard.clear()
            self.files = listAllFiles(self.curPath)
            self._updateMainPanel()

    def _handleGetPropAction(self):
        if len(self.highlighted) > 0:
            dlg = PropertiesDialog(self.highlighted[0].path, parent=self)
            dlg.show()

    def _handleNewFolderAction(self):
        text, ok = QInputDialog.getText(self, "folder name input", "Enter new folder name")
        if ok:
            createDirectory(os.path.join(self.curPath, text))
            self.files = listAllFiles(self.curPath)
            self._updateMainPanel()

    def _handleNewFileAction(self):
        text, ok = QInputDialog.getText(self, "folder name input", "Enter new file name")
        if ok:
            createEmptyFile(os.path.join(self.curPath, text))
            self.files = listAllFiles(self.curPath)
            self._updateMainPanel()

    def _handleRenameAction(self):
        if len(self.highlighted) == 1:
            text, ok = QInputDialog.getText(self, "folder name input", "Enter new file name")
            if ok:
                renameFile(self.highlighted[0].path, os.path.join(self.curPath, text))
                self.files = listAllFiles(self.curPath)
                self._updateMainPanel()

    def _handleGetCurPropAction(self):
        dlg = PropertiesDialog(self.curPath, parent=self)
        dlg.show()
    

    def _createActions(self):
        self.newWindowAction = QAction(QIcon(":add.svg"), "&New Window", self)
        self.newWindowAction.triggered.connect(self._handleNewWindowAction)
        self.closeWindowAction = QAction(QIcon(":minus.svg"), "&Close Window")
        self.closeWindowAction.triggered.connect(self._handleCloseWindowAction)
        self.newFolderAction = QAction(QIcon(":folder.svg"), "&Folder", self)
        self.newFolderAction.triggered.connect(self._handleNewFolderAction)
        self.newFileAction = QAction(QIcon(":file.svg"), "&File", self)
        self.newFileAction.triggered.connect(self._handleNewFileAction)

        self.openAction = QAction(QIcon(":add.svg"), "&Open", self)
        # TODO
        self.cutAction = QAction(QIcon(":scissors.svg"), "C&ut", self)
        self.cutAction.triggered.connect(self._handleCutAction)
        self.copyAction = QAction("&Copy", self)
        self.copyAction.triggered.connect(self._handleCopyAction)
        self.pasteAction = QAction("&Paste", self)
        self.pasteAction.triggered.connect(self._handlePasteAction)
        self.removeAction = QAction(QIcon(":delete.svg"), "&Remove", self)
        self.removeAction.triggered.connect(self._handleRemoveAction)
        self.getPropAction = QAction("&Properties", self)
        self.getPropAction.triggered.connect(self._handleGetPropAction)
        self.renameAction = QAction(QIcon(":edit.svg"), "&Rename", self)
        self.renameAction.triggered.connect(self._handleRenameAction)
        self.selectAllAction = QAction("&Select All", self)
        self.selectAllAction.triggered.connect(self._handleSelectAllAction)

        self.reloadFolderAction = QAction(QIcon(":refresh.svg"), "&Reload Folder", self)
        self.reloadFolderAction.triggered.connect(self._handleReloadFolderAction)
        self.showHiddenAction = QAction("&Show Hidden", self)
        # TODO

        self.goPrevAction = QAction(QIcon(":left.svg"), "&Previous Folder", self)
        self.goPrevAction.triggered.connect(self._handleGoPrevAction)
        self.goNextAction = QAction(QIcon(":right.svg"), "&Next Folder", self)
        self.goNextAction.triggered.connect(self._handleGoNextAction)
        self.goParentAction = QAction(QIcon(":down.svg"), "&Parent Folder", self)
        self.goParentAction.triggered.connect(self._handleGoParentAction)
        self.goHomeAction = QAction(QIcon(":home.svg"), "&Home", self)
        self.goHomeAction.triggered.connect(self._handleGoHomeAction)

        self.helpAction = QAction("&Help Content", self)
        # TODO
        self.aboutAction = QAction("&About", self)
        # TODO

        self.goToAction = QAction(QIcon(":forward.svg"), "&Go to the path in the location bar", self);
        self.goToAction.triggered.connect(self._handleGoToAction)

        self.getCurPropAction = QAction("&Folder Properties", self)
        self.getCurPropAction.triggered.connect(self._handleGetCurPropAction)

    ##### MENU, TOOLBAR, CONTEXT MENU #####

    def _createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        fileMenu.addAction(self.newWindowAction)
        fileMenu.addSeparator()
        createMenu = fileMenu.addMenu("&Create")
        createMenu.addAction(self.newFolderAction)
        createMenu.addAction(self.newFileAction)
        fileMenu.addSeparator()
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
        toolBar.addAction(self.goParentAction)
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
        
        separator1 = QAction(self)
        separator1.setSeparator(True)
        separator2 = QAction(self)
        separator2.setSeparator(True)
        separator3 = QAction(self)
        separator3.setSeparator(True)

        self.centralWidget.addAction(self.newFileAction)
        self.centralWidget.addAction(self.newFolderAction)
        self.centralWidget.addAction(separator1)
        self.centralWidget.addAction(self.pasteAction)
        self.centralWidget.addAction(separator2)
        self.centralWidget.addAction(self.selectAllAction)
        self.centralWidget.addAction(separator3)
        self.centralWidget.addAction(self.getCurPropAction)

    ##### STATUS BAR #####

    def _createStatusBar(self):
        self.statusbar = self.statusBar()
        self._getSpaceUsed(True)

    def _getItemCount(self):
        if len(self.highlighted) == 0:
            message = f"{len(self.files)} items"
        elif len(self.highlighted) == 1:
            message = f"\"{self.highlighted[0].path.split(os.sep)[-1]}\" selected"
        else:
            message = f"{len(self.highlighted)} items selected"

        self.statusbar.showMessage(message, 0)

    def _getSpaceUsed(self, iffirst):
        if not iffirst:
            self.statusbar.removeWidget(self.itemCountLabel)
        total, free = getPartUsage(self.curPath)
        self.itemCountLabel = QLabel(f"Free space: {free[0]:.1f} {free[1]} (Total: {total[0]:.1f} {total[1]})")
        self.statusbar.addPermanentWidget(self.itemCountLabel)

    ##### SIDE PANEL #####
    
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
        dirTreePage = QTreeWidget(self.sidePanel);
        self.printDirTree("/home/lukasz/Projects", dirTreePage)

        def onItemClicked():
            self.jumpToDir(dirTreePage.selectedItems()[0].path, True)

        dirTreePage.doubleClicked.connect(onItemClicked)


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

    ##### MAIN PANEL #####

    def _updateMainPanel(self):
        for i in reversed(range(self.grid_layout.count())): 
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        for f in self.files:
            fileButton = FileButton(f, 70, 70, parent=self)
            self.grid_layout.addWidget(fileButton)

        self._clearHighlited()
        self._getSpaceUsed(False)

    def _createMainPanel(self):
        grid = QWidget()
        grid.mouseReleaseEvent = lambda event: self._clearHighlited()
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