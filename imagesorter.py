#!/usr/bin/python

from defaults import *
from config import *
import faulthandler; faulthandler.enable()
import sys
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread, QEvent, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from imagefiles import ImageFiles
from imageview import ImageView
from dragtargetbutton import DragTargetButton
from trashbutton import TrashButton

log = logging.getLogger("imagesorter")

# async worker to load files
class FileLoader(QThread):

    signal = pyqtSignal()

    def __init__(self, ref: ImageFiles):
        QThread.__init__(self)
        self.imageFiles = ref

    def run(self):
        log.info("FileLoader: entry")
        # call load function
        self.imageFiles.loadFiles()
        # tell gui thread about new files
        self.signal.emit()
        log.info("FileLoader: exit")


class ImageSorter(QMainWindow):

    def __init__(self):
        super().__init__()
        self.appQuitFlag = False
        self.ignoreKeysFlag = False
        self.imageFiles = ImageFiles()
        self.srcPath = self.imageFiles.getSourcePath()
        qApp.installEventFilter(self)
        self.statusbar = self.statusBar()
        self.initUI()
        log.info('scanning source path for files')
        self.startLoaderThread(self.srcPath)
        log.info('scanning dest dir subdir names')
        self.loadDestDirs(self.imageFiles.getDestPath())

    def getCurrentImagePath(self):
        return self.imageFiles.getFilePath()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress: #or event.type() == QEvent.KeyRelease:
            #log.info(f"eventFilter: key {hex(event.key())} modifiers {hex(event.modifiers())} text '{event.text()}'")
            #log.info(f"eventFilter: nativeVirtualKey {hex(event.nativeVirtualKey())} nativeModifiers {hex(event.modifiers())} nativeScanCode {hex(event.nativeScanCode())}") 
            if not self.ignoreKeysFlag:
                self.keyPressEvent(event)
                return True
        return super(ImageSorter, self).eventFilter(source, event)

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
        elif k == Qt.Key.Key_Right:
            self.nextBtnClicked()
        elif k == Qt.Key.Key_Left:
            self.prevBtnClicked()
        elif k == Qt.Key.Key_L:
            self.loadBtnClicked()
        elif k == Qt.Key.Key_D:
            self.destBtnClicked()

    """
    def resizeEvent(self, event):
        log.info(f"main window: resize event w {self.width()} h {self.height()}")
        self.resize(self.width(), self.height())
    """

    """
    def showStats(self) :
        self.stats.setText(self.imageView.getStats())
    """

    def configBtnClicked(self):
        #log.info('config button clicked')
        QMessageBox.information(self, 
            'Config',
            'TODO: dialog to edit program options.', 
            QMessageBox.Ok)

    def filterBtnClicked(self):
        #log.info('filter button clicked')
        QMessageBox.information(self, 
            'Filter',
            'TODO: dialog to edit file filter options.', 
            QMessageBox.Ok)

    """
    def trashBtnClicked(self):
        #log.info('trash button clicked')
        QMessageBox.information(self, 
            'Trash',
            'TODO: implement drop handling in button.', 
            QMessageBox.Ok)
    """

    def nextBtnClicked(self):
        #log.info('next button clicked')
        self.imageFiles.next()

    @pyqtSlot()
    def filesLoaded(self):
        log.info('filesLoaded got signal')
        # connect ImageView slot to ImageFiles signal
        self.imageFiles.signal.connect(self.imageView.updateImage)
        # enable buttons
        self.enableButtons()
        # restore normal mouse cursor
        arrow = Qt.CursorShape.ArrowCursor
        QApplication.setOverrideCursor(arrow)
        self.imageFiles.refresh()

    def disableButtons(self):
        self.nextBtn.setEnabled(False)
        self.prevBtn.setEnabled(False)
        self.quitBtn.setEnabled(False)
        self.configBtn.setEnabled(False)
        self.filterBtn.setEnabled(False)
        self.loadBtn.setEnabled(False)

    def enableButtons(self):
        self.nextBtn.setEnabled(True)
        self.prevBtn.setEnabled(True)
        self.quitBtn.setEnabled(True)
        self.configBtn.setEnabled(True)
        self.filterBtn.setEnabled(True)
        self.loadBtn.setEnabled(True)

    def prevBtnClicked(self):
        #log.info('prev clicked')
        self.imageFiles.prev()

    # called on Quit button clicked
    def quitBtnClicked(self):
        #log.info('quit clicked')
        self.appQuitFlag = True
        self.close()

    def loadBtnClicked(self):
        #log.info('load button clicked')
        # get path from modal file selector dialog 
        # starting in currently selected folder
        currentPath = self.imageFiles.getSourcePath()
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
        self.imageFiles.setSourcePath(newPath)
        newPath = self.imageFiles.getSourcePath()
        self.startLoaderThread(newPath)

    def startLoaderThread(self, srcFilesPath):
        # clear displayed frame
        self.imageView.clear()
        # disable buttons while loading files
        self.disableButtons()
        # show hourglass mouse cursor while loading
        busy  = Qt.CursorShape.BusyCursor
        QApplication.setOverrideCursor(busy)
        # create and start worker thread
        self.loaderThread = FileLoader(self.imageFiles)
        # connect signal to slot
        self.loaderThread.signal.connect(self.filesLoaded)
        # run it
        self.loaderThread.start()

    def destBtnClicked(self):
        #log.info('dest button clicked')
        # get path from modal file selector dialog 
        # starting in currently selected folder
        currentPath = self.imageFiles.getDestPath()
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
        self.imageFiles.setDestPath(newPath)
        destPath = self.imageFiles.getDestPath()
        # get dirs below dest dir
        self.destDirs = self.imageFiles.getDestDirs()
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
            else:
                btn.setEnabled(False)
                btn.setText('')
                btn.setDestFilePath('')

    def rotateBtnClicked(self):
        pass

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
        self.setWindowTitle('Image Sorter')
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

        # create image sink
        self.imageView = ImageView(self)
        self.imageView.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # path to icon files 
        # TODO: compile to resource
        ICON_PATH = 'res/'
        
        # nav button params
        BH = 64 # height
        BIH = 64 # icon height
        BIW = 64 # icon width
        BF = 'Arial' # font
        BFP = 18 # font point size
        
        # dest btn params
        DBH = 32 # height
        #DBIH = 32 # icon height
        #DBIW = 32 # icon width
        DBF = 'Arial Narrow' # font
        DBFP = 18 # font point size
        
        # create feature buttons
        self.configBtn = QPushButton(QIcon(ICON_PATH+'config.png'),'', self)
        self.configBtn.setToolTip('Configure settings')  
        self.configBtn.setMinimumHeight(BH)
        self.configBtn.setFont(QFont(BF, BFP))
        self.configBtn.setIconSize(QSize(BIH, BIW))
        self.configBtn.clicked.connect(self.configBtnClicked)

        self.filterBtn = QPushButton(QIcon(ICON_PATH+'filter.png'),'', self)
        self.filterBtn.setToolTip('Filter files')  
        self.filterBtn.setMinimumHeight(BH)
        self.filterBtn.setFont(QFont(BF, BFP))
        self.filterBtn.setIconSize(QSize(BIH-12, BIW))
        self.filterBtn.clicked.connect(self.filterBtnClicked)

        self.loadBtn = QPushButton(QIcon(ICON_PATH+'src.png'),'', self)
        self.loadBtn.setToolTip('Select source')  
        self.loadBtn.setMinimumHeight(BH)
        self.loadBtn.setFont(QFont(BF, BFP))
        self.loadBtn.setIconSize(QSize(BIH, BIW))
        self.loadBtn.clicked.connect(self.loadBtnClicked)

        self.destBtn = QPushButton(QIcon(ICON_PATH+'dest.png'),'', self)
        self.destBtn.setToolTip('Select destination')  
        self.destBtn.setMinimumHeight(BH)
        self.destBtn.setFont(QFont(BF, BFP))
        self.destBtn.setIconSize(QSize(BIH, BIW))
        self.destBtn.clicked.connect(self.destBtnClicked)

        self.rotateBtn = QPushButton(QIcon(ICON_PATH+'rotate.png'),'', self)
        self.rotateBtn.setToolTip('Rotate current image')  
        self.rotateBtn.setMinimumHeight(BH)
        self.rotateBtn.setFont(QFont(BF, BFP))
        self.rotateBtn.setIconSize(QSize(BIH, BIW))
        self.rotateBtn.clicked.connect(self.rotateBtnClicked)

        self.quitBtn = QPushButton(QIcon(ICON_PATH+'quit.png'),'', self)
        self.quitBtn.setToolTip('Quit')  
        self.quitBtn.setMinimumHeight(BH)
        self.quitBtn.setFont(QFont(BF, BFP))
        self.quitBtn.setIconSize(QSize(BIH, BIW))
        self.quitBtn.clicked.connect(self.quitBtnClicked)

        self.nextBtn = QPushButton(QIcon(ICON_PATH+'next.png'),'', self)
        self.nextBtn.setToolTip('Go to next item')  
        self.nextBtn.setMinimumHeight(BH)
        self.nextBtn.setFont(QFont(BF, BFP))
        self.nextBtn.setIconSize(QSize(BIH, BIW))
        self.nextBtn.clicked.connect(self.nextBtnClicked)

        self.prevBtn = QPushButton(QIcon(ICON_PATH+'prev.png'),'', self)
        self.prevBtn.setToolTip('Go to previous item')  
        self.prevBtn.setMinimumHeight(BH)
        self.prevBtn.setFont(QFont(BF, BFP))
        self.prevBtn.setIconSize(QSize(BIH, BIW))
        self.prevBtn.clicked.connect(self.prevBtnClicked)

        self.trashBtn = TrashButton(QIcon(ICON_PATH+'trash.svg'),'', self)
        self.trashBtn.setToolTip('Trash Can')  
        self.trashBtn.setMinimumHeight(BH)
        self.trashBtn.setFont(QFont(BF, BFP))
        self.trashBtn.setIconSize(QSize(BIH, BIW))
        #self.trashBtn.clicked.connect(self.trashBtnClicked)

        # add feature buttons to layout
        self.btnLayout.addWidget(self.configBtn)
        self.btnLayout.addWidget(self.filterBtn)
        self.btnLayout.addWidget(self.loadBtn)
        self.btnLayout.addWidget(self.destBtn)
        self.btnLayout.addWidget(self.prevBtn)
        self.btnLayout.addWidget(self.nextBtn)
        self.btnLayout.addWidget(self.rotateBtn)
        self.btnLayout.addWidget(self.trashBtn)
        self.btnLayout.addWidget(self.quitBtn)
        self.btnLayout.setAlignment(Qt.AlignBottom)

        # create destination buttons
        self.destBtns = []
        for n in range(DEFAULT_DEST_BUTTON_ROWS*DEFAULT_DEST_BUTTON_COLS):
            lbl = f'Dest{n}'
            btn = DragTargetButton(lbl, self)
            btn.setMinimumHeight(DBH)
            btn.setFont(QFont(DBF, DBFP))
            btn.setEnabled(False)
            self.destBtns.insert(n, btn)
            row = n % DEFAULT_DEST_BUTTON_ROWS
            col = n // DEFAULT_DEST_BUTTON_ROWS
            self.destLayout.addWidget(self.destBtns[n], row, col)
        self.destLayout.setAlignment(Qt.AlignRight)

        self.hLayout.addWidget(self.imageView, 1)
        self.hLayout.addLayout(self.destLayout, 0)
        self.hLayout.setAlignment(Qt.AlignTop)

        self.mainLayout.addLayout(self.hLayout)
        self.mainLayout.addLayout(self.btnLayout)

        # add central widget
        cw = QWidget()
        cw.setLayout(self.mainLayout)
        self.setCentralWidget(cw)

        # animate stats
        #self.timer = QTimer()
        #self.timer.start()
        #self.timer.timeout.connect(self.showStats)
        #self.timer.start(777) 

def main():
    ConfigCheck()
    app = QApplication(sys.argv)
    w = ImageSorter()
    w.show()
    result = app.exec_()
    log.info("app exited")
    sys.exit(result)

if __name__ == '__main__':
    main()
