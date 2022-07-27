#!/usr/bin/python
""" File view window """

from PyQt5.QtCore import pyqtSlot, QSize, QPoint
from PyQt5.QtCore import  QEvent
from PyQt5.QtGui import QDrag, QResizeEvent
from PyQt5.QtGui import QEnterEvent, QMouseEvent, QWheelEvent
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QMimeData
from defaults import *
from thumbgrid import ThumbGrid
import json

log = logging.getLogger(__name__) 

class FileView(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setAutoFillBackground(False)
        self.setMinimumSize(1, 1)
        self.setWindowTitle("FileView")
        self.showStatusMessage('')
        self.setContentsMargins(0, 0, 0, 0)
        self.grid = ThumbGrid()
        self.grid.setParent(self)
        self.stride = 4
        self.parent.getFileManager().setStride(self.stride)
        self.setLayout(self.grid)
        self.show()

    @pyqtSlot(list)
    def updateView(self, pathList: list):
        #log.info(f"updateView: pathList: {pathList}")
        self.grid.setPathList(pathList)
        self.setLayout(self.grid)
        self.showStatusMessage('')

    def enterEvent(self, event: QEnterEvent):
        log.info(f"enterEvent: {event}")
        pass

    def leaveEvent(self, event: QEvent):
        log.info(f"leaveEvent: {event}")
        pass

    def mouseDoubleClickEvent(self, event: QMouseEvent ):
        log.info(f"mouseDoubleClickEvent: {event}")
        pass
    
    #def keyPressEvent( event: Qt.QKeyEvent): pass

    def wheelEvent(self, event: QWheelEvent ): 
        log.info(f"wheelEvent: {event}")
        pass

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.leftClickPos = event.pos()
            self.dragStartPosition = event.pos()
            log.info(f"mousePressEvent: left button @{self.leftClickPos}")
        if event.button() == Qt.RightButton:
            self.rightClickPos = event.pos()
            log.info(f"mousePressEvent: right button @{self.rightClickPos}")

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            log.info(f"mouseReleaseEvent: left button @{self.leftClickPos}")
            # TODO: if we were dragging, reset mouse pointer
        if event.button() == Qt.RightButton:
            log.info(f"mouseReleaseEvent: right button @{self.rightClickPos}")
        pass

    def mouseMoveEvent(self, event: QMouseEvent):
        # test for left btn still down
        if not (event.buttons() & Qt.LeftButton):
            return
        # test for minimum drag distance
        if (event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance():
            return
        # get list of selected files
        selectedFiles = self.grid.getSelectedFilesList()
        # none selected
        if len(selectedFiles) == 0: 
            return

        # create drag object & mime payload
        drag = QDrag(self)
        mimedata = QMimeData()
        # set mime data to json of selected files list
        jlist = json.dumps(selectedFiles)
        mimedata.setText(jlist)
        drag.setMimeData(mimedata)

        # TODO: create transparent icon for dragging
        # TODO: change mouse pointer to grab hand

        log.info("dragging selected files:'%s'", jlist)
        """
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
        srcRectF = QRectF(0.0, 0.0, float(self.pixmap.width()), float(self.pixmap.height()))
        iconRectF = QRectF(0.0, 0.0, float(iconPixmap.width()), float(iconPixmap.height()))
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
        """
        drag.setHotSpot(QPoint(0,0))
        # start dragging it around
        drag.exec_(Qt.CopyAction | Qt.MoveAction) 

    def resizeEvent(self, a0: QResizeEvent) -> None:
        s0 = QSize(a0.oldSize())
        s1 = QSize(a0.size())
        log.info(  \
                      f"resizeEvent:          a0.newSize w {s1.width()} x h {s1.height()} \n" \
        f"                                    a0.oldSize w {s0.width()} x h {s0.height()} \n")

    def showStatusMessage(self, msg : str):
        self.parent.showStatusMessage(msg)

