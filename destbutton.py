from defaults import *
from config import *
import faulthandler; faulthandler.enable()
import os, shutil
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from filemgr import checkPathValid

# dest button params
DBTN_H = DEFAULT_DEST_BUTTON_HEIGHT
DBTN_W = DEFAULT_DEST_BUTTON_WIDTH
DBTN_ICON_H = 28 # icon height
DBTN_ICON_W = 28 # icon width
DBTN_FONT = 'Arial Narrow' # font
DBTN_FONT_SIZE = 18 # font point size


class DestButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.dstFilesPath = ''
        #self.setMaximumWidth(DBTN_W)
        #self.setMinimumHeight(DBTN_H)
        self.setFont(QFont(DBTN_FONT, DBTN_FONT_SIZE))
        self.setEnabled(False)
        self.clickEnabled = False
        self.dropEnabled = False
        self.normalStyle = 'QPushButton {Text-align:left; background-color: white}'
        self.highlightStyle = 'QPushButton {Text-align:left; background-color: lightgreen}'
        self.setStyleSheet(self.normalStyle)
        self.setText("Dest"+str(id(self)))
        self.clicked.connect(self.clickHandler)

    def enableClick(self, enable : bool) -> None:
        self.clickEnabled = enable
        pass

    def enableDrop(self, enable : bool) -> None:
        self.dropEnabled = enable
        self.setAcceptDrops(enable)
        pass

    def contextMenuEvent(self, event):
        #if not self.clickEnabled: 
        #    return
        self.parent.ignoreKeys(True) # block Escape, etc
        contextMenu = QMenu(self)
        action_newfolder = QAction("New folder", self, #shortcut=QKeySequence.Action1,
            statusTip="New folder", triggered=self.newfolder)
        action_rename = QAction("Rename folder", self, #shortcut=QKeySequence.Action2,
            statusTip="Rename folder", triggered=self.rename)
        if self.text() == '':
            contextMenu.addAction(action_newfolder)
        else:
            contextMenu.addAction(action_rename)
        contextMenu.exec_(self.mapToGlobal(event.pos()))
        self.parent.ignoreKeys(False)

    def newfolder(self):
        log.info(f"newfolder called")
        # dialog to get new folder name
        folderName, okPressed = QInputDialog.getText(self, "Create folder","Folder name:", QLineEdit.Normal, '')
        folderName = folderName.strip()
        if folderName == '':
            log.info("invalid name entered, not renamed")
            QMessageBox.critical(self, "Error", "Not a valid folder name!", QMessageBox.Ok)
            return
        d = os.path.sep
        dst = self.dstFilesPath + d + folderName
        if okPressed:
            if folderName == '' or not checkPathValid(dst):
                log.info("invalid name entered, not created")
                QMessageBox.critical(self, "Error", "Not a valid folder name!", QMessageBox.Ok)
                return
            if os.path.exists(dst):
                log.info(f"folder '{folderName}' already exists")
            else:
                os.mkdir(dst)
                self.setText(folderName)
                self.enableClick(True)
                self.enableDrop(True)

    def rename(self):
        log.info(f"rename called")
        # dialog to edit folder name
        oldName = self.text()
        newName, okPressed = QInputDialog.getText(self, "Rename folder","New name:", QLineEdit.Normal, oldName)
        newName = newName.strip()
        if newName == '':
            log.info("invalid name entered, not renamed")
            QMessageBox.critical(self, "Error", "Not a valid folder name!", QMessageBox.Ok)
            return
        d = os.path.sep
        src = self.dstFilesPath + d + self.text()
        dst = self.dstFilesPath + d + newName
        if okPressed:
            if not checkPathValid(dst):
                log.info("invalid name entered, not renamed")
                QMessageBox.critical(self, "Error", "Not a valid folder name!", QMessageBox.Ok)
                return
            self.fileOp(src, dst, Qt.NoModifier)
            self.setText(newName)

    def clickHandler(self):
        if not self.clickEnabled:
            return
        log.info(f"{self.text()} button clicked")
        src = self.parent.getCurrentFilePath()
        src = src.strip()
        if src == '':
            return
        # build dest file full path
        # dest path + our dir + src's base filename
        d = os.path.sep
        dst = self.dstFilesPath + d + self.text() + d + os.path.basename(src)
        self.fileOp(src,dst, QApplication.keyboardModifiers())

    def fileOp(self, src, dst, modifiers):
        text = self.text()
        log.info(f"{text}: src file:{src}")
        log.info(f"{text}: dst file:{dst}")
        if modifiers == Qt.NoModifier: # move file
            try:
                shutil.move(src, dst)
                log.info('file moved ok')
                self.parent.removeFileFromList(src)
            except Exception as e:
                log.info('error while moving file')
                QMessageBox.critical(self, "Error", "Failed to move or rename.", QMessageBox.Ok)
        elif modifiers == Qt.ControlModifier: # copy file
            try:
                shutil.copy2(src, dst, False)
                log.info('file copied ok')
            except Exception as e:
                log.info('error while copying file')
                QMessageBox.critical(self, "Error", "Failed to copy.", QMessageBox.Ok)
        elif modifiers == Qt.ShiftModifier:
            #log.info('Shift, no action')
            pass
        elif modifiers == (Qt.ControlModifier | Qt.ShiftModifier):
            #log.info('Control-Shift, no action')
            pass

    def setDestFilePath(self, str):
        self.dstFilesPath = str

    def dragEnterEvent(self, a0: QDragEnterEvent) -> None:
        if not self.dropEnabled: 
            a0.ignore()
            return
        if a0.mimeData().hasFormat('text/plain'):
            self.setStyleSheet(self.highlightStyle)
            a0.accept()
        else:
            a0.ignore()

    def dragLeaveEvent(self, a0: QDragLeaveEvent) -> None:
        self.setStyleSheet(self.normalStyle)
        a0.accept()

    def dropEvent(self, a0):
        if not self.dropEnabled: 
            a0.ignore()
            return
        """
        QMessageBox.information(self, 
            'Text dropped: ',
            e.mimeData().text(),
            QMessageBox.Ok)
        """
        src = a0.mimeData().text()
        # build dest file full path
        # dest path + our dir + src's base filename
        d = os.path.sep
        dst = self.dstFilesPath + d + self.text() + d + os.path.basename(src)
        self.fileOp(src,dst, QApplication.keyboardModifiers())
        self.setStyleSheet(self.normalStyle)
        a0.accept()

