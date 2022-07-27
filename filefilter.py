#!/usr/bin/python
""" Container for a group of settings to filter scanned files """

import os
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QObject
from defaults import *

log = logging.getLogger(__name__) 

class FileFilter(QObject):

    def __init__(self, name=None):
        super().__init__()

