import sys

import qrc_res
from utils.FlowLayout import FlowLayout
from utils.PicButton import FileDirElem
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
    QLayout,
)
from PyQt5.QtGui import (
    QIcon, 
    QPalette, 
    QColor,
    QPixmap,
)

class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("pyfm")
        self.resize(900, 700)
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
        splitter = QSplitter(self.centralWidget)
        layout.addWidget(splitter);
        splitter.addWidget(self.sidePanel)
        splitter.addWidget(self.mainPanel)

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
        self.goNextAction = QAction(QIcon(":right.svg"), "&Next Folder", self)
        self.goParentAction = QAction(QIcon(":down.svg"), "&Parent Folder", self)
        self.goHomeAction = QAction(QIcon(":home.svg"), "&Home", self)

        self.helpAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)

        self.goToAction = QAction(QIcon(":forward.svg"), "&Go to the path in the location bar", self);

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

        names = ["Apple", "Alps", "Berry", "Cherry" ]  # TODO temporary
        completer = QCompleter(names)

        self.dirPathSpinBox = QLineEdit()
        self.dirPathSpinBox.setCompleter(completer)
        toolBar.addWidget(self.dirPathSpinBox)

        toolBar.addAction(self.goToAction);

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

    def _createMainPanel(self):
        grid = QWidget()
        grid_layout = FlowLayout()
        grid.setLayout(grid_layout)

        self.mainPanel = QScrollArea();
        self.mainPanel.setWidgetResizable(True)
        self.mainPanel.setWidget(grid)

        # for _ in range(100):
        #     a = PicButton(QPixmap(":folder.svg"), 70, 70)
        #     grid_layout.addWidget(a)

        # for i in range(25):
        #     grid_layout.addWidget(QLabel(f"Label {i}"))

        for i in range(25):
            a = FileDirElem(QPixmap(":folder.svg"), 70, 70)
            grid_layout.addWidget(a)

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