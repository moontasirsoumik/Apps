import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from ui import Ui_MainWindow
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import sqlite3


class MainWindow(QMainWindow, Ui_MainWindow, QtWidgets.QPlainTextEdit):

    def __init__(self):
        super(__class__, self).__init__()
        self.setupUi(self)
        self.show()
        self.setWindowTitle("Wordle")
        

        self.label_info.hide()

        for i in range(1, 6):
            exec(f'self.lineEdit_{i}.setMaxLength(1)')

        self.lineEdit_1.setFocus()
        for i in range(1, 6):
            exec(f'self.lineEdit_{i}.textEdited.connect(self.tabNext)')

        self.random_gen()
        self.format()
        self.enter_pressed = 0
        self.hint_pressed = 0
        self.back_pressed = False

        self.win = False

        self.pushButton_enter.clicked.connect(
            lambda: self.enter())

        self.pushButton_hint.clicked.connect(
            lambda: self.show_hint())

        self.pushButton_retry.clicked.connect(
            lambda: self.retry())

    #     for i in range(1, 6):
    #         exec(f'self.lineEdit_{i}.installEventFilter(self)')

    # def eventFilter(self, source, event):
    #     for i in range(1, 5):
    #         exec(f"""if (self.lineEdit_{i}.hasFocus()): 
    #                     if (event.type() == QtCore.QEvent.KeyPress and source is self.lineEdit_{i}): 
    #                         if (event.key() == 16777236): self.lineEdit_{i+1}.setFocus()""")

    #     for i in range(2, 6):
    #         exec(f"""if (self.lineEdit_{i}.hasFocus()): 
    #                     if (event.type() == QtCore.QEvent.KeyPress and source is self.lineEdit_{i}): 
    #                         if (event.key() == 16777234): self.lineEdit_{i-1}.setFocus();
    #                         if len(self.lineEdit_{i}.text()) == 0:
    #                             if (event.key() == 16777219): self.lineEdit_{i-1}.setFocus()""")

    #     return super(MainWindow, self).eventFilter(source, event)

    def format(self):
        for i in range(1, 31):
            exec(f'self.label_{i}.setStyleSheet("background-color: grey")')

    def retry(self):
        self.hint_pressed = 0
        self.enter_pressed = 0
        self.win = False
        self.random_gen()
        self.format()
        for i in range(1, 6):
            exec(f"self.lineEdit_{i}.setEnabled(True)")

        for i in range(1, 31):
            exec(f'self.label_{i}.clear()')

        self.line_clear()

    def random_gen(self):
        self.conn = sqlite3.connect('word.db')
        self.c = self.conn.cursor()

        self.table = self.c.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
        AND name='words'; """).fetchall()

        self.conn.commit()

        self.conn2 = sqlite3.connect('check.db')
        self.c2 = self.conn2.cursor()

        self.table2 = self.c2.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
        AND name='words'; """).fetchall()

        self.conn2.commit()

        from random import randrange
        self.limit = (randrange(2443))
        self.c.execute(
            f"""SELECT word FROM words WHERE rowid = {self.limit}""")
        items = self.c.fetchall()
        s = ''
        for item in items:
            s = ''.join(item)

        self.g_word = s

        print(s)

    def tabNext(self):
        for i in range(1, 5):
            exec(
                f"""if self.lineEdit_{i}.hasFocus() and len(self.lineEdit_{i}.text()) == 1: self.lineEdit_{i+1}.setFocus()""")

        self.lineEdit_5.returnPressed.connect(self.pushButton_enter.click)

    def backspace(self):
        if self.back_pressed == True:
            self.back_pressed = False

            if self.label_5.hasFocus() and len(self.label_5.text()) == 0:
                self.label_4.setFocus()

    def line_clear(self):
        for i in range(1, 6):
            exec(f'self.lineEdit_{i}.clear()')
            exec(
                f'self.lineEdit_{i}.setStyleSheet("background-color: white")')

        self.lineEdit_1.setFocus()

    def ans(self):
        self.winner()
        QApplication.processEvents()

        for i in range(1, 6):
            exec(f'self.lineEdit_{i}.setText(self.g_word[{i-1}].upper())')
            exec(
                f'self.lineEdit_{i}.setStyleSheet("background-color: tomato")')

    def winner(self):
        QApplication.processEvents()
        for i in range(1, 6):
            QApplication.processEvents()
            exec(f'self.lineEdit_{i}.setStyleSheet("background-color: grey")')
            exec(f'self.lineEdit_{i}.setEnabled(False)')

    def enter(self):
        self.label_info.hide()
        QApplication.processEvents()

        if (self.lineEdit_1.text() != '' and self.lineEdit_2.text() != '' and self.lineEdit_3.text() != '' and self.lineEdit_4.text() != '' and self.lineEdit_5.text() and self.enter_pressed < 6 and self.win == False):
            self.w_word = str(self.lineEdit_1.text()+self.lineEdit_2.text() +
                              self.lineEdit_3.text()+self.lineEdit_4.text()+self.lineEdit_5.text())

            self.w_word = self.w_word.lower()

            self.c2.execute(
                f"""SELECT * FROM words WHERE word= ?""", (self.w_word,))
            x = self.c2.fetchone()

            if self.w_word == self.g_word:
                QApplication.processEvents()
                self.win = True
                self.winner()

            if (x != None):

                num = (int(self.enter_pressed) * 5)

                self.enter_pressed += 1

                self.y_word = self.g_word
                for i in range(1, 6):

                    cond = f"self.lineEdit_{i}.text().lower() in self.y_word"
                    q = ''
                    if eval(cond):
                        exec(
                            f'self.label_{num+i}.setText(self.lineEdit_{i}.text().upper()); self.label_{num+i}.setStyleSheet("background-color: yellow")')

                        p = 0
                        while p <= len(self.y_word):
                            self.breaker = False
                            exec(
                                f"""if(self.y_word[{p}] == self.lineEdit_{i}.text().lower()): self.y_word = self.y_word.replace(self.y_word[{p}], ""); self.breaker = True""")
                            if (self.breaker == True):
                                break
                            p += 1

                    else:
                        exec(
                            f'self.label_{num+i}.setText(self.lineEdit_{i}.text().upper())')
                        exec(
                            f'self.label_{num+i}.setStyleSheet("background-color: white")')

                for i in range(5):
                    if (self.w_word[i] == self.g_word[i]):
                        letter = [f'self.label_{num+1}.setStyleSheet("background-color: lightgreen")', f'self.label_{num+2}.setStyleSheet("background-color: lightgreen")', f'self.label_{num+3}.setStyleSheet("background-color: lightgreen")',
                                  f'self.label_{num+4}.setStyleSheet("background-color: lightgreen")', f'self.label_{num+5}.setStyleSheet("background-color: lightgreen")']
                        exec(letter[i])

                if self.enter_pressed == 6 and self.win == False:
                    QApplication.processEvents()
                    self.ans()
                else:
                    self.line_clear()

                QApplication.processEvents()
                self.label_info.clear()
            else:
                self.label_info.show()
                QApplication.processEvents()
                self.label_info.setText("Not a valid Word")

    def show_hint(self):
        self.hint_pressed += 1
        if self.hint_pressed == 1:
            msg = QMessageBox()
            msg.setWindowTitle("Meaning")

            self.c.execute(
                f"""SELECT type FROM words WHERE rowid = {self.limit}""")
            items = self.c.fetchall()
            type = ''
            for item in items:
                type = ''.join(item)

            self.c.execute(
                f"""SELECT meaning FROM words WHERE rowid = {self.limit}""")
            items = self.c.fetchall()
            meaning = ''
            for item in items:
                meaning = ''.join(item)

            msg.setText(str(type))
            msg.setInformativeText(str(meaning))
            msg.setIcon(QMessageBox.Information)
            x = msg.exec_()

        elif self.hint_pressed == 2:
            msg = QMessageBox()
            msg.setWindowTitle("Synonyms")

            self.c.execute(
                f"""SELECT synonyms FROM words WHERE rowid = {self.limit}""")
            items = self.c.fetchall()
            synonym = ''
            for item in items:
                synonym = ''.join(item)

            msg.setText(str(synonym))
            msg.setIcon(QMessageBox.Information)
            x = msg.exec_()

        else:
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("You have run out of hints")
            msg.setIcon(QMessageBox.Warning)
            x = msg.exec_()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
