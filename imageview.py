#!/usr/bin/python

from defaults import *
import os
import PIL
from PyQt5.QtCore import pyqtSlot, QRect, QSize
from PyQt5.QtGui import QPalette, QColor, QPixmap, QDrag, QPainter, QKeySequence
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QAction
from PyQt5.QtCore import Qt, QMimeData

log = logging.getLogger(__name__) 

class ImageView(QLabel):

    def __init__(self, parent):
        super().__init__()
        super(QLabel, self).__init__(parent)
        self.parent = parent
        self.setAutoFillBackground(False)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("LightGray"))
        self.setPalette(palette)
        self.setWindowTitle("ImageView")

        self.pixmap = QPixmap()
        self.filepath = ''
        statusMsg = self.buildStatusMsg()
        self.parent.statusbar.showMessage(statusMsg)
        self.createActions()

    def contextMenuEvent(self, event):
        self.parent.ignoreKeys(True) # block Escape, etc
        contextMenu = QMenu(self)
        contextMenu.addAction(self.action1)
        contextMenu.addAction(self.action2)
        contextMenu.addAction(self.action3)
        contextMenu.exec_(self.mapToGlobal(event.pos()))
        self.parent.ignoreKeys(False)

    def action1(self):
        log.info(f"context menu action1 method called")

    def action2(self):
        log.info(f"context menu action2 method called")

    def action3(self):
        log.info(f"context menu action3 method called")

    def createActions(self):
        self.action1 = QAction("Action1", self, #shortcut=QKeySequence.Action1,
                statusTip="action 1", triggered=self.action1)

        self.action2 = QAction("Action2", self, #shortcut=QKeySequence.Action2,
                statusTip="action 2", triggered=self.action2)

        self.action3 = QAction("Action3", self, #shortcut=QKeySequence.Action3,
                statusTip="action 3", triggered=self.action3)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QDrag(self)
        mimedata = QMimeData()
        # get image file name
        mimedata.setText(self.filepath)
        drag.setMimeData(mimedata)
        pixmap = QPixmap(self.width(),self.height())
        painter = QPainter(pixmap)
        dragIconSize = QSize(self.width(), self.height())
        dragIconSize.scale(QSize(128,128), Qt.AspectRatioMode.KeepAspectRatio)
        dragIconRect = QRect(event.pos(),dragIconSize)
        painter.setOpacity(0.6)
        painter.drawPixmap(dragIconRect, self.grab())
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())
        drag.exec_(Qt.CopyAction | Qt.MoveAction)


    #def resizeEvent(self, event):
        #log.info"(f"ImageView: resize event w {self.width()} h {self.height()}")
        #if not self.pixmap.isNull():
        #    self.pixmap.scaled(self.width(), self.height(), 
        #        Qt.AspectRatioMode.KeepAspectRatio, 
        #        Qt.TransformationMode.SmoothTransformation)

    @pyqtSlot(QPixmap, str)
    def updateImage(self, pixmap: QPixmap, filepath: str):
        #log.info(f"ImageView: updateImage pixmap w {self.width()} h {self.height()}")
        #log.info(f"ImageView: updateImage file: {filepath}")
        self.pixmap  = pixmap.scaled(self.width(), self.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(self.pixmap)
        self.filepath = filepath
        statusMsg = self.buildStatusMsg()
        self.parent.statusbar.showMessage(statusMsg)

    def buildStatusMsg(self):
        s = str()
        if (self.filepath == ''):
            return ''
        iformat = ''
        iwidth = 0
        iheight = 0
        imode = ''
        ipixels = 0
        ifilesize = 0
        try:
            ifilesize = os.stat(self.filepath).st_size
            with PIL.Image.open(self.filepath) as img:
                iformat = img.format
                imode = img.mode
                iwidth = img.width
                iheight = img.height
                ipixels = iwidth * iheight
        except Exception as e:
            log.info(f"Exception:", e.Message)
            pass
        
        return f"{self.filepath}, {iformat} {imode}, {iwidth}x{iheight}, " \
                f"{self.humanize_pixels(ipixels)} pixels, {self.humanize_bytes(ifilesize)} on disk"

    def humanize(self, nBytes, tags, precision):
        i = 0
        double_bytes = nBytes
        while (i < len(tags) and  nBytes >= 1024):
            double_bytes = nBytes / 1024.0
            i = i + 1
            nBytes = nBytes / 1024
        return round(double_bytes, precision), i

    def humanize_bytes(self, nBytes):
        tags = [ " bytes", "KB", " MB", "GB", "TB" ]
        (n,i) = self.humanize(nBytes,tags,1)
        return str(n) + tags[i]

    def humanize_pixels(self, nBytes):
        tags = [ "", "K", "M", "G", "T" ]
        (n,i) = self.humanize(nBytes,tags,1)
        return str(n) + tags[i]
