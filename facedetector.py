import cv2
from cv2 import CascadeClassifier, imread
from PyQt5.QtGui import QImage
from numpy import integer

class FaceDetector():
    def __init__(self):
        super().__init__()
        self.faces = None
        self.fpath = None
        self.img = None

    def detect(self, fpath) -> integer:
        self.fpath = fpath
        # cv2.data.haarcascades is a shortcut to the data folder.
        #detector = CascadeClassifier(cv2.data.haarcascades + 'face_detector.xml')
        # load classifier
        detector = CascadeClassifier("facedetector.xml")
        # Read the input image
        self.img = imread(fpath)
        # convert to grayscale for detection
        gray = cv2.cvtColor(self.img, cv2.COLOR_BGR2GRAY)
        # detect faces
        # detectMultiScale takes 3 arguments — image, scaleFactor and minNeighbours. 
        # scaleFactor specifies how much the image size is reduced with each scale. 
        # minNeighbours specifies how many neighbors each candidate rectangle should 
        # have to retain it. 
        self.faces = detector.detectMultiScale(gray, 1.1, 4)
        # Draw rectangle around each face
        for (x, y, w, h) in self.faces: 
            cv2.rectangle(self.img, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return len(self.faces)
    
    def getAnnotatedImage(self):
        return QImage(self.img)

