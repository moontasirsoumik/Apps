import sys
import ctypes
import screen_brightness_control as sbc
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QSlider, QWidget, QFrame, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt, QSize, QRectF, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QPainterPath
from PyQt5.QtWidgets import QProxyStyle, QStyle, QStyleOptionSlider

class HollowHandleStyle(QProxyStyle):
    def __init__(self, accent_color: QColor, config: dict = None):
        super().__init__()
        self.config = {
            "groove.height": 2,
            "sub-page.color": accent_color,
            "add-page.color": QColor(200, 200, 200, 100),
            "handle.color": accent_color,
            "handle.ring-width": 2,
            "handle.hollow-radius": 3,
            "handle.margin": 2
        }
        if config:
            self.config.update(config)
        w = self.config["handle.margin"] + self.config["handle.ring-width"] + self.config["handle.hollow-radius"]
        self.config["handle.size"] = QSize(2 * w, 2 * w)

    def subControlRect(self, cc, opt, sc, widget):
        if cc != self.CC_Slider or opt.orientation != Qt.Horizontal or sc == self.SC_SliderTickmarks:
            return super().subControlRect(cc, opt, sc, widget)

        rect = opt.rect

        if sc == self.SC_SliderGroove:
            h = self.config["groove.height"]
            grooveRect = QRectF(0, (rect.height() - h) // 2, rect.width(), h)
            return grooveRect.toRect()

        if sc == self.SC_SliderHandle:
            size = self.config["handle.size"]
            x = self.sliderPositionFromValue(opt.minimum, opt.maximum, opt.sliderPosition, rect.width())
            x *= (rect.width() - size.width()) / rect.width()
            y = (rect.height() - size.height()) // 2
            sliderRect = QRectF(x, y, size.width(), size.height())
            return sliderRect.toRect()

    def drawComplexControl(self, cc, opt, painter, widget):
        if cc != self.CC_Slider or opt.orientation != Qt.Horizontal:
            return super().drawComplexControl(cc, opt, painter, widget)

        grooveRect = self.subControlRect(cc, opt, self.SC_SliderGroove, widget)
        handleRect = self.subControlRect(cc, opt, self.SC_SliderHandle, widget)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        painter.save()
        painter.translate(grooveRect.topLeft())

        w = handleRect.x() - grooveRect.x()
        h = self.config["groove.height"]
        painter.setBrush(self.config["sub-page.color"])
        painter.drawRect(0, 0, w, h)

        x = w + self.config["handle.size"].width()
        painter.setBrush(self.config["add-page.color"])
        painter.drawRect(x, 0, grooveRect.width() - w, h)
        painter.restore()

        ringWidth = self.config["handle.ring-width"]
        hollowRadius = self.config["handle.hollow-radius"]
        radius = ringWidth + hollowRadius

        path = QPainterPath()
        center = handleRect.center()
        path.addEllipse(center, radius, radius)
        path.addEllipse(center, hollowRadius, hollowRadius)

        handleColor = self.config["handle.color"]
        handleColor.setAlpha(255 if opt.activeSubControls != self.SC_SliderHandle else 200)
        painter.setBrush(handleColor)
        painter.drawPath(path)

        if widget.isSliderDown():
            handleColor.setAlpha(255)
            painter.setBrush(handleColor)
            painter.drawEllipse(handleRect)

class StyledSlider(QSlider):
    def __init__(self, orientation, accent_color, parent=None):
        super().__init__(orientation, parent)
        self.setStyle(HollowHandleStyle(accent_color))

class BrightnessControlApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.accent_color = self.get_accent_color()
        self.is_dark_mode = self.get_dark_mode_status()

        self.setWindowTitle("Brightness Control")
        self.setGeometry(100, 100, 500, 300)
        self.update_stylesheet()

        self.displays = []
        self.init_ui()
        self.refresh_displays()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_brightness_values)
        self.timer.start(1000)

    def init_ui(self):
        layout = QVBoxLayout()

        title_label = QLabel("Adjust Brightness")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        self.sliders_layout = QVBoxLayout()
        layout.addLayout(self.sliders_layout)

        refresh_button = QPushButton("Refresh Displays")
        refresh_button.clicked.connect(self.refresh_displays)
        layout.addWidget(refresh_button, alignment=Qt.AlignCenter)

        container = QFrame()
        container.setLayout(layout)
        outer_layout = QVBoxLayout()
        outer_layout.addWidget(container)
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(outer_layout)

    def refresh_displays(self):
        self.displays = sbc.list_monitors()
        for i in reversed(range(self.sliders_layout.count())):
            widget = self.sliders_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for display in self.displays:
            self.add_display_slider(display)

    def add_display_slider(self, display):
        slider_container = QVBoxLayout()

        display_label = QLabel(display)
        display_label.setFont(QFont("Segoe UI", 12))
        slider_container.addWidget(display_label)

        slider_row = QHBoxLayout()
        brightness_slider = StyledSlider(Qt.Horizontal, self.accent_color)
        brightness_slider.setRange(0, 100)
        current_brightness = self.get_brightness(display)
        brightness_slider.setValue(current_brightness)
        brightness_slider.valueChanged.connect(lambda value, d=display: self.change_brightness(d, value))
        slider_row.addWidget(brightness_slider)

        brightness_value_label = QLabel(f"{current_brightness}%")
        brightness_value_label.setFont(QFont("Segoe UI", 10))
        slider_row.addWidget(brightness_value_label)

        slider_container.addLayout(slider_row)
        frame = QFrame()
        frame.setLayout(slider_container)
        frame.setStyleSheet("background-color: transparent; border: none;")
        self.sliders_layout.addWidget(frame)

        brightness_slider.valueChanged.connect(lambda value: brightness_value_label.setText(f"{value}%"))

    def change_brightness(self, display, brightness):
        sbc.set_brightness(brightness, display=display)

    def update_brightness_values(self):
        for i in range(self.sliders_layout.count()):
            frame = self.sliders_layout.itemAt(i).widget()
            if frame:
                layout = frame.layout()
                display_label = layout.itemAt(0).widget()
                slider_row = layout.itemAt(1).layout()
                brightness_slider = slider_row.itemAt(0).widget()
                brightness_value_label = slider_row.itemAt(1).widget()

                current_brightness = self.get_brightness(display_label.text())
                brightness_slider.blockSignals(True)
                brightness_slider.setValue(current_brightness)
                brightness_slider.blockSignals(False)
                brightness_value_label.setText(f"{current_brightness}%")

    def get_brightness(self, display):
        try:
            return sbc.get_brightness(display=display)[0]
        except Exception:
            return 50

    def get_dark_mode_status(self):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return value == 0
        except Exception:
            return False

    def get_accent_color(self):
        try:
            color = ctypes.windll.dwmapi.DwmGetColorizationColor
            argb = ctypes.c_uint()
            color(ctypes.byref(argb))
            hex_color = f"#{(argb.value & 0x00FFFFFF):06X}"
            return QColor(hex_color)
        except Exception:
            return QColor(0, 120, 215)

    def update_stylesheet(self):
        background_color = "#2d2d2d" if self.is_dark_mode else "#ffffff"
        text_color = "#ffffff" if self.is_dark_mode else "#000000"

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {background_color};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
            QPushButton {{
                background-color: {self.accent_color.name()};
                border: none;
                color: {text_color};
                font-size: 14px;
                font-family: 'Segoe UI';
                padding: 6px 12px;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_color.darker(120).name()};
            }}
        """)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BrightnessControlApp()
    window.show()
    sys.exit(app.exec_())