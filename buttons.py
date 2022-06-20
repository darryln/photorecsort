#!/usr/bin/python

from defaults import *
from config import *
import faulthandler; faulthandler.enable()
from os import path
from PyQt5.QtWidgets import QPushButton, QMessageBox
from PyQt5.QtGui import QDragEnterEvent, QDragLeaveEvent
from PyQt5.QtCore import QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

log = logging.getLogger(__name__)

# path to icon files 
# TODO: compile icons to resource
ICON_PATH = 'res/'

# feature button params
BH = 64 # height
BIH = 64 # icon height
BIW = 64 # icon width
BF = 'Arial' # font
BFP = 18 # font point size

# dest button params
DBH = 32 # height
#DBIH = 32 # icon height
#DBIW = 32 # icon width
DBF = 'Arial Narrow' # font
DBFP = 18 # font point size

class AppButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumHeight(BH)
        self.setFont(QFont(BF, BFP))
        self.setIconSize(QSize(BIH, BIW))
        self.setText('')

class ConfigButton(AppButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip('Configure settings')  
        self.setIcon(QIcon(ICON_PATH+'config.png'))

class FilterButton(AppButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip('Filter files')  
        self.setIcon(QIcon(ICON_PATH+'filter.png'))

class SetSourceButton(AppButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip('Select source folder')  
        self.setIcon(QIcon(ICON_PATH+'src.png'))

class SetDestButton(AppButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip('Select destination folder')  
        self.setIcon(QIcon(ICON_PATH+'dest.png'))

class PrevButton(AppButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip('Go to previous item')  
        self.setIcon(QIcon(ICON_PATH+'prev.png'))

class NextButton(AppButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip('Go to next item')  
        self.setIcon(QIcon(ICON_PATH+'next.png'))

class RotateButton(AppButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip('Rotate preview')  
        self.setIcon(QIcon(ICON_PATH+'rotate.png'))

class QuitButton(AppButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip('Quit')  
        self.setIcon(QIcon(ICON_PATH+'quit.png'))

class TrashButton(QPushButton):
    def __init__(self, parent):
        super().__init__()
        super(QPushButton, self).__init__(parent)        
        self.parent = parent
        self.setMinimumHeight(BH)
        self.setFont(QFont(BF, BFP))
        self.setIconSize(QSize(BIH, BIW))
        self.setIcon(QIcon(ICON_PATH+'trash.svg'))
        self.setToolTip('Trash Can')  
        self.setText('')
        self.setAcceptDrops(True)
        self.clicked.connect(self.clickHandler)
        self.highlightStyle = 'QPushButton {background-color: lightgreen}'
        self.normalStyle = 'QPushButton {background-color: white}'

    def clickHandler(self):
        log.info(f"Trash button clicked")
        self.parent.ignoreKeys(True)
        QMessageBox.information(self, 
            'Trash',
            'TODO: dialog to empty trash or select items to restore.', 
            QMessageBox.Ok)
        self.parent.ignoreKeys(False)

    def dragEnterEvent(self, a0):
        if a0.mimeData().hasFormat('text/plain'):
            self.setStyleSheet(self.highlightStyle)
            a0.accept()
        else:
            a0.ignore()

    def dragLeaveEvent(self, a0: QDragLeaveEvent) -> None:
        self.setStyleSheet(self.normalStyle)
        a0.accept()

    def dropEvent(self, a0):
        """
        QMessageBox.information(self, 
            'Text dropped: ',
            a0.mimeData().text(),
            QMessageBox.Ok)
        """
        src = a0.mimeData().text()
        log.info(f"dropped on trash: {src}")
        self.setStyleSheet(self.normalStyle)
        a0.accept()

class DestButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setAcceptDrops(True)
        self.dstFilesPath = ''
        self.setMaximumWidth(DEFAULT_DEST_BUTTON_WIDTH)
        self.setMinimumHeight(DBH)
        self.setFont(QFont(DBF, DBFP))
        self.setEnabled(False)
        self.normalStyle = 'QPushButton {Text-align:left; background-color: white}'
        self.highlightStyle = 'QPushButton {Text-align:left; background-color: lightgreen}'
        self.setStyleSheet(self.normalStyle)
        self.setText("Dest"+str(id(self)))
        self.clicked.connect(self.clickHandler)

    def clickHandler(self):
        log.info(f"{self.text()} button clicked")
        src = self.parent.getCurrentFilePath()
        # build dest file full path
        # dest path + our dir + src's base filename
        text = self.text()
        d = path.sep
        dst = self.dstFilesPath + d + text + d + path.basename(src)
        log.info(f"{text}: src file:{src}")
        log.info(f"{text}: dst file:{dst}")

    def setDestFilePath(self, str):
        self.dstFilesPath = str

    def dragEnterEvent(self, a0: QDragEnterEvent) -> None:
        if a0.mimeData().hasFormat('text/plain'):
            self.setStyleSheet(self.highlightStyle)
            a0.accept()
        else:
            a0.ignore()

    def dragLeaveEvent(self, a0: QDragLeaveEvent) -> None:
        self.setStyleSheet(self.normalStyle)
        a0.accept()

    def dropEvent(self, a0):
        """
        QMessageBox.information(self, 
            'Text dropped: ',
            e.mimeData().text(),
            QMessageBox.Ok)
        """
        src = a0.mimeData().text()
        # build dest file full path
        # dest path + our dir + src's base filename
        text = self.text()
        d = path.sep
        dst = self.dstFilesPath + d + text + d + path.basename(src)
        log.info(f"{text}: src file:{src}")
        log.info(f"{text}: dst file:{dst}")
        self.setStyleSheet(self.normalStyle)

        a0.accept()

