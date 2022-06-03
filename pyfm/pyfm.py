import sys
import os
import subprocess
from pathlib import Path
from copy import copy

import pyfm.qrcRes
from pyfm.FlowLayout import FlowLayout
from pyfm.FileButton import FileButton
from pyfm.fileMng import *
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, 
    QWidget, 
    QMainWindow,
    QDialog,
    QMessageBox,
    QAction, 
    QLineEdit, 
    QLabel, 
    QCompleter, 
    QSplitter,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QTreeWidgetItem,
    QTreeWidget,
    QInputDialog,
    QDirModel,
)
from PyQt5.QtGui import (
    QIcon, 
    QPalette, 
    QColor,
)

class PropertiesDialog(QDialog):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Properties')
        layout = QVBoxLayout()
        self.setLayout(layout)

        info = getFileInfo(path)
        name = QLabel(f"Name: {path.split(os.sep)[-1]}")
        location = QLabel(f"Location: {'/'.join(path.split(os.sep)[0:-1])}")
        ftype = QLabel(f"Type: {info['type']}")
        permissions = QLabel(f"Permissions: {info['permissions']}")
        size = QLabel(f"Size: {info['size']} K")
        lastMod = QLabel(f"Last modification date: {info['lastmod']}")
        lastAccess = QLabel(f"Last access date: {info['lastaccess']}")
        lastMeta = QLabel(f"Last metadata modification date: {info['lastmeta']}")
        layout.addWidget(name)
        layout.addWidget(location)
        layout.addWidget(ftype)
        layout.addWidget(permissions)
        layout.addWidget(size)
        layout.addWidget(lastMod)
        layout.addWidget(lastAccess)
        layout.addWidget(lastMeta)

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
        layout.addWidget(splitter)
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

    def jumpToDir(self, dirPath, addToHist):
        try:
            dirPath = os.path.realpath(dirPath)
            if os.path.isdir(dirPath):
                if addToHist: 
                    self._addToHist(dirPath)

                self.curPath = dirPath
                self.files = listAllFiles(self.curPath)
                self.dirPathSpinBox.setText(self.curPath)
                self._updateMainPanel()
                self._clearHighlited()
        except PermissionError:
            QMessageBox.about(self, "Error", "Unable to open the directory due to lack of permissions")

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
        try:
            removeAllFiles([button.path for button in self.highlighted])
            self.files = listAllFiles(self.curPath)
            self._updateMainPanel()
        except PermissionError:
            QMessageBox.about(self, "Error", "Unable remove the file due to lack of permissions")

    def _handleSelectAllAction(self):
        self._clearHighlited()
        for i in reversed(range(self.gridLayout.count())): 
            self.manageHighlighted(self.gridLayout.itemAt(i).widget(), True)

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
        try:
            if len(self.clipboard) > 0:
                self.clipaction(self.clipboard, self.curPath)
                self.clipboard.clear()
                self.files = listAllFiles(self.curPath)
                self._updateMainPanel()
        except PermissionError:
            QMessageBox.about(self, "Error", "Unable to paste the files due to lack of permissions")
        except shutil.Error:
            QMessageBox.about(self, "Error", "Unable to paste, files already exist")

    def _handleGetPropAction(self):
        try:
            if len(self.highlighted) > 0:
                dlg = PropertiesDialog(self.highlighted[0].path, parent=self)
                dlg.show()
        except PermissionError:
            QMessageBox.about(self, "Error", "Unable to get file properties due to lack of permissions")

    def _handleNewFolderAction(self):
        try:
            text, ok = QInputDialog.getText(self, "folder name input", "Enter new folder name")
            if ok:
                createDirectory(os.path.join(self.curPath, text))
                self.files = listAllFiles(self.curPath)
                self._updateMainPanel()
        except PermissionError:
            QMessageBox.about(self, "Error", "Unable to create folder due to lack of permissions")
        except FileExistsError:
            QMessageBox.about(self, "Error", "Unable to create, the folder already exists")

    def _handleNewFileAction(self):
        try:
            text, ok = QInputDialog.getText(self, "folder name input", "Enter new file name")
            if ok:
                createEmptyFile(os.path.join(self.curPath, text))
                self.files = listAllFiles(self.curPath)
                self._updateMainPanel()
        except PermissionError:
            QMessageBox.about(self, "Error", "Unable to create file due to lack of permissions")
        except FileExistsError:
            QMessageBox.about(self, "Error", "Unable to create, the file already exists")

    def _handleRenameAction(self):
        try:
            if len(self.highlighted) == 1:
                text, ok = QInputDialog.getText(self, "folder name input", "Enter new file name")
                if ok:
                    renameFile(self.highlighted[0].path, os.path.join(self.curPath, text))
                    self.files = listAllFiles(self.curPath)
                    self._updateMainPanel()
        except PermissionError:
            QMessageBox.about(self, "Error", "Unable to rename the file due to lack of permissions")
        except IsADirectoryError:
            QMessageBox.about(self, "Error", "Unable to rename, directory with that name already exists")

    def _handleGetCurPropAction(self):
        try:
            dlg = PropertiesDialog(self.curPath, parent=self)
            dlg.show()
        except PermissionError:
            QMessageBox.about(self, "Error", "Unable to get file properties due to lack of permissions")
    
    def _handleOpenAction(self):
        if len(self.highlighted) == 1:
            self.jumpToDir(self.highlighted[0].path, True);

    def _handleAboutAction(self):
        QMessageBox.about(self, "About", "Python file manager\nŁukasz Wala")

    def _createActions(self):
        self.newWindowAction = QAction(QIcon(":add.svg"), "&New Window", self)
        self.newWindowAction.triggered.connect(self._handleNewWindowAction)
        self.newWindowAction.setShortcut("Ctrl+N")
        self.closeWindowAction = QAction(QIcon(":minus.svg"), "&Close Window")
        self.closeWindowAction.triggered.connect(self._handleCloseWindowAction)
        self.closeWindowAction.setShortcut("Ctrl+Q")
        self.newFolderAction = QAction(QIcon(":folder.svg"), "&Folder", self)
        self.newFolderAction.triggered.connect(self._handleNewFolderAction)
        self.newFolderAction.setShortcut("Shift+Ctrl+N")
        self.newFileAction = QAction(QIcon(":file.svg"), "&File", self)
        self.newFileAction.triggered.connect(self._handleNewFileAction)
        self.newFileAction.setShortcut("Alt+Ctrl+N")

        self.openAction = QAction(QIcon(":add.svg"), "&Open", self)
        self.openAction.triggered.connect(self._handleOpenAction);
        self.cutAction = QAction(QIcon(":scissors.svg"), "C&ut", self)
        self.cutAction.triggered.connect(self._handleCutAction)
        self.cutAction.setShortcut("Ctrl+X")
        self.copyAction = QAction("&Copy", self)
        self.copyAction.triggered.connect(self._handleCopyAction)
        self.copyAction.setShortcut("Ctrl+C")
        self.pasteAction = QAction("&Paste", self)
        self.pasteAction.triggered.connect(self._handlePasteAction)
        self.pasteAction.setShortcut("Ctrl+V")
        self.removeAction = QAction(QIcon(":delete.svg"), "&Remove", self)
        self.removeAction.triggered.connect(self._handleRemoveAction)
        self.getPropAction = QAction("&Properties", self)
        self.getPropAction.triggered.connect(self._handleGetPropAction)
        self.getPropAction.setShortcut("Alt+Return")
        self.renameAction = QAction(QIcon(":edit.svg"), "&Rename", self)
        self.renameAction.triggered.connect(self._handleRenameAction)
        self.renameAction.setShortcut("F2")
        self.selectAllAction = QAction("&Select All", self)
        self.selectAllAction.triggered.connect(self._handleSelectAllAction)
        self.selectAllAction.setShortcut("Ctrl+A")

        self.reloadFolderAction = QAction(QIcon(":refresh.svg"), "&Reload Folder", self)
        self.reloadFolderAction.triggered.connect(self._handleReloadFolderAction)
        self.reloadFolderAction.setShortcut("F5")

        self.goPrevAction = QAction(QIcon(":left.svg"), "&Previous Folder", self)
        self.goPrevAction.triggered.connect(self._handleGoPrevAction)
        self.goPrevAction.setShortcut("Alt+Left")
        self.goNextAction = QAction(QIcon(":right.svg"), "&Next Folder", self)
        self.goNextAction.triggered.connect(self._handleGoNextAction)
        self.goNextAction.setShortcut("Alt+Right")
        self.goParentAction = QAction(QIcon(":down.svg"), "&Parent Folder", self)
        self.goParentAction.triggered.connect(self._handleGoParentAction)
        self.goParentAction.setShortcut("Alt+Up")
        self.goHomeAction = QAction(QIcon(":home.svg"), "&Home", self)
        self.goHomeAction.triggered.connect(self._handleGoHomeAction)
        self.goHomeAction.setShortcut("Alt+Home")

        self.aboutAction = QAction("&About", self)
        # TODO

        self.goToAction = QAction(QIcon(":forward.svg"), "&Go to the path in the location bar", self)
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

        goMenu = menuBar.addMenu("&Go")
        goMenu.addAction(self.goPrevAction)
        goMenu.addAction(self.goNextAction)
        goMenu.addAction(self.goParentAction)
        goMenu.addAction(self.goHomeAction)

        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.aboutAction)

    def _createToolBars(self):
        toolBar = self.addToolBar("Toolbar")
        toolBar.setMovable(False)
        toolBar.addAction(self.goPrevAction)
        toolBar.addAction(self.goNextAction)
        toolBar.addAction(self.goParentAction)
        toolBar.addAction(self.goHomeAction)

        self.dirPathSpinBox = QLineEdit()
        self.dirPathSpinBox.setText(self.curPath)
        self.dirPathSpinBox.returnPressed.connect(self._handleGoToAction)
        
        completer = QCompleter(self)
        completer.setModel(QDirModel(completer))
        self.dirPathSpinBox.setCompleter(completer)

        toolBar.addWidget(self.dirPathSpinBox)

        toolBar.addAction(self.goToAction)

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

    def _printDirTree(self, item):
        if item.wasExpanded: return
        item.wasExpanded = True
        startPath = item.path
        try:
            for element in os.listdir(startPath):
                path_info = startPath + "/" + element
                if os.path.isdir(path_info):
                    parent_itm = QTreeWidgetItem(item, [os.path.basename(element)])
                    parent_itm.path = path_info
                    parent_itm.setIcon(0, QIcon(":folder.svg"))
                    parent_itm.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
                    parent_itm.wasExpanded = False
            
            if len(os.listdir(startPath)) == 0:
                parent_itm = QTreeWidgetItem(item, ["<No subfolders>"])

        except PermissionError:
            parent_itm = QTreeWidgetItem(item, ["<Permissions denied>"])
    
    def _createSidePanel(self):
        self.sidePanel = QWidget(self.centralWidget)
        layout = QVBoxLayout()
        self.sidePanel.setLayout(layout)


        dirTree = QTreeWidget(self.sidePanel)
        dirTree.setHeaderLabels(["Directory Tree"])

        def onItemClicked():
            self.jumpToDir(dirTree.selectedItems()[0].path, True)

        dirTree.doubleClicked.connect(onItemClicked)
        dirTree.itemExpanded.connect(self._printDirTree)

        home = QTreeWidgetItem(dirTree, [os.path.basename(os.getenv("HOME"))])
        home.path = os.getenv("HOME")
        home.setIcon(0, QIcon(":folder.svg"))
        home.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        home.wasExpanded = False

        root = QTreeWidgetItem(dirTree, ["/"])
        root.path = "/"
        root.setIcon(0, QIcon(":folder.svg"))
        root.setChildIndicatorPolicy(QTreeWidgetItem.ShowIndicator)
        root.wasExpanded = False

        self.sidePanel.setMinimumWidth(100)
        self.sidePanel.setMaximumWidth(300)
        
        layout.addWidget(dirTree)

    ##### MAIN PANEL #####

    def _updateMainPanel(self):
        for i in reversed(range(self.gridLayout.count())): 
            self.gridLayout.itemAt(i).widget().setParent(None)
        
        for f in self.files:
            fileButton = FileButton(f, 60, 60, parent=self)
            self.gridLayout.addWidget(fileButton)

        self._clearHighlited()
        self._getSpaceUsed(False)

    def _createMainPanel(self):
        grid = QWidget()
        grid.mouseReleaseEvent = lambda event: self._clearHighlited()
        self.gridLayout = FlowLayout()
        grid.setLayout(self.gridLayout)

        self.mainPanel = QScrollArea()
        self.mainPanel.setWidgetResizable(True)
        self.mainPanel.setWidget(grid)

        self._updateMainPanel()


def createColorPalette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    return palette

def main():
    app = QApplication(sys.argv)

    app.setPalette(createColorPalette())

    win = Window()
    win.show()
    sys.exit(app.exec_())
