#!/usr/bin/python
""" Manage list of file paths """

import os, time
from PyQt5.QtCore import QObject, pyqtSignal
import PIL.Image
from defaults import *

log = logging.getLogger(__name__)

 
class FileMgr(QObject):
    # signal to send list of file paths
    signal = pyqtSignal(list)

    def __init__(self, name=None):
        super().__init__()
        self.loaded = False
        self.initComplete = False
        self.srcFilesPath = DEFAULT_SRC_FILES_PATH
        self.dstFilesPath = DEFAULT_DST_FILES_PATH
        self.fileList = []
        self.fileListIndex = 0
        self.nFilesInList = len(self.fileList)
        self.stride = 1
        #log.info("pilinfo:")
        #PIL.features.pilinfo(out=None, supported_formats=False)
        #PIL.features.get_supported()

    def isLoaded(self): 
        return self.loaded

    def setStride(self, stride:int):
        self.stride = stride

    def getStride(self):
        return self.stride

    def getNumFilesInList(self) -> int:
        return len(self.fileList)

    def getCurrentFileIndex(self) -> int:
        return self.fileListIndex

    def getFilesList(self) -> list:
        return self.fileList

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
        
    def getPathListSlice(self, list, index, stride):
        # build list of paths to be emitted
        if self.fileListIndex+self.stride < len(self.fileList):
            # no wrap required
            firstPart = self.fileList[self.fileListIndex : self.fileListIndex+self.stride]
            nextPart = []
        else:
            # wrap required
            firstPart = self.fileList[self.fileListIndex : ]
            nextPart = self.fileList[0 : self.stride - len(firstPart)]
        pathList = firstPart + nextPart
        return pathList

    def refresh(self):
        if len(self.fileList) == 0: 
            log.info("list is empty")
            return
        pathList = self.getPathListSlice(self.fileList, self.fileListIndex, self.stride)
        # send path list slice to view
        self.signal.emit(pathList)

    def next(self):
        if len(self.fileList) == 0: 
            log.info("list is empty")
            return
        if self.fileListIndex + self.stride < len(self.fileList):
            # no wrap
            self.fileListIndex += self.stride
        else:
            # wrap
            self.fileListIndex = self.fileListIndex + self.stride - len(self.fileList)
        pathList = self.getPathListSlice(self.fileList, self.fileListIndex, self.stride)
        # send path list slice to view
        self.signal.emit(pathList)

    def prev(self):
        if len(self.fileList) == 0: 
            log.info("list is empty")
            return
        if self.fileListIndex - self.stride >= 0:
            # no wrap
            self.fileListIndex -= self.stride
        else:
            # wrap
            self.fileListIndex = self.fileListIndex - self.stride + len(self.fileList)
        pathList = self.getPathListSlice(self.fileList, self.fileListIndex, self.stride)
        # send path list to view
        self.signal.emit(pathList)

    def removeFileFromList(self, pathList : list):
        for path in pathList:
            self.removeFileFromList(path)

    def removeFileFromList(self, filepath):
        if len(self.fileList) == 0: 
            log.info("list is empty")
            return
        if not filepath in self.fileList:
            log.info("path not found in list")
            return
        # save current index & path
        curIndex = self.fileListIndex
        curPath = self.fileList[curIndex]
        # get index of item to delete
        tgtIndex = self.fileList.index(filepath)
        # remove item from list
        self.fileList.remove(filepath)
        # update list length
        self.nFilesInList = len(self.fileList)
        if self.nFilesInList == 0:
            QApplication.instance().statusbar.showMessage("No files.")
            self.fileListIndex = -1
        else:
            # update list index
            # TODO: adjust index based on last user nav direction.
            # for now, just decrement the index and wrap
            if (tgtIndex == curIndex):
                # deleted item @ curr index, decrement/wrap index 
                self.fileListIndex -= 1
                if self.fileListIndex < 0:
                    self.fileListIndex = self.nFilesInList - 1
            else:
                # get index of the current item
                self.fileListIndex = self.fileList.index(curPath)
        # update the view with new path list
        # TODO: skip refresh if item was not currently displayed
        self.refresh()


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

    def rotateFile(self, filePath):
        if len(self.fileList) == 0:
            return
        try:
            img = PIL.Image.open(filePath)
            img_90 = img.transpose(PIL.Image.ROTATE_90)
            img_90.save(filePath)
            # update view
            self.refresh()
        except Exception:
            log.error(f"rotateFile:", exc_info=True)
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
        self.fileList = scannedFilesList
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


