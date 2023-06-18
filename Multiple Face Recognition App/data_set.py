import sqlite3
import os
import threading

from PyQt5.QtCore import Qt, QThread, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtGui import QImage
import cv2


class Data(QThread):
    ImageUpdate = Signal(QImage, int, int)
    done = Signal(bool)

    @Slot(int, str, str)
    def run(self, user_no, user_name, browse_path):
        self.send_once = True
        self.ThreadActive = True
        self.training_limit = 500
        current_dir = os.getcwd()
        path = os.getcwd() + "\\dataset\\"
        isExist = os.path.exists(path)
        if not isExist:
            try:
                os.makedirs("dataset")
            except:
                pass
        else:
            pass
        os.chdir(current_dir)
        self.ff = None
        self.conn = sqlite3.connect("user.db", check_same_thread=False)
        self.c = self.conn.cursor()
        self.c.execute(
            """CREATE TABLE IF NOT EXISTS names ( 
                    name text
                    )"""
        )
        self.conn.commit()
        if browse_path == "None":
            self.cam = cv2.VideoCapture(0)
        else:
            try:
                self.cam = cv2.VideoCapture(browse_path)
            except:
                self.cam = cv2.VideoCapture(0)
        self.cam.set(3, 640)  # set video width
        self.cam.set(4, 480)  # set video height
        self.face_detector = cv2.CascadeClassifier(
            "haarcascade_frontalface_default.xml"
        )
        name = str(user_name)
        self.c.execute("SELECT * FROM names")
        x = self.c.fetchall()
        if user_no == -1:
            self.face_id = len(x) + 1
        else:
            self.face_id = int(user_no)
        if self.face_id > len(x):
            self.c.execute(f"INSERT INTO names VALUES (?)", (name,))
            self.conn.commit()
            self.conn.close()
        else:
            self.c.execute(
                f"UPDATE names set name = ? WHERE name = ?",
                ((name, x[self.face_id - 1][0])),
            )
            self.conn.commit()
            self.conn.close()
        self.count = 0
        self.take_vid()

    def save(self, gray, x, y, h, w):
        cv2.imwrite(
            "dataset/User." + str(self.face_id) + "." + str(self.count) + ".jpg",
            gray[y : y + h, x : x + w],
        )
        self.count += 1

    def take_vid(self):
        while self.ThreadActive:
            try:
                ret, img = self.cam.read()
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = self.face_detector.detectMultiScale(gray, 1.3, 5)
                for x, y, w, h in faces:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    if self.count < self.training_limit:
                        t1 = threading.Thread(
                            target=self.save,
                            args=(
                                gray,
                                x,
                                y,
                                h,
                                w,
                            ),
                        )
                        t1.start()
                ConvertToQtFormat = QImage(
                    img, img.shape[1], img.shape[0], QImage.Format_BGR888
                )
                ff = ConvertToQtFormat.scaled(416, 312, Qt.KeepAspectRatio)
                if self.count < self.training_limit:
                    self.ImageUpdate.emit(ff, int(self.count), int(self.training_limit))
                if self.count == self.training_limit:
                    self.done.emit(True)
                    self.cam.release()
                    break
                
                self.label_4.setText(self.count)
            except:
                pass
        self.done.emit(True)
        self.cam.release()
