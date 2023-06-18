import cv2
import sqlite3

from PyQt5.QtCore import Qt, QThread, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtGui import QImage
import cv2


class Recognition(QThread):
    ImageUpdate = Signal(QImage)
    completed = Signal(bool)

    @Slot(str)
    def run(self, browse_path):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.thread_active = True
        self.recognizer.read("Trainer/trainer.yml")
        self.faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.font = cv2.FONT_HERSHEY_DUPLEX
        self.id = 0
        self.names = ["None"]
        conn = sqlite3.connect("user.db", check_same_thread=False)
        c = conn.cursor()
        c.execute("SELECT * FROM names")
        x = c.fetchall()

        for i in range(len(x)):
            self.names.append(x[i][0])
        if browse_path == "None":
            self.cam = cv2.VideoCapture(0)
        else:
            try:
                self.cam = cv2.VideoCapture(browse_path)
            except:
                self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 640)  # set video width
        self.cam.set(4, 480)  # set video height
        self.minW = 0.1 * self.cam.get(3)
        self.minH = 0.1 * self.cam.get(4)
        self.camera()

    def camera(self):
        while self.thread_active:
            try:
                _, img = self.cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.faceCascade.detectMultiScale(
                    gray,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(int(self.minW), int(self.minH)),
                )
                for x, y, w, h in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    serial, confidence = self.recognizer.predict(
                        gray[y : y + h, x : x + w]
                    )
                    int_confidence = confidence
                    if confidence < 100:
                        try:
                            self.id = self.names[serial]
                            confidence = "  {0}%".format(round(100 - confidence))
                        except:
                            pass
                    else:
                        self.id = "unknown"
                        confidence = " "

                    if 100 - int_confidence < 30:
                        self.id = "unknown"
                        confidence = " "

                    cv2.putText(
                        img,
                        str(self.id),
                        (x + 5, y - 5),
                        self.font,
                        1,
                        (0, 0, 0),
                        6,
                        cv2.LINE_AA,
                    )
                    cv2.putText(
                        img,
                        str(self.id),
                        (x + 5, y - 5),
                        self.font,
                        1,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

                    cv2.putText(
                        img,
                        str(confidence),
                        (x + 5, y + h + 25),
                        self.font,
                        0.75,
                        (255, 255, 255),
                        6,
                        cv2.LINE_AA,
                    )
                    cv2.putText(
                        img,
                        str(confidence),
                        (x + 5, y + h + 25),
                        self.font,
                        0.75,
                        (0, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )
                ConvertToQtFormat = QImage(
                    img, img.shape[1], img.shape[0], QImage.Format_BGR888
                )
                ff = ConvertToQtFormat.scaled(416, 312, Qt.KeepAspectRatio)

                self.ImageUpdate.emit(ff)
            except:
                pass
        self.thread_active = False
        self.completed.emit(True)
        self.cam.release()

    def stop(self):
        self.thread_active = False
        self.completed.emit(True)
        self.cam.release()
