# from PyQt5 import QtCore, QtGui, QtWidgets
import os


class QControl:
    def up_down(self, card_counter, direction):
        # Creating backup database
        self.c.execute("DROP table IF EXISTS playlist_backup;")
        self.conn.commit()
        self.c.execute(
            """CREATE TABLE playlist_backup ( 
                    name int, 
                    title text, 
                    duration text, 
                    artist text, 
                    second_name text
                    )"""
        )
        self.conn.commit()

        # Setting up variables for up/down
        if direction == "up":
            go_down = card_counter - 1
            go_up = card_counter

        elif direction == "down":
            go_down = card_counter
            go_up = card_counter + 1

        if go_down > 0 and go_up <= self.card_counter:
            # Putting everything from the main db to backup db
            self.c.execute("INSERT INTO playlist_backup SELECT * FROM playlist;")
            self.conn.commit()

            # Getting everything for the music that will go up
            self.c.execute(f"SELECT * FROM playlist_backup WHERE name = {go_up}")
            x = self.c.fetchall()
            self.conn.commit()

            # Updating the names for both go up and down.
            # For down = -1
            # For up = -2
            self.c.execute(f"UPDATE playlist set name = -1 WHERE name = {go_down}")
            self.conn.commit()
            self.c.execute(f"UPDATE playlist set name = -2 WHERE name = {go_up}")
            self.conn.commit()

            # Selecting everything from backup db for go down
            self.c.execute(f"SELECT * FROM playlist_backup WHERE name = {go_down}")
            x = self.c.fetchall()
            self.conn.commit()

            # Updating the main db with go down info
            self.c.execute(
                f"UPDATE playlist set name = ?, title = ?, duration = ?, artist = ?, second_name = ? WHERE name = -2",
                ((go_up, x[0][1], x[0][2], x[0][3], x[0][4])),
            )
            self.conn.commit()

            # Selecting everything from backup db for go up
            self.c.execute(f"SELECT * FROM playlist_backup WHERE name = {go_up}")
            x = self.c.fetchall()
            self.conn.commit()

            # Updating the main db with go up info
            self.c.execute(
                f"UPDATE playlist set name = ?, title = ?, duration = ?, artist = ?, second_name = ? WHERE name = -1",
                ((go_down, x[0][1], x[0][2], x[0][3], x[0][4])),
            )
            self.conn.commit()

            # Clearing and reinitiating all the cards
            self.card_clear()
            self.db_initiate()

            # Setting stylesheet for now playing
            if self.playing == True:
                self.styler(self.c_playing)
