
#import os
#import time
#import PIL
#import PIL.Image
#import PIL.features
#from PIL.ExifTags import TAGS, GPSTAGS
#from PyQt5.QtCore import pyqtSlot, QSize, QPoint, QRect, QRectF
#from PyQt5.QtCore import Qt, QMimeData
#from PyQt5.QtGui import QPalette, QColor, QPixmap, QDrag, QPainter, QResizeEvent, QTransform
#from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QLabel #, QMenu, QGridLayout
#from PyQt5.QtWidgets import QAction
#from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
#from PyQt5.QtMultimediaWidgets import QVideoWidget
#from numpy import row_stack
from defaults import *
#from enum import Enum, unique, auto
from flowlayout import FlowLayout
from filethumb import FileThumb

log = logging.getLogger(__name__) 

class ThumbGrid(FlowLayout):

    def __init__(self):
        super().__init__()
        self.pathList = list()

    def removeAllThumbs(self):
        while self.count():
            child = self.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def setPathList(self, pathList : list):
        self.removeAllThumbs()
        for f in pathList:
            thumb = FileThumb(f)
            self.addWidget(thumb)
        self.pathList = pathList

    """
    def addThumb(self, filePath: str):
        thumb = FileThumb(filePath)
        self.addWidget(thumb)

    def findThumb(self, filePath: str) -> FileThumb:
        for n in self.count():
            thumb = FileThumb(self.itemAt(n))
            if thumb.widget() and thumb.getFilePath() == filePath:
                return thumb
        return None

    def removeThumb(self, filePath: str):
        thumb = self.findThumb(filePath)
        if (thumb != None):
            thumb.widget().deleteLater()

    def selectThumb(self, filePath: str, flag: bool):
        thumb = self.findThumb(filePath)
        if (thumb != None):
            thumb.select(flag)
    
    def isThumbSelected(self, filePath: str) -> bool:
        thumb = self.findThumb(filePath)
        if (thumb != None):
            return thumb.selected
        return False

    """

    def getSelectedFilesList(self) -> list:
        sel = list()
        # TODO: walk grid, build list of selected
        # return dummy for now
        sel.append("selectedFilePath1")
        sel.append("selectedFilePath2")
        sel.append("selectedFilePath3")
        return sel
