#!/usr/bin/python

import faulthandler; faulthandler.enable()
import sys
from PyQt5.QtCore import Qt, QThread, QEvent, QSize, pyqtSignal, pyqtSlot
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from filemgr import FileMgr
from fileview import FileView
from buttons import *
from config import *
from trashbutton import TrashButton
from destbutton import DestButton

log = logging.getLogger("app")

# async worker to scan files
class SourceFilesScanThread(QThread):

    signal = pyqtSignal()

    def __init__(self, ref: FileMgr):
        QThread.__init__(self)
        self.fileMgr = ref

    def run(self):
        log.info("SourceFilesScanThread: entry")
        # call load function
        self.fileMgr.loadFiles()
        # tell gui thread about new files
        self.signal.emit()
        log.info("SourceFilesScanThread: exit")


class AppMainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.appQuitFlag = False
        self.ignoreKeysFlag = False
        self.fileMgr = FileMgr()
        self.srcPath = self.fileMgr.getSourcePath()
        qApp.installEventFilter(self)
        self.statusbar = self.statusBar()
        self.initUI()
        log.info('starting source file loader thread')
        self.startLoaderThread(self.srcPath)
        log.info('scanning dest dir subdir names')
        self.loadDestDirs(self.fileMgr.getDestPath())

    def getCurrentFilePath(self):
        return self.fileMgr.getFilePath()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress: #or event.type() == QEvent.KeyRelease:
            #log.info(f"eventFilter: key {hex(event.key())} modifiers {hex(event.modifiers())} text '{event.text()}'")
            #log.info(f"eventFilter: nativeVirtualKey {hex(event.nativeVirtualKey())} nativeModifiers {hex(event.modifiers())} nativeScanCode {hex(event.nativeScanCode())}") 
            if not self.ignoreKeysFlag:
                self.keyPressEvent(event)
                return True
        return super(AppMainWindow, self).eventFilter(source, event)

    def ignoreKeys(self, flag: bool):
        self.ignoreKeysFlag = flag
        """
        if (flag):
            log.info("ignore keys on")
        else:
            log.info("ignore keys off")
        """

    def keyPressEvent(self, e):
        self.keyhandler(e)

    def keyhandler(self, e):
        k = e.key()
        #log.info(f"keyHandler:{hex(k)}")
        if k == Qt.Key.Key_Escape:
            self.quitBtnClicked()
        elif k == Qt.Key.Key_Q:
            self.quitBtnClicked()
        elif k == Qt.Key.Key_Delete:
            self.trashBtn.clickHandler()
        elif k == Qt.Key.Key_Right:
            self.nextBtnClicked()
        elif k == Qt.Key.Key_Left:
            self.prevBtnClicked()
        elif k == Qt.Key.Key_L:
            self.setSourceBtnClicked()
        elif k == Qt.Key.Key_D:
            self.setDestBtnClicked()

    def configBtnClicked(self):
        #log.info('config button clicked')
        self.ignoreKeys(True)
        QMessageBox.information(self, 
            'Config',
            'TODO: dialog to edit program options.', 
            QMessageBox.Ok)
        self.ignoreKeys(False)

    def filterBtnClicked(self):
        log.info('filter button clicked')
        self.ignoreKeys(True)
        QMessageBox.information(self, 
            'Filter',
            'TODO: dialog to edit file filter options.', 
            QMessageBox.Ok)
        self.ignoreKeys(False)

    def nextBtnClicked(self):
        #log.info('next button clicked')
        if self.fileMgr.getNumFilesInList() == 0:
            self.statusbar.showMessage("No files.")
            self.fileView.clear()
        self.fileMgr.next()

    @pyqtSlot()
    def filesLoaded(self):
        log.info('filesLoaded got signal')
        # connect View slot to Files signal
        self.fileMgr.signal.connect(self.fileView.updatePreview)
        # enable buttons
        self.enableButtons()
        # restore normal mouse cursor
        arrow = Qt.CursorShape.ArrowCursor
        QApplication.setOverrideCursor(arrow)
        self.fileMgr.refresh()
        if self.fileMgr.getNumFilesInList() == 0:
            self.statusbar.showMessage("No files.")
            self.fileView.clear()

    def disableButtons(self):
        self.configBtn.setEnabled(False)
        self.filterBtn.setEnabled(False)
        self.setSourceBtn.setEnabled(False)
        self.setDestBtn.setEnabled(False)
        self.prevBtn.setEnabled(False)
        self.nextBtn.setEnabled(False)
        self.rotateBtn.setEnabled(False)
        self.trashBtn.setEnabled(False)
        self.quitBtn.setEnabled(False)

    def enableButtons(self):
        self.configBtn.setEnabled(True)
        self.filterBtn.setEnabled(True)
        self.setSourceBtn.setEnabled(True)
        self.setDestBtn.setEnabled(True)
        self.prevBtn.setEnabled(True)
        self.nextBtn.setEnabled(True)
        self.rotateBtn.setEnabled(True)
        self.trashBtn.setEnabled(True)
        self.quitBtn.setEnabled(True)

    def removeFileFromList(self, filepath):
        self.fileMgr.removeFileFromList(filepath)
        if self.fileMgr.getNumFilesInList() == 0:
            self.statusbar.showMessage("No files.")
            self.fileView.clear()

    def prevBtnClicked(self):
        #log.info('prev clicked')
        if self.fileMgr.getNumFilesInList() == 0:
            self.statusbar.showMessage("No files.")
            self.fileView.clear()
        self.fileMgr.prev()

    # called on Quit button clicked
    def quitBtnClicked(self):
        #log.info('quit clicked')
        self.appQuitFlag = True
        self.close()

    def setSourceBtnClicked(self):
        #log.info('load button clicked')
        # get path from modal file selector dialog 
        # starting in currently selected folder
        currentPath = self.fileMgr.getSourcePath()
        #log.info("currentPath:", currentPath)
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode())
        newPath = dlg.getExistingDirectory( self, 'Select recovered files directory', currentPath )
        if newPath == '':
            log.info("loadBtnClicked: dlg canceled")
            # canceled
            return
        print(newPath)
        log.info(f"new src path: {newPath}")
		# set source folder
        self.fileMgr.setSourcePath(newPath)
        newPath = self.fileMgr.getSourcePath()
        self.startLoaderThread(newPath)

    def startLoaderThread(self, srcFilesPath):
        # clear displayed frame
        self.fileView.clear()
        # disable buttons while loading files
        self.disableButtons()
        # show hourglass mouse cursor while loading
        busy  = Qt.CursorShape.BusyCursor
        QApplication.setOverrideCursor(busy)
        # create and start worker thread
        self.loaderThread = SourceFilesScanThread(self.fileMgr)
        # connect signal to slot
        self.loaderThread.signal.connect(self.filesLoaded)
        # run it
        self.loaderThread.start()

    def setDestBtnClicked(self):
        #log.info('dest button clicked')
        # get path from modal file selector dialog 
        # starting in currently selected folder
        currentPath = self.fileMgr.getDestPath()
        #log.info("currentPath:", currentPath)
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.FileMode())
        newPath = dlg.getExistingDirectory( self, 'Select destination directory', currentPath )
        if newPath == '':
            log.info("destBtnClicked: dlg canceled")
            # canceled
            return
        log.info(f"new dest path:{newPath}")
        self.loadDestDirs(newPath)
    
    def loadDestDirs(self, newPath):
		# set dest dir
        self.fileMgr.setDestPath(newPath)
        destPath = self.fileMgr.getDestPath()
        # get dirs below dest dir
        self.destDirs = self.fileMgr.getDestDirs()
        nDirs = len(self.destDirs)
        nBtns = len(self.destBtns)
        log.info(f"{nDirs} dest dirs")
        log.info(f"{nBtns} dest buttons")
        for n in range(nBtns):
            btn = self.destBtns[n]
            if n < nDirs:
                btn.setEnabled(True)
                btn.setText(self.destDirs[n])
                btn.setDestFilePath(destPath)
                btn.enableClick(True)
                btn.enableDrop(True)
            else:
                btn.setEnabled(True)
                btn.setText('')
                btn.setDestFilePath(destPath)
                btn.enableClick(False)
                btn.enableDrop(False)

    def showStatusMessage(self, msg : str):
        n = self.fileMgr.getNumFilesInList()
        i = 1 + self.fileMgr.getCurrentFileIndex()
        self.statusbar.showMessage(f"File {i} of {n}: {msg}")

    def rotateBtnClicked(self):
        if (QApplication.keyboardModifiers() == Qt.ShiftModifier):
            # rotate file (destructive)
            self.fileMgr.rotateFile()
        else:
            # rotate preview (non-destructive)
            self.fileView.rotate()

    # called on main window "X" closer clicked
    def closeEvent(self, event):
        #log.info('main window closed')
        self.appQuitFlag = True
        event.accept()

    def initUI(self):
        # set main window defaults, initial size/pos
        QToolTip.setFont(QFont('SansSerif', 10))
        scrn = QDesktopWidget().availableGeometry()
        # TODO: handle multiheaded systems
		#self.screenCount = QDesktopWidget().screenCount()
        #self.whichScreen = QDesktopWidget().screenNumber(self)
        self.maxSize = QSize(scrn.height(), scrn.width())
        scrn.setHeight(int(scrn.height()*DEFAULT_MAIN_WINDOW_SIZE_FACTOR))
        scrn.setWidth(int(scrn.width()*DEFAULT_MAIN_WINDOW_SIZE_FACTOR))
        self.resize(scrn.width(),scrn.height())
        self.setWindowTitle(DEFAULT_APP_NAME)
        frame = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center)
        self.move(frame.topLeft())

        # create layouts
        self.mainLayout = QVBoxLayout() # cw and btn
        self.mainLayout.setSizeConstraint(QLayout.SizeConstraint.SetNoConstraint)
        self.hLayout = QHBoxLayout() # main and dest
        self.destLayout = QGridLayout()
        self.btnLayout = QHBoxLayout()

        # create view
        self.fileView = FileView(self)
        self.fileView.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # create feature buttons
        self.configBtn = ConfigButton(self)
        self.configBtn.clicked.connect(self.configBtnClicked)

        self.filterBtn = FilterButton(self)
        self.filterBtn.clicked.connect(self.filterBtnClicked)

        self.setSourceBtn = SetSourceButton(self)
        self.setSourceBtn.clicked.connect(self.setSourceBtnClicked)

        self.setDestBtn = SetDestButton(self)
        self.setDestBtn.clicked.connect(self.setDestBtnClicked)

        self.nextBtn = NextButton(self)
        self.nextBtn.clicked.connect(self.nextBtnClicked)

        self.prevBtn = PrevButton(self)
        self.prevBtn.clicked.connect(self.prevBtnClicked)

        self.rotateBtn = RotateButton(self)
        self.rotateBtn.clicked.connect(self.rotateBtnClicked)

        self.trashBtn = TrashButton(self)
        # TrashButton class handles click & drop

        self.quitBtn = QuitButton(self)
        self.quitBtn.clicked.connect(self.quitBtnClicked)


        # add feature buttons to layout
        self.btnLayout.addWidget(self.configBtn)
        self.btnLayout.addWidget(self.filterBtn)
        self.btnLayout.addWidget(self.setSourceBtn)
        self.btnLayout.addWidget(self.setDestBtn)
        self.btnLayout.addWidget(self.prevBtn)
        self.btnLayout.addWidget(self.nextBtn)
        self.btnLayout.addWidget(self.rotateBtn)
        self.btnLayout.addWidget(self.trashBtn)
        self.btnLayout.addWidget(self.quitBtn)
        self.btnLayout.setAlignment(Qt.AlignBottom)
        self.btnLayout.setStretch(0,0)

        # create destination buttons
        self.destBtns = []
        for n in range(DEFAULT_DEST_BUTTON_ROWS*DEFAULT_DEST_BUTTON_COLS):
            btn = DestButton(self)
            self.destBtns.insert(n, btn)
            row = n % DEFAULT_DEST_BUTTON_ROWS
            col = n // DEFAULT_DEST_BUTTON_ROWS
            self.destLayout.addWidget(self.destBtns[n], row, col)
        self.destLayout.setAlignment(Qt.AlignRight)

        self.hLayout.addWidget(self.fileView, 1)
        self.fileView.setAlignment(Qt.AlignLeft)
        self.fileView.setContentsMargins(0, 0, 0, 0)
        self.hLayout.addLayout(self.destLayout)
        self.hLayout.setAlignment(Qt.AlignTop)

        self.mainLayout.addLayout(self.hLayout)
        self.mainLayout.addLayout(self.btnLayout)

        # add central widget
        cw = QWidget()
        cw.setLayout(self.mainLayout)
        self.setCentralWidget(cw)

def main():
    ConfigCheck()
    app = QApplication(sys.argv)
    w = AppMainWindow()
    w.show()
    result = app.exec_()
    log.info("app exited")
    sys.exit(result)

if __name__ == '__main__':
    main()
