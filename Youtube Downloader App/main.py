import sys
import os
import sqlite3

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QHBoxLayout,
    QLabel,
    QDesktopWidget,
)
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtCore import Qt, QThread, QPoint, pyqtSignal as Signal

from ui import Ui_MainWindow
from add_music import MusicAdd, MusicCheck
from cards import Cards
from controls import QControl
from player import Player
from timer import Timer

from qframelesswindow import FramelessWindow, AcrylicWindow, FramelessDialog


class MainApp(
    QMainWindow, Ui_MainWindow, AcrylicWindow, FramelessWindow, Cards, QControl, Player
):
    work_requested = Signal(str)
    work_requested2 = Signal(str, list)
    work_requested3 = Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi(self)

        self.icon_path = os.getcwd()
        self.icon_path = self.icon_path.replace("\\", "/")
        self.style_sheet()
        # Window effect application for clear background
        self.titleBar.hide()
        self.windowEffect.setAcrylicEffect(self.winId(), "BBBBBB60")

        self.initiate()
        self.db_initiate()
        self.hider()
        self.center()

        # Initiate thread
        self.worker = MusicAdd()
        self.worker_thread = QThread()
        self.worker.completed.connect(self.complete)
        self.work_requested.connect(self.worker.add)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        # Initiate thread 2
        self.worker2 = MusicCheck()
        self.worker_thread2 = QThread()
        self.worker2.done.connect(self.done)
        self.work_requested2.connect(self.worker2.check)
        self.worker2.moveToThread(self.worker_thread2)
        self.worker_thread2.start()

        # Initiate thread 3
        self.worker3 = Timer()
        self.worker_thread3 = QThread()
        self.worker3.time_up.connect(self.time_up)
        self.work_requested3.connect(self.worker3.time_count)
        self.worker3.moveToThread(self.worker_thread3)
        self.worker_thread3.start()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # A function to initiate everything
    def initiate(self):
        # Variables
        self.card_counter = 0
        self.name = 1
        self.title = []
        self.artist = []
        self.duration = []
        self.expand = False
        self.expansion = 0
        self.playing = False
        self.c_playing = 0
        self.first_time = True
        self.mouse_release_flag = True
        self.hover_flag = False

        # Buttons
        self.close_pushButton.clicked.connect(lambda: self.close())
        self.show_pushButton.clicked.connect(lambda: self.shower())
        self.add_show_pushButton.clicked.connect(lambda: self.shower(self.expansion))
        self.play_pushButton.clicked.connect(lambda: self.play())
        self.next_pushButton.clicked.connect(
            lambda: self.play(self.c_playing + 1, -1, -1, -1)
        )
        self.prev_pushButton.clicked.connect(
            lambda: self.play(self.c_playing - 1, -2, -2, -2)
        )

        self.add_pushButton.clicked.connect(lambda: self.add_music())

        # Create directory if does not exist
        currant_dir = os.getcwd()
        path = os.getcwd() + "\\Downloads\\"
        isExist = os.path.exists(path)

        if not isExist:
            os.makedirs("Downloads")

        os.chdir(currant_dir)

        # Initiate database
        self.conn = sqlite3.connect("music.db", check_same_thread=False)
        self.c = self.conn.cursor()

        # Initiating music player
        self.player = QMediaPlayer()

        # Initiating smooth scrolling
        self.scrollArea.verticalScrollBar().setSingleStep(5)

        # Initiate mouse hovering
        self.top_frame.enterEvent = lambda event: self.mouse_hover(True)
        self.top_frame.leaveEvent = lambda event: self.mouse_hover(False)

        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.centralwidget.setStyleSheet(
            """
                QFrame{
                        color: white;
                }
                QPushButton{
                        color: white;
                }
                QLabel{
                        color: white;
                }
                QScrollBar:vertical {
                        background: rgba(0, 0, 0, 50);
                        width: 4px;
                        margin: 0;
                }
                QScrollBar::handle:vertical {
                        background:  rgba(0, 0, 0, 100); 
                        border-radius: 10px;
                }
                QScrollBar::handle::hover {
                        background:  rgba(0, 0, 0, 140); 
                        border-radius: 10px; 
                        width: 8px; 
                }
                QScrollBar::add-line:vertical {
                        height: 0px;
                }
                QScrollBar::sub-line:vertical {
                        height: 0px;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                        background: rgba(255, 255, 255, 50); 
                }"""
        )

    def db_initiate(self):
        if self.first_time == True:
            self.first_time = False
        else:
            try:
                self.conn.close()
            except:
                pass
            currant_dir = os.getcwd()
            self.conn = sqlite3.connect("music.db", check_same_thread=False)
            self.c = self.conn.cursor()
        # Check if table exists
        table = self.c.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
                        AND name='playlist'; """
        ).fetchall()

        # Create table if it does not exist
        if table == []:
            self.c.execute(
                """CREATE TABLE playlist ( 
                    name int, 
                    title text, 
                    duration text, 
                    artist text, 
                    second_name text
                    )"""
            )
            self.conn.commit()

        else:
            self.c.execute("SELECT * FROM playlist")
            x = self.c.fetchall()
            self.conn.commit()

            if len(x) != 0:
                self.name = len(x) + 1

            self.card_counter = 0

            self.title = []
            self.artist = []
            self.duration = []

            for i in range(len(x)):
                if x[i][1] not in self.title:
                    self.title.append(x[i][1])
                    self.artist.append(x[i][3])
                    self.duration.append(x[i][2])

                self.create_cards(self.title[i], self.artist[i], self.duration[i])

    def frame_styleSheet(self, color):
        if color == "green":
            self.notification_frame.setStyleSheet(
                "background: seagreen; \n" "border-radius: 4px; \n" ""
            )
        elif color == "blue":
            self.notification_frame.setStyleSheet(
                "background: teal; \n" "border-radius: 4px; \n" ""
            )
        elif color == "red":
            self.notification_frame.setStyleSheet(
                "background: tomato; \n" "border-radius: 4px; \n" ""
            )

    def add_music(self):
        self.frame_2.hide()
        self.frame_styleSheet("blue")
        self.notification_frame.show()
        self.notification_label.setText("Processing...")

        self.reply = 1
        self.expansion = 0

        self.return_val = None

        self.work_requested2.emit(self.link_lineEdit.text(), self.title)

    def done(self, reply):
        if reply == True:
            self.work_requested.emit(self.link_lineEdit.text())
            self.notification_label.setText("Downloading...")
        else:
            print("Already exists")

    def complete(self, reply):
        if reply == True:
            self.link_lineEdit.clear()
            self.name += 1
            self.card_clear()
            self.db_initiate()

            self.frame_styleSheet("green")
            self.notification_frame.show()
            self.notification_label.setText("Download Completed")
            self.work_requested3.emit()

        else:
            self.frame_styleSheet("red")
            self.notification_frame.show()
            self.notification_label.setText("Download Failed")
            self.work_requested3.emit()

    def time_up(self, reply):
        if reply == True:
            self.notification_frame.hide()

    def hider(self):
        self.frame_2.hide()
        self.bottom_frame_left_middle.hide()
        self.duration_progressBar.hide()
        self.artist_label.hide()
        self.bottom_frame_right_bottom.hide()
        self.bottom_frame.hide()
        self.duration_progress_frame.hide()

        self.notification_frame.hide()

    def shower(self, expansion=-1):
        if expansion == -1:
            if self.expand == False:
                self.bottom_frame_left_middle.show()
                self.artist_label.show()
                self.bottom_frame_right_bottom.show()
                self.artist_label.show()
                self.expand = True
                self.show_pushButton.setStyleSheet(
                    f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/down.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
                )
            else:
                self.bottom_frame_left_middle.hide()
                self.duration_progressBar.hide()
                self.artist_label.hide()
                self.bottom_frame_right_bottom.hide()
                self.artist_label.hide()
                self.expand = False
                self.show_pushButton.setStyleSheet(
                    f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/up.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
                )

        elif expansion == 0:
            self.frame_2.show()
            self.expansion = 1

        elif expansion == 1:
            self.frame_2.hide()
            self.expansion = 0

    def mouse_hover(self, flag):
        self.hover_flag = flag

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.hover_flag == True:
            self.oldPosition = event.globalPos()
            self.mouse_release_flag = False

    def mouseMoveEvent(self, event):
        if self.mouse_release_flag == False and self.hover_flag == True:
            delta = QPoint(event.globalPos() - self.oldPosition)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouse_release_flag = True

    def style_sheet(self):
        self.link_lineEdit.setPlaceholderText("Put youtube link here")
        # Putting icons on each button
        self.add_show_pushButton.setStyleSheet(
            f"""QPushButton{{background: seagreen; 
                                                border-radius: 4px;
                                                image: url('{self.icon_path}/icons/add.png'); 
                                            padding: 6px 6px 6px 6px;}}
                                                QPushButton::hover{{
                                                background: mediumseagreen;
                                                border-radius: 4px; }}
                                                """
        )
        self.minimize_pushButton.setStyleSheet(
            f"""QPushButton{{background: teal;
                                                border-radius: 4px;
                                                image: url('{self.icon_path}/icons/minimize.png'); 
                                            padding: 6px 6px 6px 6px;}}
                                                QPushButton::hover{{
                                                background: cornflowerblue; 
                                                border-radius: 4px;
                                                }}"""
        )
        self.close_pushButton.setStyleSheet(
            f"""QPushButton{{background: tomato; 
                                            border-radius: 4px;
                                            image: url('{self.icon_path}/icons/close.png'); 
                                            padding: 6px 6px 6px 6px;
                                            }}
                                            QPushButton::hover{{background: orangered; 
                                            border-radius: 4px;}}"""
        )
        self.add_pushButton.setStyleSheet(
            f"""QPushButton{{background: seagreen; 
                                                border-radius: 4px;
                                                image: url('{self.icon_path}/icons/add.png'); 
                                            padding: 6px 6px 6px 6px;}}
                                                QPushButton::hover{{
                                                background: mediumseagreen;
                                                border-radius: 4px; }}
                                                """
        )
        self.show_pushButton.setStyleSheet(
            f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/up.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
        )
        self.prev_pushButton.setStyleSheet(
            f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/prev.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
        )
        self.play_pushButton.setStyleSheet(
            f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/pause.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
        )
        self.next_pushButton.setStyleSheet(
            f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/next.png'); border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
        )


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    form = MainApp()
    form.show()
    sys.exit(app.exec_())
