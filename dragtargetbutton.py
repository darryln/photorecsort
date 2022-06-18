#!/usr/bin/python

from defaults import *
from os import pathsep, path
from PyQt5.QtWidgets import QPushButton, QMessageBox

log = logging.getLogger(__name__)

class DragTargetButton(QPushButton):

    def __init__(self, title, parent):
        super().__init__(title, parent)
        self.parent = parent
        self.setAcceptDrops(True)
        self.dstFilesPath = ''
        self.clicked.connect(self.clickHandler)

    def clickHandler(self):
        log.info(f"{self.text()} button clicked")
        src = self.parent.getCurrentImagePath()
        # build dest file full path
        # dest path + our dir + src's base filename
        text = self.text()
        d = path.sep
        dst = self.dstFilesPath + d + text + d + path.basename(src)
        log.info(f"{text}: src file:{src}")
        log.info(f"{text}: dst file:{dst}")

    def setDestFilePath(self, str):
        self.dstFilesPath = str

    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        """
        QMessageBox.information(self, 
            'Text dropped: ',
            e.mimeData().text(),
            QMessageBox.Ok)
        """
        src = e.mimeData().text()
        # build dest file full path
        # dest path + our dir + src's base filename
        text = self.text()
        d = path.sep
        dst = self.dstFilesPath + d + text + d + path.basename(src)
        log.info(f"{text}: src file:{src}")
        log.info(f"{text}: dst file:{dst}")


