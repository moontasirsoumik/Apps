import sys
import os
import shutil
import threading

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal as Signal
from PyQt5.QtGui import QPixmap

from ui import Ui_MainWindow
from data_set import Data
from trainer import Train
from recognize import Recognition


class MainApp(QMainWindow, Ui_MainWindow, Train):
    work_requested = Signal(int, str, str)
    work_requested2 = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.stackedWidget_2.setCurrentIndex(1)
        self.stackedWidget.setCurrentIndex(0)
        self.setFixedSize(self.size())

        self.browse_path = "None"
        self.first = True
        self.viewer_running = False
        self.file_browse_active = False

        self.data_exists = False
        self.ready_to_train = False
        self.check_user()

        self.collect_data = None
        self.pushButton_data.clicked.connect(lambda: self.video())
        self.pushButton_train.clicked.connect(lambda: self.start_train())
        self.pushButton_view.clicked.connect(lambda: self.viewer())
        self.pushButton_next.clicked.connect(lambda: self.next())
        self.pushButton_clear.clicked.connect(lambda: self.delete_file())
        self.pushButton_help.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(1)
        )
        self.pushButton_back.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0)
        )
        self.pushButton_browse.clicked.connect(lambda: self.file_browse())

    def file_browse(self):
        if not self.file_browse_active:
            filename = QFileDialog.getOpenFileName()
            self.browse_path = filename[0]
            if self.browse_path == "None" or self.browse_path == "":
                self.browse_path == "None"
            else:
                self.file_browse_active = True
                self.pushButton_browse.setText("Camera")
        else:
            self.browse_path = "None"
            self.file_browse_active = False
            self.pushButton_browse.setText("Browse")

    def check_user(self):
        try:
            if self.worker_thread2.isRunning():
                self.viewer()
        except:
            pass
        try:
            if self.worker_thread.isRunning():
                # self.worker_thread.quit()
                self.worker_1_stopper()
        except: 
            pass

        path = os.getcwd() + "\\dataset\\"
        isExist = os.path.exists(path)
        if isExist:
            self.data_exists = True
            self.pushButton_clear.setEnabled(True)
            self.pushButton_clear.setStyleSheet(
                "QPushButton{border: 1px solid white; padding-bottom: 2px; background:#e8464e;}\n"
                "\n"
                "QPushButton::hover{border: 1px solid black; background: white; color: black; padding-bottom: 2px;}\n"
                "\n"
                "QPushButton::pressed{border: 1px solid white; background: slategray; color: white; padding-bottom: 2px;}"
            )

        else:
            self.data_exists = False
            self.pushButton_clear.setEnabled(False)
            self.pushButton_clear.setStyleSheet(
                "QPushButton{border: 1px solid white; padding-bottom: 2px; background: slategray;}\n"
            )

    def delete_file(self):
        current_dir = os.getcwd()
        path = os.getcwd() + "\\dataset\\"
        isExist = os.path.exists(path)
        if isExist:
            try:
                shutil.rmtree(path, ignore_errors=True)
            except:
                pass
        else:
            pass
        os.chdir(current_dir)
        try:
            os.remove("user.db")
        except:
            pass
        current_dir = os.getcwd()
        path = os.getcwd() + "\\Trainer\\"
        isExist = os.path.exists(path)
        if isExist:
            try:
                shutil.rmtree(path, ignore_errors=True)
            except:
                pass
        os.chdir(current_dir)
        self.label_4.setText("Data Cleared")
        self.label_4.setStyleSheet(f"""background-color: #e8464e""")
        self.check_user()

    def next(self):
        self.stackedWidget_2.setCurrentIndex(0)
        self.setFixedSize(self.size())

    def start_train(self):
        self.ready_to_train = True
        print(self.ready_to_train)
        if self.data_exists:
            if self.ready_to_train == True:
                if not self.viewer_running:
                    self.label_4.setText("Training Images. Please Wait")
                    self.label_4.setStyleSheet(f"""background-color: cornflowerblue""")
                    t2 = threading.Thread(target=self.train_initiate)
                    t2.start()
                    self.label_4.setText("Training")
                    self.label_4.setStyleSheet(f"""background-color: cornflowerblue""")
                else:
                    self.label_4.setText("Feed Still Running")
            else:
                self.label_4.setText("No New Face To Train")
                self.label_4.setStyleSheet(f"""background-color: #e8464e""")
        else:
            self.label_4.setText("No Facial Data Found")
            self.label_4.setStyleSheet(f"""background-color: #e8464e""")

    def viewer(self):
        if self.data_exists:
            if not self.viewer_running:
                try:
                    if self.worker_thread2.isRunning():
                        self.worker_2_stopper()
                        if self.worker_thread2.isRunning():
                            self.label_4.setText("Error! Thread Still Running")
                            self.label_4.setStyleSheet(f"""background-color: #e8464e""")
                    else:
                        self.view_initiate()
                except:
                    try:
                        self.view_initiate()
                    except:
                        self.label_4.setText("Could Not Start Video")
                        self.label_4.setStyleSheet(f"""background-color: #e8464e""")
            else:
                self.worker_2_stopper()
                self.pushButton_view.setText("Start")
        else:
            self.label_4.setText("No Facial Data Found")
            self.label_4.setStyleSheet(f"""background-color: #e8464e""")

    def view_initiate(self):
        self.pushButton_view.setText("Stop")
        self.viewer_running = True
        self.collect_data = False
        self.frame_right.show()
        self.frame_2.show()
        self.label_4.setText("Initializing. Please Wait")
        self.label_4.setStyleSheet(f"""background-color: cornflowerblue""")

        self.Worker2 = Recognition()
        self.worker_thread2 = QThread()
        self.Worker2.completed.connect(self.completed)
        self.work_requested2.connect(self.Worker2.run)
        self.Worker2.moveToThread(self.worker_thread2)
        self.worker_thread2.start()
        self.Worker2.ImageUpdate.connect(self.ImageUpdateSlot)
        self.work_requested2.emit(self.browse_path)

    def worker_2_stopper(self):
        try:
            self.Worker2.stop()
            self.label_video.clear()
        except:
            pass
        try:
            if not self.worker_thread2.isFinished():
                self.worker_thread2.exit()
            if self.worker_thread2.isRunning():
                self.worker_thread2.quit()
        except:
            pass
        self.viewer_running = False
        
        
    def worker_1_stopper(self):
        try:
            self.Worker.stop()
            self.label_video.clear()
        except:
            pass
        try:
            if not self.worker_thread.isFinished():
                self.worker_thread.exit()
            if self.worker_thread.isRunning():
                self.worker_thread.quit()
        except:
            pass
        self.viewer_running = False

    def video(self):
        if not self.viewer_running:
            if self.lineEdit_name.text() != "":
                self.lineEdit_name.setStyleSheet("color: black; padding-left: 3px;")
                self.collect_data = True

                user_no = self.lineEdit_user.text()
                if self.lineEdit_user.text() != "":
                    try:
                        user_no = int(user_no)
                    except:
                        self.label_4.setText("Invalid User ID")
                        self.label_4.setStyleSheet(f"""background-color: #e8464e""")

                if isinstance(user_no, int) or self.lineEdit_user.text() == "":
                    if self.lineEdit_user.text() == "":
                        user_no = -1
                    user_name = self.lineEdit_name.text()
                    self.label_4.setText("Initializing. Please Wait")
                    self.label_4.setStyleSheet(f"""background-color: cornflowerblue""")
                    self.frame_2.show()
                    self.Worker1 = Data()
                    self.worker_thread = QThread()
                    self.Worker1.done.connect(self.done)
                    self.work_requested.connect(self.Worker1.run)
                    self.Worker1.moveToThread(self.worker_thread)
                    self.worker_thread.start()
                    self.Worker1.ImageUpdate.connect(self.ImageUpdateSlot)
                    self.work_requested.emit(int(user_no), user_name, self.browse_path)
            else:
                self.lineEdit_name.setStyleSheet(
                    "color: black; padding-left: 3px; border: 2px solid tomato;"
                )
        else:
            self.label_4.setText("Feed Still Running")
            self.label_4.setStyleSheet(f"""background-color: #e8464e""")

    def ImageUpdateSlot(self, Image, img_count=None, train_lim=None):
        self.frame_2.show()
        self.label_video.clear()
        if self.first == True:
            self.first = False
            if self.collect_data == True:
                self.label_4.setText("Collecting Facial Data")
                self.label_4.setStyleSheet(f"""background-color: cornflowerblue""")
                self.progress = True
            elif self.collect_data == False:
                self.label_4.setText("Facial Recognition Activated")
                self.label_4.setStyleSheet(f"""background-color: cornflowerblue""")
                self.progress = False
                
        self.label_video.setPixmap(QPixmap.fromImage(Image))
        if self.progress == True: 
            self.label_4.setStyleSheet(
                    f"""background-color: qlineargradient(x1: 0, x2: {float(img_count)/(float(train_lim)/2)}, stop: .5 mediumseagreen, stop: 0.500000001 cornflowerblue)"""
                )

    def done(self):
        self.frame_2.show()
        self.label_4.setText("Data Collection Complete")
        self.label_4.setStyleSheet(f"""background-color: mediumseagreen""")
        self.ready_to_train = True
        self.check_user()
        self.lineEdit_name.clear()
        self.lineEdit_user.clear()
        self.label_video.clear()
        if not self.worker_thread.isFinished():
            self.worker_thread.quit()
        self.first = True

    def completed(self):
        self.frame_2.show()
        self.label_video.clear()
        self.first = True
        self.label_4.setText("Feed Ended")
        self.label_4.setStyleSheet(f"""background-color: mediumseagreen""")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainApp()
    form.show()
    sys.exit(app.exec_())
