from defaults import *
import PIL
import PIL.features
import os, time
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObject, pyqtSignal

log = logging.getLogger(__name__)

class FileMgr(QObject):
    # signal to send a preview of image or other file
    signal = pyqtSignal(QPixmap, str)

    def __init__(self, name=None):
        super().__init__()
        self.loaded = False
        self.initComplete = False
        self.srcFilesPath = DEFAULT_SRC_FILES_PATH
        self.dstFilesPath = DEFAULT_DST_FILES_PATH
        self.fileList = []
        self.fileListIndex = 0
        self.nFilesInList = len(self.fileList)
        #log.info("pilinfo:")
        #PIL.features.pilinfo(out=None, supported_formats=False)
        #PIL.features.get_supported()

    def isLoaded(self): 
        return self.loaded

    def getSourcePath(self):
        return self.srcFilesPath
        
    def setSourcePath(self, newPath):
        log.info(f"setSourcePath:{newPath}")
        self.srcFilesPath = newPath

    def getDestPath(self):
        return self.dstFilesPath
        
    def getDestDirs(self):
        log.info(f"scanning dest dirs under {self.dstFilesPath}")
        dirlist = next(os.walk(self.dstFilesPath))[1]
        log.info(f"found {len(dirlist)} dest dirs")
        dirlist.sort()
        return dirlist
        
    def setDestPath(self, newPath):
        log.info(f"setDestPath:{newPath}")
        self.dstFilesPath = newPath

    # build set of file extensions
    def scanExtensions(self, rootPath):
        exts = set(os.path.splitext(f)[1][1:]
            for dir,dirs,files in os.walk(rootPath) 
                for f in files)
        return exts

    # generator function to emit all files under rootPath
    def scanFiles(self, rootPath):
        for entry in os.scandir(rootPath):
            if entry.is_file():
                yield os.path.join(rootPath, entry.name)
            elif entry.is_dir():
                yield from self.scanFiles(entry.path)
            else:
                log.error(f"Neither a file, nor a dir: {entry.path}")
                pass 

    def loadFiles(self):
        #breakpoint()
        start = time.perf_counter()
        log.info("scanning source files")
        self.fileList = []
        filesList = list(self.scanFiles(self.srcFilesPath))
        for f in filesList:
            #if not os.path.splitext(f)[1][1:] in DEFAULT_SUPPORTED_FILE_EXTENSIONS:
            #    continue
            try:
                with PIL.Image.open(f) as img:
                    #ignore small images
                    if img.width * img.height < DEFAULT_MIN_IMAGE_PIXELS:
                        img.close()
                        continue
                    # ignore unsupported formats
                    if not img.format in DEFAULT_SUPPORTED_IMAGE_FORMATS:
                        img.close()
                        continue
                    self.fileList.append(f)
                    img.close()            
            except PIL.UnidentifiedImageError as e:
                #log.error(f"Exception:", e)
                #TODO: process other file type, generate thumbnail preview
                pass
            except Exception as e:
                #log.error(f"Exception:", e)
                pass
        self.nFilesInList = len(self.fileList)
        self.loaded = True
        et = time.perf_counter()-start
        log.info(f"found {self.nFilesInList} recovered files in {et:.3f} seconds")

    def getFilePath(self):
        if len(self.fileList) == 0: 
            return ''
        return self.fileList[self.fileListIndex]
        
    def refresh(self):
        if len(self.fileList) == 0: 
            return
        pixmap = QPixmap(self.fileList[self.fileListIndex])
        filepath = self.fileList[self.fileListIndex]
        # send preview image to view
        self.signal.emit(pixmap, filepath)

    def next(self):
        if len(self.fileList) == 0: 
            return
        self.fileListIndex += 1
        if self.fileListIndex >= self.nFilesInList:
            self.fileListIndex = 0
        pixmap = QPixmap(self.fileList[self.fileListIndex])
        filepath = self.fileList[self.fileListIndex]
        # send new preview image to view
        self.signal.emit(pixmap, filepath)

    def prev(self):
        if len(self.fileList) == 0: 
            return
        self.fileListIndex -= 1
        if self.fileListIndex < 0:
            self.fileListIndex = self.nFilesInList - 1
        pixmap = QPixmap(self.fileList[self.fileListIndex])
        filepath = self.fileList[self.fileListIndex]
        # send preview image to view
        self.signal.emit(pixmap, filepath)

    def dumpFiles(self):
        filesList = list(self.scanFiles(self.srcFilesPath))
        log.info('dumpFiles:')
        log.info(f"    {len(filesList)} files")
        extList = sorted(self.scanExtensions(self.srcFilesPath))
        log.info('extensions:')
        log.info(f"    {extList}")

        log.info()
        log.info('examining recovered files')
        for f in filesList:
            try:
                with PIL.Image.open(f) as img:
                    if img.width < 1000 or img.height < 1000:
                        img.close()
                        continue
                    log.info("File: ",img.filename)
                    log.info("Format: ",img.format, end=' ')
                    log.info("Mode: ",img.mode, end=' ')
                    log.info("Size: ",img.size, end=' ')
                    log.info("Width: ",img.width, end=' ')
                    log.info("Height: ",img.height, end=' ')
                    log.info("Palette: ",img.palette, end=' ')
                    #log.info("Image Info : ",img.info, end=' ')
                    log.info()
                    img.close()            
            except Exception as e:
                log.error(f"Exception:", e)
                pass

