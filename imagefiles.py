from defaults import *
import PIL
import PIL.features
import os, time
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObject, pyqtSignal

log = logging.getLogger(__name__)

class ImageFiles(QObject):
    # signal to send new image
    signal = pyqtSignal(QPixmap, str)

    def __init__(self, name=None):
        super().__init__()
        self.loaded = False
        self.initComplete = False
        self.srcFilesPath = DEFAULT_SRC_FILES_PATH
        self.dstFilesPath = DEFAULT_DST_FILES_PATH
        self.files = []
        self.imageIndex = 0
        self.nImages = len(self.files)
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
        log.info("scanning dest dirs under {self.dstFilesPath}")
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
        self.files = []
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
                    self.files.append(f)
                    img.close()            
            except PIL.UnidentifiedImageError as e:
                #log.error(f"Exception:", e)
                pass
            except Exception as e:
                #log.error(f"Exception:", e)
                pass
        self.nImages = len(self.files)
        self.loaded = True
        et = time.perf_counter()-start
        log.info(f"found {self.nImages} files in {et:.3f} seconds")

    def getFilePath(self):
        if len(self.files) == 0: 
            return ''
        return self.files[self.imageIndex]
        
    def refresh(self):
        if len(self.files) == 0: 
            return
        pixmap = QPixmap(self.files[self.imageIndex])
        filepath = self.files[self.imageIndex]
        # resend image to gui
        self.signal.emit(pixmap, filepath)

    def next(self):
        if len(self.files) == 0: 
            return
        self.imageIndex += 1
        if self.imageIndex >= self.nImages:
            self.imageIndex = 0
        pixmap = QPixmap(self.files[self.imageIndex])
        filepath = self.files[self.imageIndex]
        # send new image to gui
        self.signal.emit(pixmap, filepath)

    def prev(self):
        if len(self.files) == 0: 
            return
        self.imageIndex -= 1
        if self.imageIndex < 0:
            self.imageIndex = self.nImages - 1
        pixmap = QPixmap(self.files[self.imageIndex])
        filepath = self.files[self.imageIndex]
        # send new image to gui
        self.signal.emit(pixmap, filepath)

    def dumpFiles(self):
        filesList = list(self.scanFiles(self.srcFilesPath))
        log.info('dumpFiles:')
        log.info(f"    {len(filesList)} files")
        extList = sorted(self.scanExtensions(self.srcFilesPath))
        log.info('extensions:')
        log.info(f"    {extList}")

        log.info()
        log.info('examining image files')
        for f in filesList:
            try:
                with PIL.Image.open(f) as img:
                    if img.width < 1000 or img.height < 1000:
                        img.close()
                        continue
                    # Getting the filename of image
                    log.info("File: ",img.filename)
                    # Getting the format of image
                    log.info("Format: ",img.format, end=' ')
                    # Getting the mode of image
                    log.info("Mode: ",img.mode, end=' ')
                    # Getting the size of image
                    log.info("Size: ",img.size, end=' ')
                    # Getting only the width of image
                    log.info("Width: ",img.width, end=' ')
                    # Getting only the height of image
                    log.info("Height: ",img.height, end=' ')
                    # Getting the color palette of image
                    log.info("Palette: ",img.palette, end=' ')
                    # Getting the info about image
                    #log.info("Image Info : ",img.info, end=' ')
                    log.info()
                    # Closing Image object
                    img.close()            
            except Exception as e:
                log.error(f"Exception:", e)
                pass

