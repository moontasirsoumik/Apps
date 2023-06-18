from PyQt5 import QtCore, QtGui, QtWidgets


class Cards:
    def cards_initiate(self):
        self.card_counter += 1

        self.widget_frame_ = QtWidgets.QFrame(self.scroll_frame)
        self.widget_frame_.setMinimumSize(QtCore.QSize(0, 0))
        self.widget_frame_.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Text")
        font.setPointSize(11)
        self.widget_frame_.setFont(font)
        self.widget_frame_.setStyleSheet(
            "QFrame#widget_frame_{background: rgba(0, 0, 0, 100); border-radius: 4px; }\n"
            ""
        )
        self.widget_frame_.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.widget_frame_.setFrameShadow(QtWidgets.QFrame.Raised)
        self.widget_frame_.setObjectName("widget_frame_")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.widget_frame_)
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.widget_frame_left_ = QtWidgets.QFrame(self.widget_frame_)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Text")
        font.setPointSize(11)
        self.widget_frame_left_.setFont(font)
        self.widget_frame_left_.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.widget_frame_left_.setFrameShadow(QtWidgets.QFrame.Raised)
        self.widget_frame_left_.setObjectName("widget_frame_left_")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.widget_frame_left_)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.title_label_ = QtWidgets.QLabel(self.widget_frame_left_)
        self.title_label_.setMinimumSize(QtCore.QSize(300, 0))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Text")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.title_label_.setFont(font)
        self.title_label_.setObjectName("title_label_")
        self.verticalLayout_6.addWidget(self.title_label_)
        self.artist_label_ = QtWidgets.QLabel(self.widget_frame_left_)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Text")
        font.setPointSize(9)
        font.setItalic(True)
        self.artist_label_.setFont(font)
        self.artist_label_.setObjectName("artist_label_")
        self.verticalLayout_6.addWidget(self.artist_label_)
        self.duration_label_ = QtWidgets.QLabel(self.widget_frame_left_)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Text")
        font.setPointSize(8)
        self.duration_label_.setFont(font)
        self.duration_label_.setObjectName("duration_label_")
        self.verticalLayout_6.addWidget(self.duration_label_)
        self.horizontalLayout_5.addWidget(self.widget_frame_left_)
        self.widget_frame_right_ = QtWidgets.QFrame(self.widget_frame_)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Text")
        font.setPointSize(11)
        self.widget_frame_right_.setFont(font)
        self.widget_frame_right_.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.widget_frame_right_.setFrameShadow(QtWidgets.QFrame.Raised)
        self.widget_frame_right_.setObjectName("widget_frame_right_")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_frame_right_)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.up_pushButton_ = QtWidgets.QPushButton(self.widget_frame_right_)
        self.up_pushButton_.setMinimumSize(QtCore.QSize(20, 20))
        self.up_pushButton_.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Text")
        font.setPointSize(11)
        self.up_pushButton_.setFont(font)
        self.up_pushButton_.setObjectName("up_pushButton_")
        self.horizontalLayout_6.addWidget(self.up_pushButton_)
        self.down_pushButton_ = QtWidgets.QPushButton(self.widget_frame_right_)
        self.down_pushButton_.setMinimumSize(QtCore.QSize(20, 20))
        self.down_pushButton_.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Text")
        font.setPointSize(11)
        self.down_pushButton_.setFont(font)
        self.down_pushButton_.setObjectName("down_pushButton_")
        self.horizontalLayout_6.addWidget(self.down_pushButton_)
        self.play_pushButton_ = QtWidgets.QPushButton(self.widget_frame_right_)
        self.play_pushButton_.setMinimumSize(QtCore.QSize(20, 20))
        self.play_pushButton_.setMaximumSize(QtCore.QSize(20, 20))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Variable Static Text")
        font.setPointSize(11)
        self.play_pushButton_.setFont(font)
        self.play_pushButton_.setObjectName("play_pushButton_")
        self.horizontalLayout_6.addWidget(self.play_pushButton_)
        self.horizontalLayout_5.addWidget(
            self.widget_frame_right_, 0, QtCore.Qt.AlignRight
        )
        self.verticalLayout_7.addWidget(self.widget_frame_)

        # self.scroll_style()

    def scroll_style(self):
        self.scrollArea.setStyleSheet(
            "QScrollArea {\n"
            "        border: none;\n"
            "    }\n"
            "\n"
            "    QScrollBar {\n"
            "        border-radius: 5px;\n"
            "    }\n"
            "\n"
            "    QScrollBar:horizontal {\n"
            "        height: 7px;\n"
            "\n"
            "    }\n"
            "\n"
            "    QScrollBar:vertical {\n"
            "        width: 7px;\n"
            "        border-radius: 10px;\n"
            "    }\n"
            "\n"
            "    QScrollBar::handle {\n"
            "        background:  rgba(0, 0, 0, 140);\n"
            "        border-radius: 10px;\n"
            "    }\n"
            "\n"
            "    QScrollBar::handle::hover {\n"
            "        background:  rgba(0, 0, 0, 180);\n"
            "        border-radius: 10px;\n"
            "    }\n"
            "\n"
            "    QScrollBar::handle:horizontal {\n"
            "        height: 25px;\n"
            "        min-width: 10px;\n"
            "    }\n"
            "\n"
            "    QScrollBar::handle:vertical {\n"
            "        width: 25px;\n"
            "        min-height: 10px;\n"
            "\n"
            "    }\n"
            "\n"
            "    QScrollBar::add-line {\n"
            "        border: none;\n"
            "    }\n"
            "\n"
            "    QScrollBar::sub-line {\n"
            "\n"
            "        border: none;\n"
            "        background: none;\n"
            "    }"
        )

    def create_cards(self, title, artist, duration):
        self.cards_initiate()

        # Adding unique names to the cards
        self.widget_frame_.setObjectName(f"widget_frame_{self.card_counter}")
        self.widget_frame_left_.setObjectName(f"widget_frame_left_{self.card_counter}")
        self.artist_label_.setObjectName(f"artist_label_{self.card_counter}")
        self.duration_label_.setObjectName(f"duration_label_{self.card_counter}")
        self.title_label_.setObjectName(f"title_label_{self.card_counter}")
        self.widget_frame_right_.setObjectName(
            f"widget_frame_right_{self.card_counter}"
        )
        self.down_pushButton_.setObjectName(f"down_pushButton_{self.card_counter}")
        self.up_pushButton_.setObjectName(f"up_pushButton_{self.card_counter}")
        self.play_pushButton_.setObjectName(f"play_pushButton_{self.card_counter}")

        # Setting attributes
        setattr(self, f"widget_frame_{self.card_counter}", self.widget_frame_)
        setattr(self, f"widget_frame_left_{self.card_counter}", self.widget_frame_left_)
        setattr(self, f"artist_label_{self.card_counter}", self.artist_label_)
        setattr(self, f"duration_label_{self.card_counter}", self.duration_label_)
        setattr(self, f"title_label_{self.card_counter}", self.title_label_)
        setattr(
            self, f"widget_frame_right_{self.card_counter}", self.widget_frame_right_
        )
        setattr(self, f"down_pushButton_{self.card_counter}", self.down_pushButton_)
        setattr(self, f"play_pushButton_{self.card_counter}", self.play_pushButton_)
        setattr(self, f"up_pushButton_{self.card_counter}", self.up_pushButton_)

        # Creating pushbutton connects
        cc = self.card_counter
        self.up_pushButton_.clicked.connect(lambda: self.up_down(cc, "up"))
        self.down_pushButton_.clicked.connect(lambda: self.up_down(cc, "down"))
        self.play_pushButton_.clicked.connect(
            lambda: self.play(cc, title, artist, duration)
        )

        # Duration calculation
        minutes = int(int(duration) / 60)
        seconds = int(duration) % 60
        duration_text = f"{minutes} min. {seconds} sec."

        # Setting texts
        self.title_label_.setText(title)
        self.artist_label_.setText(artist)
        self.duration_label_.setText(str(duration_text))
        self.up_pushButton_.setStyleSheet(
            f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/up.png'); border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
        )
        self.down_pushButton_.setStyleSheet(
            f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/down.png'); border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
        )
        self.styler()

    def styler(self, card_counter=-1):
        # Stylesheet for all the cards
        for i in range(1, self.card_counter + 1):
            try:
                exec(
                    f"""self.widget_frame_{i}.setStyleSheet(
                    "QFrame#widget_frame_{i}{{background: rgba(0, 0, 0, 50); border-radius: 4px; }}"
                )"""
                )

                exec(
                    f"""self.play_pushButton_{i}.setStyleSheet("QPushButton{{background: transparent; image: url('{self.icon_path}/icons/play.png'); border-radius: 4px;}}"
                    "QPushButton::hover{{background: rgba(255, 255, 255, 20); }}")"""
                )

                exec(f"self.down_pushButton_{i}.show()")
                exec(f"self.up_pushButton_{i}.show()")

            except:
                pass

        try:
            exec(f"self.up_pushButton_{1}.hide()")
            exec(f"self.down_pushButton_{self.card_counter}.hide()")
        except:
            pass

        # Stylesheet for only the playing card
        if card_counter != -1:
            try:
                exec(
                    f"""self.widget_frame_{card_counter}.setStyleSheet(
                        "QFrame#widget_frame_{card_counter}{{background: rgba(0, 0, 0, 100); border-radius: 4px; }}"
                    )"""
                )
                exec(f"self.down_pushButton_{card_counter}.hide()")
                exec(f"self.up_pushButton_{card_counter}.hide()")
                exec(
                    f"""self.play_pushButton_{card_counter}.setStyleSheet("QPushButton{{background: transparent; image: url('{self.icon_path}/icons/pause.png'); border-radius: 4px;}}"
                "QPushButton::hover{{background: rgba(255, 255, 255, 20); }}")"""
                )

            except:
                pass

        # Hiding up/down button for certain cards
        if card_counter != -1:
            try:
                exec(f"self.down_pushButton_{card_counter-1}.hide()")
            except:
                pass
            try:
                exec(f"self.up_pushButton_{card_counter+1}.hide()")
            except:
                pass

    def card_clear(self):
        # Deleting all cards
        for i in range(self.card_counter):
            try:
                exec(f"self.widget_frame_{i+1}.deleteLater()")
                exec(f"self.widget_frame_{i+1} = None")
            except:
                pass
