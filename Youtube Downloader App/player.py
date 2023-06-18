from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtCore import QUrl


class Player:
    def play(self, card_counter=-1, title=0, artist=0, duration=0):
        self.card_counter_player = card_counter
        self.bottom_frame.show()
        self.player.positionChanged.connect(self.update_duration)

        if self.card_counter_player > 0:
            # Pause/Play for an already playing card
            if self.playing == True and self.c_playing == self.card_counter_player:
                self.player.pause()
                self.playing = False
                self.play_pushButton.setStyleSheet(
                    f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/play.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
                )

                try:
                    exec(
                        f"""self.play_pushButton_{self.c_playing}.setStyleSheet("QPushButton{{background: transparent; image: url('{self.icon_path}/icons/play.png'); border-radius: 4px;}}"
                    "QPushButton::hover{{background: rgba(255, 255, 255, 20); }}")"""
                    )
                except:
                    pass
            elif self.playing == False and self.c_playing == self.card_counter_player:
                self.player.play()
                self.playing = True
                self.play_pushButton.setStyleSheet(
                    f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/pause.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
                )
                try:
                    exec(
                        f"""self.play_pushButton_{self.c_playing}.setStyleSheet("QPushButton{{background: transparent; image: url('{self.icon_path}/icons/pause.png'); border-radius: 4px;}}"
                    "QPushButton::hover{{background: rgba(255, 255, 255, 20); }}")"""
                    )
                except:
                    pass

            else:
                try:
                    # Geting title, artist, and duration
                    if title == -1 and artist == -1 and duration == -1:
                        title = self.title[self.c_playing]
                        artist = self.artist[self.c_playing]
                        duration = self.duration[self.c_playing]

                    elif title == -2 and artist == -2 and duration == -2:
                        title = self.title[self.c_playing - 2]
                        artist = self.artist[self.c_playing - 2]
                        duration = self.duration[self.c_playing - 2]

                    # Getting track name from db
                    self.c.execute(
                        "SELECT second_name FROM playlist WHERE name = ?",
                        ((self.card_counter_player,)),
                    )
                    x = self.c.fetchone()

                    audio_path = x[0]

                    # Playing the track
                    url = QUrl.fromLocalFile(audio_path)
                    content = QMediaContent(url)

                    self.player.setMedia(content)
                    self.player.play()
                    self.play_pushButton.setStyleSheet(
                        f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/pause.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
                    )
                    try:
                        exec(
                            f"""self.play_pushButton_{self.card_counter_player}.setStyleSheet("QPushButton{{background: transparent; image: url('{self.icon_path}/icons/pause.png'); border-radius: 4px;}}"
                        "QPushButton::hover{{background: rgba(255, 255, 255, 20); }}")"""
                        )
                    except:
                        pass

                    # Duration calculation
                    minutes = int(int(duration) / 60)
                    seconds = int(duration) % 60
                    duration_text = f"{minutes} min. {seconds} sec."

                    # Updating texts and variables
                    self.duration_label.setText(str(duration_text))
                    self.title_label.setText(title)
                    self.artist_label.setText(artist)
                    self.playing = True
                    self.c_playing = self.card_counter_player
                    self.styler(self.card_counter_player)

                    self.start_progress_bar(int(duration))

                except:
                    pass

        # Pause/Play from the Now Playing bar
        elif self.card_counter_player == -1:
            if self.playing == True:
                self.player.pause()
                self.playing = False
                self.play_pushButton.setStyleSheet(
                    f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/play.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
                )
                try:
                    exec(
                        f"""self.play_pushButton_{self.c_playing}.setStyleSheet("QPushButton{{background: transparent; image: url('{self.icon_path}/icons/play.png'); border-radius: 4px;}}"
                    "QPushButton::hover{{background: rgba(255, 255, 255, 20); }}")"""
                    )
                except:
                    pass
            else:
                self.player.play()
                self.playing = True
                self.play_pushButton.setStyleSheet(
                    f"""QPushButton{{background: transparent;
                                            image: url('{self.icon_path}/icons/pause.png');border-radius: 4px;}}
                                            QPushButton::hover{{background: rgba(255, 255, 255, 20);}}"""
                )
                try:
                    exec(
                        f"""self.play_pushButton_{self.c_playing}.setStyleSheet("QPushButton{{background: transparent; image: url('{self.icon_path}/icons/pause.png'); border-radius: 4px;}}"
                    "QPushButton::hover{{background: rgba(255, 255, 255, 20); }}")"""
                    )
                except:
                    pass

    def update_duration(self):
        # Updating the duration on the song card and the now playing bar
        try:
            exec(
                f"""self.widget_frame_{self.card_counter_player}.setStyleSheet(
                            "QFrame#widget_frame_{self.card_counter_player}{{background-color: qlineargradient(x1: 0, x2: {float(self.player.position())/(float(self.player.duration())/2)}, stop: .5 rgba(0, 0, 0, 50), stop: 0.500000001 rgba(0, 0, 0, 100))}}"
                        )"""
            )

            self.bottom_frame.setStyleSheet(
                f"QFrame#bottom_frame{{background-color: qlineargradient(x1: 0, x2: {float(self.player.position())/(float(self.player.duration())/2)}, stop: .5 rgba(0, 0, 0, 140), stop: 0.500000001 rgba(0, 0, 0, 100)); border-radius: 4px; }}"
            )

        except:
            pass

        # Once the song has ended, autoplay to next song
        if (
            self.player.position() > 0
            and self.player.duration() == self.player.position()
        ):
            self.playing = False
            self.styler()
            try:
                self.next_pushButton.click()
            except:
                pass
