import sys
from PyQt5.QtWidgets import QApplication
from frontend import BrightnessControlApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrightnessControlApp()
    sys.exit(app.exec_())