# importing packages
from pytube import YouTube
import os

import sqlite3


class Music:
    def music_add(self, video_url, name):
        try:
            # url input from user
            self.yt = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)

            # Title of video
            if self.yt.title not in self.title:
                # extract only audio
                video = self.yt.streams.get_audio_only()

                # saving destination
                destination = os.getcwd() + "\\Downloads\\"
                currant_dir = os.getcwd()
                # download the file
                out_file = video.download(output_path=destination)

                # save the file
                base, ext = os.path.splitext(out_file)
                try:
                    base, ext = os.path.splitext(out_file)
                    self.new_file = base + ".mp3"
                    os.rename(out_file, self.new_file)

                    os.chdir(currant_dir)
                except:
                    pass
                # result of success
                ans = self.data_update()

                if ans == False:
                    return False
                else:
                    return True

            else:
                return False

        except:
            return False

    def data_update(self):
        try:
            # Database
            currant_dir = os.getcwd()
            conn = sqlite3.connect(
                "music.db", check_same_thread=False
            )
            c = conn.cursor()
            c.execute(
                """CREATE TABLE IF NOT EXISTS playlist ( 
                    name int, 
                    title text, 
                    duration text, 
                    artist text, 
                    second_name text
                    )"""
            )
            conn.commit()

            info = [
                (
                    self.name,
                    self.yt.title,
                    self.yt.length,
                    self.yt.author,
                    self.new_file,
                )
            ]
            c.executemany("INSERT INTO playlist VALUES (?, ?, ?, ?, ?)", info)
            conn.commit()
            conn.close()
            return True
        except:
            return False
