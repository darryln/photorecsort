#!/usr/bin/python
""" video player widget """

#import faulthandler; import faulthandler.enable()
import sys
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QWidget, QPushButton, QFileDialog, QStyle, QVBoxLayout)
import sys
from defaults import *

log = logging.getLogger(__name__)

class VideoView(QWidget):
    def __init__(self):
        super().__init__()
        #self.setWindowTitle("VideoView") 
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.videoWidget = QVideoWidget()
 
        #self.playButton = QPushButton()
        #self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        #self.playButton.clicked.connect(self.play)
 
        #self.openButton = QPushButton("Open Video")   
        #self.openButton.clicked.connect(self.openFile)
 
        widget = QWidget(self)
        self.setCentralWidget(widget)
 
        #layout = QVBoxLayout()
        #layout.addWidget(videoWidget)
        #layout.addWidget(self.openButton)
        #layout.addWidget(self.playButton)
 
        #widget.setLayout(layout)
        self.mediaPlayer.setVideoOutput(videoWidget)
 
    def showPreview(self):
        #TODO: show static preview frame with play icon superimposed
        pass

    def hidePreview(self):
        #TODO: hide static preview, revealing video "underneath"
        self.mediaPlayer.set
        pass

    def openFile(self, fpath):
        self.fpath = fpath
        self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fpath)))
        self.showPreview()
 
    def play(self):
        match self.mediaPlayer.state():
            case QMediaPlayer.State.PlayingState:
                self.mediaPlayer.stop()
                self.showPreview()
            case QMediaPlayer.State.PausedState:
                self.mediaPlayer.stop()
                self.showPreview()
            case QMediaPlayer.State.StoppedState:
                self.hidePreview()
                self.mediaPlayer.play()
