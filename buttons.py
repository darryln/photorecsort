#!/usr/bin/python

from defaults import *
from config import *
import faulthandler; faulthandler.enable()
import os, shutil
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

log = logging.getLogger(__name__)

# feature button params
BTN_H = 64 # height
BTN_ICON_H = 64 # icon height
BTN_ICON_W = 64 # icon width
BTN_FONT = 'Arial' # font
BTN_FONT_SIZE = 18 # font point size
ICON_PATH = DEFAULT_ICON_FILES_PATH

class AppButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setMinimumHeight(BTN_H)
        self.setFont(QFont(BTN_FONT, BTN_FONT_SIZE))
        self.setIconSize(QSize(BTN_ICON_H, BTN_ICON_W))
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
        self.setToolTip('Rotate preview. Shift-click to rotate file')  
        self.setIcon(QIcon(ICON_PATH+'rotate.png'))

class QuitButton(AppButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setToolTip('Quit')  
        self.setIcon(QIcon(ICON_PATH+'quit.png'))


