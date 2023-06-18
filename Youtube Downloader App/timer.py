import time
from PyQt5.QtCore import QThread, QObject, pyqtSignal as Signal, pyqtSlot as Slot


class Timer(QObject):
    time_up = Signal(bool)

    @Slot()
    def time_count(self):
        time.sleep(4)
        self.time_up.emit(True)
