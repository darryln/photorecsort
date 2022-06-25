#!/usr/bin/python
""" Manage list of file paths, scanning, trees, etc """

import os, time
import PIL
import PIL.Image
import PIL.features
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObject, pyqtSignal
from defaults import *

log = logging.getLogger(__name__)

class FileMgrException(Exception):

    def __init__(self, fpath, msg):
        self.msg = msg
        self.fpath = fpath
        super(FileMgrException, self).__init__(self.msg)

    def __str__(self):
        return f'{self.msg}:{self.fpath}'

class FileMgrException_NotFound(FileMgrException):
    def __init__(self, fpath):
        super().__init__(fpath, "not found")

class FileMgrException_Filtered(FileMgrException):
    def __init__(self, fpath):
        super().__init__(fpath, "file filtered")

class FileMgrException_LoadFailed(FileMgrException):
    def __init__(self, fpath):
        super().__init__(fpath, "load failed")

class FileMgrException_ImageFormatUnidentified(FileMgrException):
    def __init__(self, fpath):
        super().__init__(fpath, "unidentified image format")

class FileMgrException_ImageFormatNotSupported(FileMgrException):
    def __init__(self, fpath):
        super().__init__(fpath, "image format not supported")

class FileMgrException_FileTypeNotSupported(FileMgrException):
    def __init__(self, fpath):
        super().__init__(fpath, "file type not supported")

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

    def getNumFilesInList(self) -> int:
        return len(self.fileList)

    def getCurrentFileIndex(self) -> int:
        return self.fileListIndex

    def getSourcePath(self):
        return self.srcFilesPath
        
    def setSourcePath(self, newPath):
        log.info("setSourcePath:%s", newPath)
        self.srcFilesPath = newPath

    def getDestPath(self):
        return self.dstFilesPath
        
    def getDestDirs(self):
        log.info("scanning dest dirs under %s", self.dstFilesPath)
        dirlist = []
        try:
            dirlist = next(os.walk(self.dstFilesPath))[1]
            log.info(f"found {len(dirlist)} dest dirs")
            dirlist.sort()
        except Exception:
            log.error("getDestDirs:", exc_info=True)
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
        try:
            for entry in os.scandir(rootPath):
                if entry.is_file():
                    yield os.path.join(rootPath, entry.name)
                elif entry.is_dir():
                    yield from self.scanFiles(entry.path)
                else:
                    log.error(f"Neither a file, nor a dir: {entry.path}")
                    pass 
        except Exception:
            log.error(f"scanFiles:", exc_info=True)

    def getFilePath(self):
        if len(self.fileList) == 0: 
            log.info("list is empty")
            return ''
        return self.fileList[self.fileListIndex]
        
    def refresh(self):
        if len(self.fileList) == 0: 
            log.info("list is empty")
            return
        pixmap = QPixmap(self.fileList[self.fileListIndex])
        filepath = self.fileList[self.fileListIndex]
        # send preview image to view
        self.signal.emit(pixmap, filepath)

    def next(self):
        if len(self.fileList) == 0: 
            log.info("list is empty")
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
            log.info("list is empty")
            return
        self.fileListIndex -= 1
        if self.fileListIndex < 0:
            self.fileListIndex = self.nFilesInList - 1
        pixmap = QPixmap(self.fileList[self.fileListIndex])
        filepath = self.fileList[self.fileListIndex]
        # send preview image to view
        self.signal.emit(pixmap, filepath)

    def removeFileFromList(self, filepath):
        if len(self.fileList) == 0: 
            log.info("list is empty")
            return
        if not filepath in self.fileList:
            log.info("path not found in list")
            return
        #save current index & path
        curIndex = self.fileListIndex
        curPath = self.fileList[curIndex]
        #get target index
        tgtIndex = self.fileList.index(filepath)
        self.fileList.remove(filepath)
        # update list length
        self.nFilesInList = len(self.fileList)
        if (tgtIndex == curIndex):
            # we deleted the displayed item
            # set index to prev
            # and update the view
            self.fileListIndex -= 1
            if self.fileListIndex < 0:
                self.fileListIndex = self.nFilesInList - 1
            pixmap = QPixmap(self.fileList[self.fileListIndex])
            filepath = self.fileList[self.fileListIndex]
            # send preview image to view
            self.signal.emit(pixmap, filepath)
        else:
            # set index of the current item
            self.fileListIndex = self.fileList.index(curPath)


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
            except Exception:
                log.error(f"dumpFiles:", exc_info=True)
                pass

    def rotateFile(self):
        if len(self.fileList) == 0:
            return
        filepath = self.fileList[self.fileListIndex]
        try:
            img = PIL.Image.open(filepath)
            img_90 = img.transpose(PIL.Image.ROTATE_90)
            img_90.save(filepath)
            pixmap = QPixmap(self.fileList[self.fileListIndex])
            # update view
            self.signal.emit(pixmap, filepath)
        except Exception:
            log.error(f"rotateFile:", exc_info=True)
            pass

    def loadImageFile(self, fpath: str):
        try:
            if not os.path.exists(fpath):
                raise FileMgrException_NotFound
            basename = os.path.basename(fpath)
            ext = os.path.splitext(fpath)[1][1:]
            filtered = False
            reason = None
            desc = ''
            with PIL.Image.open(fpath) as img:
                width = img.width
                height = img.height
                fmt = img.format
                if width * height < DEFAULT_MIN_IMAGE_PIXELS:
                    filtered = True
                    reason = 'resolution'
                mode = img.mode
                found = [item for item in DEFAULT_SUPPORTED_IMAGE_FORMATS if item[0] == fmt]
                if len(found):
                    desc = found[0][1]                
                    if found[0][2]:
                        filtered = True
                        reason = 'format'
                log.info("loadImageFile:'%s' '%s' %s %s %d x %d %s" % \
                    (basename, ext, fmt, mode, width, height, "Filtered" if filtered else "" ))
                if filtered:
                    raise FileMgrException_Filtered(fpath)
        except PIL.UnidentifiedImageError:
            raise FileMgrException_ImageFormatUnidentified(fpath)
        finally:
            pass

    def loadFiles(self):
        #breakpoint()
        # TODO: estimate time to scan and show progress dialog
        start = time.perf_counter()
        log.info("scanning source files")
        self.fileList = []
        scannedFilesList = list(self.scanFiles(self.srcFilesPath))
        if len(scannedFilesList) == 0:
            log.info("no files found during scan")
            return
        for f in scannedFilesList:
            try:
                self.loadImageFile(f)
                self.fileList.append(f)
            except FileMgrException_NotFound:
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
        self.nFilesInList = len(self.fileList)
        self.loaded = True
        et = time.perf_counter()-start
        log.info(f"found {self.nFilesInList} recovered files in {et:.3f} seconds")



def checkPathCreatable(pathname: str) -> bool:
    dirname = os.path.dirname(pathname) or os.getcwd()
    return os.access(dirname, os.W_OK)

def checkPathValid(pathname: str) -> bool:
    try:
        return checkPathCreatable(pathname) and (
            os.path.exists(pathname) or checkPathCreatable(pathname))
    except OSError:
        return False


