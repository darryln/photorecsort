#!/usr/bin/python

from defaults import *
from os import pathsep, path
from PyQt5.QtWidgets import QPushButton, QMessageBox

log = logging.getLogger(__name__)

class TrashButton(QPushButton):

    def __init__(self, icon, title, parent):
        super().__init__(icon, title, parent)
        self.icon = icon
        self.parent = parent
        self.setAcceptDrops(True)
        self.dstFilesPath = ''
        self.clicked.connect(self.clickHandler)

    def clickHandler(self):
        #log.info(f"Trash button clicked")
        QMessageBox.information(self, 
            'Trash',
            'TODO: dialog to empty trash or select items to restore.', 
            QMessageBox.Ok)

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
        log.info(f"dropped on trash: {src}")


