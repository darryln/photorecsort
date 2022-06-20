#!/usr/bin/python

from defaults import *
import os
import PIL
from PyQt5.QtCore import pyqtSlot, QSize, QPoint, QRect, QRectF
from PyQt5.QtGui import QPalette, QColor, QPixmap, QDrag, QPainter, QResizeEvent, QTransform
from PyQt5.QtWidgets import QApplication, QLabel, QMenu, QAction, QMainWindow, QDesktopWidget
from PyQt5.QtCore import Qt, QMimeData

log = logging.getLogger(__name__) 

class FileView(QLabel):

    def __init__(self, parent):
        super().__init__()
        super(QLabel, self).__init__(parent)
        self.parent = parent
        self.setAutoFillBackground(False)
        self.setMinimumSize(1, 1)
        self.setMaximumSize(QSize(DEFAULT_MAX_SCREEN_HEIGHT, DEFAULT_MAX_SCREEN_HEIGHT))

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("LightGray"))
        self.setPalette(palette)
        self.setWindowTitle("View")

        self.pixmap = QPixmap()
        self.rotation = 0
        self.setAlignment(Qt.AlignTop)
        self.setScaledContents(False)
        self.filepath = ''
        self.showStatusMessage(self.buildStatusMsg())
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

        # create drag object & mime payload
        drag = QDrag(self)
        mimedata = QMimeData()
        # set mime data to file path
        mimedata.setText(self.filepath)
        drag.setMimeData(mimedata)

        # create transparent icon for dragging

        # get pixmap size
        srcSize = QSize(self.pixmap.width(), self.pixmap.height())
        # scale it to icon size
        iconSize = srcSize.scaled(
            DEFAULT_DRAG_ICON_SIZE,DEFAULT_DRAG_ICON_SIZE,
            Qt.AspectRatioMode.KeepAspectRatio)
        # create a pixmap to paint on
        iconPixmap = QPixmap(iconSize)
        # must prefill transparent to avoid artifacts
        # because the constructor does not zero mem
        iconPixmap.fill(Qt.GlobalColor.transparent)
        # QPainter.drawPixmap scales if you specify QRectF for src & dest
        srcRectF = QRectF(0.0, 0.0, float(self.pixmap.width()), float(self.pixmap.height()));
        iconRectF = QRectF(0.0, 0.0, float(iconPixmap.width()), float(iconPixmap.height()));
        # begin painting
        painter = QPainter(iconPixmap)
        hints = painter.renderHints()
        #hints |= painter.Antialiasing
        hints |= painter.SmoothPixmapTransform 
        painter.setRenderHints(hints, True)
        painter.setOpacity(DEFAULT_DRAG_ICON_OPACITY)
        painter.drawPixmap(iconRectF, self.pixmap, srcRectF)
        # end painting
        painter.end()
        # set drag icon
        drag.setPixmap(iconPixmap)
        drag.setHotSpot(QPoint(0,0))
        # start dragging it around
        # TODO: test kbd shift/ctrl modifiers to select copy vs move?
        drag.exec_(Qt.CopyAction | Qt.MoveAction) 

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if not self.pixmap.isNull():
            """
            s = self.size()
            s0 = QSize(a0.oldSize())
            s1 = QSize(a0.size())
            log.info(      f"resizeEvent   w { s.width()} x h { s.height()} \n" \
            f"               event.oldSize w {s0.width()} x h {s0.height()} \n" \
            f"               event.size    w {s1.width()} x h {s1.height()}")
            """
            self.showPixmap()

    @pyqtSlot(QPixmap, str)
    def updatePreview(self, pixmap: QPixmap, filepath: str):
        #log.info(f"updatePreview pixmap w {pixmap.width()} x h {pixmap.height()}")
        #log.info(f"updatePreview file: {filepath}")
        self.pixmap = pixmap
        self.filepath = filepath
        self.resetRotation()
        self.showPixmap()
        self.showStatusMessage(self.buildStatusMsg())

    def showStatusMessage(self, msg : str):
        self.parent.statusbar.showMessage(msg)

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

    def rotate(self):
        self.rotation += 90
        if self.rotation > 270: 
            self.rotation = 0
        self.showPixmap()

    def resetRotation(self):
        self.rotation = 0

    def showPixmap(self):
        pixmap = QPixmap(self.pixmap)
        if self.rotation > 0:
            transform = QTransform().rotate(self.rotation)
            pixmap = pixmap.transformed(transform, 
                Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(pixmap.scaled(self.width(), self.height(), 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation))
