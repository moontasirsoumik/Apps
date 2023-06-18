from PyQt5.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot
from pytube import YouTube
import sqlite3
import os

class MusicCheck(QObject): 
    done = Signal(bool)
    
    @Slot(str, list)
    def check(self, link, title): 
        self.yt = YouTube(link, use_oauth=True, allow_oauth_cache=True)
        if self.yt.title  not in title:
            self.done.emit(True)
        else: 
            self.done.emit(False)
        
        
class MusicAdd(QObject):
    completed = Signal(bool)
    
    @Slot(str)
    def add(self, link):
        try:
            # url input from user
            video_url = link

            self.yt = YouTube(video_url, use_oauth=True, allow_oauth_cache=True)

            #Title of video
            print("Title: ",self.yt.title)


            #Number of views of video
            print("Number of views: ",self.yt.views)
            #Length of the video
            print("Length of video: ",self.yt.length,"seconds")
            #Rating
            print("Ratings: ",self.yt.rating)
            print("Author: ",self.yt.author)

            # print(self.yt.streams.filter(only_audio=True))
            print("\n")
            
            # extract only audio
            video = self.yt.streams.get_audio_only()

            # saving destination
            destination = os.getcwd() + "\\Downloads\\"
            currant_dir = os.getcwd()
            # download the file
            out_file = video.download(output_path=destination)
            
            # save the file
            base, ext = os.path.splitext(out_file)
            # new_file = base + '.mp3'
            try:
                base, ext = os.path.splitext(out_file)
                self.new_file = base + '.mp3'
                os.rename(out_file, self.new_file)

                os.chdir(currant_dir)
            except: 
                print("failed to create mp3")
                self.completed.emit(False)
            # result of success
            print(self.yt.title + " has been successfully downloaded.")
            ans = self.data_update()
            
            if ans == False: 
                self.completed.emit(False)
            else: 
                self.completed.emit(True)           
        except: 
            print("Failed")
            self.completed.emit(False)

    def data_update(self): 
        try: 
            # Database 
            con = sqlite3.connect("music.db", check_same_thread=False)
            c0 = con.cursor()

            c0.execute(
                """CREATE TABLE IF NOT EXISTS playlist ( 
                    name int, 
                    title text, 
                    duration text, 
                    artist text, z
                    second_name text
                    )"""
            )
            con.commit()
            
            c0.execute("SELECT * FROM playlist")
            x = c0.fetchall()
            
            print(len(x))
            name = int(len(x)) + 1  
            info = [(name, self.yt.title, self.yt.length, self.yt.author, self.new_file)]
            c0.executemany("INSERT INTO playlist VALUES (?, ?, ?, ?, ?)", info)
            con.commit()
            con.close()
            return True
        except: 
            print("eije ekhane")
            return False

