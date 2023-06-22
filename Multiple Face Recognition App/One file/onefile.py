import sys
import os
import shutil
import threading
import cv2
import numpy as np
from PIL import Image
import sqlite3

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal as Signal, pyqtSlot as Slot
from PyQt5.QtGui import QPixmap, QImage


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(693, 394)
        self.mw = MainWindow
        MainWindow.setMinimumSize(QtCore.QSize(693, 394))
        MainWindow.setMaximumSize(QtCore.QSize(2000, 2000))
        MainWindow.setStyleSheet("QMainWindow#MainWindow{background: darkgreen;}")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMaximumSize(QtCore.QSize(693, 394))
        self.centralwidget.setStyleSheet("border-radius: 6px; \n" "color: white;")
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.stackedWidget_2 = QtWidgets.QStackedWidget(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.stackedWidget_2.setFont(font)
        self.stackedWidget_2.setStyleSheet("")
        self.stackedWidget_2.setObjectName("stackedWidget_2")
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.page_3)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.stackedWidget = QtWidgets.QStackedWidget(self.page_3)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.stackedWidget.setFont(font)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.frame_left = QtWidgets.QFrame(self.page)
        self.frame_left.setMinimumSize(QtCore.QSize(235, 304))
        self.frame_left.setMaximumSize(QtCore.QSize(235, 16777215))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_left.setFont(font)
        self.frame_left.setStyleSheet("QFrame#frame_left{background: seagreen;}")
        self.frame_left.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_left.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_left.setObjectName("frame_left")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_left)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame_data = QtWidgets.QFrame(self.frame_left)
        self.frame_data.setMinimumSize(QtCore.QSize(0, 120))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_data.setFont(font)
        self.frame_data.setStyleSheet("QFrame#frame_data{background: mediumpurple;}")
        self.frame_data.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_data.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_data.setObjectName("frame_data")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.frame_data)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.frame_data)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("")
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label, 0, QtCore.Qt.AlignTop)
        self.lineEdit_user = QtWidgets.QLineEdit(self.frame_data)
        self.lineEdit_user.setMinimumSize(QtCore.QSize(160, 20))
        self.lineEdit_user.setMaximumSize(QtCore.QSize(500, 25))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(9)
        self.lineEdit_user.setFont(font)
        self.lineEdit_user.setToolTip("")
        self.lineEdit_user.setStyleSheet("color: black; padding-left: 3px; ")
        self.lineEdit_user.setFrame(False)
        self.lineEdit_user.setDragEnabled(True)
        self.lineEdit_user.setCursorMoveStyle(QtCore.Qt.VisualMoveStyle)
        self.lineEdit_user.setClearButtonEnabled(True)
        self.lineEdit_user.setObjectName("lineEdit_user")
        self.verticalLayout_3.addWidget(self.lineEdit_user, 0, QtCore.Qt.AlignTop)
        self.lineEdit_name = QtWidgets.QLineEdit(self.frame_data)
        self.lineEdit_name.setMinimumSize(QtCore.QSize(160, 20))
        self.lineEdit_name.setMaximumSize(QtCore.QSize(500, 25))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(9)
        self.lineEdit_name.setFont(font)
        self.lineEdit_name.setStyleSheet("color: black; padding-left: 3px; ")
        self.lineEdit_name.setFrame(False)
        self.lineEdit_name.setDragEnabled(True)
        self.lineEdit_name.setClearButtonEnabled(True)
        self.lineEdit_name.setObjectName("lineEdit_name")
        self.verticalLayout_3.addWidget(self.lineEdit_name)
        self.pushButton_data = QtWidgets.QPushButton(self.frame_data)
        self.pushButton_data.setMinimumSize(QtCore.QSize(160, 25))
        self.pushButton_data.setMaximumSize(QtCore.QSize(500, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.pushButton_data.setFont(font)
        self.pushButton_data.setStyleSheet(
            "QPushButton{border: 1px solid white; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::hover{border: 1px solid black; background: white; color: black; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::pressed{border: 1px solid white; background: slategray; color: white; padding-bottom: 2px;}"
        )
        self.pushButton_data.setObjectName("pushButton_data")
        self.verticalLayout_3.addWidget(self.pushButton_data)
        self.verticalLayout_2.addWidget(self.frame_data)
        self.frame_train = QtWidgets.QFrame(self.frame_left)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_train.setFont(font)
        self.frame_train.setStyleSheet("QFrame#frame_train{background: darkseagreen;}")
        self.frame_train.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_train.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_train.setObjectName("frame_train")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frame_train)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.frame_train)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: white;")
        self.label_2.setObjectName("label_2")
        self.verticalLayout_4.addWidget(self.label_2, 0, QtCore.Qt.AlignTop)
        self.pushButton_train = QtWidgets.QPushButton(self.frame_train)
        self.pushButton_train.setMinimumSize(QtCore.QSize(160, 25))
        self.pushButton_train.setMaximumSize(QtCore.QSize(500, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.pushButton_train.setFont(font)
        self.pushButton_train.setStyleSheet(
            "QPushButton{border: 1px solid white; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::hover{border: 1px solid black; background: white; color: black; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::pressed{border: 1px solid white; background: slategray; color: white; padding-bottom: 2px;}"
        )
        self.pushButton_train.setObjectName("pushButton_train")
        self.verticalLayout_4.addWidget(self.pushButton_train)
        self.verticalLayout_2.addWidget(self.frame_train)
        self.frame_view = QtWidgets.QFrame(self.frame_left)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_view.setFont(font)
        self.frame_view.setStyleSheet("QFrame#frame_view{background: lightseagreen;}")
        self.frame_view.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_view.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_view.setObjectName("frame_view")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_view)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_3 = QtWidgets.QLabel(self.frame_view)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: white;")
        self.label_3.setObjectName("label_3")
        self.verticalLayout_5.addWidget(self.label_3, 0, QtCore.Qt.AlignTop)
        self.pushButton_view = QtWidgets.QPushButton(self.frame_view)
        self.pushButton_view.setMinimumSize(QtCore.QSize(160, 25))
        self.pushButton_view.setMaximumSize(QtCore.QSize(500, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.pushButton_view.setFont(font)
        self.pushButton_view.setStyleSheet(
            "QPushButton{border: 1px solid white; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::hover{border: 1px solid black; background: white; color: black; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::pressed{border: 1px solid white; background: slategray; color: white; padding-bottom: 2px;}"
        )
        self.pushButton_view.setObjectName("pushButton_view")
        self.verticalLayout_5.addWidget(self.pushButton_view)
        self.verticalLayout_2.addWidget(self.frame_view)
        self.pushButton_clear = QtWidgets.QPushButton(self.frame_left)
        self.pushButton_clear.setMinimumSize(QtCore.QSize(160, 30))
        self.pushButton_clear.setMaximumSize(QtCore.QSize(500, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.pushButton_clear.setFont(font)
        self.pushButton_clear.setStyleSheet(
            "QPushButton{border: 1px solid white; padding-bottom: 2px; background:#e8464e;}\n"
            "\n"
            "QPushButton::hover{border: 1px solid black; background: white; color: black; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::pressed{border: 1px solid white; background: slategray; color: white; padding-bottom: 2px;}"
        )
        self.pushButton_clear.setObjectName("pushButton_clear")
        self.verticalLayout_2.addWidget(self.pushButton_clear)
        self.frame_10 = QtWidgets.QFrame(self.frame_left)
        self.frame_10.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_10.setFont(font)
        self.frame_10.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_10.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_10.setObjectName("frame_10")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame_10)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.pushButton_help = QtWidgets.QPushButton(self.frame_10)
        self.pushButton_help.setMinimumSize(QtCore.QSize(0, 30))
        self.pushButton_help.setMaximumSize(QtCore.QSize(500, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.pushButton_help.setFont(font)
        self.pushButton_help.setStyleSheet(
            "QPushButton{border: 1px solid white; padding-bottom: 2px; background: #4b7196;}\n"
            "\n"
            "QPushButton::hover{border: 1px solid black; background: white; color: black; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::pressed{border: 1px solid white; background: slategray; color: white; padding-bottom: 2px;}"
        )
        self.pushButton_help.setObjectName("pushButton_help")
        self.horizontalLayout_3.addWidget(self.pushButton_help)
        self.pushButton_browse = QtWidgets.QPushButton(self.frame_10)
        self.pushButton_browse.setMinimumSize(QtCore.QSize(0, 30))
        self.pushButton_browse.setMaximumSize(QtCore.QSize(16777215, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.pushButton_browse.setFont(font)
        self.pushButton_browse.setStyleSheet(
            "QPushButton{border: 1px solid white; padding-bottom: 2px; background: rgb(255,160,71);}\n"
            "\n"
            "QPushButton::hover{border: 1px solid black; background: white; color: black; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::pressed{border: 1px solid white; background: slategray; color: white; padding-bottom: 2px;}"
        )
        self.pushButton_browse.setObjectName("pushButton_browse")
        self.horizontalLayout_3.addWidget(self.pushButton_browse)
        self.verticalLayout_2.addWidget(self.frame_10)
        self.verticalLayout_8.addWidget(self.frame_left)
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.page_2)
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.frame_welcome = QtWidgets.QFrame(self.page_2)
        self.frame_welcome.setMinimumSize(QtCore.QSize(235, 304))
        self.frame_welcome.setMaximumSize(QtCore.QSize(235, 16777215))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_welcome.setFont(font)
        self.frame_welcome.setStyleSheet("QFrame#frame_welcome{background: seagreen;}")
        self.frame_welcome.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_welcome.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_welcome.setObjectName("frame_welcome")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.frame_welcome)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.frame = QtWidgets.QFrame(self.frame_welcome)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.frame_5 = QtWidgets.QFrame(self.frame)
        self.frame_5.setStyleSheet("QFrame{background: mediumpurple;}")
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout_14 = QtWidgets.QVBoxLayout(self.frame_5)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.label_6 = QtWidgets.QLabel(self.frame_5)
        self.label_6.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_14.addWidget(self.label_6)
        self.label_7 = QtWidgets.QLabel(self.frame_5)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_14.addWidget(self.label_7, 0, QtCore.Qt.AlignTop)
        self.verticalLayout_6.addWidget(self.frame_5)
        self.frame_6 = QtWidgets.QFrame(self.frame)
        self.frame_6.setStyleSheet("QFrame{background: darkseagreen;}")
        self.frame_6.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_6.setObjectName("frame_6")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout(self.frame_6)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.label_8 = QtWidgets.QLabel(self.frame_6)
        self.label_8.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_15.addWidget(self.label_8)
        self.label_9 = QtWidgets.QLabel(self.frame_6)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_15.addWidget(self.label_9, 0, QtCore.Qt.AlignTop)
        self.verticalLayout_6.addWidget(self.frame_6)
        self.frame_7 = QtWidgets.QFrame(self.frame)
        self.frame_7.setStyleSheet("QFrame{background: lightseagreen;}")
        self.frame_7.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_7.setObjectName("frame_7")
        self.verticalLayout_16 = QtWidgets.QVBoxLayout(self.frame_7)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.label_10 = QtWidgets.QLabel(self.frame_7)
        self.label_10.setMaximumSize(QtCore.QSize(16777215, 15))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_16.addWidget(self.label_10)
        self.label_11 = QtWidgets.QLabel(self.frame_7)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.verticalLayout_16.addWidget(self.label_11, 0, QtCore.Qt.AlignTop)
        self.verticalLayout_6.addWidget(self.frame_7)
        self.verticalLayout_10.addWidget(self.frame, 0, QtCore.Qt.AlignTop)
        self.pushButton_back = QtWidgets.QPushButton(self.frame_welcome)
        self.pushButton_back.setMinimumSize(QtCore.QSize(160, 30))
        self.pushButton_back.setMaximumSize(QtCore.QSize(500, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.pushButton_back.setFont(font)
        self.pushButton_back.setStyleSheet(
            "QPushButton{border: 1px solid white; padding-bottom: 2px; background: #4b7196;}\n"
            "\n"
            "QPushButton::hover{border: 1px solid black; background: white; color: black; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::pressed{border: 1px solid white; background: slategray; color: white; padding-bottom: 2px;}"
        )
        self.pushButton_back.setObjectName("pushButton_back")
        self.verticalLayout_10.addWidget(self.pushButton_back)
        self.verticalLayout_9.addWidget(self.frame_welcome)
        self.stackedWidget.addWidget(self.page_2)
        self.horizontalLayout_2.addWidget(self.stackedWidget)
        self.frame_8 = QtWidgets.QFrame(self.page_3)
        self.frame_8.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_8.setMaximumSize(QtCore.QSize(500, 500))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_8.setFont(font)
        self.frame_8.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_8.setObjectName("frame_8")
        self.verticalLayout_17 = QtWidgets.QVBoxLayout(self.frame_8)
        self.verticalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_17.setSpacing(0)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.frame_right = QtWidgets.QFrame(self.frame_8)
        self.frame_right.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_right.setMaximumSize(QtCore.QSize(450, 400))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_right.setFont(font)
        self.frame_right.setStyleSheet("QFrame#frame_right{background: seagreen;}")
        self.frame_right.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_right.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_right.setObjectName("frame_right")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame_right)
        self.verticalLayout.setContentsMargins(9, 9, 9, 9)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_2 = QtWidgets.QFrame(self.frame_right)
        self.frame_2.setMaximumSize(QtCore.QSize(480, 40))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_2.setFont(font)
        self.frame_2.setStyleSheet("background: mediumseagreen;")
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_4 = QtWidgets.QLabel(self.frame_2)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(True)
        self.label_4.setFont(font)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_7.addWidget(self.label_4)
        self.verticalLayout.addWidget(self.frame_2)
        self.frame_9 = QtWidgets.QFrame(self.frame_right)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.frame_9.setFont(font)
        self.frame_9.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_9.setObjectName("frame_9")
        self.verticalLayout_18 = QtWidgets.QVBoxLayout(self.frame_9)
        self.verticalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_18.setSpacing(0)
        self.verticalLayout_18.setObjectName("verticalLayout_18")
        self.label_video = QtWidgets.QLabel(self.frame_9)
        self.label_video.setMinimumSize(QtCore.QSize(416, 312))
        self.label_video.setMaximumSize(QtCore.QSize(420, 315))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        self.label_video.setFont(font)
        self.label_video.setStyleSheet("background: teal;")
        self.label_video.setText("")
        self.label_video.setObjectName("label_video")
        self.verticalLayout_18.addWidget(self.label_video)
        self.verticalLayout.addWidget(self.frame_9)
        self.verticalLayout_17.addWidget(self.frame_right)
        self.horizontalLayout_2.addWidget(self.frame_8)
        self.stackedWidget_2.addWidget(self.page_3)
        self.page_4 = QtWidgets.QWidget()
        self.page_4.setObjectName("page_4")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout(self.page_4)
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.frame_4 = QtWidgets.QFrame(self.page_4)
        self.frame_4.setStyleSheet("QFrame{background: seagreen;}")
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.frame_3 = QtWidgets.QFrame(self.frame_4)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_5 = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_11.addWidget(self.label_5)
        spacerItem = QtWidgets.QSpacerItem(
            20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        self.verticalLayout_11.addItem(spacerItem)
        self.pushButton_next = QtWidgets.QPushButton(self.frame_3)
        self.pushButton_next.setMinimumSize(QtCore.QSize(160, 30))
        self.pushButton_next.setMaximumSize(QtCore.QSize(160, 30))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Small")
        font.setPointSize(10)
        self.pushButton_next.setFont(font)
        self.pushButton_next.setStyleSheet(
            "QPushButton{border: 1px solid white; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::hover{border: 1px solid black; background: white; color: black; padding-bottom: 2px;}\n"
            "\n"
            "QPushButton::pressed{border: 1px solid white; background: slategray; color: white; padding-bottom: 2px;}"
        )
        self.pushButton_next.setObjectName("pushButton_next")
        self.verticalLayout_11.addWidget(
            self.pushButton_next, 0, QtCore.Qt.AlignHCenter
        )
        self.verticalLayout_13.addWidget(
            self.frame_3, 0, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
        )
        self.verticalLayout_12.addWidget(self.frame_4)
        self.stackedWidget_2.addWidget(self.page_4)
        self.horizontalLayout.addWidget(self.stackedWidget_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.stackedWidget_2.setCurrentIndex(0)
        self.stackedWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Face Recognition App"))
        self.label.setText(_translate("MainWindow", "ADD DATA"))
        self.lineEdit_user.setPlaceholderText(_translate("MainWindow", "ID"))
        self.lineEdit_name.setPlaceholderText(_translate("MainWindow", "Name"))
        self.pushButton_data.setText(_translate("MainWindow", "Start"))
        self.label_2.setText(_translate("MainWindow", "TRAIN"))
        self.pushButton_train.setText(_translate("MainWindow", "Start"))
        self.label_3.setText(_translate("MainWindow", "VIEW"))
        self.pushButton_view.setText(_translate("MainWindow", "Start"))
        self.pushButton_clear.setText(_translate("MainWindow", "Clear Data"))
        self.pushButton_help.setText(_translate("MainWindow", "Help"))
        self.pushButton_browse.setText(_translate("MainWindow", "Browse"))
        self.label_6.setText(_translate("MainWindow", "1. Add Facial Data"))
        self.label_7.setText(
            _translate(
                "MainWindow",
                'a. Put ID in "ID" \n'
                'b. Put Name in "Name" \n'
                'c. Click "Start"\n'
                "d. Wait till finish",
            )
        )
        self.label_8.setText(_translate("MainWindow", "2. Train the Collected Data"))
        self.label_9.setText(
            _translate("MainWindow", 'a. Click "Start"\n' "b. Wait till finish")
        )
        self.label_10.setText(_translate("MainWindow", "3. View"))
        self.label_11.setText(
            _translate("MainWindow", 'a. Click on "Start"\n' "b. Check feed")
        )
        self.pushButton_back.setText(_translate("MainWindow", "Back"))
        self.label_4.setText(_translate("MainWindow", "Notification"))
        self.label_5.setText(_translate("MainWindow", "WELCOME"))
        self.pushButton_next.setText(_translate("MainWindow", "NEXT"))


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
            self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            try:
                self.cam = cv2.VideoCapture(browse_path)
            except:
                self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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
            self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        else:
            try:
                self.cam = cv2.VideoCapture(browse_path)
            except:
                self.cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainApp()
    form.show()
    sys.exit(app.exec_())
