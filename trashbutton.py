
# [Trash Info]
# Path=/home/embsysdev/some_path_to_file/somefile.ext
# DeletionDate=2022-06-19T22:24:59

from defaults import *
from config import *
import faulthandler; faulthandler.enable()
import os, shutil
from PyQt5.QtWidgets import QPushButton, QMessageBox, QInputDialog
from PyQt5.QtGui import QDragEnterEvent, QDragLeaveEvent
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from send2trash import send2trash

from buttons import BTN_H, BTN_ICON_H, BTN_ICON_W, BTN_FONT, BTN_FONT_SIZE, ICON_PATH

DEFAULT_TRASH_FILES_PATH = str('/home/'+USER+'/.local/share/.Trash/files')
DEFAULT_TRASH_INFO_PATH = str('/home/'+USER+'/.local/share/.Trash/info')

class TrashButton(QPushButton):
    def __init__(self, parent):
        super().__init__()
        super(QPushButton, self).__init__(parent)        
        self.parent = parent
        self.setMinimumHeight(BTN_H)
        self.setFont(QFont(BTN_FONT, BTN_FONT_SIZE))
        self.setIconSize(QSize(BTN_ICON_H, BTN_ICON_W))
        self.iconEmpty = QIcon(ICON_PATH+'trash.svg')
        self.iconFull = QIcon(ICON_PATH+'trash-full.svg')
        self.updateIcon()
        self.setToolTip('Trash Can')  
        self.setText('')
        self.setAcceptDrops(True)
        self.clicked.connect(self.clickHandler)
        self.highlightStyle = 'QPushButton {background-color: lightgreen}'
        self.normalStyle = 'QPushButton {background-color: white}'
        # update icon on a timer
        self.refreshTimer = QTimer(self)
        self.refreshTimer.setInterval(1000) # milliseconds
        self.refreshTimer.setSingleShot(False)
        self.refreshTimer.timeout.connect(self.updateIcon)

    def updateIcon(self):
        if (self.isTrashEmpty()):
            self.setIcon(self.iconEmpty)
        else:
            self.setIcon(self.iconFull)

    def isTrashEmpty(self):
        p = getTrashFilesPath()
        if os.path.isdir(p):
            if not os.listdir(p):
                return True
            else:    
                return False
        else:
            msg = f"Cannot find system trash '{getTrashBasePath()}'"
            raise FatalError(msg)
        return True

    def clickHandler(self):
        log.info(f"Trash button clicked")
        """
        self.parent.ignoreKeys(True)
        QMessageBox.information(self, 
            'Trash',
            'TODO: dialog to empty trash or select items to restore.', 
            QMessageBox.Ok)
        self.parent.ignoreKeys(False)
        """
        src = self.parent.getCurrentFilePath()
        src = src.strip()
        if src == '':
            return
        log.info(f"trashing: {src}")
        try:
            send2trash(src)
            log.info(f"moved to trash ok")
            self.parent.removeFileFromList(src)
        except:
            log.info(f"error moving to trash")

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
