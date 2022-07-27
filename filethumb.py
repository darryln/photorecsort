#!/usr/bin/python
""" Widget to show file thumbnail based on detected file type. Inherits from QLabel """

import os
import time
import PIL
import PIL.Image
import PIL.features
from PIL.ExifTags import TAGS, GPSTAGS
from PyQt5.QtCore import pyqtSlot, QSize, QPoint, QRect, QRectF
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPalette, QColor, QPixmap, QDrag, QPainter, QResizeEvent, QTransform
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QLabel, QMenu, QGridLayout
from PyQt5.QtWidgets import QAction
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from numpy import row_stack
from defaults import *
from enum import Enum, unique, auto
from flowlayout import FlowLayout

log = logging.getLogger(__name__)


class FileType(Enum):
    pass

class FileThumb(QLabel):
    def __init__(self, filePath):
        super().__init__()
        self.filePath = filePath
        self.setAutoFillBackground(False)
        self.setMinimumSize(32, 32)
        self.thumbSize = 32
        self.setScaledContents(True)
        #self.createActions()
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("LightGray"))
        self.setPalette(palette)
        self.setWindowTitle("")
        self.pixmap = QPixmap()
        self.rotation = 0
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setContentsMargins(0, 0, 0, 0)
        #self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        #self.videoWidget = QVideoWidget()
        #log.info(f"creating thumbnail for {self.filePath}")
        self.loadImage(self.filePath)
        #self.createThumbnail()
        self.selected = False
        self.show()

    def select(self, flag: bool):
        self.selected = flag
        self.setb

    def selected(self) -> bool:
        return self.selected

    def getFilePath(self):
        return self.filePath

    # create thumbnail
    def createThumbnail(self):
        # get pixmap size
        srcSize = QSize(self.pixmap.width(), self.pixmap.height())
        # scale it to icon size
        thumbSize = srcSize.scaled(
            self.thumbSize, self.thumbSize,
            Qt.AspectRatioMode.KeepAspectRatio)
        # create a pixmap to paint on
        thumbPixmap = QPixmap(thumbSize)
        # must prefill transparent to avoid artifacts
        # because the constructor does not zero mem
        thumbPixmap.fill(Qt.GlobalColor.transparent)
        # QPainter.drawPixmap scales if you specify QRectF for src & dest
        srcRectF = QRectF(0.0, 0.0, float(self.pixmap.width()),
                          float(self.pixmap.height()))
        thumbRectF = QRectF(0.0, 0.0, float(
            thumbPixmap.width()), float(thumbPixmap.height()))
        # begin painting
        painter = QPainter(thumbPixmap)
        hints = painter.renderHints()
        #hints |= painter.Antialiasing
        hints |= painter.SmoothPixmapTransform
        painter.setRenderHints(hints, True)
        painter.setOpacity(1.0)
        painter.drawPixmap(thumbRectF, self.pixmap, srcRectF)
        # end painting
        painter.end()
        # set containing label with this thumbnail
        self.setPixmap(thumbPixmap)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        if not self.pixmap.isNull():
            # """
            s0 = QSize(a0.oldSize())
            s1 = QSize(a0.size())
            log.info(
                f"resizeEvent:          a0.size    w {s1.width()} x h {s1.height()} \n"
                f"                                    a0.oldSize w {s0.width()} x h {s0.height()} \n")
            # """
            self.showPixmap()

    def showPixmap(self):
        pixmap = QPixmap(self.pixmap)
        if pixmap.size() == QSize(0, 0):
            log.info(f"showPixmap: null pixmap {self.filePath}")
            # TODO: create pixmap on the fly based on file extension
            pixmap = QPixmap('res/file-generic.svg')
            s3 = self.size()
            self.setPixmap(pixmap.scaled(s3.width()//4, s3.height()//4,
                                         Qt.AspectRatioMode.KeepAspectRatio))
        else:
            if self.rotation > 0:
                transform = QTransform().rotate(self.rotation)
                pixmap = pixmap.transformed(transform,
                                            Qt.TransformationMode.SmoothTransformation)
            # """
            s0 = super().size()
            s1 = self.pixmap.size()
            s2 = pixmap.size()
            s3 = self.size()
            log.info(
                f"showPixmap: super QLabel.size    w { s0.width()} x h { s0.height()} \n"
                f"                           orig pixmap.size    w { s1.width()} x h { s1.height()} \n"
                f"                    transformed pixmap.size    w { s2.width()} x h { s2.height()} \n"
                f"                          current self.size    w { s3.width()} x h { s3.height()} \n")
            # """
            self.setPixmap(pixmap.scaled(s3.width(), s3.height(),
                                         Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation))

    """
    def buildStatusMsg(self) -> str:
        s = str()
        if (self.filePath == ''):
            return ''
        iformat = ''
        iwidth = 0
        iheight = 0
        imode = ''
        ipixels = 0
        ifilesize = 0
        try:
            ifilesize = os.stat(self.filePath).st_size
            with PIL.Image.open(self.filePath) as img:
                iformat = img.format
                imode = img.mode
                iwidth = img.width
                iheight = img.height
                ipixels = iwidth * iheight
                return f"{self.filePath}, {iformat} {imode}, {iwidth}x{iheight}, " \
                        f"{self.humanize_pixels(ipixels)} pixels, {self.humanize_bytes(ifilesize)} on disk"
        except PIL.UnidentifiedImageError:
            log.info(f"buildStatusMsg: non-image {self.filePath}")
            ifilesize = os.stat(self.filePath).st_size
            return f"{self.filePath}, {self.humanize_bytes(ifilesize)} on disk"
        except Exception:
            log.error(f"buildStatusMsg:", exc_info=True)
        return f"{self.filePath}"
    """

    # rotate preview
    def rotate(self):
        self.rotation += 90
        if self.rotation > 270:
            self.rotation = 0
        self.showPixmap()

    def resetRotation(self):
        self.rotation = 0

    def loadImage(self, fpath: str):
        log.info(f'loadImage:{fpath}')
        self.clear()
        if not os.path.exists(fpath):
            log.error('file not found ')
            return
        basename = os.path.basename(fpath)
        ext = os.path.splitext(fpath)[1][1:]
        try:
            with PIL.Image.open(fpath) as img:
                width = img.width
                height = img.height
                fmt = img.format
                mode = img.mode
                log.info("loadImage:'%s' '%s' %s %s %d x %d " % \
                    (basename, ext, fmt, mode, width, height ))
                self.setPixmap(QPixmap(fpath))
        except PIL.UnidentifiedImageError:
            log.info("unsupported image format - default icon")
            self.setPixmap(QPixmap('res/file-generic.svg'))

        """
        f = fpath
        try:
            self.loadImageFile(f)
            except ExceptionFileMgrException_NotFound:
                # problem loading, skip
                pass
            except FileMgrException_LoadFailed:
                # problem loading, skip
                pass
            except FileMgrException_Filtered:
                # filtered, skip
                pass
            except (FileMgrException_ImageFormatNotSupported,
                FileMgrException_ImageFormatUnidentified):
                # Pillow can't read it
                # check recovered file formats
                #log.info(f"Checking non-image file ")
                ext = os.path.splitext(f)[1][1:]
                found = [item for item in DEFAULT_PHOTOREC_FILE_FORMATS 
                    if item[0] == ext]
                if len(found):
                    desc = found[0][1]
                    filtered = found[0][2]
                else:
                    desc = ''
                    filtered = False
                #TODO: load icon
                log.info(f"non-image    :'{os.path.basename(f)}' '{ext}' '{desc}' {'Filtered' if filtered else ''}")
                self.fileList.append(f)
            except Exception:
                log.error(f"loadFiles:", exc_info=True)
                pass
            """

    """def createActions(self):
        self.action1 = QAction("Show File Info", self,
                               statusTip="Show detailed file info", triggered=self.showFileInfo)

        self.action2 = QAction("Rotate File", self,
                               statusTip="Rotate File", triggered=self.rotateFile)

        # self.action3 = QAction("Action3", self, #shortcut=QKeySequence.Action3,
        #    statusTip="action 3", triggered=None)
    """

    """def contextMenuEvent(self, event: QContextMenuEvent):
        log.info(f"contextMenuEvent: {event}")
        #self.parent.ignoreKeys(True)  # block Escape, etc
        contextMenu = QMenu(self)
        contextMenu.addAction(self.action1)
        contextMenu.addAction(self.action2)
        # contextMenu.addAction(self.action3)
        contextMenu.exec_(self.mapToGlobal(event.pos()))
        #self.parent.ignoreKeys(False)
    """

    def showFileInfo(self):
        log.info("show file info")
        if len(self.fileList) == 0:
            return
        mbox = QMessageBox()
        title = "File Info"
        mbox.setText(title)
        mbox.setStandardButtons(QMessageBox.Ok)
        mbox.setIcon(QMessageBox.Information)
        # TODO: find which grid position was right-clicked
        msg = ""
        try:
            with PIL.Image.open(self.filepath) as img:
                msg = f"{img.filename} \n\n"

                #msg += f"Created: {time.ctime(os.path.getctime(self.filepath))}"
                msg += f"Modified: {time.ctime(os.path.getmtime(self.filepath))}\n\n"

                msg += f"Format: {img.format}\n" \
                    f"Mode: {img.mode}\n" \
                    f"Size: {img.size}\n" \
                    f"Width: {img.width}\n" \
                    f"Height: {img.height}\n" \
                    f"Palette: {img.palette}"
                exif = img.getexif()
            if not exif is None:
                msg += "\n\nEXIF data: \n"
                for key, val in exif.items():
                    if key in TAGS:
                        msg += f"\n{TAGS[key]}:{val}"
                    if key in GPSTAGS:
                        msg += f"\n{GPSTAGS[key]}:{val}"
        except PIL.UnidentifiedImageError:
            msg = "This image file format is not supported."

        log.info(msg)
        mbox.setInformativeText(msg)
        mbox.exec_()

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
                return f"{self.filepath}, {iformat} {imode}, {iwidth}x{iheight}, " \
                    f"{self.humanize_pixels(ipixels)} pixels, {self.humanize_bytes(ifilesize)} on disk"
        except PIL.UnidentifiedImageError:
            log.info(f"buildStatusMsg: non-image {self.filepath}")
            ifilesize = os.stat(self.filepath).st_size
            return f"{self.filepath}, {self.humanize_bytes(ifilesize)} on disk"
        except Exception:
            log.error(f"buildStatusMsg:", exc_info=True)
        return f"{self.filepath}"

    def humanize(self, nBytes, tags, precision):
        i = 0
        double_bytes = nBytes
        while (i < len(tags) and nBytes >= 1024):
            double_bytes = nBytes / 1024.0
            i = i + 1
            nBytes = nBytes / 1024
        return round(double_bytes, precision), i

    def humanize_bytes(self, nBytes):
        tags = [" bytes", "KB", " MB", "GB", "TB"]
        (n, i) = self.humanize(nBytes, tags, 1)
        return str(n) + tags[i]

    def humanize_pixels(self, nBytes):
        tags = ["", "K", "M", "G", "T"]
        (n, i) = self.humanize(nBytes, tags, 1)
        return str(n) + tags[i]

    """
    def rotateBtnClicked(self):
        if (QApplication.keyboardModifiers() == Qt.ShiftModifier):
            # rotate file (destructive)
            self.parent.getFileManager().rotateFile()
        else:
            # rotate preview (non-destructive)
            self.rotate()

    # rotate preview
    def rotate(self):
        self.rotation += 90
        if self.rotation > 270: 
            self.rotation = 0
        #self.showPixmap()

    def resetRotation(self):
        self.rotation = 0 
    """

    """
    def showPixmap(self):
        pixmap = QPixmap(self.pixmap)
        if pixmap.size() == QSize(0,0):
            log.info(f"showPixmap: null pixmap {self.filepath}")
            #TODO: create pixmap on the fly based on file extension
            pixmap = QPixmap('res/file-generic.svg')
            s3 = self.size()
            self.setPixmap(pixmap.scaled(s3.width()//4, s3.height()//4, 
                Qt.AspectRatioMode.KeepAspectRatio))
        else:
            if self.rotation > 0:
                transform = QTransform().rotate(self.rotation)
                pixmap = pixmap.transformed(transform, 
                    Qt.TransformationMode.SmoothTransformation)
            s0 = super().size()
            s1 = self.pixmap.size()
            s2 = pixmap.size()
            s3 = self.size()
            log.info( \
                        f"showPixmap: super QLabel.size    w { s0.width()} x h { s0.height()} \n" \
            f"                           orig pixmap.size    w { s1.width()} x h { s1.height()} \n" \
            f"                    transformed pixmap.size    w { s2.width()} x h { s2.height()} \n" \
            f"                          current self.size    w { s3.width()} x h { s3.height()} \n" )
            self.setPixmap(pixmap.scaled(s3.width(), s3.height(), 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation))
            """

    """
        log.info(f"updateView pixmap w {pixmap.width()} x h {pixmap.height()}")
        self.pixmap = pixmap
        self.filepath = filepath
        self.resetRotation()
        self.showPixmap() 
    """


@unique
class FileType(Enum):
    '3gp',
    '7z',
    'ai',
    'aif',
    'ani',
    'avi',
    'bmp',
    'caf',
    'cdr',
    'db',
    'doc',
    'docx',
    'dv',
    'dwg',
    'dxf',
    'epub',
    'gif',
    'gz',
    'ipt',
    'iso',
    'jar',
    'jpg',
    'm4p',
    'mid',
    'mov',
    'mp4',
    'mpg',
    'odg',
    'ods',
    'odt',
    'ogg',
    'pcx',
    'pdf',
    'png',
    'ppt',
    'rar',
    'sda',
    'sxw',
    'tar',
    'vsd',
    'wav',
    'wdb',
    'wim',
    'wma',
    'wmf',
    'wmv',
    'wps',
    'xls',
    'xlsx',
    'xpi',
    'zip'
