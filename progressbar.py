from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QPropertyAnimation, QAbstractAnimation, QEasingCurve

# https://www.bogotobogo.com/Qt/Qt5_QProgressDialog_Modal_Modeless_QTimer.php


class AnimatedProgressBar(QProgressBar):
    def __init__(self, title=None, ):
        super().__init__()
        self.title=title
        self.__initUi()

    def __initUi(self):
        self.setValue(0)
        self.setTextVisible(False)
        self.__animation = QPropertyAnimation(self, b'loading')
        self.__animation.setStartValue(self.minimum())
        self.__animation.setEndValue(self.maximum())
        self.__animation.valueChanged.connect(self.__loading)
        self.__animation.setDuration(1000)
        self.__animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.__animation.start()

    def __loading(self, v):
        self.setValue(v)
        if self.__animation.currentValue() == self.__animation.endValue():
            self.__animation.setDirection(QAbstractAnimation.Backward)
            self.setInvertedAppearance(True)
            self.__animation.start()
        elif self.__animation.currentValue() == self.__animation.startValue():
            self.__animation.setDirection(QAbstractAnimation.Forward)
            self.setInvertedAppearance(False)
            self.__animation.start()

    def setAnimationType(self, type: str):
        if type == 'fade':
            self.setStyleSheet('''
                QProgressBar::chunk {
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop: 0.5 #CCCCCC, stop: 0.6 #CCCCCC, stop:1 transparent);
                }
            ''')
            self.__animation.setEasingCurve(QEasingCurve.Linear)
            self.__animation.setDuration(500)
        elif type == 'dynamic':
            self.setStyleSheet('')
            self.__animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.__animation.setDuration(1000)


"""
# example usage

from progressbar import AnimatedProgressBar

class DlgWindow(QDialogWindow):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        bar = ProgressBar("Scanning, please wait...")
        bar.setAnimationType('fade') # set animation type to fade
        lay = QVBoxLayout()
        lay.addWidget(QLabel('Loading...'))
        lay.addWidget(bar)
        mainWidget = QWidget()
        mainWidget.setLayout(lay)
        self.setCentralWidget(mainWidget)
"""