import cv2
import numpy as np
from PIL import Image
import os


class Train:
    def train_initiate(self):
        current_dir = os.getcwd()
        path = os.getcwd() + "\\Trainer\\"
        isExist = os.path.exists(path)
        if not isExist:
            try:
                os.makedirs("Trainer")
            except:
                pass
        os.chdir(current_dir)
        path = "dataset"
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
        self.i = 0
        faces, ids = self.getImagesAndLabels(path)
        recognizer.train(faces, np.array(ids))
        recognizer.save("Trainer/trainer.yml")
        self.label_4.setText("{0} faces trained".format(len(np.unique(ids))))
        self.label_4.setStyleSheet(f"""background-color: mediumseagreen""")
        self.ready_to_train = False

    def getImagesAndLabels(self, path):
        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []

        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert("L")  # convert it to grayscale
            img_numpy = np.array(PIL_img, "uint8")
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = self.detector.detectMultiScale(img_numpy)
            for x, y, w, h in faces:
                faceSamples.append(img_numpy[y : y + h, x : x + w])
                ids.append(id)

            if self.i + 20 < len(imagePaths):
                self.i += 1
                self.label_4.setStyleSheet(
                    f"""background-color: qlineargradient(x1: 0, x2: {(float(self.i)*2)/(float(len(imagePaths)))}, stop: .5 mediumseagreen, stop: 0.500000001 cornflowerblue)"""
                )

        return faceSamples, ids


if __name__ == "__main__":
    d = Train()
